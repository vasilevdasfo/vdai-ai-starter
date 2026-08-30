---
name: economy-guard
description: Show task weight and prevent long, expensive, duplicated AI work without a verified outcome.
---

# Economy Guard

Use one owner, one source of truth, one outcome, and one proof. Prefer one bounded pass; do not mix build, browser QA, deploy, and external send in one pass.

When exact runtime counters are available, show a compact H2 block immediately before numbered actions:

- `🟩` — continue: below 2M cumulative input and below 40 calls.
- `🟨` — checkpoint and split: at least 2M input, 40 calls, two consecutive inputs over 100k, or 12 calls in the current turn.
- `🟥` — stop and close out: at least 10M input or 100 calls.

Format: `## 🟩 ВЕС ЭТОЙ ЗАДАЧИ: **<compact cumulative> cumulative / <compact uncached> uncached** · **<calls> calls** · CONTINUE`.

Never invent counters. If exact counters or identity proof are unavailable, say `weight unavailable` and do not display guessed numbers.

## Identity and counting rules

- Weight belongs to one exact current task/thread. A source task and its continuation have different identities and counters.
- Accept counters only when requested thread ID, runtime thread/session ID, rollout ID, and the single live rollout agree.
- A working directory match is not identity proof.
- Use compact readable units such as `382 тыс.` or `3,62 млн`; do not print long raw integers in the user-facing block.
- Count the current task's cumulative input, uncached input, and calls from the same authoritative readback.

At yellow, finish the current proof and split before beginning a new phase. At red, stop new work and create a closeout/checkpoint. Do not start background loops, broad research, deploy, browser QA, and external delivery in one pass merely because tools are available.

Efficiency must not replace fidelity. Reuse stable context and bounded readback, but keep every explicit requirement and required proof.
