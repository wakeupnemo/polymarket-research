from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.state.build_books_state import build_books_state


def test_build_books_state(tmp_path: Path) -> None:
    raw_dir = tmp_path / "data" / "raw" / "polymarket" / "books"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_jsonl = raw_dir / "books_run_test.jsonl"
    raw_manifest = raw_dir / "latest_books_manifest.json"

    envelope = {
        "collector_ts": "2026-03-11T21:42:30.014861+00:00",
        "iteration": 0,
        "batch_index": 0,
        "requested_token_ids": ["tok_yes", "tok_no"],
        "requested_tokens": [
            {
                "token_id": "tok_yes",
                "market_id": "m1",
                "event_id": "",
                "outcome": "Yes",
                "token_index": "0",
            },
            {
                "token_id": "tok_no",
                "market_id": "m1",
                "event_id": "",
                "outcome": "No",
                "token_index": "1",
            },
        ],
        "book_count": 2,
        "books": [
            {
                "market": "cond-m1",
                "asset_id": "tok_yes",
                "timestamp": "1773265349862",
                "hash": "hash-yes",
                "bids": [{"price": "0.40", "size": "10"}, {"price": "0.41", "size": "20"}],
                "asks": [{"price": "0.59", "size": "30"}, {"price": "0.58", "size": "40"}],
                "last_trade_price": "0.50",
            },
            {
                "market": "cond-m1",
                "asset_id": "tok_no",
                "timestamp": "1773265349862",
                "hash": "hash-no",
                "bids": [{"price": "0.60", "size": "15"}, {"price": "0.62", "size": "25"}],
                "asks": [{"price": "0.39", "size": "35"}, {"price": "0.38", "size": "45"}],
                "last_trade_price": "0.49",
            },
        ],
    }
    raw_jsonl.write_text(json.dumps(envelope) + "\n", encoding="utf-8")

    raw_manifest.write_text(
        json.dumps(
            {
                "run_id": "test_run",
                "output_jsonl": str(raw_jsonl),
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
state_builder:
  books_input_manifest: data/raw/polymarket/books/latest_books_manifest.json
  books_output_dir: data/state/polymarket
""",
        encoding="utf-8",
    )

    manifest = build_books_state(cfg)

    output_csv = Path(manifest["output_csv"])
    latest_manifest = tmp_path / "data" / "state" / "polymarket" / "latest_books_state_manifest.json"

    assert output_csv.exists()
    assert latest_manifest.exists()
    assert manifest["row_count"] == 2

    with output_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 2

    yes_row = next(row for row in rows if row["token_id"] == "tok_yes")
    assert yes_row["best_bid_price"] == "0.41"
    assert yes_row["best_ask_price"] == "0.58"
    assert yes_row["mid_price"] == "0.495"
    assert yes_row["spread"] == "0.17"

    no_row = next(row for row in rows if row["token_id"] == "tok_no")
    assert no_row["best_bid_price"] == "0.62"
    assert no_row["best_ask_price"] == "0.38"
