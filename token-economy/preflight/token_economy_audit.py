#!/usr/bin/env python3
"""Read-only token/context preflight and comparable usage audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

TEXT_NAMES = {"AGENTS.md", "CLAUDE.md", "SKILL.md"}
TEXT_SUFFIXES = {".md", ".txt"}
SKIP_PARTS = {".git", "node_modules", ".venv", "dist", "build"}
MANIFEST_KEYS = {"version", "root", "task_key", "max_files", "max_estimated_input_tokens", "stable_prefix", "sources"}


class AuditError(ValueError):
    pass


class BudgetBlocked(AuditError):
    def __init__(self, result: dict):
        super().__init__("preflight budget blocked")
        self.result = result


def estimate_tokens(chars: int) -> int:
    return (chars + 3) // 4


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditError(f"invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise AuditError("JSON root must be an object")
    return value


def validate_root_scope(root: Path) -> None:
    home = Path.home().resolve()
    filesystem_root = Path(root.anchor).resolve()
    if root == home or root == filesystem_root:
        raise AuditError("refusing broad root; choose an exact project directory")


def safe_source(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise AuditError("source path must be a non-empty string")
    try:
        resolved = (root / relative).resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise AuditError(f"source escapes root or is missing: {relative}") from exc
    if not resolved.is_file():
        raise AuditError(f"source is not a file: {relative}")
    return resolved


def extract_sections(text: str, names: list[str], relative: str) -> str:
    if not names or not all(isinstance(name, str) and name.strip() for name in names):
        raise AuditError(f"sections must be a non-empty string list: {relative}")
    lines = text.splitlines(keepends=True)
    headings = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line.rstrip("\n"))
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))
    chunks = []
    for name in names:
        matches = [(pos, level) for pos, level, title in headings if title == name.strip()]
        if len(matches) != 1:
            state = "missing" if not matches else "ambiguous"
            raise AuditError(f"section {state} in {relative}: {name}")
        start, level = matches[0]
        end = len(lines)
        for pos, next_level, _ in headings:
            if pos > start and next_level <= level:
                end = pos
                break
        chunks.append("".join(lines[start:end]).rstrip())
    return "\n\n".join(chunks) + "\n"


def normalize_source(item) -> tuple[str, list[str] | None]:
    if isinstance(item, str):
        return item, None
    if not isinstance(item, dict) or set(item) - {"path", "sections"} or "path" not in item:
        raise AuditError("each source must be a path string or {path, sections}")
    sections = item.get("sections")
    if sections is not None and not isinstance(sections, list):
        raise AuditError("sections must be a list")
    return item["path"], sections


def preflight(manifest_path: Path) -> dict:
    manifest = read_json(manifest_path)
    if set(manifest) - MANIFEST_KEYS:
        raise AuditError("manifest contains unknown fields")
    if manifest.get("version") != 1:
        raise AuditError("manifest version must be 1")
    task_key = manifest.get("task_key")
    if not isinstance(task_key, str) or not task_key.strip():
        raise AuditError("task_key is required")
    root_value = manifest.get("root")
    if not isinstance(root_value, str):
        raise AuditError("root is required")
    root = Path(root_value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise AuditError("root must be a directory")
    validate_root_scope(root)
    max_files = manifest.get("max_files")
    max_tokens = manifest.get("max_estimated_input_tokens")
    if not isinstance(max_files, int) or isinstance(max_files, bool) or max_files < 1:
        raise AuditError("max_files must be a positive integer")
    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens < 1:
        raise AuditError("max_estimated_input_tokens must be a positive integer")
    raw_sources = manifest.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise AuditError("sources must be a non-empty list")
    stable_prefix = manifest.get("stable_prefix", [])
    if not isinstance(stable_prefix, list) or not all(isinstance(x, str) for x in stable_prefix):
        raise AuditError("stable_prefix must be a string list")

    selected = []
    seen = set()
    for raw in raw_sources:
        relative, sections = normalize_source(raw)
        if relative in seen:
            raise AuditError(f"duplicate source: {relative}")
        seen.add(relative)
        path = safe_source(root, relative)
        try:
            full_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise AuditError(f"source is not UTF-8 text: {relative}") from exc
        selected_text = extract_sections(full_text, sections, relative) if sections is not None else full_text
        selected.append({
            "path": relative,
            "sections": sections or [],
            "chars": len(selected_text),
            "estimated_tokens": estimate_tokens(len(selected_text)),
            "content_sha256": sha256_text(selected_text),
        })
    missing_prefix = sorted(set(stable_prefix) - seen)
    if missing_prefix:
        raise AuditError("stable_prefix paths must also appear in sources: " + ", ".join(missing_prefix))

    total = sum(row["estimated_tokens"] for row in selected)
    reasons = []
    if len(selected) > max_files:
        reasons.append("max_files_exceeded")
    if total > max_tokens:
        reasons.append("estimated_input_budget_exceeded")
    prefix_rows = [(row["path"], row["content_sha256"]) for row in selected if row["path"] in stable_prefix]
    prefix_hash = sha256_text(json.dumps(prefix_rows, ensure_ascii=False, separators=(",", ":")))
    result = {
        "mode": "preflight",
        "decision": "BLOCK" if reasons else "ALLOW",
        "task_key": task_key,
        "root": str(root),
        "estimate_basis": "selected UTF-8 characters / 4, rounded up; not provider billing",
        "limits": {"max_files": max_files, "max_estimated_input_tokens": max_tokens},
        "selected_files": len(selected),
        "estimated_input_tokens": total,
        "stable_prefix_hash": prefix_hash,
        "sources": selected,
        "reasons": reasons,
    }
    if reasons:
        raise BudgetBlocked(result)
    return result


def parse_usage(path: Path) -> tuple[dict, list[dict]]:
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "calls": 0}
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AuditError(f"invalid JSON on line {line_no}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise AuditError(f"line {line_no} must be an object")
        usage = row.get("usage", row)
        if not isinstance(usage, dict):
            raise AuditError(f"usage must be an object on line {line_no}")
        values = {}
        for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
            value = usage.get(key, 0)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise AuditError(f"{key} must be a non-negative integer on line {line_no}")
            values[key] = value
            totals[key] += value
        if values["cached_input_tokens"] > values["input_tokens"]:
            raise AuditError(f"cached_input_tokens exceeds input_tokens on line {line_no}")
        totals["calls"] += 1
        rows.append({"line": line_no, "task_key": row.get("task_key"), "accepted": row.get("accepted"), **values})
    totals["uncached_input_tokens"] = max(0, totals["input_tokens"] - totals["cached_input_tokens"])
    totals["cache_ratio"] = round(totals["cached_input_tokens"] / totals["input_tokens"], 4) if totals["input_tokens"] else None
    return totals, rows


def audit_usage(path: Path) -> dict:
    totals, rows = parse_usage(path)
    return {"mode": "exact_usage", "source": str(path.resolve()), "exact_usage": True, **totals,
            "claims": "observed counters only; no price or savings claim", "rows": rows}


def reduction_percent(before: int, after: int):
    return round((before - after) * 100 / before, 2) if before else None


def compare_usage(before_path: Path, after_path: Path, expected_task_key: str | None) -> dict:
    before, before_rows = parse_usage(before_path)
    after, after_rows = parse_usage(after_path)
    if not before_rows or not after_rows:
        raise AuditError("comparison requires non-empty before and after files")
    before_keys = {row["task_key"] for row in before_rows}
    after_keys = {row["task_key"] for row in after_rows}
    if len(before_keys) != 1 or len(after_keys) != 1 or None in before_keys | after_keys or before_keys != after_keys:
        raise AuditError("comparison requires one identical non-empty task_key")
    task_key = next(iter(before_keys))
    if expected_task_key is not None and task_key != expected_task_key:
        raise AuditError("task_key does not match --task-key")
    if before_rows[-1]["accepted"] is not True or after_rows[-1]["accepted"] is not True:
        raise AuditError("both final rows must have accepted=true")
    metrics = ("input_tokens", "uncached_input_tokens", "output_tokens", "calls")
    delta = {key: after[key] - before[key] for key in metrics}
    reductions = {key: reduction_percent(before[key], after[key]) for key in metrics}
    return {
        "mode": "comparable_before_after", "task_key": task_key, "comparable": True,
        "accepted_before": True, "accepted_after": True,
        "before": {key: before[key] for key in metrics},
        "after": {key: after[key] for key in metrics},
        "delta_after_minus_before": delta, "reduction_percent": reductions,
        "claims": "exact observed counters for the same accepted task; price not calculated",
    }


def audit_project(root: Path) -> dict:
    root = root.resolve(strict=True)
    validate_root_scope(root)
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.name not in TEXT_NAMES and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append({"path": str(path.relative_to(root)), "chars": len(text), "estimated_tokens": estimate_tokens(len(text))})
    files.sort(key=lambda row: row["estimated_tokens"], reverse=True)
    findings = [{"severity": "review", "path": row["path"], "reason": "large_text_context",
                 "action": "load only the task-relevant section; keep the full file as source"}
                for row in files if row["estimated_tokens"] >= 4000]
    return {"mode": "project_estimate", "root": str(root.resolve()), "exact_usage": False,
            "estimate_basis": "UTF-8 characters / 4, rounded up; not billing", "files_scanned": len(files),
            "estimated_tokens": sum(row["estimated_tokens"] for row in files), "largest_files": files[:10], "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only token/context preflight and audit")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--project", type=Path)
    action.add_argument("--usage-jsonl", type=Path)
    action.add_argument("--preflight", type=Path, help="version 1 selection/budget manifest")
    action.add_argument("--compare", nargs=2, metavar=("BEFORE_JSONL", "AFTER_JSONL"), type=Path)
    parser.add_argument("--task-key", help="expected task key for --compare")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        if args.project:
            if not args.project.is_dir():
                raise AuditError("--project must be an existing directory")
            result = audit_project(args.project)
        elif args.usage_jsonl:
            if not args.usage_jsonl.is_file():
                raise AuditError("--usage-jsonl must be an existing file")
            result = audit_usage(args.usage_jsonl)
        elif args.preflight:
            result = preflight(args.preflight)
        else:
            result = compare_usage(args.compare[0], args.compare[1], args.task_key)
    except BudgetBlocked as exc:
        print(json.dumps(exc.result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 3
    except (OSError, AuditError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
