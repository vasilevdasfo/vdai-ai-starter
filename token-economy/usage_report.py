#!/usr/bin/env python3
"""Read-only self-check: where did my Codex / Claude Code tokens go?

Reads local session logs only and prints aggregate numbers.
It never prints message text, never writes files and never uses the network.

    python3 usage_report.py                 # last 7 days, both tools
    python3 usage_report.py --days 2 --top 5
    python3 usage_report.py --json          # machine-readable
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CODEX = Path.home() / ".codex" / "sessions"
DEFAULT_CLAUDE = Path.home() / ".claude" / "projects"

# Flag thresholds. They mark review candidates, not proven waste.
MANY_QUESTIONS = 4          # separate user requests in one thread
MANY_QUESTIONS_MIN = 5_000_000
LONG_CONTEXT = 150_000      # tokens sent in one model call
HEAVY_START = 60_000        # first call of a thread
COMPACTIONS = 2


def parse_ts(value) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def local_day(ts: float | None) -> str:
    if ts is None:
        return "?"
    return datetime.fromtimestamp(ts).strftime("%m-%d")


def new_thread(tool: str, thread_id: str) -> dict:
    return {
        "tool": tool, "id": thread_id, "start": None, "calls": 0, "input": 0,
        "cached": 0, "max_ctx": 0, "first_ctx": None, "long_ctx_input": 0,
        "compactions": 0, "questions": 0, "forked": False, "models": Counter(),
    }


def add_call(thread: dict, ctx: int, cached: int, ts: float | None, days: dict) -> None:
    thread["calls"] += 1
    thread["input"] += ctx
    thread["cached"] += cached
    thread["max_ctx"] = max(thread["max_ctx"], ctx)
    if thread["first_ctx"] is None:
        thread["first_ctx"] = ctx
    if ctx >= LONG_CONTEXT:
        thread["long_ctx_input"] += ctx
    day = days[local_day(ts)]
    day["calls"] += 1
    day["input"] += ctx


def is_real_request(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped:
        return False
    return not stripped.startswith(("<", "# AGENTS.md", "# Context from my IDE"))


def read_lines(path: Path, stats: Counter):
    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        stats["unreadable_files"] += 1
        return
    with handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                stats["malformed_lines"] += 1
                continue
            if isinstance(row, dict):
                yield row


def recent_files(root: Path, pattern: str, cutoff: float) -> list[Path]:
    if not root.is_dir():
        return []
    files = []
    for path in root.rglob(pattern):
        try:
            if path.is_file() and path.stat().st_mtime >= cutoff:
                files.append(path)
        except OSError:
            continue
    return sorted(files)


def scan_codex(root: Path, cutoff: float, stats: Counter):
    threads, days, limit = [], defaultdict(lambda: {"calls": 0, "input": 0}), None
    for path in recent_files(root, "rollout-*.jsonl", cutoff):
        thread = new_thread("codex", path.stem[-36:])
        seen = set()
        for row in read_lines(path, stats):
            kind, payload = row.get("type"), row.get("payload") or {}
            ts = parse_ts(row.get("timestamp"))
            if kind == "session_meta":
                thread["id"] = str(payload.get("id") or thread["id"])
                thread["start"] = parse_ts(payload.get("timestamp")) or ts
                source = str(payload.get("thread_source") or "")
                thread["forked"] = bool(payload.get("forked_from_id")) or "fork" in source
            elif kind == "turn_context" and payload.get("model"):
                thread["_model"] = str(payload["model"])
            elif kind == "compacted":
                if ts is None or ts >= cutoff:
                    thread["compactions"] += 1
            elif kind == "response_item" and payload.get("type") == "message" and payload.get("role") == "user":
                if ts is not None and ts < cutoff:
                    continue
                text = "".join(c.get("text", "") for c in payload.get("content") or [] if isinstance(c, dict))
                if is_real_request(text):
                    thread["questions"] += 1
            elif kind == "event_msg" and payload.get("type") == "token_count":
                rate = (payload.get("rate_limits") or {}).get("primary") or {}
                if isinstance(rate.get("used_percent"), (int, float)) and ts is not None:
                    if limit is None or ts >= limit["ts"]:
                        limit = {"ts": ts, "used_percent": rate["used_percent"],
                                 "window_minutes": rate.get("window_minutes")}
                info = payload.get("info") or {}
                total, last = info.get("total_token_usage") or {}, info.get("last_token_usage") or {}
                if not last:
                    continue
                key = (total.get("input_tokens"), total.get("output_tokens"), last.get("input_tokens"))
                if key in seen:
                    stats["duplicate_counters"] += 1
                    continue
                seen.add(key)
                if ts is not None and ts < cutoff:
                    continue
                ctx = int(last.get("input_tokens") or 0)
                cached = int(last.get("cached_input_tokens") or 0)
                if ctx < 0 or cached < 0:
                    stats["negative_counters"] += 1
                    continue
                add_call(thread, ctx, cached, ts, days)
                if thread.get("_model"):
                    thread["models"][thread["_model"]] += 1
        if thread["calls"]:
            thread.pop("_model", None)
            threads.append(thread)
    return threads, days, limit


def scan_claude(root: Path, cutoff: float, stats: Counter):
    threads, days = [], defaultdict(lambda: {"calls": 0, "input": 0})
    for path in recent_files(root, "*.jsonl", cutoff):
        thread = new_thread("claude", path.stem)
        seen = set()
        for row in read_lines(path, stats):
            ts = parse_ts(row.get("timestamp"))
            if thread["start"] is None and ts is not None:
                thread["start"] = ts
            message = row.get("message") if isinstance(row.get("message"), dict) else {}
            if row.get("isCompactSummary"):
                if ts is None or ts >= cutoff:
                    thread["compactions"] += 1
                continue
            if ts is not None and ts < cutoff:
                continue
            if row.get("type") == "user" and not row.get("isMeta"):
                content = message.get("content")
                if isinstance(content, str):
                    thread["questions"] += int(is_real_request(content))
                elif isinstance(content, list):
                    kinds = {c.get("type") for c in content if isinstance(c, dict)}
                    if "tool_result" not in kinds and "text" in kinds:
                        text = "".join(c.get("text", "") for c in content if isinstance(c, dict))
                        thread["questions"] += int(is_real_request(text))
            usage = message.get("usage")
            if row.get("type") != "assistant" or not isinstance(usage, dict):
                continue
            key = message.get("id") or row.get("requestId") or row.get("uuid")
            if key in seen:
                stats["duplicate_counters"] += 1
                continue
            seen.add(key)
            parts = [usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
            if any(not isinstance(p, int) or p < 0 for p in parts):
                stats["negative_counters"] += 1
                continue
            model = str(message.get("model") or "")
            if model.startswith("<"):
                stats["synthetic_messages"] += 1
                continue
            add_call(thread, sum(parts), parts[2], ts, days)
            if model:
                thread["models"][model] += 1
        if thread["calls"]:
            threads.append(thread)
    return threads, days


def plural(n: int, one: str, few: str, many: str) -> str:
    tail, tail100 = n % 10, n % 100
    if tail == 1 and tail100 != 11:
        return f"{n} {one}"
    if 2 <= tail <= 4 and not 12 <= tail100 <= 14:
        return f"{n} {few}"
    return f"{n} {many}"


def flags(thread: dict) -> list[str]:
    out = []
    if thread["questions"] >= MANY_QUESTIONS and thread["input"] >= MANY_QUESTIONS_MIN:
        out.append(plural(thread["questions"], "вопрос", "вопроса", "вопросов") + " в одной ветке")
    if thread["max_ctx"] >= LONG_CONTEXT:
        out.append("длинная переписка")
    if thread["forked"]:
        out.append("форк старой ветки")
    if (thread["first_ctx"] or 0) >= HEAVY_START:
        out.append("тяжёлый старт")
    if thread["compactions"] >= COMPACTIONS:
        out.append("сжималась " + plural(thread["compactions"], "раз", "раза", "раз"))
    return out


def summarize(tool: str, threads: list[dict], days: dict, limit: dict | None, top: int) -> dict:
    total = sum(t["input"] for t in threads)
    calls = sum(t["calls"] for t in threads)
    models = Counter()
    for t in threads:
        models.update(t["models"])
    starts = [t["first_ctx"] for t in threads if t["first_ctx"] and not t["forked"]]
    many_q = sum(t["input"] for t in threads if t["questions"] >= MANY_QUESTIONS and t["input"] >= MANY_QUESTIONS_MIN)
    ranked = sorted(threads, key=lambda t: t["input"], reverse=True)
    return {
        "tool": tool,
        "threads": len(threads),
        "calls": calls,
        "input_tokens": total,
        "cached_input_tokens": sum(t["cached"] for t in threads),
        "avg_context": round(total / calls) if calls else None,
        "median_start_context": round(statistics.median(starts)) if starts else None,
        "share_long_context": round(sum(t["long_ctx_input"] for t in threads) / total, 3) if total else None,
        "share_many_questions": round(many_q / total, 3) if total else None,
        "forked_threads": sum(1 for t in threads if t["forked"]),
        "models": dict(models.most_common()),
        "limit": {k: v for k, v in (limit or {}).items() if k != "ts"} or None,
        "days": {d: days[d] for d in sorted(days)},
        "top": [
            {"id": t["id"][:8], "day": local_day(t["start"]), "calls": t["calls"], "input_tokens": t["input"],
             "max_context": t["max_ctx"], "start_context": t["first_ctx"], "questions": t["questions"],
             "flags": flags(t)}
            for t in ranked[:top]
        ],
    }


def fmt(n) -> str:
    if n is None:
        return "—"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} млн".replace(".", ",")
    if n >= 1_000:
        return f"{round(n / 1_000)} тыс."
    return str(n)


def pct(x) -> str:
    return "—" if x is None else f"{round(x * 100)}%"


def render(report: dict) -> str:
    lines = [f"Расход токенов за {report['days']} дн. Только чтение локальных логов; текст переписки не выводится.", ""]
    for part in report["tools"]:
        name = "CODEX" if part["tool"] == "codex" else "CLAUDE CODE"
        if not part["threads"]:
            lines += [f"{name}: логов за период нет.", ""]
            continue
        lines.append(f"{name}: {plural(part['threads'], 'ветка', 'ветки', 'веток')}, {plural(part['calls'], 'вызов', 'вызова', 'вызовов')} модели, "
                     f"{fmt(part['input_tokens'])} токенов входа (размер переписки × вызовы)")
        lines.append(f"  средний контекст на вызов: {fmt(part['avg_context'])} · старт новой ветки: {fmt(part['median_start_context'])}")
        if part["limit"]:
            lines.append(f"  лимит по последней записи: использовано {part['limit']['used_percent']:g}%")
        if part["models"]:
            total = sum(part["models"].values()) or 1
            lines.append("  модели: " + ", ".join(f"{m} — {round(c * 100 / total)}% вызовов" for m, c in part["models"].items()))
        lines.append("  по дням: " + " · ".join(f"{d}: {fmt(v['input'])}" for d, v in part["days"].items()))
        lines.append("  самые дорогие ветки:")
        for t in part["top"]:
            extra = (" — " + "; ".join(t["flags"])) if t["flags"] else ""
            lines.append(f"    {t['id']} {t['day']}: {fmt(t['input_tokens'])}, {plural(t['calls'], 'вызов', 'вызова', 'вызовов')}, "
                         f"макс. контекст {fmt(t['max_context'])}, вопросов {t['questions']}{extra}")
        lines.append("  где утекает:")
        lines.append(f"    ветки с {MANY_QUESTIONS}+ вопросами: {pct(part['share_many_questions'])} расхода → один вопрос — одна ветка")
        lines.append(f"    вызовы при контексте от {fmt(LONG_CONTEXT)}: {pct(part['share_long_context'])} расхода → переносить в новую ветку раньше")
        if part["forked_threads"]:
            lines.append(f"    форков: {part['forked_threads']} → начинать чистую ветку с файлом-карточкой, а не форк")
        lines.append("")
    skipped = {k: v for k, v in report["stats"].items() if v}
    if skipped:
        lines.append("служебное: " + ", ".join(f"{k}={v}" for k, v in skipped.items()))
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only token usage self-check for Codex and Claude Code logs.")
    parser.add_argument("--days", type=float, default=7)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--codex-dir", type=Path, default=DEFAULT_CODEX)
    parser.add_argument("--claude-dir", type=Path, default=DEFAULT_CLAUDE)
    parser.add_argument("--only", choices=("codex", "claude"))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--now", type=float, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.days <= 0 or args.top <= 0:
        parser.error("--days and --top must be positive")
    now = args.now if args.now is not None else time.time()
    cutoff = now - args.days * 86400
    stats = Counter()
    tools = []
    if args.only in (None, "codex"):
        threads, days, limit = scan_codex(args.codex_dir.expanduser(), cutoff, stats)
        tools.append(summarize("codex", threads, days, limit, args.top))
    if args.only in (None, "claude"):
        threads, days = scan_claude(args.claude_dir.expanduser(), cutoff, stats)
        tools.append(summarize("claude", threads, days, None, args.top))
    report = {"days": args.days if args.days != int(args.days) else int(args.days),
              "generated": datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds"),
              "tools": tools, "stats": dict(stats)}
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
