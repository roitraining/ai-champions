#!/usr/bin/env bash
# Puts a demo sandbox configuration into project/.claude/settings.json.
# Usage: bash apply.sh on|fail-closed|off      (then restart Claude Code in project/)
set -e
here="$(cd "$(dirname "$0")" && pwd)"
case "$1" in
  on) src=sandbox-on.json ;;
  fail-closed) src=sandbox-fail-closed.json ;;
  off) src=sandbox-off.json ;;
  *) echo "Usage: bash apply.sh on|fail-closed|off"; exit 2 ;;
esac
mkdir -p "$here/project/.claude"
cp "$here/configs/$src" "$here/project/.claude/settings.json"
echo "Applied $src. Restart Claude Code in $here/project, or run /sandbox to check the panel."
