#!/usr/bin/env bash
# Installs a managed-mcp.json that allows ONLY the approved "notes" server. Linux and macOS. Needs root.
# Usage: sudo bash install_managed_mcp.sh
# Linux path: /etc/claude-code/managed-mcp.json
# macOS path: /Library/Application Support/ClaudeCode/managed-mcp.json
set -e
if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo."; exit 1; fi
here="$(cd "$(dirname "$0")" && pwd)"
if [ "$(uname -s)" = "Darwin" ]; then dir="/Library/Application Support/ClaudeCode"; else dir="/etc/claude-code"; fi
srv=/opt/champions-mcp
mkdir -p "$srv" "$dir"
cp "$here"/servers/*.py "$srv"/
chmod 755 "$srv"/*.py
if [ -e "$dir/managed-mcp.json" ]; then cp "$dir/managed-mcp.json" "$dir/managed-mcp.json.bak-demo"; fi
cat > "$dir/managed-mcp.json" <<JSON
{
  "mcpServers": {
    "notes": {
      "command": "python3",
      "args": ["$srv/notes_server.py"],
      "env": { "NOTES_TOKEN": "\${NOTES_TOKEN}" }
    }
  }
}
JSON
chmod 644 "$dir/managed-mcp.json"
echo "Installed $dir/managed-mcp.json. The file holds no secret: NOTES_TOKEN is read from each user's own environment."
echo "Restart Claude Code. Check: claude mcp list"
