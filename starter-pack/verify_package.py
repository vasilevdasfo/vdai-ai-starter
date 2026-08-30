#!/usr/bin/env python3
"""Verify that VDAI AI Starter is complete, not a partial transfer."""

from __future__ import annotations

import argparse
import json
import shutil
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
    if manifest.get("acceptance", {}).get("partial_install_is_complete") is not False:
        errors.append("partial installation must never count as complete")

    required_files = ["AGENTS.md", "CLAUDE.md", "INSTALL.md", "VERIFICATION.md", "install.sh", "install.ps1"]
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

    print("PASS: 11 Skills + 11 tasks + instructions + two-turn verification; partial-package negative test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
