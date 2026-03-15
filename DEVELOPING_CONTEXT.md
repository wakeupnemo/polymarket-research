# Developing Context

## Current Development Focus
- Current focus is a small server-side reproducibility / runtime-truth pass, not new implementation.
- Current focus is:
  - separating preserved longer-sample runtime truth from current tracked-latest checkout truth,
  - keeping latest-pointer truth coherent,
  - identifying the exact prerequisite blocking tradability reruns on the live checkout,
  - and avoiding any architecture or scope expansion.

## Decisions Made In This Chat
- Do not add new ingestion, new features, new diagnostics logic, websocket work, event enrichment, crypto fair-value work, stale-anchor work, or simulator expansion in this step.
- Inspect live repo/runtime reality first.
- Restore latest freeze / feature-set pointers if they point to missing artifacts.
- The current live checkout now has coherent latest pointers again:
  - latest freeze pointer resolves,
  - latest feature-set pointer resolves.
- The restored tracked latest basis is the older coherent 60-row sample:
  - books-state row count = `60`
  - feature-set row count = `60`
- The preserved runtime snapshot under `~/pmre_runtime_snapshots/20260313T102233Z/` contains the memo-basis longer-sample truth:
  - local calibration file,
  - diagnostics manifest,
  - calibrated tradability outputs,
  - active-universe CSV,
  - maker-markout outputs.
- The preserved calibrated runtime note matches:
  - keep IDs `540818`, `540819`, `540844`, `540881`
  - `selected_rows = 44`
  - `market_summary_rows = 4`
  - horizons `[1, 2, 5]`
- Current live tradability reruns fail because:
  - `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`
  is missing.
- Current live maker-markout reruns fail downstream because tradability did not produce fresh outputs.
- Therefore the current result is not “drift in tradability counts”; it is “missing diagnostics prerequisite on the live checkout.”

## Current Coding Task
- No new coding task.
- Current task is runtime verification only:
  - keep tracked latest pointers coherent,
  - verify which runtime basis is actually active,
  - verify preserved snapshot contents,
  - and identify the smallest blocker preventing rerun on the current checkout.

## Current Runtime Reality
- `HEAD` is `8980f88` on `main`.
- Current tracked latest freeze / feature-set pair is coherent and points to the older 60-row basis.
- Current tracked latest diagnostics latest-manifest is missing.
- Current tracked latest tradability rerun is blocked.
- Current tracked latest maker-markout rerun is blocked.
- Preserved longer-sample runtime truth exists outside the repo tree under:
  - `~/pmre_runtime_snapshots/20260313T102233Z/`
- Preserved memo-basis calibrated facts remain:
  - default longer-sample split = `keep 0 / watch 4 / exclude 6`
  - calibrated longer-sample split = `keep 4 / watch 0 / exclude 6`
  - calibrated keep IDs = `540818`, `540819`, `540844`, `540881`

## Implementation Constraints / Assumptions
- Smallest meaningful step only.
- Do not change Python code, tests, CLI wiring, or tracked configs unless a real path inconsistency forces it.
- Keep maker and taker logic separate.
- Keep scaffold interpretation conservative.
- Keep preserved snapshot truth separate from tracked-latest truth.
- Do not promote calibrated thresholds into tracked baseline config in this phase.
- Do not overread positive maker-markout scaffold output as execution evidence.

## Immediate Next Steps
1. Restore or regenerate diagnostics latest-manifest truth for the live checkout.
2. Only after diagnostics exists again, rerun tradability on the current tracked latest checkout.
3. Only after calibrated tradability reproduces, rerun maker-markout once.
4. Keep any update to docs or tracked state explicit about the distinction between:
   - preserved 120-row runtime truth,
   - and current tracked 60-row checkout truth.
