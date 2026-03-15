# Current State

## Highlighted Updates

This document has been updated to reflect the server-side reproducibility inspection after the maker-markout interpretation memo pass.

### New since the previous version
- Ran a small server-side reproducibility inspection instead of a new implementation step.
- Confirmed local repo reality on Debian:
  - branch = `main`
  - `HEAD = 8980f88`
  - repo dirt is currently cache junk only, not intentional code work:
    - `src/pmre/__pycache__/cli.cpython-311.pyc`
    - untracked `__pycache__` files under `experiments/`, `features/`, and `reporting/`
- Detected that the working-tree versions of:
  - `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`
  - `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
  had been pointing to missing newer artifacts from the longer bounded sample.
- Restored those two latest-pointer files back to coherent tracked artifacts.
- Confirmed that the current tracked latest artifacts now resolve successfully to the older coherent bounded sample:
  - freeze id = `20260311T214230Z__20260312T133004Z`
  - books-state row count = `60`
  - feature-set row count = `60`
- Confirmed that the current tracked latest checkout is missing:
  - `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`
- Confirmed that this missing diagnostics manifest currently blocks both:
  - default-threshold tradability rerun,
  - calibrated-threshold tradability rerun,
  - and therefore any current-checkout maker-markout rerun.
- Confirmed that the preserved runtime snapshot under:
  - `~/pmre_runtime_snapshots/20260313T102233Z/`
  contains the longer bounded-sample runtime truth, including:
  - local calibration config,
  - 120-row feature-set artifacts,
  - diagnostics manifest,
  - tradability outputs,
  - active-universe CSV,
  - maker-markout outputs,
  - and a preserved note matching the documented calibrated keep set and maker-markout summary.
- Confirmed preserved snapshot facts for the longer bounded sample:
  - calibrated keep IDs:
    - `540818`
    - `540819`
    - `540844`
    - `540881`
  - maker-markout scaffold facts:
    - `selected_rows = 44`
    - `market_summary_rows = 4`
    - row-step horizons = `[1, 2, 5]`

### Outdated assumptions removed
- Do not assume the current tracked latest checkout still corresponds to the longer bounded 120-row sample.
- Do not assume that the current checkout can rerun tradability from latest pointers without first restoring or regenerating diagnostics artifacts.
- Do not describe the memo-basis 120-row calibrated result as currently reproducible from tracked latest as-is.
- Do not treat the restored tracked latest state and the preserved longer-sample runtime snapshot as the same runtime basis.
- Do not treat current repo state as fully clean; cache junk remains, even though the manifest-pointer issue has been resolved locally.

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

**Phase 1 — minimum data backbone, stable feature set, diagnostics, tradability gating, and conservative maker-markout scaffold all exist; preserved longer-sample runtime truth exists, but current tracked latest reproducibility is partially blocked**

Current reality:
- metadata universe refresh works,
- token IDs are collected and stored,
- raw order-book snapshots are collected,
- top-of-book state is built from raw snapshots,
- feature-job inputs are frozen explicitly,
- a stable feature set `v0_1` exists,
- a diagnostics layer exists,
- a tradability / gating layer exists,
- a conservative maker-markout scaffold exists,
- a longer bounded sample was previously validated locally with 120 rows and non-empty calibrated keep set,
- those longer-sample calibrated artifacts were preserved outside the repo tree under `~/pmre_runtime_snapshots/20260313T102233Z/`,
- the current tracked latest checkout has been restored to a coherent older 60-row freeze / feature-set pair,
- and the current tracked latest checkout cannot yet rerun tradability because the latest diagnostics manifest is missing.

This remains an early research-stage system. The first maker-markout result still remains scaffold-level triage under explicit simplifying assumptions. In addition, current reproducibility must distinguish between:
- preserved longer-sample runtime truth,
- and current tracked-latest checkout truth.

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
A minimal GitHub-centered workflow is established:
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
- and it currently targets a bounded subset of tokens for early research.

#### 3. State builder
Implemented and working:
- reads raw books JSONL,
- maps book snapshots back to token / market metadata present in the request envelope,
- extracts best bid and best ask,
- computes midpoint and spread,
- writes flat state CSV,
- writes a state manifest.

Important implementation detail:
- raw `bids` and `asks` arrays are not assumed to be pre-sorted,
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

Important feature semantics now in use:
- `spread = best_ask_price - best_bid_price`
- `midpoint = mid_price` if already present, otherwise recomputed
- `top_of_book_imbalance = (best_bid_size - best_ask_size) / (best_bid_size + best_ask_size)` when the denominator is positive
- `microprice_proxy = (best_ask_price * best_bid_size + best_bid_price * best_ask_size) / (best_bid_size + best_ask_size)` when the denominator is positive
- `last_trade_minus_mid = last_trade_price - midpoint` when both exist
- `staleness_flag` is a first-pass diagnostic flag
- `market_quality_score` is an additive/subtractive first-pass diagnostic score, not a final research metric

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
- wide-spread count,
- zero / empty top-size count,
- null imbalance count,
- null microprice count,
- repeated-hash diagnostics when `hash` exists,
- market-level summary statistics.

Current runtime note:
- diagnostics outputs were validated on the preserved longer bounded sample,
- but the current tracked latest checkout is missing `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`,
- which is now the immediate prerequisite blocker for rerunning tradability from tracked latest.

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
- threshold overrides are read from `tradability_report.thresholds`.

Validated runtime truth:
- on the preserved longer bounded sample:
  - books-state row count = `120`
  - feature-set row count = `120`
- default thresholds produced:
  - total markets = `10`
  - `keep = 0`
  - `watch = 4`
  - `exclude = 6`
- an explicit local calibration override with:
  - `min_row_count_keep = 12`
  - `max_repeated_hash_fraction_keep = 0.5`
  produced:
  - total markets = `10`
  - `keep = 4`
  - `watch = 0`
  - `exclude = 6`
- calibrated keep IDs were:
  - `540818`
  - `540819`
  - `540844`
  - `540881`

Current tracked-latest note:
- the current tracked latest freeze / feature-set pair is coherent,
- but it is the older 60-row basis, not the preserved 120-row memo basis,
- and current tradability reruns are blocked until diagnostics latest-manifest truth is restored.

#### 8. Conservative maker-markout scaffold
Implemented and locally validated.

Implemented and working:
- `src/pmre/experiments/build_maker_markout_report.py` exists,
- the CLI exposes `build-maker-markout`,
- `scripts/run_build_maker_markout.sh` runs the scaffold,
- `tests/test_build_maker_markout.py` exists,
- the scaffold consumes the latest tradability manifest + active-universe CSV + latest feature-set manifest,
- writes a maker-markout report JSON,
- writes per-row markout CSV output,
- writes per-market summary CSV output,
- and writes a latest maker-markout manifest.

Current implementation notes:
- this is explicitly a conservative triage scaffold,
- not execution PnL,
- and it does not model queue position, fees, fill probability, or passive execution mechanics.

Validated runtime truth:
- the preserved longer-sample calibrated maker-markout run produced:
  - `selected_rows = 44`
  - `drop_not_in_active_universe = 72`
  - `drop_stale = 4`
  - `market_summary_rows = 4`
  - row-step horizons `[1, 2, 5]`

Current tracked-latest note:
- current maker-markout rerun from tracked latest is blocked downstream because tradability cannot currently rerun from tracked latest.

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
- `src/pmre/`
  - `config.py`
  - `cli.py`
  - `ingest/`
  - `state/`
  - `features/`
  - `reporting/`
  - `experiments/`
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

This structure is real and should be preserved unless there is a strong reason to change it.

---

## Current Data Products

### Metadata layer

#### Raw metadata pages
Stored under:
- `data/raw/polymarket/metadata/markets_pages/`

#### Metadata manifest and checkpoint
Stored under:
- `data/raw/polymarket/metadata/metadata_refresh_manifest.json`
- `data/raw/polymarket/metadata/metadata_refresh_checkpoint.json`

#### Canonical market table
Stored under:
- `data/reference/polymarket/markets.csv`

#### Canonical token table
Stored under:
- `data/reference/polymarket/tokens.csv`

### Raw books layer

#### Raw books JSONL
Stored under:
- `data/raw/polymarket/books/books_run_<run_id>.jsonl`

#### Raw books manifest
Stored under:
- `data/raw/polymarket/books/books_run_<run_id>_manifest.json`
- `data/raw/polymarket/books/latest_books_manifest.json`

### State layer

#### Flat books state CSV
Stored under:
- `data/state/polymarket/books_state_<run_id>.csv`

#### State manifest
Stored under:
- `data/state/polymarket/books_state_<run_id>_manifest.json`
- `data/state/polymarket/latest_books_state_manifest.json`

### Feature input freeze layer

#### Frozen feature-input bundle
Stored under:
- `data/features/polymarket/input_freezes/freeze_<freeze_id>/`

#### Latest feature-input freeze manifest
Stored under:
- `data/features/polymarket/input_freezes/latest_feature_input_freeze_manifest.json`

Current tracked latest:
- resolves to coherent older freeze `20260311T214230Z__20260312T133004Z`

Preserved longer-sample snapshot:
- contains a separate later freeze basis for the memo-era 120-row run under `~/pmre_runtime_snapshots/20260313T102233Z/`

### Feature layer

#### Stable feature set CSV
Stored under:
- `data/features/polymarket/feature_sets/feature_set_v0_1_<freeze_id>.csv`

#### Feature-set manifest and schema
Stored under:
- `data/features/polymarket/feature_sets/feature_set_v0_1_<freeze_id>_manifest.json`
- `data/features/polymarket/feature_sets/latest_feature_set_manifest.json`
- `data/features/polymarket/feature_sets/feature_set_v0_1_schema.json`

Current tracked latest:
- resolves to coherent older feature set with `row_count = 60`

Preserved longer-sample snapshot:
- contains a later feature set with `row_count = 120`

### Diagnostics layer

#### Diagnostics JSON summary
Stored under:
- `data/features/polymarket/diagnostics/feature_diagnostics_<feature_set_id>.json`

#### Market-summary CSV
Stored under:
- `data/features/polymarket/diagnostics/feature_diagnostics_<feature_set_id>_market_summary.csv`

#### Latest diagnostics manifest
Stored under:
- `data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`

Current tracked-latest note:
- this file is currently missing in the live checkout

Preserved longer-sample snapshot:
- contains a preserved latest diagnostics manifest under:
  - `~/pmre_runtime_snapshots/20260313T102233Z/data/features/polymarket/diagnostics/latest_feature_diagnostics_manifest.json`

### Tradability / universe layer

#### Tradability JSON report
Stored under:
- `data/features/polymarket/universe/tradability_report_<feature_set_id>.json`

#### Tradability market-summary CSV
Stored under:
- `data/features/polymarket/universe/tradability_report_<feature_set_id>_market_summary.csv`

#### Active universe CSV
Stored under:
- `data/features/polymarket/universe/active_universe_<feature_set_id>.csv`

Validated preserved longer-sample calibrated result:
- active universe size = `4`
- keep IDs:
  - `540818`
  - `540819`
  - `540844`
  - `540881`

#### Latest tradability manifest
Stored under:
- `data/features/polymarket/universe/latest_tradability_manifest.json`

Current tracked-latest note:
- current rerun did not produce a fresh latest tradability manifest because tradability is blocked by missing diagnostics latest-manifest truth

Preserved longer-sample snapshot:
- contains:
  - `data/features/polymarket/universe/latest_tradability_manifest.json`
  - calibrated tradability JSON report
  - calibrated tradability market-summary CSV
  - calibrated active-universe CSV

### Maker-markout experiment layer

#### Maker-markout report JSON
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>.json`

#### Maker-markout rows CSV
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>_rows.csv`

#### Maker-markout market-summary CSV
Stored under:
- `data/experiments/polymarket/maker_markout/maker_markout_<feature_set_id>_market_summary.csv`

#### Latest maker-markout manifest
Stored under:
- `data/experiments/polymarket/maker_markout/latest_maker_markout_manifest.json`

Validated preserved longer-sample result:
- selected rows = `44`
- market summary rows = `4`
- horizons = `[1, 2, 5]`

Current tracked-latest note:
- no fresh rerun was produced from the current checkout because maker-markout depends on tradability output, which is currently blocked by missing diagnostics latest-manifest truth

---

## Immediate Next Tasks

The next concrete tasks should now be:

1. Restore or regenerate diagnostics latest-manifest truth for the current tracked latest checkout.
2. Keep current-tracked reproducibility separate from preserved longer-sample reproducibility.
3. Re-run default and calibrated tradability only after diagnostics latest-manifest truth is present.
4. Re-run maker-markout only if calibrated tradability reproduces successfully.
5. Keep calibrated thresholds as experimental local override unless deliberately promoted later.
6. Do not overinterpret preserved positive maker-markout scaffold output as execution evidence.

---

## What Is Validated

At the current stage, the following should be treated as validated.

### Project-level validation
- A modular, execution-aware architecture is the correct design target.
- The first sprint should focus on data trust, execution realism, and cheap falsification rather than aggressive implementation.
- Maker-first microstructure remains the highest-priority research direction among the original candidates.

### Implementation validation
- The Debian project skeleton is usable.
- Metadata refresh runs successfully with resumable progress.
- Canonical market and token tables can be built from live Polymarket metadata.
- Token IDs from the metadata table can be used to collect real CLOB book data.
- Raw book snapshots can be preserved in append-only JSONL.
- A normalized top-of-book state table can be built from raw book snapshots.
- The feature job input boundary can be frozen reproducibly.
- A stable feature-set version `v0_1` can be built from the frozen input bundle.
- The diagnostics layer exists in the repo and is wired into the CLI.
- The tradability / gating layer exists and is wired into the CLI.
- The maker-markout scaffold exists and is wired into the CLI.
- The longer bounded sample, calibrated tradability result, and first maker-markout scaffold run were preserved successfully outside the repo tree.
- Latest feature-freeze and feature-set pointers in the live checkout were restored to coherent tracked artifacts after an inconsistent working-tree state was detected.

### Data-contract validation
- `market_id` is usable in the current backbone.
- Feature-set manifests, tradability manifests, and maker-markout manifests are sufficient to reconstruct preserved runtime truth when those artifacts are present.
- Current tracked latest freeze / feature-set pointers now resolve to existing artifacts.

### Process validation
- Small server-side verification can reveal the difference between:
  - preserved runtime truth,
  - tracked latest checkout truth,
  - and accidental working-tree drift.
- Preserving experimental calibrated artifacts outside the repo tree is operationally useful.
- Latest-pointer files should be checked by actual path existence, not only by apparent recency.

---

## What Is Not Yet Validated

### Event linkage
- Event-level enrichment is not yet part of the trusted backbone.

### Market-state truth beyond top of book
- Full-depth state, queue state, and hidden liquidity are not modeled.

### Execution realism
- Queue position is not modeled.
- Fees are not modeled.
- Fill probability is not modeled.
- Passive execution mechanics are not modeled.

### Signal validity
- The first maker-markout scaffold result is not execution PnL.
- The first maker-markout scaffold result is not yet robust across broader windows or regimes.
- Preserved longer-sample positive symmetric markouts may still be heavily shaped by scaffold assumptions.

### Operational robustness
- Current tracked latest checkout is not yet fully rerunnable end-to-end because diagnostics latest-manifest truth is missing.
- Exact rerun of the memo-basis 120-row result has not yet been reproduced from the current tracked latest checkout.

### Diagnostic + gating sufficiency of the first reporting layer
- Current gating may still be brittle across other bounded windows.
- Default-threshold versus calibrated-threshold behavior still needs reproducibility confirmation on a runnable checkout.

### Maker-markout readiness
- Current maker-markout remains a conservative descriptive scaffold.
- It is not yet sufficient evidence for deployment, PnL claims, or threshold promotion.

---

## What Remains Speculative

### Direction 1 — maker-first microstructure
Still the leading direction, but real executable edge remains unproven.

### Direction 2 — crypto fair value
Still plausible later, but not the immediate focus.

### Direction 3 — displayed-price / stale-anchor
Still plausible later, but not the immediate focus.

---

## What Has Been Rejected or Explicitly Deprioritized

- Duplicating ingestion work already present in the repo.
- Duplicating feature-builder scaffolding already present in the repo.
- Duplicating diagnostics work already present in the repo.
- Treating maker-markout scaffold output as execution PnL.
- Promoting calibrated thresholds into tracked baseline config during this phase.
- Branching into websocket ingestion, event enrichment, stale-anchor work, crypto fair-value work, or simulator expansion during this specific reproducibility pass.
