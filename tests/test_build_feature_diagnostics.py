from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.reporting.build_feature_diagnostics import build_feature_diagnostics


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_feature_diagnostics(tmp_path: Path) -> None:
    feature_set_dir = tmp_path / "data" / "features" / "polymarket" / "feature_sets"
    feature_set_dir.mkdir(parents=True, exist_ok=True)

    feature_csv = feature_set_dir / "feature_set_v0_1_test_freeze.csv"
    _write_csv(
        feature_csv,
        [
            "feature_set_version",
            "freeze_id",
            "source_run_id",
            "collector_ts",
            "book_timestamp",
            "iteration",
            "batch_index",
            "market_id",
            "event_id",
            "outcome",
            "token_index",
            "token_id",
            "clob_market",
            "hash",
            "spread",
            "midpoint",
            "best_bid_size",
            "best_ask_size",
            "top_of_book_imbalance",
            "microprice_proxy",
            "last_trade_minus_mid",
            "bid_levels_count",
            "ask_levels_count",
            "staleness_flag",
            "market_quality_score",
        ],
        [
            {
                "feature_set_version": "v0_1",
                "freeze_id": "test_freeze",
                "source_run_id": "run1",
                "collector_ts": "2026-01-01T00:00:00+00:00",
                "book_timestamp": "1773273600000",
                "iteration": "0",
                "batch_index": "0",
                "market_id": "m1",
                "event_id": "",
                "outcome": "Yes",
                "token_index": "0",
                "token_id": "tok1",
                "clob_market": "cm1",
                "hash": "h1",
                "spread": "0.04",
                "midpoint": "0.50",
                "best_bid_size": "100",
                "best_ask_size": "80",
                "top_of_book_imbalance": "0.11111111",
                "microprice_proxy": "0.51",
                "last_trade_minus_mid": "0.01",
                "bid_levels_count": "5",
                "ask_levels_count": "4",
                "staleness_flag": "0",
                "market_quality_score": "3",
            },
            {
                "feature_set_version": "v0_1",
                "freeze_id": "test_freeze",
                "source_run_id": "run1",
                "collector_ts": "2026-01-01T00:00:01+00:00",
                "book_timestamp": "1773273601000",
                "iteration": "0",
                "batch_index": "1",
                "market_id": "m1",
                "event_id": "",
                "outcome": "Yes",
                "token_index": "0",
                "token_id": "tok1",
                "clob_market": "cm1",
                "hash": "h1",
                "spread": "0.20",
                "midpoint": "0.50",
                "best_bid_size": "",
                "best_ask_size": "30",
                "top_of_book_imbalance": "",
                "microprice_proxy": "",
                "last_trade_minus_mid": "",
                "bid_levels_count": "2",
                "ask_levels_count": "2",
                "staleness_flag": "1",
                "market_quality_score": "0",
            },
            {
                "feature_set_version": "v0_1",
                "freeze_id": "test_freeze",
                "source_run_id": "run1",
                "collector_ts": "2026-01-01T00:00:02+00:00",
                "book_timestamp": "1773273602000",
                "iteration": "0",
                "batch_index": "2",
                "market_id": "m2",
                "event_id": "",
                "outcome": "No",
                "token_index": "1",
                "token_id": "tok2",
                "clob_market": "cm2",
                "hash": "h2",
                "spread": "-0.01",
                "midpoint": "0.48",
                "best_bid_size": "0",
                "best_ask_size": "10",
                "top_of_book_imbalance": "",
                "microprice_proxy": "",
                "last_trade_minus_mid": "",
                "bid_levels_count": "1",
                "ask_levels_count": "1",
                "staleness_flag": "1",
                "market_quality_score": "-1",
            },
        ],
    )

    latest_feature_manifest = feature_set_dir / "latest_feature_set_manifest.json"
    latest_feature_manifest.write_text(
        json.dumps(
            {
                "feature_set_version": "v0_1",
                "freeze_id": "test_freeze",
                "output_csv": str(feature_csv),
            }
        ),
        encoding="utf-8",
    )

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
feature_diagnostics:
  latest_feature_set_manifest: data/features/polymarket/feature_sets/latest_feature_set_manifest.json
  output_dir: data/features/polymarket/diagnostics
  wide_spread_threshold: 0.10
  low_quality_threshold: 1.0
""",
        encoding="utf-8",
    )

    result = build_feature_diagnostics(cfg)

    diagnostics_manifest = tmp_path / "data" / "features" / "polymarket" / "diagnostics" / "latest_feature_diagnostics_manifest.json"
    diagnostics_json = Path(result["diagnostics_json"])
    market_summary_csv = Path(result["market_summary_csv"])

    assert diagnostics_manifest.exists()
    assert diagnostics_json.exists()
    assert market_summary_csv.exists()

    diagnostics_payload = json.loads(diagnostics_json.read_text(encoding="utf-8"))
    aggregate = diagnostics_payload["aggregate_summary"]

    assert aggregate["total_row_count"] == 3
    assert aggregate["stale_row_count"] == 2
    assert aggregate["missing_spread_count"] == 0
    assert aggregate["non_positive_spread_count"] == 1
    assert aggregate["wide_spread_count"] == 1
    assert aggregate["zero_or_empty_top_size_count"] == 2
    assert aggregate["null_imbalance_count"] == 2
    assert aggregate["null_microprice_count"] == 2
    assert aggregate["repeated_hash_row_count"] == 1
    assert aggregate["low_quality_row_count"] == 2

    with market_summary_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 2
    m1 = next(row for row in rows if row["market_id"] == "m1")
    m2 = next(row for row in rows if row["market_id"] == "m2")

    assert m1["row_count"] == "2"
    assert m1["stale_row_fraction"] == "0.5"
    assert m1["repeated_hash_fraction"] == "0.5"
    assert m2["row_count"] == "1"
    assert m2["stale_row_fraction"] == "1"
    assert m2["zero_or_empty_top_size_fraction"] == "1"
