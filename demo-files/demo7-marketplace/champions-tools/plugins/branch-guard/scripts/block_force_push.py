#!/usr/bin/env python3
"""PreToolUse hook for Bash: block a force push, and any push to main or master.

Reads the hook input as JSON on stdin (tool_name and tool_input). Exit code 2 blocks the
command and sends the stderr text back to Claude. Exit code 0 lets it run.
"""
import json
import re
import sys

PUSH = re.compile(r"\bgit\s+push\b")
FORCE = re.compile(r"\s(--force\b|--force-with-lease\b|-[a-zA-Z]*f[a-zA-Z]*\b)")
MAIN = re.compile(r"\b(main|master)\b")


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = (data.get("tool_input") or {}).get("command", "")
    if not PUSH.search(command):
        return 0
    if FORCE.search(command):
        print("BRANCH-GUARD: a force push is blocked. Push normally, or ask the user.", file=sys.stderr)
        return 2
    if MAIN.search(command):
        print("BRANCH-GUARD: pushing to main or master is blocked. Push a feature branch and open a pull request.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
