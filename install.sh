#!/bin/bash
# OpenCode Dotfiles - Install Script
# https://github.com/JuChLi/opencode-dotfiles
#
# Creates symlinks for commands and skills to this repo

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMANDS_SOURCE="$SCRIPT_DIR/commands"
SKILLS_SOURCE="$SCRIPT_DIR/skills"

COMMANDS_TARGET="$HOME/.config/opencode/commands"
SKILLS_TARGET="$HOME/.agents/skills"

# Skill name mappings (repo folder -> installed name)
declare -A SKILL_MAPPINGS=(
    ["ddd-arch"]="clean-ddd-hexagonal"
    ["ddd-refactor"]="moai-workflow-ddd"
)

echo "OpenCode Dotfiles Installer"
echo "=========================="
echo ""

# === Commands ===
echo "[Commands]"
echo "Source: $COMMANDS_SOURCE"
echo "Target: $COMMANDS_TARGET"

# Ensure parent directory exists
mkdir -p "$(dirname "$COMMANDS_TARGET")"

# Remove existing (file, folder, or symlink)
if [ -e "$COMMANDS_TARGET" ] || [ -L "$COMMANDS_TARGET" ]; then
    rm -rf "$COMMANDS_TARGET"
    echo "  Removed existing: $COMMANDS_TARGET"
fi

# Create symlink
ln -s "$COMMANDS_SOURCE" "$COMMANDS_TARGET"
echo "  Created symlink: $COMMANDS_TARGET -> $COMMANDS_SOURCE"

# List installed commands
echo ""
echo "  Installed commands:"
for f in "$COMMANDS_SOURCE"/*.md; do
    name=$(basename "$f" .md)
    desc=$(grep -m1 "^description:" "$f" 2>/dev/null | sed 's/description: *//' || echo "")
    echo "    /$name - $desc"
done

# === Skills ===
echo ""
echo "[Skills]"
echo "Source: $SKILLS_SOURCE"
echo "Target: $SKILLS_TARGET"

# Ensure skills directory exists
mkdir -p "$SKILLS_TARGET"

# Create symlinks for each skill
for source_folder in "${!SKILL_MAPPINGS[@]}"; do
    target_name="${SKILL_MAPPINGS[$source_folder]}"
    source_path="$SKILLS_SOURCE/$source_folder"
    target_path="$SKILLS_TARGET/$target_name"

    if [ ! -d "$source_path" ]; then
        echo "  Skipped (not found): $source_folder"
        continue
    fi

    # Remove existing
    if [ -e "$target_path" ] || [ -L "$target_path" ]; then
        rm -rf "$target_path"
    fi

    # Create symlink
    ln -s "$source_path" "$target_path"
    echo "  Created symlink: $target_name -> $source_path"
done

# === Done ===
echo ""
echo "Installation complete!"
echo ""
echo "Symlinks created:"
echo "  $COMMANDS_TARGET -> $COMMANDS_SOURCE"
for source_folder in "${!SKILL_MAPPINGS[@]}"; do
    target_name="${SKILL_MAPPINGS[$source_folder]}"
    echo "  $SKILLS_TARGET/$target_name -> $SKILLS_SOURCE/$source_folder"
done
echo ""
echo "Restart OpenCode to load the new commands and skills."
