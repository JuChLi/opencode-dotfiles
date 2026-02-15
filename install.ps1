# OpenCode Dotfiles - Skills Install Script (PowerShell)
# https://github.com/JuChLi/opencode-dotfiles

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = "$env:USERPROFILE\.agents\skills"

Write-Host "Installing OpenCode skills..."
Write-Host "Source: $ScriptDir\skills\"
Write-Host "Target: $TargetDir"
Write-Host ""

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# Copy all skill directories
Get-ChildItem "$ScriptDir\skills" -Directory | ForEach-Object {
    $skillName = $_.Name
    Write-Host "Installing skill: $skillName"
    Copy-Item $_.FullName -Destination $TargetDir -Recurse -Force
}

Write-Host ""
Write-Host "Installed skills:"
Get-ChildItem "$ScriptDir\skills" -Directory | ForEach-Object {
    Write-Host "  - $($_.Name)"
}
Write-Host ""
Write-Host "Done! Skills are now available in your OpenCode sessions." -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  /save - Save current session progress"
Write-Host "  /load - Load and resume previous progress"
