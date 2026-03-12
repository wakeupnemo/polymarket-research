#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

OUT=".project_context_upload"
rm -rf "$OUT"
mkdir -p "$OUT"

REQUIRED_FILES=(
  "PROJECT_BRIEF.md"
  "OPERATING_MANUAL.md"
  "STATE.md"
  "DEVELOPING_CONTEXT.md"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "Missing required context file: $f"
    exit 1
  fi
  cp "$f" "$OUT/"
done

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")"
STAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "$OUT/PROJECT_CONTEXT_INDEX.md" <<EOF
# Project Context Upload Bundle

Generated: $STAMP
Branch: $BRANCH
Commit: $COMMIT

## Upload these files to the ChatGPT Project
- PROJECT_BRIEF.md
- OPERATING_MANUAL.md
- STATE.md
- DEVELOPING_CONTEXT.md

## Rule
GitHub is the source of truth for code and docs.
ChatGPT Project files are persistent context only.
Do not upload source code or generated data artifacts as normal workflow.
EOF

echo "Prepared ChatGPT Project upload bundle in: $OUT"
echo
find "$OUT" -maxdepth 1 -type f | sort
