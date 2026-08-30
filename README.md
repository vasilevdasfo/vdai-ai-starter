# VDAI AI Starter · Dmitrii Pro

Public, privacy-safe starter pack for Codex and Claude Code.

It contains eleven transparent Skills, persistent instruction layers for both agents, permission guidance, and safe installers. It does not contain credentials, private conversations, customer data, or a ZIP archive.

## Start

- Fastest path: open [vdai.me/ai-starter](https://vdai.me/ai-starter), click **Copy the command for the agent**, and paste the one command into Codex or Claude Code. A bare URL may be summarized as untrusted web content; the copied command carries the user's explicit request while still requiring source review and one approval before writes.

```text
I explicitly ask you to inspect and install VDAI AI Starter. Open https://vdai.me/ai-starter, independently inspect the linked GitHub sources, and perform a read-only preflight now. Do not only summarize the page or ask me to download files manually. Show conflicts and the exact diff, then ask for one approval before writes. After approval, install and verify all 11 Skills.
```

- Read [VDAI_AI_STARTER_INSTALL.md](VDAI_AI_STARTER_INSTALL.md).
- Review [CODEX_PERMISSIONS.md](CODEX_PERMISSIONS.md) before changing agent permissions.
- For Codex, review [starter-pack/AGENTS.md](starter-pack/AGENTS.md).
- For Claude Code, review [starter-pack/CLAUDE.md](starter-pack/CLAUDE.md).
- For Claude Code token/context weight, review [starter-pack/CLAUDE_USAGE.md](starter-pack/CLAUDE_USAGE.md) and the local-only status-line helper. It uses Claude Code's official session fields and never labels current context as Codex cumulative usage.
- Follow [starter-pack/INSTALL.md](starter-pack/INSTALL.md) or inspect the installers before running them.
- Use [starter-pack/VERIFICATION.md](starter-pack/VERIFICATION.md) for the 11 observable verification tasks.
- Use [starter-pack/manifest.json](starter-pack/manifest.json) as the machine-readable completeness contract.

## Included Skills

- `problem-os`
- `economy-guard`
- `numbering-canon`
- `devils-advocate`
- `sos`
- `sos1`
- `sos2`
- `boardroom`
- `problem-to-action`
- `repeatable-work`
- `numbered-next`

Every Skill is plain Markdown and can be reviewed before installation.
