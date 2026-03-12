# Changelog

All meaningful project changes should be recorded here.

The purpose of this file is not to document every tiny edit.  
Its purpose is to preserve the major conceptual and implementation history of the project:
- why the project exists,
- what changed,
- why it changed,
- what was rejected,
- and what the next milestone is.

---

## Versioning Convention

The project uses lightweight research-stage versioning.

### Suggested interpretation
- `0.x` — early research and architecture stage
- `1.x` — first robust research engine with validated workflows
- `2.x` — deeper implementation, automation, and live execution expansion

At the current stage, the project remains in the `0.x` family.

---

## v0.1 — Initial research-engine framing

### Date
Initial project framing stage

### Why This Project Exists
A basic Polymarket screener already exists, but it is too naïve to support serious research.

The original framing relied too heavily on:
- very cheap longshots,
- near-sure outcomes,
- simple historical price features,
- and threshold-like screening logic.

That framing can generate ideas, but it does not provide a credible path to platform-specific, execution-aware edge.

The project therefore exists to build a more serious research engine that can:
- reconstruct executable market state,
- distinguish raw signal from tradable edge,
- test maker and taker paths separately,
- and falsify weak ideas before implementation effort is wasted.

### What Was Established in v0.1
Version `0.1` establishes the project at the level of:
- core objective,
- research philosophy,
- target architecture,
- first roadmap,
- initial hypothesis catalog,
- and initial data-schema design.

It also establishes that the project should be run as a **research engine**, not as a quick strategy notebook or opportunistic bot project.

### Directions Prioritized in v0.1
The initial serious research scope is concentrated on three directions:

1. **Maker-first microstructure**
2. **Crypto fair-value**
3. **Displayed-price anchor / stale-last-trade correction**

### What Was Explicitly Rejected in v0.1
The following ideas were rejected or sharply downgraded as core research framing:
- “cheap versus expensive by history” as the primary signal family
- percentile gimmicks without execution realism
- simplistic threshold screens
- generic TA-style indicators on prediction-market prices
- midpoint-only backtests
- monolithic scripts without reusable state reconstruction
- any research logic that does not separate maker and taker paths

### Main Architecture Decision in v0.1
The project adopts a modular research architecture centered on:
- universe discovery,
- metadata normalization,
- live market-state ingestion,
- state reconstruction,
- feature computation,
- signal research,
- simulation,
- and evaluation.

### What Remained Unvalidated in v0.1
Version `0.1` did **not** claim that any real edge had been validated.

Open questions included:
- whether live market-state reconstruction would be trustworthy enough,
- whether maker fills could be modeled conservatively enough,
- whether any maker regime was genuinely positive EV,
- whether crypto fair-value residuals would survive execution,
- whether stale-anchor effects would be real and tradable,
- and whether the active research universe would be liquid enough.

### Next Major Milestone from v0.1
Build the minimum viable state pipeline and complete the first conservative maker markout study.

---

## v0.2 — Minimum Debian repo and first working data backbone

### Date
2026-03-12

### Why v0.2 Exists
The project needed to move from architecture-only planning into a working, inspectable, testable implementation backbone.

The first goal was not full sophistication.  
The first goal was to establish that the project could:
- collect trustworthy identifiers,
- preserve raw market data,
- build a usable first state table,
- and do so with maintainable repo structure and repeatable runners.

### What Changed in v0.2
Version `0.2` adds the first implemented research backbone:

#### Repo scaffold
A Debian-first project skeleton now exists with:
- modular `src/pmre/` package layout,
- `configs/base.yaml`,
- shell runners in `scripts/`,
- tests in `tests/`,
- separated `data/raw`, `data/reference`, `data/state`, `data/features`, `reports`, and `logs`.

#### Metadata layer
Implemented:
- `Gamma /markets` metadata refresh,
- resumable checkpointing,
- raw paginated metadata preservation,
- canonical `markets.csv`,
- canonical `tokens.csv`.

#### Raw books layer
Implemented:
- token subset selection from `tokens.csv`,
- batched `CLOB /books` polling,
- append-only raw JSONL storage,
- run manifests.

#### State layer
Implemented:
- flat books-state builder from raw JSONL,
- best bid / best ask extraction,
- midpoint and spread computation,
- state manifests.

### Important Implementation Decisions in v0.2

#### Decision 1 — use `Gamma /markets` for the first metadata layer
The initial `events`-oriented crawl proved too heavy and too timeout-prone for the first reliable implementation pass.

The first validated metadata layer therefore uses:
- `Gamma /markets`
- plus canonical `tokens.csv`

This was chosen because reliability was more important than theoretical completeness.

#### Decision 2 — use polling before websocket engineering
The first raw collector is built from:
- batched `CLOB /books` polling

not from websocket ingestion.

This was chosen because:
- it is smaller,
- easier to validate,
- and sufficient for the first tradability and markout preconditions.

#### Decision 3 — compute top-of-book from unsorted levels
Raw `bids` and `asks` are not assumed to arrive best-first.

The state builder therefore computes:
- best bid as maximum bid price,
- best ask as minimum ask price,

rather than trusting array order.

### What v0.2 Validates
Version `0.2` validates that:
- the project can run as a real repo on the Debian server,
- Polymarket market and token metadata can be collected reliably enough for research,
- real token IDs can be used to request CLOB book data,
- raw book payloads can be preserved,
- and a first normalized top-of-book state table can be built.

### What v0.2 Does Not Yet Validate
Version `0.2` does **not** validate:
- event-level joins as a stable dependency,
- websocket ingestion,
- incremental book reconstruction,
- orderbook reconciliation,
- honest maker-fill simulation,
- or any actual positive-EV strategy.

### Assumptions Removed or Downgraded in v0.2
The following assumptions were removed or downgraded:
- that `events.csv` had to be built before useful research could begin,
- that websocket ingestion had to come before any state diagnostics,
- that event linkage was required before token-level state work,
- that the project was still only in planning mode.

### New Priority After v0.2
The new immediate priority is:
1. feature computation on top of the books state,
2. data-quality diagnostics,
3. tradability and universe narrowing,
4. first conservative maker-markout study.

### Why This Matters
v0.2 is the point where the project becomes maintainable by other agents without re-deriving the architecture from scratch.

There is now a real working chain:

metadata -> tokens -> raw books -> flat state

That chain is the current backbone and should be preserved while downstream research is built.

### Expected Shape of v0.3
If `v0.2` is executed correctly, `v0.3` should include:
- first state-derived feature library,
- first data-quality diagnostics report,
- first tradability / liquidity report,
- first narrowed active research universe,
- and first conservative maker-markout scaffold or report.

---

## v0.3 — Dual feature paths and books-feature sanity diagnostics

### Date
2026-03-12

### Why v0.3 Exists
After validating the minimum backbone in v0.2, the project needed a faster iterative feature workflow while preserving the existing freeze-based path.

The goal of v0.3 is to:
- keep the stable `feature_set_v0_1` chain,
- add a direct state-to-features path for quicker diagnostics,
- and make feature runs self-checking with explicit sanity counters.

### What Changed in v0.3

#### New direct books-features builder
Added a new standalone job:
- `src/pmre/features/build_books_features.py`

The job now:
- reads latest books-state manifest,
- loads the referenced books-state CSV,
- computes lightweight books-derived features,
- writes `books_features_<run_id>.csv`,
- writes `books_features_<run_id>_manifest.json`,
- updates `latest_books_features_manifest.json`.

#### New execution wiring
Added:
- CLI command: `build-books-features`
- runner: `scripts/run_build_books_features.sh`
- config block: `books_feature_builder` in `configs/base.yaml`

#### New in-builder sanity diagnostics
The books-features job now computes and stores:
- `row_count_in`
- `row_count_out`
- `missing_token_id_count`
- `missing_bid_ask_count`
- `negative_spread_count`
- `zero_depth_rows_count`
- `null_imbalance_count`
- `null_microprice_count`
- `null_last_trade_minus_mid_count`

These diagnostics are printed at runtime and persisted in manifests under `sanity_checks`.

#### Test coverage
Added:
- `tests/test_build_books_features.py`

The test validates:
- output artifacts,
- core computed feature values,
- staleness behavior,
- sanity diagnostic counters.

### Important Decisions in v0.3

#### Decision 1 — keep two feature paths in parallel
The project now supports:
1. freeze-based stable feature path (`v0_1`),
2. direct books-features path for fast diagnostics.

This preserves reproducibility while improving iteration speed.

#### Decision 2 — make sanity checks first-class output
Sanity counters are now treated as required output metadata rather than ad-hoc logs.

This supports:
- faster triage of bad runs,
- explicit data-quality visibility,
- and safer handoff across agents.

### What v0.3 Validates
Version `0.3` validates that:
- state-to-feature runs can be executed independently from freeze flow,
- books-derived diagnostics can be generated and tracked run-by-run,
- and feature artifacts can include embedded quality signals for downstream research.

### What v0.3 Does Not Yet Validate
Version `0.3` does **not** validate:
- final tradability or PnL claims,
- maker-fill realism beyond current proxies,
- websocket-first ingestion,
- incremental full book reconstruction,
- or cross-market/event-level diagnostics as mandatory dependencies.

### Assumptions Removed or Downgraded in v0.3
The following assumptions were removed or downgraded:
- that feature iteration must always go through freeze flow,
- that feature outputs without explicit sanity counters are acceptable,
- that diagnostics should live only in separate downstream reporting jobs.

### New Priority After v0.3
The new immediate priority is:
1. build diagnostics that can consume both feature manifest types,
2. produce market-level quality summaries and exclusions,
3. narrow the active tradable universe,
4. run the first conservative markout/tradability reports.

### Why This Matters
v0.3 makes the feature layer more practical for day-to-day research while preserving the conservative frozen path.

The project now has two concrete feature-production modes:
- reproducible freeze-based feature set,
- fast direct books-features diagnostics.

This improves both research velocity and operational clarity.

---


## v0.3.1 — Manual feature validation and stale-row confirmation
### Date
2026-03-12

### Why v0.3.1 Exists
After `v0.3` added dual feature paths and embedded sanity diagnostics, the next necessary step was to verify by hand that the core feature formulas matched the builder logic on real output rows and that bad rows were explicitly surfaced rather than silently passing through as clean data.

### What Changed in v0.3.1
A first manual validation pass was completed against the latest freeze-based feature artifact.

#### Manual spot checks completed
Performed 10 manual spot checks against sampled feature rows and joined state data.

Verified on the sampled rows:
- `spread = best_ask_price - best_bid_price`
- `top_of_book_imbalance = (best_bid_size - best_ask_size) / (best_bid_size + best_ask_size)`
- `microprice_proxy` moved toward the heavier side of the book
- `last_trade_minus_mid = last_trade_price - midpoint`

#### Validation outcome
The manual pass confirmed:
- spread matched on 10/10 sampled rows
- imbalance matched on 10/10 sampled rows
- microprice direction matched on 10/10 sampled rows
- `last_trade_minus_mid` sign and value matched on 10/10 sampled rows

#### Stale-row handling confirmed
The sampled bad rows were not silently accepted:
- rows identified as stale were emitted with `staleness_flag = 1`
- sampled stale rows showed blank raw emitted book/trade fields rather than being treated as clean rows

#### Evidence artifacts
The manual validation pass produced local evidence files under:
- `reports/manual_checks/manual_spot_check_10.tsv`
- `reports/manual_checks/manual_spot_check_10_audit.tsv`
- `reports/manual_checks/STEP5_VERDICT.md`

### Important Decisions in v0.3.1
#### Decision 1 — require at least one manual validation pass after feature-builder changes
Passing tests and successful artifact generation are not sufficient by themselves. Core feature formulas should also be checked directly on real sampled rows before downstream research relies on them.

#### Decision 2 — treat stale-row surfacing as part of feature correctness
Feature correctness is not only about numeric formulas. It also includes making sure bad rows are visibly flagged rather than silently blending into clean research inputs.

### What v0.3.1 Validates
Version `0.3.1` validates that:
- the freeze-based feature builder is numerically consistent on the sampled rows,
- microstructure-derived fields match the intended formulas in live artifacts,
- and stale rows are surfaced explicitly through `staleness_flag`.

### What v0.3.1 Does Not Yet Validate
Version `0.3.1` does **not** validate:
- that repeated-hash stale behavior was triggered in the current sample,
- that missing-last-trade streak stale behavior was triggered in the current sample,
- market-level exclusion rules,
- tradability or PnL claims,
- or any positive-EV strategy result.

### Assumptions Removed or Downgraded in v0.3.1
The following assumptions were removed or downgraded:
- that feature outputs could be trusted without a manual spot-check pass,
- that stale-row handling was already sufficiently evidenced by builder logic alone,
- that current diagnostics were enough without row-level validation evidence.

### New Priority After v0.3.1
The new immediate priority is:
1. add a deterministic diagnostics/report step that summarizes feature quality at the market level,
2. make stale reasons more explicit by category where useful,
3. narrow the active research universe using quality and tradability filters,
4. proceed to first conservative markout and tradability reporting.

### Why This Matters
`v0.3.1` is the point where the feature layer is not only implemented, but manually sanity-checked on real output. This reduces the risk of building downstream diagnostics, exclusions, and markout studies on top of silently broken feature logic.

## Changelog Usage Rule

When adding future entries:
- state what changed,
- state why it changed,
- record what was invalidated or deprioritized,
- record what became the new priority,
- and link the change to a concrete milestone or experiment where possible.

This file should remain concise at the version level, while experiment-level detail belongs elsewhere.