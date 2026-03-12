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
