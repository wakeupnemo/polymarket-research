# Roadmap

## Highlighted Updates

This roadmap has been updated after the first implemented data backbone.

### What changed
- The previous roadmap assumed the project was still in pure pre-implementation mode. That is no longer true.
- The first three concrete units are now implemented:
  1. metadata tables,
  2. raw books collector,
  3. books state builder.
- The current working ingestion path is:
  - `Gamma /markets` for metadata,
  - `CLOB /books` polling for raw book snapshots.
- The current live collection path is polling, not websocket.
- Event-level enrichment is not yet a dependency for the next research step.
- The roadmap is now centered on:
  - data-quality validation,
  - feature computation,
  - tradability diagnostics,
  - and first maker-markout experiments.

### What was removed or downgraded
- Immediate websocket engineering as a hard dependency for week 1.
- Immediate event-table completion as a hard dependency for week 1.
- Broad “build everything first” sequencing.

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

The project is now past initial framing and into early execution.

### Completed backbone blocks
- repo scaffold and execution entrypoints,
- metadata refresh,
- token mapping,
- raw books collection,
- flat top-of-book state construction.

### Current live limitations
- no websocket ingestion yet,
- no incremental orderbook reconstruction yet,
- no reconciliation engine yet,
- no first-class event table yet,
- no feature library yet,
- no markout experiment yet.

This means the project has enough structure to begin serious diagnostics, but not enough evidence to claim any edge.

---

## Backbone Already Completed

## Block A — Metadata foundation
### Status
Completed in first usable form.

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
Completed in first usable form.

### Deliverables now available
- append-only raw books JSONL,
- raw books manifests,
- bounded token-subset polling.

### Notes
- Built from `CLOB /books` batch polling.
- This is a research collector, not a production-grade live engine.

## Block C — Books state builder
### Status
Completed in first usable form.

### Deliverables now available
- flat state CSV with best bid / ask, midpoint, spread, last trade price, and level counts,
- state manifests.

### Notes
- Best bid and best ask are computed robustly from unsorted levels.
- State is snapshot-based, not incrementally reconstructed.

---

## Next Execution Sequence

## Step 1 — Data-quality diagnostics
### Objective
Prove that the current state layer is usable enough for the first experiments.

### Concrete Tasks
- check for empty books,
- check for crossed or inverted books,
- check spread sanity,
- check missing-token or missing-market mapping cases,
- inspect repeated hashes and stale timestamps,
- inspect a few Yes/No pairs manually.

### Outputs
- data-quality report,
- failure-rate summary,
- list of excluded markets or tokens,
- explicit go / no-go judgment for the current polling state layer.

### Success
- obvious corruption is rare or explainable,
- bad rows can be flagged or excluded cleanly,
- the current state layer can support first-pass research.

### Failure
- too many empty / stale / pathological books,
- or the current polling layer proves too lossy for even conservative studies.

---

## Step 2 — First feature library
### Objective
Build the first state-derived feature layer.

### Concrete Tasks
Compute, at minimum:
- spread,
- midpoint,
- best-bid size,
- best-ask size,
- top-of-book imbalance,
- basic microprice proxy,
- last-trade minus midpoint,
- bid/ask level counts,
- simple staleness flags,
- simple market quality score.

### Outputs
- features CSV or parquet,
- feature definitions note,
- first inspection report.

### Success
- features are well-defined and reproducible,
- obvious leakage risks are absent,
- feature values match raw spot checks.

### Failure
- features are ambiguous,
- misaligned,
- or too noisy to interpret.

---

## Step 3 — Tradability and universe narrowing
### Objective
Measure which markets are actually researchable.

### Concrete Tasks
- compute spread distributions,
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

## Step 4 — First maker-markout scaffold
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
- or the current state layer is too weak to support the assumptions honestly.

---

## Step 5 — Cheap stale-anchor diagnostics
### Objective
Test the stale-display direction cheaply before investing heavily.

### Concrete Tasks
- define stale / lagged-display proxy from the state layer,
- look for subsequent price response,
- bucket by spread, depth, and market quality,
- test whether the effect survives basic controls.

### Outputs
- simple event study,
- falsification memo.

### Success
- either the effect looks real enough to keep,
- or it is killed cheaply.

---

## Step 6 — Minimal crypto fair-value alignment
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

### Success
- the direction becomes evidence-backed rather than speculative.

---

## Current Week-1 / Week-2 Split

## Week 1
Must-have:
- metadata tables,
- raw books collector,
- books state builder,
- data-quality diagnostics,
- first feature layer.

Nice-to-have:
- first tradability report,
- first maker-markout scaffold.

## Week 2
Must-have:
- tradability report,
- narrowed research universe,
- first conservative maker-markout run,
- first go / no-go memo on maker-first.

Nice-to-have:
- cheap stale-anchor test,
- minimal crypto fair-value alignment,
- event enrichment if it becomes necessary.

---

## Immediate Next Tasks

1. Build the first **state-derived feature computation layer**.
2. Build the first **data-quality diagnostics** on the current state output.
3. Build the first **tradability report** and define a narrower active universe.
4. Build the first **maker markout experiment scaffold**.

That is the highest-information next sequence.

---

## Success Criteria for the Next Milestone

The next milestone is successful if:
- the current polling-based state layer survives basic integrity checks,
- the project can rank markets by tradability,
- the first feature layer is stable and interpretable,
- and the first maker-markout study can be run without obviously dishonest assumptions.

If those conditions fail, the project should repair data and state quality before building more research logic.

---

## Non-Goals Right Now

The following are not immediate goals of this phase:
- launching a fully automated production bot,
- building a portfolio optimizer,
- training large ML models,
- engineering a full websocket + reconciliation system before first evidence exists,
- or optimizing strategy complexity before signal validity is established.

Those may become relevant later, but only after the current backbone earns its keep.

---

## Summary

The project has crossed the line from concept to working backbone.

Current implemented stack:
- metadata refresh,
- token mapping,
- raw order-book polling,
- flat top-of-book state builder.

The roadmap should now stay narrow:
- validate data quality,
- compute first features,
- measure tradability,
- and run the first conservative maker-quality studies.