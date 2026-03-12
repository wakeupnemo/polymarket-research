# Polymarket Research Engine

Minimal Debian-first week-1 skeleton for:
- ingestion
- feature computation
- experiments
- reporting

Structure:
- configs/      project config
- data/raw/     preserved raw inputs
- data/normalized/ normalized tables
- data/state/   reconstructed market state
- data/features/ computed research features
- data/reference/ metadata and external reference data
- reports/      experiment outputs
- src/pmre/ingest/ collectors and raw loaders
- src/pmre/features/ feature computation
- src/pmre/experiments/ experiment runners
- src/pmre/reporting/ report builders
- tests/        smoke tests

Setup:
  sudo apt-get update
  sudo apt-get install -y python3-venv
  bash scripts/bootstrap_venv.sh

Run smoke pipeline:
  bash scripts/run_smoke.sh

Run tests:
  source .venv/bin/activate
  PYTHONPATH=src pytest -q
