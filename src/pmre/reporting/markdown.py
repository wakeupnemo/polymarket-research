from __future__ import annotations

from pathlib import Path


def write_smoke_report(path: str | Path, summary: dict, outputs: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Smoke Report",
        "",
        "Minimal week-1 pipeline validation output.",
        "",
        "## Summary",
        f"- snapshots: {summary['snapshot_count']}",
        f"- mean spread: {summary['mean_spread']}",
        f"- median spread: {summary['median_spread']}",
        f"- mean total depth: {summary['mean_total_depth']}",
        "",
        "## Output files",
        f"- raw snapshots: {outputs['raw_file']}",
        f"- metadata: {outputs['metadata_file']}",
        f"- features: {outputs['feature_file']}",
        f"- report: {outputs['report_file']}",
        "",
        "## Notes",
        "- This is a smoke pipeline, not a live collector.",
        "- Raw, features, and reporting paths are separated.",
        "- Next step: replace mock ingestion with a Polymarket collector.",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
