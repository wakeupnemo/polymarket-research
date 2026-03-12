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
