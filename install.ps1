# OpenCode Dotfiles - Commands Install Script (PowerShell)
# https://github.com/JuChLi/opencode-dotfiles

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = "$env:USERPROFILE\.config\opencode\commands"

Write-Host "Installing OpenCode custom commands..."
Write-Host "Source: $ScriptDir\commands\"
Write-Host "Target: $TargetDir"
Write-Host ""

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# Copy all command files
Copy-Item "$ScriptDir\commands\*.md" -Destination $TargetDir -Force

Write-Host "Installed commands:"
Get-ChildItem "$ScriptDir\commands\*.md" | ForEach-Object {
    $name = $_.BaseName
    $content = Get-Content $_.FullName -Raw
    if ($content -match "description:\s*(.+)") {
        $desc = $Matches[1].Trim()
    } else {
        $desc = ""
    }
    Write-Host "  /$name - $desc"
}
Write-Host ""
Write-Host "Done! Commands are now available in OpenCode." -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  /save - Save current session progress"
Write-Host "  /load - Load and resume previous progress"
