#!/usr/bin/env bash
set -euo pipefail
target="${1:-}"
target_kind="$(basename "$target")"
if [[ -z "$target" || ( "$target_kind" != ".codex" && "$target_kind" != ".claude" ) ]]; then
  echo "Usage: bash install.sh /explicit/path/.codex  # or .claude"
  exit 2
fi
source_dir="$(cd "$(dirname "$0")" && pwd)"
skills=(problem-os economy-guard numbering-canon devils-advocate sos sos1 sos2 boardroom problem-to-action repeatable-work numbered-next)
conflict=0
if [[ "$target_kind" == ".codex" ]]; then
  [[ -e "$target/AGENTS.md" ]] && conflict=1
else
  [[ -e "$target/CLAUDE.md" ]] && conflict=1
fi
[[ -e "$target/VDAI_AI_STARTER_VERIFICATION.md" ]] && conflict=1
[[ -e "$target/VDAI_AI_STARTER_FEEDBACK.md" ]] && conflict=1
[[ -e "$target/VDAI_AI_STARTER_VISUAL_GUIDE.md" ]] && conflict=1
[[ "$target_kind" == ".codex" && -e "$target/vdai-task-weight.py" ]] && conflict=1
[[ "$target_kind" == ".claude" && -e "$target/VDAI_AI_STARTER_USAGE.md" ]] && conflict=1
for skill in "${skills[@]}"; do [[ -e "$target/skills/$skill" ]] && conflict=1; done
if [[ "$conflict" -eq 1 ]]; then
  echo "Existing Claude configuration detected. Nothing was overwritten. Follow INSTALL.md to merge manually."
  exit 3
fi
mkdir -p "$target"
if [[ "$target_kind" == ".codex" ]]; then
  cp "$source_dir/AGENTS.md" "$target/AGENTS.md"
else
  cp "$source_dir/CLAUDE.md" "$target/CLAUDE.md"
fi
cp "$source_dir/VERIFICATION.md" "$target/VDAI_AI_STARTER_VERIFICATION.md"
cp "$source_dir/FEEDBACK.md" "$target/VDAI_AI_STARTER_FEEDBACK.md"
cp "$source_dir/VISUAL_TASK_LABELS.md" "$target/VDAI_AI_STARTER_VISUAL_GUIDE.md"
if [[ "$target_kind" == ".codex" ]]; then
  cp "$source_dir/tools/codex_task_weight.py" "$target/vdai-task-weight.py"
  chmod 0755 "$target/vdai-task-weight.py"
fi
if [[ "$target_kind" == ".claude" ]]; then
  cp "$source_dir/CLAUDE_USAGE.md" "$target/VDAI_AI_STARTER_USAGE.md"
  cp "$source_dir/tools/claude_statusline.py" "$target/vdai-statusline.py"
  chmod 0755 "$target/vdai-statusline.py"
fi
for skill in "${skills[@]}"; do
  mkdir -p "$target/skills/$skill"
  cp "$source_dir/skills/$skill/SKILL.md" "$target/skills/$skill/SKILL.md"
done
echo "VDAI AI Starter · Dmitrii Pro installed. Restart the agent and run both turns from VDAI_AI_STARTER_VERIFICATION.md. Feedback instructions: VDAI_AI_STARTER_FEEDBACK.md. Claude Code users: review VDAI_AI_STARTER_USAGE.md before merging statusLine settings."
