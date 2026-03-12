from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import csv
import json

from pmre.config import load_config, project_root


DEFAULT_HORIZONS = [1, 2, 5]
DEFAULT_MIN_MARKET_QUALITY_SCORE = 1.0


def _resolve_path(root: Path, path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _resolve_manifest_file(root: Path, path_value: str | Path) -> Path:
    """Resolve paths stored in manifests with a conservative fallback.

    Some checked-in manifests may contain absolute paths from another workstation.
    If that absolute path is missing, try to re-anchor from the local project root
    using the first `data/...` suffix found in the original path.
    """

    raw = str(path_value or "")
    direct = _resolve_path(root, raw)
    if direct.exists():
        return direct

    marker = "data/"
    idx = raw.find(marker)
    if idx >= 0:
        rebased = (root / raw[idx:]).resolve()
        if rebased.exists():
            return rebased

    return direct


def _parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _fraction_true(flags: list[bool]) -> float | None:
    if not flags:
        return None
    return sum(1 for x in flags if x) / len(flags)


def _future_value(series: list[float | None], i: int, horizon: int) -> float | None:
    j = i + horizon
    if j >= len(series):
        return None
    return series[j]


def build_maker_markout_report(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    root = project_root(cfg)

    markout_cfg = cfg.get("maker_markout", {})
    latest_tradability_manifest = _resolve_path(
        root,
        markout_cfg.get("latest_tradability_manifest", "data/features/polymarket/universe/latest_tradability_manifest.json"),
    )
    latest_feature_manifest = _resolve_path(
        root,
        markout_cfg.get("latest_feature_set_manifest", "data/features/polymarket/feature_sets/latest_feature_set_manifest.json"),
    )
    output_dir = _resolve_path(
        root,
        markout_cfg.get("output_dir", "data/experiments/polymarket/maker_markout"),
    )
    horizons = [int(h) for h in markout_cfg.get("row_step_horizons", DEFAULT_HORIZONS)]
    min_market_quality_score = float(markout_cfg.get("min_market_quality_score", DEFAULT_MIN_MARKET_QUALITY_SCORE))

    if not latest_tradability_manifest.exists():
        raise FileNotFoundError(
            "Missing prerequisite tradability manifest: "
            f"{latest_tradability_manifest}. Run build-tradability-report first."
        )
    if not latest_feature_manifest.exists():
        raise FileNotFoundError(f"Missing latest feature-set manifest: {latest_feature_manifest}")

    tradability_payload = json.loads(latest_tradability_manifest.read_text(encoding="utf-8"))
    active_universe_csv = _resolve_manifest_file(root, tradability_payload.get("active_universe_csv", ""))
    if not active_universe_csv.exists():
        raise FileNotFoundError(
            "Missing prerequisite active-universe CSV: "
            f"{active_universe_csv}. Run build-tradability-report first."
        )

    feature_payload = json.loads(latest_feature_manifest.read_text(encoding="utf-8"))
    feature_csv = _resolve_manifest_file(root, feature_payload.get("output_csv", ""))
    if not feature_csv.exists():
        raise FileNotFoundError(f"Missing feature-set CSV: {feature_csv}")

    feature_set_version = str(feature_payload.get("feature_set_version") or "")
    freeze_id = str(feature_payload.get("freeze_id") or "")
    run_id = f"{feature_set_version}_{freeze_id}".strip("_") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    active_market_ids: set[str] = set()
    with active_universe_csv.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if "market_id" not in (reader.fieldnames or []):
            raise ValueError("active-universe CSV missing required market_id column")
        for row in reader:
            market_id = str(row.get("market_id") or "").strip()
            if market_id:
                active_market_ids.add(market_id)

    # Candidate selection is intentionally conservative and explicit.
    # This is a triage scaffold, not an execution simulator.
    selected_rows: list[dict[str, Any]] = []
    selection_counts: dict[str, int] = defaultdict(int)

    with feature_csv.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            selection_counts["total_rows"] += 1

            market_id = str(row.get("market_id") or "").strip()
            token_id = str(row.get("token_id") or "").strip()
            collector_ts = str(row.get("collector_ts") or "").strip()
            spread = _parse_float(row.get("spread"))
            midpoint = _parse_float(row.get("midpoint"))
            staleness_flag = str(row.get("staleness_flag") or "").strip()
            market_quality_score = _parse_float(row.get("market_quality_score"))

            if not market_id:
                selection_counts["drop_missing_market_id"] += 1
                continue
            if market_id not in active_market_ids:
                selection_counts["drop_not_in_active_universe"] += 1
                continue
            if not token_id:
                selection_counts["drop_missing_token_id"] += 1
                continue
            if spread is None:
                selection_counts["drop_null_spread"] += 1
                continue
            if spread <= 0:
                selection_counts["drop_non_positive_spread"] += 1
                continue
            if midpoint is None:
                selection_counts["drop_null_midpoint"] += 1
                continue
            if staleness_flag == "1":
                selection_counts["drop_stale"] += 1
                continue
            if market_quality_score is None or market_quality_score < min_market_quality_score:
                selection_counts["drop_low_market_quality"] += 1
                continue

            # Stable feature-set v0_1 does not carry best bid/ask prices directly.
            # We derive quote prices from midpoint +/- spread/2 for a consistent,
            # conservative snapshot-based diagnostic view.
            buy_quote_price = midpoint - (spread / 2.0)
            sell_quote_price = midpoint + (spread / 2.0)

            selected_rows.append(
                {
                    "market_id": market_id,
                    "token_id": token_id,
                    "collector_ts": collector_ts,
                    "spread": spread,
                    "midpoint": midpoint,
                    "best_bid_size": _parse_float(row.get("best_bid_size")),
                    "best_ask_size": _parse_float(row.get("best_ask_size")),
                    "market_quality_score": market_quality_score,
                    "buy_quote_price": buy_quote_price,
                    "sell_quote_price": sell_quote_price,
                }
            )
            selection_counts["selected_rows"] += 1

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in selected_rows:
        groups[(str(row["market_id"]), str(row["token_id"]))].append(row)

    row_outputs: list[dict[str, str]] = []
    for _, rows in groups.items():
        rows.sort(key=lambda r: str(r["collector_ts"]))
        mids = [r["midpoint"] for r in rows]

        for i, row in enumerate(rows):
            out_row = {
                "market_id": str(row["market_id"]),
                "token_id": str(row["token_id"]),
                "collector_ts": str(row["collector_ts"]),
                "spread": _fmt_float(row["spread"]),
                "midpoint": _fmt_float(row["midpoint"]),
                "best_bid_size": _fmt_float(row["best_bid_size"]),
                "best_ask_size": _fmt_float(row["best_ask_size"]),
                "market_quality_score": _fmt_float(row["market_quality_score"]),
                "buy_quote_price": _fmt_float(row["buy_quote_price"]),
                "sell_quote_price": _fmt_float(row["sell_quote_price"]),
            }

            for horizon in horizons:
                future_mid = _future_value(mids, i, horizon)
                # Sign conventions:
                # - buy_markout > 0 means a passive bid at current snapshot looks favorable
                #   versus future midpoint; buy_markout < 0 implies adverse selection risk.
                # - sell_markout > 0 means a passive ask at current snapshot looks favorable
                #   versus future midpoint; sell_markout < 0 implies adverse selection risk.
                buy_markout = None if future_mid is None else future_mid - float(row["buy_quote_price"])
                sell_markout = None if future_mid is None else float(row["sell_quote_price"]) - future_mid

                out_row[f"future_mid_h{horizon}"] = _fmt_float(future_mid)
                out_row[f"buy_markout_h{horizon}"] = _fmt_float(buy_markout)
                out_row[f"sell_markout_h{horizon}"] = _fmt_float(sell_markout)

            row_outputs.append(out_row)

    row_outputs.sort(key=lambda r: (r["market_id"], r["token_id"], r["collector_ts"]))

    market_summary: list[dict[str, str]] = []
    by_market: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in row_outputs:
        by_market[row["market_id"]].append(row)

    for market_id in sorted(by_market):
        rows = by_market[market_id]
        spreads = [_parse_float(r.get("spread")) for r in rows]
        qualities = [_parse_float(r.get("market_quality_score")) for r in rows]

        summary_row: dict[str, str] = {
            "market_id": market_id,
            "row_count": str(len(rows)),
            "mean_spread": _fmt_float(_mean([x for x in spreads if x is not None])),
            "mean_market_quality_score": _fmt_float(_mean([x for x in qualities if x is not None])),
        }

        for horizon in horizons:
            buy_vals = [_parse_float(r.get(f"buy_markout_h{horizon}")) for r in rows]
            sell_vals = [_parse_float(r.get(f"sell_markout_h{horizon}")) for r in rows]

            clean_buy = [x for x in buy_vals if x is not None]
            clean_sell = [x for x in sell_vals if x is not None]

            summary_row[f"mean_buy_markout_h{horizon}"] = _fmt_float(_mean(clean_buy))
            summary_row[f"mean_sell_markout_h{horizon}"] = _fmt_float(_mean(clean_sell))

            if horizon == 1:
                summary_row["adverse_buy_markout_fraction"] = _fmt_float(_fraction_true([x < 0 for x in clean_buy]))
                summary_row["adverse_sell_markout_fraction"] = _fmt_float(_fraction_true([x < 0 for x in clean_sell]))

        market_summary.append(summary_row)

    output_dir.mkdir(parents=True, exist_ok=True)
    rows_csv = output_dir / f"maker_markout_{run_id}_rows.csv"
    market_summary_csv = output_dir / f"maker_markout_{run_id}_market_summary.csv"
    report_json = output_dir / f"maker_markout_{run_id}.json"
    latest_manifest = output_dir / "latest_maker_markout_manifest.json"

    row_fields = [
        "market_id",
        "token_id",
        "collector_ts",
        "spread",
        "midpoint",
        "best_bid_size",
        "best_ask_size",
        "market_quality_score",
        "buy_quote_price",
        "sell_quote_price",
    ]
    for horizon in horizons:
        row_fields += [f"future_mid_h{horizon}", f"buy_markout_h{horizon}", f"sell_markout_h{horizon}"]

    with rows_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=row_fields)
        writer.writeheader()
        writer.writerows(row_outputs)

    summary_fields = [
        "market_id",
        "row_count",
        "mean_spread",
        "mean_market_quality_score",
    ]
    for horizon in horizons:
        summary_fields += [f"mean_buy_markout_h{horizon}", f"mean_sell_markout_h{horizon}"]
    summary_fields += ["adverse_buy_markout_fraction", "adverse_sell_markout_fraction"]

    with market_summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(market_summary)

    payload = {
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "feature_set_id": run_id,
        "input_latest_tradability_manifest": str(latest_tradability_manifest),
        "input_active_universe_csv": str(active_universe_csv),
        "input_latest_feature_set_manifest": str(latest_feature_manifest),
        "input_feature_set_csv": str(feature_csv),
        "horizon_type": "row_steps",
        "row_step_horizons": horizons,
        "min_market_quality_score": min_market_quality_score,
        "selection_counts": selection_counts,
        "assumptions": {
            "scope": "Conservative snapshot-based maker markout scaffold for triage only.",
            "not_execution_pnl": True,
            "no_queue_modeling": True,
            "no_fee_modeling": True,
            "no_fill_probability_modeling": True,
            "quote_price_derivation": "best_bid/best_ask approximated from midpoint +/- spread/2 in stable feature set v0_1",
        },
        "rows_csv": str(rows_csv),
        "market_summary_csv": str(market_summary_csv),
        "report_json": str(report_json),
    }
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    latest_payload = {
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "feature_set_id": run_id,
        "input_latest_tradability_manifest": str(latest_tradability_manifest),
        "input_latest_feature_set_manifest": str(latest_feature_manifest),
        "report_json": str(report_json),
        "rows_csv": str(rows_csv),
        "market_summary_csv": str(market_summary_csv),
        "manifest_json": str(latest_manifest),
    }
    latest_manifest.write_text(json.dumps(latest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return latest_payload
