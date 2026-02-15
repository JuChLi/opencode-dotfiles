#!/bin/bash
# OpenCode Config - Install Script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.config/opencode/commands"

echo "Installing OpenCode commands to $TARGET_DIR..."

mkdir -p "$TARGET_DIR"

# Copy all command files
cp "$SCRIPT_DIR/commands/"*.md "$TARGET_DIR/"

echo ""
echo "✅ Done! Installed commands:"
for f in "$SCRIPT_DIR/commands/"*.md; do
    name=$(basename "$f" .md)
    echo "  /$name"
done
echo ""
echo "Restart OpenCode or start a new session to use the commands."
