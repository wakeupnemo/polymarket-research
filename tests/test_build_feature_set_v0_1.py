from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.features.build_feature_set_v0_1 import build_feature_set_v0_1


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_feature_set_v0_1(tmp_path: Path) -> None:
    freeze_root = tmp_path / "data" / "features" / "polymarket" / "input_freezes"
    freeze_dir = freeze_root / "freeze_test_run__20260312T000000Z"
    freeze_dir.mkdir(parents=True, exist_ok=True)

    books_state_csv = freeze_dir / "books_state_test_run.csv"
    markets_csv = freeze_dir / "markets.csv"
    tokens_csv = freeze_dir / "tokens.csv"
    latest_state_manifest = freeze_dir / "latest_books_state_manifest.json"

    _write_csv(
        books_state_csv,
        [
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
            "best_bid_price",
            "best_bid_size",
            "best_ask_price",
            "best_ask_size",
            "mid_price",
            "spread",
            "bid_levels_count",
            "ask_levels_count",
            "last_trade_price",
            "hash",
            "source_jsonl",
        ],
        [
            {
                "source_run_id": "test_run",
                "collector_ts": "2026-03-12T00:00:10+00:00",
                "book_timestamp": "1773273600000",
                "iteration": "0",
                "batch_index": "0",
                "market_id": "m1",
                "event_id": "",
                "outcome": "Yes",
                "token_index": "0",
                "token_id": "tok_yes",
                "clob_market": "cond1",
                "best_bid_price": "0.45",
                "best_bid_size": "60",
                "best_ask_price": "0.55",
                "best_ask_size": "40",
                "mid_price": "0.50",
                "spread": "0.10",
                "bid_levels_count": "5",
                "ask_levels_count": "4",
                "last_trade_price": "0.52",
                "hash": "h1",
                "source_jsonl": "/tmp/raw.jsonl",
            },
            {
                "source_run_id": "test_run",
                "collector_ts": "2026-03-12T00:01:00+00:00",
                "book_timestamp": "1773273500000",
                "iteration": "0",
                "batch_index": "0",
                "market_id": "m2",
                "event_id": "",
                "outcome": "No",
                "token_index": "1",
                "token_id": "tok_no",
                "clob_market": "cond2",
                "best_bid_price": "0.20",
                "best_bid_size": "10",
                "best_ask_price": "0.90",
                "best_ask_size": "5",
                "mid_price": "0.55",
                "spread": "0.70",
                "bid_levels_count": "1",
                "ask_levels_count": "1",
                "last_trade_price": "0.10",
                "hash": "h2",
                "source_jsonl": "/tmp/raw.jsonl",
            },
        ],
    )

    _write_csv(markets_csv, ["market_id", "question"], [{"market_id": "m1", "question": "Q1"}])
    _write_csv(tokens_csv, ["market_id", "token_id", "outcome"], [{"market_id": "m1", "token_id": "tok_yes", "outcome": "Yes"}])

    latest_state_manifest.write_text(
        json.dumps({"source_run_id": "test_run", "output_csv": str(books_state_csv)}),
        encoding="utf-8",
    )

    freeze_manifest = freeze_root / "latest_feature_input_freeze_manifest.json"
    freeze_manifest.write_text(
        json.dumps(
            {
                "freeze_id": "test_run__20260312T000000Z",
                "source_run_id": "test_run",
                "books_state_csv": str(books_state_csv),
                "markets_csv": str(markets_csv),
                "tokens_csv": str(tokens_csv),
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
feature_builder:
  latest_freeze_manifest: data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json
  output_dir: data/features/polymarket/feature_sets
  feature_set_version: v0_1
  stale_threshold_ms: 15000
  quality_score_max_spread: 0.10
  quality_score_min_top_depth: 100
""",
        encoding="utf-8",
    )

    result = build_feature_set_v0_1(cfg)

    output_csv = Path(result["output_csv"])
    schema_json = Path(result["schema_json"])
    manifest_json = Path(result["manifest_json"])
    latest_manifest_json = tmp_path / "data" / "features" / "polymarket" / "feature_sets" / "latest_feature_set_manifest.json"

    assert output_csv.exists()
    assert schema_json.exists()
    assert manifest_json.exists()
    assert latest_manifest_json.exists()

    with output_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 2

    row1 = next(r for r in rows if r["token_id"] == "tok_yes")
    assert row1["feature_set_version"] == "v0_1"
    assert row1["spread"] == "0.1"
    assert row1["midpoint"] == "0.5"
    assert row1["best_bid_size"] == "60"
    assert row1["best_ask_size"] == "40"
    assert row1["top_of_book_imbalance"] == "0.2"
    assert row1["microprice_proxy"] == "0.51"
    assert row1["last_trade_minus_mid"] == "0.02"
    assert row1["bid_levels_count"] == "5"
    assert row1["ask_levels_count"] == "4"
    assert row1["staleness_flag"] == "0"
    assert row1["market_quality_score"] == "3"

    row2 = next(r for r in rows if r["token_id"] == "tok_no")
    assert row2["staleness_flag"] == "1"
    assert row2["market_quality_score"] == "1"
