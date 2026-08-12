# Implementation plan: M8 end-to-end product integrity

## Status

M8 is the active milestone. M8.0-M8.3 and M8.5 are closed. M8.4 was removed by
the human lead. Their implementation detail belongs in the named result records under
`documents/history/`, not in this active work plan.

M8.7 Product Boundary Generalization source development is implemented in the current working
tree. Its payload regeneration, active-document synchronization, result record, and explicit
closure are intentionally deferred until M8.8 settles; M8.7 is therefore implemented but still
open. The former detailed M8.7 execution contract has been removed from this active plan because
it is no longer a work order.

M8.8 Surface Effect Composability Generalization is the next Package. Its research and four-part
execution contract were revised by human-lead direction and await confirmation. It owns the cross-surface
finding that early acceptance examples were treated as complete effect boundaries even when the
legal surface lifecycle can compose broader grounded game/framework operations. This drafted
contract is not implementation permission and does not authorize payload generation, document
delivery, install, launch, acceptance, commit, push, publish, or release.

M8.6 remains the final clean installed whole-skill acceptance. It intentionally executes after
M8.7 and M8.8 even though its number is lower: M8.6 must judge the generalized product boundary,
not the fixture-shaped boundary found by the audits. M8.6 remains waiting and has no execution
contract until the human lead selects it after both Packages close.

Current Package order:

1. M8.8 - research complete; detailed execution contract awaits human confirmation.
2. M8.7 - source implemented; combined payload/document delivery and closure wait for M8.8.
3. M8.6 - waiting for M8.7/M8.8 closure and a human-selected request/host.

## New-Session Start Protocol

1. Read root `AGENTS.md`, `documents/PROJECT.md`, `documents/BASELINE_RESEARCH.md`, and this
   file. Treat `documents/history/` as evidence, never as current instruction.
2. Check `git status` before any edit. Preserve unrelated dirty and untracked work.
3. A plan entry is not execution authorization. The first eligible Package is M8.8, but its source
   work must not start until the human lead explicitly confirms the execution contract below. After
   confirmation, `start M8` or `continue M8` resumes that contract at its first incomplete part;
   do not repeat the completed research. If the lead names a Package, verify its prerequisites and
   execute only that Package.
4. Do not start M8.6 while M8.7 or M8.8 is open. Do not reopen M8.0-M8.5 unless the lead
   explicitly requests a repair owned by one of their current contracts.
5. Work in `games/sts2/`. `plugins/open-mod/` and top-level `skills/` are generated payloads;
   never hand-edit them. Generate them only when the selected Package reaches its delivery step.
6. Do not install a payload or run the game merely because a Package contains a proof plan.
   Tier 1, Tier 2, headed review, and fresh acceptance require their own human authorization.
7. Close a Package only after its named result record exists and all active documents that own
   changed facts are synchronized. The result must list active documents reviewed but unchanged.

If a prerequisite is not closed, stop and report that dependency. Do not silently substitute a
later Package, a smaller semantic result, or an ungrounded consumer-local implementation.

## Current Product Contract

The supported workflow remains:

```text
plain-language request
  -> adaptive interview
  -> claim-bearing DESIGN.md
  -> validated current-slice SPEC.md
  -> scaffold
  -> author
  -> build
  -> verify
  -> evidence-bounded final report
```

Generated Mods target STS2 `0.107.1` and the RitsuLib Compat `0.5.4` authoring baseline.
Every promoted fact must be checked against that exact profile. Current website documentation
may describe a newer RitsuLib and is not sufficient. `baselines/decomp` can show that a game
mechanism exists, but it cannot by itself establish a stable authoring route.

Every capability statement must keep three statuses separate:

- **framework-expressible**: the pinned public API can express the behavior;
- **open-mod-authorable**: the pinned capability has a complete shipped lifecycle/parameter
  authoring contract and the current request closes DESIGN/SPEC, project-local C# grounding,
  generation, fallback, and proof through it; prior inclusion in a recipe or proof is not required;
  and
- **game-observed**: the declared shape was exercised in its real host with recorded evidence.

A Tier 2 exception does not make an implemented route unsupported. Conversely, a generated Mod must
still map its exact semantics and implementation through the shipped lifecycle/parameter contracts;
M8.8 establishes those contracts exhaustively for the pinned RitsuLib effect surface rather than
requiring ad hoc promotion or previous proof for each requested effect.

## Package Summary

| Package | State | Durable record or next result | Current relevance |
|---|---|---|---|
| M8.0 - skill structure restructuring | Closed 2026-08-10 | `documents/history/M80_SKILL_STRUCTURE_RESULTS.md` | Surface pages own element envelopes; do not restore stage-duplicated rules. |
| M8.1 - literal deliverable contract | Closed 2026-08-10 | `documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md` | Every new/revised design keeps one literal claim and evidence-settled player experiences. |
| M8.2 - exact semantic capability conformance | Closed 2026-08-10 | `documents/history/M82_CAPABILITY_CONFORMANCE_RESULTS.md` | Hook reachability remains machine-checked; its two real-host proofs remain assigned to M8.6. |
| M8.3 - semantic continuity and backtracking | Closed 2026-08-11 | `documents/history/M83_SEMANTIC_CONTINUITY_RESULTS.md` | A semantic change returns to DESIGN/SPEC and clears affected settlements. |
| M8.4 | Removed 2026-08-05 | none | Do not reuse this number or recreate the removed Package. |
| M8.5 - cross-platform installed workflow | Closed 2026-08-12 with exceptions | `documents/history/M85_CROSS_PLATFORM_WORKFLOW_RESULTS.md` | Manifest and executable-adjacent paths were repaired; macOS installed reproduction and owned process-tree cleanup remain unimplemented/unproved. |
| M8.7 - product boundary generalization | **Source implemented; delivery/closure deferred** | `documents/history/M87_PRODUCT_BOUNDARY_GENERALIZATION_RESULTS.md` still required at combined close | The v3 structural generalization is present in source; do not re-execute its retired detailed contract. |
| M8.8 - surface effect composability generalization | **Research revised; execution contract awaiting confirmation** | `documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md` required at combined close | Exhaustively contract every effect capability supported by the pinned RitsuLib profile across eight surfaces. |
| M8.6 - clean installed whole-skill acceptance | Waiting | contract and result path are defined only when selected | Final installed judgment after M8.7 and M8.8; also owns M8.2's two deferred hook proofs. |

## M8.7 - Product Boundary Generalization

M8.7 source development is complete in the current working tree. Do not re-run or reconstruct its
former detailed execution contract. Its generated payloads, remaining active-document updates,
durable result record, and explicit human closure are deferred so M8.7 and M8.8 can be reconciled
and delivered once rather than publishing an intermediate product boundary.

No M8.7 runtime, Tier 1, Tier 2, headed, install, or game observation is inferred from its source
implementation. Preserve the current dirty work and its literal evidence labels until combined
delivery is explicitly authorized.

## M8.8 - Surface Effect Composability Generalization

### State And Goal

M8.8 research has been revised by explicit human-lead direction. This four-part contract is
executable only after confirmation. Once confirmed, execute the parts in order, preserve the
current M8.7 dirty source, and stop after the source/static gate in Part 4 for human review. Source
implementation does not itself authorize the later combined M8.7/M8.8 delivery gate.

M8.8 is an up-front capability expansion for Card, Potion, Relic, Power, Orb, Enchantment, Monster,
and Event. It must not wait for a user to name an unfamiliar effect. It first finds every effect
capability RitsuLib supports for those eight surfaces, then makes every capability in the pinned
profile an open-mod authoring contract. A missing old recipe, proof Mod, acceptance example, or
validator branch is evidence of an open-mod gap to remove, never a reason to exclude the effect.

The official guide at `https://sts2-ritsulib.ritsukage.com/guide/` is the exhaustive discovery
index. Exact current support is decided by the local RitsuLib `v0.5.4` source at commit
`8b971a79e6b0a62daddd948790cd3661bb13a930`, its versioned documentation, and the pinned public
STS2 `0.107.1`/Compat assembly metadata. Because the live website may describe a later release,
every website-only capability must be recorded as a version delta. Do not silently omit it or claim
that it exists in `0.5.4`; raising the profile remains a separate human decision.

After M8.8, support does not depend on previous open-mod proof. An effect found in RitsuLib
documentation/source but absent from all old open-mod recipes and proof Mods is equally authorable.
New combinations of supported effects may use ordinary C# and BCL, public STS2 `0.107.1` and
RitsuLib Compat `0.5.4` APIs, Mod-owned helper methods/types/state, and an already maintained checked
Adapter where that is the supported route. Conditions, loops, queries, local variables, helper
classes, ordered asynchronous calls, intermediate results, and combinations not seen in any
previous artifact are all in scope.

Existing `OP-###` values remain stable DESIGN-to-SPEC identities for the player's requested
behavior. The Part 1 audit determines the exact maintained representation needed to carry complete
capability provenance, lifecycle, parameter, composition, and trace facts through the shipped
contract; that representation must cover the complete pinned RitsuLib effect surface.

The real boundaries are the host lifecycle and product safety contract, not absence from a list.
M8.8 does not create a new content surface, registration path, external dependency, arbitrary UI/VFX
host, multiplayer claim, or cross-Mod coordination system. It does not generate new prompt-derived
Harmony, reflection, Publicizer, IL, private/internal access, or unrelated filesystem/network/process
behavior. Existing reviewed fixed Adapters retain their exact scopes. A composition blocks only when
it needs one of those excluded mechanisms, a value no legal lifecycle can supply, a capability not
present in the pinned profile, or a separately unsupported product surface. Report that concrete
reason rather than "no recipe" or "not previously proved".

M8.7's v3 structural families, M8.2 hook reachability, registration/ownership rules, targeting
lifecycle, Event presentation, Monster intent truthfulness, bilingual localization, deliverable
claims, and M8.3 repair continuity remain in force. M8.8 generalizes effect authoring; it does not
discard the semantic facts and evidence boundaries those contracts protect.

### 1. Exhaustively Audit The RitsuLib Effect Surface

Create `games/sts2/tests/m88-ritsulib-effect-audit.md` as a maintainer-only source-development
ledger. Audit the complete official guide navigation, every linked guide page, and the corresponding
public `v0.5.4` source/API rather than searching only for effects already named by open-mod. Include
all public commands, model callbacks, lifecycle listeners, Event outcome paths, state/query helpers,
and public data or return types needed to invoke an effect from Card, Potion, Relic, Power, Orb,
Enchantment, Monster, or Event. Use the pinned assembly metadata to cross-check the exact public
surface; use the maintainer decompile only to locate candidates or understand native dispatch, never
as sole authority for generated access.

The audit also covers the current open-mod consumers that could narrow what was found:

- all eight owner pages under `skills/modmaker/surfaces/` and their
  `skills/sts2-api/recipes/`/reference routes;
- `modmaker/semantic-contract.md`, `modmaker/spec.md`, `modmaker/author.md`, Interview, Repair,
  Verify, invariants, and `content-capability-graph.md`;
- M8.2 hook participation, M8.7 surface contracts/state, targeting, computed values, Rest Site,
  Event outcome/presentation, and vanilla-owner composition references; and
- `spec_envelope_trace.py`, `surface_contract_trace.py`, `design_trace.py`, the pinned model-hook
  collector/catalog, `vanilla_overrides.py`, and every validator that interprets effect support.

For every guide page and every relevant public source/API capability, record its official
documentation/source anchor, first confirmed version when known, player-visible behavior, exact
public symbols, input/result/async shape, applicable lifecycle facts, and one audit disposition:

- `current-profile effect`: RitsuLib `0.5.4` supports it and M8.8 owes an authoring-contract owner;
- `effect-supporting context`: it supplies lifecycle, query, target, state, or result data needed by
  an effect contract but is not itself a player-visible effect;
- `later-version delta`: the live guide/source advertises it but the pinned profile does not;
- `not an effect`: the page/symbol concerns registration, assets, diagnostics, tooling, or another
  product surface outside the eight effect bodies; or
- `retained product boundary`: the route requires a forbidden mechanism or a separately unsupported
  product surface, with the concrete reason.

No guide page or relevant public symbol may be silently skipped. "No recipe", "not previously
proved", and "not in the capability graph" are invalid dispositions. The ledger must also identify
every current effect declaration, recipe-only rule, and exact-route preflight, then determine how
the maintained contract and validation structures must change to cover the complete pinned profile.

The ledger is complete only when every discovery source is accounted for, every current-profile
effect row has an open-mod contract owner selected for Part 2, all website/profile deltas are
literal, and at least one capability found only in RitsuLib docs/source and absent from old open-mod
recipes/proofs is selected as a representative coverage regression. The ledger proves coverage of
the research and supplies the provenance needed by the shipped contract.

### 2. Make Every Current-Profile Effect Authorable And Composable

Add shared effect-authoring guidance under `games/sts2/skills/sts2-api/reference/` and revise the
eight surface/recipe owners. The exact file split is chosen from the Part 1 audit, but it must avoid
eight copied effect lists. The shipped contract must cover every `current-profile effect` row and
must make old recipes illustrative examples rather than the boundary of support.

Each surface owner describes all of its legal effect triggers as lifecycle-context contracts. For
each trigger, record the public callback/signature and pinned source, owner/source types, scope and
reachability, and every value the host supplies: owner/player/creature, selected target or target
set, Card play, choice context, combat/run state, Event/page state, RNG, and callback-specific
results. Record origin, type, cardinality, nullability, ownership, validity window, and await/order
phase. These contracts answer "what is available at this trigger"; they do not enumerate which
effects are permitted there.

The shared effect guidance records every RitsuLib-supported effect capability with a stable
maintained identity, its official documentation/source anchor, and public C# symbol. For each one
it states:

- exact player-visible semantics and current-profile provenance;
- required parameters, accepted targets/cardinality/nullability, required scope/state, and legal
  ways those inputs may be obtained;
- return/intermediate result, side effects, cancellation/failure behavior, async requirement, and
  ordering constraints;
- text, DynamicVar, Hover Tip, localization, preview, presentation, and verification obligations;
  and
- the exact public call shape or maintained checked Adapter, with examples labeled as non-exhaustive.

The universal composition rule is input closure:

1. Select the real surface trigger and take its lifecycle-context values.
2. For each desired effect call, map every required parameter from a supplied value, a legal
   owner/target relationship, an in-scope public query, a prior compatible result, a SPEC-declared
   constant/calculation, or M8.7 Mod-owned bounded state.
3. Check type, target cardinality, nullability, ownership, validity window, choice context, and
   combat/run/Event scope. A value cannot be invented or retained after its lifecycle expires.
4. Order and await calls exactly as their public contracts require. A returned value may feed a
   later call when its type and lifetime remain valid. Conditions, loops, helpers, queries, and
   repeated or branched calls are ordinary C#, not new capability kinds.
5. If all inputs close, the composition is authorable regardless of whether that combination or
   effect appeared in an old recipe/proof. If they do not close, try another legal trigger; otherwise
   block on the exact missing context or retained product boundary.

Hook-driven triggers reuse M8.2's checked reachability and public signatures. M8.7 bounded state
supplies only state explicitly owned and transitioned by the current Mod. Existing vanilla
replacement Adapters retain their reviewed scopes; ordinary new-content effect bodies use public
C# directly. The maintained representation chosen from the audit must encode or resolve these
composition facts without duplicating eight independently drifting surface boundaries.

### 3. Close SPEC And The Existing Contract-Trace Chain

Keep `sts2-content-semantic/v3` and `open-mod-spec-trace/v1`. Each existing `OP-###` continues to
mean one complete player-facing behavior selected by DESIGN.

Add one project-local `open-mod-effect-grounding/v1` block to each newly written or user-accepted
revised v3 SPEC that contains effect behavior. The human-readable envelope still owns exact
semantics: trigger, target, values, sequence, scaling, state, text, presentation, fallback, and
proof. The grounding block connects that semantic promise to implementation without choosing from
a closed set of implementation shapes. Each entry is keyed by its existing `OP-###` and records:

- selected surface trigger and the exact lifecycle context used;
- each public effect call or maintained Adapter, its pinned documentation/source anchor, and every
  required input mapped to its concrete context/query/result/calculation/state source;
- target cardinality/nullability, conditions, data flow, control-flow outline, await/order rules,
  intermediate results, and failure/neutral behavior;
- state ownership, lifetime, transition/check/reset/consume order, persistence, and refresh;
- Mod-owned helper types/methods and the generated source locations that will implement it;
- behavior/text/DynamicVar/Hover Tip/localization/preview/presentation equivalence; and
- implementation status and exact evidence boundary, including `game-unobserved` where applicable.

Framework symbols stay in this marked grounding block, not in the semantic envelope. A legacy
v1/v2 or pre-M8.8 v3 project resumes unchanged until the user accepts an effect revision; a newly
written effect cannot omit the block. The block may describe arbitrary ordinary C# control/data
flow and multiple calls. It is project-local implementation grounding.

The contract chain closes at two different scopes:

- Maintainer audit completeness: a focused source check proves that every official guide page and
  relevant pinned public symbol has an audit disposition, and that every `current-profile effect`
  reaches a real shipped authoring-contract owner.
- Generated project closure: `design_trace.py` retains D-to-OP closure and verifies that an
  effect-bearing operation has project-local grounding. `spec_envelope_trace.py` remains the single
  SPEC entry point, retains v1/v2/v3 plus M8.7 structural checks, and invokes one shared grounding
  validator. `surface_contract_trace.py` continues to own M8.7 structural families. No validator
  is duplicated once per surface.

The shared grounding validator checks only facts that can be checked without pretending to prove
arbitrary C# semantics:

- every current effect-bearing `OP-###` has exactly one entry and every entry maps back to current
  DESIGN/SPEC semantics;
- the cited surface trigger is real and reachable, and every declared call input maps to supplied or
  legally derived context with compatible type/cardinality/nullability/scope/lifetime;
- target/choice handling, state phase, await/order, result flow, value/text bindings, fallback, and
  proof obligations are explicit and internally consistent;
- pinned provenance, intended public symbols, local helpers, implementation files, and evidence
  status are recorded; and
- no entry uses a forbidden mechanism, historical fixture, generic recipe, or previous proof as a
  substitute for context/parameter closure.

The generated-project validator resolves the maintained capability/lifecycle representation and
verifies the mapping structure. Static authoring review checks the exact C# against those contracts,
compilation later proves symbols and types, and selected Mod verification proves only its own cases.
Author marks generated classes/methods with their owning `OP-###` so post-Author checks can pair
source back to SPEC. M8.3 clears behavior, state, text, tips, localization, preview, presentation,
grounding, generated source, and proof settlements together when an effect changes.

M8.7 `bounded_state.outputs` links to the owning `OP-###` grounding and phase. For example, an
effect that fires after every four owner Card plays records the listener context, counter update,
threshold check, effect invocation, and reset order inside one project-local contract.

Focused contract scenarios must include a bounded-state payoff, an ordered multi-call composition
with an intermediate result, at least one RitsuLib docs/source-only effect absent from old open-mod
recipes/proofs, and legacy resume. Negative scenarios reject missing or expired lifecycle values,
false context derivation, illegal choice/target handling, unreachable hooks, ambiguous order/state,
stale text or DynamicVar bindings, missing pinned provenance, and forbidden mechanisms.

The docs/source-only coverage regression is mandatory: add the capability to a temporary project's
DESIGN/SPEC grounding and generated-source sample using the shared contract created from the
exhaustive audit. The complete version must pass through the maintained representation and trace
chain; an incomplete version must fail for the concrete missing context, parameter, or trace fact.

### 4. Use Existing Acceptance As Point-To-Family Evidence

Use the following existing records as representative host/path evidence, never as proof that every
possible effect or surface pairing was observed:

- `M80_SKILL_STRUCTURE_RESULTS.md`: the Card pilot's real `[PASS] Tier-2 verified` result;
- `RITSULIB_MIGRATION_RESULTS.md`: R3 coverage of Card, Relic, Potion, Power, Enchantment, and Orb,
  and R4 coverage of Monster/Encounter and Event/World Node;
- `M6_NATIVE_PRESENTATION_RESULTS.md` and `M6_FORCED_FOLLOWUP_EVENT_RESULTS.md`: strict Tier 2
  examples for ordered Event consequences/presentation and one bounded forced follow-up lifecycle;
- `M66_ADVANCED_TARGETING_RESULTS.md`, `M66_COMPUTED_VALUES_RESULTS.md`,
  `M66_REST_SITE_OPTIONS_RESULTS.md`, and maintained state/cadence evidence: focused target,
  value-phase, ownership, threshold/reset, and lifecycle observations with their recorded
  exceptions; and
- `M67_VANILLA_OVERRIDES_RESULTS.md`: consolidated existing-owner composition acceptance, without
  inferring individual-route observation for unselected behaviors.

These records establish representative legal hosts, awaited/ordered C# execution, target and owner
handling, state/cadence patterns, and the SPEC-to-generated-code development path. They do not
establish all eight surfaces independently, every callback context, every newly covered effect,
multiplayer, or every combination. Preserve each record's literal exceptions. Their accepted
development paths are the point-to-family runtime rationale requested for M8.8: absence of a new
bespoke runtime proof does not remove a pinned RitsuLib capability from support. Newly covered
effects are `open-mod-authorable` and remain `game-unobserved` until later evidence observes them.

After implementation authorization, source verification is limited to the contract layer:

1. Run/check the maintainer audit coverage projection: every official guide page and relevant
   pinned public symbol has a disposition; every current-profile effect has a shipped contract
   owner; every later-version delta remains explicit. Recheck changed public signatures against
   RitsuLib `v0.5.4` source and pinned assembly metadata.
2. Run existing pinned catalog `--check` commands, including
   `python games/sts2/tools/collect_model_hooks.py extract --check` if the callback projection
   changes. Verify every lifecycle context and effect parameter contract against its cited source.
3. Set `$env:PYTHONUTF8='1'`, then run focused M8.8 audit/context/grounding/trace/legacy/coverage
   tests plus existing M8.2/M8.3/M8.7 trace modules; name their exact module paths in the
   implementation result. Run the full suite with `python -m unittest discover -s
   games/sts2/tools/tests -p 'test_*.py'`; then run `python -m compileall -q games/sts2/tools
   scripts/publish` and `git diff --check`. Report exact counts.
4. Search source for fixture-shaped support wording, uncovered guide/source capabilities,
   independently drifting per-surface boundaries, and any rule requiring prior recipe/proof
   membership. Review the diff against the Part 1 ledger and state the evidence boundary literally.

The contract scenarios may use temporary, noncompiled generated-source samples solely to pair
current `OP-###` grounding with intended C# shape. Do not create an M8.8-specific compiled C# proof
fixture, per-effect/per-surface compile matrix, generated Mod matrix, install, game launch, or new
Tier 1, Tier 2, headed, save/load, or gameplay acceptance. The new checks prove audit completeness,
contract coverage, and composition/trace closure; they do not claim that every effect ran. A missing
bespoke runtime case must remain `game-unobserved`, never become an effect or surface whitelist.

The initial authorized implementation stops after the source/static checks and reports the exact
dirty scope for human review. It does not regenerate either payload, update active status documents,
write a history result, close M8.8/M8.7, commit, push, or begin M8.6.

Only a later explicit combined-delivery instruction authorizes all of the following as one step:

- regenerate `plugins/open-mod/` and top-level `skills/` from `games/sts2/` through `publish.sh`,
  never by hand, and run repeatability, parity, payload-tool-layout, and payload-shaped validators;
- synchronize the active documents that own M8.7/M8.8 facts without reimplementing M8.7;
- write `documents/history/M87_PRODUCT_BOUNDARY_GENERALIZATION_RESULTS.md` and
  `documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`, each with exact tests,
  evidence labels, exceptions, changed files, and active documents reviewed but unchanged; and
- request explicit human closure of M8.7 and M8.8. Closure does not start M8.6.

M8.8 source is ready for review when the official guide and pinned public source/API audit is
complete, every current-profile effect has a shipped authoring-contract owner, all eight surfaces
publish their legal lifecycle contexts, the input-closure rule supports arbitrary valid
combinations, and SPEC grounding closes through the existing trace chain. At least one
docs/source-only effect absent from old recipes/proofs must pass the representative coverage case.
Focused and full static regressions must pass, website/profile deltas must remain explicit, and
unobserved effects must retain literal `game-unobserved` status. M8.8 is not closed until the later
delivery artifacts exist and the human lead explicitly closes it.

## M8.6 - Clean Installed Whole-Skill Acceptance

M8.6 remains intent only. It is not eligible until M8.7 and M8.8 close and the human lead selects
the fresh request, host, installed payload, completion claim, and acceptance boundary. Its
contract must be written and confirmed before execution.

At selection, M8.6 must include:

- one untouched installed-payload workflow driven from a fresh natural-language request;
- the literal deliverable and every required player experience;
- current M8.7 structural contracts and M8.8 RitsuLib-supported effect contracts actually selected
  by that request, without pretending the run covers unselected variants;
- M8.2's deferred incoming-damage multiplier proof with a neutral case and collection-edit proof
  preserving unrelated entries;
- build, Tier 1, selected Tier 2, bilingual checks, presentation/human observation, process cleanup,
  and literal final reporting; and
- explicit carry-forward of unresolved M8.5 exceptions unless separately repaired.

Do not draft technical implementation details for M8.6 before its request and host are selected.

## Verification Policy

- Static/design/payload evidence proves only the layer it exercised.
- A build proves compilation/packaging, not load or behavior.
- Tier 1 proves load and absence of fresh scoped errors, not mechanic semantics.
- Tier 2 proves only its structured cases on the claimed host/profile.
- Headed human observation owns subjective presentation and player-experience claims.
- User decision can accept an exception but cannot be relabeled as observation.
- Every generated expected value, identity, route, and terminal marker comes from current SPEC and
  its validated current contracts/catalogs, never a historical proof Mod.

## Closed Work And Future Outlook

Completed M6/M7/M8 evidence remains indexed by `documents/history/README.md`. This plan keeps only
closed status that changes current prerequisites or verification boundaries.

Future work requires separate human selection. In particular: multiplayer authoring, arbitrary
asset/scene behavior, profile progression, cross-Mod conflict coordination, M8.5 process-tree
ownership repair, and publication/release remain outside the current M8.8 direction.
