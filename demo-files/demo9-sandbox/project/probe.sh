#!/usr/bin/env bash
# Three harmless probes for Demo 9. Run them through Claude Code's Bash tool (ask Claude to run: bash probe.sh).
# Each probe prints BLOCKED or SUCCEEDED, and cleans up after itself.
cd "$(dirname "$0")"

echo "1 write outside the working directory (../outside-probe.txt):"
if touch ../outside-probe.txt 2>/dev/null; then echo "   SUCCEEDED"; rm -f ../outside-probe.txt; else echo "   BLOCKED"; fi

echo "2 write to the home folder (~/sandbox-probe):"
if touch ~/sandbox-probe 2>/dev/null; then echo "   SUCCEEDED"; rm -f ~/sandbox-probe; else echo "   BLOCKED"; fi

echo "3 call a domain that is NOT on the allowed list (example.com):"
code=$(curl -sS -m 6 -o /dev/null -w '%{http_code}' https://example.com 2>/dev/null)
if [ "$code" = "200" ]; then echo "   SUCCEEDED (HTTP 200)"; else echo "   BLOCKED (no HTTP 200; got '$code')"; fi

echo "4 call a domain that IS on the allowed list (pypi.org), for contrast:"
code=$(curl -sS -m 6 -o /dev/null -w '%{http_code}' https://pypi.org 2>/dev/null)
echo "   HTTP status: ${code:-none}"
echo
echo "If probe 3 shows BLOCKED because this machine has no internet, run the same curl from a normal terminal first to check."
