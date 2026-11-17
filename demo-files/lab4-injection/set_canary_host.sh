#!/usr/bin/env bash
# Points the payload at a different canary host (for example a second machine on the class network).
# Use this only if your instructor says loopback does not behave as expected under the sandbox.
# Usage: bash set_canary_host.sh HOST:PORT        (default in the files: 127.0.0.1:8765)
# Then run the listener there:  python3 canary_listener.py --host 0.0.0.0 --port PORT
set -e
here="$(cd "$(dirname "$0")" && pwd)"
[ -n "$1" ] || { echo "Usage: bash set_canary_host.sh HOST:PORT"; exit 2; }
sed -i "s#127\.0\.0\.1:8765#$1#g" "$here/shipping-notes/README.md" "$here/shipping-notes/issues/ISSUE-017.md" "$here/shipping-notes/tools/ticket_lookup.py"
echo "Payloads now point at $1."
