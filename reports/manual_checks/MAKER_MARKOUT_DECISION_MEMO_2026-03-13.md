# Maker-Markout Decision Memo (2026-03-13)

## Objective
Record a conservative, operational interpretation of the first maker-markout scaffold run without overclaiming execution edge.

## Inputs / runtime basis
- Longer bounded sample validation with `books-state row_count = 120` and `feature-set row_count = 120`.
- Tradability output under default thresholds: `keep = 0`, `watch = 4`, `exclude = 6`.
- Tradability output under experimental local calibration override (`min_row_count_keep = 12`, `max_repeated_hash_fraction_keep = 0.5`): `keep = 4`, `watch = 0`, `exclude = 6`.
- Calibrated keep set: `540818`, `540819`, `540844`, `540881`.

## What was tested
- Conservative maker-markout scaffold run on the calibrated active universe.
- Output checks included selected rows, market summary coverage, and horizon population.

## What is validated
- Maker-markout scaffold execution succeeded end-to-end on calibrated keep markets.
- Run produced `selected_rows = 44` and `market_summary_rows = 4`.
- Row-step horizons were `[1, 2, 5]`.
- Populated market summaries showed positive mean buy/sell markouts and zero adverse fractions for populated cells.

## What is NOT validated
- Execution PnL under realistic queue, fees, and fill dynamics.
- Robustness across broader sample windows, regimes, or universes.
- Any claim that calibrated thresholds should replace default thresholds.

## Interpretation limits
- This is scaffold-level triage, not executable strategy evidence.
- Positive symmetric markouts and zero adverse fractions may be heavily shaped by scaffold assumptions.
- Missing `h5` coverage for two markets materially limits horizon interpretation.
- Calibrated thresholds remain an experimental local override unless explicitly promoted later.

## Decision
- This result is enough to justify continuing conservative maker-first triage on the same bounded methodology and documenting outcomes with the same caveats.
- This result is not enough to justify execution deployment, PnL claims, or threshold promotion into tracked baseline config.

## Immediate next action
Perform one small bounded server verification run to confirm reproducibility of:
1. default-threshold split (`keep = 0`, `watch = 4`, `exclude = 6`),
2. calibrated split (`keep = 4`, `watch = 0`, `exclude = 6`), and
3. calibrated keep IDs (`540818`, `540819`, `540844`, `540881`).
