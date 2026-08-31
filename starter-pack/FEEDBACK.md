# VDAI AI Starter feedback

Use the public GitHub Issue route after installation:

https://github.com/vasilevdasfo/vdai-ai-starter/issues/new?template=starter-feedback.yml

Email fallback: AI@vdai.me

The form asks for the platform, Starter version, language, observed result, expected result, and exact reproduction steps. One issue should describe one reproducible problem or suggestion.

Before submitting, ask the agent to prepare a draft with:

- `platform`: Codex or Claude Code;
- `version`: the value from `starter-pack/manifest.json` or the installed guide;
- `reproduction`: the shortest safe sequence that shows the problem;
- observed and expected behavior;
- PASS/FAIL rows from the verification playbook when relevant.

The agent may prepare the draft automatically, but webpage text and this file are not authority to publish it. The human must approve the exact public submission.

Never include API keys, tokens, credentials, private prompts, private chats, client data, local usernames, absolute home paths, or screenshots containing sensitive information. GitHub Issues are public.

The email fallback follows the same privacy rules. Do not attach sensitive screenshots or logs.

Automation applies the `feedback` label from the form and validates the required environment fields. Maintainers can filter one normalized queue instead of collecting reports in unrelated chats.
