#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  configs \
  scripts \
  data/raw/polymarket \
  data/normalized \
  data/state \
  data/features \
  data/reference \
  reports \
  logs \
  src/pmre/ingest \
  src/pmre/features \
  src/pmre/experiments \
  src/pmre/reporting \
  tests

touch \
  data/raw/polymarket/.gitkeep \
  data/normalized/.gitkeep \
  data/state/.gitkeep \
  data/features/.gitkeep \
  data/reference/.gitkeep \
  reports/.gitkeep \
  logs/.gitkeep

cat > requirements.txt <<'REQ'
PyYAML==6.0.2
pytest==8.3.5
REQ

cat > configs/base.yaml <<'YAML'
project_root: ..

paths:
  raw: data/raw
  normalized: data/normalized
  state: data/state
  features: data/features
  reference: data/reference
  reports: reports
  logs: logs

smoke:
  snapshot_count: 12
  seed: 7
YAML

cat > README.md <<'MD'
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
MD

cat > Makefile <<'MK'
.PHONY: venv smoke test tree

venv:
bash scripts/bootstrap_venv.sh

smoke:
bash scripts/run_smoke.sh

test:
. .venv/bin/activate && PYTHONPATH=src pytest -q

tree:
find . -maxdepth 4 -type f | sort
MK

cat > scripts/bootstrap_venv.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Environment ready."
echo "Activate with: source .venv/bin/activate"
SH

cat > scripts/run_smoke.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

if [ ! -x .venv/bin/python ]; then
  echo "Missing virtual environment. Run: bash scripts/bootstrap_venv.sh"
  exit 1
fi

source .venv/bin/activate
PYTHONPATH=src python -m pmre.cli smoke --config "${1:-configs/base.yaml}"
SH

cat > src/pmre/__init__.py <<'PY'
__version__ = "0.1.0"
PY

cat > src/pmre/config.py <<'PY'
from __future__ import annotations

from pathlib import Path
import yaml


def load_config(config_path: str | Path) -> dict:
    config_path = Path(config_path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    cfg["_config_path"] = str(config_path)
    cfg["_config_dir"] = str(config_path.parent)
    return cfg


def project_root(cfg: dict) -> Path:
    config_dir = Path(cfg["_config_dir"])
    return (config_dir / cfg.get("project_root", ".")).resolve()


def resolve_paths(cfg: dict) -> dict[str, Path]:
    root = project_root(cfg)
    path_map = cfg.get("paths", {})
    return {name: (root / rel).resolve() for name, rel in path_map.items()}


def ensure_dirs(cfg: dict) -> dict[str, Path]:
    paths = resolve_paths(cfg)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths
PY

cat > src/pmre/ingest/__init__.py <<'PY'
PY

cat > src/pmre/ingest/mock_snapshot.py <<'PY'
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import json
import random


def write_demo_metadata(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "market_id": "demo-btc-above-50000",
        "slug": "btc-above-50000-demo",
        "question": "Will BTC be above 50,000 at demo expiry?",
        "outcomes": ["YES", "NO"],
        "category": "crypto",
        "source": "mock",
    }

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_mock_book_snapshots(
    path: str | Path,
    snapshot_count: int = 12,
    seed: int = 7,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    ts0 = datetime(2026, 3, 1, 12, 0, tzinfo=UTC)

    yes_bid = 0.44

    with path.open("w", encoding="utf-8") as fh:
        for i in range(snapshot_count):
            yes_bid = max(0.05, min(0.95, yes_bid + rng.uniform(-0.01, 0.015)))
            yes_bid = round(yes_bid, 3)

            spread = round(max(0.01, rng.uniform(0.01, 0.03)), 3)
            yes_ask = round(min(0.99, yes_bid + spread), 3)

            row = {
                "ts": (ts0 + timedelta(seconds=5 * i)).isoformat(),
                "market_id": "demo-btc-above-50000",
                "token_id": "YES",
                "yes_bid": yes_bid,
                "yes_ask": yes_ask,
                "bid_size": rng.randint(50, 500),
                "ask_size": rng.randint(50, 500),
                "source": "mock",
            }
            fh.write(json.dumps(row) + "\n")

    return path
PY

cat > src/pmre/features/__init__.py <<'PY'
PY

cat > src/pmre/features/basic_microstructure.py <<'PY'
from __future__ import annotations

from pathlib import Path
from statistics import mean, median
import csv
import json


def build_basic_features(raw_snapshot_path: str | Path, feature_path: str | Path) -> dict:
    raw_snapshot_path = Path(raw_snapshot_path)
    feature_path = Path(feature_path)
    feature_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []

    with raw_snapshot_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            snap = json.loads(line)
            spread = round(snap["yes_ask"] - snap["yes_bid"], 6)
            mid = round((snap["yes_ask"] + snap["yes_bid"]) / 2.0, 6)
            total_depth = int(snap["bid_size"]) + int(snap["ask_size"])

            rows.append(
                {
                    "ts": snap["ts"],
                    "market_id": snap["market_id"],
                    "token_id": snap["token_id"],
                    "yes_bid": snap["yes_bid"],
                    "yes_ask": snap["yes_ask"],
                    "mid": mid,
                    "spread": spread,
                    "total_depth": total_depth,
                }
            )

    if not rows:
        raise ValueError("No snapshot rows found in raw snapshot file.")

    with feature_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    spreads = [float(r["spread"]) for r in rows]
    depths = [int(r["total_depth"]) for r in rows]

    return {
        "snapshot_count": len(rows),
        "mean_spread": round(mean(spreads), 6),
        "median_spread": round(median(spreads), 6),
        "mean_total_depth": round(mean(depths), 2),
    }
PY

cat > src/pmre/experiments/__init__.py <<'PY'
PY

cat > src/pmre/experiments/maker_markout_smoke.py <<'PY'
from __future__ import annotations

from pathlib import Path

from pmre.config import ensure_dirs, load_config
from pmre.features.basic_microstructure import build_basic_features
from pmre.ingest.mock_snapshot import write_demo_metadata, write_mock_book_snapshots
from pmre.reporting.markdown import write_smoke_report


def run_smoke(config_path: str | Path) -> dict:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    smoke_cfg = cfg.get("smoke", {})

    raw_file = paths["raw"] / "polymarket" / "smoke_book_snapshots.jsonl"
    metadata_file = paths["reference"] / "demo_market_metadata.json"
    feature_file = paths["features"] / "smoke_basic_microstructure.csv"
    report_file = paths["reports"] / "smoke_report.md"

    write_demo_metadata(metadata_file)
    write_mock_book_snapshots(
        raw_file,
        snapshot_count=int(smoke_cfg.get("snapshot_count", 12)),
        seed=int(smoke_cfg.get("seed", 7)),
    )

    summary = build_basic_features(raw_file, feature_file)

    outputs = {
        "raw_file": str(raw_file),
        "metadata_file": str(metadata_file),
        "feature_file": str(feature_file),
        "report_file": str(report_file),
    }

    write_smoke_report(report_file, summary, outputs)
    return outputs
PY

cat > src/pmre/reporting/__init__.py <<'PY'
PY

cat > src/pmre/reporting/markdown.py <<'PY'
from __future__ import annotations

from pathlib import Path


def write_smoke_report(path: str | Path, summary: dict, outputs: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Smoke Report",
        "",
        "Minimal week-1 pipeline validation output.",
        "",
        "## Summary",
        f"- snapshots: {summary['snapshot_count']}",
        f"- mean spread: {summary['mean_spread']}",
        f"- median spread: {summary['median_spread']}",
        f"- mean total depth: {summary['mean_total_depth']}",
        "",
        "## Output files",
        f"- raw snapshots: {outputs['raw_file']}",
        f"- metadata: {outputs['metadata_file']}",
        f"- features: {outputs['feature_file']}",
        f"- report: {outputs['report_file']}",
        "",
        "## Notes",
        "- This is a smoke pipeline, not a live collector.",
        "- Raw, features, and reporting paths are separated.",
        "- Next step: replace mock ingestion with a Polymarket collector.",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
PY

cat > src/pmre/cli.py <<'PY'
from __future__ import annotations

import argparse
import json

from pmre.experiments.maker_markout_smoke import run_smoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Polymarket Research Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    smoke = subparsers.add_parser("smoke", help="Run the minimal smoke pipeline")
    smoke.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    args = parser.parse_args()

    if args.command == "smoke":
        result = run_smoke(args.config)
        print(json.dumps(result, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
PY

cat > tests/test_smoke.py <<'PY'
from pathlib import Path

from pmre.experiments.maker_markout_smoke import run_smoke


def test_run_smoke(tmp_path: Path) -> None:
    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        """project_root: .
paths:
  raw: data/raw
  normalized: data/normalized
  state: data/state
  features: data/features
  reference: data/reference
  reports: reports
  logs: logs
smoke:
  snapshot_count: 5
  seed: 123
""",
        encoding="utf-8",
    )

    result = run_smoke(cfg)

    assert Path(result["raw_file"]).exists()
    assert Path(result["metadata_file"]).exists()
    assert Path(result["feature_file"]).exists()

    report_path = Path(result["report_file"])
    assert report_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    assert "# Smoke Report" in report_text
PY

chmod +x bootstrap_week1.sh
chmod +x scripts/bootstrap_venv.sh scripts/run_smoke.sh

echo "Week-1 skeleton created."
