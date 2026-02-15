# OpenCode Config - Install Script (PowerShell)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = "$env:USERPROFILE\.config\opencode\commands"

Write-Host "Installing OpenCode commands to $TargetDir..."

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# Copy all command files
Copy-Item "$ScriptDir\commands\*.md" -Destination $TargetDir -Force

Write-Host ""
Write-Host "Done! Installed commands:" -ForegroundColor Green
Get-ChildItem "$ScriptDir\commands\*.md" | ForEach-Object {
    $name = $_.BaseName
    Write-Host "  /$name"
}
Write-Host ""
Write-Host "Restart OpenCode or start a new session to use the commands."
