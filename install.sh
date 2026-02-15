#!/bin/bash
# OpenCode Dotfiles - Install Script
# https://github.com/JuChLi/opencode-dotfiles

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.config/opencode/commands"

echo "Installing OpenCode commands..."
echo "Source: $SCRIPT_DIR/commands/"
echo "Target: $TARGET_DIR"
echo ""

mkdir -p "$TARGET_DIR"

# Copy all command files
cp "$SCRIPT_DIR/commands/"*.md "$TARGET_DIR/"

echo "Installed commands:"
for f in "$SCRIPT_DIR/commands/"*.md; do
    name=$(basename "$f" .md)
    echo "  /$name"
done
echo ""
echo "Done! Restart OpenCode or start a new session to use the commands."
