from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import csv
import json
import time

from pmre.config import ensure_dirs, load_config
from pmre.ingest.gamma_client import GammaClient


def _parse_jsonish_array(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return []
        try:
            decoded = json.loads(text)
            return decoded if isinstance(decoded, list) else [decoded]
        except json.JSONDecodeError:
            return [text]
    return [value]


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def _extract_market_row(run_ts: str, market: dict[str, Any]) -> dict[str, Any]:
    outcomes = _parse_jsonish_array(market.get("outcomes"))
    token_ids = _parse_jsonish_array(market.get("clobTokenIds"))
    prices = _parse_jsonish_array(market.get("outcomePrices"))

    return {
        "run_ts": run_ts,
        "market_id": _to_str(market.get("id") or market.get("marketId")),
        "event_id": _to_str(market.get("eventId")),
        "condition_id": _to_str(market.get("conditionId")),
        "question_id": _to_str(market.get("questionID") or market.get("questionId")),
        "slug": _to_str(market.get("slug")),
        "question": _to_str(market.get("question")),
        "category": _to_str(market.get("category")),
        "active": _to_str(market.get("active")),
        "closed": _to_str(market.get("closed")),
        "archived": _to_str(market.get("archived")),
        "accepting_orders": _to_str(market.get("acceptingOrders")),
        "enable_order_book": _to_str(market.get("enableOrderBook")),
        "minimum_order_size": _to_str(market.get("minimumOrderSize")),
        "minimum_tick_size": _to_str(market.get("minimumTickSize")),
        "liquidity": _to_str(market.get("liquidity")),
        "volume": _to_str(market.get("volume")),
        "start_date": _to_str(market.get("startDate")),
        "end_date": _to_str(market.get("endDate")),
        "description": _to_str(market.get("description")),
        "market_type": _to_str(market.get("marketType")),
        "format_type": _to_str(market.get("formatType")),
        "outcomes_json": json.dumps(outcomes, ensure_ascii=False),
        "outcome_prices_json": json.dumps(prices, ensure_ascii=False),
        "clob_token_ids_json": json.dumps(token_ids, ensure_ascii=False),
    }


def _extract_token_rows(run_ts: str, market: dict[str, Any]) -> list[dict[str, Any]]:
    market_id = _to_str(market.get("id") or market.get("marketId"))
    event_id = _to_str(market.get("eventId"))
    outcomes = _parse_jsonish_array(market.get("outcomes"))
    token_ids = _parse_jsonish_array(market.get("clobTokenIds"))
    prices = _parse_jsonish_array(market.get("outcomePrices"))

    n = max(len(outcomes), len(token_ids), len(prices))
    rows: list[dict[str, Any]] = []

    for i in range(n):
        rows.append(
            {
                "run_ts": run_ts,
                "market_id": market_id,
                "event_id": event_id,
                "token_index": i,
                "outcome": _to_str(outcomes[i] if i < len(outcomes) else ""),
                "token_id": _to_str(token_ids[i] if i < len(token_ids) else ""),
                "outcome_price": _to_str(prices[i] if i < len(prices) else ""),
            }
        )

    return rows


def _load_existing_page_files(raw_pages_dir: Path) -> list[Path]:
    return sorted(raw_pages_dir.glob("markets_page_*.json"))


def _load_markets_from_page_files(page_files: list[Path]) -> list[dict[str, Any]]:
    all_markets: list[dict[str, Any]] = []
    for path in page_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        markets = payload.get("markets") or []
        all_markets.extend(markets)
    return all_markets


def _load_resume_offset(checkpoint_path: Path) -> int:
    if not checkpoint_path.exists():
        return 0
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    return int(payload.get("next_offset", 0))


def _write_checkpoint(checkpoint_path: Path, payload: dict[str, Any]) -> None:
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_metadata_refresh(config_path: str | Path, client: GammaClient | None = None) -> dict[str, Any]:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    meta_cfg = cfg.get("metadata", {})

    if client is None:
        client = GammaClient(
            base_url=str(meta_cfg["gamma_base_url"]),
            timeout_seconds=int(meta_cfg.get("timeout_seconds", 60)),
            max_retries=int(meta_cfg.get("max_retries", 5)),
        )

    raw_root = paths["raw"] / "polymarket" / "metadata"
    raw_pages_dir = raw_root / "markets_pages"
    ref_root = paths["reference"] / "polymarket"
    checkpoint_path = raw_root / "metadata_refresh_checkpoint.json"
    manifest_json = raw_root / "metadata_refresh_manifest.json"

    raw_pages_dir.mkdir(parents=True, exist_ok=True)
    ref_root.mkdir(parents=True, exist_ok=True)

    run_ts = datetime.now(UTC).isoformat()
    page_limit = int(meta_cfg.get("page_limit", 25))
    pause_seconds = float(meta_cfg.get("pause_seconds", 0.50))
    active = bool(meta_cfg.get("active", True))
    closed = bool(meta_cfg.get("closed", False))
    resume = bool(meta_cfg.get("resume", True))

    page_files_before = _load_existing_page_files(raw_pages_dir)
    offset = _load_resume_offset(checkpoint_path) if resume else 0
    page_index = len(page_files_before) if resume else 0

    while True:
        markets = client.list_markets(
            active=active,
            closed=closed,
            limit=page_limit,
            offset=offset,
        )

        page_payload = {
            "run_ts": run_ts,
            "page_index": page_index,
            "offset": offset,
            "limit": page_limit,
            "active": active,
            "closed": closed,
            "count": len(markets),
            "markets": markets,
        }

        page_path = raw_pages_dir / f"markets_page_{page_index:05d}_offset_{offset:08d}.json"
        page_path.write_text(json.dumps(page_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        _write_checkpoint(
            checkpoint_path,
            {
                "run_ts": run_ts,
                "next_offset": offset + len(markets),
                "last_page_index": page_index,
                "last_page_file": str(page_path),
                "last_page_count": len(markets),
                "page_limit": page_limit,
                "active": active,
                "closed": closed,
            },
        )

        if not markets:
            break

        if len(markets) < page_limit:
            break

        offset += len(markets)
        page_index += 1

        if pause_seconds > 0:
            time.sleep(pause_seconds)

    page_files = _load_existing_page_files(raw_pages_dir)
    all_markets = _load_markets_from_page_files(page_files)

    market_rows: list[dict[str, Any]] = []
    token_rows: list[dict[str, Any]] = []

    seen_market_ids: set[str] = set()
    for market in all_markets:
        market_id = _to_str(market.get("id") or market.get("marketId"))
        if not market_id or market_id in seen_market_ids:
            continue
        seen_market_ids.add(market_id)

        market_rows.append(_extract_market_row(run_ts, market))
        token_rows.extend(_extract_token_rows(run_ts, market))

    markets_csv = ref_root / "markets.csv"
    tokens_csv = ref_root / "tokens.csv"

    _write_csv(
        markets_csv,
        market_rows,
        [
            "run_ts",
            "market_id",
            "event_id",
            "condition_id",
            "question_id",
            "slug",
            "question",
            "category",
            "active",
            "closed",
            "archived",
            "accepting_orders",
            "enable_order_book",
            "minimum_order_size",
            "minimum_tick_size",
            "liquidity",
            "volume",
            "start_date",
            "end_date",
            "description",
            "market_type",
            "format_type",
            "outcomes_json",
            "outcome_prices_json",
            "clob_token_ids_json",
        ],
    )

    _write_csv(
        tokens_csv,
        token_rows,
        [
            "run_ts",
            "market_id",
            "event_id",
            "token_index",
            "outcome",
            "token_id",
            "outcome_price",
        ],
    )

    manifest = {
        "run_ts": run_ts,
        "resume": resume,
        "active": active,
        "closed": closed,
        "page_limit": page_limit,
        "market_count": len(market_rows),
        "token_count": len(token_rows),
        "page_file_count": len(page_files),
        "markets_csv": str(markets_csv),
        "tokens_csv": str(tokens_csv),
        "checkpoint_path": str(checkpoint_path),
        "manifest_path": str(manifest_json),
    }
    manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
