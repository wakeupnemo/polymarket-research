# Developing Context

## Current Development Focus
- Implement the first conservative maker-markout scaffold downstream of active-universe/tradability outputs.
- Keep scope as triage/reporting only (not a full execution simulator).

## Decisions Made In This Chat
- Added `build_maker_markout_report` experiment module consuming only stable downstream artifacts:
  - `latest_tradability_manifest.json` (+ referenced `active_universe_*.csv`)
  - `latest_feature_set_manifest.json` (+ referenced stable feature CSV)
- Added explicit candidate-row filtering for active-universe-only, valid IDs, positive spread, non-stale rows, and minimum market quality.
- Added row-step horizon markouts (`h1`, `h2`, `h5` by default) with explicit sign conventions for buy/sell passive quote diagnostics.
- Added market-level summary outputs and adverse-markout fractions.
- Added CLI command `build-maker-markout`, runner script, and focused test.
- Kept feature and diagnostics schemas unchanged.

## Current Coding Task
- Finalize and validate maker-markout scaffold outputs:
  - `maker_markout_<run_id>.json`
  - `maker_markout_<run_id>_rows.csv`
  - `maker_markout_<run_id>_market_summary.csv`
  - `latest_maker_markout_manifest.json`

## Implementation Constraints / Assumptions
- This scaffold is snapshot-based and does **not** claim execution PnL.
- No queue modeling, fee modeling, or fill-probability modeling in this step.
- Quote prices are approximated from `midpoint ± spread/2` because stable feature-set `v0_1` does not include best bid/ask prices directly.
- Row-step horizons are the primary forward view unless reliable elapsed-time alignment is added later.

## Immediate Next Steps
- Run `build-feature-diagnostics` and `build-tradability-report` if the latest tradability artifacts are missing.
- Run `build-maker-markout` and review market-level adverse-selection signals.
- Decide whether to deepen maker-first work for selected markets or stop if adverse risk dominates.
