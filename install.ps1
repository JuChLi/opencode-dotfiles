# OpenCode Dotfiles - Install Script (PowerShell)
# https://github.com/JuChLi/opencode-dotfiles
#
# Creates symlinks for commands and skills to this repo

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CommandsSource = "$ScriptDir\commands"
$SkillsSource = "$ScriptDir\skills"

$CommandsTarget = "$env:USERPROFILE\.config\opencode\commands"
$SkillsTarget = "$env:USERPROFILE\.agents\skills"

# Skill name mappings (repo folder -> installed name)
$SkillMappings = @{
    "ddd-arch" = "clean-ddd-hexagonal"
    "ddd-refactor" = "moai-workflow-ddd"
}

# Plugin name mappings (repo folder -> installed name)
$PluginMappings = @{
    "opencode-myquota" = "myquota"
}

Write-Host "OpenCode Dotfiles Installer" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check admin rights for symlinks
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Warning: Running without admin rights. Symlinks may fail on older Windows versions." -ForegroundColor Yellow
    Write-Host "If symlinks fail, run PowerShell as Administrator." -ForegroundColor Yellow
    Write-Host ""
}

# === Commands ===
Write-Host "[Commands]" -ForegroundColor Green
Write-Host "Source: $CommandsSource"
Write-Host "Target: $CommandsTarget"

# Ensure parent directory exists
$CommandsParent = Split-Path -Parent $CommandsTarget
if (-not (Test-Path $CommandsParent)) {
    New-Item -ItemType Directory -Force -Path $CommandsParent | Out-Null
}

# Remove existing (file, folder, or symlink)
if (Test-Path $CommandsTarget) {
    Remove-Item -Recurse -Force $CommandsTarget
    Write-Host "  Removed existing: $CommandsTarget"
}

# Create symlink
New-Item -ItemType SymbolicLink -Path $CommandsTarget -Target $CommandsSource | Out-Null
Write-Host "  Created symlink: $CommandsTarget -> $CommandsSource" -ForegroundColor Green

# List installed commands
Write-Host ""
Write-Host "  Installed commands:"
Get-ChildItem "$CommandsSource\*.md" | ForEach-Object {
    $name = $_.BaseName
    $content = Get-Content $_.FullName -Raw
    if ($content -match "description:\s*(.+)") {
        $desc = $Matches[1].Trim()
    } else {
        $desc = ""
    }
    Write-Host "    /$name - $desc"
}

# === Skills ===
Write-Host ""
Write-Host "[Skills]" -ForegroundColor Green
Write-Host "Source: $SkillsSource"
Write-Host "Target: $SkillsTarget"

# Ensure skills directory exists
if (-not (Test-Path $SkillsTarget)) {
    New-Item -ItemType Directory -Force -Path $SkillsTarget | Out-Null
}

# Create symlinks for each skill
foreach ($mapping in $SkillMappings.GetEnumerator()) {
    $sourceFolder = $mapping.Key
    $targetName = $mapping.Value
    $sourcePath = "$SkillsSource\$sourceFolder"
    $targetPath = "$SkillsTarget\$targetName"

    if (-not (Test-Path $sourcePath)) {
        Write-Host "  Skipped (not found): $sourceFolder" -ForegroundColor Yellow
        continue
    }

    # Remove existing
    if (Test-Path $targetPath) {
        Remove-Item -Recurse -Force $targetPath
    }

    # Create symlink
    New-Item -ItemType SymbolicLink -Path $targetPath -Target $sourcePath | Out-Null
    Write-Host "  Created symlink: $targetName -> $sourcePath" -ForegroundColor Green
}

# === Plugins ===
Write-Host ""
Write-Host "[Plugins]" -ForegroundColor Green

$PluginsSource = "$ScriptDir\opencode-myquota\plugin"
$PluginTargetBase = "$env:USERPROFILE\.config\opencode\plugin"

foreach ($mapping in $PluginMappings.GetEnumerator()) {
    $sourceFolder = $mapping.Key
    $targetName = $mapping.Value
    $sourcePath = "$ScriptDir\$sourceFolder\plugin"
    $targetPath = "$PluginTargetBase\$targetName"
    $commandSourcePath = "$ScriptDir\$sourceFolder\command\$targetName.md"
    $commandTargetPath = "$env:USERPROFILE\.config\opencode\command\$targetName.md"

    if (-not (Test-Path $sourcePath)) {
        Write-Host "  Skipped (not found): $sourceFolder" -ForegroundColor Yellow
        continue
    }

    # Ensure plugin directory exists
    if (-not (Test-Path $PluginTargetBase)) {
        New-Item -ItemType Directory -Force -Path $PluginTargetBase | Out-Null
    }

    # Ensure command directory exists
    $commandParent = Split-Path -Parent $commandTargetPath
    if (-not (Test-Path $commandParent)) {
        New-Item -ItemType Directory -Force -Path $commandParent | Out-Null
    }

    # Remove existing
    if (Test-Path $targetPath) {
        Remove-Item -Recurse -Force $targetPath
    }
    if (Test-Path $commandTargetPath) {
        Remove-Item -Force $commandTargetPath
    }

    # Create plugin symlink
    New-Item -ItemType SymbolicLink -Path $targetPath -Target $sourcePath | Out-Null
    Write-Host "  Created plugin symlink: $targetName -> $sourcePath" -ForegroundColor Green

    # Create command symlink
    New-Item -ItemType SymbolicLink -Path $commandTargetPath -Target $commandSourcePath | Out-Null
    Write-Host "  Created command symlink: $commandTargetPath -> $commandSourcePath" -ForegroundColor Green
}

# === Done ===
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Symlinks created:" -ForegroundColor White
Write-Host "  $CommandsTarget -> $CommandsSource"
foreach ($mapping in $SkillMappings.GetEnumerator()) {
    Write-Host "  $SkillsTarget\$($mapping.Value) -> $SkillsSource\$($mapping.Key)"
}
foreach ($mapping in $PluginMappings.GetEnumerator()) {
    $targetName = $mapping.Value
    Write-Host "  $PluginTargetBase\$targetName -> $ScriptDir\$($mapping.Key)\plugin"
    Write-Host "  $env:USERPROFILE\.config\opencode\command\$targetName -> $ScriptDir\$($mapping.Key)\command\$targetName.md"
}
Write-Host ""
Write-Host "Restart OpenCode to load the new commands and skills."
