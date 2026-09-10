import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "token_economy_audit.py"


class AuditTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)], text=True, capture_output=True)

    def test_exact_usage(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "usage.jsonl"
            source.write_text('{"usage":{"input_tokens":100,"cached_input_tokens":60,"output_tokens":5}}\n'
                              '{"input_tokens":40,"cached_input_tokens":10,"output_tokens":7}\n', encoding="utf-8")
            result = self.run_cli("--usage-jsonl", source)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["input_tokens"], 140)
            self.assertEqual(data["cached_input_tokens"], 70)
            self.assertEqual(data["uncached_input_tokens"], 70)
            self.assertEqual(data["calls"], 2)
            self.assertTrue(data["exact_usage"])

    def test_negative_counter_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "usage.jsonl"
            source.write_text('{"input_tokens":-1}\n', encoding="utf-8")
            result = self.run_cli("--usage-jsonl", source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-negative integer", result.stderr)

    def test_cached_input_cannot_exceed_input(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "usage.jsonl"
            source.write_text('{"input_tokens":10,"cached_input_tokens":11}\n', encoding="utf-8")
            result = self.run_cli("--usage-jsonl", source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exceeds input_tokens", result.stderr)

    def test_empty_usage_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "usage.jsonl"
            source.write_text("", encoding="utf-8")
            result = self.run_cli("--usage-jsonl", source)
            data = json.loads(result.stdout)
            self.assertEqual(data["calls"], 0)
            self.assertIsNone(data["cache_ratio"])

    def test_project_mode_is_estimate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text("x" * 16001, encoding="utf-8")
            result = self.run_cli("--project", root)
            data = json.loads(result.stdout)
            self.assertFalse(data["exact_usage"])
            self.assertIn("not billing", data["estimate_basis"])
            self.assertEqual(data["findings"][0]["reason"], "large_text_context")

    def test_project_mode_rejects_home_root(self):
        result = self.run_cli("--project", Path.home())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing broad root", result.stderr)

    @unittest.skipUnless((ROOT / "club-settings-draft.html").exists(), "Club draft is not shipped in the public kit")
    def test_club_draft_has_both_languages_and_honest_gate(self):
        html = (ROOT / "club-settings-draft.html").read_text(encoding="utf-8")
        self.assertIn('data-lang="ru"', html)
        self.assertIn('data-lang="en"', html)
        self.assertIn("оценка размера текста не равна биллингу", html)
        self.assertIn("text-size estimate is not billing", html)
        self.assertNotIn("% savings", html)

    def write_manifest(self, root, **overrides):
        data = {
            "version": 1,
            "root": str(root),
            "task_key": "same-task-v1",
            "max_files": 2,
            "max_estimated_input_tokens": 100,
            "stable_prefix": ["AGENTS.md"],
            "sources": ["AGENTS.md", {"path": "notes.md", "sections": ["Needed"]}],
        }
        data.update(overrides)
        path = root / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_preflight_allows_selected_section_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text("stable rules\n", encoding="utf-8")
            (root / "notes.md").write_text("# Needed\nsmall context\n# Excluded\n" + "x" * 2000, encoding="utf-8")
            manifest = self.write_manifest(root)
            first = self.run_cli("--preflight", manifest)
            second = self.run_cli("--preflight", manifest)
            self.assertEqual(first.returncode, 0, first.stderr)
            one, two = json.loads(first.stdout), json.loads(second.stdout)
            self.assertEqual(one["decision"], "ALLOW")
            self.assertLess(one["estimated_input_tokens"], 100)
            self.assertEqual(one["stable_prefix_hash"], two["stable_prefix_hash"])
            self.assertEqual(one["sources"][1]["sections"], ["Needed"])

    def test_preflight_blocks_budget_with_machine_exit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text("x" * 1000, encoding="utf-8")
            manifest = self.write_manifest(root, max_files=1, max_estimated_input_tokens=10,
                                           stable_prefix=["AGENTS.md"], sources=["AGENTS.md"])
            result = self.run_cli("--preflight", manifest)
            self.assertEqual(result.returncode, 3)
            data = json.loads(result.stdout)
            self.assertEqual(data["decision"], "BLOCK")
            self.assertIn("estimated_input_budget_exceeded", data["reasons"])

    def test_preflight_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            root.mkdir()
            outside = Path(td) / "outside.md"
            outside.write_text("secret", encoding="utf-8")
            manifest = self.write_manifest(root, stable_prefix=[], sources=["../outside.md"])
            result = self.run_cli("--preflight", manifest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("escapes root", result.stderr)

    def test_compare_requires_same_accepted_task_and_calculates_delta(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before = root / "before.jsonl"
            after = root / "after.jsonl"
            before.write_text('{"task_key":"x","accepted":true,"usage":{"input_tokens":100,"cached_input_tokens":60,"output_tokens":20}}\n', encoding="utf-8")
            after.write_text('{"task_key":"x","accepted":true,"usage":{"input_tokens":60,"cached_input_tokens":45,"output_tokens":10}}\n', encoding="utf-8")
            result = self.run_cli("--compare", before, after, "--task-key", "x")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["reduction_percent"]["input_tokens"], 40.0)
            self.assertEqual(data["reduction_percent"]["uncached_input_tokens"], 62.5)
            self.assertEqual(data["delta_after_minus_before"]["calls"], 0)

    def test_compare_rejects_mismatched_or_unaccepted_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before = root / "before.jsonl"
            after = root / "after.jsonl"
            before.write_text('{"task_key":"x","accepted":true,"input_tokens":10}\n', encoding="utf-8")
            after.write_text('{"task_key":"y","accepted":true,"input_tokens":9}\n', encoding="utf-8")
            mismatch = self.run_cli("--compare", before, after)
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("identical", mismatch.stderr)
            after.write_text('{"task_key":"x","accepted":false,"input_tokens":9}\n', encoding="utf-8")
            rejected = self.run_cli("--compare", before, after)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("accepted=true", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
