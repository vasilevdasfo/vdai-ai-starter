#!/usr/bin/env python3
"""Read-only exact-thread Codex token weight. No network and no writes."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

UUID = re.compile(r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


def find_rollout(thread_id: str, root: Path) -> Path:
    live = list((root / "sessions").glob(f"**/rollout-*{thread_id}.jsonl"))
    if len(live) != 1:
        raise SystemExit(f"UNAVAILABLE: expected one live rollout for {thread_id}, found {len(live)}")
    return live[0]


def analyze(path: Path, requested: str) -> dict:
    session_id = None
    inputs: list[int] = []
    cached: list[int] = []
    calls = 0
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            payload = obj.get("payload") or {}
            if obj.get("type") == "session_meta":
                session_id = payload.get("id") or session_id
            if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                usage = ((payload.get("info") or {}).get("last_token_usage") or {})
                if usage:
                    inputs.append(int(usage.get("input_tokens") or 0))
                    cached.append(int(usage.get("cached_input_tokens") or 0))
            if obj.get("type") == "response_item" and payload.get("type") in {"custom_tool_call", "function_call", "mcpToolCall"}:
                calls += 1
    env_ids = [value for value in (os.getenv("CODEX_THREAD_ID"), os.getenv("CODEX_SESSION_ID")) if value]
    if session_id != requested or any(value != requested for value in env_ids):
        raise SystemExit("UNAVAILABLE: exact-thread identity mismatch")
    total = sum(inputs)
    uncached = max(0, total - sum(cached))
    status = "RED" if total >= 10_000_000 or calls >= 100 else "YELLOW" if total >= 2_000_000 or calls >= 40 else "GREEN"
    return {"thread_id": requested, "cumulative_input": total, "uncached_input": uncached, "calls": calls, "status": status}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread-id", default=os.getenv("CODEX_THREAD_ID") or os.getenv("CODEX_SESSION_ID"))
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.thread_id or not UUID.fullmatch(args.thread_id):
        raise SystemExit("UNAVAILABLE: pass the exact current --thread-id")
    result = analyze(find_rollout(args.thread_id, args.codex_root), args.thread_id)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return
    icon, action = {"GREEN": ("🟩", "CONTINUE"), "YELLOW": ("🟨", "CHECKPOINT_AND_SPLIT"), "RED": ("🟥", "STOP_AND_CLOSEOUT")}[result["status"]]
    print(f"{icon} {result['cumulative_input']} cumulative / {result['uncached_input']} uncached · {result['calls']} calls · {action}")


if __name__ == "__main__":
    main()
