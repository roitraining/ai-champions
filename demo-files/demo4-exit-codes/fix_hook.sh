#!/usr/bin/env bash
# Swaps the hook script in project/.claude/hooks/ between the broken (exit 1) and fixed (exit 2) versions.
# Usage: bash fix_hook.sh broken|fixed
set -e
here="$(cd "$(dirname "$0")" && pwd)"
case "$1" in
  broken|fixed)
    cp "$here/hooks-source/block_rm_$1.py" "$here/project/.claude/hooks/block_rm.py"
    echo "Hook is now the $1 version." ;;
  *)
    echo "Usage: bash fix_hook.sh broken|fixed"; exit 2 ;;
esac
