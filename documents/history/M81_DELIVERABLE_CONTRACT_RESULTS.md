# M8.1 literal deliverable contract

## Decision

M8.1 Literal Deliverable Contract is implemented in source and synchronized into both
committed payloads on 2026-08-10. Its execution contract was written against the file layout
M8.0 left behind and confirmed by the human lead before implementation, including the three
decisions the contract left open.

This is an implementation record, not a claim that a generated Mod was built, launched, or
observed. No forward-model run, generated Mod, game launch, Tier 1, or Tier 2 is claimed by
this Package.

## Problem

The workflow recorded requirements but never stated what the finished thing was.
`DESIGN.md`'s scope ledger is a `D-###` requirement table; `SPEC.md`'s trace is an `OP-###`
generation allowlist. Neither answers "what does the user have when this is done", and nothing
bound the final report to that answer. Four gaps, each located in source before the change:

1. **No statement of the whole.** The Watcher run delivered a nine-Card vertical slice with
   all-placeholder presentation and several acknowledged fallbacks while every local stage
   passed. Because no artifact said "this will be an evaluable slice, not a run-capable
   Character", the disappointing result violated no contract.
2. **No player-experience obligation.** "The player enters Wrath and then takes more damage"
   was neither a requirement nor an operation, so Watcher's Wrath shipped without its
   multiplier while all of its operations passed.
3. **No link from claim to final report.** `verify.md` § Finalize was a two-branch prose
   template. `INV-1` kept *tier* reporting honest, but nothing compared the report against
   what was promised; Watcher's closing narrative called Scry verified while the same record
   disclosed Scry was never driven.
4. **No combined view of accumulated fallbacks.** Each `PLACEHOLDER` was individually
   accepted, but no artifact read "all art placeholder + composed-instead-of-replaced
   behaviors + slice-scale pool" as one player experience.

## Three Confirmed Decisions

1. **The settlement ledger lives in `PLAN.md`**, which already owns literal pipeline status;
   experience settlement is the deliverable's completion status. `MEMORY.md` keeps its
   existing job of recording which checks actually ran.
2. **`repair.md` gets only a staleness rule.** A repair that changes an experience outcome may
   not leave the ledger describing the pre-fix run. Substantive backtracking to the owning
   artifact remains a later Package, and the page says so explicitly.
3. **The claim is a third independent marked block**, not a field inside the scope block. The
   deciding reasons are the existing one-block-one-stamp-one-validator precedent and the fact
   that an absent block is an unambiguous "predates this contract" signal, the way an absent
   coherence block signals a pre-M7.5 project. A merged field would have forced
   `open-mod-design/v2` plus a migration, and would have made "old file" and "author forgot
   the field" indistinguishable. The recorded cost is a third JSON block in `DESIGN.md`, which
   runs against M8.0's structural compression.

An earlier justification for decision 3 — that a merged field would collide with a contract
version M8.2 must migrate — was wrong and is not the basis for the decision. The SPEC envelope
M8.2 owns (`sts2-content-semantic/v1`) and the DESIGN scope block (`open-mod-design/v1`) are
different stamps and would not have collided. What survives is weaker: M8.2 already carries one
contract migration, and keeping M8.1 purely additive avoids a project created between the two
Packages having to pass through two.

## What Was Implemented

**The claim** — `DESIGN.md` gains `open-mod-deliverable:v1`, written before the scope ledger:

- `claim`: one sentence a non-programmer can check against the finished Mod;
- `shape`: a free-text descriptor. **Presence-only by design.** Nothing branches on its value
  and no validator checks it against a list, because prototype/slice/run-capable are optional
  descriptions rather than a closed taxonomy;
- `required_experiences`: stable `E-###` items, each one player-observable statement plus its
  `design_ids` and one `settled_by`; and
- `excluded_experiences`: what a reasonable reader of the claim would expect that is not there.
  This is where gap 4 becomes one readable list.

`settled_by` is exactly four values: `tier-2-structured`, `tier-1-load`, `headed-human`,
`user-decision`. The fourth is deliberately not evidence of observation — it records that the
user accepted a stated difference, which is what an accepted `PLACEHOLDER` actually has behind
it. Keeping it separate is what stops "the user agreed to template art" from later reading as
"the art was checked".

**Confirmation** — `spec.md`'s single combined confirmation now leads with the claim and names
what it does not include, so what the user approves before scaffold is the shape of the
finished thing rather than only requirement rows.

**Finalize** — `verify.md` settles every `E-###` in `PLAN.md`'s ledger as `observed`,
`unobserved`, or `exception` with its evidence, validates the ledger, and generates the
user-facing summary from it. `unobserved` and `exception` each require a note stating what is
missing, so an exception cannot read as a quiet pass.

**Validator** — new `deliverable_trace.py`, two modes. Pre-SPEC checks the claim's structure,
`E-###` form and uniqueness, the current-design trace, and `settled_by`. Finalize checks that
every required experience has an outcome and that no outcome outruns its evidence type. It is a
third validator beside `coherence_trace.py` and `design_trace.py`; it earns its place by
checking at finalize, where neither existing tool runs.

**No `INV-9`.** The claim-versus-report rule fires at finalize only, and `invariants.md`
deliberately keeps single-stage rules where they fire, as the repair attempt cap and the
art-consent boundary already do. A test asserts no ninth invariant was added.

**Routing** — `route.md` and `interview.md` carry a `deliverable signals` handoff line so the
claim is derived from what the user already said. `interview.md` explicitly forbids asking for
the claim: "what kind of deliverable do you want" is the workflow-mode question routing already
refuses to ask.

**Resume compatibility** — a project whose `DESIGN.md` has no claim block resumes unchanged.
On its next revision the claim is derived from the accepted SPEC, and an experience settled
before the ledger existed is recorded as an `exception`, never as `observed`.

## Verification

Proportional and non-game: prompt, tooling, and documentation only, with no generated runtime
behavior or presentation change, so no game launch.

- Focused Python suite `298/298`, up from `256`. The 42 new tests are
  `tools/tests/test_m81_deliverable_contract.py`.
- Six validator negative cases were also run directly against fixtures before the tests were
  written: an `observed` outcome on insufficient evidence, a missing settlement, an `exception`
  with no note, an experience tracing to a non-current design item, an empty `shape`, and a
  non-taxonomy `shape` wording that must pass.
- The shipped copy under `plugins/open-mod/skills/modmaker/scripts/` was executed from its
  bundled location in a scratch directory, in both modes, including the honest-exception route.
- Both payloads regenerated from source, verified repeatable across a second render, and the
  two modmaker trees are identical. No payload was installed or run.
- No milestone id appears anywhere in the shipped pack.

**Two pre-existing tests were repaired rather than the source they tested.** Both broke for the
same reason and neither indicates a defect in the new contract:

- `test_m74_scope_traceability.py` asserted `PLAN.md` owns "stage status only". PLAN now also
  owns the settlement ledger, so the assertion was narrowed to the boundary that matters —
  which artifact owns which fact — rather than the word "only".
- `test_m75_coherence.py` mutated "the first `route: fast` in `design.md`" to prove the
  coherence validator rejects route drift. That positional replace used to hit the scope block
  and now hits the deliverable block, so the test silently stopped testing what it claimed. It
  now anchors on the coherence block explicitly. This was a latent fragility in the test, and
  adding a third block is what exposed it.

## Literal Boundaries

- No generated Mod, scaffold, build, launch, Tier 1, Tier 2, or headed review was run.
- No independent forward-model run exercised the three scenarios; the review record in
  `games/sts2/tests/m81-deliverable-contract-scenarios.md` is a source-contract inspection.
- The validator checks structure and evidence sufficiency. It cannot judge whether a claim is
  the *right* claim, whether an experience statement is well chosen, or whether the delivered
  Mod is any good.
- A green pre-SPEC run means the claim is well formed, not that it is delivered.
- Checking that a required experience has an exact maintained route, surface parity for
  text/keyword/Hover-Tip/localization, and backtracking when an experience fails all remain
  later Packages. M8.1 did not widen the capability graph.
- The three open M8.0 surface cross-check mismatches remain open and deferred; M8.1 did not
  touch them.
- No payload publication, GitHub release, or acceptance Mod is authorized by this result.

## Documents Reviewed

Changed: `documents/IMPLEMENTATION_PLAN.md` (contract, status), `games/sts2/tests/README.md`
(test ownership), `documents/PROJECT.md` (release state), `AGENTS.md` (current status),
`documents/history/README.md` (index), `README.md` (status banner, pipeline step, and the M8
paragraph that said none of the M8 flow was implemented).

Reviewed and left unchanged: `documents/BASELINE_RESEARCH.md` — M8.1 used no baseline
research, since the claim contract is a workflow layer and needs no API grounding;
`games/sts2/tests/content-capability-graph.md` — the runtime support graph is unchanged by
design; `games/sts2/tests/m80-surface-cross-check.md` — its three open mismatches are M8.2's,
untouched here.
