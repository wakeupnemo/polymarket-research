#!/usr/bin/env bash
set -euo pipefail

TASK="${*:-Continue the current coding task}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")"

cat <<EOF
Use the GitHub repo as the source of truth.
Read STATE.md and DEVELOPING_CONTEXT.md from the ChatGPT Project first.
Then inspect the repo on branch $BRANCH at commit $COMMIT.
Do not redesign the architecture unless necessary.

Current task: $TASK

When responding in this chat:
- prefer copy-paste-ready Debian commands
- keep changes minimal and modular
- keep code in the repo, not in Project files
- update DEVELOPING_CONTEXT.md if the active coding task changes materially
- update STATE.md only if implemented state, validations, or priorities changed
EOF
