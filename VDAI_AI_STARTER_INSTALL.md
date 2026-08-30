# VDAI AI Starter — transparent Codex install

Open https://vdai.me/ai-starter/ and use **Copy prompt for Codex**. The prompt makes Codex inspect the complete public Dmitrii Pro set, preserve existing files, explain both permission modes and wait for an explicit choice before changing `config.toml`.

The complete set includes task weight and color, ProblemOS, persistent task-local numbering, critique, SOS/SOS1/SOS2, boardroom with eight perspectives, and three beginner compatibility helpers.

Codex also needs the persistent instruction layer from `starter-pack/AGENTS.md`. Skills alone do not force every ordinary task to keep the same format. The installer stops instead of overwriting an existing `~/.codex/AGENTS.md`; merge it deliberately, restart Codex, and run both verification turns.

Recommended mode:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

Full access is never enabled automatically. Use it only by explicit choice in a small isolated trusted folder without secrets.

For Codex + Claude Code collaboration, use **Connect Codex + Claude** on the same page. Start with a file/Git handoff and one active writer; add MCP only after that workflow passes a real task.
