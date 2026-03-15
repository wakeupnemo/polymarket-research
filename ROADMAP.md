# Roadmap

## Highlighted Updates

This roadmap has been updated after:
- the first concise maker-markout interpretation memo,
- a server-side reproducibility / runtime-truth inspection,
- and a check of the preserved longer-sample runtime snapshot versus the current tracked latest checkout.

### What changed
- The project is no longer waiting on:
  - first diagnostics interpretation,
  - first tradability / active-universe output,
  - first maker-markout scaffold execution,
  - or the first concise decision memo on what the maker-markout scaffold currently does and does not establish.
- The project now has two distinct runtime truths that must be kept separate:
  - the preserved longer bounded sample under `~/pmre_runtime_snapshots/20260313T102233Z/`,
  - and the current tracked latest checkout under `data/features/polymarket/...`.
- The preserved longer bounded sample remains the memo-basis runtime truth:
  - books-state row count = `120`
  - feature-set row count = `120`
  - default tradability = `keep 0 / watch 4 / exclude 6`
  - calibrated tradability = `keep 4 / watch 0 / exclude 6`
  - calibrated keep IDs:
    - `540818`
    - `540819`
    - `540844`
    - `540881`
  - maker-markout scaffold facts:
    - `selected_rows = 44`
    - `market_summary_rows = 4`
    - row-step horizons `[1, 2, 5]`
- A server-side reproducibility inspection showed that the working-tree versions of:
  - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`
  - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
  had been pointing to missing newer artifacts.
- Restoring those two pointer files returned the tracked latest checkout to a coherent older basis:
  - freeze id `20260311T214230Z__20260312T133004Z`
  - books-state row count = `60`
  - feature-set row count = `60`
- The current tracked latest checkout is presently blocked from rerunning tradability because:
  - `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`
  is missing.

### What was removed or downgraded
- Any assumption that the current tracked latest checkout still corresponds to the memo-basis 120-row sample.
- Any assumption that current-tracked reproducibility can be checked immediately from latest pointers without verifying diagnostics latest-manifest truth.
- Any assumption that pointer-file existence alone is enough evidence that the pointed-to artifacts exist.
- Any assumption that the first maker-markout decision memo is still missing.

---

## Purpose of This Roadmap

This roadmap is the current implementation-aware plan for turning the project from:
- a naïve historical screener,
- into a serious execution-aware research engine.

It is designed to optimize for:
- learning speed,
- falsification speed,
- execution realism,
- and durable architecture.

It is **not** designed to maximize the amount of code written.  
It is designed to maximize the probability that the project quickly learns:
- which data products are trustworthy,
- which hypotheses are worth expanding,
- and which directions should be killed.

---

## Roadmap Principles

This roadmap follows five rules:

1. **Data trust before signal sophistication**  
   If executable market state is not trustworthy, everything downstream is weak.

2. **Maker-first before model-first**  
   The first real edge question should be about microstructure and fill quality, not about elegant forecasting.

3. **Tradability before alpha**  
   Thin-book gains do not count as evidence.

4. **Cheap falsification before expansion**  
   Weak ideas should fail quickly and explicitly.

5. **Implementation realism over broad scope**  
   The first sprint should produce a usable research backbone, not an overbuilt system.

---

## Current Position

The project is now past initial backbone construction and into early research-layer interpretation plus reproducibility discipline.

### Completed backbone / research blocks
- repo scaffold and execution entrypoints,
- metadata refresh,
- token mapping,
- raw books collection,
- flat top-of-book state construction,
- feature-job input freeze,
- stable feature set `v0_1`,
- diagnostics reporting layer on top of the stable feature set,
- first tradability / active-universe layer,
- first conservative maker-markout scaffold run,
- first concise maker-markout interpretation / decision memo.

### Current live limitations
- no websocket ingestion yet,
- no incremental orderbook reconstruction yet,
- no reconciliation engine yet,
- no first-class event table yet,
- no execution-PnL-quality fill model,
- no queue-position model,
- no fee model,
- calibrated tradability thresholds are still a local experimental override rather than a promoted tracked config path,
- the current tracked latest checkout is not the same runtime basis as the preserved longer-sample memo run,
- the current tracked latest checkout is missing `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`,
- therefore current-tracked tradability and maker-markout reruns are blocked until diagnostics latest-manifest truth is restored.

This means the project has a usable early research loop and a preserved longer-sample runtime truth, but current tracked-latest reproducibility is not yet fully restored.

---

## Backbone Already Completed

## Block A — Metadata foundation
### Status
**Completed**

### Deliverables now available
- raw paginated metadata pages,
- `markets.csv`,
- `tokens.csv`,
- metadata checkpoint,
- metadata manifest.

### Notes
- Built from `Gamma /markets`.
- `event_id` should currently be treated as optional / unreliable.

## Block B — Raw books collection
### Status
**Completed**

### Deliverables now available
- append-only raw books JSONL,
- raw books manifests,
- bounded token-subset polling.

### Notes
- Built from `CLOB /books` batch polling.
- This is a research collector, not a production-grade live engine.

## Block C — Books state builder
### Status
**Completed**

### Deliverables now available
- flat state CSV with best bid / ask, midpoint, spread, last trade price, and level counts,
- state manifests.

### Notes
- Best bid and best ask are computed robustly from unsorted levels.
- State is snapshot-based, not incrementally reconstructed.

## Block D — Feature input freeze
### Status
**Completed**

### Deliverables now available
- frozen feature-input bundles under `data/features/polymarket/input_freezes/`,
- latest feature-input freeze manifest,
- reproducible boundary between upstream state artifacts and downstream feature generation.

### Notes
- Only approved frozen inputs are allowed into the stable feature job.
- This is a reproducibility boundary, not a research signal layer.
- The current tracked latest pointer now resolves coherently again, but it resolves to the older 60-row basis.
- The preserved longer 120-row basis exists separately under `~/pmre_runtime_snapshots/20260313T102233Z/`.

## Block E — Stable feature layer
### Status
**Completed**

### Deliverables now available
- `feature_set_v0_1_<freeze_id>.csv`,
- feature-set manifests,
- stable schema file,
- CLI / shell entrypoints for feature-set generation.

### Notes
- This is a first stable diagnostic feature layer, not a final research feature library.
- The preserved longer bounded validation run reached feature-set row count `120`.
- The current tracked latest feature-set pointer now resolves coherently, but to the older tracked feature set with `row_count = 60`.

## Block F — Feature diagnostics layer
### Status
**Completed**

### Deliverables now available
- diagnostics JSON summary,
- market-summary CSV,
- latest diagnostics manifest,
- CLI command `build-feature-diagnostics`,
- shell runner `scripts/run_build_feature_diagnostics.sh`,
- focused diagnostics test.

### Notes
- The diagnostics job was run successfully on the longer bounded sample.
- The diagnostics layer feeds the validated tradability pass used for active-universe narrowing.
- Diagnostics interpretation is no longer hypothetical; it has been exercised through explicit gating decisions.
- Current tracked-latest reproducibility is blocked because the live checkout is missing:
  - `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`

## Block G — Tradability / active-universe layer
### Status
**Completed**

### Deliverables now available
- tradability JSON report,
- tradability market-summary CSV with `keep / watch / exclude`,
- keep-only active-universe CSV,
- latest tradability manifest,
- CLI command `build-tradability-report`,
- shell runner `scripts/run_build_tradability_report.sh`,
- focused tradability test.

### Notes
- On the preserved longer bounded sample:
  - total markets = `10`
  - default thresholds produced:
    - `keep = 0`
    - `watch = 4`
    - `exclude = 6`
  - the calibrated local override under `tradability_report.thresholds` produced:
    - `keep = 4`
    - `watch = 0`
    - `exclude = 6`
- The validated calibrated keep set remains:
  - `540818`
  - `540819`
  - `540844`
  - `540881`
- The currently validated non-empty active universe should still be described as a **calibrated local-override result**, not as a base-config result.
- Current tracked-latest tradability reruns are blocked until diagnostics latest-manifest truth is restored.

## Block H — Conservative maker-markout scaffold
### Status
**Completed**

### Deliverables now available
- maker-markout report JSON,
- maker-markout per-row CSV,
- maker-markout per-market summary CSV,
- latest maker-markout manifest,
- CLI command `build-maker-markout`,
- shell runner `scripts/run_build_maker_markout.sh`,
- focused maker-markout test,
- first concise interpretation / decision memo.

### Notes
- The preserved memo-basis maker-markout run consumed the calibrated keep-only active universe of `4` markets.
- The preserved longer-sample maker-markout run produced:
  - `selected_rows = 44`
  - `drop_not_in_active_universe = 72`
  - `drop_stale = 4`
  - `market_summary_rows = 4`
  - row-step horizons `[1, 2, 5]`
- The scaffold remains explicitly conservative and triage-only:
  - no queue modeling,
  - no fee modeling,
  - no fill-probability modeling,
  - quote prices approximated from midpoint ± spread / 2.
- Current tracked-latest maker-markout reruns are blocked downstream because current-tracked tradability cannot rerun yet.

---

## Next Execution Sequence

## Step 1 — Restore current-tracked diagnostics latest-manifest truth
### Status
**In progress**

### Objective
Make the current tracked latest checkout runnable again for tradability verification.

### Concrete Tasks
- inspect the live diagnostics directory under `data/features/polymarket/diagnostics/`,
- restore or regenerate `latest_feature_diagnostics_manifest.json` for the current tracked latest checkout,
- keep this current-tracked repair clearly separate from preserved longer-sample runtime artifacts.

### Outputs
- coherent diagnostics latest-manifest truth on the live checkout,
- clear statement of whether diagnostics were restored or regenerated,
- runnable prerequisite state for tradability.

### Success
- `build-tradability-report` can run again on the current tracked latest checkout.

---

## Step 2 — Current-tracked tradability reproducibility check
### Status
**Planned**

### Objective
Verify what the current tracked latest checkout actually produces once diagnostics truth is restored.

### Concrete Tasks
- rerun tradability once under default tracked thresholds,
- rerun tradability once under the calibrated local override,
- inspect total markets, keep / watch / exclude counts, and calibrated keep IDs,
- keep the result clearly labeled as a current-tracked checkout result rather than a memo-basis 120-row result unless they genuinely coincide.

### Outputs
- current-tracked default tradability summary,
- current-tracked calibrated tradability summary,
- explicit match / drift decision versus preserved runtime truth.

### Success
- the project can state exactly whether the current tracked latest checkout reproduces the documented tradability behavior.

### Failure
- tradability remains blocked,
- or current-tracked results diverge and require explicit drift interpretation.

---

## Step 3 — Current-tracked calibrated maker-markout follow-up
### Status
**Planned**

### Objective
Only if current-tracked calibrated tradability is runnable and coherent, rerun maker-markout once on that basis.

### Concrete Tasks
- run maker-markout on the calibrated active universe produced by the current tracked latest checkout,
- inspect selected rows, market-summary rows, and available horizons,
- compare cautiously against preserved longer-sample scaffold facts.

### Outputs
- current-tracked maker-markout summary,
- explicit note on whether the current checkout aligns with preserved scaffold facts.

### Success
- the project knows whether current-tracked maker-markout remains aligned with preserved runtime truth.

### Failure
- current-tracked tradability never becomes runnable,
- or maker-markout output diverges without a clear artifact-basis explanation.

---

## Step 4 — Broader validation of calibrated universe
### Status
**Planned**

### Objective
Test whether the calibrated active universe remains credible beyond the single preserved longer bounded sample.

### Concrete Tasks
- rerun bounded sampling under similar operational conditions,
- compare keep-set persistence,
- compare row-count / repeated-hash behavior,
- test whether current calibration is stable enough for continued use.

### Outputs
- comparison note across bounded runs,
- keep-set stability assessment,
- recommendation on whether current calibration should remain temporary.

### Success
- the calibrated universe looks repeatable enough to remain useful,
- or instability is identified explicitly and cheaply.

### Failure
- the keep set collapses immediately under similar bounded conditions,
- or calibration proves too brittle to trust even for triage.

---

## Step 5 — Cheap stale-anchor diagnostics
### Status
**Postponed**

### Objective
Test the stale-display direction cheaply before investing heavily.

### Concrete Tasks
- define stale / lagged-display proxy from the state / feature layer,
- look for subsequent price response,
- bucket by spread, depth, and market quality,
- test whether the effect survives basic controls.

### Outputs
- simple event study,
- falsification memo.

### Notes
- This remains a valid research direction,
- but it is not the next implementation priority while current-tracked reproducibility is unresolved.

---

## Step 6 — Minimal crypto fair-value alignment
### Status
**Postponed**

### Objective
Test whether the crypto-linked direction has enough structure to deserve further work.

### Concrete Tasks
- identify a small contract family that clearly maps to external crypto prices,
- define the crudest honest fair-probability model,
- align contract times and underlying data,
- compute residuals,
- test whether residuals correlate with later executable movement.

### Outputs
- minimal alignment layer,
- residual diagnostic report,
- keep / kill recommendation.

### Notes
- This remains a valid later branch,
- but it is not the next implementation priority while maker-first microstructure remains the lead path and current-tracked reproducibility is unresolved.

---

## Current Week-1 / Week-2 Split

## Week 1
### Status
**Completed**

Completed:
- metadata tables,
- raw books collector,
- books state builder,
- feature-input freeze,
- first stable feature layer,
- first diagnostics layer.

## Week 2
### Status
**Current focus**

Must-have:
- current-tracked diagnostics latest-manifest truth restored,
- current-tracked tradability reproducibility checked under default and calibrated settings,
- preserved 120-row runtime truth kept explicitly separate from current-tracked 60-row truth,
- current-tracked maker-markout rerun only if tradability becomes runnable.

Nice-to-have:
- comparison note between preserved runtime truth and current-tracked rerun results,
- broader repeatability check of the calibrated keep set,
- stale-anchor test only if current maker-first triage still supports that expansion.

---

## Next 3 Highest-Priority Tasks

1. **Restore current-tracked diagnostics latest-manifest truth**
   - make the live checkout runnable for tradability again,
   - keep restored current-tracked artifacts distinct from preserved snapshot artifacts.

2. **Rerun current-tracked tradability under default and calibrated settings**
   - measure keep / watch / exclude on the live checkout,
   - compare carefully against preserved 120-row runtime truth.

3. **Rerun maker-markout only if current-tracked calibrated tradability succeeds**
   - inspect selected rows, market-summary rows, and horizons,
   - keep interpretation scaffold-level only.
