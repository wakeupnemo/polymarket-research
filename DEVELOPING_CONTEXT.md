# Developing Context

## Current Development Focus
- Current focus is no longer tradability implementation or the search for any non-empty universe.
- Current focus is:
  - documenting the validated calibrated runtime truth cleanly after the hygiene pass,
  - resolving the remaining staged latest-manifest pointer updates deliberately,
  - interpreting the first conservative maker-markout scaffold outputs conservatively,
  - and keeping experimental local calibration clearly separate from tracked default config.
- Treat the current maker-markout output as a triage result under scaffold assumptions, not as execution PnL.

## Decisions Made In This Chat
- A slightly longer bounded polling sample was run by increasing raw-books iterations from `3` to `6` without widening the token subset.
- Downstream rebuild succeeded on that bounded sample:
  - books-state row count = `120`,
  - stable feature-set row count = `120`.
- Default tradability thresholds on the longer bounded sample produced:
  - total markets = `10`,
  - `keep = 0`,
  - `watch = 4`,
  - `exclude = 6`.
- The watch set was a genuine near-miss calibration regime driven by `row_count_watch|repeated_hash_watch`.
- Tradability overrides are read from `tradability_report.thresholds`.
- A local calibration override with:
  - `min_row_count_keep = 12`,
  - `max_repeated_hash_fraction_keep = 0.5`
  produced:
  - total markets = `10`,
  - `keep = 4`,
  - `watch = 0`,
  - `exclude = 6`.
- The calibrated keep set is:
  - `540818`,
  - `540819`,
  - `540844`,
  - `540881`.
- Local `main` was behind `origin/main`; after syncing, the maker-markout scaffold was present locally and ran successfully.
- The first maker-markout scaffold run succeeded on the calibrated active universe and produced:
  - `selected_rows = 44`,
  - `market_summary_rows = 4`,
  - row-step horizons `[1, 2, 5]`.
- A repo/runtime hygiene pass was completed:
  - calibrated runtime artifacts and the local calibration config were backed up under `~/pmre_runtime_snapshots/20260313T102233Z/`,
  - local-only configs were copied to `~/pmre_local_configs/` and removed from `configs/`,
  - generated runtime artifacts and cache junk were removed from the checkout,
  - and no untracked or unmerged entries remain.
- Remaining repo dirt is currently limited to staged updates of:
  - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`,
  - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`.

## Current Coding Task
- No new implementation should be assumed necessary from this chat alone.
- Current task is to update tracked docs so they match the cleaned runtime reality and to decide deliberately what to do with the two remaining staged latest-manifest pointers.
- Treat `configs/local_tradability_calibration.yaml` as an experimental local override unless intentionally promoted.

## Current Runtime Reality
- Latest meaningful bounded-sample feature-set row count is `120`.
- Default-threshold tradability on that sample gives `keep = 0`, `watch = 4`, `exclude = 6`.
- Calibrated tradability gives `keep = 4`, `watch = 0`, `exclude = 6` and a non-empty active universe.
- Latest maker-markout scaffold run is tied to feature-set ID `v0_1_20260312T205218Z__20260312T205508Z`.
- Current maker-markout scaffold assumptions are explicitly conservative:
  - no queue modeling,
  - no fee modeling,
  - no fill-probability modeling,
  - quote prices approximated from midpoint ± spread / 2.
- Current market-summary output shows positive populated mean buy/sell markouts and zero adverse fractions for all four calibrated keep markets, with missing `h5` values for two of them.
- The calibrated runtime artifacts are preserved outside the repo tree; the checkout itself is now near-clean except for the two staged latest-manifest updates.

## Implementation Constraints / Assumptions
- Smallest meaningful next step only.
- Do not duplicate code already present in GitHub.
- Distinguish default-threshold behavior from calibrated local-override behavior.
- Do not describe the current non-empty active universe as a base-config result.
- Treat the current maker-markout result as scaffold-level triage, not realistic execution PnL.
- Keep experimental local configs outside tracked `configs/` unless intentionally promoted.
- ChatGPT Project files remain persistent context; local server flow should not depend on them existing in the checkout.

## Immediate Next Steps
1. Update `STATE.md` and `DEVELOPING_CONTEXT.md` to reflect:
   - longer bounded sample validated,
   - calibrated non-empty active universe validated,
   - maker-markout scaffold validated locally,
   - repo/runtime hygiene pass completed,
   - remaining staged manifest-pointer changes identified explicitly.
2. Decide whether to restore or keep the staged updates to:
   - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`,
   - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`.
3. Keep the calibrated thresholds clearly labeled as experimental unless intentionally promoted into tracked config.
4. Interpret maker-markout outputs conservatively under the stated scaffold assumptions.
