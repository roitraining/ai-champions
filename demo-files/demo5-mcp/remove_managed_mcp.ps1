# Removes the demo managed-mcp.json on Windows. Run from an elevated PowerShell.
$target = 'C:\Program Files\ClaudeCode\managed-mcp.json'
Remove-Item $target -Force -ErrorAction SilentlyContinue
if (Test-Path "$target.bak-demo") { Move-Item "$target.bak-demo" $target -Force; Write-Host 'Restored the backed-up file.' } else { Write-Host "Removed $target." }
Remove-Item 'C:\ProgramData\champions-mcp' -Recurse -Force -ErrorAction SilentlyContinue
