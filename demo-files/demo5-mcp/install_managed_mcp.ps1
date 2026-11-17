# Installs the demo managed-mcp.json on Windows. Run from an elevated (administrator) PowerShell.
# Target: C:\Program Files\ClaudeCode\managed-mcp.json
$dir = 'C:\Program Files\ClaudeCode'
$srv = 'C:\ProgramData\champions-mcp'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force $dir, $srv | Out-Null
Copy-Item (Join-Path $here 'servers\*.py') $srv -Force
$target = Join-Path $dir 'managed-mcp.json'
if (Test-Path $target) { Copy-Item $target "$target.bak-demo" -Force }
$notes = ($srv -replace '\', '/') + '/notes_server.py'
$json = @"
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": ["$notes"],
      "env": { "NOTES_TOKEN": "`${NOTES_TOKEN}" }
    }
  }
}
"@
Set-Content -Path $target -Value $json -Encoding utf8
Write-Host "Installed $target. Restart Claude Code. Check: claude mcp list"
