from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import csv
import json

from pmre.config import ensure_dirs, load_config, project_root


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


def _fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _resolve_path(root: Path, path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _best_level(levels: list[dict[str, Any]] | None, side: str) -> tuple[float | None, str]:
    if not levels:
        return None, ""

    best_price: float | None = None
    best_size = ""

    for level in levels:
        price = _parse_float(level.get("price"))
        size = _to_str(level.get("size"))
        if price is None:
            continue

        if best_price is None:
            best_price = price
            best_size = size
            continue

        if side == "bid" and price > best_price:
            best_price = price
            best_size = size
        elif side == "ask" and price < best_price:
            best_price = price
            best_size = size

    return best_price, best_size


def build_books_state(
    config_path: str | Path,
    input_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    root = project_root(cfg)
    state_cfg = cfg.get("state_builder", {})

    if input_manifest_path is None:
        input_manifest = _resolve_path(root, state_cfg["books_input_manifest"])
    else:
        input_manifest = _resolve_path(root, input_manifest_path)

    if not input_manifest.exists():
        raise FileNotFoundError(f"Missing input manifest: {input_manifest}")

    raw_manifest = json.loads(input_manifest.read_text(encoding="utf-8"))
    input_jsonl = Path(raw_manifest["output_jsonl"]).resolve()
    if not input_jsonl.exists():
        raise FileNotFoundError(f"Missing raw JSONL: {input_jsonl}")

    output_dir = _resolve_path(root, state_cfg.get("books_output_dir", "data/state/polymarket"))
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = raw_manifest.get("run_id") or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_csv = output_dir / f"books_state_{run_id}.csv"
    manifest_json = output_dir / f"books_state_{run_id}_manifest.json"
    latest_manifest_json = output_dir / "latest_books_state_manifest.json"

    fieldnames = [
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
        "best_bid_price",
        "best_bid_size",
        "best_ask_price",
        "best_ask_size",
        "mid_price",
        "spread",
        "bid_levels_count",
        "ask_levels_count",
        "last_trade_price",
        "hash",
        "source_jsonl",
    ]

    row_count = 0

    with input_jsonl.open("r", encoding="utf-8") as in_fh, output_csv.open("w", newline="", encoding="utf-8") as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()

        for line in in_fh:
            envelope = json.loads(line)
            requested_tokens = envelope.get("requested_tokens") or []
            token_meta = {str(item.get("token_id", "")): item for item in requested_tokens}

            collector_ts = _to_str(envelope.get("collector_ts"))
            iteration = _to_str(envelope.get("iteration"))
            batch_index = _to_str(envelope.get("batch_index"))

            for book in envelope.get("books") or []:
                token_id = _to_str(book.get("asset_id") or book.get("token_id"))
                meta = token_meta.get(token_id, {})

                bids = book.get("bids") or []
                asks = book.get("asks") or []

                best_bid_price, best_bid_size = _best_level(bids, "bid")
                best_ask_price, best_ask_size = _best_level(asks, "ask")

                mid_price = None
                spread = None
                if best_bid_price is not None and best_ask_price is not None:
                    mid_price = (best_bid_price + best_ask_price) / 2.0
                    spread = best_ask_price - best_bid_price

                row = {
                    "source_run_id": _to_str(run_id),
                    "collector_ts": collector_ts,
                    "book_timestamp": _to_str(book.get("timestamp")),
                    "iteration": iteration,
                    "batch_index": batch_index,
                    "market_id": _to_str(meta.get("market_id")),
                    "event_id": _to_str(meta.get("event_id")),
                    "outcome": _to_str(meta.get("outcome")),
                    "token_index": _to_str(meta.get("token_index")),
                    "token_id": token_id,
                    "clob_market": _to_str(book.get("market")),
                    "best_bid_price": _fmt_float(best_bid_price),
                    "best_bid_size": best_bid_size,
                    "best_ask_price": _fmt_float(best_ask_price),
                    "best_ask_size": best_ask_size,
                    "mid_price": _fmt_float(mid_price),
                    "spread": _fmt_float(spread),
                    "bid_levels_count": _to_str(len(bids)),
                    "ask_levels_count": _to_str(len(asks)),
                    "last_trade_price": _to_str(book.get("last_trade_price")),
                    "hash": _to_str(book.get("hash")),
                    "source_jsonl": str(input_jsonl),
                }
                writer.writerow(row)
                row_count += 1

    manifest = {
        "run_ts": datetime.now(UTC).isoformat(),
        "source_run_id": run_id,
        "input_manifest": str(input_manifest),
        "input_jsonl": str(input_jsonl),
        "output_csv": str(output_csv),
        "manifest_json": str(manifest_json),
        "row_count": row_count,
    }

    manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
