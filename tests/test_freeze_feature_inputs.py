from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.features.freeze_feature_inputs import freeze_feature_inputs


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_freeze_feature_inputs(tmp_path: Path) -> None:
    state_dir = tmp_path / "data" / "state" / "polymarket"
    ref_dir = tmp_path / "data" / "reference" / "polymarket"
    state_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    books_state_csv = state_dir / "books_state_test_run.csv"
    latest_state_manifest = state_dir / "latest_books_state_manifest.json"
    markets_csv = ref_dir / "markets.csv"
    tokens_csv = ref_dir / "tokens.csv"

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
                "collector_ts": "2026-03-12T00:00:00Z",
                "book_timestamp": "1",
                "iteration": "0",
                "batch_index": "0",
                "market_id": "m1",
                "event_id": "",
                "outcome": "Yes",
                "token_index": "0",
                "token_id": "tok1",
                "clob_market": "cond1",
                "best_bid_price": "0.45",
                "best_bid_size": "10",
                "best_ask_price": "0.55",
                "best_ask_size": "20",
                "mid_price": "0.5",
                "spread": "0.1",
                "bid_levels_count": "3",
                "ask_levels_count": "4",
                "last_trade_price": "0.51",
                "hash": "h1",
                "source_jsonl": "/tmp/raw.jsonl",
            }
        ],
    )

    latest_state_manifest.write_text(
        json.dumps(
            {
                "source_run_id": "test_run",
                "output_csv": str(books_state_csv),
            }
        ),
        encoding="utf-8",
    )

    _write_csv(
        markets_csv,
        ["market_id", "question"],
        [{"market_id": "m1", "question": "Will X happen?"}],
    )

    _write_csv(
        tokens_csv,
        ["market_id", "token_id", "outcome"],
        [{"market_id": "m1", "token_id": "tok1", "outcome": "Yes"}],
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
feature_input_freeze:
  latest_state_manifest: data/state/polymarket/latest_books_state_manifest.json
  markets_csv: data/reference/polymarket/markets.csv
  tokens_csv: data/reference/polymarket/tokens.csv
  output_dir: data/features/polymarket/input_freezes
""",
        encoding="utf-8",
    )

    result = freeze_feature_inputs(cfg)

    freeze_dir = Path(result["freeze_dir"])
    manifest_json = Path(result["manifest_json"])
    latest_manifest_json = Path(result["latest_manifest_json"])

    assert freeze_dir.exists()
    assert manifest_json.exists()
    assert latest_manifest_json.exists()

    assert (freeze_dir / "latest_books_state_manifest.json").exists()
    assert (freeze_dir / "books_state_test_run.csv").exists()
    assert (freeze_dir / "markets.csv").exists()
    assert (freeze_dir / "tokens.csv").exists()

    payload = json.loads(manifest_json.read_text(encoding="utf-8"))
    assert payload["source_run_id"] == "test_run"
    assert payload["policy"]["allowed_inputs_only"] == [
        "latest_books_state_manifest",
        "books_state_csv",
        "markets_csv",
        "tokens_csv",
    ]
    assert payload["frozen_files"]["books_state_csv"]["row_count"] == 1
    assert payload["frozen_files"]["markets_csv"]["row_count"] == 1
    assert payload["frozen_files"]["tokens_csv"]["row_count"] == 1
