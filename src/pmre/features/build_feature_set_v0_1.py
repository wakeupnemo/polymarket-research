from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import csv
import json

from pmre.config import ensure_dirs, load_config, project_root


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


def _compute_staleness_flag(
    collector_ts: str,
    book_timestamp: str,
    best_bid_price: float | None,
    best_ask_price: float | None,
    spread: float | None,
    current_hash: str,
    repeated_hash_count: int,
    consecutive_missing_last_trade_count: int,
    stale_threshold_ms: int,
    max_repeated_hash_count: int,
    max_missing_last_trade_count: int,
) -> int:
    if best_bid_price is None or best_ask_price is None:
        return 1

    if spread is None or spread <= 0:
        return 1

    collector_ms = _iso_to_epoch_ms(collector_ts)
    book_ms = _parse_int(book_timestamp)
    if collector_ms is None or book_ms is None:
        return 1

    age_ms = collector_ms - book_ms
    if age_ms < 0 or age_ms > stale_threshold_ms:
        return 1

    if current_hash and repeated_hash_count > max_repeated_hash_count:
        return 1

    if consecutive_missing_last_trade_count > max_missing_last_trade_count:
        return 1

    return 0


def _compute_market_quality_score(
    spread: float | None,
    best_bid_price: float | None,
    best_ask_price: float | None,
    best_bid_size: float | None,
    best_ask_size: float | None,
    bid_levels_count: int | None,
    ask_levels_count: int | None,
    staleness_flag: int,
    max_spread: float,
) -> float:
    score = 0.0

    if best_bid_price is not None and best_ask_price is not None:
        score += 1.0

    if spread is not None and 0 < spread <= max_spread:
        score += 1.0

    if (best_bid_size or 0.0) > 0 and (best_ask_size or 0.0) > 0:
        score += 1.0

    if (bid_levels_count or 0) <= 0 or (ask_levels_count or 0) <= 0:
        score -= 1.0

    if spread is None or spread <= 0:
        score -= 1.0

    if staleness_flag == 1:
        score -= 1.0

    return score


def _schema_definition(
    feature_set_version: str,
    stale_threshold_ms: int,
    max_spread: float,
    max_repeated_hash_count: int,
    max_missing_last_trade_count: int,
) -> dict[str, Any]:
    return {
        "feature_set_version": feature_set_version,
        "description": "Minimum stable feature schema for books-state derived research features.",
        "inputs_allowed_only": [
            "latest_books_state_manifest",
            "books_state_csv",
            "markets.csv",
            "tokens.csv",
        ],
        "features": {
            "spread": "best_ask_price - best_bid_price.",
            "midpoint": "mid_price if already present, otherwise recomputed.",
            "best_bid_size": "Top-of-book bid size as float.",
            "best_ask_size": "Top-of-book ask size as float.",
            "top_of_book_imbalance": "(best_bid_size - best_ask_size) / (best_bid_size + best_ask_size) when denominator > 0.",
            "microprice_proxy": "(best_ask_price * best_bid_size + best_bid_price * best_ask_size) / (best_bid_size + best_ask_size) when denominator > 0.",
            "last_trade_minus_mid": "last_trade_price - midpoint when both exist.",
            "bid_levels_count": "Bid level count as integer.",
            "ask_levels_count": "Ask level count as integer.",
            "staleness_flag": (
                "1 if bid/ask missing, spread <= 0, timestamp age exceeds threshold, "
                f"hash repeats too long (> {max_repeated_hash_count}), or last_trade_price missing too long "
                f"(> {max_missing_last_trade_count} consecutive snapshots)."
            ),
            "market_quality_score": (
                "Simple first-pass diagnostic score: add points for tight spread, both sides populated, "
                "and nonzero top sizes; subtract points for empty levels, pathological spread, and stale rows."
            ),
        },
        "non_goals": [
            "websocket-derived features",
            "event enrichment",
            "simulator assumptions",
            "queue position assumptions",
        ],
        "params": {
            "stale_threshold_ms": stale_threshold_ms,
            "quality_score_max_spread": max_spread,
            "max_repeated_hash_count": max_repeated_hash_count,
            "max_missing_last_trade_count": max_missing_last_trade_count,
        },
    }


def _extract_frozen_paths(freeze_payload: dict[str, Any]) -> tuple[Path, Path, Path]:
    if all(key in freeze_payload for key in ["books_state_csv", "markets_csv", "tokens_csv"]):
        return (
            Path(freeze_payload["books_state_csv"]).resolve(),
            Path(freeze_payload["markets_csv"]).resolve(),
            Path(freeze_payload["tokens_csv"]).resolve(),
        )

    frozen_files = freeze_payload.get("frozen_files") or {}
    try:
        books_state_csv = Path(frozen_files["books_state_csv"]["path"]).resolve()
        markets_csv = Path(frozen_files["markets_csv"]["path"]).resolve()
        tokens_csv = Path(frozen_files["tokens_csv"]["path"]).resolve()
    except KeyError as exc:
        raise KeyError(
            "Freeze manifest is missing required input paths. "
            "Expected either top-level books_state_csv/markets_csv/tokens_csv "
            "or frozen_files.<name>.path entries."
        ) from exc

    return books_state_csv, markets_csv, tokens_csv


def build_feature_set_v0_1(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    root = project_root(cfg)

    builder_cfg = cfg.get("feature_builder", {})
    latest_freeze_manifest = _resolve_path(root, builder_cfg["latest_freeze_manifest"])
    output_dir = _resolve_path(root, builder_cfg["output_dir"])
    feature_set_version = str(builder_cfg.get("feature_set_version", "v0_1"))
    stale_threshold_ms = int(builder_cfg.get("stale_threshold_ms", 15000))
    quality_score_max_spread = float(builder_cfg.get("quality_score_max_spread", 0.10))
    max_repeated_hash_count = int(builder_cfg.get("max_repeated_hash_count", 2))
    max_missing_last_trade_count = int(builder_cfg.get("max_missing_last_trade_count", 2))

    if not latest_freeze_manifest.exists():
        raise FileNotFoundError(f"Missing latest freeze manifest: {latest_freeze_manifest}")

    freeze_payload = json.loads(latest_freeze_manifest.read_text(encoding="utf-8"))
    freeze_id = str(freeze_payload["freeze_id"])
    source_run_id = str(freeze_payload["source_run_id"])

    books_state_csv, markets_csv, tokens_csv = _extract_frozen_paths(freeze_payload)

    for p in [books_state_csv, markets_csv, tokens_csv]:
        if not p.exists():
            raise FileNotFoundError(f"Missing frozen input file: {p}")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / f"feature_set_{feature_set_version}_{freeze_id}.csv"
    manifest_json = output_dir / f"feature_set_{feature_set_version}_{freeze_id}_manifest.json"
    schema_json = output_dir / f"feature_set_{feature_set_version}_schema.json"
    latest_manifest_json = output_dir / "latest_feature_set_manifest.json"

    schema_payload = _schema_definition(
        feature_set_version=feature_set_version,
        stale_threshold_ms=stale_threshold_ms,
        max_spread=quality_score_max_spread,
        max_repeated_hash_count=max_repeated_hash_count,
        max_missing_last_trade_count=max_missing_last_trade_count,
    )
    schema_json.write_text(json.dumps(schema_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "feature_set_version",
        "freeze_id",
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
        "market_quality_score",
    ]

    row_count = 0
    last_hash_by_token: dict[str, str] = {}
    repeated_hash_count_by_token: dict[str, int] = {}
    missing_last_trade_count_by_token: dict[str, int] = {}

    with books_state_csv.open("r", encoding="utf-8", newline="") as in_fh, output_csv.open("w", encoding="utf-8", newline="") as out_fh:
        reader = csv.DictReader(in_fh)
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            token_id = _to_str(row.get("token_id"))

            best_bid_price = _parse_float(row.get("best_bid_price"))
            best_ask_price = _parse_float(row.get("best_ask_price"))
            midpoint = _parse_float(row.get("mid_price"))
            spread = _parse_float(row.get("spread"))
            best_bid_size = _parse_float(row.get("best_bid_size"))
            best_ask_size = _parse_float(row.get("best_ask_size"))
            last_trade_price = _parse_float(row.get("last_trade_price"))
            bid_levels_count = _parse_int(row.get("bid_levels_count"))
            ask_levels_count = _parse_int(row.get("ask_levels_count"))
            current_hash = _to_str(row.get("hash"))

            if midpoint is None and best_bid_price is not None and best_ask_price is not None:
                midpoint = (best_bid_price + best_ask_price) / 2.0

            if spread is None and best_bid_price is not None and best_ask_price is not None:
                spread = best_ask_price - best_bid_price

            top_of_book_imbalance = _compute_top_of_book_imbalance(best_bid_size, best_ask_size)
            microprice_proxy = _compute_microprice_proxy(best_bid_price, best_ask_price, best_bid_size, best_ask_size)

            last_trade_minus_mid = None
            if last_trade_price is not None and midpoint is not None:
                last_trade_minus_mid = last_trade_price - midpoint

            prev_hash = last_hash_by_token.get(token_id, "")
            if current_hash and current_hash == prev_hash:
                repeated_hash_count_by_token[token_id] = repeated_hash_count_by_token.get(token_id, 0) + 1
            else:
                repeated_hash_count_by_token[token_id] = 0
            last_hash_by_token[token_id] = current_hash

            if last_trade_price is None:
                missing_last_trade_count_by_token[token_id] = missing_last_trade_count_by_token.get(token_id, 0) + 1
            else:
                missing_last_trade_count_by_token[token_id] = 0

            repeated_hash_count = repeated_hash_count_by_token.get(token_id, 0)
            consecutive_missing_last_trade_count = missing_last_trade_count_by_token.get(token_id, 0)

            staleness_flag = _compute_staleness_flag(
                collector_ts=_to_str(row.get("collector_ts")),
                book_timestamp=_to_str(row.get("book_timestamp")),
                best_bid_price=best_bid_price,
                best_ask_price=best_ask_price,
                spread=spread,
                current_hash=current_hash,
                repeated_hash_count=repeated_hash_count,
                consecutive_missing_last_trade_count=consecutive_missing_last_trade_count,
                stale_threshold_ms=stale_threshold_ms,
                max_repeated_hash_count=max_repeated_hash_count,
                max_missing_last_trade_count=max_missing_last_trade_count,
            )

            market_quality_score = _compute_market_quality_score(
                spread=spread,
                best_bid_price=best_bid_price,
                best_ask_price=best_ask_price,
                best_bid_size=best_bid_size,
                best_ask_size=best_ask_size,
                bid_levels_count=bid_levels_count,
                ask_levels_count=ask_levels_count,
                staleness_flag=staleness_flag,
                max_spread=quality_score_max_spread,
            )

            out_row = {
                "feature_set_version": feature_set_version,
                "freeze_id": freeze_id,
                "source_run_id": source_run_id,
                "collector_ts": _to_str(row.get("collector_ts")),
                "book_timestamp": _to_str(row.get("book_timestamp")),
                "iteration": _to_str(row.get("iteration")),
                "batch_index": _to_str(row.get("batch_index")),
                "market_id": _to_str(row.get("market_id")),
                "event_id": _to_str(row.get("event_id")),
                "outcome": _to_str(row.get("outcome")),
                "token_index": _to_str(row.get("token_index")),
                "token_id": token_id,
                "clob_market": _to_str(row.get("clob_market")),
                "hash": current_hash,
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
                "market_quality_score": _fmt_float(market_quality_score),
            }
            writer.writerow(out_row)
            row_count += 1

    manifest = {
        "run_ts": datetime.now(UTC).isoformat(),
        "feature_set_version": feature_set_version,
        "freeze_id": freeze_id,
        "source_run_id": source_run_id,
        "input_freeze_manifest": str(latest_freeze_manifest),
        "books_state_csv": str(books_state_csv),
        "markets_csv": str(markets_csv),
        "tokens_csv": str(tokens_csv),
        "output_csv": str(output_csv),
        "manifest_json": str(manifest_json),
        "schema_json": str(schema_json),
        "row_count": row_count,
    }

    manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
