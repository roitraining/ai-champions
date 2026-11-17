#!/bin/sh
# Nightly summary job.
export CLAUDE_CODE_OAUTH_TOKEN=FAKE-TOKEN-DO-NOT-USE
claude -p "Summarize yesterday's failed builds" > nightly-summary.txt
