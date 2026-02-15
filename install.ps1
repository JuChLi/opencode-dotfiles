# OpenCode Dotfiles - Install Script (PowerShell)
# https://github.com/JuChLi/opencode-dotfiles

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = "$env:USERPROFILE\.config\opencode\commands"

Write-Host "Installing OpenCode commands..."
Write-Host "Source: $ScriptDir\commands\"
Write-Host "Target: $TargetDir"
Write-Host ""

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# Copy all command files
Copy-Item "$ScriptDir\commands\*.md" -Destination $TargetDir -Force

Write-Host "Installed commands:"
Get-ChildItem "$ScriptDir\commands\*.md" | ForEach-Object {
    $name = $_.BaseName
    Write-Host "  /$name"
}
Write-Host ""
Write-Host "Done! Restart OpenCode or start a new session to use the commands." -ForegroundColor Green
