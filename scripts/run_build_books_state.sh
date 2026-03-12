#!/usr/bin/env bash
set -euo pipefail

if [ ! -x .venv/bin/python ]; then
  echo "Missing virtual environment. Run: bash scripts/bootstrap_venv.sh"
  exit 1
fi

source .venv/bin/activate
PYTHONPATH=src python -m pmre.cli build-books-state --config "${1:-configs/base.yaml}"
