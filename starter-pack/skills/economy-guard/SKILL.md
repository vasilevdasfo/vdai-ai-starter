---
name: economy-guard
description: Show task weight and prevent long, expensive, duplicated AI work without a verified outcome.
---

# Economy Guard

Use one owner, one source of truth, one outcome, and one proof. Prefer one bounded pass; do not mix build, browser QA, deploy, and external send in one pass.

First detect the current platform and the language of the user's current message. Examples never override the user's language.

## Platform-native counters

For Codex, run the installed `vdai-task-weight.py` with the exact current thread ID before declaring weight unavailable. It reads only the one live local rollout, fails closed on identity mismatch, and returns cumulative input, uncached input, calls, and status. If the helper cannot prove identity but the native Codex Status panel visibly exposes context tokens, use those displayed values as an explicitly labeled fallback; never relabel context as cumulative.

For Claude Code, use only its official `/usage` or `statusLine` data. Read `CLAUDE_USAGE.md` when installed. Claude Code 2.1.132+ exposes current context input/output tokens and context percentage, not Codex cumulative/call counters. Label them `context`, never `cumulative`.

When exact runtime counters are available, show a compact H2 block immediately before numbered actions:

- `🟩` — continue: below 2M cumulative input and below 40 calls.
- `🟨` — checkpoint and split: at least 2M input, 40 calls, two consecutive inputs over 100k, or 12 calls in the current turn.
- `🟥` — stop and close out: at least 10M input or 100 calls.

Codex English format: `## 🟩 TASK WEIGHT: **<compact cumulative> cumulative / <compact uncached> uncached** · **<calls> calls** · CONTINUE`.

Claude Code English format: `## 🟩 TASK WEIGHT: **<compact input> context input / <compact output> output** · **<used>% context** · CONTINUE`.

Localized headings:

- English: `TASK WEIGHT`
- Russian: `ВЕС ЭТОЙ ЗАДАЧИ`
- Spanish: `PESO DE LA TAREA`
- Polish: `WAGA ZADANIA`

For platform-native context fallback, use `🟩` below 70% used, `🟨` from 70% through 89%, and `🟥` at 90% or above. Example: `## 🟩 TASK WEIGHT: **37,889 / 250k context tokens** · **15% used** · CONTINUE`.

Never invent counters. If neither verified cumulative data nor visible platform-native context data is available, show a localized gray current block: `## ⚪ TASK WEIGHT: unavailable · exact counters not exposed`. Always follow every current block with `Scale: 🟩 CONTINUE · 🟨 CHECKPOINT_AND_SPLIT · 🟥 STOP_AND_CLOSEOUT`. Gray means unknown, not safe. Do not assign a colored current status without verified cumulative or native-context values. Do not emit a Russian heading in an English, Spanish, or Polish conversation.

## Identity and counting rules

- Weight belongs to one exact current task/thread. A source task and its continuation have different identities and counters.
- Accept counters only when requested thread ID, runtime thread/session ID, rollout ID, and the single live rollout agree.
- A working directory match is not identity proof.
- Use compact readable units that match the user's language, such as `382k`, `3.62m`, `382 тыс.`, or `3,62 млн`; do not print long raw integers in the user-facing block.
- Count the current task's cumulative input, uncached input, and calls from the same authoritative readback.

At yellow, finish the current proof and split before beginning a new phase. At red, stop new work and create a closeout/checkpoint. Do not start background loops, broad research, deploy, browser QA, and external delivery in one pass merely because tools are available.

Efficiency must not replace fidelity. Reuse stable context and bounded readback, but keep every explicit requirement and required proof.
