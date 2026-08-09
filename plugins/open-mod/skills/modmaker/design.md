# Design - preserve intent and choose the current deliverable

Goal: write the durable `DESIGN.md` after routing and Interview, before `SPEC.md`. Preserve
the user's intended experience and larger vision while selecting only a supported, exact
current slice for generation. Do not turn this stage into a second interview.

## Artifact ownership

- `DESIGN.md` owns player intent, accepted decisions, trade-offs, rejected alternatives,
  tuning hypotheses, current scope, future vision, and explicit boundaries.
- `SPEC.md` owns the exact framework-neutral operations generated now and their supported
  semantic routes.
- `PLAN.md` owns stage status only.
- `MEMORY.md` owns resolved technical identities, adapter/API/resource facts, builds, and
  repairs. It must not silently revise creative intent.

When artifacts disagree, stop before authoring. Treat the mismatch as design/SPEC drift,
show the smallest revision delta, and update `DESIGN.md` first. Neither SPEC nor MEMORY may
override a settled design choice merely because its implementation is easier.

## Adaptive depth

Every new or revised Mod gets `DESIGN.md`, but only include useful sections:

- **Fast:** contract, route, one-sentence intent, accepted/defaulted decision, compact scope
  ledger, one compact coherence anchor/check, and no empty full-design ceremony. A complete
  exact Card should fit in a short capsule and require no new question.
- **Co-design:** add the selected alternatives/trade-off and only the relevant native-grammar and planning
  planning sections: fantasy, core decision/loop, content relationships, formula/economy,
  tuning knobs, dominance concern, and open hypotheses.
- **Revision:** preserve stable IDs, settled and rejected decisions, and unrelated scope.
  Record only the requested delta, its ordered impact/re-evaluation queue, and why it
  reopens specific downstream work.

Do not add pillars, lore, content-role tables, formulas, or rejected alternatives when the
request never needed them. Do not omit a material accepted decision merely to keep the file
short.

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
`../sts2-api/design/coherence-review.md` only when the request has multiple
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
each marked block literally once. Use `future_vision: []` when there is no future/deferred/
out-of-scope item. Use `blocking_gaps: []` and `conflicts: []` before proceeding to SPEC.
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

## Handoff and confirmation

Carry the scope ledger to `spec.md`. Assign every generated semantic operation one stable
`OP-###` ID already listed by its current design items. Future and out-of-scope items never
enter SPEC.

Before SPEC, run:

```powershell
python ../modmaker/scripts/coherence_trace.py --design DESIGN.md
```

Stop on an unknown design/anchor reference, unresolved conflict, invalid surface, or an
empty revision impact queue. The validator checks structure and references. A green run is
not quality or human acceptance (`INV-4`).

Use one combined DESIGN/current-slice/SPEC confirmation before scaffolding. Summarize
**build now**, **placeholder**, and **later/not included**; omit empty groups. Do not ask for
separate approval of each file. If the user changes scope, update DESIGN first, regenerate
the coherence/design traces, and validate again.
