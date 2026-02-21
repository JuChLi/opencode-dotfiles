# opencode-myquota - Install Script (PowerShell)
# Query all AI account quota (GitHub Copilot, OpenAI, Z.ai, MiniMax)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Target locations
$OpenCodeConfig = "$env:USERPROFILE\.config\opencode"
$PluginsTarget = "$OpenCodeConfig\plugins\myquota"
$CommandTarget = "$OpenCodeConfig\commands\myquota.md"

Write-Host "opencode-myquota Installer" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# === Step 1: Build TypeScript ===
Write-Host "[1/2] Building TypeScript..." -ForegroundColor Green
Push-Location $ScriptDir
try {
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build failed with exit code $LASTEXITCODE"
    }
    Write-Host "  Build completed successfully" -ForegroundColor Green
} finally {
    Pop-Location
}

# === Step 2: Copy to plugins directory ===
Write-Host ""
Write-Host "[2/2] Copying to plugins directory..." -ForegroundColor Green

# Ensure plugins directory exists
if (-not (Test-Path "$OpenCodeConfig\plugins")) {
    New-Item -ItemType Directory -Force -Path "$OpenCodeConfig\plugins" | Out-Null
}

# Remove existing plugin if present
if (Test-Path $PluginsTarget) {
    Remove-Item -Recurse -Force $PluginsTarget
}

# Copy compiled plugin
Copy-Item -Path "$ScriptDir\dist" -Destination $PluginsTarget -Recurse -Force
Write-Host "  Copied to: $PluginsTarget" -ForegroundColor Green

# Copy command file
Copy-Item -Path "$ScriptDir\command\myquota.md" -Destination $CommandTarget -Force
Write-Host "  Copied command: $CommandTarget" -ForegroundColor Green

# === Done ===
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files copied:" -ForegroundColor White
Write-Host "  Plugin: $PluginsTarget"
Write-Host "  Command: $CommandTarget"
Write-Host ""
Write-Host "Note: Do NOT add opencode-myquota to plugin array in opencode.json" -ForegroundColor Yellow
Write-Host "      (Local plugins in plugins/ are loaded automatically)"
Write-Host ""
Write-Host "Restart OpenCode and use /myquota to query all AI quotas"
