# Implementation plan: M8 end-to-end product integrity

## Status

Version `0.6.0` remains the unreleased RitsuLib-only development baseline for STS2 stable
`0.107.1` and RitsuLib `0.5.4`. The BaseLib migration and M6.5-M6.7 implementation tracks
are closed.

M7 Design Intelligence and User Experience is also closed by explicit human-lead decision
on 2026-08-05. M7.1 through M7.5 are implemented in source and synchronized into the
plugin and portable payloads. M7.6 closed through the external human-led Watcher
whole-skill evaluation recorded in
`documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`; no M7.6 source Package or
successful tuning result is inferred.

M8 End-to-End Product Integrity is the active planned milestone. It turns the Watcher
evaluation's cross-stage findings into changes across modmaker routing, capability
grounding, artifact traceability, repair, content-set scope, cross-platform tooling, and
final installed acceptance. M8.4 Independent Verification and Evidence-Derived Reporting
was removed by the human lead on 2026-08-05; M8.5 and M8.6 retain their numbers.

**M8.0 Skill Structure Restructuring is closed by explicit human-lead decision on
2026-08-10.** All five approved changes are implemented in source and both committed payloads
are synchronized. The shipped pack now reads one file per element, projects its art contract
from code into a catalog, splits diagnostic from preventive rules, states support rather than
which Package promoted it, and states each cross-stage invariant once. Its durable result is
`documents/history/M80_SKILL_STRUCTURE_RESULTS.md`.

Closing it did not resolve everything it found. Three of thirteen recorded cross-check
mismatches remain open and are live contradictions in the shipped pack: two envelope forms
where `semantic-contract.md` claims authority six surfaces do not honor, the character
resource/ordered-buffer envelope-proof split, and the absence of any check comparing a
generated project's `SPEC.md` against its surface envelope. The lead deferred all three to
M8.2 on 2026-08-10, because the envelope decision overlaps M8.2's recorded ownership and the
other two depend on it. Nine of the ten co-located surfaces have never been piloted.

**M8.1 Literal Deliverable Contract is implemented in source** and synchronized into both
payloads on 2026-08-10. Its execution contract was written against the structure M8.0 left
behind and confirmed with the human lead, including the three decisions it left open. Every
`DESIGN.md` now carries one deliverable claim, and Finalize reports from a `PLAN.md` settlement
ledger rather than free prose. Focused tests are `298/298`. Closing the Package remains a
human-lead decision. The durable result is
`documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md`.

M8.2-M8.6 are recorded as intent only: the plain-language result in the Package Plan table is
the whole of their current planning.

Neither closed Package authorizes a new acceptance Mod, payload publication, or a GitHub
release.

## New-Session Start Protocol

A new coding session must not re-plan M8 from scratch. After reading `AGENTS.md` and the
active documents, it must use this sequence:

1. Read the Package Status table below and, for the first Package marked **Next selectable**
   or **In progress**, its execution contract if it has one. M8.2-M8.6 currently hold intent
   only; the M8.0 and M8.1 contracts are retained as records of completed work and must not
   be re-executed.
2. If the human lead says only "start M8" or "continue M8", select or resume that Package.
   Do not ask the human to choose among later Packages and do not begin the final acceptance.
   If the Package to resume is M8.2-M8.6, its execution contract must be written and
   confirmed with the human lead before implementation, against the current file layout.
3. Read the listed authoritative source files before editing. Inspect current dirty changes
   and preserve unrelated work, especially `usertest_M76/`.
4. Implement only that Package's work order. A later Package may be read for interface
   compatibility but may not be implemented early.
5. Run only the Package's listed proportional checks unless the human lead narrows or
   reserves verification. Never turn an intermediate Package into a fresh whole-skill Mod.
6. Write the named history result and update this status table. Review `AGENTS.md`,
   `README.md`, `documents/PROJECT.md`, `documents/BASELINE_RESEARCH.md`,
   `documents/history/README.md`, `games/sts2/tests/README.md`, and
   `games/sts2/tests/content-capability-graph.md`; edit only the files whose owned facts
   changed, and list checked-but-unchanged current documents in the result record.
7. Source changes under `games/sts2/` require regenerated and validated plugin and portable
   payloads. Do not hand-edit payloads, commit, merge, publish, or start the next Package
   without the corresponding instruction.

If the named Package's prerequisite is not closed, stop and report that exact dependency.
If current source contradicts an execution contract, preserve the product invariant, record
the smallest plan correction in this file, and explain it rather than silently improvising.

## Product Problem

The current workflow can produce a Mod for which every local stage has a plausible pass
while the final player-facing result has drifted from the original intent:

```text
locally implementable + locally verified + separately accepted fallbacks
    != end-to-end faithful + evidence-bound + reproducible
```

M8 must preserve one literal product contract from request through observed result. It
must distinguish what is being delivered, resolve exact authoring routes before generation,
backtrack on semantic change, keep runtime behavior and every required player-facing rule
surface together, and reproduce the installed workflow without self-modification or leaked
child processes.

This cannot be implemented as a growing prompt checklist of named mechanics. Existing
DESIGN decisions, SPEC operations, and maintained recipe/reference routes must carry the
smallest machine-checkable semantic facts needed to bind behavior, lifecycle, rules-text
tokens, keyword/DynamicVar and Hover Tip obligations, localization, preview, and
presentation consumers. Do not create a parallel contract or capability truth source when
an existing artifact can own the fact. Behavior and localized explanatory surfaces may be
authored separately, but their shared values, keywords, and invariants must agree.

M8 improves the whole skill. It does not widen the RitsuLib runtime capability graph merely
because the Watcher experiment wanted an unavailable or ungrounded behavior. M8.2 may
promote a reusable generic capability family only after maintainer-owned pinned research,
an exact public/fixed route, semantic-conformance tests, documentation, and payload
validation. If that route cannot be grounded, the literal request remains blocked rather
than receiving an approximate substitute.

## Dependency And Support Boundary

The dependency and Supported Boundary in `AGENTS.md` apply unchanged. The active runtime
inventory remains `games/sts2/tests/content-capability-graph.md`; M8 records implementation
and verification gaps without silently changing Package support. Missing exact routes block
generation, and no M8 work authorizes BaseLib or prompt-derived Harmony, reflection,
Publicizer, or IL.

## Target Flow

```text
plain-language request
  -> literal completion claim and required player experiences
  -> exact semantic capability and presentation preflight
  -> adaptive DESIGN and current/future scope
  -> validated SPEC operation allowlist
  -> scaffold / author / build
  -> repair classification
       -> equivalent technical repair continues locally
       -> player-visible semantic change backtracks to DESIGN/scope/SPEC
  -> existing proportional operation-linked verification
  -> human observation when an experience claim is in scope
  -> literal final report
```

Existing artifact ownership remains:

- `DESIGN.md` owns player intent, accepted decisions, rationale, current/future scope,
  tuning hypotheses, identity anchors, and revision impact;
- `SPEC.md` owns only exact supported operations generated now;
- `PLAN.md` owns literal pipeline stage and backtracking status; and
- project `MEMORY.md` owns resolved technical identities and build/repair facts.

## Package Plan

M8.0 is a restructuring and evaluation layer, not a separate acceptance project: it changes
how the shipped pack is organized, and it is measured by piloting real authoring through the
reorganized pack. There is no separate M8.0 evaluator Mod. The Watcher record remains the
baseline evidence, and the smallest behavioral cases travel with the Package that changes a
decision.

M8.2-M8.6 rows below are intent only. Do not add technical detail to them here; each
Package's execution contract is written when it is selected.

| Package | Status | Prerequisite | Plain-language result |
| --- | --- | --- | --- |
| M8.0 - skill structure restructuring | **Closed 2026-08-10** | M7 closed | The shipped pack is organized so an author reads one file per element instead of three per stage, data lives in queryable catalogs instead of prose, and hardening rules are stated once; contradictions between what a SPEC can declare and what a proof demands become visible. Three found contradictions remain open and moved to M8.2. |
| M8.1 - literal deliverable contract | **Implemented in source 2026-08-10** | M8.0 closed | Before making anything, state the exact completion claim and the player experiences required now; prototype/slice/run-capable labels are optional descriptions, not a closed taxonomy. |
| M8.2 - exact semantic capability conformance and preflight | **Next selectable** | M8.1 closed | Complex mechanics come from one maintained exact implementation; unsupported or broken routes block instead of becoming an approximation. Also owns whether a native engine capability the SPEC grammar cannot yet declare is a grammar gap or a capability-promotion decision, and inherits M8.0's three open envelope mismatches on that same decision. |
| M8.3 - semantic continuity and backtracking | Waiting | M8.2 closed | If implementation or repair changes what the player gets, return to the owning design/spec decision instead of patching forward. |
| M8.5 - cross-platform reproducible installed workflow | Waiting; may be selected independently after M8.1 | M8.1 closed | The committed installed skill works reproducibly on Windows and macOS and cleans up only the process tree it started. Default order remains M8.2 then M8.3 unless the human lead explicitly selects M8.5 earlier. |
| M8.6 - clean installed whole-skill acceptance | Waiting | M8.1-M8.3 and M8.5 closed, plus human-selected request/host | Run one fresh broad request from an untouched installed payload and let the result prove the whole workflow. |

## Package Execution Contracts

M8.2-M8.6 hold intent in the Package Plan table and receive a contract when selected.
Contracts for those Packages were not written in advance, because M8.0 relocated the files
they would name; that layout is now settled, so M8.1's contract is written against it.

The M8.0 contract below is **retained as a closed record**, not as a work order. Do not
re-execute it. Its value to a later session is the found-mismatch list and the reasoning behind
the three left open.

### M8.1 - Literal Deliverable Contract — implemented in source 2026-08-10

**Problem.** The workflow records requirements but never states what the finished thing is.
`DESIGN.md`'s scope ledger is a `D-###` requirement table and `SPEC.md`'s trace is an `OP-###`
generation allowlist. Neither answers "what does the user have when this is done", and nothing
binds the final report to that answer. Four concrete gaps, each located in current source:

1. **No statement of the whole.** The Watcher run delivered a nine-Card vertical slice with
   all-placeholder presentation and several acknowledged fallbacks, and every local stage
   passed. Because no artifact ever said "this will be an evaluable slice, not a run-capable
   Character", the disappointing result violated no contract. (M7.6 finding 1.)
2. **No player-experience obligation.** A `D-###` is a requirement ("Wrath doubles incoming
   damage") and an `OP-###` is a generated operation. "The player enters Wrath and then takes
   more damage" is neither. Watcher's Wrath shipped without the multiplier while all of its
   operations passed.
3. **No link from claim to final report.** `verify.md` § Finalize is a two-branch prose
   template. `INV-1` keeps *tier* reporting honest, but nothing compares the report against
   what was promised. Watcher's closing narrative called Scry verified while the same record
   disclosed that Scry was never driven.
4. **No combined view of accumulated fallbacks.** Each `PLACEHOLDER` is individually accepted
   and `design.md` is explicit that it "remains player-visible current behavior", but no
   artifact reads "all art placeholder + three composed-instead-of-replaced behaviors +
   slice-scale pool" as one player experience. (M7.6 finding 4.)

**Three decisions, confirmed by the human lead on 2026-08-10.**

1. The settlement ledger lives in `PLAN.md`, which already owns literal pipeline and
   backtracking status; experience settlement is the deliverable's completion status.
   `MEMORY.md` keeps its existing job of recording which checks actually ran.
2. `repair.md` gets only a staleness rule: a repair that changes an experience outcome may not
   leave the ledger stale. Substantive backtracking to the owning artifact remains M8.3.
3. The claim is a third independent marked block, not a field inside the scope block. Rationale
   is the existing one-block-one-stamp-one-validator precedent, and an absent block being an
   unambiguous "predates M8.1" signal — the same way an absent coherence block signals
   pre-M7.5. A merged field would force `open-mod-design/v2` plus a migration path, and would
   make "old file" and "author forgot the field" indistinguishable. The recorded cost is a
   third JSON block in `DESIGN.md`, which runs against M8.0's structural compression.

   One argument offered for this decision was wrong and is not part of it: that a merged field
   would collide with a contract version M8.2 must migrate. The SPEC envelope M8.2 owns
   (`sts2-content-semantic/v1`) and the DESIGN scope block (`open-mod-design/v1`) are separate
   stamps. What survives is weaker — M8.2 already carries one migration, and keeping M8.1
   purely additive means a project created between the two Packages passes through one rather
   than two.

**Work order.**

1. **`DESIGN.md` gains `open-mod-deliverable:v1`.** Fields: `claim`, one sentence in the user's
   own terms for what exists when this is done; `shape`, a free-text descriptor
   ("one Card", "nine-Card evaluable slice", "run-capable Character") that the validator checks
   for presence only, never against an enum, because prototype/slice/run-capable are optional
   descriptions and not a closed taxonomy; `required_experiences`, stable `E-###` items each
   carrying a player-observable statement, its `design_ids`, and one `settled_by` method; and
   `excluded_experiences`, what a reasonable reader of the claim would expect that is not
   there. The last field is where gap 4 becomes one readable list.
2. **`settled_by` uses a fixed small set** aligned to what the pack already distinguishes:
   `tier-2-structured`, `tier-1-load`, `headed-human`, `user-decision`. The fourth is
   deliberately not evidence of observation — it records that the user accepted a stated
   difference, which is where an accepted `PLACEHOLDER` lands.
3. **The combined confirmation restates the claim.** `spec.md`'s single
   DESIGN/current-slice/SPEC confirmation currently shows build-now / placeholder / later. It
   adds the claim and the excluded list, so what the user approves before scaffold is the shape
   of the finished thing rather than only requirement rows.
4. **Finalize generates its report from a settlement ledger.** Each `E-###` resolves to
   `observed`, `unobserved`, or `exception` with the evidence that settled it; the user-facing
   summary is written from that ledger. An unsettled required experience may not be reported as
   delivered, and a `headed-human` experience no human observed is an `exception`, never a pass.
5. **New `deliverable_trace.py`, two modes.** Pre-SPEC checks `E-###` form and uniqueness, that
   each traces to at least one current design item, that `settled_by` is in the allowed set, and
   that `claim`/`shape` are nonempty. Finalize checks that every `E-###` has an outcome and that
   no outcome exceeds what its evidence type permits. This is a third validator beside
   `coherence_trace.py` and `design_trace.py`; it earns its place by checking at finalize, where
   neither existing tool runs.
6. **No `INV-9`.** The claim-versus-report rule fires at finalize only, and `invariants.md`
   deliberately keeps single-stage rules where they fire, as the repair attempt cap and the
   art-consent boundary already do. The rule belongs in `verify.md`.
7. **Resume compatibility.** A project without the block resumes unchanged, reusing the
   pre-M7.5 coherence precedent. Any new or revised design writes it.

**Out of scope, stated so it is not absorbed.** M8.1 does not check that a required experience
has an exact route (M8.2), does not add text/keyword/Hover-Tip/localization parity checks
(M8.2), does not implement backtracking when an experience fails (M8.3), does not run a fresh
acceptance Mod (M8.6, unauthorized), and does not widen the capability graph.

**Proportional checks.** Prompt, tooling, and documentation only; no generated runtime behavior
or presentation changes, so no game launch. Focused Python tests plus regenerated and validated
plugin and portable payloads. Behavioral cases are
`games/sts2/tests/m81-deliverable-contract-scenarios.md` with
`tools/tests/test_m81_deliverable_contract.py`: an exact Card whose claim stays one line, a
Character/content-set claim that names its slice shape and excluded experiences, and a
claim-versus-report mismatch where the harness reached only tier-1 — the generalized form of
Watcher's Scry overclaim.

**Outcome.** Every item in the work order is implemented in source and both payloads are
synchronized. Focused tests are `298/298`, up from `256`. Two pre-existing tests were repaired
rather than the source they tested: one asserted `PLAN.md` owns "stage status only", which the
ledger changes, and one mutated "the first `route:` line in `design.md`" to prove coherence
route-drift detection — a positional replace that used to hit the scope block, now hits the
deliverable block, and had silently stopped testing what it claimed. Adding a third block is
what exposed that latent fragility.

The claim contract checks structure and evidence sufficiency. It cannot judge whether a claim is
the right claim, and a green pre-SPEC run means well-formed rather than delivered. No generated
Mod, game launch, Tier 1, Tier 2, or forward-model run is claimed.

**Result record:** `documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md`.

### M8.0 - Skill Structure Restructuring — closed 2026-08-10

**Problem (as stated when the Package opened).** The shipped pack was organized by authoring
stage, so one element's rules were split across files: a Card's envelope lived in `spec.md`, its
driver body in `author.md`, and its proof matrix in `verify.md`, hundreds of lines apart. Prose
also carried data that belonged in catalogs, diagnostic scars sat on main paths, project history
was mixed into runtime instruction, and hardening rules were restated per stage with drifting
wording.

The layout did not merely cost tokens; it hid a class of defect. When an element's
envelope and its proof matrix cannot be read together, a proof can demand a value the
envelope has no field to declare, and nothing in the workflow surfaces the contradiction.

**Five approved changes.**

1. **Co-locate by element, not by stage.** `surfaces/<element>.md` holds that element's
   {envelope + driver body + proof matrix}. `spec.md` shrinks to shared rules plus a
   pointer to `surfaces/<element>.md`.
2. **Extract data into queryable form.** Art-contract tables and character starting facts
   are data. `design/catalogs/character-foundation-sts2-0.107.1.json` already exists while
   `character-foundation.md` restates the same table in prose. The vanilla-override set is
   the proven pattern in this repository: 1624 models and 4165 fingerprints live in JSON
   while prose states only the rules. Apply that pattern beyond the largest dataset.
3. **Split scars by kind.** Diagnostic scars ("if you see X, the cause is Y") move to
   `errors.md`, which exists for them; the main path keeps only "on failure, read
   `errors.md`". Preventive scars (for example: do not name the working directory after the
   Mod) stay where they fire, compressed to a one-line constraint without full history.
4. **Move project history out of runtime files.** `IMPLEMENTATION_PLAN.md` and
   `documents/history/` already own it. Runtime instruction needs "these operations are
   supported", not "M6.7.1 promoted them".
5. **Consolidate hardening rules.** One `invariants.md` that stages reference instead of
   restating. "Never misreport a Tier" is currently written separately in `SKILL.md`,
   `verify.md`, and `repair.md` with wording that does not match.

**Execution order.** Not 1 through 5. The approved order is: card pilot -> one real run ->
pilot packaging fix -> remaining nine surfaces -> changes 2 and 3 -> change 4 as wrap-up ->
change 5 evaluated separately. The packaging fix was inserted by the human lead on
2026-08-07; see the packaging-defect record below.

**Progress.**

- Card pilot: **done**. `surfaces/card.md` co-located by `c5452d8`.
- One real run: **done and passing**. A pilot Mod authored only through `surfaces/card.md`
  reached `[PASS] Tier-2 verified` on STS2 `0.107.1` with RitsuLib `0.5.4`, asserting 13
  state proofs across base and upgraded play, including result-pile membership.
- Pilot packaging fix: **done**. Present in both committed payloads, which were synchronized
  from source on 2026-08-10 after the nine-surface step.
- Remaining nine surfaces: **done**, source only. All ten are co-located, all ten are
  reachable from `spec.md`, and the nine inline bodies were removed from `author.md`/
  `verify.md` rather than left duplicated. The carry-forward cross-check ran and is recorded
  in `games/sts2/tests/m80-surface-cross-check.md`: eleven mismatches found at that step,
  eight fixed, three left open with reasons.
- Change 2 (extract data into queryable form): **done**, source only. The art contract is
  projected from its code definition into
  `sts2-api/reference/catalogs/art-contract-sts2-0.107.1.json` by
  `gen_sprite.py export-contract`, and the three prose views plus the Character starter table
  are locked to their data by tests that fail in both directions. The comparison found
  mismatch 12: the cue sheet grid was written columns-first in four prose copies and printed
  rows-first by `list-specs`, live on the only non-square sheet. The human lead also approved
  surfacing the Character inventory's native HP range and Starter relic ids, which the loaded
  design grammar had never stated while requiring `starting HP` on every custom Character;
  their effects stay unstated because the pinned catalog has no relic effect text. Focused
  tests are `246/246`, up from `231`.
- Change 3 (split scars by kind): **done**, source only. `quirks.md` and `errors.md` already
  existed as the two homes; the split is now stated as a rule about *when* a line is needed —
  constraints followed before a failure versus signatures matched after one. Three diagnostic
  clusters left the main path (`build.md` § Failure classes, `repair.md`'s per-mechanic
  localization, `verify.md`'s restated tier-1 causes), with four missing signatures and the
  boundary discrimination merged into `errors.md` first; the preventive log-rotation and
  MSB1008/CS8602 rules stayed where they fire, compressed. Net 67 lines off the main path,
  +68 into the catalog. Found a pointer that had never resolved: `verify.md` referenced an
  `errors.md` "Verification harness" section that does not exist, for a console failure the
  catalog had no entry for. `test_surface_cross_check.py` now resolves every `errors.md §`
  pointer. Focused tests are `248/248`.
- Change 4 (move project history out of runtime instruction): **done**, source only. Classified
  ~190 milestone-id occurrences by what the id does, then removed only two classes: bookkeeping
  ("M6.7.1 accepts X" → the reference that owns X) and ids standing in for the artifact that owns
  a contract ("M7.4 owns `DESIGN.md`" → the `design.md` stage owns it). Manifest keys, Tier 2
  markers, resume-compatibility boundaries, and evidence attributions were kept as load-bearing.
  Two real defects surfaced: both route lists stopped at four packages while `build.py` validates
  five, and six reference pages instructed readers to follow the M6.7 batch-window verification
  exception that closed 2026-08-04 — an expired policy authorizing deferral of real-host proof.
  Six tests were repointed from milestone wording to the rule each sentence carries.
  `test_surface_cross_check.py` guards both removed classes and found a seventh expired-policy
  occurrence the manual sweep missed. Down to 45 occurrences. Focused tests are `249/249`.
- Change 5 (consolidate hardening rules): **done**. Reading for the pattern rather
  than the named instance found eight rules in one shape, each a way the product ends up false
  while every local stage passes; they are `INV-1` through `INV-8` in
  `modmaker/invariants.md`. The change as specified had a flaw that had to be corrected first:
  under lazy loading, replacing a rule with a pointer leaves *zero* copies whenever the target
  was not read, which is worse than three drifting copies. So `invariants.md` is the one page
  read at pipeline start and kept in context. Two candidate rules were deliberately left where
  they fire, because each applies at one stage only — the repair attempt cap and the art-consent
  boundary. Recorded as mismatch 13, on a third axis: prose against the same rule stated in
  another file. Focused tests are `256/256`.
- Payload regeneration: **done**. Both committed payloads regenerated from source on 2026-08-10
  after change 5, carrying all five changes. Rendering verified repeatable and the two modmaker
  trees identical; no payload was installed or run.
- Open mismatches 1 and 7: **deferred to M8.2** by human-lead decision on 2026-08-10. The envelope
  form is a contract-version migration that overlaps M8.2's recorded ownership, and mismatch 7's
  destination depends on it. Both remain live contradictions in the shipped pack until M8.2.

Every approved change in this Package's work order is implemented and both payloads are
synchronized. Closing M8.0 and selecting M8.1 remain human-lead decisions.

**The pilot's other two findings.** Both are contract defects, not packaging, and both are
instances of the class the carry-forward cross-check is meant to catch. They are recorded here
so a co-located surface is never mistaken for a validated one:

1. *Engine-composed text must not be re-authored.* A self-exhausting Card must not write
   "Exhaust" in its description: `CardKeywordOrder` appends the keyword text automatically,
   and vanilla `Impervious`/`Offering` carry none of it in their own description. Following
   `surfaces/card.md` as written produces the duplicate. The same risk applies wherever the
   engine or framework composes player-facing text, including mod keywords with
   `includeInCardHoverTip: true` and the Enchantment/Affliction tips folded into a Card's
   `HoverTips`. Fix shape to be decided from the full cross-check, not from the Card alone.
2. *A driver that asserts only the obvious delta under-proves the element.* The documented
   Card driver asserts damage only, so a Card whose core mechanic is its result pile passes
   while that mechanic is broken. Any Card with a non-default result pile owes that assertion
   in the recipe itself. Audit the equivalent identity mechanic per surface: relic trigger
   boundary, Power stack decay/expiry, Potion belt consumption, Orb channel/passive/evoke,
   Enchantment host restriction, Monster move graph, Event option/page coverage, Character
   starter-deck identity.

**Pilot verdict on change 1.** Change 1 predicted that co-location would make "a proof
requires a field the envelope lacks" visible at a glance, and that the gap was partly caused
by the old layout. Both held. The contradiction now reads within one file: the Card envelope
has no field to declare a native keyword, while the same file's proof matrix requires
`result pile` as an invariant, 42 lines apart. Before `c5452d8` those statements sat in
`spec.md` roughly 44 lines apart with a third in `verify.md`, across files. The moved
`relations:` line is byte-identical before and after, confirming the refactor relocated the
text without altering it, so the contradiction predates the refactor and was inherited, not
introduced.

**Recorded weakening of that verdict.** The pilot card was deliberately chosen to force a
non-default result pile, so the test was aimed rather than blind. The supportable claim is
that co-location makes the cross-check possible in a single read, not that it performs the
check. Two enforcement gaps remained open at the pilot; one is now partly closed.
`tools/tests/test_surface_cross_check.py` pairs each mandatory envelope field with the proof
case that observes it, and it found three mismatches the manual ten-surface read had missed,
which is the strongest available evidence that a mechanical check was the missing piece rather
than more careful reading. Still open: `design_trace.py` accepts invented SPEC fields silently,
and nothing checks a *generated* project's `SPEC.md` against its surface envelope. That second
one needs the envelope-form decision recorded as open mismatch 1.

**Carry-forward for the remaining nine surfaces.**

1. Run an explicit envelope-versus-proof-matrix cross-check while co-locating each surface.
2. Collect mismatches across all ten elements before fixing any of them, so one fix shape is
   decided from the full set rather than generalized from the Card alone.
3. Record every mismatch found, including ones left unfixed, so a co-located surface is never
   mistaken for a validated one.

**Packaging defect found by the pilot: fixed 2026-08-07.** The build deployed
`openmod/vanilla-overrides.json` inside the Mod tree, where the game's recursive manifest
scan (`ModManager.ReadModsInDirRecursive`) parses every `.json` at any depth as a Mod
manifest and logs a missing-`id` error for it. Every generated Mod carried it. The human lead
selected it as the first fix, ahead of the remaining nine surfaces, because it cost every
user a frightening undocumented error line; that reorders the approved execution order below
and nothing else.

The sidecar is a build-time input with no runtime consumer, so `scaffold.py` no longer copies
it into `mods/<ModName>/`, and `build.py` now enforces the general rule rather than the single
case: only `<ModName>.json` may be loose JSON in a deployed Mod, a copy left by an older
build is pruned so existing projects self-heal, and any other deployed non-manifest `.json`
fails the build. Authored JSON belongs inside the `.pck`. Proved on Windows in one log: a
fresh probe scanned one manifest with no error and passed Tier 1, while a Mod built by the
older scaffold still showed the phantom error in the same run. An existing installed Mod
keeps the error until it is rebuilt.

**Result record:** `documents/history/M80_SKILL_STRUCTURE_RESULTS.md`.

## Verification Policy

The literal Tier definitions and host ownership in `AGENTS.md` and
`games/sts2/tests/README.md` remain authoritative. M8 contract tests own completion-claim
traceability, route conformance, surface parity, and backtracking; changed runtime or
presentation still uses the nearest real host; platform claims require evidence from the
claimed host; and human observation alone owns experience claims. M8.6 is the only fresh
natural-language acceptance gate and is not authorized to run yet.

## Closed Milestones

Closed migration through M7 results are indexed by `documents/history/README.md`; they are
evidence, not active instruction. Historical records retain the status and exceptions true
at their own close.

## Future Outlook

Multiplayer vanilla overrides, optional Mod settings, and unrelated runtime operation
families remain outside M8 unless a separately selected product need promotes them. M8.2
may promote the reusable generic capability gaps selected by this plan, but only through
the normal grounded support process; it does not authorize arbitrary runtime expansion.
