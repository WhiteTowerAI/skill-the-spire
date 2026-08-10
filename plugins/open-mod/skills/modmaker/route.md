# Route - choose the smallest useful design path

Goal: decide whether this request needs the fast, co-design, or revision path before
asking questions. State the route in one short sentence. Route selection is not a
questionnaire and does not change the runtime support boundary.

## Read project state first

Inspect the work directory before treating the request as new:

1. Read `DESIGN.md` when present, then `SPEC.md`, `PLAN.md`, and `MEMORY.md`.
2. Inspect the existing generated project only when the request changes or diagnoses it.
3. Treat facts already written in those artifacts as settled unless the user explicitly
   changes them or two artifacts conflict.

If an unfinished `PLAN.md` exists and the user requested no design change, resume the first
unfinished stage immediately. Do not run another interview and do not call this a revision.
If that older project has `SPEC.md` but no `DESIGN.md`, first use `design.md` to backfill a
compact artifact from settled facts, assign trace IDs, validate it, and then resume. Ask
only if the existing artifacts contain a material contradiction; do not invent rationale,
rejected alternatives, or future vision.
If a new project has accepted `DESIGN.md` but no SPEC/PLAN yet, resume at SPEC without
rerunning Route or Interview. Every resume path here is `INV-6`: the artifacts are the state.
If the user asks to change an existing Mod or its artifacts, use the revision route even
when the change looks small.

## Choose one route

### Fast

Use fast when the request is narrow and has one clear player-facing interpretation, such as
an exact Card, Relic, Potion, or similarly bounded operation. Defaults may fill details that
do not materially change the idea.

- Ask no question when the request plus safe defaults is sufficient.
- Ask at most one compact clarification round when one material decision is missing.
- State inferred defaults in the combined DESIGN/current-slice/SPEC confirmation; do not
  ask the user to approve each default separately.
- Do not add pillars, a full GDD, alternative mechanics, or speculative future systems to a
  clear request.

### Co-design

Use co-design when the player experience or mechanic has multiple plausible interpretations,
or when a Character, archetype, content set, or interacting system lacks a core decision.

- Resolve the highest-impact open decision first instead of sending an exhaustive intake.
- Present two or three materially different choices. Describe what the player does or feels,
  the concrete trade-off, and which option you recommend and why.
- Batch up to three questions only when they are independent and short. Keep dependent
  decisions for the next turn.
- Preserve every accepted choice. Later questions may refine it but must not silently replace
  it.
- Stop offering alternatives once the remaining details have safe defaults.

### Revision

Use revision for an existing Mod, `DESIGN.md`/`SPEC.md` pair, requested design change, or
user-supplied playtest observation.

- Read the existing artifacts before asking anything.
- Summarize a delta as **keep**, **change**, **check**, and **re-verify**. Omit empty groups.
- Ask only about a contradiction or missing choice introduced by the requested change.
- `INV-6` covers the rest of the project: unrelated decisions, rejected alternatives, content,
  identifiers, and completed stages stay as they are, and the general interview does not restart.
- After confirmation, update DESIGN first, then only the affected SPEC operations and
  trace; reopen only the PLAN stages invalidated by the delta.
- A playtest observation arrives as user-reported evidence (`INV-4`). Routing it does not
  diagnose balance automatically or start an automated tuning loop.

The route may change when new information changes the request. Briefly state why, keep all
settled decisions, and continue from the smallest affected decision.

## Load only the relevant design references

After choosing the route and before asking a creative question, classify the design
surface and load the smallest applicable set:

- **Playable Character or Foundation:** read
  `../sts2-api/design/character-foundation.md`.
- **Ambiguous mechanic or system:** read
  `../sts2-api/design/mechanic-planning.md` when the request introduces or
  revises a resource, stateful loop, risk/reward structure, or interacting system whose
  core decision is not already exact.
- **Character, archetype, or content set:** read
  `../sts2-api/design/content-set-planning.md`; for a Character also read the
  Foundation reference, and add mechanic planning only when its core decision is unclear.
- **Numeric, economy, or balance problem:** read
  `../sts2-api/design/balance-planning.md` when values materially change the
  mechanic, numeric resource sources/sinks/cadence are a current design question, or the
  user asks for balance analysis.
- **Theme, narrative, presentation, or cross-surface identity:** read
  `../sts2-api/design/coherence-review.md` when more than one intentional
  expressive surface must reinforce the same design, the request explicitly selects one
  of those directions, or a revision changes an existing identity anchor. A checked
  placeholder is not an expressive surface by itself.

An exact narrow Card stays on the fast path without loading mechanic, content-set, or
balance planning merely because the Card contains a cost or effect number. Record `none`
when no design reference applies. Native grammar remains Character-specific; for other
surfaces, record `none` in the `native grammar` handoff even when a planning
reference is loaded. A narrow exact Card keeps the same question economy: run its compact
mechanics/naming check without loading coherence review unless the request introduces a
second intentional expression or a material conflict.

Use the loaded references to distinguish pinned facts, observed conventions, creative
decisions, and open hypotheses. A convention can supply a recommended default but cannot
overwrite a settled user choice or become an engine restriction. Planning does not
authorize a runtime route, prove balance, or expand the capability graph.

## Material-question filter

Ask a question only when different answers would produce meaningfully different player
behavior, supported operations, scope, state lifetime, content relationships, or proof.
Before asking, check whether the answer is already in the prompt, project artifacts, pinned
references, capability graph, or safe defaults.

Do not ask the user for:

- game, catalog, framework, API, localization-key, or resource-path facts that local checked
  references own;
- a preference whose alternatives lead to the same SPEC;
- optional polish the user did not request;
- confirmation of each inferred name, rarity, pool, target, art fallback, or other documented
  default; or
- facts already settled in `DESIGN.md`, `SPEC.md`, `PLAN.md`, or `MEMORY.md`.

When a default could alter the core experience, it is no longer a safe default: explain the
two or three outcomes and ask for the decision.

## Contradictions and unsupported requests

For contradictory input, quote or closely paraphrase the two conflicting requirements,
explain the player-facing consequence, and ask one constrained resolution question. Do not
pick the convenient interpretation or discard either requirement silently.

For an unsupported operation, state the exact current boundary before SPEC or scaffold
(`INV-3`). Preserve the intended player experience and offer at most two supported
alternatives only when they keep that intent. Each one is a visible difference, so it needs
the explicit acceptance `INV-5` requires — including when the user asked to be asked less.

## Handoff

Carry this compact routing state into `interview.md`:

```text
route: fast | co-design | revision
intent: <one player-facing sentence>
settled decisions: <facts and choices that must not be re-asked>
open decisions: none | <only material unresolved decisions>
defaults: <inferred defaults that will be stated at confirmation>
native grammar: none | <loaded design reference and pinned profile>
planning references: none | <loaded mechanic/content-set/balance references>
coherence reference: none | design/coherence-review.md
revision delta: none | <keep/change/check/re-verify summary>
gaps: none | <unsupported intent awaiting an explicit choice>
scope signals: <requested now; explicitly later; accepted placeholder; explicitly excluded>
deliverable signals: <what the user seems to expect to have when this is done, in their own
  words; the player experiences they would check first; anything their wording implies that
  this deliverable will not contain>
coherence signals: <selected expressive surfaces and any apparent cross-artifact conflict>
```

`deliverable signals` is observation, not a new question. Take it from what the user already
said — "just a card to test" and "a character I can actually play a run with" imply very
different finished things, and the difference is usually already in the prompt. When the
request genuinely does not imply a scale, record what it does say and let `design.md` state
the inferred shape at confirmation like any other default.

Routing itself does not define or generate the `DESIGN.md` schema, the current/future split,
the deliverable claim, or design-to-SPEC traceability, and neither do the design-grammar or
planning references. `design.md` owns those contracts and implements them with
`design_trace.py` and `deliverable_trace.py`. Read an existing `DESIGN.md` as authoritative
creative/scope state and route only the smallest unresolved delta.
