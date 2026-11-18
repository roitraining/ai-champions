"""A tiny MCP server helper for the class demos. Standard library only.

Speaks newline-delimited JSON-RPC 2.0 over stdin and stdout, the way a local (stdio) MCP server does.
It supports initialize, ping, tools/list and tools/call. It is a teaching stand-in, not a full
implementation of the protocol. Nothing here touches a network.
"""
import json
import sys


def serve(server_name, tools, handlers):
    """tools: list of tool definition dicts. handlers: {tool_name: function(arguments) -> str}."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, mid = msg.get("method"), msg.get("id")
        if mid is None:
            continue  # a notification such as notifications/initialized: no reply
        if method == "initialize":
            version = (msg.get("params") or {}).get("protocolVersion", "2025-06-18")
            result = {"protocolVersion": version, "capabilities": {"tools": {}},
                      "serverInfo": {"name": server_name, "version": "0.1.0"}}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": tools}
        elif method == "tools/call":
            params = msg.get("params") or {}
            fn = handlers.get(params.get("name"))
            if fn is None:
                reply = {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "unknown tool"}}
                print(json.dumps(reply), flush=True)
                continue
            result = {"content": [{"type": "text", "text": fn(params.get("arguments") or {})}]}
        else:
            reply = {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}}
            print(json.dumps(reply), flush=True)
            continue
        print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}), flush=True)
