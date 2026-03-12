from __future__ import annotations

from pathlib import Path
import csv
import json

from pmre.reporting.build_tradability_report import build_tradability_report


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_tradability_report(tmp_path: Path) -> None:
    diagnostics_dir = tmp_path / "data" / "features" / "polymarket" / "diagnostics"
    feature_set_dir = tmp_path / "data" / "features" / "polymarket" / "feature_sets"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    feature_set_dir.mkdir(parents=True, exist_ok=True)

    feature_csv = feature_set_dir / "feature_set_v0_1_test_freeze.csv"
    _write_csv(feature_csv, ["market_id", "token_id", "spread"], [{"market_id": "m1", "token_id": "t1", "spread": "0.01"}])

    latest_feature_manifest = feature_set_dir / "latest_feature_set_manifest.json"
    latest_feature_manifest.write_text(
        json.dumps(
            {
                "feature_set_version": "v0_1",
                "freeze_id": "test_freeze",
                "output_csv": str(feature_csv),
            }
        ),
        encoding="utf-8",
    )

    diagnostics_market_summary_csv = diagnostics_dir / "feature_diagnostics_v0_1_test_freeze_market_summary.csv"
    _write_csv(
        diagnostics_market_summary_csv,
        [
            "market_id",
            "row_count",
            "stale_row_fraction",
            "median_spread",
            "p90_spread",
            "median_best_bid_size",
            "median_best_ask_size",
            "zero_or_empty_top_size_fraction",
            "repeated_hash_fraction",
            "mean_market_quality_score",
            "median_market_quality_score",
        ],
        [
            {
                "market_id": "m_keep",
                "row_count": "60",
                "stale_row_fraction": "0.10",
                "median_spread": "0.02",
                "p90_spread": "0.05",
                "median_best_bid_size": "100",
                "median_best_ask_size": "110",
                "zero_or_empty_top_size_fraction": "0.05",
                "repeated_hash_fraction": "0.10",
                "mean_market_quality_score": "2.5",
                "median_market_quality_score": "2.7",
            },
            {
                "market_id": "m_watch",
                "row_count": "30",
                "stale_row_fraction": "0.28",
                "median_spread": "0.05",
                "p90_spread": "0.12",
                "median_best_bid_size": "40",
                "median_best_ask_size": "39",
                "zero_or_empty_top_size_fraction": "0.22",
                "repeated_hash_fraction": "0.42",
                "mean_market_quality_score": "1.4",
                "median_market_quality_score": "1.4",
            },
            {
                "market_id": "m_exclude",
                "row_count": "4",
                "stale_row_fraction": "0.65",
                "median_spread": "0.12",
                "p90_spread": "0.22",
                "median_best_bid_size": "0",
                "median_best_ask_size": "4",
                "zero_or_empty_top_size_fraction": "0.90",
                "repeated_hash_fraction": "0.90",
                "mean_market_quality_score": "0.5",
                "median_market_quality_score": "0.5",
            },
        ],
    )

    diagnostics_json = diagnostics_dir / "feature_diagnostics_v0_1_test_freeze.json"
    diagnostics_json.write_text(
        json.dumps(
            {
                "feature_set_id": "v0_1_test_freeze",
                "diagnostics_json": str(diagnostics_json),
                "market_summary_csv": str(diagnostics_market_summary_csv),
                "aggregate_summary": {"total_row_count": 94},
            }
        ),
        encoding="utf-8",
    )

    latest_diagnostics_manifest = diagnostics_dir / "latest_feature_diagnostics_manifest.json"
    latest_diagnostics_manifest.write_text(
        json.dumps(
            {
                "feature_set_id": "v0_1_test_freeze",
                "diagnostics_json": str(diagnostics_json),
                "market_summary_csv": str(diagnostics_market_summary_csv),
            }
        ),
        encoding="utf-8",
    )

    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        """project_root: .
tradability_report:
  latest_diagnostics_manifest: data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json
  latest_feature_set_manifest: data/features/polymarket/feature_sets/latest_feature_set_manifest.json
  output_dir: data/features/polymarket/universe
""",
        encoding="utf-8",
    )

    result = build_tradability_report(cfg)

    latest_manifest = tmp_path / "data" / "features" / "polymarket" / "universe" / "latest_tradability_manifest.json"
    report_json = Path(result["tradability_report_json"])
    summary_csv = Path(result["market_summary_csv"])
    active_csv = Path(result["active_universe_csv"])

    assert latest_manifest.exists()
    assert report_json.exists()
    assert summary_csv.exists()
    assert active_csv.exists()

    with summary_csv.open("r", encoding="utf-8") as fh:
        summary_rows = {row["market_id"]: row for row in csv.DictReader(fh)}

    assert summary_rows["m_keep"]["gating_class"] == "keep"
    assert summary_rows["m_keep"]["gating_reason"] == "ok"
    assert summary_rows["m_watch"]["gating_class"] == "watch"
    assert "watch" in summary_rows["m_watch"]["gating_reason"]
    assert summary_rows["m_exclude"]["gating_class"] == "exclude"
    assert "row_count_too_low" in summary_rows["m_exclude"]["gating_reason"]

    with active_csv.open("r", encoding="utf-8") as fh:
        active_rows = list(csv.DictReader(fh))

    assert len(active_rows) == 1
    assert active_rows[0]["market_id"] == "m_keep"

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    assert payload["market_counts"] == {"total": 3, "keep": 1, "watch": 1, "exclude": 1}
