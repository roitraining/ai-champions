#!/usr/bin/env python3
"""Summarize the demo log without jq. Usage: python3 summarize_log.py [logfile]"""
import collections
import json
import os
import sys

path = sys.argv[1] if len(sys.argv) > 1 else (os.environ.get("CLAUDE_TOOL_LOG") or os.path.join(os.path.expanduser("~"), "claude-tool-calls.log"))
if not os.path.exists(path):
    sys.exit("No log at %s yet." % path)
rows = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
print("Calls by tool:")
for tool, n in collections.Counter(r["tool"] for r in rows if r.get("event") == "tool_call").most_common():
    print("  %3d  %s" % (n, tool))
print("\nBlocked attempts:")
blocked = [r for r in rows if r.get("event") == "blocked"]
for r in blocked:
    print("  %s  %s  %s" % (r["ts"], r["rule"], (r.get("input") or {}).get("command")))
print("\nBlocked pushes: %d" % sum(1 for r in blocked if r.get("rule") == "no-push"))
