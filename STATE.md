# Current State

## Highlighted Updates

This document has been updated to reflect the first implemented research feature layer, the first real feature build on project data, and the newly implemented feature diagnostics layer on top of the stable feature set.

### New since the previous version
- A dedicated books-features builder now exists (`build-books-features`) for direct state-to-features output without the freeze-based `v0_1` chain.
- The books-features job now emits explicit sanity diagnostics in the run manifest and latest manifest.
- Sanity diagnostics now include:
  - row count in/out,
  - missing `token_id` count,
  - missing bid/ask count,
  - negative spread count,
  - zero-depth row count,
  - null imbalance count,
  - null microprice count,
  - null `last_trade_minus_mid` count.
- The first stable feature set `v0_1` remains available and unchanged for freeze-based research runs.
- A dedicated feature diagnostics builder now exists (`build-feature-diagnostics`) and consumes only the latest stable feature-set manifest/artifact.
- Diagnostics outputs now include aggregate quality counts plus market-level summary statistics and a latest diagnostics manifest.
- The workflow remains GitHub-centered for code, while ChatGPT Project files are used for persistent context.

### Outdated assumptions removed
- The project no longer stops at metadata, raw books, flat state, and planned feature logic.
- The next immediate task is no longer “build the first feature layer”; that layer now exists.
- The first feature output should not be treated as final research truth; it is a simple diagnostic product.
- Websocket logic, event enrichment, and simulator assumptions are still not part of the feature job.
- Persistent Project context files should not be assumed to be stored on the Debian server.

---

## Project Objective

Build a serious research engine for discovering **platform-specific, execution-aware edge** on Polymarket.

The goal is not to rush into a bot or accumulate loosely related ideas. The goal is to build the correct research process and implementation sequence so that:
- raw patterns are separated from executable edge,
- maker and taker logic remain distinct,
- weak ideas are falsified early,
- and only robust hypotheses are promoted into deeper implementation.

---

## Current Phase

**Phase 1 — minimum data backbone plus first stable feature layer implemented; research diagnostics beginning**

The project has moved beyond pure data plumbing and into the first reproducible feature stage.

Current reality:
- metadata universe refresh works,
- token IDs are being collected and stored,
- raw order-book snapshots are being collected,
- top-of-book state is being built from raw snapshots,
- the feature-job input set is frozen explicitly,
- a first stable feature set `v0_1` has been built successfully from those frozen inputs,
- and a first diagnostics layer now runs on top of `feature_set_v0_1` outputs.

This is still an early research-stage system, but it is no longer just a design document set and it is no longer only an ingestion/state project.

---

## What Is Already Implemented

### Repository and execution scaffold
A minimal Debian-first repo exists with:
- config-driven execution,
- modular Python package layout under `src/pmre/`,
- shell runners under `scripts/`,
- tests under `tests/`,
- raw / reference / state / features / reports directory separation.

### Repository workflow
A minimal GitHub-centered workflow is now established:
- the GitHub repository is the source of truth for code,
- the Debian server runs the checked-out repo,
- ChatGPT Project files are used for persistent context,
- and server-side coding flow should not depend on Project context files existing locally.

### Implemented data layers

#### 1. Metadata tables
Implemented and working:
- raw paginated market metadata preservation,
- canonical `markets.csv`,
- canonical `tokens.csv`,
- resumable metadata refresh,
- active-market filtering.

Current implementation notes:
- metadata is currently built from `Gamma /markets`,
- not from `Gamma /events`,
- because the event-heavy crawl proved too operationally fragile for the first backbone pass.

#### 2. Raw books collector
Implemented and working:
- token selection from `tokens.csv`,
- batched `CLOB /books` polling,
- append-only raw JSONL storage,
- run manifest output,
- repeated polling across iterations.

Current implementation notes:
- this is a polling collector,
- not websocket ingestion,
- and it currently targets a bounded subset of tokens for week-1 research.

#### 3. State builder
Implemented and working:
- reads raw books JSONL,
- maps book snapshots back to token / market metadata present in the request envelope,
- extracts best bid and best ask,
- computes midpoint and spread,
- writes flat state CSV,
- writes a state manifest.

Important implementation detail:
- the raw `bids` and `asks` arrays are not assumed to be pre-sorted,
- so best bid is computed as `max(bid price)`,
- and best ask is computed as `min(ask price)`.

#### 4. Feature-job input freeze
Implemented and working:
- takes the latest built books-state artifact as the only allowed state input,
- freezes:
  - latest books state manifest,
  - corresponding `books_state_<run_id>.csv`,
  - `markets.csv`,
  - `tokens.csv`,
- copies them into a run-specific feature input bundle,
- writes a feature-input freeze manifest,
- records hashes and row counts.

Current implementation notes:
- this is an explicit reproducibility boundary,
- and it intentionally excludes:
  - websocket-derived inputs,
  - event enrichment,
  - simulator assumptions.

#### 5. Stable feature schema and feature builder
Implemented and working:
- defines `feature_set_version = v0_1`,
- consumes only the frozen feature-input bundle,
- builds the first stable feature CSV,
- writes feature-set manifest and schema files.

Current implementation notes:
- the current feature layer is intentionally minimal and diagnostic,
- not a final research truth layer,
- and it is limited to the roadmap feature set already planned.
- the current live feature build succeeds on real project data.

Important feature semantics now in use:
- `spread = best_ask_price - best_bid_price`
- `midpoint = mid_price` if already present, otherwise recomputed
- `top_of_book_imbalance = (best_bid_size - best_ask_size) / (best_bid_size + best_ask_size)` when the denominator is positive
- `microprice_proxy = (best_ask_price * best_bid_size + best_bid_price * best_ask_size) / (best_bid_size + best_ask_size)` when the denominator is positive
- `last_trade_minus_mid = last_trade_price - midpoint` when both exist
- `staleness_flag` is currently a first-pass diagnostic flag that includes:
  - missing bid or ask,
  - `spread <= 0`,
  - timestamp-age threshold,
  - repeated hash too long,
  - missing `last_trade_price` for too many consecutive snapshots
- `market_quality_score` is currently an additive/subtractive first-pass diagnostic score,
  - not a normalized final research metric.

---

## Current Project Structure

The current repo should be understood approximately as:

- `configs/`
  - `base.yaml`
- `scripts/`
  - `bootstrap_venv.sh`
  - `run_metadata_refresh.sh`
  - `run_raw_books_collect.sh`
  - `run_build_books_state.sh`
  - `run_freeze_feature_inputs.sh`
  - `run_build_feature_set_v0_1.sh`
  - `run_build_books_features.sh`
  - `run_build_feature_diagnostics.sh`
  - GitHub / workflow helper scripts
- `src/pmre/`
  - `config.py`
  - `cli.py`
  - `ingest/`
    - `gamma_client.py`
    - `metadata_refresh.py`
    - `clob_client.py`
    - `raw_books_collector.py`
  - `state/`
    - `build_books_state.py`
  - `features/`
    - `freeze_feature_inputs.py`
    - `build_feature_set_v0_1.py`
    - `build_books_features.py`
  - `experiments/`
  - `reporting/`
    - `build_feature_diagnostics.py`
- `tests/`
  - metadata refresh test
  - raw books collector test
  - books state builder test
  - feature input freeze test
  - feature set `v0_1` test
  - books-features builder test
  - feature-diagnostics builder test
- `data/`
  - `raw/`
  - `reference/`
  - `state/`
  - `features/`

This structure is now real and should be preserved unless there is a strong reason to change it.

---

## Current Data Products

### Metadata layer

#### Raw metadata pages
Stored under:
- `data/raw/polymarket/metadata/markets_pages/`

These are paginated raw Gamma market responses preserved as JSON files.

#### Metadata manifest and checkpoint
Stored under:
- `data/raw/polymarket/metadata/metadata_refresh_manifest.json`
- `data/raw/polymarket/metadata/metadata_refresh_checkpoint.json`

These define:
- crawl progress,
- offsets,
- run parameters,
- and output paths.

#### Canonical market table
Stored under:
- `data/reference/polymarket/markets.csv`

Current fields include:
- `market_id`
- `event_id`
- `condition_id`
- `question_id`
- `slug`
- `question`
- `category`
- `active`
- `closed`
- `archived`
- `accepting_orders`
- `enable_order_book`
- `minimum_order_size`
- `minimum_tick_size`
- `liquidity`
- `volume`
- `start_date`
- `end_date`
- `description`
- `market_type`
- `format_type`
- `outcomes_json`
- `outcome_prices_json`
- `clob_token_ids_json`

#### Canonical token table
Stored under:
- `data/reference/polymarket/tokens.csv`

Current fields include:
- `market_id`
- `event_id`
- `token_index`
- `outcome`
- `token_id`
- `outcome_price`

### Raw books layer

#### Raw books JSONL
Stored under:
- `data/raw/polymarket/books/books_run_<run_id>.jsonl`

Each JSONL line is an envelope containing:
- collector timestamp,
- iteration index,
- batch index,
- requested token IDs,
- requested token metadata,
- returned books payload.

This raw file is the main preserved source for downstream state building.

#### Raw books manifest
Stored under:
- `data/raw/polymarket/books/books_run_<run_id>_manifest.json`
- `data/raw/polymarket/books/latest_books_manifest.json`

### State layer

#### Flat books state CSV
Stored under:
- `data/state/polymarket/books_state_<run_id>.csv`

Current fields include:
- `source_run_id`
- `collector_ts`
- `book_timestamp`
- `iteration`
- `batch_index`
- `market_id`
- `event_id`
- `outcome`
- `token_index`
- `token_id`
- `clob_market`
- `best_bid_price`
- `best_bid_size`
- `best_ask_price`
- `best_ask_size`
- `mid_price`
- `spread`
- `bid_levels_count`
- `ask_levels_count`
- `last_trade_price`
- `hash`
- `source_jsonl`

#### State manifest
Stored under:
- `data/state/polymarket/books_state_<run_id>_manifest.json`
- `data/state/polymarket/latest_books_state_manifest.json`

### Feature input freeze layer

#### Frozen feature-input bundle
Stored under:
- `data/features/polymarket/input_freezes/freeze_<freeze_id>/`

Each frozen bundle currently contains:
- latest books state manifest,
- corresponding `books_state_<run_id>.csv`,
- `markets.csv`,
- `tokens.csv`,
- feature-input freeze manifest.

#### Latest feature-input freeze manifest
Stored under:
- `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`

This defines the exact approved input set for the current feature job.

### Feature layer

#### Stable feature set CSV
Stored under:
- `data/features/polymarket/feature_sets/feature_set_v0_1_<freeze_id>.csv`

Current feature columns include:
- `spread`
- `midpoint`
- `best_bid_size`
- `best_ask_size`
- `top_of_book_imbalance`
- `microprice_proxy`
- `last_trade_minus_mid`
- `bid_levels_count`
- `ask_levels_count`
- `staleness_flag`
- `market_quality_score`

along with row identifiers and provenance fields such as:
- `feature_set_version`
- `freeze_id`
- `source_run_id`
- `collector_ts`
- `market_id`
- `token_id`
- `hash`

#### Feature-set manifest and schema
Stored under:
- `data/features/polymarket/feature_sets/feature_set_v0_1_<freeze_id>_manifest.json`
- `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
- `data/features/polymarket/feature_sets/feature_set_v0_1_schema.json`

These define:
- the frozen inputs consumed,
- the feature set version,
- the output path,
- the row count,
- and the diagnostic feature definitions.

---

## What Is Validated

At the current stage, the following should be treated as validated.

### Project-level validation
- The original longshot / near-certainty framing is too weak to serve as the core research engine.
- The project should prioritize **maker-first microstructure** before the other two directions.
- A modular, execution-aware architecture is the correct design target.
- The first sprint should focus on data trust, execution realism, and cheap falsification rather than aggressive implementation.

### Implementation validation
- The Debian project skeleton is usable.
- The metadata refresh process runs successfully with resumable progress.
- Canonical market and token tables can be built from live Polymarket metadata.
- Token IDs from the metadata table can be used to collect real CLOB book data.
- Raw book snapshots can be preserved in append-only JSONL.
- A first normalized top-of-book state table can be built from raw book snapshots.
- The state builder correctly computes best bid and best ask from unsorted book levels.
- The feature job input boundary can be frozen reproducibly.
- A first stable feature-set version `v0_1` can be built from the frozen input bundle.
- The current live feature build succeeds on the real project data.
- The GitHub repository is now initialized, connected, and pushed successfully.
- The practical workflow now supports:
  - GitHub for code truth,
  - ChatGPT Project files for persistent context,
  - and multiple coding chats without relying on local server copies of context files.

### Data-contract validation
- `market_id` is usable in the current backbone.
- `condition_id` is usable in the current backbone.
- `token_id` is usable in the current backbone.
- `outcome` to `token_id` mapping is usable in the current backbone.
- The current state artifact is sufficient to support a first stable diagnostic feature layer.

### Process validation
The project has a clear operating mode:
- smallest meaningful next step,
- conservative implementation first,
- simple baselines before complexity,
- explicit labeling of validated vs speculative,
- and written go / no-go decisions.

The feature job now also has an explicit reproducibility rule:
- only the frozen approved inputs are allowed,
- and feature logic should remain narrower than downstream simulation or execution logic.

The workflow now also has an explicit source-of-truth rule:
- GitHub is the source of truth for code,
- ChatGPT Project files are persistent context,
- and server-side scripts should not depend on those context files existing locally.

---

## What Is Not Yet Validated

The following remain important and unvalidated.

### Event linkage
- whether `event_id` can be reliably recovered and maintained in the canonical backbone,
- whether an `events.csv` table should be built now or deferred,
- whether event-level joins are stable enough to rely on for research segmentation.

### Market-state truth beyond top of book
- whether polling-based snapshots are sufficient for the first markout studies,
- whether websocket data is required for the next integrity jump,
- whether book updates between polls create too much hidden state loss,
- whether orderbook reconciliation against incremental updates can be made trustworthy.

### Execution realism
- whether conservative maker fill modeling is good enough for early research,
- whether a first taker simulator will produce realistic effective prices,
- whether partial fills, queue approximations, and fee handling will be honest enough.

### Signal validity
- whether any maker regime has positive expected value after realistic fill and toxicity assumptions,
- whether any crypto fair-value residual survives spread and fees,
- whether any stale-anchor effect is both real and tradable rather than merely observable.

### Operational robustness
- whether the current polling collector can run stably for longer collection windows,
- whether schema drift or payload shape changes will create silent failure modes,
- whether the initial token subset should be expanded or narrowed for research.

### Diagnostic sufficiency of the first feature layer
- whether `v0_1` features are enough for the first useful diagnostics,
- whether the current `staleness_flag` logic is adequate for triage,
- whether the simple `market_quality_score` is good enough for first-pass ranking,
- which additional diagnostics should remain separate from the core stable schema,
- and whether test expectations remain aligned with the current diagnostic scoring semantics.

---

## What Remains Speculative

The following should still be treated as speculative until tested.

### Direction 1 — maker-first microstructure
- that passive quoting is genuinely superior to taker-style entries in selected regimes,
- that fill quality can be predicted well enough to filter toxic fills,
- that refill and aggression features can produce net positive maker EV under realistic assumptions.

### Direction 2 — crypto fair value
- that a crude fair-probability model is informative enough to produce useful residuals,
- that those residuals are not overwhelmed by model error,
- that any residual signal survives execution rather than living only in thin books.

### Direction 3 — displayed-price / stale-anchor
- that stale displayed prices materially influence later behavior,
- that any observed effect is platform-specific rather than generic sparse-book reversion,
- that the effect is economically meaningful after execution costs.

---

## What Has Been Rejected or Explicitly Deprioritized

The following are no longer acceptable as the core research framework:
- “cheap vs expensive by history” as a primary signal family,
- percentile gimmicks without execution context,
- simplistic threshold-only screens,
- generic technical indicators on Polymarket prices,
- midpoint-only backtests,
- monolithic scripts without reusable state reconstruction,
- and any conclusion that depends on historical prints being treated as executable fills.

The following are also currently deprioritized as immediate implementation targets:
- event-table enrichment before market/token/state work is stable,
- websocket ingestion before the first polling-based research loop is exploited,
- overbuilt reconciliation before the first feature and markout studies exist,
- simulator assumptions inside the first stable feature layer,
- and making the server workflow depend on locally stored Project context files.

These are not banned forever; they are just not the next smallest meaningful step.

---

## Open Questions

### Data and infrastructure
1. Should event enrichment be added now or postponed until after the first experiments?
2. Is the current polling cadence sufficient for first-pass research, or does it miss too much state?
3. What is the minimum viable universe size for the first serious experiments?

### State and integrity
4. How should complement consistency between Yes and No books be checked?
5. How should crossed, empty, or obviously stale books be flagged?
6. What diagnostics best separate good data from unusable data?

### Feature layer
7. Which `v0_1` feature diagnostics are most informative for market triage?
8. Which checks belong inside the stable feature schema versus inside a separate diagnostics job?
9. When should `v0_2` be introduced, and what would justify expanding the stable schema?

### Workflow and maintenance
10. What is the smallest reliable routine for keeping ChatGPT Project context current while leaving code truth in GitHub?
11. Which helper scripts should remain server-side, and which should be treated as optional?
12. How much workflow automation is worth keeping before it becomes overhead?

### Maker-first microstructure
13. Can a conservative maker simulator be built from polling snapshots plus simple assumptions?
14. Which features best separate good fills from toxic fills?
15. Is positive maker EV concentrated in a narrow regime or absent altogether?

### Crypto fair value
16. What is the minimum honest fair-value model for short-horizon crypto contracts?
17. Which contract families are easiest to parse and align first?
18. Does fair-value deviation matter only when liquidity is already good?

### Displayed-price / stale-anchor
19. How often do stale-display episodes occur in markets that are actually tradable?
20. Can anchor-like effects survive controls for spread, depth, and liquidity vacuum?
21. Is this direction a real opportunity or mostly a falsification target?

---

## Current Priorities

### Priority 1 — data-quality diagnostics on top of `feature_set_v0_1`
Before serious experiments, the project now needs a first diagnostics layer derived from the implemented feature set:
- spread pathologies,
- stale rows,
- empty or one-sided books,
- suspicious hash repetition,
- last-trade missingness,
- and market quality ranking.

### Priority 2 — tradability diagnostics and universe narrowing
The next outputs should establish:
- spread regimes,
- depth regimes,
- book quality,
- stale / dead market detection,
- and which subset of markets is worth serious simulation.

### Priority 3 — first maker markout study
The next high-information experiment is a maker-first markout and toxicity study under conservative assumptions.

### Priority 4 — keep crypto fair value simple
The crypto direction should begin with the crudest honest model that can be aligned to contracts cleanly.

### Priority 5 — treat stale-anchor as a falsification-first direction
This direction should be tested cheaply and skeptically. It should not receive heavy implementation effort until it proves that the effect is both real and economically meaningful.

---

## Immediate Next Tasks

### Task 1
Implement the first **data-quality diagnostics job** on top of `feature_set_v0_1`:
- spread sanity,
- stale-row frequency,
- one-sided / empty-book checks,
- repeated-hash diagnostics,
- last-trade missingness diagnostics,
- and market quality summaries.

### Task 2
Implement the first **tradability report**:
- spread distributions,
- top-size distributions,
- market quality ranking,
- and a proposed narrowed research universe.

### Task 3
Implement the first **maker markout experiment scaffold**:
- define decision timestamps,
- define conservative fill assumptions,
- define markout horizons,
- and compute outcome distributions by regime bucket.

### Task 4
Keep the GitHub-centered workflow simple:
- treat GitHub as code truth,
- treat ChatGPT Project files as persistent context,
- and avoid server-side dependence on local copies of context documents.

### Task 5
Decide whether **event enrichment** is needed before the first serious report.

---

## Current Go / No-Go Read

### Go
- metadata layer,
- raw polling collector,
- top-of-book state builder,
- frozen feature-input boundary,
- first stable feature set `v0_1`,
- GitHub-centered code workflow.

### Still unknown
- whether the current polling backbone is sufficient for real microstructure research,
- whether the first feature layer is strong enough to rank tradability reliably,
- whether maker alpha survives conservative execution assumptions.

### No-go for now
- broad strategy claims,
- complex fair-value modeling,
- fully automated execution work,
- deep websocket engineering before the first research loop proves it is necessary,
- treating the first diagnostic feature layer as final research truth,
- and bloating the workflow with unnecessary context-file mirroring on the server.

---

## Summary

The project now has a real, working first backbone plus first stable feature layer:

- metadata universe,
- token mapping,
- raw book collection,
- flat top-of-book state construction,
- reproducible frozen feature inputs,
- feature set `v0_1`,
- and a working GitHub-centered code workflow.

That is enough to move into the next stage of week-1 / early week-2 research mode.

The next job is not to add more infrastructure for its own sake.  
The next job is to use the existing feature layer to produce the first honest diagnostics, narrow the active research universe, and support the first conservative maker-quality studies.