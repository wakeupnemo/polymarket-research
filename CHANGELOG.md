# Changelog

## 2026-03-13

### Changed
- Added a first concise maker-markout interpretation decision memo at `reports/manual_checks/MAKER_MARKOUT_DECISION_MEMO_2026-03-13.md`.
- Recorded explicit policy to keep both tracked latest-manifest pointers because they still resolve to intentionally present tracked artifacts:
  - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`
  - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
- Updated project state/context docs to reflect:
  - completed repo/runtime hygiene,
  - default-threshold versus calibrated-threshold separation,
  - scaffold-only interpretation limits for first maker-markout outputs,
  - and calibrated thresholds remaining experimental local override.

### Decision Notes
- First maker-markout output is accepted as scaffold-level triage signal only.
- Result is not sufficient evidence for execution PnL claims or strategy promotion.
- Missing `h5` coverage for two markets remains an explicit interpretation limit.

## 2026-03-12

### Implemented
- Confirmed that the stable feature pipeline now reaches:
  - metadata refresh,
  - raw books collection,
  - books state build,
  - feature-input freeze,
  - stable feature set `v0_1`,
  - feature diagnostics.
- Confirmed that the dedicated diagnostics layer is already present in the repo via:
  - `src/pmre/reporting/build_feature_diagnostics.py`
  - CLI wiring in `src/pmre/cli.py`
  - `scripts/run_build_feature_diagnostics.sh`
  - `tests/test_build_feature_diagnostics.py`
- Successfully ran the diagnostics job on the current latest stable feature-set manifest.
- Produced diagnostics artifacts:
  - diagnostics JSON summary,
  - market-summary CSV,
  - latest diagnostics manifest.
- Validated the diagnostics layer with:
  - focused diagnostics test,
  - focused feature + diagnostics test slice,
  - broader feature / smoke test slice.

### Changed
- Project reality is now “stable feature pipeline plus diagnostics reporting layer”, not just “data backbone plus planned next layers”.
- The roadmap focus moved from building first features / first diagnostics to:
  - diagnostics interpretation,
  - market gating decisions,
  - tradability / universe narrowing,
  - first conservative maker-markout scaffold.
- Current live diagnostics result for the latest feature artifact:
  - `total_row_count = 60`
  - `stale_row_count = 26`
  - `stale_row_fraction = 0.43333333333333335`
  - `missing_spread_count = 0`
  - `non_positive_spread_count = 0`
  - `wide_spread_count = 0`
  - `zero_or_empty_top_size_count = 0`
  - `null_imbalance_count = 0`
  - `null_microprice_count = 0`
  - `repeated_hash_row_count = 26`

### Invalidated
- “Implement the diagnostics layer next” is no longer current.
- “Build the first feature layer next” is no longer current.
- Additional ingestion scaffolding, additional feature-builder scaffolding, or a new smoke experiment are not the right next step for this phase.
- The Debian server did not require a fresh diagnostics code patch once local repo reality was checked; GitHub `main` already contained the implementation.

### Priority Impact
- Highest-priority work is now:
  1. repo hygiene and intentional artifact/versioning decisions,
  2. diagnostics interpretation and first gating rules,
  3. tradability / research-universe narrowing,
  4. first maker-markout scaffold.
- Event enrichment, websocket ingestion, stale-anchor tests, and crypto fair-value alignment remain valid but are not the immediate implementation priority.
