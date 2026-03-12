#!/usr/bin/env bash
set -euo pipefail

TASK="${*:-Continue the current coding task}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")"
REMOTE="$(git remote get-url origin 2>/dev/null || echo "no-remote")"

cat <<EOF2
Use the GitHub repository as the source of truth for code.

Use the ChatGPT Project files as the source of truth for persistent context:
- STATE.md
- DEVELOPING_CONTEXT.md
- PROJECT_BRIEF.md
- OPERATING_MANUAL.md

Inspect the repo on:
- branch: $BRANCH
- commit: $COMMIT
- remote: $REMOTE

Current task: $TASK

When responding:
- prefer copy-paste-ready Debian commands
- keep changes minimal and modular
- keep code in the repo
- do not assume Project files exist in the server checkout
- use the ChatGPT Project files for persistent context
EOF2
