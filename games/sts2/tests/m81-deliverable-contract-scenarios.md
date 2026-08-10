# M8.1 literal deliverable contract scenarios

These repository-owned cases define the behavioral review surface for M8.1. They evaluate
whether the workflow states what the finished thing is before building it, whether the
required player experiences are separable from requirements and operations, and whether the
final report can say more than the run earned. They do not prove runtime behavior, Tier 1,
Tier 2, design quality, balance, enjoyment, or human playtest results.

Review behavior semantically rather than matching preferred prose. A response passes when it
preserves the same claim, experience set, settlement honesty, and exclusion visibility; exact
headings and sentences may differ.

## Common rubric

- **Claim before build:** one plain sentence for what the user has when this is done, written
  before SPEC and restated at the combined confirmation.
- **Shape is a description:** `shape` is free text. No route branches on it, no validator
  checks it against a list, and an unusual phrasing is not an error. "prototype", "slice",
  and "run-capable" are available words, not a taxonomy.
- **Experience is not requirement is not operation:** an `E-###` states what the player
  observes. A passing `OP-###` never settles an `E-###` by itself.
- **Settlement matches evidence:** `observed` only on evidence the experience's `settled_by`
  accepts; a human-owned experience nobody observed is an `exception`; an accepted difference
  is `user-decision` and never becomes observation.
- **Exclusions are visible once, together:** accepted placeholders, accepted visible
  differences, and scale limits appear as one readable list rather than only as scattered
  individual acceptances.
- **Question economy:** the claim costs the user no new question. It is derived from routed
  signals and stated at confirmation like any other inferred default.
- **Scope honesty:** M8.1 changes artifacts, validation, and reporting. It does not check that
  a required experience has an exact route, does not add surface-parity checks, does not
  implement backtracking, and does not widen the capability graph.

## Case 1 - exact Card keeps a one-line claim

**Input**

> Make a 1-Energy Common Attack called Ember Step. It deals 9 damage, upgrades to 12, and
> uses placeholder art.

**Expected behavior**

1. Stay on the fast route and ask no question, including no question about the deliverable.
2. Write a claim naming one playable Card the user can add to a run and play in combat, with
   `shape` describing one Card.
3. Record the effect as one required experience settled by `tier-2-structured`, and the
   template portrait as one required experience settled by `user-decision`. Do not invent
   experiences for rarity, pool, or target defaults nobody asked about.
4. Record at least the absent custom art in `excluded_experiences`, plus the absence of other
   content the phrase "a card" could be read to imply.
5. Restate the claim in one sentence at the combined confirmation, alongside what it does not
   include, without turning it into a second approval round.

**Failure signals**

- asks the user what kind of deliverable or what scale they want;
- writes a claim that restates the SPEC operation list instead of what the user gets;
- creates one experience per SPEC operation;
- records the placeholder as `tier-1-load` or `tier-2-structured` rather than an accepted
  difference; or
- omits `excluded_experiences` because the request was simple.

## Case 2 - Character content set names its slice and its exclusions

**Input**

> Build me a Frost Oracle character with a card pool, so I can try it out and see if the
> mechanic feels right.

The user accepts a first playable slice with a native-shaped starter deck, a Starter relic,
a small reward pool, and placeholder presentation.

**Expected behavior**

1. Use co-design, load the Character Foundation grammar, and resolve the mechanic decision
   before writing the claim.
2. Write a claim that says what the user can actually do — start a run as this Character and
   play the accepted slice — with a `shape` describing the slice honestly rather than implying
   a finished Character.
3. Record required experiences for the identity-bearing behaviors the user would check first,
   each traced to its current design items. The starter-mechanic behavior is
   `tier-2-structured`; Character selection appearing in the real UI may be `tier-1-load`;
   any presentation the user would have to look at is `headed-human`.
4. Record the accumulated exclusions as one list: placeholder presentation across every
   surface, the reward pool's slice scale, and every accepted composed-instead-of-replaced or
   fallback behavior. This is the case the list exists for — each was individually acceptable
   and the combined result is what the user actually receives.
5. Do not promote a deferred future item into a required experience because the fantasy is
   compelling, and do not let the claim describe the eventual complete Character.

**Failure signals**

- claims a run-capable or complete Character when the accepted slice is smaller;
- lists placeholders only inside individual scope rows, never as one combined statement;
- assigns `tier-2-structured` to art or feel;
- creates required experiences for deferred content; or
- asks the user to approve the claim separately from the DESIGN/SPEC confirmation.

## Case 3 - the harness never drove it, so the report may not claim it

**Input**

A Card whose required experience is a top-X draw-pile inspection settled by
`tier-2-structured`. Build and tier-1 pass. The harness reports `selftest done`, but no state
proof for that experience appears in the log, and the run's own record notes the scenario was
not driven.

**Expected behavior**

1. Settle that `E-###` as `unobserved` with a note saying the structured proof for it is
   absent, or as an `exception` if the harness never reached its scenario at all. Never as
   `observed`.
2. Keep the distinction `INV-1` requires: a harness that could not reach its scenario is
   tier-1, not a tier-2 failure of the Mod.
3. Fail `deliverable_trace.py --design DESIGN.md --plan PLAN.md` if the ledger claims
   `observed` on tier-1 evidence for a `tier-2-structured` experience, or if any required
   experience has no settlement at all.
4. Generate the user-facing summary from the ledger: state plainly which experience was not
   proved and what is missing. An aggregate line such as "all behaviors observed" is not a
   substitute for the missing per-experience proof.
5. Do not delete the experience, weaken its `settled_by`, or move it into
   `excluded_experiences` to make the report clean.

**Failure signals**

- reports the experience as delivered, verified, or working;
- relies on an unconditional aggregate assertion as evidence for a specific experience;
- downgrades `settled_by` after the fact so the available evidence qualifies;
- silently drops the experience from the claim; or
- reports a harness setup failure as a behavior failure of the Mod, or the reverse.

## Review record

Record the reviewer, date, cases inspected, and any deviation. A static contract pass and
validator tests mean only that the shipped workflow contains and mechanically checks these
contracts. A forward-model run, if later authorized, must record its actual artifacts and may
not be inferred from this file.

- **2026-08-10 source-contract review:** Claude Code inspected all three cases against
  `route.md`, `interview.md`, `design.md`, `spec.md`, `verify.md`, `repair.md`, `SKILL.md`,
  and `deliverable_trace.py`. The source instructions state the claim before SPEC, keep
  `shape` free text, separate experience from requirement and operation, restate the claim at
  confirmation, settle each experience against evidence its method accepts, and generate the
  final report from the ledger. Six validator negative cases were run directly against
  fixtures: an `observed` outcome on insufficient evidence, a missing settlement, an
  `exception` with no note, an experience tracing to a non-current design item, an empty
  `shape`, and a non-taxonomy `shape` wording that must pass. No independent forward-model
  output was produced or reviewed, and no generated Mod, game launch, Tier 1, or Tier 2 run is
  claimed by this Package.
