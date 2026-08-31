#!/usr/bin/env bash
set -euo pipefail
mode="install"
if [[ "${1:-}" == "--check" || "${1:-}" == "--plan" ]]; then
  mode="${1#--}"
  shift
fi
target="${1:-}"
target_kind="$(basename "$target")"
if [[ -z "$target" || ( "$target_kind" != ".codex" && "$target_kind" != ".claude" ) ]]; then
  echo "Usage: bash install.sh [--check|--plan] /explicit/path/.codex  # or .claude"
  exit 2
fi
source_dir="$(cd "$(dirname "$0")" && pwd)"
skills=(problem-os economy-guard numbering-canon devils-advocate sos sos1 sos2 boardroom problem-to-action repeatable-work numbered-next)
platform_name="Codex"
[[ "$target_kind" == ".claude" ]] && platform_name="Claude Code"
conflicts=()
planned=()
record_target() {
  local source="$1" destination="$2"
  planned+=("$destination")
  if [[ -e "$destination" ]]; then
    conflicts+=("$destination")
  fi
  return 0
}
if [[ "$target_kind" == ".codex" ]]; then
  record_target "$source_dir/AGENTS.md" "$target/AGENTS.md"
else
  record_target "$source_dir/CLAUDE.md" "$target/CLAUDE.md"
fi
record_target "$source_dir/VERIFICATION.md" "$target/VDAI_AI_STARTER_VERIFICATION.md"
record_target "$source_dir/FEEDBACK.md" "$target/VDAI_AI_STARTER_FEEDBACK.md"
record_target "$source_dir/VISUAL_TASK_LABELS.md" "$target/VDAI_AI_STARTER_VISUAL_GUIDE.md"
[[ "$target_kind" == ".codex" ]] && record_target "$source_dir/tools/codex_task_weight.py" "$target/vdai-task-weight.py"
if [[ "$target_kind" == ".claude" ]]; then
  record_target "$source_dir/CLAUDE_USAGE.md" "$target/VDAI_AI_STARTER_USAGE.md"
  record_target "$source_dir/tools/claude_statusline.py" "$target/vdai-statusline.py"
fi
for skill in "${skills[@]}"; do record_target "$source_dir/skills/$skill/SKILL.md" "$target/skills/$skill/SKILL.md"; done

if [[ "$mode" == "check" || "$mode" == "plan" ]]; then
  echo "VDAI AI Starter $mode · platform=$platform_name · target=$target"
  for destination in "${planned[@]}"; do
    if [[ -e "$destination" ]]; then echo "CONFLICT $destination"; else echo "ADD $destination"; fi
  done
  [[ "${#conflicts[@]}" -eq 0 ]] && echo "RESULT READY" || echo "RESULT MERGE_REQUIRED conflicts=${#conflicts[@]}"
  exit 0
fi

if [[ "${#conflicts[@]}" -gt 0 ]]; then
  echo "Existing $platform_name configuration detected. Nothing was overwritten."
  printf 'CONFLICT %s\n' "${conflicts[@]}"
  echo "Run with --plan to review every destination, then follow INSTALL.md for an approved merge."
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
