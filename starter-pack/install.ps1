param([Parameter(Mandatory=$true)][string]$Target)
$resolved = [System.IO.Path]::GetFullPath($Target)
$targetKind = [System.IO.Path]::GetFileName($resolved)
if ($targetKind -notin @(".codex", ".claude")) { throw "Target must end with .codex or .claude" }
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$skills = @("problem-os", "economy-guard", "numbering-canon", "devils-advocate", "sos", "sos1", "sos2", "boardroom", "problem-to-action", "repeatable-work", "numbered-next")
$instructionFile = if ($targetKind -eq ".codex") { "AGENTS.md" } else { "CLAUDE.md" }
if ((Test-Path (Join-Path $resolved $instructionFile)) -or (Test-Path (Join-Path $resolved "VDAI_AI_STARTER_VERIFICATION.md")) -or ($skills | Where-Object { Test-Path (Join-Path $resolved "skills\$_") })) {
  throw "Existing Claude configuration detected. Nothing was overwritten. Follow INSTALL.md to merge manually."
}
New-Item -ItemType Directory -Force -Path $resolved | Out-Null
Copy-Item (Join-Path $source $instructionFile) (Join-Path $resolved $instructionFile) -Force
Copy-Item (Join-Path $source "VERIFICATION.md") (Join-Path $resolved "VDAI_AI_STARTER_VERIFICATION.md") -Force
foreach ($skill in $skills) {
  $dest = Join-Path $resolved "skills\$skill"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item "$source\skills\$skill\SKILL.md" "$dest\SKILL.md" -Force
}
Write-Host "VDAI AI Starter · Dmitrii Pro installed. Restart the agent and run both turns from VDAI_AI_STARTER_VERIFICATION.md."
