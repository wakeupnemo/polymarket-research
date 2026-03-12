from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.ingest.metadata_refresh import run_metadata_refresh


class FakeGammaClient:
    def list_markets(self, *, closed: bool, limit: int, offset: int):
        assert closed is False
        assert limit == 50

        if offset > 0:
            return []

        return [
            {
                "id": "market-1",
                "eventId": "event-1",
                "conditionId": "cond-1",
                "questionId": "q-1",
                "slug": "demo-market",
                "question": "Will demo happen?",
                "category": "politics",
                "active": True,
                "closed": False,
                "archived": False,
                "acceptingOrders": True,
                "enableOrderBook": True,
                "minimumOrderSize": 5,
                "minimumTickSize": 0.01,
                "liquidity": 123.4,
                "volume": 567.8,
                "startDate": "2026-03-01T00:00:00Z",
                "endDate": "2026-03-31T00:00:00Z",
                "description": "demo desc",
                "marketType": "binary",
                "formatType": "binary",
                "outcomes": "[\"Yes\", \"No\"]",
                "outcomePrices": "[\"0.42\", \"0.58\"]",
                "clobTokenIds": "[\"tok_yes\", \"tok_no\"]",
            }
        ]


def test_run_metadata_refresh(tmp_path: Path) -> None:
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
metadata:
  gamma_base_url: https://gamma-api.polymarket.com
  active: true
  closed: false
  page_limit: 50
  pause_seconds: 0
  timeout_seconds: 60
  max_retries: 5
  resume: true
""",
        encoding="utf-8",
    )

    manifest = run_metadata_refresh(cfg, client=FakeGammaClient())

    markets_csv = Path(manifest["markets_csv"])
    tokens_csv = Path(manifest["tokens_csv"])
    manifest_json = tmp_path / "data" / "raw" / "polymarket" / "metadata" / "metadata_refresh_manifest.json"

    assert markets_csv.exists()
    assert tokens_csv.exists()
    assert manifest_json.exists()

    with markets_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["market_id"] == "market-1"
    assert rows[0]["event_id"] == "event-1"

    with tokens_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert {row["token_id"] for row in rows} == {"tok_yes", "tok_no"}

    manifest_payload = json.loads(manifest_json.read_text(encoding="utf-8"))
    assert manifest_payload["market_count"] == 1
    assert manifest_payload["token_count"] == 2
