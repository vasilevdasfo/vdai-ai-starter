param([Parameter(Mandatory=$true)][string]$Target)
$resolved = [System.IO.Path]::GetFullPath($Target)
$targetKind = [System.IO.Path]::GetFileName($resolved)
if ($targetKind -notin @(".codex", ".claude")) { throw "Target must end with .codex or .claude" }
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$skills = @("problem-os", "economy-guard", "numbering-canon", "devils-advocate", "sos", "sos1", "sos2", "boardroom", "problem-to-action", "repeatable-work", "numbered-next")
$instructionFile = if ($targetKind -eq ".codex") { "AGENTS.md" } else { "CLAUDE.md" }
if ((Test-Path (Join-Path $resolved $instructionFile)) -or (Test-Path (Join-Path $resolved "VDAI_AI_STARTER_VERIFICATION.md")) -or (Test-Path (Join-Path $resolved "VDAI_AI_STARTER_FEEDBACK.md")) -or (Test-Path (Join-Path $resolved "VDAI_AI_STARTER_VISUAL_GUIDE.md")) -or (($targetKind -eq ".codex") -and (Test-Path (Join-Path $resolved "vdai-task-weight.py"))) -or (($targetKind -eq ".claude") -and (Test-Path (Join-Path $resolved "VDAI_AI_STARTER_USAGE.md"))) -or ($skills | Where-Object { Test-Path (Join-Path $resolved "skills\$_") })) {
  throw "Existing Claude configuration detected. Nothing was overwritten. Follow INSTALL.md to merge manually."
}
New-Item -ItemType Directory -Force -Path $resolved | Out-Null
Copy-Item (Join-Path $source $instructionFile) (Join-Path $resolved $instructionFile) -Force
Copy-Item (Join-Path $source "VERIFICATION.md") (Join-Path $resolved "VDAI_AI_STARTER_VERIFICATION.md") -Force
Copy-Item (Join-Path $source "FEEDBACK.md") (Join-Path $resolved "VDAI_AI_STARTER_FEEDBACK.md") -Force
Copy-Item (Join-Path $source "VISUAL_TASK_LABELS.md") (Join-Path $resolved "VDAI_AI_STARTER_VISUAL_GUIDE.md") -Force
if ($targetKind -eq ".codex") {
  Copy-Item (Join-Path $source "tools\codex_task_weight.py") (Join-Path $resolved "vdai-task-weight.py") -Force
}
if ($targetKind -eq ".claude") {
  Copy-Item (Join-Path $source "CLAUDE_USAGE.md") (Join-Path $resolved "VDAI_AI_STARTER_USAGE.md") -Force
  Copy-Item (Join-Path $source "tools\claude_statusline.py") (Join-Path $resolved "vdai-statusline.py") -Force
}
foreach ($skill in $skills) {
  $dest = Join-Path $resolved "skills\$skill"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item "$source\skills\$skill\SKILL.md" "$dest\SKILL.md" -Force
}
Write-Host "VDAI AI Starter · Dmitrii Pro installed. Restart the agent and run both turns from VDAI_AI_STARTER_VERIFICATION.md. Feedback instructions: VDAI_AI_STARTER_FEEDBACK.md. Claude Code users: review VDAI_AI_STARTER_USAGE.md before merging statusLine settings."
