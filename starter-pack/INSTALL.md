# Install VDAI AI Starter

## Codex · macOS / Linux

For a clean profile run:

`bash install.sh ~/.codex`

If `~/.codex/AGENTS.md` or any target Skill already exists, the installer stops. Review and merge deliberately; it never overwrites your working system.

## Claude Code · macOS / Linux

`bash install.sh ~/.claude`

The installer also copies `VDAI_AI_STARTER_USAGE.md` and `vdai-statusline.py`. Review the settings snippet in the usage guide before merging it into `~/.claude/settings.json`. Existing status-line settings are never overwritten automatically. Claude Code can then expose exact current-context input/output tokens and context percentage; these are not labeled as Codex cumulative counters.

## Windows PowerShell

From this unpacked folder run:

`powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target "$env:USERPROFILE\.codex"`

## Manual installation

For Codex, merge `AGENTS.md` into `~/.codex/AGENTS.md`, copy `VERIFICATION.md` as `~/.codex/VDAI_AI_STARTER_VERIFICATION.md`, and copy the eleven folders inside `skills/` into `~/.codex/skills/`. For Claude Code, use `CLAUDE.md`, `~/.claude/VDAI_AI_STARTER_VERIFICATION.md`, `CLAUDE_USAGE.md`, `tools/claude_statusline.py`, and `~/.claude/skills/`. Restart the app or open a new task. Existing files and status-line settings must be merged deliberately.

## Included Skills

- `problem-os` — P/U/L/R/N, owner, gate and proof;
- `economy-guard` — 🟩/🟨/🟥 task weight;
- `numbering-canon` — task-local numbering that continues across replies;
- `devils-advocate` — material critique before a risky decision;
- `sos`, `sos1`, `sos2` — standard, deep and maximum useful routing;
- `boardroom` — eight strategic perspectives and judge synthesis;
- `problem-to-action`, `repeatable-work`, `numbered-next` — beginner compatibility helpers.

## Verify

Turn 1:

`I need to improve how I use AI. Diagnose one real task with P/U/L/R/N and finish with numbered next actions where 0 means all safe actions.`

Installation is successful only when `manifest.json` is satisfied: all eleven Skills and `VDAI_AI_STARTER_VERIFICATION.md` are discovered, the correct instruction layer is merged, and both turns in `VERIFICATION.md` pass. A partial set is FAIL.

Turn 2 in the same task:

`Continue the same topic. Show the next available routes without reusing any positive number from your previous answer.`

The second reply fails if it starts again at `1`, omits the platform-appropriate token/context weight block or the visible `🟩/🟨/🟥` scale, uses a heading in the wrong language, or drops the observable result/blocker.
