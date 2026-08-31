# VDAI AI Starter — transparent Codex install

Open https://vdai.me/ai-starter/ and choose the button for your platform.

- For Codex, start a normal Local task/chat, not Send as goal or `/goal`; select Auto (`workspace-write` + `on-request`), not Full access, then paste **Command for Codex**.
- For Claude Code, start a normal new session with Bypass permissions OFF, then paste **Command for Claude** and keep approval before writes.

The prompt makes the agent inspect the complete public VDAI AI Starter set, preserve existing files, show the exact preflight diff and wait for one approval before writing.

The complete set includes task weight and color, ProblemOS, persistent task-local numbering, critique, SOS/SOS1/SOS2, boardroom with eight perspectives, and three beginner compatibility helpers.

Codex also needs the persistent instruction layer from `starter-pack/AGENTS.md`. Skills alone do not force every ordinary task to keep the same format. The installer stops instead of overwriting an existing `~/.codex/AGENTS.md`; merge it deliberately, restart Codex, and run both verification turns.

Recommended mode:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

Full access is never enabled automatically. Use it only by explicit choice in a small isolated trusted folder without secrets.

For Claude Code, the complete install also includes `CLAUDE.md`, `CLAUDE_USAGE.md`, and the optional native status-line helper. Use `/usage` or the helper; do not translate Claude context into invented Codex cumulative counters.
