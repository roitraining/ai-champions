#!/usr/bin/env python3
"""shadow-sync: the UNAPPROVED demo server. It stands in for a server nobody reviewed.

It does nothing harmful. It only reports what a local server process could reach, to make the point:
a local MCP server runs with your user's rights, outside the sandbox.
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_min import serve  # noqa: E402


def sync_notes(_args):
    home = os.path.expanduser("~")
    return ("shadow-sync is running as user %s. It could read anything that user can read, "
            "for example files under %s. It is not limited by the sandbox." % (getpass.getuser(), home))


TOOLS = [{"name": "sync_notes", "description": "Pretend to sync notes to a remote service.",
          "inputSchema": {"type": "object", "properties": {}}}]

if __name__ == "__main__":
    serve("shadow-sync", TOOLS, {"sync_notes": sync_notes})
