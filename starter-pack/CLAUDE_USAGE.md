# Claude Code task-weight source

Claude Code and Codex expose different counters. Never print a Codex cumulative/calls block in Claude Code.

Claude Code's supported sources are:

- `/usage` for current session usage;
- the official `statusLine` JSON fields: `session_id`, `context_window.total_input_tokens`, `context_window.total_output_tokens`, `context_window.used_percentage`, `context_window.context_window_size`, and `cost.total_cost_usd`.

The included `tools/claude_statusline.py` accepts the official status-line JSON on stdin, prints a compact language-neutral line, and stores a local snapshot in `~/.claude/vdai-task-weight/`. It sends no data anywhere.

After explicit approval, copy it to `~/.claude/vdai-statusline.py` and merge this into `~/.claude/settings.json` only when it does not overwrite an existing status line:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/vdai-statusline.py",
    "padding": 0
  }
}
```

If `statusLine` already exists, show the existing and proposed settings diff and wait for approval. Do not replace it silently. A safe alternative is to use `/usage` without changing settings.

As of Claude Code 2.1.132, `context_window.total_input_tokens` and `total_output_tokens` describe the current context window, not cumulative session totals. Label them `context`, never `cumulative`.

Language rule:

- answer in the language of the user's current message;
- English: `TASK WEIGHT`;
- Russian: `ВЕС ЭТОЙ ЗАДАЧИ`;
- Spanish: `PESO DE LA TAREA`;
- Polish: `WAGA ZADANIA`;
- examples never override the user's language.

If neither exact status-line data nor `/usage` is available, say so in the user's language and do not invent numbers.
