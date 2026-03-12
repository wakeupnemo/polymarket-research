from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import csv
import hashlib
import json
import shutil

from pmre.config import ensure_dirs, load_config, project_root


def _resolve_path(root: Path, path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        row_count = -1
        for row_count, _ in enumerate(reader):
            pass
    return max(0, row_count)


def _file_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "basename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "row_count": _csv_row_count(path) if path.suffix.lower() == ".csv" else None,
    }


def freeze_feature_inputs(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    paths = ensure_dirs(cfg)
    root = project_root(cfg)
    freeze_cfg = cfg.get("feature_input_freeze", {})

    latest_state_manifest = _resolve_path(root, freeze_cfg["latest_state_manifest"])
    markets_csv = _resolve_path(root, freeze_cfg["markets_csv"])
    tokens_csv = _resolve_path(root, freeze_cfg["tokens_csv"])
    freeze_root = _resolve_path(root, freeze_cfg["output_dir"])

    if not latest_state_manifest.exists():
        raise FileNotFoundError(f"Missing latest books state manifest: {latest_state_manifest}")
    if not markets_csv.exists():
        raise FileNotFoundError(f"Missing markets.csv: {markets_csv}")
    if not tokens_csv.exists():
        raise FileNotFoundError(f"Missing tokens.csv: {tokens_csv}")

    state_manifest_payload = json.loads(latest_state_manifest.read_text(encoding="utf-8"))
    books_state_csv = Path(state_manifest_payload["output_csv"]).resolve()

    if not books_state_csv.exists():
        raise FileNotFoundError(f"Missing books state CSV from manifest: {books_state_csv}")

    source_run_id = str(state_manifest_payload.get("source_run_id") or books_state_csv.stem)
    freeze_ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    freeze_id = f"{source_run_id}__{freeze_ts}"

    freeze_dir = freeze_root / f"freeze_{freeze_id}"
    freeze_dir.mkdir(parents=True, exist_ok=False)

    copied_latest_state_manifest = freeze_dir / latest_state_manifest.name
    copied_books_state_csv = freeze_dir / books_state_csv.name
    copied_markets_csv = freeze_dir / markets_csv.name
    copied_tokens_csv = freeze_dir / tokens_csv.name

    shutil.copy2(latest_state_manifest, copied_latest_state_manifest)
    shutil.copy2(books_state_csv, copied_books_state_csv)
    shutil.copy2(markets_csv, copied_markets_csv)
    shutil.copy2(tokens_csv, copied_tokens_csv)

    manifest = {
        "freeze_id": freeze_id,
        "freeze_ts": datetime.now(UTC).isoformat(),
        "source_run_id": source_run_id,
        "policy": {
            "description": "Feature job input freeze",
            "allowed_inputs_only": [
                "latest_books_state_manifest",
                "books_state_csv",
                "markets_csv",
                "tokens_csv",
            ],
            "forbidden_for_now": [
                "websocket inputs",
                "event enrichment",
                "simulator assumptions",
            ],
        },
        "source_files": {
            "latest_books_state_manifest": _file_info(latest_state_manifest),
            "books_state_csv": _file_info(books_state_csv),
            "markets_csv": _file_info(markets_csv),
            "tokens_csv": _file_info(tokens_csv),
        },
        "frozen_files": {
            "latest_books_state_manifest": _file_info(copied_latest_state_manifest),
            "books_state_csv": _file_info(copied_books_state_csv),
            "markets_csv": _file_info(copied_markets_csv),
            "tokens_csv": _file_info(copied_tokens_csv),
        },
        "freeze_dir": str(freeze_dir),
    }

    manifest_path = freeze_dir / "feature_input_freeze_manifest.json"
    latest_manifest_path = freeze_root / "latest_feature_input_freeze_manifest.json"

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "freeze_id": freeze_id,
        "source_run_id": source_run_id,
        "freeze_dir": str(freeze_dir),
        "manifest_json": str(manifest_path),
        "latest_manifest_json": str(latest_manifest_path),
        "books_state_csv": str(copied_books_state_csv),
        "markets_csv": str(copied_markets_csv),
        "tokens_csv": str(copied_tokens_csv),
    }
