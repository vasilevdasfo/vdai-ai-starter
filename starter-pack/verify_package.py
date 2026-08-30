#!/usr/bin/env python3
"""Verify that VDAI AI Starter is complete, not a partial transfer."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXPECTED_SKILLS = [
    "problem-os",
    "economy-guard",
    "numbering-canon",
    "devils-advocate",
    "sos",
    "sos1",
    "sos2",
    "boardroom",
    "problem-to-action",
    "repeatable-work",
    "numbered-next",
]


def verify(pack: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = pack / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest unreadable: {exc}"]

    if manifest.get("skills") != EXPECTED_SKILLS:
        errors.append("manifest must contain the canonical 11 Skills in order")
    if manifest.get("acceptance", {}).get("skill_files") != 11:
        errors.append("acceptance.skill_files must be 11")
    if manifest.get("acceptance", {}).get("verification_turns") != 2:
        errors.append("acceptance.verification_turns must be 2")
    if manifest.get("acceptance", {}).get("language_auto_detect") is not True:
        errors.append("acceptance.language_auto_detect must be true")
    if manifest.get("acceptance", {}).get("platform_native_weight") is not True:
        errors.append("acceptance.platform_native_weight must be true")
    if manifest.get("acceptance", {}).get("partial_install_is_complete") is not False:
        errors.append("partial installation must never count as complete")
    installed = manifest.get("installed_layout", {})
    if installed.get("source_filenames_required_in_live_profile") is not False:
        errors.append("source filenames must not be required in the live profile")
    if installed.get("codex", {}).get("verification") != "VDAI_AI_STARTER_VERIFICATION.md":
        errors.append("Codex installed verification path is wrong")
    if installed.get("claude", {}).get("usage") != "VDAI_AI_STARTER_USAGE.md":
        errors.append("Claude installed usage path is wrong")

    required_files = ["AGENTS.md", "CLAUDE.md", "CLAUDE_USAGE.md", "INSTALL.md", "VERIFICATION.md", "install.sh", "install.ps1", "tools/claude_statusline.py"]
    for relative in required_files:
        if not (pack / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for skill in EXPECTED_SKILLS:
        if not (pack / "skills" / skill / "SKILL.md").is_file():
            errors.append(f"missing Skill: {skill}/SKILL.md")

    try:
        verification = (pack / manifest["verification_playbook"]).read_text(encoding="utf-8")
    except (KeyError, OSError) as exc:
        errors.append(f"verification playbook unreadable: {exc}")
        verification = ""
    for skill in EXPECTED_SKILLS:
        if f"`{skill}`" not in verification:
            errors.append(f"verification task missing for: {skill}")
    if verification.count("| `") != 11:
        errors.append("verification table must contain exactly 11 Skill tasks")
    if "TASK WEIGHT" not in verification or "user's language" not in verification:
        errors.append("verification must test language-aware task weight")

    for instruction_name in ("AGENTS.md", "CLAUDE.md"):
        instruction = (pack / instruction_name).read_text(encoding="utf-8")
        if "language of the user's current message" not in instruction:
            errors.append(f"{instruction_name} lacks automatic language selection")
        if "Do not require source-only filenames" not in instruction:
            errors.append(f"{instruction_name} confuses source and installed paths")
        if "Never label work `[COMPLETE]`" not in instruction:
            errors.append(f"{instruction_name} allows false completion with an open gate")
        if "Почему:" in instruction or "ВЕС ЗАДАЧИ" in instruction:
            errors.append(f"{instruction_name} hard-codes Russian user-facing labels")

    economy = (pack / "skills" / "economy-guard" / "SKILL.md").read_text(encoding="utf-8")
    for required in ("TASK WEIGHT", "PESO DE LA TAREA", "WAGA ZADANIA", "Claude Code", "statusLine"):
        if required not in economy:
            errors.append(f"economy-guard lacks: {required}")
    for required in ("native Codex Status", "37,889 / 250k context tokens", "⚪", "🟩 CONTINUE", "🟨 CHECKPOINT_AND_SPLIT", "🟥 STOP_AND_CLOSEOUT", "Gray means unknown, not safe"):
        if required not in economy:
            errors.append(f"economy-guard lacks platform-native weight contract: {required}")
    if "omit the numeric/color weight block" in economy:
        errors.append("economy-guard still removes color icons when counters are unavailable")

    feedback = (pack / "FEEDBACK.md").read_text(encoding="utf-8") if (pack / "FEEDBACK.md").is_file() else ""
    for required in ("GitHub Issue", "platform", "version", "reproduction", "Never include"):
        if required not in feedback:
            errors.append(f"feedback guide lacks: {required}")

    visual = (pack / "VISUAL_TASK_LABELS.md").read_text(encoding="utf-8") if (pack / "VISUAL_TASK_LABELS.md").is_file() else ""
    for required in ("🎯 P", "🚧 U", "🛡️ L", "🛠️ R", "✅ N", "📁 TASK", "👤 OWNER", "🔎 PROOF"):
        if required not in visual:
            errors.append(f"visual guide lacks: {required}")
    helper = pack / "tools" / "codex_task_weight.py"
    if not helper.is_file() or "exact-thread identity mismatch" not in helper.read_text(encoding="utf-8"):
        errors.append("Codex exact-thread weight helper missing or fail-open")

    numbering = (pack / "skills" / "numbering-canon" / "SKILL.md").read_text(encoding="utf-8")
    if "Почему:" in numbering or "localized to the user's current language" not in numbering:
        errors.append("numbering-canon hard-codes or fails to localize the reason label")

    for installer_name in ("install.sh", "install.ps1"):
        try:
            installer = (pack / installer_name).read_text(encoding="utf-8")
        except OSError:
            continue
        for skill in EXPECTED_SKILLS:
            if skill not in installer:
                errors.append(f"{installer_name} does not install: {skill}")
        if "VERIFICATION.md" not in installer:
            errors.append(f"{installer_name} does not install the verification playbook")
        if "CLAUDE_USAGE.md" not in installer or "claude_statusline.py" not in installer:
            errors.append(f"{installer_name} does not include Claude usage support")
        if "FEEDBACK.md" not in installer or "VDAI_AI_STARTER_FEEDBACK.md" not in installer:
            errors.append(f"{installer_name} does not install feedback guide")
        if "VISUAL_TASK_LABELS.md" not in installer or "VDAI_AI_STARTER_VISUAL_GUIDE.md" not in installer:
            errors.append(f"{installer_name} does not install visual guide")
        if "codex_task_weight.py" not in installer or "vdai-task-weight.py" not in installer:
            errors.append(f"{installer_name} does not install Codex weight helper")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--self-test", action="store_true", help="also prove that a partial package fails")
    args = parser.parse_args()

    errors = verify(args.pack.resolve())
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    if args.self_test:
        with tempfile.TemporaryDirectory(prefix="vdai-ai-starter-negative-") as temp_dir:
            broken = Path(temp_dir) / "starter-pack"
            shutil.copytree(args.pack.resolve(), broken)
            (broken / "skills" / EXPECTED_SKILLS[-1] / "SKILL.md").unlink()
            if not verify(broken):
                print("FAIL")
                print("- negative test accepted a package with one missing Skill")
                return 1

        with tempfile.TemporaryDirectory(prefix="vdai-ai-starter-statusline-") as temp_dir:
            mock = {
                "session_id": "test-session-abc",
                "transcript_path": "/tmp/test.jsonl",
                "model": {"display_name": "Sonnet"},
                "version": "2.1.132",
                "context_window": {"total_input_tokens": 15500, "total_output_tokens": 1200, "used_percentage": 8, "remaining_percentage": 92, "context_window_size": 200000},
                "cost": {"total_cost_usd": 0.01234},
            }
            env = os.environ.copy()
            env["HOME"] = temp_dir
            result = subprocess.run([sys.executable, str(args.pack.resolve() / "tools" / "claude_statusline.py")], input=json.dumps(mock), text=True, capture_output=True, env=env, check=False)
            snapshot = Path(temp_dir) / ".claude" / "vdai-task-weight" / "test-session-abc.json"
            if result.returncode != 0 or "ctx 8%" not in result.stdout or not snapshot.is_file():
                print("FAIL")
                print("- Claude status-line helper did not render and snapshot official counters")
                return 1

    print("PASS: 11 Skills + 11 tasks + auto-language + platform-native weight + two-turn verification; negative tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
