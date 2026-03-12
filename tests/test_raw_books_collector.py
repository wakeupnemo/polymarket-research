from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.ingest.raw_books_collector import run_raw_books_collection


class FakeClobClient:
    def get_books(self, token_ids: list[str]) -> list[dict]:
        rows = []
        for token_id in token_ids:
            rows.append(
                {
                    "market": "cond-demo",
                    "asset_id": token_id,
                    "timestamp": "1710000000",
                    "hash": f"hash-{token_id}",
                    "bids": [{"price": "0.45", "size": "100"}],
                    "asks": [{"price": "0.46", "size": "150"}],
                    "min_order_size": "1",
                    "tick_size": "0.01",
                    "neg_risk": False,
                    "last_trade_price": "0.455",
                }
            )
        return rows


def test_run_raw_books_collection(tmp_path: Path) -> None:
    tokens_dir = tmp_path / "data" / "reference" / "polymarket"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    tokens_csv = tokens_dir / "tokens.csv"
    with tokens_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["run_ts", "market_id", "event_id", "token_index", "outcome", "token_id", "outcome_price"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "run_ts": "x",
                "market_id": "m1",
                "event_id": "",
                "token_index": "0",
                "outcome": "Yes",
                "token_id": "tok_yes_1",
                "outcome_price": "0.4",
            }
        )
        writer.writerow(
            {
                "run_ts": "x",
                "market_id": "m1",
                "event_id": "",
                "token_index": "1",
                "outcome": "No",
                "token_id": "tok_no_1",
                "outcome_price": "0.6",
            }
        )
        writer.writerow(
            {
                "run_ts": "x",
                "market_id": "m2",
                "event_id": "",
                "token_index": "0",
                "outcome": "Yes",
                "token_id": "tok_yes_2",
                "outcome_price": "0.55",
            }
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
raw_books:
  clob_base_url: https://clob.polymarket.com
  token_limit: 3
  batch_size: 2
  iterations: 2
  poll_interval_seconds: 0
  timeout_seconds: 30
  max_retries: 5
""",
        encoding="utf-8",
    )

    manifest = run_raw_books_collection(cfg, client=FakeClobClient())

    output_jsonl = Path(manifest["output_jsonl"])
    manifest_json = Path(manifest["manifest_json"])

    assert output_jsonl.exists()
    assert manifest_json.exists()
    assert manifest["selected_token_count"] == 3
    assert manifest["batch_count_per_iteration"] == 2
    assert manifest["iterations"] == 2
    assert manifest["jsonl_line_count"] == 4

    lines = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 4
    assert lines[0]["book_count"] >= 1
    assert lines[0]["books"][0]["asset_id"] in {"tok_yes_1", "tok_no_1", "tok_yes_2"}
