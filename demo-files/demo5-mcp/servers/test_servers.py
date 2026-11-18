#!/usr/bin/env python3
"""Talks to both demo servers directly (no Claude Code, no model). Usage: python3 test_servers.py"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def call(script, env_extra, tool):
    env = dict(os.environ, **env_extra)
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": tool, "arguments": {}}},
    ]
    p = subprocess.run([sys.executable, os.path.join(HERE, script)], input="\n".join(json.dumps(r) for r in reqs) + "\n",
                       capture_output=True, text=True, env=env, timeout=20)
    out = [json.loads(x) for x in p.stdout.splitlines() if x.strip()]
    return out[-1]["result"]["content"][0]["text"]


ok = True
for label, script, env, tool, expect in [
    ("notes as alice", "notes_server.py", {"NOTES_TOKEN": "FAKE-TOKEN-DO-NOT-USE-alice"}, "whoami", "alice"),
    ("notes as bo", "notes_server.py", {"NOTES_TOKEN": "FAKE-TOKEN-DO-NOT-USE-bo"}, "whoami", "bo"),
    ("notes with no token", "notes_server.py", {"NOTES_TOKEN": ""}, "whoami", "Not authenticated"),
    ("shadow-sync", "shadow_server.py", {}, "sync_notes", "shadow-sync is running"),
]:
    text = call(script, env, tool)
    good = expect in text
    ok = ok and good
    print("[%s] %s: %s" % ("ok" if good else "FAIL", label, text))
sys.exit(0 if ok else 1)
