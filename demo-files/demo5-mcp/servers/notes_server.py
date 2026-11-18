#!/usr/bin/env python3
"""notes: the approved demo server. It authenticates the caller from a per-user environment variable.

Each person sets their own NOTES_TOKEN before starting Claude Code. This server maps the token to a
user. The tokens are obviously fake (FAKE-TOKEN-DO-NOT-USE-<name>). In real life the server would
check the token with a remote service. The point of the demo: the shared file holds no secret,
each user brings their own identity.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_min import serve  # noqa: E402

PREFIX = "FAKE-TOKEN-DO-NOT-USE-"
NOTES = {
    "alice": ["Alice: draft the Friday release notes", "Alice: review the retry-logic pull request"],
    "bo": ["Bo: rotate the staging key", "Bo: update the on-call schedule"],
}


def identity():
    token = os.environ.get("NOTES_TOKEN", "")
    if token.startswith(PREFIX) and token[len(PREFIX):] in NOTES:
        return token[len(PREFIX):]
    return None


def whoami(_args):
    user = identity()
    return "Authenticated as: %s" % user if user else "Not authenticated. Set NOTES_TOKEN in your own shell before starting Claude Code."


def list_notes(_args):
    user = identity()
    if not user:
        return "Not authenticated."
    return "\n".join(NOTES[user])


TOOLS = [
    {"name": "whoami", "description": "Say which user this server has authenticated.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "list_notes", "description": "List the notes that belong to the authenticated user.",
     "inputSchema": {"type": "object", "properties": {}}},
]

if __name__ == "__main__":
    serve("notes", TOOLS, {"whoami": whoami, "list_notes": list_notes})
