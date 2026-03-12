#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
cd "$ROOT"

mkdir -p \
  data/raw \
  data/reference \
  data/state \
  data/features \
  logs \
  reports \
  .project_context_upload

touch \
  data/.gitkeep \
  data/raw/.gitkeep \
  data/reference/.gitkeep \
  data/state/.gitkeep \
  data/features/.gitkeep \
  logs/.gitkeep \
  reports/.gitkeep

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Git repo already initialized at: $(git rev-parse --show-toplevel)"
else
  git init -b main
  echo "Initialized new git repo on branch main"
fi

git branch -M main

if ! git config user.name >/dev/null 2>&1; then
  echo "WARNING: git user.name is not set"
fi

if ! git config user.email >/dev/null 2>&1; then
  echo "WARNING: git user.email is not set"
fi

echo
echo "Repository ready at: $PWD"
echo "Next steps:"
echo "  1) review .gitignore"
echo "  2) git status"
echo "  3) git add ."
echo "  4) git commit -m \"Initialize GitHub-centered workflow\""
echo "  5) bash scripts/first_push_github.sh <REMOTE_URL>"
