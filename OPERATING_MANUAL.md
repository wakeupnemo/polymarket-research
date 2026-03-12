# Operating Manual

## Purpose of This Document

This manual defines how the Polymarket Research Engine project is run in practice.

Its purpose is to keep the work:
- rigorous,
- execution-aware,
- modular,
- updateable,
- and resistant to false discovery.

This is the default operating protocol for future iterations unless explicitly revised.

---

## Core Working Principles

### 1. Start with the smallest meaningful next step
Every task should be reduced to the smallest experiment or implementation step that can generate meaningful information.

Prefer:
- one reliable metric over ten vague ones,
- one falsification test over one more theory discussion,
- one working module over an ambitious unfinished system.

### 2. Falsification comes before expansion
Before improving an idea, try to kill it.

A good workflow asks:
- What would make this hypothesis fail quickly?
- What data limitation could make this conclusion weak?
- What execution assumption is doing the real work?

### 3. Never mix maker and taker logic
Maker and taker paths must be designed, simulated, and evaluated separately.

Do not merge them into one “signal quality” concept, because:
- fill mechanics differ,
- costs differ,
- adverse selection differs,
- and apparent alpha often survives in one path and dies in the other.

### 4. Separate raw signal from executable signal
Every result should distinguish between:
- **raw signal** — statistical pattern in prices or state,
- **execution-feasible signal** — signal that can realistically be entered,
- **post-cost signal** — signal that survives spread, fees, slippage, and fill uncertainty.

A pattern that fails this separation is not ready for implementation.

### 5. Prefer simple baselines first
Before adding model complexity, test the simplest plausible version.

Examples:
- simple diffusion baseline before richer fair-value modeling,
- simple queue bounds before sophisticated queue inference,
- simple event study before complex predictive modeling.

Complexity is allowed only after simple versions earn their keep.

### 6. State uncertainty explicitly
Every conclusion should make clear what is:
- validated,
- tentative,
- speculative,
- or invalidated.

The project should never silently promote weak evidence into accepted truth.

### 7. Optimize for research value per hour
The next task should be chosen based on expected information gain, not intellectual beauty.

High-priority work usually has at least one of these properties:
- it can falsify an important direction cheaply,
- it unlocks multiple later experiments,
- it reduces a major source of simulation optimism,
- or it resolves an ambiguity in platform behavior or data integrity.

### 8. Preserve platform-specific context
Polymarket-specific mechanics matter. They should not be flattened into generic finance abstractions unless testing shows that the platform-specific component adds nothing.

### 9. Build durable project memory
Every meaningful decision, invalidated idea, assumption change, and research milestone should be written down in the project files.

The goal is not just to progress. The goal is to progress without losing context.

---

## Default Research Loop

Every non-trivial research task should follow this sequence.

### Step 1 — Define the hypothesis clearly
State:
- what is being claimed,
- why it might work,
- where it should work,
- and where it should fail.

A hypothesis is not ready if it cannot be falsified.

### Step 2 — Define the exact required data
List:
- required entities,
- required timestamps,
- required joins,
- required fields,
- and known limitations.

Avoid vague “we probably need orderbook data” language. Be exact.

### Step 3 — Define the exact features
For each feature, specify:
- formula,
- lookback,
- time alignment,
- interpretation,
- and leakage risk.

If a feature is not precisely defined, it is not ready for testing.

### Step 4 — Define the executable test design
State:
- whether the path is maker or taker,
- entry assumptions,
- exit assumptions,
- fill assumptions,
- fee assumptions,
- and what metric determines success or failure.

### Step 5 — Run sanity checks first
Before reading any alpha into results, run checks such as:
- state reconstruction integrity,
- complement consistency,
- executable-price realism,
- thin-market exclusion,
- placebo timing,
- and cost sensitivity.

### Step 6 — Run conservative simulation
The first simulation should bias against the idea, not in favor of it.

Use:
- conservative fill assumptions,
- realistic spread handling,
- partial fills,
- size sensitivity,
- and out-of-sample or later-period checks wherever possible.

### Step 7 — Write a decision memo
Every completed experiment should end with a short decision memo containing:
- what was tested,
- what assumptions mattered,
- what survived,
- what failed,
- what remains ambiguous,
- and what the next decision is.

No experiment should end with silent ambiguity.

---

## Default Deliverable Format

Unless there is a reason to do otherwise, every meaningful deliverable should contain the following sections:

1. **Objective**  
   What question is being answered?

2. **Hypothesis or task statement**  
   What exactly is being tested or built?

3. **Inputs / dependencies**  
   What data, modules, and assumptions are required?

4. **Implementation notes**  
   What was implemented or proposed?

5. **Outputs**  
   Metrics, tables, plots, schemas, interfaces, or code artifacts.

6. **Failure modes / caveats**  
   What could make the result misleading?

7. **Interpretation limits**  
   What can and cannot be concluded?

8. **Next action**  
   What is the smallest meaningful follow-up?

This format should be used for experiment writeups, architecture notes, and implementation plans.

---

## Implementation Mode

### Modular by default
Prefer reusable modules over notebook-only logic.

As a rule:
- API clients belong in modules,
- parsers belong in modules,
- feature formulas belong in modules,
- simulations belong in modules,
- notebooks are for inspection and exploration, not primary logic.

### Config-driven where possible
The following should be externalized into config:
- universe filters,
- experiment definitions,
- signal thresholds,
- simulation sizes,
- quote lifetimes,
- and report parameters.

Avoid scattering research assumptions through code.

### Raw data preservation is mandatory
Always preserve raw payloads before normalization.

This is important for:
- debugging parser changes,
- recovering from schema misunderstandings,
- replaying experiments,
- and verifying platform behavior later.

### Logging is part of the research system
Log:
- collector starts/stops,
- websocket reconnects,
- parser failures,
- schema versions,
- reconciliation mismatches,
- experiment config hashes,
- and output locations.

Good logs are part of scientific hygiene, not just engineering hygiene.

### Unit-test what can silently ruin conclusions
Minimum testing targets:
- parser logic,
- timestamp alignment,
- feature formulas,
- fee calculations,
- queue-bound mechanics,
- displayed-price proxy,
- and token/market mapping logic.

### Visually inspect before trusting aggregates
Before trusting a metric or signal:
- inspect raw ladders,
- inspect a few real event traces,
- inspect a few stale-anchor episodes,
- inspect a few crypto fair-value alignments,
- inspect a few maker-fill paths.

A single visual inspection can catch errors that a hundred summary rows hide.

---

## Research Prioritization Rules

When choosing among possible tasks, prefer the one that most improves one of these:

### 1. Data trust
Examples:
- websocket integrity,
- snapshot reconciliation,
- timestamp correctness,
- token mapping correctness.

### 2. Execution realism
Examples:
- queue-bound modeling,
- slippage realism,
- fee handling,
- partial fill support.

### 3. Cheap falsification
Examples:
- placebo tests,
- thin-market exclusion,
- out-of-sample checks,
- conservative fill assumptions.

### 4. Reusability
Examples:
- state builder,
- feature library,
- simulator components,
- experiment runner.

### 5. Strategic narrowing
Examples:
- identifying one direction to demote,
- proving a major idea is weak,
- or isolating one regime worth expanding.

Tasks that improve none of these should usually be delayed.

---

## Roadmap Revision Rules

The roadmap is a living document, not a fixed promise.

It should be revised when:
- a key assumption is invalidated,
- a data source proves unreliable,
- platform mechanics change,
- a simpler route to falsification appears,
- or one direction clearly dominates the others.

When revising the roadmap:
1. state what changed,
2. explain why it changed,
3. say what this invalidates or deprioritizes,
4. record what becomes the new top priority,
5. update the next milestone accordingly.

Do not revise silently.

---

## Project Update Protocol

Every meaningful project update should record the following:

### What changed
Examples:
- new module added,
- data schema revised,
- feature formula changed,
- simulator assumption tightened,
- hypothesis invalidated.

### Why it changed
Examples:
- documentation verification,
- bug found,
- experiment result,
- platform change,
- simplification decision.

### What is now validated
List only what is actually supported.

### What remains uncertain
List unresolved issues plainly.

### What the next task is
State the smallest meaningful next step.

This update protocol should be reflected in `STATE.md`, `CHANGELOG.md`, and experiment notes.

---

## Default Classification Labels

Use these labels consistently across hypotheses, results, and summaries:

- **validated** — strong enough to rely on for the current stage
- **tentative** — some supporting evidence, still fragile
- **speculative** — plausible but unproven
- **weak evidence** — tested, but support is limited or unstable
- **promising** — survives initial realism well enough to justify expansion
- **invalidated** — failed the relevant test or proved too fragile to matter

Do not use vague labels such as “interesting” without one of the above.

---

## Guardrails Against Common Failure Modes

### 1. Midpoint fantasy
Never treat midpoint as an automatic fill assumption.

### 2. Queue fantasy
Never assume top-of-book placement implies fast or full fill.

### 3. Cancel fantasy
Never assume perfect cancellation ahead of toxicity without modeling delay or uncertainty.

### 4. Thin-book fantasy
Never count gains in markets where realistic size cannot be entered or exited.

### 5. Model-precision fantasy
Never let a more detailed fair-value model hide the fact that the edge may not exist.

### 6. Aggregation fantasy
Never average incompatible regimes together and call the result robust.

### 7. Documentation fantasy
Never assume a platform mechanic is fully understood unless verified or clearly labeled as inference.

---

## Collaboration Mode for Future Iterations

The default collaboration style for future work is:

- always prefer the smallest meaningful next implementation step,
- always separate must-have from nice-to-have,
- always expose hidden assumptions,
- always mark validated vs speculative,
- always keep maker and taker logic separate,
- always keep research value per hour in mind.

Future tasks should generally fall into one of these categories:
- schema design,
- endpoint selection,
- feature definition,
- simulator design,
- experiment design,
- result interpretation,
- bias detection,
- realism improvement,
- or roadmap refinement.

The goal of collaboration is not to generate more text.  
It is to reduce ambiguity, eliminate weak paths early, and steadily convert promising research into solid implementation.

---

## Practical Default

When unsure what to do next, do this:

1. choose one hypothesis,
2. define the minimum data needed,
3. define one conservative test,
4. run the cheapest sanity checks,
5. simulate realistically,
6. write down the decision,
7. move only if the idea earns the next step.

That is the default operating behavior of this project.