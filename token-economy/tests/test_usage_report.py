import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "usage_report.py"
NOW = float(int(time.time()))  # fixture files get the real mtime, so the clock stays near it
DAY = 86_400


def iso(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")


def token_row(ts, total_in, last_in, cached, rate=None):
    payload = {"type": "token_count", "info": {
        "total_token_usage": {"input_tokens": total_in, "output_tokens": 10},
        "last_token_usage": {"input_tokens": last_in, "cached_input_tokens": cached}}}
    if rate is not None:
        payload["rate_limits"] = {"primary": {"used_percent": rate, "window_minutes": 10080}}
    return {"timestamp": iso(ts), "type": "event_msg", "payload": payload}


def user_row(ts, text):
    return {"timestamp": iso(ts), "type": "response_item",
            "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}}


def write_jsonl(path, rows, extra_lines=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r, ensure_ascii=False) for r in rows] + list(extra_lines)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class UsageReportTests(unittest.TestCase):
    def run_cli(self, *args):
        result = subprocess.run([sys.executable, str(CLI), "--now", str(NOW), *map(str, args)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def report(self, codex, claude, *args):
        return json.loads(self.run_cli("--json", "--codex-dir", codex, "--claude-dir", claude, *args))

    def codex_fixture(self, root):
        t = NOW - 3600
        rows = [
            {"timestamp": iso(t), "type": "session_meta",
             "payload": {"id": "11111111-aaaa-bbbb-cccc-000000000001", "timestamp": iso(t)}},
            {"timestamp": iso(t), "type": "turn_context", "payload": {"model": "model-a"}},
            user_row(t, "<environment_context>ignored</environment_context>"),
            user_row(t, "first question"),
            token_row(t + 1, 40_000, 40_000, 0, rate=5.0),
            token_row(t + 2, 40_000, 40_000, 0),  # duplicate counter, must be skipped
            user_row(t + 3, "second question"),
            token_row(t + 4, 200_000, 160_000, 150_000, rate=7.5),
            {"timestamp": iso(t + 5), "type": "compacted", "payload": {}},
        ]
        write_jsonl(root / "2026" / "01" / "01" / "rollout-x-11111111-aaaa-bbbb-cccc-000000000001.jsonl",
                    rows, extra_lines=["{not json"])
        forked = [
            {"timestamp": iso(t), "type": "session_meta",
             "payload": {"id": "22222222-aaaa-bbbb-cccc-000000000002", "timestamp": iso(t),
                         "forked_from_id": "11111111-aaaa-bbbb-cccc-000000000001"}},
            token_row(t + 1, 95_000, 95_000, 90_000),
        ]
        write_jsonl(root / "2026" / "01" / "01" / "rollout-y-22222222-aaaa-bbbb-cccc-000000000002.jsonl", forked)

    def claude_fixture(self, root):
        t = NOW - 1800
        usage = {"input_tokens": 10, "cache_creation_input_tokens": 1_000, "cache_read_input_tokens": 49_000}
        rows = [
            {"type": "user", "timestamp": iso(t), "message": {"role": "user", "content": "hello"}},
            {"type": "assistant", "timestamp": iso(t + 1), "requestId": "r1",
             "message": {"id": "m1", "model": "model-c", "usage": usage}},
            {"type": "assistant", "timestamp": iso(t + 1), "requestId": "r1",
             "message": {"id": "m1", "model": "model-c", "usage": usage}},  # same message, second block
            {"type": "user", "timestamp": iso(t + 2),
             "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "assistant", "timestamp": iso(t + 3),
             "message": {"id": "m2", "model": "<synthetic>", "usage": {"input_tokens": 0}}},
            {"type": "user", "timestamp": iso(t + 4), "isCompactSummary": True,
             "message": {"role": "user", "content": "summary"}},
            {"type": "summary", "summary": "session title, not a compaction"},
        ]
        write_jsonl(root / "-proj" / "abc-session.jsonl", rows)

    def test_codex_counts_dedupe_flags_and_limit(self):
        with tempfile.TemporaryDirectory() as td:
            codex, claude = Path(td) / "codex", Path(td) / "claude"
            self.codex_fixture(codex)
            data = self.report(codex, claude, "--only", "codex")
            part = data["tools"][0]
            self.assertEqual(part["threads"], 2)
            self.assertEqual(part["calls"], 3)
            self.assertEqual(part["input_tokens"], 40_000 + 160_000 + 95_000)
            self.assertEqual(part["cached_input_tokens"], 240_000)
            self.assertEqual(part["forked_threads"], 1)
            self.assertEqual(part["median_start_context"], 40_000)  # forks excluded from start median
            self.assertEqual(part["limit"]["used_percent"], 7.5)
            top = {t["id"]: t for t in part["top"]}
            self.assertEqual(top["11111111"]["questions"], 2)
            self.assertIn("длинная переписка", top["11111111"]["flags"])
            self.assertIn("форк старой ветки", top["22222222"]["flags"])
            self.assertIn("тяжёлый старт", top["22222222"]["flags"])
            self.assertEqual(data["stats"]["duplicate_counters"], 1)
            self.assertEqual(data["stats"]["malformed_lines"], 1)

    def test_claude_dedupes_message_blocks_and_skips_synthetic(self):
        with tempfile.TemporaryDirectory() as td:
            codex, claude = Path(td) / "codex", Path(td) / "claude"
            self.claude_fixture(claude)
            part = self.report(codex, claude, "--only", "claude")["tools"][0]
            self.assertEqual(part["calls"], 1)
            self.assertEqual(part["input_tokens"], 50_010)
            self.assertEqual(part["cached_input_tokens"], 49_000)
            self.assertEqual(part["models"], {"model-c": 1})
            self.assertEqual(part["top"][0]["questions"], 1)  # tool_result and compact summary are not requests

    def test_days_window_excludes_old_calls(self):
        with tempfile.TemporaryDirectory() as td:
            codex, claude = Path(td) / "codex", Path(td) / "claude"
            old = NOW - 10 * DAY
            rows = [token_row(old, 50_000, 50_000, 0), token_row(NOW - 60, 120_000, 70_000, 0)]
            write_jsonl(codex / "rollout-old-33333333-aaaa-bbbb-cccc-000000000003.jsonl", rows)
            part = self.report(codex, claude, "--only", "codex", "--days", 7)["tools"][0]
            self.assertEqual(part["calls"], 1)
            self.assertEqual(part["input_tokens"], 70_000)

    def test_missing_directories_report_zero(self):
        with tempfile.TemporaryDirectory() as td:
            data = self.report(Path(td) / "none1", Path(td) / "none2")
            self.assertEqual([p["threads"] for p in data["tools"]], [0, 0])
            text = self.run_cli("--codex-dir", Path(td) / "none1", "--claude-dir", Path(td) / "none2")
            self.assertIn("логов за период нет", text)

    def test_text_output_never_contains_message_text(self):
        with tempfile.TemporaryDirectory() as td:
            codex, claude = Path(td) / "codex", Path(td) / "claude"
            self.codex_fixture(codex)
            self.claude_fixture(claude)
            text = self.run_cli("--codex-dir", codex, "--claude-dir", claude)
            for secret in ("first question", "second question", "hello", "summary"):
                self.assertNotIn(secret, text)
            self.assertIn("CODEX: 2 ветки, 3 вызова модели", text)

    def test_rejects_non_positive_days(self):
        result = subprocess.run([sys.executable, str(CLI), "--days", "0"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
