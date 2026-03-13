# Current State

## Highlighted Updates

This document has been updated to reflect the current Debian validation pass through calibrated tradability and the first successful maker-markout scaffold run, followed by a server-side repo/runtime hygiene pass that preserved the calibrated runtime truth outside the repo tree.

### New since the previous version
- Ran a slightly longer bounded polling sample by increasing raw-books iterations from `3` to `6` while keeping the same bounded token subset and polling cadence.
- Validated refreshed downstream artifacts on that bounded sample:
  - raw books manifest with `jsonl_line_count = 12`,
  - books-state manifest with `row_count = 120`,
  - refreshed feature-input freeze,
  - refreshed stable feature set `v0_1` with `row_count = 120`,
  - refreshed diagnostics outputs.
- Validated tradability on the longer bounded sample under default thresholds:
  - total markets = `10`,
  - `keep = 0`,
  - `watch = 4`,
  - `exclude = 6`,
  - active universe size = `0`.
- Confirmed that the previous hard blocker `row_count_too_low` no longer dominated after the longer sample; the gating result moved into a near-miss calibration regime centered on `row_count_watch` plus repeated-hash constraints.
- Inspected the four watch markets directly and confirmed they were blocked only by `row_count_watch|repeated_hash_watch` with otherwise tight spreads and acceptable quality scores.
- Confirmed that tradability threshold overrides are read from `tradability_report.thresholds`, not from flat keys under `tradability_report`.
- Validated a conservative local calibration override with:
  - `min_row_count_keep = 12`,
  - `max_repeated_hash_fraction_keep = 0.5`.
- Validated calibrated tradability outputs on real local artifacts:
  - total markets = `10`,
  - `keep = 4`,
  - `watch = 0`,
  - `exclude = 6`,
  - active universe size = `4`.
- Confirmed the calibrated keep set:
  - `540818`,
  - `540819`,
  - `540844`,
  - `540881`.
- Confirmed that the local checkout was previously behind `origin/main` and missing the maker-markout scaffold even though it already existed upstream.
- Synced local `main` to `origin/main`, validated local presence of the maker-markout scaffold, and confirmed:
  - `src/pmre/experiments/build_maker_markout_report.py`,
  - CLI wiring `build-maker-markout`,
  - `scripts/run_build_maker_markout.sh`,
  - `tests/test_build_maker_markout.py`.
- Successfully ran the conservative maker-markout scaffold on the calibrated active universe.
- Produced maker-markout outputs:
  - latest maker-markout manifest,
  - report JSON,
  - per-row CSV,
  - per-market summary CSV.
- Current maker-markout scaffold result on the calibrated active universe:
  - selected rows = `44`,
  - stale rows dropped = `4`,
  - market summary rows = `4`,
  - row-step horizons = `[1, 2, 5]`,
  - all four market summaries show positive populated mean buy/sell markouts and zero adverse fractions under the scaffold assumptions.
- Completed a repo/runtime hygiene pass on the Debian checkout:
  - backed up the calibrated runtime artifacts and local calibration config outside the repo tree under `~/pmre_runtime_snapshots/20260313T102233Z/`,
  - moved local-only configs out of `configs/` into `~/pmre_local_configs/`,
  - removed generated runtime artifacts and cache junk from the working tree,
  - and cleared diagnostics-manifest conflict residue.
- Current local repo state after cleanup:
  - no untracked generated artifacts remain,
  - no unmerged entries remain,
  - remaining intentional repo dirt is limited to staged updates of:
    - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`,
    - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`.

### Outdated assumptions removed
- The active universe is no longer empty under the currently validated calibrated thresholds.
- The maker-markout scaffold is no longer merely assumed upstream; it is now present locally, CLI-wired, and has been run successfully on the Debian server.
- The immediate blocker is no longer “obtain any non-empty keep set before markout.” That hurdle has been cleared.
- The current calibrated tradability result should not be described as the default-threshold outcome; the non-empty active universe depends on an explicit local tradability override.
- The calibrated runtime truth does not need to remain in a dirty repo tree; it has now been preserved outside the checkout and should remain clearly separated from tracked default config unless intentionally promoted.

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

**Phase 1 — minimum data backbone plus stable feature set, diagnostics, tradability gating, and first conservative maker-markout scaffold validated; calibration and interpretation remain explicit**

Current reality:
- metadata universe refresh works,
- token IDs are being collected and stored,
- raw order-book snapshots are being collected,
- top-of-book state is being built from raw snapshots,
- the feature-job input set is frozen explicitly,
- a first stable feature set `v0_1` has been built successfully from those frozen inputs,
- a diagnostics layer on top of the stable feature set exists and runs successfully,
- a downstream tradability / gating layer converts diagnostics into keep/watch/exclude plus active-universe outputs,
- a slightly longer bounded sample materially improved row count from `60` to `120`,
- default tradability thresholds on that longer sample still produced `keep = 0`, `watch = 4`, `exclude = 6`,
- an explicit conservative local calibration override produced a non-empty keep-only active universe of size `4`,
- the conservative maker-markout scaffold has now been run successfully on that calibrated active universe,
- and a cleanup pass has preserved the validated calibrated runtime artifacts outside the repo tree while reducing the checkout to a near-clean state.

This remains an early research-stage system. The current maker-markout result is still a triage scaffold under explicit simplifying assumptions, but the project is no longer blocked before its first markout experiment.

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
- the latest successful diagnostics run on the longer bounded sample processed `120` rows from the current stable feature set,
- refreshed the diagnostics JSON summary,
- refreshed the diagnostics market-summary CSV,
- refreshed the latest diagnostics manifest,
- and provided the market-level inputs used by the calibrated tradability pass without error.

#### 7. Tradability / gating layer
Implemented and working:
- consumes latest diagnostics manifest + diagnostics outputs + latest stable feature-set manifest,
- applies centralized conservative thresholds for `keep` / `watch` / `exclude`,
- computes a simple additive tradability score for first-pass ranking,
- writes a tradability market-summary CSV with gating columns,
- writes keep-only `active_universe_<feature_set_id>.csv`,
- writes tradability JSON report + latest tradability manifest,
- is exposed through CLI `build-tradability-report`,
- and is callable via `scripts/run_build_tradability_report.sh`.

Current implementation notes:
- this remains a reporting / triage layer and does not mutate diagnostics or stable feature-set artifacts.
- threshold overrides are currently read from `tradability_report.thresholds`.

Current local validation result:
- tradability runs successfully on the current local artifacts,
- the longer bounded sample increased feature-set row count from `60` to `120`,
- default thresholds on that longer sample produced:
  - total markets = `10`,
  - `keep = 0`,
  - `watch = 4`,
  - `exclude = 6`,
  - active-universe size = `0`,
- the near-miss watch set was driven by `row_count_watch|repeated_hash_watch`,
- an explicit local calibration override with `min_row_count_keep = 12` and `max_repeated_hash_fraction_keep = 0.5` produced:
  - total markets = `10`,
  - `keep = 4`,
  - `watch = 0`,
  - `exclude = 6`,
  - active-universe size = `4`,
- and the current non-empty active universe should therefore be treated as validated under calibrated thresholds, not under untouched base defaults.

#### 8. Conservative maker-markout scaffold
Implemented and locally validated.

Implemented and working:
- `src/pmre/experiments/build_maker_markout_report.py` exists in the synced local checkout,
- the CLI exposes `build-maker-markout`,
- `scripts/run_build_maker_markout.sh` runs the scaffold,
- `tests/test_build_maker_markout.py` exists upstream and is present locally,
- the scaffold consumes the latest tradability manifest + active-universe CSV + latest feature-set manifest,
- writes a maker-markout report JSON,
- writes per-row markout CSV output,
- writes per-market summary CSV output,
- and writes a latest maker-markout manifest.

Current implementation notes:
- this is explicitly a conservative triage scaffold,
- not execution PnL,
- and it does not model queue position, fees, fill probability, or passive execution mechanics.

Current local validation result:
- the maker-markout scaffold ran successfully on the Debian server,
- it consumed the calibrated keep-only active universe of `4` markets,
- it selected `44` rows after dropping `72` rows not in the active universe and `4` stale rows,
- it produced `4` market summaries,
- it used row-step horizons `[1, 2, 5]`,
- and the current summary outputs show positive populated mean buy/sell markouts with zero adverse fractions under the scaffold assumptions.

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
    - `maker_markout_smoke.py`
    - `build_maker_markout_report.py`
- `tests/`
  - metadata refresh test
  - raw books collector test
  - books state builder test
  - feature input freeze test
  - feature set `v0_1` test
  - feature diagnostics test
  - tradability report test
  - maker-markout scaffold test
  - smoke test
- `data/`
  - `raw/`
  - `reference/`
  - `state/`
  - `features/`
  - `experiments/`

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

Current local validation result:
- the file is being written correctly,
- the default-threshold longer-sample run still produced a header-only CSV,
- but the latest calibrated local validation run produced `4` keep markets:
  - `540818`,
  - `540819`,
  - `540844`,
  - `540881`.

#### Latest tradability manifest
Stored under:
- `data/features/polymarket/universe/latest_tradability_manifest.json`

Defines the latest tradability run and pointers to tradability outputs.

Current local note:
- the latest calibrated tradability manifest and outputs were validated locally,
- used as input for the first maker-markout scaffold pass,
- and then backed up outside the repo tree during hygiene cleanup because the calibrated thresholds remain experimental.

### Maker-markout experiment layer

#### Maker-markout report JSON
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>.json`

Contains:
- run metadata,
- input manifest paths,
- horizon configuration,
- selection counts,
- explicit scaffold assumptions,
- and output paths.

#### Maker-markout rows CSV
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>_rows.csv`

Contains row-level snapshot-based markout fields including:
- buy/sell quote prices,
- future mids at configured horizons,
- buy/sell markouts,
- market quality score,
- spread,
- midpoint,
- top-of-book sizes,
- market and token identifiers.

#### Maker-markout market-summary CSV
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>_market_summary.csv`

Contains per-market rollups including:
- `row_count`,
- `mean_spread`,
- `mean_market_quality_score`,
- mean buy/sell markouts by horizon,
- adverse buy/sell markout fractions.

#### Latest maker-markout manifest
Stored under:
- `data/experiments/polymarket/maker_markout/latest_maker_markout_manifest.json`

Defines the latest maker-markout scaffold run and pointers to its outputs.

Current local validation result:
- the latest maker-markout run selected `44` rows,
- covered `4` markets,
- used row-step horizons `[1, 2, 5]`,
- produced populated market summaries for all `4` calibrated keep markets,
- and those runtime outputs were backed up outside the repo tree during hygiene cleanup rather than left as accidental tracked state.

---

## Immediate Next Tasks

The next concrete tasks should now be:

1. Update tracked project context to reflect the current runtime truth and cleanup result:
   - longer bounded sample validated,
   - calibrated non-empty active universe validated,
   - maker-markout scaffold present locally and run successfully,
   - repo/runtime hygiene pass completed,
   - and the remaining staged manifest-pointer changes called out explicitly.

2. Resolve the remaining staged latest-manifest updates deliberately:
   - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`,
   - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`,
   - either restore them to tracked default truth or commit them intentionally together with the matching documentation.

3. Interpret the first maker-markout scaffold outputs conservatively:
   - per-market mean buy/sell markouts,
   - adverse fractions,
   - missing horizon coverage for some markets,
   - and the extent to which the current positive symmetric markouts may be scaffold artifacts versus useful triage signal.

4. Keep the calibrated tradability thresholds as an experimental local override unless there is a deliberate decision to promote them into a tracked config path.

5. Keep the implementation sequence conservative:
   - no duplicate ingestion work,
   - no duplicate feature-builder scaffolding,
   - no extra diagnostics layer duplication,
   - no websocket / event enrichment in this immediate step,
   - and no further server/runtime work unless the remaining manifest pointers prove inconsistent with the documented runtime truth.

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
- The tradability / gating layer exists locally and runs successfully on the Debian server.
- The tradability shell runner exists.
- The tradability job consumes diagnostics + feature-set manifests and writes tradability summary + active-universe outputs.
- The longer bounded polling sample and full downstream rebuild succeed on the Debian server.
- The current default-threshold tradability output is structurally correct even when the active universe is empty.
- The local synced checkout now contains the upstream maker-markout scaffold.
- The maker-markout shell runner exists.
- The maker-markout CLI wiring exists.
- The maker-markout scaffold successfully consumes the current latest tradability + feature-set artifacts and writes all expected maker-markout outputs.
- The repo/runtime hygiene pass successfully preserved the calibrated runtime artifacts outside the repo tree while removing generated artifacts, cache junk, and local-only configs from the checkout.

### Data-contract validation
- `market_id` is usable in the current backbone.
- `condition_id` is usable in the current backbone.
- `token_id` is usable in the current backbone.
- `outcome` to `token_id` mapping is usable in the current backbone.
- The current state artifact is sufficient to support a first stable diagnostic feature layer.
- The current stable feature artifact is sufficient to support a first diagnostics reporting layer.
- Diagnostics outputs are sufficient to drive a first explicit keep/watch/exclude market gating layer and keep-only active-universe artifact.
- The longer bounded sample is sufficient to move the gating result from hard row-count exclusion into a near-miss calibration regime.
- The current calibrated threshold override is sufficient to produce a non-empty keep-only active universe.
- The current active-universe artifact is sufficient input for the conservative maker-markout scaffold.

### Process validation
- Inspecting local repo reality before changing code is the correct operating rule.
- GitHub remains the source of truth for code.
- Local server artifacts are the runtime truth for validation.
- Project context files are useful for continuity, but local server flow should not depend on them existing in the checkout.
- Repo hygiene must be handled before rebasing a dirty local branch.
- Experimental runtime artifacts should be backed up outside the repo tree before cleanup rather than left as ambiguous tracked state.
- Experimental local configs should remain outside tracked `configs/` unless intentionally promoted.

---

## What Is Not Yet Validated

The following are still not validated.

### Event linkage
- whether event-level enrichment is necessary for the next useful research delta,
- whether event grouping changes the first-pass microstructure conclusions materially.

### Market-state truth beyond top of book
- whether top-of-book-only state is sufficient for the first maker / toxicity studies,
- whether deeper ladder reconstruction is needed before markout work becomes meaningful.

### Execution realism
- queue position,
- passive fill probability,
- cancellation timing,
- fees / rebates,
- realized maker PnL under realistic assumptions.

### Signal validity
- whether any current microstructure feature family produces genuine edge,
- whether any tradability ranking survives beyond triage usefulness.

### Operational robustness
- robustness of the bounded polling collector across longer runs,
- how stable diagnostics / gating outputs remain over larger samples and more markets.

### Diagnostic + gating sufficiency of the first reporting layer
- whether the current calibrated thresholds generalize beyond this single bounded sample,
- whether spread / quality / row-count / repeated-hash thresholds are calibrated well enough for conservative universe narrowing,
- whether current gating reasons remain compact and interpretable over additional runs,
- whether the simple tradability score is adequate for first-pass ranking,
- whether the calibrated keep set persists under a slightly larger sample or under tracked config rather than a local override,
- and whether further threshold work should remain limited to calibration rather than architecture changes.

### Maker-markout readiness
- whether the current positive symmetric snapshot-based markouts are informative beyond scaffold sanity checking,
- whether missing `h5` coverage for some markets materially limits interpretation,
- whether the current zero adverse fractions are robust or mostly a consequence of the scaffold assumptions,
- and how much of the present result survives once more realistic execution assumptions are introduced.

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
