# Current State

## Highlighted Updates

This document has been updated to reflect a repo-reality check confirming that diagnostics, tradability/active-universe triage, and the first conservative maker-markout scaffold are already implemented.

### New since the previous version
- Confirmed via repository inspection that tradability and active-universe artifacts are already implemented in code/test/CLI/script layers (no duplicate implementation required in this step).
- The dedicated diagnostics interpretation layer is now implemented under reporting as `build_tradability_report.py`.
- The current implemented chain is now:
  - metadata -> tokens -> raw books -> flat state -> frozen feature inputs -> feature set `v0_1` -> feature diagnostics -> market gating/tradability -> active universe
- The new tradability layer is callable from the CLI (`build-tradability-report`) and from a shell runner.
- The tradability layer now writes:
  - tradability JSON report,
  - tradability market-summary CSV with gating columns,
  - active-universe CSV (keep-only markets),
  - latest tradability manifest.
- Gating thresholds are now explicit and centralized for conservative keep/watch/exclude decisions.
- The focused tradability test passes (plus diagnostics test slice).
- The first conservative maker-markout scaffold is implemented as an experiment/reporting layer (row-level and market-level outputs + latest manifest).

### Outdated assumptions removed
- The next immediate task is no longer “implement diagnostics interpretation/gating”; that layer now exists.
- The current repo still does not need more ingestion scaffolding, more feature-builder scaffolding, or a new smoke experiment for this step.
- The next step should not be framed as adding another diagnostics layer; it is now using the new active universe for tradability narrowing and first conservative maker-markout scaffolding.
- Gating/tradability outputs are still first-pass triage artifacts, not alpha or production execution rules.

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

**Phase 1 — minimum data backbone plus stable feature set, diagnostics, tradability gating, and first conservative maker-markout scaffold implemented**

The project has moved beyond pure data plumbing and beyond the first reproducible feature stage.

Current reality:
- metadata universe refresh works,
- token IDs are being collected and stored,
- raw order-book snapshots are being collected,
- top-of-book state is being built from raw snapshots,
- the feature-job input set is frozen explicitly,
- a first stable feature set `v0_1` has been built successfully from those frozen inputs,
- a diagnostics layer on top of the stable feature set exists and runs successfully,
- a downstream tradability/gating layer now converts diagnostics into keep/watch/exclude plus active-universe outputs,
- and the maker-markout scaffold now produces first-pass adverse-selection diagnostics for active-universe triage.

This is still an early research-stage system, but it is no longer just a design document set, it is no longer only an ingestion/state project, and it is no longer waiting on its first reporting layer.

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

#### 6. Diagnostics reporting layer
Implemented and working:
- consumes the latest stable feature-set manifest,
- loads the current feature-set CSV,
- writes a diagnostics JSON summary,
- writes a market-summary CSV,
- writes a latest diagnostics manifest,
- is exposed through the CLI as `build-feature-diagnostics`,
- and is callable through `scripts/run_build_feature_diagnostics.sh`.

Current diagnostics coverage includes:
- total row count,
- stale row count and stale row fraction,
- null / missing spread count,
- non-positive spread count,
- wide-spread count using an explicit threshold,
- zero / empty top-size count,
- null imbalance count,
- null microprice count,
- repeated-hash diagnostics when `hash` exists,
- and market-level summary statistics.

Current market-summary outputs include:
- `market_id`
- `row_count`
- `stale_row_fraction`
- `median_spread`
- `p90_spread`
- `median_best_bid_size`
- `median_best_ask_size`
- `zero_or_empty_top_size_fraction`
- `repeated_hash_fraction`
- `mean_market_quality_score`
- `median_market_quality_score`

Current live implementation result:
- the latest successful diagnostics run processed `60` rows from the current stable feature set,
- found `26` stale rows,
- found stale-row fraction `0.43333333333333335`,
- found `0` missing-spread rows,
- found `0` non-positive-spread rows,
- found `0` wide-spread rows at threshold `0.1`,
- found `0` zero/empty top-size rows,
- found `0` null imbalance rows,
- found `0` null microprice rows,
- found `26` repeated-hash rows,
- and produced mean / median market-quality values without error.


#### 7. Tradability / gating layer
Implemented and working:
- consumes latest diagnostics manifest + diagnostics outputs + latest stable feature-set manifest,
- applies centralized conservative thresholds for `keep` / `watch` / `exclude`,
- computes a simple additive tradability score for first-pass ranking,
- writes a tradability market-summary CSV with gating columns,
- writes keep-only `active_universe_<feature_set_id>.csv`,
- writes tradability JSON report + latest tradability manifest,
- exposed through CLI `build-tradability-report`,
- callable via `scripts/run_build_tradability_report.sh`.

Current implementation note:
- this remains a reporting/triage layer and does not mutate diagnostics or stable feature-set artifacts.

#### 8. Conservative maker-markout scaffold
Implemented and working:
- consumes latest tradability manifest + active-universe CSV + latest feature-set manifest + stable feature CSV,
- applies explicit candidate-row selection (active universe only, valid IDs, spread > 0, non-stale, minimum quality),
- computes row-step forward midpoint markouts for passive buy/sell quote diagnostics,
- writes row-level markout CSV + market-summary CSV,
- writes experiment JSON + latest maker-markout manifest,
- exposed through CLI `build-maker-markout`,
- callable via `scripts/run_build_maker_markout.sh`.

Current implementation note:
- this is explicitly a conservative triage scaffold (not execution PnL, no queue/fill/fee model).

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
  - `run_build_feature_diagnostics.sh`
  - `run_build_tradability_report.sh`
  - `run_build_maker_markout.sh`
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
  - `reporting/`
    - `build_feature_diagnostics.py`
    - `build_tradability_report.py`
  - `experiments/`
    - `build_maker_markout_report.py`
- `tests/`
  - metadata refresh test
  - raw books collector test
  - books state builder test
  - feature input freeze test
  - feature set `v0_1` test
  - feature diagnostics test
  - tradability report test
  - maker markout report test
  - smoke test
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

### Diagnostics layer

#### Diagnostics JSON summary
Stored under:
- `data/features/polymarket/diagnostics/feature_diagnostics_<feature_set_id>.json`

This contains:
- run metadata,
- input feature manifest path,
- input feature CSV path,
- aggregate diagnostics summary,
- output paths.

#### Market-summary CSV
Stored under:
- `data/features/polymarket/diagnostics/feature_diagnostics_<feature_set_id>_market_summary.csv`

This contains market-level rollups for diagnostics and triage.

#### Latest diagnostics manifest
Stored under:
- `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`

This defines:
- the latest diagnostics run,
- the current feature-set ID,
- the input feature artifact,
- the diagnostics JSON path,
- the market-summary CSV path.

### Tradability / universe layer

#### Tradability JSON report
Stored under:
- `data/features/polymarket/universe/tradability_report_<feature_set_id>.json`

Contains:
- centralized threshold config used for this run,
- scoring formula notes,
- keep/watch/exclude counts,
- top keep markets and frequent exclusion reasons,
- output paths for this tradability run.

#### Tradability market-summary CSV
Stored under:
- `data/features/polymarket/universe/tradability_report_<feature_set_id>_market_summary.csv`

Contains market-level diagnostics + gating additions including:
- `gating_class`,
- `tradability_score`,
- `gating_reason`.

#### Active universe CSV
Stored under:
- `data/features/polymarket/universe/active_universe_<feature_set_id>.csv`

Contains keep-only markets for the next maker-markout step.

#### Latest tradability manifest
Stored under:
- `data/features/polymarket/universe/latest_tradability_manifest.json`

Defines the latest tradability run and pointers to tradability outputs.

---

## Immediate Next Tasks

The next concrete tasks should now be:

1. Confirm artifact hygiene decisions for diagnostics + tradability outputs:
   - keep intentional generated artifacts only,
   - avoid accidental cache/junk files in commits.

2. Interpret and calibrate gating behavior on real runs before broadening scope:
   - review keep/watch/exclude distributions,
   - review common exclusion reasons,
   - adjust thresholds only with explicit evidence.

3. Use keep-only active universe for conservative maker-markout iteration (not simulator expansion):
   - market-level first,
   - simple assumptions first,
   - no queue/fill/fee complexity jump yet.

4. Keep the implementation sequence conservative:
   - no duplicate ingestion work,
   - no duplicate feature-builder scaffolding,
   - no extra diagnostics layer duplication,
   - no websocket/event enrichment in this immediate step.

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
- The diagnostics layer exists in the repo and is wired into the CLI.
- The diagnostics shell runner exists and runs successfully.
- The diagnostics job successfully consumes the latest stable feature-set manifest and writes all expected outputs.
- The tradability/gating layer exists in the repo and is wired into the CLI.
- The tradability shell runner exists.
- The tradability job consumes diagnostics + feature-set manifests and writes tradability summary + active-universe outputs.
- The diagnostics test passes.
- The focused tradability + diagnostics test subset passes.
- The broader feature/smoke test slice passes.
- GitHub `main` already contains the diagnostics implementation and the local Debian checkout matched the targeted diagnostics files without extra patching.
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
- The current stable feature artifact is sufficient to support a first diagnostics reporting layer.
- Diagnostics outputs are sufficient to drive a first explicit keep/watch/exclude market gating layer and keep-only active universe artifact.

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

The current diagnostics+gating step now has an explicit implementation rule:
- use diagnostics as immutable input and build gating as a downstream reporting layer,
- without re-adding ingestion layers, feature-builder scaffolding, duplicate diagnostics layers, or duplicate smoke logic.

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

### Diagnostic + gating sufficiency of the first reporting layer
- whether the current stale / repeated-hash patterns are informative enough to keep current gating classes stable over time,
- whether the spread/quality/row-count thresholds are calibrated well enough for conservative universe narrowing,
- whether current gating reasons are compact and interpretable enough for operational triage,
- whether the simple tradability score is adequate for first-pass ranking,
- and whether the next useful delta after this should be threshold calibration or maker-markout iteration.

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
- duplicate ingestion / feature scaffolding while the current stable pipeline already exists,
- and making the server workflow depend on locally stored Project context files.
