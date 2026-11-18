#!/usr/bin/env bash
# Clears the file canary and the hit log between runs, and puts the default configuration back.
# Usage: bash reset.sh
here="$(cd "$(dirname "$0")" && pwd)"
rm -f "$here"/shipping-notes/canary/INJECTED.txt "$here"/canary-hits.log
mkdir -p "$here/shipping-notes/canary" "$here/shipping-notes/.claude"
cp "$here/defense_configs/01_default.json" "$here/shipping-notes/.claude/settings.json"
echo "Reset: file canary removed, hit log removed, configuration 01_default applied."
