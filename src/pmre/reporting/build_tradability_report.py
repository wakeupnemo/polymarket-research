from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import csv
import json

from pmre.config import load_config, project_root


DEFAULT_THRESHOLDS = {
    "min_row_count_keep": 25,
    "min_row_count_watch": 10,
    "max_stale_fraction_keep": 0.20,
    "max_stale_fraction_watch": 0.40,
    "max_repeated_hash_fraction_keep": 0.30,
    "max_repeated_hash_fraction_watch": 0.60,
    "max_median_spread_keep": 0.04,
    "max_median_spread_watch": 0.08,
    "max_p90_spread_keep": 0.09,
    "max_p90_spread_watch": 0.16,
    "max_zero_or_empty_top_size_fraction_keep": 0.20,
    "max_zero_or_empty_top_size_fraction_watch": 0.50,
    "min_mean_market_quality_score_keep": 2.00,
    "min_mean_market_quality_score_watch": 1.00,
}


REQUIRED_MARKET_COLUMNS = [
    "market_id",
    "row_count",
    "stale_row_fraction",
    "repeated_hash_fraction",
    "median_spread",
    "p90_spread",
    "median_best_bid_size",
    "median_best_ask_size",
    "zero_or_empty_top_size_fraction",
    "mean_market_quality_score",
    "median_market_quality_score",
]


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


def _parse_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _missing_or_above(value: float | None, threshold: float) -> bool:
    return value is None or value > threshold


def _missing_or_below(value: float | None, threshold: float) -> bool:
    return value is None or value < threshold


def _score_market(row: dict[str, Any], thresholds: dict[str, float]) -> float:
    score = 0.0

    row_count = _parse_int(row.get("row_count"))
    stale_fraction = _parse_float(row.get("stale_row_fraction"))
    repeated_hash_fraction = _parse_float(row.get("repeated_hash_fraction"))
    median_spread = _parse_float(row.get("median_spread"))
    p90_spread = _parse_float(row.get("p90_spread"))
    zero_or_empty_fraction = _parse_float(row.get("zero_or_empty_top_size_fraction"))
    mean_quality = _parse_float(row.get("mean_market_quality_score"))

    score += 25 if row_count >= thresholds["min_row_count_keep"] else (10 if row_count >= thresholds["min_row_count_watch"] else -20)

    if stale_fraction is None:
        score -= 15
    elif stale_fraction <= thresholds["max_stale_fraction_keep"]:
        score += 20
    elif stale_fraction <= thresholds["max_stale_fraction_watch"]:
        score += 5
    else:
        score -= 20

    if repeated_hash_fraction is None:
        score -= 10
    elif repeated_hash_fraction <= thresholds["max_repeated_hash_fraction_keep"]:
        score += 15
    elif repeated_hash_fraction <= thresholds["max_repeated_hash_fraction_watch"]:
        score += 5
    else:
        score -= 15

    if median_spread is None:
        score -= 15
    elif median_spread <= thresholds["max_median_spread_keep"]:
        score += 20
    elif median_spread <= thresholds["max_median_spread_watch"]:
        score += 5
    else:
        score -= 20

    if p90_spread is None:
        score -= 10
    elif p90_spread <= thresholds["max_p90_spread_keep"]:
        score += 10
    elif p90_spread <= thresholds["max_p90_spread_watch"]:
        score += 3
    else:
        score -= 10

    if zero_or_empty_fraction is None:
        score -= 10
    elif zero_or_empty_fraction <= thresholds["max_zero_or_empty_top_size_fraction_keep"]:
        score += 10
    elif zero_or_empty_fraction <= thresholds["max_zero_or_empty_top_size_fraction_watch"]:
        score += 3
    else:
        score -= 10

    if mean_quality is None:
        score -= 10
    elif mean_quality >= thresholds["min_mean_market_quality_score_keep"]:
        score += 15
    elif mean_quality >= thresholds["min_mean_market_quality_score_watch"]:
        score += 5
    else:
        score -= 15

    return score


def _classify_market(row: dict[str, Any], thresholds: dict[str, float]) -> tuple[str, str]:
    reasons: list[str] = []

    row_count = _parse_int(row.get("row_count"))
    stale_fraction = _parse_float(row.get("stale_row_fraction"))
    repeated_hash_fraction = _parse_float(row.get("repeated_hash_fraction"))
    median_spread = _parse_float(row.get("median_spread"))
    p90_spread = _parse_float(row.get("p90_spread"))
    zero_or_empty_fraction = _parse_float(row.get("zero_or_empty_top_size_fraction"))
    mean_quality = _parse_float(row.get("mean_market_quality_score"))

    if row_count < thresholds["min_row_count_watch"]:
        reasons.append("row_count_too_low")
    elif row_count < thresholds["min_row_count_keep"]:
        reasons.append("row_count_watch")

    if _missing_or_above(stale_fraction, thresholds["max_stale_fraction_watch"]):
        reasons.append("stale_too_high")
    elif _missing_or_above(stale_fraction, thresholds["max_stale_fraction_keep"]):
        reasons.append("stale_watch")

    if _missing_or_above(repeated_hash_fraction, thresholds["max_repeated_hash_fraction_watch"]):
        reasons.append("repeated_hash_too_high")
    elif _missing_or_above(repeated_hash_fraction, thresholds["max_repeated_hash_fraction_keep"]):
        reasons.append("repeated_hash_watch")

    if _missing_or_above(median_spread, thresholds["max_median_spread_watch"]):
        reasons.append("median_spread_too_wide")
    elif _missing_or_above(median_spread, thresholds["max_median_spread_keep"]):
        reasons.append("median_spread_watch")

    if _missing_or_above(p90_spread, thresholds["max_p90_spread_watch"]):
        reasons.append("p90_spread_too_wide")
    elif _missing_or_above(p90_spread, thresholds["max_p90_spread_keep"]):
        reasons.append("p90_spread_watch")

    if _missing_or_above(zero_or_empty_fraction, thresholds["max_zero_or_empty_top_size_fraction_watch"]):
        reasons.append("top_size_empty_too_often")
    elif _missing_or_above(zero_or_empty_fraction, thresholds["max_zero_or_empty_top_size_fraction_keep"]):
        reasons.append("top_size_watch")

    if _missing_or_below(mean_quality, thresholds["min_mean_market_quality_score_watch"]):
        reasons.append("quality_too_low")
    elif _missing_or_below(mean_quality, thresholds["min_mean_market_quality_score_keep"]):
        reasons.append("quality_watch")

    hard_exclude_reasons = {
        "row_count_too_low",
        "stale_too_high",
        "repeated_hash_too_high",
        "median_spread_too_wide",
        "p90_spread_too_wide",
        "top_size_empty_too_often",
        "quality_too_low",
    }

    gating_class = "keep"
    if any(reason in hard_exclude_reasons for reason in reasons):
        gating_class = "exclude"
    elif reasons:
        gating_class = "watch"

    gating_reason = "ok" if not reasons else "|".join(sorted(set(reasons)))
    return gating_class, gating_reason


def build_tradability_report(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    root = project_root(cfg)

    tradability_cfg = cfg.get("tradability_report", {})
    diagnostics_manifest_path = _resolve_path(
        root,
        tradability_cfg.get(
            "latest_diagnostics_manifest",
            "data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json",
        ),
    )
    latest_feature_manifest_path = _resolve_path(
        root,
        tradability_cfg.get(
            "latest_feature_set_manifest",
            "data/features/polymarket/feature_sets/latest_feature_set_manifest.json",
        ),
    )
    output_dir = _resolve_path(
        root,
        tradability_cfg.get("output_dir", "data/features/polymarket/universe"),
    )

    if not diagnostics_manifest_path.exists():
        raise FileNotFoundError(f"Missing latest diagnostics manifest: {diagnostics_manifest_path}")
    if not latest_feature_manifest_path.exists():
        raise FileNotFoundError(f"Missing latest feature-set manifest: {latest_feature_manifest_path}")

    diagnostics_manifest = json.loads(diagnostics_manifest_path.read_text(encoding="utf-8"))
    diagnostics_json_path = Path(diagnostics_manifest["diagnostics_json"]).resolve()
    diagnostics_market_summary_path = Path(diagnostics_manifest["market_summary_csv"]).resolve()

    if not diagnostics_json_path.exists():
        raise FileNotFoundError(f"Missing diagnostics JSON: {diagnostics_json_path}")
    if not diagnostics_market_summary_path.exists():
        raise FileNotFoundError(f"Missing diagnostics market-summary CSV: {diagnostics_market_summary_path}")

    latest_feature_manifest = json.loads(latest_feature_manifest_path.read_text(encoding="utf-8"))
    feature_csv_path = Path(latest_feature_manifest["output_csv"]).resolve()
    if not feature_csv_path.exists():
        raise FileNotFoundError(f"Missing feature-set CSV: {feature_csv_path}")

    diagnostics_payload = json.loads(diagnostics_json_path.read_text(encoding="utf-8"))

    diagnostics_feature_set_id = str(diagnostics_manifest.get("feature_set_id") or diagnostics_payload.get("feature_set_id") or "")
    feature_set_version = str(latest_feature_manifest.get("feature_set_version") or "")
    freeze_id = str(latest_feature_manifest.get("freeze_id") or "")
    manifest_feature_set_id = f"{feature_set_version}_{freeze_id}".strip("_")
    feature_set_id = diagnostics_feature_set_id or manifest_feature_set_id or feature_csv_path.stem

    if diagnostics_feature_set_id and manifest_feature_set_id and diagnostics_feature_set_id != manifest_feature_set_id:
        raise ValueError(
            "Mismatch between diagnostics feature_set_id and latest feature-set manifest: "
            f"{diagnostics_feature_set_id} != {manifest_feature_set_id}"
        )

    threshold_overrides = tradability_cfg.get("thresholds", {})
    thresholds: dict[str, float] = {k: float(threshold_overrides.get(k, v)) for k, v in DEFAULT_THRESHOLDS.items()}

    output_dir.mkdir(parents=True, exist_ok=True)
    report_json = output_dir / f"tradability_report_{feature_set_id}.json"
    market_summary_csv = output_dir / f"tradability_report_{feature_set_id}_market_summary.csv"
    active_universe_csv = output_dir / f"active_universe_{feature_set_id}.csv"
    latest_manifest_path = output_dir / "latest_tradability_manifest.json"

    with diagnostics_market_summary_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_MARKET_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Diagnostics market-summary CSV missing required columns: {missing}")
        input_rows = list(reader)

    enriched_rows: list[dict[str, str]] = []
    keep_rows: list[dict[str, str]] = []
    class_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()

    for row in input_rows:
        gating_class, gating_reason = _classify_market(row, thresholds)
        tradability_score = _score_market(row, thresholds)

        enriched = {
            "market_id": str(row.get("market_id") or ""),
            "row_count": str(_parse_int(row.get("row_count"))),
            "stale_row_fraction": _fmt_float(_parse_float(row.get("stale_row_fraction"))),
            "repeated_hash_fraction": _fmt_float(_parse_float(row.get("repeated_hash_fraction"))),
            "median_spread": _fmt_float(_parse_float(row.get("median_spread"))),
            "p90_spread": _fmt_float(_parse_float(row.get("p90_spread"))),
            "median_best_bid_size": _fmt_float(_parse_float(row.get("median_best_bid_size"))),
            "median_best_ask_size": _fmt_float(_parse_float(row.get("median_best_ask_size"))),
            "zero_or_empty_top_size_fraction": _fmt_float(_parse_float(row.get("zero_or_empty_top_size_fraction"))),
            "mean_market_quality_score": _fmt_float(_parse_float(row.get("mean_market_quality_score"))),
            "median_market_quality_score": _fmt_float(_parse_float(row.get("median_market_quality_score"))),
            "gating_class": gating_class,
            "tradability_score": _fmt_float(tradability_score),
            "gating_reason": gating_reason,
        }
        enriched_rows.append(enriched)

        class_counts[gating_class] += 1
        if gating_reason != "ok":
            for reason in gating_reason.split("|"):
                reason_counts[reason] += 1

        if gating_class == "keep":
            keep_rows.append(
                {
                    "market_id": enriched["market_id"],
                    "tradability_score": enriched["tradability_score"],
                    "gating_class": gating_class,
                    "gating_reason": gating_reason,
                    "row_count": enriched["row_count"],
                    "stale_row_fraction": enriched["stale_row_fraction"],
                    "repeated_hash_fraction": enriched["repeated_hash_fraction"],
                    "median_spread": enriched["median_spread"],
                    "p90_spread": enriched["p90_spread"],
                    "zero_or_empty_top_size_fraction": enriched["zero_or_empty_top_size_fraction"],
                    "mean_market_quality_score": enriched["mean_market_quality_score"],
                }
            )

    enriched_rows.sort(key=lambda r: (-_parse_float(r.get("tradability_score")) if _parse_float(r.get("tradability_score")) is not None else float("inf"), r["market_id"]))
    keep_rows.sort(key=lambda r: (-_parse_float(r.get("tradability_score")) if _parse_float(r.get("tradability_score")) is not None else float("inf"), r["market_id"]))

    summary_fields = REQUIRED_MARKET_COLUMNS + ["gating_class", "tradability_score", "gating_reason"]
    with market_summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(enriched_rows)

    active_fields = [
        "market_id",
        "tradability_score",
        "gating_class",
        "gating_reason",
        "row_count",
        "stale_row_fraction",
        "repeated_hash_fraction",
        "median_spread",
        "p90_spread",
        "zero_or_empty_top_size_fraction",
        "mean_market_quality_score",
    ]
    with active_universe_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=active_fields)
        writer.writeheader()
        writer.writerows(keep_rows)

    report_payload = {
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "feature_set_id": feature_set_id,
        "input_latest_diagnostics_manifest": str(diagnostics_manifest_path),
        "input_diagnostics_json": str(diagnostics_json_path),
        "input_diagnostics_market_summary_csv": str(diagnostics_market_summary_path),
        "input_latest_feature_set_manifest": str(latest_feature_manifest_path),
        "input_feature_set_csv": str(feature_csv_path),
        "thresholds": thresholds,
        "scoring_formula": {
            "description": "Simple additive score for first-pass tradability ranking. Higher is better.",
            "components": [
                "row_count rewards keep/watch thresholds and penalizes very low count",
                "stale_row_fraction rewards lower staleness",
                "repeated_hash_fraction rewards lower repetition",
                "median_spread and p90_spread reward tighter spreads",
                "zero_or_empty_top_size_fraction penalizes missing depth",
                "mean_market_quality_score rewards higher quality",
            ],
        },
        "market_counts": {
            "total": len(enriched_rows),
            "keep": class_counts.get("keep", 0),
            "watch": class_counts.get("watch", 0),
            "exclude": class_counts.get("exclude", 0),
        },
        "top_exclusion_reasons": reason_counts.most_common(10),
        "top_keep_markets": keep_rows[:10],
        "tradability_report_json": str(report_json),
        "market_summary_csv": str(market_summary_csv),
        "active_universe_csv": str(active_universe_csv),
    }
    report_json.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    latest_manifest = {
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "feature_set_id": feature_set_id,
        "input_latest_diagnostics_manifest": str(diagnostics_manifest_path),
        "input_latest_feature_set_manifest": str(latest_feature_manifest_path),
        "tradability_report_json": str(report_json),
        "market_summary_csv": str(market_summary_csv),
        "active_universe_csv": str(active_universe_csv),
        "manifest_json": str(latest_manifest_path),
    }
    latest_manifest_path.write_text(json.dumps(latest_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return latest_manifest
