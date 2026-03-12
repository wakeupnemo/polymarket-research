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
