from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import csv
import json

from pmre.config import load_config, project_root


def _resolve_path(root: Path, path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


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


def _iso_to_epoch_ms(iso_ts: str) -> int | None:
    if not iso_ts:
        return None
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except ValueError:
        return None


def _compute_top_of_book_imbalance(best_bid_size: float | None, best_ask_size: float | None) -> float | None:
    if best_bid_size is None or best_ask_size is None:
        return None
    denom = best_bid_size + best_ask_size
    if denom <= 0:
        return None
    return (best_bid_size - best_ask_size) / denom


def _compute_microprice_proxy(
    best_bid_price: float | None,
    best_ask_price: float | None,
    best_bid_size: float | None,
    best_ask_size: float | None,
) -> float | None:
    if None in (best_bid_price, best_ask_price, best_bid_size, best_ask_size):
        return None
    denom = best_bid_size + best_ask_size
    if denom <= 0:
        return None
    return ((best_ask_price * best_bid_size) + (best_bid_price * best_ask_size)) / denom


def build_books_features(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    root = project_root(cfg)

    builder_cfg = cfg.get("books_feature_builder", {})
    latest_state_manifest = _resolve_path(
        root,
        builder_cfg.get("latest_state_manifest", "data/state/polymarket/latest_books_state_manifest.json"),
    )
    output_dir = _resolve_path(root, builder_cfg.get("output_dir", "data/features/polymarket"))
    stale_threshold_ms = int(builder_cfg.get("stale_threshold_ms", 15000))

    if not latest_state_manifest.exists():
        raise FileNotFoundError(f"Missing latest books state manifest: {latest_state_manifest}")

    state_manifest = json.loads(latest_state_manifest.read_text(encoding="utf-8"))
    source_run_id = str(state_manifest.get("source_run_id") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    state_csv = Path(state_manifest["output_csv"]).resolve()

    if not state_csv.exists():
        raise FileNotFoundError(f"Missing books state CSV: {state_csv}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / f"books_features_{source_run_id}.csv"
    output_manifest = output_dir / f"books_features_{source_run_id}_manifest.json"
    latest_output_manifest = output_dir / "latest_books_features_manifest.json"

    fieldnames = [
        "source_run_id",
        "collector_ts",
        "book_timestamp",
        "market_id",
        "event_id",
        "outcome",
        "token_id",
        "clob_market",
        "hash",
        "spread",
        "midpoint",
        "best_bid_size",
        "best_ask_size",
        "top_of_book_imbalance",
        "microprice_proxy",
        "last_trade_minus_mid",
        "bid_levels_count",
        "ask_levels_count",
        "staleness_flag",
    ]

    row_count_in = 0
    row_count_out = 0
    missing_token_id_count = 0
    missing_bid_ask_count = 0
    negative_spread_count = 0
    zero_depth_rows_count = 0
    null_imbalance_count = 0
    null_microprice_count = 0
    null_last_trade_minus_mid_count = 0

    with state_csv.open("r", encoding="utf-8", newline="") as in_fh, output_csv.open("w", encoding="utf-8", newline="") as out_fh:
        reader = csv.DictReader(in_fh)
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row_count_in += 1

            token_id = _to_str(row.get("token_id"))
            if not token_id:
                missing_token_id_count += 1

            best_bid_price = _parse_float(row.get("best_bid_price"))
            best_ask_price = _parse_float(row.get("best_ask_price"))
            best_bid_size = _parse_float(row.get("best_bid_size"))
            best_ask_size = _parse_float(row.get("best_ask_size"))
            midpoint = _parse_float(row.get("mid_price"))
            spread = _parse_float(row.get("spread"))
            last_trade_price = _parse_float(row.get("last_trade_price"))
            bid_levels_count = _parse_int(row.get("bid_levels_count"))
            ask_levels_count = _parse_int(row.get("ask_levels_count"))

            if best_bid_price is None or best_ask_price is None:
                missing_bid_ask_count += 1

            if midpoint is None and best_bid_price is not None and best_ask_price is not None:
                midpoint = (best_bid_price + best_ask_price) / 2.0

            if spread is None and best_bid_price is not None and best_ask_price is not None:
                spread = best_ask_price - best_bid_price

            if spread is not None and spread < 0:
                negative_spread_count += 1

            bid_size_value = best_bid_size or 0.0
            ask_size_value = best_ask_size or 0.0
            if (bid_size_value + ask_size_value) <= 0:
                zero_depth_rows_count += 1

            top_of_book_imbalance = _compute_top_of_book_imbalance(best_bid_size, best_ask_size)
            if top_of_book_imbalance is None:
                null_imbalance_count += 1

            microprice_proxy = _compute_microprice_proxy(best_bid_price, best_ask_price, best_bid_size, best_ask_size)
            if microprice_proxy is None:
                null_microprice_count += 1

            last_trade_minus_mid = None
            if last_trade_price is not None and midpoint is not None:
                last_trade_minus_mid = last_trade_price - midpoint
            if last_trade_minus_mid is None:
                null_last_trade_minus_mid_count += 1

            collector_ms = _iso_to_epoch_ms(_to_str(row.get("collector_ts")))
            book_ms = _parse_int(row.get("book_timestamp"))
            age_ms = None if collector_ms is None or book_ms is None else collector_ms - book_ms

            staleness_flag = 0
            if (
                best_bid_price is None
                or best_ask_price is None
                or spread is None
                or spread <= 0
                or age_ms is None
                or age_ms < 0
                or age_ms > stale_threshold_ms
            ):
                staleness_flag = 1

            out_row = {
                "source_run_id": source_run_id,
                "collector_ts": _to_str(row.get("collector_ts")),
                "book_timestamp": _to_str(row.get("book_timestamp")),
                "market_id": _to_str(row.get("market_id")),
                "event_id": _to_str(row.get("event_id")),
                "outcome": _to_str(row.get("outcome")),
                "token_id": token_id,
                "clob_market": _to_str(row.get("clob_market")),
                "hash": _to_str(row.get("hash")),
                "spread": _fmt_float(spread),
                "midpoint": _fmt_float(midpoint),
                "best_bid_size": _fmt_float(best_bid_size),
                "best_ask_size": _fmt_float(best_ask_size),
                "top_of_book_imbalance": _fmt_float(top_of_book_imbalance),
                "microprice_proxy": _fmt_float(microprice_proxy),
                "last_trade_minus_mid": _fmt_float(last_trade_minus_mid),
                "bid_levels_count": "" if bid_levels_count is None else str(bid_levels_count),
                "ask_levels_count": "" if ask_levels_count is None else str(ask_levels_count),
                "staleness_flag": str(staleness_flag),
            }
            writer.writerow(out_row)
            row_count_out += 1

    sanity_checks = {
        "row_count_in": row_count_in,
        "row_count_out": row_count_out,
        "missing_token_id_count": missing_token_id_count,
        "missing_bid_ask_count": missing_bid_ask_count,
        "negative_spread_count": negative_spread_count,
        "zero_depth_rows_count": zero_depth_rows_count,
        "null_imbalance_count": null_imbalance_count,
        "null_microprice_count": null_microprice_count,
        "null_last_trade_minus_mid_count": null_last_trade_minus_mid_count,
    }

    manifest = {
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "source_run_id": source_run_id,
        "latest_books_state_manifest": str(latest_state_manifest),
        "books_state_csv": str(state_csv),
        "output_csv": str(output_csv),
        "manifest_json": str(output_manifest),
        "row_count": row_count_out,
        "sanity_checks": sanity_checks,
    }

    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[build-books-features] sanity_checks={json.dumps(sanity_checks, ensure_ascii=False, sort_keys=True)}")

    return manifest
