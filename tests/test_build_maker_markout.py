from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.experiments.build_maker_markout_report import build_maker_markout_report


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_maker_markout_report(tmp_path: Path) -> None:
    universe_dir = tmp_path / "data" / "features" / "polymarket" / "universe"
    feature_set_dir = tmp_path / "data" / "features" / "polymarket" / "feature_sets"
    universe_dir.mkdir(parents=True, exist_ok=True)
    feature_set_dir.mkdir(parents=True, exist_ok=True)

    active_universe_csv = universe_dir / "active_universe_v0_1_demo.csv"
    _write_csv(
        active_universe_csv,
        ["market_id", "tradability_score", "gating_class", "gating_reason"],
        [{"market_id": "m1", "tradability_score": "50", "gating_class": "keep", "gating_reason": "ok"}],
    )

    latest_tradability_manifest = universe_dir / "latest_tradability_manifest.json"
    latest_tradability_manifest.write_text(
        json.dumps(
            {
                "feature_set_id": "v0_1_demo",
                "active_universe_csv": str(active_universe_csv),
            }
        ),
        encoding="utf-8",
    )

    feature_csv = feature_set_dir / "feature_set_v0_1_demo.csv"
    _write_csv(
        feature_csv,
        [
            "collector_ts",
            "market_id",
            "token_id",
            "spread",
            "midpoint",
            "best_bid_size",
            "best_ask_size",
            "staleness_flag",
            "market_quality_score",
        ],
        [
            {
                "collector_ts": "2026-01-01T00:00:00+00:00",
                "market_id": "m1",
                "token_id": "t1",
                "spread": "0.02",
                "midpoint": "0.50",
                "best_bid_size": "100",
                "best_ask_size": "100",
                "staleness_flag": "0",
                "market_quality_score": "2.0",
            },
            {
                "collector_ts": "2026-01-01T00:00:01+00:00",
                "market_id": "m1",
                "token_id": "t1",
                "spread": "0.02",
                "midpoint": "0.54",
                "best_bid_size": "100",
                "best_ask_size": "100",
                "staleness_flag": "0",
                "market_quality_score": "2.0",
            },
            {
                "collector_ts": "2026-01-01T00:00:02+00:00",
                "market_id": "m1",
                "token_id": "t1",
                "spread": "0.02",
                "midpoint": "0.52",
                "best_bid_size": "100",
                "best_ask_size": "100",
                "staleness_flag": "0",
                "market_quality_score": "2.0",
            },
            {
                "collector_ts": "2026-01-01T00:00:03+00:00",
                "market_id": "m2",
                "token_id": "t2",
                "spread": "0.02",
                "midpoint": "0.50",
                "best_bid_size": "100",
                "best_ask_size": "100",
                "staleness_flag": "0",
                "market_quality_score": "2.0",
            },
        ],
    )

    latest_feature_manifest = feature_set_dir / "latest_feature_set_manifest.json"
    latest_feature_manifest.write_text(
        json.dumps(
            {
                "feature_set_version": "v0_1",
                "freeze_id": "demo",
                "output_csv": str(feature_csv),
            }
        ),
        encoding="utf-8",
    )

    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        """project_root: .
maker_markout:
  latest_tradability_manifest: data/features/polymarket/universe/latest_tradability_manifest.json
  latest_feature_set_manifest: data/features/polymarket/feature_sets/latest_feature_set_manifest.json
  output_dir: data/experiments/polymarket/maker_markout
  row_step_horizons: [1, 2]
  min_market_quality_score: 1.0
""",
        encoding="utf-8",
    )

    result = build_maker_markout_report(cfg)

    rows_csv = Path(result["rows_csv"])
    summary_csv = Path(result["market_summary_csv"])
    latest_manifest = tmp_path / "data" / "experiments" / "polymarket" / "maker_markout" / "latest_maker_markout_manifest.json"

    assert rows_csv.exists()
    assert summary_csv.exists()
    assert latest_manifest.exists()

    with rows_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 3  # only active-universe market m1 survives selection
    first = rows[0]
    # buy quote = 0.49; future mid h1 = 0.54 => buy markout +0.05 (favorable)
    assert first["buy_markout_h1"] == "0.05"
    # sell quote = 0.51; future mid h1 = 0.54 => sell markout -0.03 (adverse)
    assert first["sell_markout_h1"] == "-0.03"

    with summary_csv.open("r", encoding="utf-8") as fh:
        summary_rows = list(csv.DictReader(fh))

    assert len(summary_rows) == 1
    assert summary_rows[0]["market_id"] == "m1"
    assert summary_rows[0]["row_count"] == "3"
    assert summary_rows[0]["adverse_sell_markout_fraction"] == "0.5"
