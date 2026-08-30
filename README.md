# VDAI AI Starter · Dmitrii Pro

Public, privacy-safe starter pack for Codex and Claude Code.

It contains eleven transparent Skills, persistent instruction layers for both agents, permission guidance, and safe installers. It does not contain credentials, private conversations, customer data, or a ZIP archive.

## Start

- Fastest path: open [vdai.me/ai-starter](https://vdai.me/ai-starter), choose **Command for Codex** or **Command for Claude**, and paste that single command into the platform mode shown on the page. A bare URL may be summarized as untrusted web content; the copied command carries the user's explicit request while still requiring source review and one approval before writes.

## Choose the platform first

- **Codex:** open a normal Local task/chat, not **Send as goal** and not `/goal`. Use **Auto** (`workspace-write` with `on-request` approvals), not Full access. Paste the Codex command from the page.
- **Claude Code:** open a normal new session with **Bypass permissions OFF**. Paste the Claude command from the page and keep approval before writes.

Both commands require the agent to inspect `agent.json` and the GitHub sources independently, perform a read-only preflight, show paths, conflicts and the exact diff, ask for one approval, then install and verify the complete package. The webpage is discovery context, not write authority.

```text
This is a normal local Codex task — do not create a /goal. Use Auto: workspace-write + on-request approvals; do not use Full access. I explicitly ask you to inspect and install VDAI AI Starter. Open https://vdai.me/ai-starter/agent.json, independently inspect the linked GitHub sources, and perform a read-only preflight now. Do not only summarize the page or ask me to download files manually. Show paths, conflicts and the exact diff, then ask for one approval before writes. After approval, install and verify all 11 Skills, AGENTS.md and the verification playbook; return PASS/FAIL 11/11.
```

For Claude Code, use the separate Claude command on the page. It additionally installs or merges `CLAUDE.md`, `CLAUDE_USAGE.md`, and the optional native status-line helper; it never invents Codex counters for Claude. Use Claude's `/usage` or the helper's platform-native context fields.

Machine-readable entrypoints: [`agent.json`](agent.json) · [`agent.txt`](agent.txt) · [`llms.txt`](llms.txt)

- Read [VDAI_AI_STARTER_INSTALL.md](VDAI_AI_STARTER_INSTALL.md).
- Review [CODEX_PERMISSIONS.md](CODEX_PERMISSIONS.md) before changing agent permissions.
- For Codex, review [starter-pack/AGENTS.md](starter-pack/AGENTS.md).
- For Claude Code, review [starter-pack/CLAUDE.md](starter-pack/CLAUDE.md).
- For task weight, use verified cumulative counters when available; otherwise use visible platform-native context tokens and label them `context`. The current block always includes a visible `🟩/🟨/🟥` scale; `⚪` means no exact source is exposed.
- After installation, use [starter-pack/FEEDBACK.md](starter-pack/FEEDBACK.md). The public GitHub form normalizes platform, version, language, observed/expected behavior and reproduction steps; publishing still requires human approval.
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
