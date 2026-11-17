#!/usr/bin/env bash
# Removes the demo managed settings file (Linux and WSL). Needs root (sudo).
# Usage: sudo bash remove-managed.sh
set -e
dir=/etc/claude-code
if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo."; exit 1; fi
rm -f "$dir/managed-settings.json"
if [ -e "$dir/managed-settings.json.bak-demo" ]; then
  mv "$dir/managed-settings.json.bak-demo" "$dir/managed-settings.json"
  echo "Restored the backed-up file."
else
  echo "Removed $dir/managed-settings.json."
fi
