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

## Changelog Usage Rule

When adding future entries:
- state what changed,
- state why it changed,
- record what was invalidated or deprioritized,
- record what became the new priority,
- and link the change to a concrete milestone or experiment where possible.

This file should remain concise at the version level, while experiment-level detail belongs elsewhere.