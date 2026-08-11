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

Closing it found three of thirteen cross-check mismatches that needed a later contract: two
envelope forms where `semantic-contract.md` claimed authority six surfaces did not honor, the
character resource/ordered-buffer envelope-proof split, and the absence of a check comparing a
generated project's `SPEC.md` against its surface envelope. The lead deferred all three to M8.2
on 2026-08-10. M8.2 resolved them by normalizing the six flat envelopes to v2, moving the
Character declarations beside their proof, and adding `spec_envelope_trace.py`. Nine of the ten
co-located surfaces have never been piloted, which is why
`games/sts2/tests/m80-surface-cross-check.md` remains required reading.

**M8.1 Literal Deliverable Contract is closed by explicit human-lead decision on
2026-08-10.** Every `DESIGN.md` now carries one deliverable claim, and Finalize reports from
a `PLAN.md` settlement ledger rather than free prose. Focused tests were `298/298`. Its
durable result is `documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md`.

**M8.2 Exact Semantic Capability Conformance and Preflight is closed by explicit human-lead
decision on 2026-08-10.** All five work-order steps are implemented in source with both payloads
synchronized, and focused tests are `364 passed`. A mechanic that changes a value the engine is
computing is now a declaration rather than prose, preflight resolves and pairs every cited route,
and a hook the declaring surface cannot receive blocks instead of shipping as a method that never
fires. **The two real-host proofs step 3 owed were deferred to M8.6 by the human lead**, so every
hook route is implemented-and-unproved. Four defects were found while spending step 1's catalog,
three of them in this Package's own earlier steps. The durable result is
`documents/history/M82_CAPABILITY_CONFORMANCE_RESULTS.md`.

**M8.3 Semantic Continuity and Backtracking is closed by explicit human-lead decision on
2026-08-11.**
M8.5-M8.6 remain intent only: the plain-language result in the Package Plan table is the whole
of their current planning. No Package authorizes a new acceptance Mod, payload publication,
or a GitHub release.

## New-Session Start Protocol

A new coding session must not re-plan M8 from scratch. After reading `AGENTS.md` and the
active documents, it must use this sequence:

1. Read the Package Status table below and, for the first Package marked **Contract drafted;
   awaiting confirmation**, **In progress**, or **Implemented; awaiting closure**, its execution
   contract. M8.0-M8.3 are closed records; do not re-execute them or begin M8.5/M8.6 without
   later human-lead selection and a confirmed execution contract.
2. If the human lead says only "start M8" or "continue M8", select or resume that Package.
   Do not ask the human to choose among later Packages and do not begin the final acceptance.
   If the Package to resume is M8.3-M8.6, its execution contract must be written and
   confirmed with the human lead before implementation, against the current file layout.
3. Read the listed authoritative source files before editing. Inspect current dirty changes
   and preserve unrelated work.
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

M8.3's row is backed by the closed execution contract below. M8.5-M8.6 remain intent only;
do not add technical detail to those rows until each Package is selected.

| Package | Status | Prerequisite | Plain-language result |
| --- | --- | --- | --- |
| M8.0 - skill structure restructuring | **Closed 2026-08-10** | M7 closed | The shipped pack is organized so an author reads one file per element instead of three per stage, data lives in queryable catalogs instead of prose, and hardening rules are stated once; contradictions between what a SPEC can declare and what a proof demands become visible. Three found contradictions were deferred to and resolved in M8.2. |
| M8.1 - literal deliverable contract | **Closed 2026-08-10** | M8.0 closed | Before making anything, state the exact completion claim and the player experiences required now; prototype/slice/run-capable labels are optional descriptions, not a closed taxonomy. |
| M8.2 - exact semantic capability conformance and preflight | **Closed 2026-08-10** | M8.1 closed | Complex mechanics come from one maintained exact implementation; unsupported or broken routes block instead of becoming an approximation. Resolved M8.0's three deferred envelope mismatches on that same decision. Its two real-host proofs were deferred to M8.6. |
| M8.3 - semantic continuity and backtracking | **Closed 2026-08-11** | M8.2 closed | If implementation or repair changes what the player gets, return to the owning design/spec decision instead of patching forward. |
| M8.5 - cross-platform reproducible installed workflow | Waiting; may be selected independently after M8.1 | M8.1 closed | The committed installed skill works reproducibly on Windows and macOS and cleans up only the process tree it started. Default order remains M8.3 unless the human lead explicitly selects M8.5 earlier. |
| M8.6 - clean installed whole-skill acceptance | Waiting | M8.1-M8.3 and M8.5 closed, plus human-selected request/host | Run one fresh broad request from an untouched installed payload and let the result prove the whole workflow. Also carries the two hook-participation proofs M8.2 deferred: one incoming-damage multiplier with its neutral case, and one collection edit preserving unrelated entries. |

## Package Execution Contracts

M8.3's confirmed contract below is closed and retained as a record. M8.5-M8.6 still hold intent
only in the Package Plan table.

The four closed contracts below are **retained records**, not work orders. Do not re-execute any
of them. M8.0's value to a later session is its found-mismatch list and the reasoning
behind the three it deferred; M8.1's is the deliverable-claim decisions M8.2 built on; M8.2's is the
hook-reachability rule, the four defects it found in its own earlier steps, and the two proofs it
handed to M8.6.

### M8.3 - Semantic Continuity and Backtracking - closed 2026-08-11

**Authorization boundary.** This contract was written against the current post-M8.2 layout and
confirmed by the human lead on 2026-08-11. Implement only the work order below and preserve
unrelated work. Do not install either payload, create an acceptance Mod, launch the game, commit,
or push without later instruction.

**Problem.** The workflow now knows what it promised (M8.1) and whether a selected semantic route
exists and claims the exact capability (M8.2), but it still does not decide what to do when Author,
Build, Verify, headed observation, or Finalize discovers a difference. `repair.md` clears stale
experience settlements, then explicitly says that deciding whether the repair changed what the
player gets is not its job. The existing revision route starts for a user-requested change or
user-supplied playtest observation; it is not entered automatically when the pipeline itself finds
semantic drift.

That is the unresolved M7.6 finding: player-visible repairs moved forward locally instead of
returning to DESIGN, scope, SPEC, and trace validation. It is also where two other M7.6 findings
meet: behavior, lifecycle, rules text, keyword/Hover-Tip discoverability, localization, preview,
and presentation were not treated as one player-facing operation, and an approximate consumer-
local mechanic could replace the requested one. M8.1 deliberately left substantive backtracking
here. M8.2 blocks an absent or claimed-but-broken shared route, but explicitly left semantic-impact
backtracking and full surface continuity out of scope.

**Artifact ownership.** Do not create a second design, capability, or semantic truth source.

1. `DESIGN.md` remains the owner of player intent, accepted semantic decisions, the literal claim,
   `E-###` experiences, current/future scope, identity anchors, and the `Q-###` revision queue. Any
   accepted change to what the player gets returns here first.
2. `SPEC.md` remains the owner of the exact supported `OP-###` operations generated now. A missing
   lowering detail that is already required by accepted DESIGN is contract fulfillment, not a new
   creative decision; correct SPEC and revalidate without silently changing DESIGN.
3. `PLAN.md` remains the owner of current pipeline and backtracking status plus settlement state.
   Add one `open-mod-repair-routing/v1` marked block whose `active_repair` is either `null` or one
   current repair decision. It records only the trigger stage, observed difference, one of the four
   classifications below, owning artifact, affected `D/E/OP` ids, invalidated stages, and current
   routing status. It is resumable state, not a history log or semantic contract.
4. Project `MEMORY.md` remains the owner of the exact signature, observed values, hypothesis,
   attempted technical change, resolved adapter facts, and completed repair history. It may never
   revise DESIGN or SPEC by implication. When the PLAN block clears after convergence, the concise
   completed record moves here.
5. A shipped recipe/reference and its route-local capability metadata remain the owner of a shared
   implementation contract and its smallest known limitation. An absent or broken route is fixed
   or narrowed there by a maintainer; the consumer project does not acquire a private substitute.

`repair_trace.py` validates the PLAN routing block against the existing DESIGN deliverable/scope/
coherence blocks and SPEC operation trace. It checks ids, classification/owner combinations,
allowed classification/status combinations, settlement invalidation, and the earliest reopened
stage. It does not judge whether observed behavior is correct and does not duplicate route
capability metadata.

**Four repair routes.** Classification happens before an attempted fix. A visible difference is
`INV-5` even when it is discovered after Author; extend that invariant's firing stages through
Verify, Repair, and Finalize rather than adding a tenth invariant.

1. **`implementation-equivalent`.** The fix changes no player-facing behavior, lifecycle, rule,
   value, localization meaning, preview, presentation, deliverable claim, or proof meaning. Typical
   examples are a grounded namespace/import, manifest path, packaging path, or harness navigation
   correction. `MEMORY.md` owns the technical fact. Keep DESIGN and SPEC unchanged,
   apply one bounded fix, and rerun the minimum failed stage (rebuilding first whenever project
   output changed). A harness/setup failure stays distinct from a Mod behavior failure.
2. **`contract-fulfillment`.** Observed output or an incomplete lowering fails an already accepted
   DESIGN/SPEC operation, while the exact shared route remains supported and conformant. Preserve
   the accepted `D/E/OP` meaning. Correct the earliest wrong layer: SPEC when it omitted an already
   accepted required field, otherwise generated source/resource/localization/proof. Clear affected
   settlements, reopen the earliest affected stage, and reverify every applicable consumer named
   by the owning surface envelope/proof matrix. No user re-decision is needed because the promised
   result does not change; uncertainty about that fact forces `accepted-semantic-change` instead.
3. **`accepted-semantic-change`.** The proposed fix would change anything a player can notice or
   understand: trigger, target, ordering, movement, value, lifecycle, text meaning, tooltip,
   fallback, preview, presentation, or deliverable shape. Stop before applying it. Route the
   smallest delta through revision, update DESIGN first (claim, affected `E-###`, scope, anchors,
   and `Q-###` queue as applicable), obtain explicit user acceptance, then update only affected
   SPEC operations and run the existing validators. Reopen only invalidated PLAN stages and clear
   affected settlements. Rejection preserves the original decision and leaves the project blocked
   or returns it to contract fulfillment; it never licenses the convenient substitute.
4. **`missing-capability`.** The required route is absent, is public but lacks maintained
   authoring, cannot reach the selected surface, or exists but fails its claimed contract (`INV-3`
   and `INV-9`). Stop the consumer repair loop; this does not consume one of its three attempts.
   Record the exact project gap and upstream learning candidate, block the affected operation, and
   repair/narrow the shared route before any project resumes. No consumer-local approximation,
   generated Harmony/reflection/Publicizer/IL, or installed-pack edit is permitted. If the user
   later selects a genuinely different supported result, that transition is
   `accepted-semantic-change`, with normal DESIGN-first confirmation.

**Semantic-continuity rule.** Classification compares the observed result with the complete
selected operation, not only the assertion that happened to fail. For each affected `OP-###`, read
its existing surface envelope, driver, proof matrix, and cited route together. Review every
applicable consumer of the shared fact: behavior, lifecycle/state/reset, rules text and engine-
composed text, keyword/DynamicVar/Hover Tips, shipped localization meaning, preview values,
presentation, and proof. `not applicable` stays legitimate when the surface/route says why. Do not
add a universal field to every surface or a second dependency catalog. Shared values stay in their
current owning SPEC field and route; repair routing only makes downstream invalidation explicit.

**Complete scenario matrix.** The repository-owned behavioral file is
`games/sts2/tests/m83-semantic-continuity-scenarios.md`. It covers all of the following, with each
case naming the classification, owning artifact, ids preserved or changed, stages reopened, user
question rule, and exact stop/resume condition.

*Implementation-equivalent cases*

1. A grounded namespace, manifest, or package-path correction makes the same frozen operation
   build/load; DESIGN/SPEC stay semantically unchanged and only the required downstream stage runs.
2. `selftest FAILED` or timeout proves the harness did not reach its scenario; repair navigation or
   timing without changing the Mod, or finalize the experience as an exception. Never rewrite the
   element to satisfy a harness setup failure.
3. A proposed "technical" fix also changes text meaning, a fallback, or proof expectation; it is
   rejected from this class and routed to `accepted-semantic-change`.

*Contract-fulfillment cases*

4. A Card promised to Exhaust deals the correct damage but enters Discard, or its engine-composed
   Exhaust meaning is absent from the player-facing result. Preserve the decision and operation;
   repair lifecycle/text at the earliest wrong layer, then reverify damage, result pile, and text.
5. A declared incoming-damage multiplier fires for its owner but returns a non-neutral value for
   unrelated targets/damage. Preserve DESIGN/SPEC, repair the generated guard/neutral body, and
   require both modified and neutral proofs. This is a source-contract scenario, not the deferred
   M8.6 real-host proof.
6. Runtime behavior is correct but a shared value is stale in rules text, DynamicVar/Hover Tip,
   localization, preview, or real presentation. Update every applicable consumer from the same
   owning SPEC field and reverify only those consumers; do not call this a cosmetic equivalent.
7. DESIGN already requires an exact player result but SPEC omitted one required surface field.
   Correct SPEC and its trace as fulfillment, preserve the accepted DESIGN ids, rerun all four
   pre-scaffold validators, then reopen Author/Build/affected Verify without asking the user to
   choose the same result again.

*Accepted-semantic-change cases*

8. A third-turn relic is easier to implement as "after three Attacks". Stop; the timing and player
   decision changed. Continue only after a DESIGN-first revision and explicit acceptance.
9. A requested complete description replacement can only compose before/after vanilla text, or a
   requested multi-target behavior would become single-target. The exact visible difference is
   confirmed, deferred, or removed; it is never patched forward.
10. Custom art acquisition fails and placeholder art was not already an accepted fallback. After
    acceptance, add a `PLACEHOLDER`, excluded experience, and affected `E-###` with
    `settled_by: user-decision`; Finalize later settles it from that acceptance. An already accepted
    checked fallback remains contract fulfillment/normal fallback, not a new question.
11. Several individually proposed fallbacks change the literal deliverable shape or an identity
    anchor. Re-read the combined claim/exclusions, update them together, and require one bounded
    confirmation rather than accepting each local patch in isolation.

*Missing-capability and boundary cases*

12. No route exists, or the public Package exists but maintained authoring is missing. State which
    fact applies, record a blocking gap, and stop without an invented API or a consumed repair
    attempt.
13. A cited shared route resolves and passes preflight but observed reality violates its documented
    capability. Block and repair/narrow the shared route under `INV-9`; a consumer-local copy is not
    contract fulfillment.
14. The user supplies playtest feedback that changes balance or feel. Preserve it as user evidence
    and use the existing revision route; do not automatically diagnose or tune it. Once the exact
    semantic delta is accepted, its downstream path follows `accepted-semantic-change`.
15. An unchanged pre-M7.5, pre-M8.1, or v1-SPEC project resumes under its existing compatibility
    rule. Do not backfill repair state. If a new repair begins, create only the active PLAN routing
    block; if it becomes a semantic revision, add/update the current contracts exactly as the
    existing revision migration rules require, without inventing old evidence.

**Source scope.** Implementation is limited to the workflow and its checks:

- `games/sts2/skills/modmaker/SKILL.md`, `invariants.md`, `route.md`, `design.md`, `spec.md`,
  `semantic-contract.md`, `author.md`, `build.md`, `verify.md`, and `repair.md` for classification,
  state transitions, artifact return order, invalidation, and Finalize blocking;
- `games/sts2/tools/repair_trace.py` as the one new PLAN-state validator, plus the existing
  validators only where integration is required;
- `games/sts2/tests/m83-semantic-continuity-scenarios.md` and
  `games/sts2/tools/tests/test_m83_semantic_continuity.py`, with focused updates to invariant,
  M7.5 revision, M8.1 settlement, payload-layout, and surface-cross-check tests when their owned
  contract changes; and
- current documents at closure only where their owned status/test facts change, plus the named
  result record.

Review all ten `surfaces/*.md` envelope/proof pairs, but do not rewrite them as a batch. Change a
surface page only if a matrix case proves its current co-located envelope/proof cannot express the
required continuity or invalidation. Do not edit `sts2-api/errors.md` without a new proven
signature, and do not modify a runtime recipe/reference merely to manufacture an M8.3 example.

**Work order.** Execute in this order after confirmation:

1. **State and ownership.** Add the minimal current-repair block to the PLAN template and
   `repair_trace.py`. Validate ids against existing DESIGN/SPEC blocks, enforce the four
   classification-to-owner mappings, and keep completed technical history in MEMORY. Prove old
   PLAN files with no block resume unchanged.
2. **Classification at every discovery point.** Wire Author visible differences, Build failures,
   Tier-1/Tier-2/headed differences, Repair, and Finalize into the classifier before a fix. Extend
   `INV-5`'s firing list rather than adding a duplicate invariant. Only
   `implementation-equivalent` and `contract-fulfillment` enter the bounded three-attempt loop.
3. **Artifact-owned transitions.** Implement the four routes exactly: local minimum rerun;
   fulfillment at the earliest wrong SPEC/output layer; DESIGN-first user-confirmed revision;
   or shared-route block. Clear affected settlements and reopen only the earliest invalid stage.
   State check must resume an active repair instead of skipping to the old first unchecked box.
4. **Complete-operation impact.** Make Repair and revision impact inspection use the existing
   surface envelope/driver/proof and cited route as one operation view. A changed shared value or
   meaning invalidates all applicable behavior/lifecycle/text/tip/localization/preview/
   presentation/proof consumers, while unaffected operations and `PRESERVE` decisions remain
   untouched.
5. **Scenarios, checks, and synchronization.** Implement all fifteen cases, include negative and
   mutation checks that fail when classification/owner/invalidation enforcement is removed, run
   the proportional checks below, regenerate both payloads from source, write the result record,
   and synchronize only current documents whose facts changed.

**Proportional checks.** This Package changes workflow instructions and project-state validation;
it does not add or change a C# runtime route. Therefore it does not schedule a game launch, Tier 1,
Tier 2, headed review, or fresh generated Mod.

1. Focused Python tests for `repair_trace.py`, all fifteen scenarios, legacy PLAN resume,
   classification/owner/status combinations, affected-id references, settlement
   invalidation, minimum stage reopening, and rejection of a silent semantic substitute.
2. Mutation/neutered-validator checks for each load-bearing rejection branch. A negative fixture
   must fail for the intended reason after its enforcement is removed.
3. Existing M7.4/M7.5/M8.1/M8.2, invariant, surface-cross-check, and payload-layout tests, followed
   by the full `games/sts2/tools/tests` regression and Python compilation.
4. Source plus both generated-payload skill validation; run the shipped `repair_trace.py` from a
   payload-shaped scratch layout; regenerate each payload twice and require repeatability plus
   plugin/portable effective parity. Do not install either payload.
5. `git diff --check` and scoped status/diff review. No commit, push, merge, publication, or release
   without later instruction.

The scenarios and tests establish the shipped routing contract and deterministic artifact state.
They do not prove that a generated Mod behaves correctly, that a human accepts a semantic change,
or that every surface is good in-game. Those remain literal runtime/human evidence when a future
consumer selects them.

**Out of scope.** Do not absorb any of the following into M8.3:

- a new engine capability, hook, helper, recipe, support row, or broad route-conformance repair;
- a second semantic dependency catalog, new mechanic-name checklist, or duplicate DESIGN/SPEC
  truth block;
- repair of the historical Watcher project or replay of its evaluation;
- the two M8.2 hook-participation real-host proofs, which remain deferred to M8.6;
- cross-platform installed-workflow/process-tree ownership (M8.5);
- a fresh natural-language acceptance Mod or final whole-skill judgment (M8.6);
- automatic balance/tuning decisions, simulated human acceptance, or subjective quality claims;
- changed Tier definitions, a replacement reporting subsystem, or revival of removed M8.4;
- blanket migration/backfill of unchanged legacy projects, wider multiplayer support, BaseLib,
  prompt-derived Harmony/reflection/Publicizer/IL, installed-pack edits, or payload installation;
  and
- commit, push, merge, publication, release, or starting M8.5/M8.6 without separate instruction.

**Result record:** `documents/history/M83_SEMANTIC_CONTINUITY_RESULTS.md`.

**Closed by explicit human-lead decision on 2026-08-11.** All five work-order items are implemented in source
and both generated payloads. The focused/related/full regressions, Python compilation, six skill-
root validations, payload-shaped validator run, repeatability, effective parity, and diff hygiene
pass. No Mod was generated or installed, and no game, Tier 1, Tier 2, headed, commit, or push run
occurred. The named result record contains the exact evidence and exceptions. Closure does not
select M8.5 or authorize M8.6.

The closure record names every work-order item, each scenario/check actually run, exact exceptions,
payload synchronization evidence, current documents changed, and current documents reviewed but
left unchanged. The explicit closure decision does not select M8.5 or authorize M8.6.

### M8.2 — Exact Semantic Capability Conformance and Preflight — closed 2026-08-10

**Problem.** The workflow can pass every local stage while the identity-critical behavior the
user asked for is absent. M7.6's Wrath is the reference case: the user asked for a stance that
doubles incoming damage, `SPEC.md` recorded the requirement, an operation was generated, the
harness passed, and the multiplier was never implemented. Nothing in the pipeline could catch
it, for three separate reasons this Package owns:

1. **The SPEC grammar cannot declare it.** `surfaces/power.md`'s envelope has fields for the
   effect, its lifetime, its amount domain, and its display. There is no field in which "this
   Power multiplies damage its owner receives" is a *declaration* rather than prose inside the
   effect text. A value stated only in prose is not checkable by anything downstream.
2. **The route pointer does not have to be real.** `design_trace.py`'s `supported_route` regex
   accepts `#anchor`, but `validate_files` split the anchor off and checked only that the file
   existed. Verified: `reference/art-contract.md#placeholder`, shipped as the canonical example
   in `spec.md`, points at an anchor that has never existed in that file. Every generated
   project has been copying it.
3. **A route that exists need not cover the operation.** Even with a resolving pointer, nothing
   checked that the cited route documents the semantics `OP-00N` needs. Watcher's Wrath cited a
   real route; the route simply had no multiplier line, so the author improvised and the
   improvisation was empty.

M8.2 also inherits M8.0's three open mismatches, deferred here on 2026-08-10 because the
envelope-form decision is a prerequisite for the other two.

**Grounding research, completed before the contract was confirmed.** Done against
`baselines/decomp/sts2_full` (pinned `0.107.1` decompile) and `baselines/STS2-RitsuLib/src`
(`0.5.4`), per the maintainer research order in `sts2-api/grounding.md`. Recheck each promoted
fact against the pinned assembly before it ships, since the decomp sidecar's provenance was not
retained.

The Wrath capability exists and is public: `AbstractModel.ModifyDamageMultiplicative` is
`public virtual decimal`, default `1m`, with 25 vanilla implementors across Powers and Relics.
`ModPowerTemplate : PowerModel : AbstractModel` seals nothing except `ExtraHoverTips`, and
`PowerModel.ShouldReceiveCombatHooks => true`. `VulnerablePower` is the exact "damage received
x 1.5" precedent, and it declares its multiplier as a `DynamicVar` so the number reaches the
rules text through the same substitution the pack already documents. So this is `INV-3`'s first
clause — a public route the pack has not written authoring for, which is **missing authoring
work, not an unsupported API**. It needs no capability promotion.

**Three decisions, confirmed by the human lead on 2026-08-10.**

1. **Envelope: normalize the six flat surfaces to the canonical nested form and bump to
   `sts2-content-semantic/v2`.** Potion, Power, Orb, Monster, Event, and Character move from a
   flat `element:` opening plus ad-hoc top-level keys to `content:/surface:` with the nine shared
   sections. Card and Relic already comply. Rationale: mismatch 8's remaining half — checking a
   *generated* project's `SPEC.md` against its surface envelope — needs one schema to check
   against, and two legal shapes means no schema. Cost: six pages plus a migration path, and the
   `semantic-contract.md` requirement that an envelope change carry a version bump and migration
   note is honored rather than waived.
2. **Hook scope: open all reachable hooks, not a curated subset.** Symmetry with the
   vanilla-override side, which already catalogs 26+28 for vanilla owners; a custom Power should
   not be able to do less to itself than a vanilla override can do to someone else's Power.
   Bounded by two hard constraints: a hook is authorable on a surface only where that surface is
   in the dispatching iterator's listener set, and an Enchantment routes to its five `Enchant*`
   replacements. The recorded cost is that Tier 2 will cover a small fraction of the matrix;
   unproved routes are recorded as unrun, per `AGENTS.md`'s rule that missing verification is not
   missing support.

   **Extended on 2026-08-10, after step 1 reported them:** the 14 `TryModify*` callbacks are also
   in scope, taking the total to 68. They were outside the original 26+28 because neither the
   vanilla reference nor any custom surface listed them. Step 1 found they need **two**
   declaration shapes rather than one, and that two of them are already owned by
   `reference/rest-site-options.md`.
3. **Preflight depth: route + anchor resolution, plus capability-id pairing.** Every `OP-###`
   names the exact semantic capability it consumes; every route page declares the capability ids
   it provides; the validator pairs them. Not the full behavior/lifecycle/rules-text/keyword/
   Hover-Tip/localization/preview/presentation parity sweep — that is larger than one Package and
   mostly resolves to proof-matrix obligations rather than static checks. Deferred explicitly,
   not silently.

**Work order.** Step 1 was a blocking prerequisite for steps 2-4.

1. **The hook catalog. Done.** Extract per hook, from the pinned assembly: exact signature,
   return type, neutral default, dispatching iterator, and the vanilla implementor families.
   Derive reachability per custom surface from the iterator's listener set rather than from a
   heuristic. Emit `sts2-api/reference/catalogs/model-hooks-sts2-0.107.1.json` from a committed
   script in `games/sts2/tools/`, following the `art-contract` precedent exactly: code owns the
   values, the catalog is a projection, prose states only rules, and a test fails when the
   catalog is stale or a prose view disagrees. Never hand-edit it. A hook whose scope the
   extraction cannot resolve is **recorded as unresolved and is not authorable** — a gap, not a
   guess (`INV-3`). Cross-check the derived 26+28 against `vanilla-non-card-overrides.md`; any
   disagreement is a finding about that shipped reference.
2. **Envelope v2 and the migration path. Done.** Normalize the six flat surfaces.
   `semantic-contract.md` becomes v2 with a migration note stating what moved and how a v1
   project is read. Fold in M8.0 mismatch 7: the character resource and ordered-buffer envelopes
   move from `spec.md` into `surfaces/character.md`, joining their proof, now that the target form
   is settled. A v1 `SPEC.md` on an unfinished project resumes unchanged — the same precedent as a
   pre-M7.5 coherence block and a pre-M8.1 deliverable block; only a new or revised SPEC is
   written as v2.
3. **Hook-participation declarations on the surfaces that can receive them. Implemented in
   source; both real-host proofs unrun.** Two declaration shapes, because step 1 found the hook
   surface needs two.

   *Value shapes (60 hooks: 54 scalar-return, 6 out-replacement).* One envelope block carrying the
   semantic capability id, the player-facing statement, the direction/subject guard, the value or
   formula with its `DynamicVar` name when the number appears in rules text, and the neutral return
   outside the guard. Recipes gain the matching authoring line including the guard shape vanilla
   uses (`VulnerablePower` returns `1m` unless the subject is its owner and the damage is a powered
   attack). An `out-replacement` adds only the taken/not-taken flag. Enchantment gets its five
   `Enchant*` routes and an explicit statement that the general hooks are wrong there.

   *Collection shape (8 hooks).* A separate block, because nothing is replaced: it declares the
   entries added or removed, the condition, and the composition rule when several editors touch
   the same list. The vocabulary is bounded — `Reward` has six concrete subclasses, and vanilla
   usage is add-one-under-a-guard with one vanilla remover. `TryModifyRestSiteOptions` and
   `ShouldDisableRemainingRestSiteOptions` are excluded here and route through
   `reference/rest-site-options.md`, whose four boundaries the raw hook does not carry.

   Each declaration owes a proof case, per the `FIELD_PROOF_PAIRS` pattern in
   `test_surface_cross_check.py`. For a value shape: assert the modified value *and* the neutral
   case outside the guard, because a hook that returns its modifier unconditionally passes a
   single-value assertion while breaking every unrelated interaction — the same shape as the Relic
   cadence case. For a collection shape: assert the resulting list contents *and* that unrelated
   entries survive, since an editor that clears the list also passes "my entry is present".
4. **Capability ids and the preflight validator. Done.** Route pages declare the capability ids
   they provide; `OP-###` entries name the id they consume. `design_trace.py` resolves anchors
   against real headings and pairs consumed ids against provided ones, and the shipped
   `art-contract.md#placeholder` example is fixed. An unresolvable anchor, an unprovided id, or an
   operation whose capability has no route entry blocks before SPEC with a message naming what is
   missing. Add the generated-SPEC-versus-envelope check that mismatch 8 left open: a project's
   `SPEC.md` is validated against its surface's v2 envelope — required sections present, no
   invented top-level keys, declared fields belonging to that surface.
5. **The conformance rule for a claimed-but-broken route. Done.** `AGENTS.md` already states that
   a claimed route failing its maintained semantic contract must block until repaired or narrowed.
   Write where that fires: preflight blocks, and the limitation is recorded with the route rather
   than worked around per project.

**Out of scope, stated so it is not absorbed.** Full surface parity across behavior/lifecycle/
rules text/keyword/Hover Tip/localization/preview/presentation (deferred; partly M8.3's
backtracking, partly a later Package). Semantic-impact backtracking (M8.3). Cross-platform
process ownership (M8.5). Any fresh whole-skill acceptance Mod (M8.6, unauthorized). The 100
async hooks on custom surfaces — the current per-surface trigger tables already cover the
selected ones, and widening them is a separate decision. Multiplayer. No new BaseLib, Harmony,
reflection, Publicizer, or IL.

**Proportional checks.** Steps 1, 2, 4, and 5 are prompt, tooling, catalog, and documentation
only — no generated runtime behavior changes, so no game launch, per `AGENTS.md` § Verification.

**Step 3 does change generated runtime behavior and therefore needed a real host.** Two narrow
proofs: a custom Power declaring an incoming-damage multiplier, asserted structurally for the
modified value, the neutral case outside the guard, and the rules-text number matching the applied
multiplier; and one collection edit asserting both its own entry and the survival of unrelated
entries. The first is the smallest thing that proves the Wrath class of failure is closed.

**Both were deferred to M8.6 by the human lead on 2026-08-10 and did not run.** They need Windows,
STS2 `0.107.1`, and RitsuLib `0.5.4`, and M8.6 is the next scheduled run on that host, so they
travel with it rather than triggering a separate launch. This is a recorded exception, not a pass:
until they run, no generated override has been observed firing in a game.

Focused Python tests: the catalog freshness/prose-agreement pair, anchor and capability-id
resolution (positive and negative), the generated-SPEC envelope check, v1-resume compatibility,
and per-surface hook reachability rejection. Behavioral scenarios in
`games/sts2/tests/m82-capability-conformance-scenarios.md`: the Wrath case now blocking or
generating correctly rather than passing empty; a hook requested on a surface that cannot receive
it; and an Enchantment damage multiplier routing to `EnchantDamageMultiplicative`.

Both payloads regenerated and validated at closure. No commit, merge, publish, or release without
instruction.

**Closure status as of 2026-08-10.** All five steps are implemented in source, both payloads were
synchronized, and the human lead closed the Package with the two real-host proofs deferred to M8.6
as a recorded exception. Closure synchronization in item 6 of the New-Session Start Protocol was
completed.

Step 3 delivered one new authoring route, `reference/model-hook-participation.md`, declaring 71
capability ids: the two declaration shapes, the guard-value-neutral body copied from
`VulnerablePower`, the direction rule (`target` versus `dealer`), the damage-kind rule
(`IsPoweredAttack()` excludes Poison-style loss and relic/potion/power damage), engine-fixed
composition order, and the per-surface owner property — `Owner` is a `Creature` on a Power, a
`Player` on Relic/Potion/Orb/Card (so guards need `Owner.Osty` too), and a Monster uses `Creature`
with no owner at all. The seven authorable surfaces each declare the envelope field with their own
reachability note and owe the paired neutral-case proof; the three that no listener set contains
must not declare it, and a test asserts both halves. `spec_envelope_trace.py` now rejects an
unknown capability, a shape the catalog contradicts, a route-owned hook, and — the load-bearing
one — a hook the declaring surface cannot receive. All six rejection tests were verified to fail
against a neutered validator.

Four defects were found and fixed while spending step 1's catalog, three of them in earlier steps
of this same Package:

- **`design_trace.py`'s capability parser could not span lines** (step 4). Without `re.DOTALL` the
  first real declaration parsed as zero ids, so the pairing check silently passed everything. This
  is also why step 4's end-to-end test was skipped rather than failing: no shipped route declared
  a capability, so nothing exercised the parser.
- **`COMBAT_LISTENERS` was missing `modifier` and `badge`** (step 1). Step 1's own second fix
  over-corrected: it concluded the combat-state form reached neither family, but
  `CombatState.IterateHookListeners()` walks `combatState.Modifiers` and `combatState.BadgeModels`
  — what the run-only branch adds is the run-scope *instances*, not the family. Re-extraction left
  authorable surfaces unchanged at 40/23/5 with zero contradictions, and it is recorded as a third
  finding in `games/sts2/tests/m82-hook-catalog-findings.md`. The vanilla cross-check could not
  have caught it: all six vanilla Modifier hook overrides happen to be run-scope, so no vanilla
  evidence contradicted the narrowed set. Silence from a cross-check is not confirmation.
- **`spec_envelope_trace.py` could not find the pack in a payload** (step 4). Its payload path
  candidate was `skills/surfaces`, missing the `modmaker` segment, so the validator `spec.md` tells
  every project to run resolved in the repo and in nothing else. New
  `tools/tests/test_payload_tool_layout.py` builds a throwaway payload-shaped tree and runs the
  shipped tools inside it, so a repo-only path resolution fails a test instead of an install.
- **A pre-existing test asserted no `INV-9` could exist** (M8.1). Narrowed to the
  deliverable-claim rule it was actually about.

**What is not established.** Preflight is static: a green run means the declaration is well-formed,
reachable, correctly shaped, and paired with a route that claims the capability — not that the
generated override fires, returns the right number, or leaves unrelated interactions alone. No
generated Mod, game launch, Tier 1, Tier 2, or forward-model run is claimed for any step. Every
hook route in the catalog is implemented-and-unproved until the two proofs run, which per
`AGENTS.md` is missing verification rather than missing support.

Step 1 produced 68 hooks (26 numeric, 28 decision, 14 `TryModify*`), zero unresolved.
`collect_model_hooks.py` is maintainer-only and excluded from both payloads, following
`collect_vanilla_catalog.py`. The shipped `vanilla-non-card-overrides.md` lists match the assembly
exactly (26 and 28), so that reference needs no correction, and a test now holds the two statements
together. Its five findings are in `games/sts2/tests/m82-hook-catalog-findings.md`:
iterator-decided reachability splitting the list into three authorable groups (40 / 23 / 5), the
five Enchantment redirects, a first derivation that was wrong and was caught by the vanilla
cross-check plus a second data bug in the `run+combat` listener set, the two-shape split in the
`TryModify*` family, and the two hooks already owned by the Rest Site route.

Two consequences carry into step 3. The capability-id mechanism from step 4 is implemented but
idle: no shipped route declares a capability yet, so its end-to-end test skips. Step 3's route
pages are the first real providers and turn that skip into a live test. And the three M8.0
mismatches recorded as open in `games/sts2/tests/m80-surface-cross-check.md` are resolved in source
by steps 2 and 4 but not yet re-recorded there — that synchronization belongs to closure, together
with this file's § Status, both payloads, and the result record.

**Result record:** `documents/history/M82_CAPABILITY_CONFORMANCE_RESULTS.md`.



### M8.1 - Literal Deliverable Contract — closed 2026-08-10

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
