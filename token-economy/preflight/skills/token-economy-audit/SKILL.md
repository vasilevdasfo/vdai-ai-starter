---
name: token-economy-audit
description: Audit a local project or exported AI usage counters when a person asks to reduce repeated context, inspect token usage, compare cached and uncached input, or choose a smaller working scope. Do not use it to predict bills, promise savings, change provider settings, delete context, or scan private folders without an exact path.
---

# Token Economy Audit

Turn “I spend too many tokens” into one measured, reversible improvement.

## Input

- An exact project directory, or
- a JSONL export with non-negative integer fields `input_tokens`,
  `cached_input_tokens`, and `output_tokens` (top-level or under `usage`).

Never scan the home directory. Never request API keys or account access.

## Workflow

1. Ask for one real task and one exact source path.
2. Create a version-1 selection manifest with an exact project root, allowed
   files or Markdown sections, a stable-prefix list, and preflight limits.
3. Run `--preflight` before a model call. Exit `3` means the caller must stop;
   the tool itself never invokes a model.
4. Separate exact counters from text-size estimates.
5. Name one bottleneck: repeated stable context, overly broad source loading,
   mixed tasks, repeated failed calls, or no measurable usage data.
6. Compare only the same `task_key` where both final rows have `accepted=true`.
7. Keep cache enabled. Do not delete or rewrite source material automatically.

```bash
python3 token_economy_audit.py --project /exact/project --pretty
python3 token_economy_audit.py --usage-jsonl /exact/usage.jsonl --pretty
python3 token_economy_audit.py --preflight example-manifest.json --pretty
python3 token_economy_audit.py --compare before.jsonl after.jsonl --task-key one-task --pretty
```

## Output

Return: observed facts, estimates with their basis, one recommendation, the
measurement still missing, and the next comparison. A large file is a review
candidate, not proof of waste. Multiple instruction files may be intentional.

## Gate

Do not claim dollars, percentages, or saved tokens without comparable observed
before/after counters for the same accepted task. Treat `ALLOW` as an input
budget check, not proof that the later model call used this manifest. Do not change model, reasoning,
permissions, cache, retention, files, or provider configuration without the
person's explicit choice and a readback.

## Acceptance

- positive: exact JSONL totals and derived uncached input are correct;
- negative: malformed/negative counters fail closed;
- boundary: empty JSONL reports zero calls and `cache_ratio: null`;
- project mode labels every count as an estimate and performs no writes;
- preflight returns `ALLOW` only inside both limits and machine exit `3` on
  `BLOCK`; path escape, duplicate source and missing/ambiguous section fail;
- before/after rejects mismatched task keys and unaccepted results.
