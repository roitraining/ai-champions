#!/usr/bin/env bash
# Puts one defense configuration into shipping-notes/.claude/settings.json.
# Usage: bash apply_config.sh 01|02|03|04     (then restart Claude Code in shipping-notes/)
set -e
here="$(cd "$(dirname "$0")" && pwd)"
src=$(ls "$here"/defense_configs/"$1"_*.json 2>/dev/null | head -1)
[ -n "$src" ] || { echo "Usage: bash apply_config.sh 01|02|03|04"; exit 2; }
mkdir -p "$here/shipping-notes/.claude"
cp "$src" "$here/shipping-notes/.claude/settings.json"
echo "Applied $(basename "$src"). Restart Claude Code in $here/shipping-notes."
