#!/usr/bin/env bash
# Builds a tiny local repository with no remote, so a push can never go anywhere.
set -e
git init -q -b main
echo "v1" > app.txt
git add -A
git -c user.name="Fixture" -c user.email="fixture@example.invalid" -c commit.gpgsign=false commit -q -m "chore: initial import"
