#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

LIST_FILE="PROJECT_CONTEXT_FILES.txt"

if [ ! -f "$LIST_FILE" ]; then
  echo "Missing $LIST_FILE"
  exit 1
fi

echo "Project context files:"
echo

missing=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if [ -f "$f" ]; then
    echo "  OK   $f"
  else
    echo "  MISS $f"
    missing=1
  fi
done < "$LIST_FILE"

if [ "$missing" -ne 0 ]; then
  echo
  echo "Some required context files are missing."
  exit 1
fi

echo
echo "Git status for context files:"
echo

git status --short -- $(cat "$LIST_FILE")

echo
echo "Changed since HEAD:"
echo

git diff --name-only HEAD -- $(cat "$LIST_FILE") || true

echo
echo "Reminder:"
echo "If any of the files above changed meaningfully, re-upload them manually to the ChatGPT Project."
