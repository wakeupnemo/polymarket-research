# Roadmap

## Highlighted Updates

This roadmap has been updated after the first stable feature pipeline and the first diagnostics layer were successfully implemented and validated.

### What changed
- The project is no longer waiting on:
  - first data-quality diagnostics,
  - first feature computation,
  - or first diagnostics/reporting on top of the stable feature set.
- The implemented pipeline now reaches:
  - metadata refresh,
  - raw books collection,
  - books state build,
  - feature-input freeze,
  - stable feature set `v0_1`,
  - feature diagnostics.
- The diagnostics layer is now live in the repo, wired into the CLI, covered by a focused test, and successfully run on the current real feature artifact.
- The current next sequence is now:
  1. repo hygiene and intentional artifact/versioning decisions,
  2. diagnostics interpretation and gating decisions,
  3. tradability / research-universe narrowing,
  4. first conservative maker-markout scaffold.

### What was removed or downgraded
- “Build the first feature layer” as an immediate next task.
- “Build the first diagnostics layer” as an immediate next task.
- Any additional ingestion or feature-builder scaffolding for this step.
- Any duplicate smoke or validation scaffolding for this step.

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

The project is now past initial backbone construction and into early research-layer validation.

### Completed backbone blocks
- repo scaffold and execution entrypoints,
- metadata refresh,
- token mapping,
- raw books collection,
- flat top-of-book state construction,
- feature-job input freeze,
- stable feature set `v0_1`,
- diagnostics reporting layer on top of the stable feature set.

### Current live limitations
- no websocket ingestion yet,
- no incremental orderbook reconstruction yet,
- no reconciliation engine yet,
- no first-class event table yet,
- no markout experiment yet,
- no explicit market gating / tradability rules yet,
- no first decision memo on whether stale / repeated-hash patterns should drive exclusion.

This means the project now has enough structure to begin research triage, but not enough evidence yet to claim any edge.

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
- Current live feature-set row count is `60` for the latest validated run.

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
- The diagnostics job was run successfully on the current stable feature artifact.
- The latest validated run reported:
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
- The implementation already existed on GitHub `main`; the Debian server matched the targeted files and required no additional diagnostics code patch.

---

## Next Execution Sequence

## Step 1 — Repo hygiene and sync discipline
### Status
**In progress**

### Objective
Keep the working tree intentional before further research steps.

### Concrete Tasks
- remove `__pycache__` / `.pyc` junk,
- inspect generated artifacts intentionally,
- decide which generated data products should be versioned,
- rebase local `main` before any push.

### Outputs
- clean working tree,
- explicit artifact commit policy for this stage,
- synced branch state.

### Success
- no accidental Python cache junk is tracked,
- only intentional artifacts are committed,
- branch divergence does not block the next research step.

---

## Step 2 — Diagnostics interpretation and gating rules
### Status
**In progress**

### Objective
Turn the first diagnostics outputs into explicit triage rules instead of passive reports.

### Concrete Tasks
- inspect stale-row behavior by market,
- inspect repeated-hash concentration by market,
- decide whether stale / repeated-hash thresholds should gate or only annotate,
- decide whether current market-quality score is sufficient for first-pass filtering,
- define explicit keep / watch / exclude rules.

### Outputs
- diagnostics interpretation note,
- first market-quality / exclusion rules,
- go / no-go decision on using current diagnostics for research-universe narrowing.

### Success
- diagnostics are actionable rather than merely descriptive,
- poor-quality markets can be excluded consistently,
- the project has a concrete rule for when current polling state is “good enough”.

### Failure
- diagnostics remain too ad hoc,
- repeated-hash or stale behavior is too widespread to ignore,
- or threshold choices prove too unstable to trust.

---

## Step 3 — Tradability and universe narrowing
### Status
**Planned**

### Objective
Measure which markets are actually researchable.

### Concrete Tasks
- compute spread distributions from the current feature / diagnostics outputs,
- compute depth distributions,
- bucket by market and token,
- rank markets by practical quality,
- define a smaller active research universe,
- separate “interesting but unusable” from “boring but tradable”.

### Outputs
- liquidity / tradability report,
- inclusion and exclusion rules,
- first active research universe definition.

### Success
- a narrower research universe is defined clearly,
- the project stops wasting time on junk books.

### Failure
- the current token subset is mostly noise,
- or tradability is too weak for the lead direction.

---

## Step 4 — First conservative maker-markout scaffold
### Status
**Planned**

### Objective
Build the first conservative maker-first experiment.

### Concrete Tasks
- define candidate decision timestamps,
- define quote side and quote level,
- define conservative fill assumptions,
- define fill / no-fill cases,
- define post-fill markout horizons,
- compute markouts by regime bucket.

### Outputs
- experiment code scaffold,
- first markout tables,
- first toxicity slices,
- first decision memo.

### Success
- the experiment can tell whether maker ideas deserve more attention.

### Failure
- the experiment reveals no plausible maker edge,
- or the current state / diagnostics layer is too weak to support the assumptions honestly.

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
- but it is not the next implementation priority until tradability and maker-markout basics exist.

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
- but it is not the next implementation priority while maker-first microstructure remains the lead path.

---

## Current Week-1 / Week-2 Split

## Week 1
### Status
**Mostly completed**

Must-have completed:
- metadata tables,
- raw books collector,
- books state builder,
- feature-input freeze,
- first stable feature layer,
- first diagnostics layer.

Remaining from the spirit of week 1:
- convert diagnostics output into explicit gating / triage decisions.

## Week 2
### Status
**Current focus**

Must-have:
- diagnostics interpretation and gating rules,
- tradability report,
- narrowed research universe,
- first conservative maker-markout scaffold.

Nice-to-have:
- first go / no-go memo on maker-first,
- cheap stale-anchor test if current data quality is strong enough,
- event enrichment only if it becomes necessary.

---

## Next 3 Highest-Priority Tasks

1. **Finalize repo hygiene and branch sync**
   - remove Python cache junk,
   - make intentional artifact/versioning decisions,
   - rebase local `main` before push.

2. **Turn diagnostics into explicit gating rules**
   - decide how stale rows, repeated hashes, and market-quality score affect keep / exclude decisions.

3. **Produce the first tradability / active-universe report**
   - rank markets by practical research quality,
   - define the first active universe for maker-markout work.

---

## Immediate Next Tasks

1. Clean repo hygiene on the Debian server and sync local `main`.
2. Interpret the current diagnostics outputs and define first exclusion / gating rules.
3. Build the first tradability report and active research-universe definition.
4. Start the first conservative maker-markout scaffold on the narrowed universe.

That is now the highest-information next sequence.

---

## Success Criteria for the Next Milestone

The next milestone is successful if:
- the current diagnostics layer produces explicit keep / exclude rules,
- the project can rank markets by tradability,
- a narrower active universe is defined clearly,
- and the first maker-markout scaffold can be run on that universe without obviously dishonest assumptions.

If those conditions fail, the project should repair data quality / collection cadence / diagnostics logic before building more research logic.

---

## Non-Goals Right Now

The following are not immediate goals of this phase:
- launching a fully automated production bot,
- building a portfolio optimizer,
- training large ML models,
- engineering a full websocket + reconciliation system before first evidence exists,
- rebuilding ingestion or feature scaffolding that already exists,
- or optimizing strategy complexity before signal validity is established.

Those may become relevant later, but only after the current backbone earns its keep.

---

## Summary

The project has crossed the line from working backbone into first research-quality diagnostics.

Current implemented stack:
- metadata refresh,
- token mapping,
- raw order-book polling,
- flat top-of-book state builder,
- feature-input freeze,
- stable feature set `v0_1`,
- feature diagnostics.

The roadmap should now stay narrow:
- keep the repo clean and synced,
- turn diagnostics into explicit gating rules,
- measure tradability,
- and run the first conservative maker-quality studies.
