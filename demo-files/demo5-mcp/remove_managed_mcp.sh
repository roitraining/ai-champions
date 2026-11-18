#!/usr/bin/env bash
# Removes the demo managed-mcp.json. Linux and macOS. Needs root.
set -e
if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo."; exit 1; fi
if [ "$(uname -s)" = "Darwin" ]; then dir="/Library/Application Support/ClaudeCode"; else dir="/etc/claude-code"; fi
rm -f "$dir/managed-mcp.json"
if [ -e "$dir/managed-mcp.json.bak-demo" ]; then mv "$dir/managed-mcp.json.bak-demo" "$dir/managed-mcp.json"; echo "Restored the backed-up file."; else echo "Removed $dir/managed-mcp.json."; fi
rm -rf /opt/champions-mcp
