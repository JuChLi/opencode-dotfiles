#!/bin/bash
# OpenCode Dotfiles - Commands Install Script
# https://github.com/JuChLi/opencode-dotfiles

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.config/opencode/commands"

echo "Installing OpenCode custom commands..."
echo "Source: $SCRIPT_DIR/commands/"
echo "Target: $TARGET_DIR"
echo ""

mkdir -p "$TARGET_DIR"

# Copy all command files
cp "$SCRIPT_DIR/commands/"*.md "$TARGET_DIR/"

echo "Installed commands:"
for f in "$SCRIPT_DIR/commands/"*.md; do
    name=$(basename "$f" .md)
    desc=$(grep -m1 "^description:" "$f" | sed 's/description: *//')
    echo "  /$name - $desc"
done
echo ""
echo "Done! Commands are now available in OpenCode."
echo ""
echo "Usage:"
echo "  /save - Save current session progress"
echo "  /load - Load and resume previous progress"
