# Installs the demo managed settings file on Windows. Run from an elevated (administrator) PowerShell.
# Target: C:\Program Files\ClaudeCode\managed-settings.json
# (The older C:\ProgramData\ClaudeCode path is NOT read.)
$dir = 'C:\Program Files\ClaudeCode'
$target = Join-Path $dir 'managed-settings.json'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path $target) { Copy-Item $target "$target.bak-demo" -Force; Write-Host "Existing file backed up to $target.bak-demo" }
New-Item -ItemType Directory -Force $dir | Out-Null
Copy-Item (Join-Path $here 'managed-settings.json') $target -Force
Write-Host "Installed $target. Restart Claude Code, then run /status."
