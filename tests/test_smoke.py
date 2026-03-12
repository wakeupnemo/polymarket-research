from pathlib import Path

from pmre.experiments.maker_markout_smoke import run_smoke


def test_run_smoke(tmp_path: Path) -> None:
    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        """project_root: .
paths:
  raw: data/raw
  normalized: data/normalized
  state: data/state
  features: data/features
  reference: data/reference
  reports: reports
  logs: logs
smoke:
  snapshot_count: 5
  seed: 123
""",
        encoding="utf-8",
    )

    result = run_smoke(cfg)

    assert Path(result["raw_file"]).exists()
    assert Path(result["metadata_file"]).exists()
    assert Path(result["feature_file"]).exists()

    report_path = Path(result["report_file"])
    assert report_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    assert "# Smoke Report" in report_text
