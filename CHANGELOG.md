# Changelog

## 2026-03-15

### Implemented
- Ran a server-side reproducibility / runtime-truth inspection on the Debian checkout instead of starting a new implementation branch.
- Inspected live repo state on `main` at `8980f88`.
- Verified that the working-tree versions of:
  - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`
  - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
  had been pointing to missing newer artifacts.
- Restored those two latest-pointer files back to coherent tracked artifacts.
- Verified that the restored tracked latest basis now resolves successfully to:
  - freeze id `20260311T214230Z__20260312T133004Z`
  - books-state row count = `60`
  - feature-set row count = `60`
- Verified that the preserved runtime snapshot under `~/pmre_runtime_snapshots/20260313T102233Z/` contains:
  - local calibration config,
  - 120-row feature-set artifacts,
  - diagnostics latest-manifest truth,
  - calibrated tradability outputs,
  - calibrated active-universe CSV,
  - maker-markout outputs.
- Verified that the preserved runtime note matches the documented memo-basis facts:
  - calibrated keep IDs `540818`, `540819`, `540844`, `540881`
  - `selected_rows = 44`
  - `market_summary_rows = 4`
  - row-step horizons `[1, 2, 5]`

### Changed
- Project reality now distinguishes explicitly between:
  - preserved longer-sample runtime truth outside the repo tree,
  - and current tracked-latest checkout truth inside `data/features/polymarket/...`.
- The current tracked latest checkout is coherent again for freeze / feature-set pointers, but it is not the memo-basis 120-row state; it is the older coherent 60-row state.
- The current tracked latest checkout is presently blocked from rerunning tradability because:
  - `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`
  is missing.
- Current maker-markout reruns from tracked latest are blocked downstream because tradability cannot currently produce fresh outputs.

### Invalidated
- The assumption that the current tracked latest checkout still corresponds to the memo-basis 120-row sample.
- The assumption that pointer-file existence alone is enough to trust latest runtime truth.
- The assumption that current-tracked tradability drift has already been observed; the current blocker is missing diagnostics prerequisite, not a confirmed count mismatch.
- The assumption that current-tracked maker-markout reproducibility can be checked before tradability becomes runnable again.

### Priority Impact
- Highest-priority work is now:
  1. restore or regenerate diagnostics latest-manifest truth on the current tracked latest checkout,
  2. rerun current-tracked tradability under default and calibrated settings,
  3. rerun current-tracked maker-markout only if calibrated tradability becomes runnable,
  4. keep preserved 120-row runtime truth separate from current-tracked 60-row checkout truth.
- Websocket ingestion, event enrichment, stale-anchor work, crypto fair-value alignment, and broader simulator expansion remain valid later directions but are not the immediate priority.

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
- Ran a longer bounded raw-books collection by increasing `raw_books.iterations` from `3` to `6` without widening the token subset.
- Rebuilt downstream artifacts successfully on the longer bounded sample:
  - books-state row count = `120`
  - stable feature-set row count = `120`
- Validated the first-pass tradability / active-universe layer on real local artifacts.
- Confirmed default-threshold tradability behavior on the longer bounded sample:
  - total markets = `10`
  - `keep = 0`
  - `watch = 4`
  - `exclude = 6`
- Identified the near-miss watch regime as driven by:
  - `row_count_watch`
  - `repeated_hash_watch`
- Confirmed that tradability threshold overrides are read from `tradability_report.thresholds`.
- Validated a conservative local calibration override:
  - `min_row_count_keep = 12`
  - `max_repeated_hash_fraction_keep = 0.5`
- Confirmed calibrated tradability behavior on real local artifacts:
  - total markets = `10`
  - `keep = 4`
  - `watch = 0`
  - `exclude = 6`
  - active universe size = `4`
- Confirmed the calibrated keep set:
  - `540818`
  - `540819`
  - `540844`
  - `540881`
- Synced the local Debian checkout to `origin/main` and confirmed that the maker-markout scaffold already existed upstream.
- Validated local presence of:
  - `src/pmre/experiments/build_maker_markout_report.py`
  - CLI wiring `build-maker-markout`
  - `scripts/run_build_maker_markout.sh`
  - `tests/test_build_maker_markout.py`
- Ran the first conservative maker-markout scaffold successfully on the calibrated active universe.
- Produced maker-markout artifacts:
  - latest maker-markout manifest,
  - report JSON,
  - per-row CSV,
  - per-market summary CSV.
- Confirmed current maker-markout scaffold selection and summary facts:
  - `selected_rows = 44`
  - `drop_not_in_active_universe = 72`
  - `drop_stale = 4`
  - `market_summary_rows = 4`
  - row-step horizons `[1, 2, 5]`

### Changed
- Project reality moved from “diagnostics plus planned gating / maker-markout” to:
  - bounded-sample validation completed,
  - first-pass tradability completed,
  - calibrated non-empty active universe validated,
  - first maker-markout scaffold run completed.
- The hard blocker `row_count_too_low` no longer dominated after the longer bounded sample; the gating regime moved into a near-miss watch state before calibration.
- The local Debian checkout was shown to be behind `origin/main`; the lack of local maker-markout scaffold was a sync issue, not a missing-upstream implementation.
- Current maker-markout interpretation must be framed as a conservative scaffold result:
  - no queue modeling,
  - no fee modeling,
  - no fill-probability modeling,
  - quote prices approximated from midpoint ± spread / 2.

### Invalidated
- “The active universe is still empty” is no longer current under the validated calibrated local override.
- “Collect more data first” is no longer the default next move after the successful bounded sample and non-empty calibrated universe.
- “The maker-markout scaffold is not present in the repo / local runtime path” is no longer current after syncing to `origin/main`.
- The failed first calibration attempt did **not** invalidate calibration; it was caused by using the wrong config shape under `tradability_report` instead of `tradability_report.thresholds`.

### Priority Impact
- Highest-priority work is now:
  1. repo hygiene and artifact/config intent after sync, stash, calibration, and scaffold execution,
  2. explicit documentation of default-threshold versus calibrated-threshold tradability behavior,
  3. conservative interpretation of the first maker-markout scaffold outputs,
  4. first concise decision memo on what the current maker-markout scaffold does and does not establish.
- Additional bounded polling, websocket ingestion, stale-anchor tests, crypto fair-value alignment, and broader architecture changes remain valid later directions but are not the immediate priority.

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
