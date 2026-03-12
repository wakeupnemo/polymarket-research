# Smoke Report

Minimal week-1 pipeline validation output.

## Summary
- snapshots: 12
- mean spread: 0.017083
- median spread: 0.0165
- mean total depth: 473.25

## Output files
- raw snapshots: /home/lev/polymarket-research/data/raw/polymarket/smoke_book_snapshots.jsonl
- metadata: /home/lev/polymarket-research/data/reference/demo_market_metadata.json
- features: /home/lev/polymarket-research/data/features/smoke_basic_microstructure.csv
- report: /home/lev/polymarket-research/reports/smoke_report.md

## Notes
- This is a smoke pipeline, not a live collector.
- Raw, features, and reporting paths are separated.
- Next step: replace mock ingestion with a Polymarket collector.
