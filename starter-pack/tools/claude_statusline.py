#!/usr/bin/env python3
"""Render and snapshot the official Claude Code status-line JSON."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path


def compact(value: object) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0
    if number >= 1_000_000:
        return f"{number / 1_000_000:.2f}m"
    if number >= 1_000:
        return f"{number / 1_000:.1f}k"
    return str(int(number))


def safe_session_id(value: object) -> str:
    session_id = str(value or "unknown")
    return re.sub(r"[^A-Za-z0-9._-]", "_", session_id)[:128] or "unknown"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        print("VDAI · Claude usage unavailable")
        return 0

    session_id = safe_session_id(payload.get("session_id"))
    context = payload.get("context_window") or {}
    cost = payload.get("cost") or {}
    snapshot = {
        "source": "claude-code-statusline",
        "session_id": payload.get("session_id"),
        "transcript_path": payload.get("transcript_path"),
        "model": (payload.get("model") or {}).get("display_name"),
        "version": payload.get("version"),
        "context_window": {
            "total_input_tokens": context.get("total_input_tokens"),
            "total_output_tokens": context.get("total_output_tokens"),
            "used_percentage": context.get("used_percentage"),
            "remaining_percentage": context.get("remaining_percentage"),
            "context_window_size": context.get("context_window_size"),
        },
        "cost": {"total_cost_usd": cost.get("total_cost_usd")},
    }
    snapshot_dir = Path.home() / ".claude" / "vdai-task-weight"
    atomic_json(snapshot_dir / f"{session_id}.json", snapshot)
    atomic_json(snapshot_dir / "latest.json", snapshot)

    model = snapshot.get("model") or "Claude"
    used = context.get("used_percentage")
    used_text = "--" if used is None else f"{used}%"
    input_text = compact(context.get("total_input_tokens"))
    output_text = compact(context.get("total_output_tokens"))
    cost_value = cost.get("total_cost_usd")
    cost_text = "" if cost_value is None else f" · ${float(cost_value):.2f}"
    print(f"{model} · ctx {used_text} · in {input_text} · out {output_text}{cost_text} · {session_id[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
