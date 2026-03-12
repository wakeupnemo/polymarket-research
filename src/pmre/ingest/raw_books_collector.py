from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import csv
import json
import time

from pmre.config import ensure_dirs, load_config
from pmre.ingest.clob_client import ClobClient


def _utc_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _chunked(items: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _load_selected_tokens(tokens_csv: Path, token_limit: int) -> list[dict[str, str]]:
    if not tokens_csv.exists():
        raise FileNotFoundError(f"Missing token table: {tokens_csv}")

    selected: list[dict[str, str]] = []
    seen: set[str] = set()

    with tokens_csv.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            token_id = (row.get("token_id") or "").strip()
            if not token_id or token_id in seen:
                continue
            seen.add(token_id)

            selected.append(
                {
                    "token_id": token_id,
                    "market_id": (row.get("market_id") or "").strip(),
                    "event_id": (row.get("event_id") or "").strip(),
                    "outcome": (row.get("outcome") or "").strip(),
                    "token_index": (row.get("token_index") or "").strip(),
                }
            )

            if len(selected) >= token_limit:
                break

    if not selected:
        raise ValueError("No token IDs found in tokens.csv")

    return selected


def run_raw_books_collection(config_path: str | Path, client: ClobClient | None = None) -> dict[str, Any]:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    raw_cfg = cfg.get("raw_books", {})

    if client is None:
        client = ClobClient(
            base_url=str(raw_cfg["clob_base_url"]),
            timeout_seconds=int(raw_cfg.get("timeout_seconds", 30)),
            max_retries=int(raw_cfg.get("max_retries", 5)),
        )

    token_limit = int(raw_cfg.get("token_limit", 20))
    batch_size = int(raw_cfg.get("batch_size", 10))
    iterations = int(raw_cfg.get("iterations", 3))
    poll_interval_seconds = float(raw_cfg.get("poll_interval_seconds", 5))

    tokens_csv = paths["reference"] / "polymarket" / "tokens.csv"
    raw_root = paths["raw"] / "polymarket" / "books"
    raw_root.mkdir(parents=True, exist_ok=True)

    selected_tokens = _load_selected_tokens(tokens_csv, token_limit=token_limit)
    token_batches = _chunked(selected_tokens, batch_size)

    run_id = _utc_run_id()
    output_jsonl = raw_root / f"books_run_{run_id}.jsonl"
    manifest_json = raw_root / f"books_run_{run_id}_manifest.json"
    latest_manifest_json = raw_root / "latest_books_manifest.json"

    line_count = 0

    with output_jsonl.open("a", encoding="utf-8") as out_fh:
        for iteration in range(iterations):
            collector_ts = datetime.now(UTC).isoformat()

            for batch_index, batch in enumerate(token_batches):
                token_ids = [row["token_id"] for row in batch]
                books = client.get_books(token_ids)

                envelope = {
                    "collector_ts": collector_ts,
                    "iteration": iteration,
                    "batch_index": batch_index,
                    "requested_token_ids": token_ids,
                    "requested_tokens": batch,
                    "book_count": len(books),
                    "books": books,
                }
                out_fh.write(json.dumps(envelope, ensure_ascii=False) + "\n")
                out_fh.flush()
                line_count += 1

            if iteration + 1 < iterations and poll_interval_seconds > 0:
                time.sleep(poll_interval_seconds)

    manifest = {
        "run_id": run_id,
        "run_ts": datetime.now(UTC).isoformat(),
        "token_limit": token_limit,
        "selected_token_count": len(selected_tokens),
        "batch_size": batch_size,
        "batch_count_per_iteration": len(token_batches),
        "iterations": iterations,
        "jsonl_line_count": line_count,
        "output_jsonl": str(output_jsonl),
        "manifest_json": str(manifest_json),
        "tokens_csv": str(tokens_csv),
        "selected_tokens_preview": selected_tokens[:5],
    }

    manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
