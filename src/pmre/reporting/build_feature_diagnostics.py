from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any
import csv
import json

from pmre.config import load_config, project_root


DEFAULT_WIDE_SPREAD_THRESHOLD = 0.10
DEFAULT_LOW_QUALITY_THRESHOLD = 1.0


def _resolve_path(root: Path, path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _p90(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(0.9 * (len(ordered) - 1)))))
    return ordered[index]


def build_feature_diagnostics(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    root = project_root(cfg)

    diagnostics_cfg = cfg.get("feature_diagnostics", {})
    latest_feature_manifest = _resolve_path(
        root,
        diagnostics_cfg.get(
            "latest_feature_set_manifest",
            "data/features/polymarket/feature_sets/latest_feature_set_manifest.json",
        ),
    )
    output_dir = _resolve_path(
        root,
        diagnostics_cfg.get("output_dir", "data/features/polymarket/diagnostics"),
    )
    wide_spread_threshold = float(diagnostics_cfg.get("wide_spread_threshold", DEFAULT_WIDE_SPREAD_THRESHOLD))
    low_quality_threshold = float(diagnostics_cfg.get("low_quality_threshold", DEFAULT_LOW_QUALITY_THRESHOLD))

    if not latest_feature_manifest.exists():
        raise FileNotFoundError(f"Missing latest feature-set manifest: {latest_feature_manifest}")

    feature_manifest = json.loads(latest_feature_manifest.read_text(encoding="utf-8"))
    feature_csv = Path(feature_manifest["output_csv"]).resolve()
    if not feature_csv.exists():
        raise FileNotFoundError(f"Missing feature-set CSV: {feature_csv}")

    feature_set_version = str(feature_manifest.get("feature_set_version", ""))
    freeze_id = str(feature_manifest.get("freeze_id", ""))
    feature_set_id = f"{feature_set_version}_{freeze_id}".strip("_") or feature_csv.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    diagnostics_json = output_dir / f"feature_diagnostics_{feature_set_id}.json"
    market_summary_csv = output_dir / f"feature_diagnostics_{feature_set_id}_market_summary.csv"
    latest_diagnostics_manifest = output_dir / "latest_feature_diagnostics_manifest.json"

    total_row_count = 0
    stale_row_count = 0
    missing_spread_count = 0
    non_positive_spread_count = 0
    wide_spread_count = 0
    zero_or_empty_top_size_count = 0
    null_imbalance_count = 0
    null_microprice_count = 0
    quality_scores: list[float] = []
    low_quality_row_count = 0

    repeated_hash_row_count = 0
    hash_present = False
    last_hash_by_token: dict[str, str] = {}

    market_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "row_count": 0,
            "stale_count": 0,
            "spreads": [],
            "best_bid_sizes": [],
            "best_ask_sizes": [],
            "zero_or_empty_top_size_count": 0,
            "repeated_hash_count": 0,
            "quality_scores": [],
        }
    )

    with feature_csv.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            total_row_count += 1
            market_id = str(row.get("market_id") or "")
            token_id = str(row.get("token_id") or "")
            market_bucket = market_stats[market_id]
            market_bucket["row_count"] += 1

            staleness_flag = _parse_int(row.get("staleness_flag")) or 0
            if staleness_flag == 1:
                stale_row_count += 1
                market_bucket["stale_count"] += 1

            spread = _parse_float(row.get("spread"))
            if spread is None:
                missing_spread_count += 1
            else:
                market_bucket["spreads"].append(spread)
                if spread <= 0:
                    non_positive_spread_count += 1
                if spread > wide_spread_threshold:
                    wide_spread_count += 1

            best_bid_size = _parse_float(row.get("best_bid_size"))
            best_ask_size = _parse_float(row.get("best_ask_size"))
            if best_bid_size is not None:
                market_bucket["best_bid_sizes"].append(best_bid_size)
            if best_ask_size is not None:
                market_bucket["best_ask_sizes"].append(best_ask_size)

            if (best_bid_size or 0.0) <= 0 or (best_ask_size or 0.0) <= 0:
                zero_or_empty_top_size_count += 1
                market_bucket["zero_or_empty_top_size_count"] += 1

            if _parse_float(row.get("top_of_book_imbalance")) is None:
                null_imbalance_count += 1

            if _parse_float(row.get("microprice_proxy")) is None:
                null_microprice_count += 1

            quality_score = _parse_float(row.get("market_quality_score"))
            if quality_score is not None:
                quality_scores.append(quality_score)
                market_bucket["quality_scores"].append(quality_score)
                if quality_score < low_quality_threshold:
                    low_quality_row_count += 1

            hash_value = str(row.get("hash") or "")
            if hash_value:
                hash_present = True
                previous_hash = last_hash_by_token.get(token_id, "")
                is_repeated = hash_value == previous_hash
                if is_repeated:
                    repeated_hash_row_count += 1
                    market_bucket["repeated_hash_count"] += 1
                last_hash_by_token[token_id] = hash_value

    aggregate_summary = {
        "feature_set_id": feature_set_id,
        "feature_set_version": feature_set_version,
        "freeze_id": freeze_id,
        "total_row_count": total_row_count,
        "stale_row_count": stale_row_count,
        "stale_row_fraction": 0.0 if total_row_count == 0 else stale_row_count / total_row_count,
        "missing_spread_count": missing_spread_count,
        "non_positive_spread_count": non_positive_spread_count,
        "wide_spread_count": wide_spread_count,
        "wide_spread_threshold": wide_spread_threshold,
        "zero_or_empty_top_size_count": zero_or_empty_top_size_count,
        "null_imbalance_count": null_imbalance_count,
        "null_microprice_count": null_microprice_count,
        "repeated_hash_row_count": repeated_hash_row_count if hash_present else None,
        "repeated_hash_fraction": (repeated_hash_row_count / total_row_count) if hash_present and total_row_count > 0 else None,
        "mean_market_quality_score": (sum(quality_scores) / len(quality_scores)) if quality_scores else None,
        "median_market_quality_score": median(quality_scores) if quality_scores else None,
        "low_quality_threshold": low_quality_threshold,
        "low_quality_row_count": low_quality_row_count,
    }

    market_summary_fieldnames = [
        "market_id",
        "row_count",
        "stale_row_fraction",
        "median_spread",
        "p90_spread",
        "median_best_bid_size",
        "median_best_ask_size",
        "zero_or_empty_top_size_fraction",
        "repeated_hash_fraction",
        "mean_market_quality_score",
        "median_market_quality_score",
    ]

    with market_summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=market_summary_fieldnames)
        writer.writeheader()
        for market_id in sorted(market_stats):
            stats = market_stats[market_id]
            row_count = int(stats["row_count"])
            spreads = list(stats["spreads"])
            bid_sizes = list(stats["best_bid_sizes"])
            ask_sizes = list(stats["best_ask_sizes"])
            market_quality_scores = list(stats["quality_scores"])
            repeated_hash_count = int(stats["repeated_hash_count"])

            writer.writerow(
                {
                    "market_id": market_id,
                    "row_count": str(row_count),
                    "stale_row_fraction": _fmt_float(0.0 if row_count == 0 else stats["stale_count"] / row_count),
                    "median_spread": _fmt_float(median(spreads) if spreads else None),
                    "p90_spread": _fmt_float(_p90(spreads)),
                    "median_best_bid_size": _fmt_float(median(bid_sizes) if bid_sizes else None),
                    "median_best_ask_size": _fmt_float(median(ask_sizes) if ask_sizes else None),
                    "zero_or_empty_top_size_fraction": _fmt_float(
                        0.0 if row_count == 0 else stats["zero_or_empty_top_size_count"] / row_count
                    ),
                    "repeated_hash_fraction": _fmt_float((repeated_hash_count / row_count) if hash_present and row_count > 0 else None),
                    "mean_market_quality_score": _fmt_float(
                        (sum(market_quality_scores) / len(market_quality_scores)) if market_quality_scores else None
                    ),
                    "median_market_quality_score": _fmt_float(median(market_quality_scores) if market_quality_scores else None),
                }
            )

    diagnostics_payload = {
        "run_ts": datetime.now(UTC).isoformat(),
        "feature_set_id": feature_set_id,
        "input_feature_manifest": str(latest_feature_manifest),
        "input_feature_csv": str(feature_csv),
        "aggregate_summary": aggregate_summary,
        "market_summary_csv": str(market_summary_csv),
        "diagnostics_json": str(diagnostics_json),
    }

    diagnostics_json.write_text(json.dumps(diagnostics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "run_ts": datetime.now(UTC).isoformat(),
        "feature_set_id": feature_set_id,
        "input_feature_set_manifest": str(latest_feature_manifest),
        "input_feature_csv": str(feature_csv),
        "diagnostics_json": str(diagnostics_json),
        "market_summary_csv": str(market_summary_csv),
        "manifest_json": str(latest_diagnostics_manifest),
    }
    latest_diagnostics_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
