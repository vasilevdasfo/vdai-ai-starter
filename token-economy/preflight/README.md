# Token Economy Starter

Local, read-only preflight software plus a companion Skill and Club copy draft.

```bash
python3 token_economy_audit.py --project /exact/project --pretty
python3 token_economy_audit.py --preflight example-manifest.json --pretty
python3 token_economy_audit.py --compare before.jsonl after.jsonl --task-key one-task --pretty
python3 -m unittest discover -s tests -v
```

`--preflight` validates an explicit source/section selection before a model call
and exits `3` when its file or estimated-token budget is exceeded. It emits a
stable-prefix hash but never sends content to a model. `--compare` reports a
percentage only for the same accepted task in both exact-counter exports.

The project scan estimates text tokens from character count and labels the
estimate. No mode changes files, settings or accounts, and no mode calculates
price. Enforcement+read-only does not prove a caller obeyed the gate; compose
the command with `&&` before the model invocation.
