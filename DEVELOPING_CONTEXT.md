# Developing Context

## Current development focus

Build the first diagnostic research loop on top of the implemented backbone:

metadata -> tokens -> raw books -> books state -> frozen feature inputs -> feature set `v0_1`

The immediate focus is no longer ingestion plumbing.  
The immediate focus is diagnostics and first research utilities using the existing frozen/state/feature artifacts.

## What was decided in this chat

- Step 2 began with a strict feature-job input freeze.
- The feature job is allowed to use only:
  - latest books state manifest,
  - corresponding `books_state_<run_id>.csv`,
  - `markets.csv`,
  - `tokens.csv`.
- Do **not** add:
  - websocket logic,
  - event enrichment,
  - simulator assumptions.
- A first stable feature schema now exists:
  - `feature_set_version = v0_1`
- `v0_1` computes only:
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

## Current coding task

Build the first **data-quality diagnostics job** on top of `feature_set_v0_1`.

This should use the latest built feature-set artifact and produce a simple diagnostic output for:
- spread sanity / pathological spread,
- stale row frequency,
- one-sided / empty-book behavior,
- repeated-hash behavior,
- missing `last_trade_price`,
- market-quality summaries and ranking.

## Important implementation constraints and assumptions

- `STATE.md` is the source of full project context. Use it for anything broader.
- Keep new code modular and aligned with the current repo layout.
- Prefer copy-paste-ready bash and Python.
- Use the existing config / CLI / runner pattern.
- Keep the feature layer diagnostic and conservative.
- Do not silently widen the feature schema.
- Do not treat `event_id` as reliable.
- Current live collection path is polling, not websocket.
- Current state layer is top-of-book snapshot state, not reconciled orderbook state.
- The feature builder is already compatible with the real frozen-input manifest shape.
- The current `market_quality_score` is an additive/subtractive first-pass diagnostic score, not a normalized final metric.
- The current `staleness_flag` includes:
  - missing bid or ask,
  - `spread <= 0`,
  - timestamp-age threshold,
  - repeated hash too long,
  - missing `last_trade_price` too many consecutive times.

## Immediate next steps

1. Add a diagnostics module that consumes the latest feature-set manifest.
2. Produce a diagnostics artifact with row-level counts and market-level summaries.
3. Add a CLI command and shell runner for the diagnostics job.
4. Add a small test for the diagnostics job.
5. After diagnostics, build the first tradability report / narrowed research universe.