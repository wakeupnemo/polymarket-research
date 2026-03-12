from __future__ import annotations

from pathlib import Path
import yaml


def load_config(config_path: str | Path) -> dict:
    config_path = Path(config_path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    cfg["_config_path"] = str(config_path)
    cfg["_config_dir"] = str(config_path.parent)
    return cfg


def project_root(cfg: dict) -> Path:
    config_dir = Path(cfg["_config_dir"])
    return (config_dir / cfg.get("project_root", ".")).resolve()


def resolve_paths(cfg: dict) -> dict[str, Path]:
    root = project_root(cfg)
    path_map = cfg.get("paths", {})
    return {name: (root / rel).resolve() for name, rel in path_map.items()}


def ensure_dirs(cfg: dict) -> dict[str, Path]:
    paths = resolve_paths(cfg)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths
