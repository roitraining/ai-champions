#!/usr/bin/env bash
# Writes project/.mcp.json so a project declares BOTH demo servers (the "before" state).
# Usage: bash setup_project.sh      (then: cd project && claude)
set -e
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$here/project"
cat > "$here/project/.mcp.json" <<JSON
{
  "mcpServers": {
    "notes": { "command": "python3", "args": ["$here/servers/notes_server.py"] },
    "shadow-sync": { "command": "python3", "args": ["$here/servers/shadow_server.py"] }
  }
}
JSON
echo "Wrote $here/project/.mcp.json"
