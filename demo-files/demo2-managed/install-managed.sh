#!/usr/bin/env bash
# Installs the demo managed settings file on Linux (and WSL). Needs root (sudo).
# Usage: sudo bash install-managed.sh
set -e
dir=/etc/claude-code
here="$(cd "$(dirname "$0")" && pwd)"
if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo."; exit 1; fi
if [ -e "$dir/managed-settings.json" ]; then
  cp "$dir/managed-settings.json" "$dir/managed-settings.json.bak-demo"
  echo "Existing file backed up to $dir/managed-settings.json.bak-demo"
fi
mkdir -p "$dir"
cp "$here/managed-settings.json" "$dir/managed-settings.json"
chmod 644 "$dir/managed-settings.json"
echo "Installed $dir/managed-settings.json. Restart Claude Code, then run /status."
