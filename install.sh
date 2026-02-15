#!/bin/bash
# OpenCode Dotfiles - Skills Install Script
# https://github.com/JuChLi/opencode-dotfiles

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.agents/skills"

echo "Installing OpenCode skills..."
echo "Source: $SCRIPT_DIR/skills/"
echo "Target: $TARGET_DIR"
echo ""

mkdir -p "$TARGET_DIR"

# Copy all skill directories
for skill_dir in "$SCRIPT_DIR/skills/"*/; do
    skill_name=$(basename "$skill_dir")
    echo "Installing skill: $skill_name"
    cp -r "$skill_dir" "$TARGET_DIR/"
done

echo ""
echo "Installed skills:"
for skill_dir in "$SCRIPT_DIR/skills/"*/; do
    skill_name=$(basename "$skill_dir")
    echo "  - $skill_name"
done
echo ""
echo "Done! Skills are now available in your OpenCode sessions."
echo ""
echo "Usage:"
echo "  /save - Save current session progress"
echo "  /load - Load and resume previous progress"
