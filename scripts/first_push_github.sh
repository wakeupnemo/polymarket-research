#!/usr/bin/env bash
set -euo pipefail

REMOTE_URL="${1:-}"
COMMIT_MSG="${2:-Initialize GitHub-centered workflow}"

if [ -z "$REMOTE_URL" ]; then
  echo "Usage: bash scripts/first_push_github.sh <REMOTE_URL> [COMMIT_MESSAGE]"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository."
  exit 1
fi

if ! git config user.name >/dev/null 2>&1; then
  echo "git user.name is not set."
  echo "Run: git config --global user.name \"Your Name\""
  exit 1
fi

if ! git config user.email >/dev/null 2>&1; then
  echo "git user.email is not set."
  echo "Run: git config --global user.email \"you@example.com\""
  exit 1
fi

git branch -M main

if [ -n "$(git status --porcelain)" ]; then
  git add .
  git commit -m "$COMMIT_MSG"
else
  echo "Working tree clean; nothing new to commit."
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

git push -u origin main

echo
echo "Pushed to origin/main"
echo "Remote: $(git remote get-url origin)"
