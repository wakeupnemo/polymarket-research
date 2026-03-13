# Developing Context

## Current Development Focus
- Current focus is a repo-side interpretation / policy pass, not a new implementation sprint.
- Current focus is:
  - preserving validated runtime truth in tracked docs,
  - recording the first maker-markout scaffold interpretation conservatively,
  - and closing latest-manifest pointer policy deliberately.
- Treat the current maker-markout output as scaffold-level triage under explicit simplifying assumptions, not execution PnL.

## Decisions Captured In This Pass
- Longer bounded sample validation remains the current runtime basis:
  - books-state row count = `120`,
  - stable feature-set row count = `120`.
- Default tradability thresholds on that sample produced:
  - total markets = `10`,
  - `keep = 0`,
  - `watch = 4`,
  - `exclude = 6`.
- Experimental local calibration override (`min_row_count_keep = 12`, `max_repeated_hash_fraction_keep = 0.5`) produced:
  - total markets = `10`,
  - `keep = 4`,
  - `watch = 0`,
  - `exclude = 6`.
- Calibrated keep set:
  - `540818`,
  - `540819`,
  - `540844`,
  - `540881`.
- First conservative maker-markout scaffold run on calibrated active universe produced:
  - `selected_rows = 44`,
  - `market_summary_rows = 4`,
  - row-step horizons `[1, 2, 5]`.
- Repo/runtime hygiene remains complete:
  - calibrated runtime artifacts + local calibration config preserved outside repo tree,
  - local-only configs removed from tracked `configs/`,
  - generated runtime artifacts and cache junk removed from checkout.
- Latest-manifest pointer policy was resolved:
  - keep `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`,
  - keep `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`,
  - because both still point to intentionally present tracked artifacts under `data/features/polymarket/...`.

## Current Runtime Reality
- Default-threshold tradability remains empty-keep (`keep = 0`, `watch = 4`, `exclude = 6`).
- Non-empty active universe currently depends on experimental local calibration, not default tracked config.
- Current maker-markout scaffold assumptions remain:
  - no queue modeling,
  - no fee modeling,
  - no fill-probability modeling,
  - quote prices approximated from midpoint ± spread / 2.
- Current market summaries are useful for triage only; missing `h5` for two markets limits interpretation.

## Implementation Constraints / Assumptions
- Smallest meaningful next step only.
- Do not duplicate already implemented ingestion, feature, diagnostics, tradability, or maker-markout scaffolding.
- Keep maker and taker logic separate.
- Keep descriptive/reporting interpretation separate from the stable feature schema.
- Keep calibrated thresholds labeled experimental unless deliberately promoted later.

## Immediate Next Step
1. Run a small bounded server-side verification pass that reproduces the documented default-vs-calibrated split and confirms the same calibrated keep IDs before any further interpretation updates.
