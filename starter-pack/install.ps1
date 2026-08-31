param(
  [Parameter(Mandatory=$true)][string]$Target,
  [ValidateSet("Install", "Check", "Plan")][string]$Mode = "Install"
)
$resolved = [System.IO.Path]::GetFullPath($Target)
$targetKind = [System.IO.Path]::GetFileName($resolved)
if ($targetKind -notin @(".codex", ".claude")) { throw "Target must end with .codex or .claude" }
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$skills = @("problem-os", "economy-guard", "numbering-canon", "devils-advocate", "sos", "sos1", "sos2", "boardroom", "problem-to-action", "repeatable-work", "numbered-next")
$instructionFile = if ($targetKind -eq ".codex") { "AGENTS.md" } else { "CLAUDE.md" }
$platformName = if ($targetKind -eq ".codex") { "Codex" } else { "Claude Code" }
$destinations = @(
  (Join-Path $resolved $instructionFile),
  (Join-Path $resolved "VDAI_AI_STARTER_VERIFICATION.md"),
  (Join-Path $resolved "VDAI_AI_STARTER_FEEDBACK.md"),
  (Join-Path $resolved "VDAI_AI_STARTER_VISUAL_GUIDE.md")
)
if ($targetKind -eq ".codex") { $destinations += (Join-Path $resolved "vdai-task-weight.py") }
if ($targetKind -eq ".claude") {
  $destinations += (Join-Path $resolved "VDAI_AI_STARTER_USAGE.md")
  $destinations += (Join-Path $resolved "vdai-statusline.py")
}
$destinations += $skills | ForEach-Object { Join-Path $resolved "skills\$_\SKILL.md" }
$conflicts = @($destinations | Where-Object { Test-Path $_ })
if ($Mode -in @("Check", "Plan")) {
  Write-Host "VDAI AI Starter $($Mode.ToLower()) · platform=$platformName · target=$resolved"
  foreach ($destination in $destinations) {
    if (Test-Path $destination) { Write-Host "CONFLICT $destination" } else { Write-Host "ADD $destination" }
  }
  if ($conflicts.Count -eq 0) { Write-Host "RESULT READY" } else { Write-Host "RESULT MERGE_REQUIRED conflicts=$($conflicts.Count)" }
  exit 0
}
if ($conflicts.Count -gt 0) {
  Write-Host "Existing $platformName configuration detected. Nothing was overwritten."
  $conflicts | ForEach-Object { Write-Host "CONFLICT $_" }
  throw "Run with -Mode Plan to review every destination, then follow INSTALL.md for an approved merge."
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
