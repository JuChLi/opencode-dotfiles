#!/bin/bash
# opencode-myquota - Install Script (Bash)
# Query all AI account quota (GitHub Copilot, OpenAI, Z.ai, MiniMax)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OPENCODE_CONFIG="$HOME/.config/opencode"
PLUGINS_TARGET="$OPENCODE_CONFIG/plugins/myquota"
COMMAND_TARGET="$OPENCODE_CONFIG/commands/myquota.md"

echo "opencode-myquota Installer"
echo "========================="
echo ""

# === Step 1: Build TypeScript ===
echo "[1/2] Building TypeScript..."
cd "$SCRIPT_DIR"
npm run build
echo "  Build completed successfully"

# === Step 2: Copy to plugins directory ===
echo ""
echo "[2/2] Copying to plugins directory..."

# Ensure plugins directory exists
mkdir -p "$OPENCODE_CONFIG/plugins"

# Remove existing plugin if present
if [ -d "$PLUGINS_TARGET" ]; then
    rm -rf "$PLUGINS_TARGET"
fi

# Copy compiled plugin
cp -r "$SCRIPT_DIR/dist" "$PLUGINS_TARGET"
echo "  Copied to: $PLUGINS_TARGET"

# Copy command file
cp "$SCRIPT_DIR/command/myquota.md" "$COMMAND_TARGET"
echo "  Copied command: $COMMAND_TARGET"

# === Done ===
echo ""
echo "Installation complete!"
echo ""
echo "Files copied:"
echo "  Plugin: $PLUGINS_TARGET"
echo "  Command: $COMMAND_TARGET"
echo ""
echo "Note: Do NOT add opencode-myquota to plugin array in opencode.json"
echo "      (Local plugins in plugins/ are loaded automatically)"
echo ""
echo "Restart OpenCode and use /myquota to query all AI quotas"
