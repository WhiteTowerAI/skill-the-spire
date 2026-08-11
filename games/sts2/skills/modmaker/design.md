# Design - preserve intent and choose the current deliverable

Goal: write the durable `DESIGN.md` after routing and Interview, before `SPEC.md`. Preserve
the user's intended experience and larger vision while selecting only a supported, exact
current slice for generation. Do not turn this stage into a second interview.

State what the finished thing is before listing what it requires. A scope ledger of
requirements answers "what must be true"; it does not answer "what does the user have when
this is done". Those are different questions, and only the second one can be checked against
the final report.

## Artifact ownership

- `DESIGN.md` owns player intent, accepted decisions, trade-offs, rejected alternatives,
  tuning hypotheses, the deliverable claim and its required/excluded player experiences,
  current scope, future vision, and explicit boundaries.
- `SPEC.md` owns the exact framework-neutral operations generated now and their supported
  semantic routes.
- `PLAN.md` owns stage status, the one active repair route, and the deliverable settlement
  ledger — which required experiences the run actually earned.
- `MEMORY.md` owns resolved technical identities, adapter/API/resource facts, builds, and
  repairs. It must not silently revise creative intent.

When artifacts disagree, stop before authoring. Treat the mismatch as design/SPEC drift,
show the smallest revision delta, and update `DESIGN.md` first. Neither SPEC nor MEMORY may
override a settled design choice merely because its implementation is easier.

The same ownership applies to repair. A player-visible fix is an
`accepted-semantic-change`: stop before applying it, route the smallest delta through revision,
update the claim, affected `E-###`, scope, anchors, and `Q-###` queue as applicable, and obtain
explicit acceptance before SPEC changes. A missing lowering field for an already accepted exact
result is `contract-fulfillment`; preserve DESIGN and correct SPEC instead.

## Adaptive depth

Every new or revised Mod gets `DESIGN.md`, but only include useful sections:

- **Fast:** contract, route, one-sentence intent, accepted/defaulted decision, a one-line
  deliverable claim with one or two required experiences, compact scope ledger, one compact
  coherence anchor/check, and no empty full-design ceremony. A complete exact Card should fit
  in a short capsule and require no new question.
- **Co-design:** add the selected alternatives/trade-off and only the relevant native-grammar and planning
  planning sections: fantasy, core decision/loop, content relationships, formula/economy,
  tuning knobs, dominance concern, and open hypotheses. The claim usually names a slice shape
  and carries a real excluded list.
- **Revision:** preserve stable IDs, settled and rejected decisions, and unrelated scope.
  Record only the requested delta, its ordered impact/re-evaluation queue, and why it
  reopens specific downstream work. Preserve existing `E-###` ids whose experience is
  unchanged; a revision that changes what the player gets updates the claim rather than
  leaving it describing the old deliverable.

Do not add pillars, lore, content-role tables, formulas, or rejected alternatives when the
request never needed them. Do not omit a material accepted decision merely to keep the file
short.

## The deliverable claim

Write one literal claim before the scope ledger: what exists when this is done, said in the
user's own terms. Then list the player experiences that must be true for the claim to be
honest, and the ones a reasonable reader of the claim would expect that are not there.

- **`claim`** — one sentence a non-programmer can check against the finished Mod. "One
  playable Attack card you can add to a run and play in combat for 9 damage", not "a Card
  operation with an upgrade path".
- **`shape`** — a short free-text descriptor: "one Card", "nine-Card evaluable slice",
  "run-capable Character". This is a **description, not a category.** There is no fixed list
  of allowed words, nothing branches on its value, and no route requires a particular one.
  Say what fits the request.
- **`required_experiences`** — stable `E-###` items. Each states one thing the *player* can
  observe, names the `D-###` decisions it comes from, and names how it will be settled. An
  experience is not a requirement and not an operation: "the player enters Wrath and then
  takes more damage" is the experience; "Wrath doubles incoming damage" is the requirement;
  the generated Power is the operation. All three can exist while the experience is false.
- **`excluded_experiences`** — plain sentences for what the claim might reasonably be read to
  include but does not. Every accepted `PLACEHOLDER`, every accepted visible difference under
  `INV-5`, and every scale limit belongs here. Individually each was already accepted; the
  point of collecting them is that the combined list is itself a player experience, and it is
  the only place the user sees "all art is placeholder **and** three behaviors are composed
  rather than replaced **and** the pool is slice-scale" as one thing.

`settled_by` uses exactly one of four values:

| Value | Means | Settled when |
|---|---|---|
| `tier-2-structured` | A structured state proof asserts it | The harness emits the matching `state proof:` line |
| `tier-1-load` | Presence in-game is the whole experience | The exact load marker appears with no fresh error block |
| `headed-human` | Only a person can judge it — art framing, UI legibility, feel | A human reports the observation |
| `user-decision` | The user accepted a stated difference | They accepted it, at confirmation or later |

`user-decision` is **not** evidence of observation (`INV-4`). It records acceptance, which is
what an accepted `PLACEHOLDER` actually has behind it. Keeping it separate is what stops
"the user agreed to template art" from later reading as "the art was checked".

Keep this proportional. An exact Card gets one or two experiences and a one-line claim; do
not invent experiences for defaults nobody asked about. A Character or content set names its
slice shape and usually carries a real `excluded_experiences` list. Do not ask a new question
to fill these fields — derive them from the routed intake and settled decisions, and state
them at the combined confirmation like any other inferred default.

## Scope decisions

Give every distinct user requirement or explicit fallback a stable `D-###` ID. Use exactly
one disposition after the user has resolved any blocking boundary:

- **MUST:** required in the current deliverable. It must be exact enough for SPEC, have a
  confirmed supported route, and map to at least one current `OP-###` SPEC operation.
- **PLACEHOLDER:** a documented current fallback the user accepted, such as template art.
  It remains player-visible current behavior and maps to an explicit SPEC fallback
  operation; it is not silent omission.
- **DEFER:** preserved future vision that will not be generated now. State why it is later
  and what evidence, support, or user decision would reopen it. It maps to no SPEC operation.
- **OUT-OF-SCOPE:** explicitly rejected or excluded from this Mod. State the decision so it
  is not accidentally reintroduced. It maps to no SPEC operation.

`MUST` means product necessity, not implementation authority. Before assigning it, confirm
the operation against the current capability graph and shipped semantic recipe/reference.
A documented public Package route may be supported even when verification is unrun; state
verification literally later. A missing public/promoted route cannot become `MUST` through
design confidence.

## Unsupported and unresolved intent

For a requested operation outside the current support graph:

1. preserve the intended player experience and state the exact boundary;
2. offer at most two supported alternatives only when they preserve that intent, including
   their visible trade-offs;
3. ask for one explicit choice: accept a supported current version, preserve the original
   as `DEFER`, or remove it as `OUT-OF-SCOPE`; and
4. keep the issue in `blocking_gaps` until the user decides.

Do not freeze DESIGN, write SPEC, scaffold, or assign the unsupported operation an
`OP-###` ID while `blocking_gaps` is nonempty. A request to avoid questions does not permit
a silent downgrade. `DEFER` preserves the original idea; it does not claim that a future
runtime route exists.

## Coherence contract

Run a proportional coherence check before freezing every new or revised DESIGN. Load
`${STS2_API_SKILL_DIR}/design/coherence-review.md` only when the request has multiple
intentional expressive surfaces, explicitly selects theme/narrative/presentation, or
revises an identity anchor. A narrow exact Card still records one compact mechanics/naming
check without receiving a general style review or another question.

Derive one to three `A-###` identity anchors from accepted `D-###` decisions. Check only
applicable current surfaces among mechanics, naming, localization, visuals, Event text,
and Character identity. A placeholder is a current fallback, not an expressive visual
claim, so do not invent its motif or palette. Record an accepted ironic or contrasting
choice as `deliberate-tension` rather than silently normalizing it.

When selected artifacts disagree, record the exact conflict and stop before SPEC. Resolve
it by aligning the downstream expression, explicitly revising the anchor, or preserving a
user-selected deliberate tension. Use temporary surface status `conflict` with a matching
conflict record; resolution changes it to `aligned` or `deliberate-tension`. `conflicts`
must be empty before validation succeeds.
Coherence cannot widen support, add an untraced operation, or turn text/art/build evidence
into proof of behavior, balance, or player experience.

For revision, inspect only artifacts that can depend on changed design IDs and write an
ordered `Q-###` impact/re-evaluation queue. Use `UPDATE`, `REVIEW`, `REVERIFY`, and
`PRESERVE` as defined by the reference. Update DESIGN first and reopen only affected PLAN
stages. Stable runtime/localization identifiers are technical facts; a display-name change
puts them under REVIEW rather than blindly renaming them.

When revision came from active repair, preserve the PLAN repair decision until the accepted
DESIGN and affected SPEC operations validate. Rejection preserves the old DESIGN; it does not
turn the proposed substitute into a technical repair.

## Write `DESIGN.md`

Create the dedicated outer work directory now. Its name must differ from `<ModName>` because
the later template scatters into the current directory and creates a `<ModName>/` resource
subdirectory. Write `DESIGN.md` at that outer root; SPEC, PLAN, and MEMORY will join it.

Use the shortest applicable prose sections, followed by exactly one machine-readable scope
block and one machine-readable coherence block. JSON is used only for deterministic
validation; keep explanations in plain language.

````markdown
# DESIGN - <Mod Name>

- **contract**: open-mod-design/v1
- **route**: fast | co-design | revision

## Intent

<one player-facing sentence>

## Decisions

- <accepted/defaulted decision and its basis>
- <selected alternative and trade-off, only when applicable>

## Design Notes

<omit on the fast path; otherwise include only relevant native-grammar and planning capsule fields,
rejected alternatives, tuning hypotheses, and evidence that could change the design>

## Deliverable

<one plain sentence naming what the user has when this is done; then the claim block>

<!-- open-mod-deliverable:v1:start -->
```json
{
  "contract": "open-mod-deliverable/v1",
  "route": "fast",
  "claim": "One playable Attack card called Ember Step that you can add to a run and play in combat for 9 damage.",
  "shape": "one Card",
  "required_experiences": [
    {
      "experience_id": "E-001",
      "statement": "Playing Ember Step in combat deals 9 damage to the chosen enemy, and 12 after upgrade",
      "design_ids": ["D-001"],
      "settled_by": "tier-2-structured"
    },
    {
      "experience_id": "E-002",
      "statement": "The card shows the template placeholder portrait rather than custom art",
      "design_ids": ["D-002"],
      "settled_by": "user-decision"
    }
  ],
  "excluded_experiences": [
    "No custom portrait art in this deliverable",
    "No Character, relic, or reward-pool content beyond this single Card"
  ]
}
```
<!-- open-mod-deliverable:v1:end -->

## Scope Ledger

<!-- open-mod-scope:v1:start -->
```json
{
  "contract": "open-mod-design/v1",
  "route": "fast",
  "current_slice": [
    {
      "design_id": "D-001",
      "disposition": "MUST",
      "summary": "Exact current player-facing requirement",
      "support": "confirmed",
      "spec_operations": ["OP-001"],
      "reason": "Why this belongs in the first playable deliverable"
    },
    {
      "design_id": "D-002",
      "disposition": "PLACEHOLDER",
      "summary": "Use the checked template art fallback",
      "support": "placeholder-fallback",
      "spec_operations": ["OP-002"],
      "reason": "Custom art was not requested"
    }
  ],
  "future_vision": [
    {
      "design_id": "D-003",
      "disposition": "DEFER",
      "summary": "Larger future feature preserved literally",
      "support": "not-current",
      "spec_operations": [],
      "reason": "Current boundary and the evidence or decision needed to revisit it"
    }
  ],
  "blocking_gaps": []
}
```
<!-- open-mod-scope:v1:end -->

## Coherence

<one short player-facing account of how the selected surfaces reinforce the intent; omit
surface essays and list only resolved deliberate tensions>

<!-- open-mod-coherence:v1:start -->
```json
{
  "contract": "open-mod-coherence/v1",
  "route": "fast",
  "anchors": [
    {
      "anchor_id": "A-001",
      "design_ids": ["D-001"],
      "statement": "The exact current behavior is legible in the content name and effect"
    }
  ],
  "surface_checks": [
    {
      "surface": "mechanics",
      "design_ids": ["D-001"],
      "anchor_ids": ["A-001"],
      "expression": "The repeated player action and payoff implement the accepted intent",
      "status": "aligned"
    },
    {
      "surface": "naming",
      "design_ids": ["D-001"],
      "anchor_ids": ["A-001"],
      "expression": "The displayed name uses the accepted gameplay vocabulary",
      "status": "aligned"
    }
  ],
  "conflicts": [],
  "impact_queue": []
}
```
<!-- open-mod-coherence:v1:end -->
````

The Markdown example contains inner JSON fences; when authoring the actual artifact, write
each marked block literally once. All three marked blocks carry the same `route`. Use
`excluded_experiences: []` only when the claim genuinely has no readable-but-absent edge —
a Mod with placeholder art always has at least one entry. Use `future_vision: []` when there
is no future/deferred/out-of-scope item. Use `blocking_gaps: []` and `conflicts: []` before proceeding to SPEC.
New fast/co-design work uses `impact_queue: []`. A revision requires at least one affected
UPDATE/REVIEW/REVERIFY queue item and may add focused PRESERVE entries for decisions at
real risk of accidental change.

## Existing projects without DESIGN.md

Do not restart or re-interview an unchanged unfinished project created before M7.4. Backfill
a compact `DESIGN.md` from the user's settled request and accepted SPEC:

- preserve every exact existing operation as a current `MUST` or accepted `PLACEHOLDER`;
- record no invented rationale, rejected alternative, or future vision;
- assign stable design and operation IDs, then validate the trace;
- ask only when a real DESIGN/SPEC contradiction or missing current-scope choice cannot be
  resolved from the existing artifacts.

After backfill, resume the first unfinished PLAN stage. This migration records existing
truth; it is not a design revision.

An unchanged project created before M7.5 may resume without a coherence block. Do not
reopen completed stages solely to backfill it. On its next design revision, add the
coherence block from explicit settled decisions and existing artifacts; do not invent
historical theme, lore, or rationale.

A project whose `DESIGN.md` has no `open-mod-deliverable:v1` block predates the deliverable
claim and resumes unchanged the same way. On its next revision, derive the claim from the
accepted SPEC and settled decisions: the claim describes what that project already builds,
and every required experience traces to an existing current design item. Do not invent a
larger deliverable than the artifacts already show, and do not backfill a settlement ledger
for stages that already completed — an experience settled before the ledger existed is
recorded as an `exception` with what is actually known, never as `observed`.

## Handoff and confirmation

Carry the scope ledger to `spec.md`. Assign every generated semantic operation one stable
`OP-###` ID already listed by its current design items. Future and out-of-scope items never
enter SPEC.

Before SPEC, run:

```powershell
python ${GAME_TOOLS_DIR}/coherence_trace.py --design DESIGN.md
python ${GAME_TOOLS_DIR}/deliverable_trace.py --design DESIGN.md
```

Stop on an unknown design/anchor reference, unresolved conflict, invalid surface, or an
empty revision impact queue. Stop equally on a missing claim or shape, an `E-###` that
traces to no current design item, or an unknown `settled_by`. Both validators check
structure and references. A green run is not quality or human acceptance (`INV-4`), and a
well-formed claim is not a delivered one.

Use one combined DESIGN/current-slice/SPEC confirmation before scaffolding. Lead with the
claim, then summarize **build now**, **placeholder**, and **later/not included**; omit empty
groups. Do not ask for separate approval of each file. If the user changes scope, update
DESIGN first, regenerate the coherence/design traces, and validate again.
