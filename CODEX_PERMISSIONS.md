# Codex permissions for VDAI AI Starter

Choose deliberately before changing `~/.codex/config.toml`.

## 1. Recommended everyday mode

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

Codex may edit the selected workspace. Actions outside it or actions requiring broader authority ask for approval.

## 2. Explicit full access

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

Use this only for a small isolated trusted folder with no credentials, private data, payment access or unrelated files. It removes the normal filesystem boundary and approval pause.

Never enable full access automatically. Preserve the rest of the config, read these two keys back after the change, and restart Codex.

