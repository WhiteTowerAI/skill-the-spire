# M8.2 exact semantic capability conformance and preflight

## Decision

M8.2 Exact Semantic Capability Conformance and Preflight is closed by explicit human-lead
decision on 2026-08-10. All five work-order steps are implemented in source and synchronized
into both committed payloads. Its execution contract was written against the layout M8.0 left
behind and confirmed by the human lead before implementation, including the three decisions the
contract left open.

**The two real-host proofs step 3 owed were deferred to M8.6 by the human lead on 2026-08-10.**
They were named in the contract as the smallest thing that proves the Wrath class of failure is
closed, and they did not run. This is a recorded exception, not a pass: see § Literal Boundaries.

This is an implementation record. No generated Mod, game launch, Tier 1, Tier 2, or forward-model
run is claimed by this Package.

## Problem

The workflow could pass every local stage while the identity-critical behavior the user asked for
was absent. M7.6's Wrath is the reference case: the user asked for a stance that doubles incoming
damage, `SPEC.md` recorded the requirement, an operation was generated, the harness passed, and
the multiplier was never implemented. Three independent reasons, each located in source before the
change:

1. **The SPEC grammar could not declare it.** `surfaces/power.md`'s envelope had fields for the
   effect, its lifetime, its amount domain, and its display. There was no field in which "this
   Power multiplies damage its owner receives" was a *declaration* rather than prose inside the
   effect text. A value stated only in prose is not checkable by anything downstream.
2. **The route pointer did not have to be real.** `design_trace.py` accepted a `#anchor` in
   `supported_route` but split it off and checked only that the file existed. The canonical example
   shipped in `spec.md` pointed at `reference/art-contract.md#placeholder`, an anchor that has
   never existed in that file. Every generated project copied it.
3. **A route that exists need not cover the operation.** Nothing checked that the cited route
   documented the semantics the operation needed. Watcher's Wrath cited a real route; the route had
   no multiplier line, so the author improvised and the improvisation was empty.

M8.2 also inherited M8.0's three open surface cross-check mismatches, deferred here on 2026-08-10
because the envelope-form decision was a prerequisite for the other two.

## Three Confirmed Decisions

1. **Envelope: normalize the six flat surfaces and bump to `sts2-content-semantic/v2`.** Potion,
   Power, Orb, Monster, Event, and Character moved from a flat `element:` opening plus ad-hoc
   top-level keys to the nested `content:/surface:` form Card and Relic already used. The reason is
   mismatch 8's remaining half: checking a *generated* project's `SPEC.md` against its surface
   envelope needs one schema to check against, and two legal shapes means no schema. The cost is
   six pages plus a migration path, and `semantic-contract.md`'s own requirement that an envelope
   change carry a version bump and migration note was honored rather than waived.
2. **Hook scope: open all reachable hooks, not a curated subset.** Symmetry with the
   vanilla-override side, which already catalogs 26+28 for vanilla owners: a custom Power should not
   be able to do less to itself than a vanilla override can do to someone else's Power. Bounded by
   two hard constraints — a hook is authorable on a surface only where that surface is in the
   dispatching iterator's listener set, and an Enchantment routes to its five `Enchant*`
   replacements. Extended the same day, after step 1 reported them, to include the 14 `TryModify*`
   callbacks, taking the total to 68; they were outside the original 26+28 because neither the
   vanilla reference nor any custom surface listed them.
3. **Preflight depth: route + anchor resolution plus capability-id pairing.** Every `OP-###` names
   the capability it consumes, every route page declares what it provides, the validator pairs
   them. Explicitly *not* the full behavior/lifecycle/rules-text/keyword/Hover-Tip/localization/
   preview/presentation parity sweep, which is larger than one Package and mostly resolves to
   proof-matrix obligations rather than static checks.

## What Was Implemented

**Step 1 — the hook catalog.** `tools/collect_model_hooks.py` projects the pinned hook surface into
`sts2-api/reference/catalogs/model-hooks-sts2-0.107.1.json`: 68 hooks (26 numeric, 28 decision, 14
`TryModify*`), zero unresolved. Maintainer-only and excluded from both payloads, following the
`collect_vanilla_catalog.py` precedent; the committed catalog is the shipped artifact. Per hook it
records the exact signature, return type, neutral default, dispatchers, dispatch iterators,
listener families, authorable surfaces, declaration shape, and vanilla implementor counts. Its five
findings — iterator-decided reachability splitting the list into three authorable groups, the five
Enchantment redirects, a bad first derivation caught by the vanilla cross-check, the two-shape split
in the `TryModify*` family, and two hooks already owned by the Rest Site route — are recorded in
`games/sts2/tests/m82-hook-catalog-findings.md`. The shipped `vanilla-non-card-overrides.md` lists
match the assembly exactly (26 and 28), so that reference needed no correction, and a test now holds
the two statements together.

**Step 2 — envelope v2 and the migration path.** The six flat surfaces now use the canonical nested
form with the nine shared sections. `semantic-contract.md` is v2 with a migration note stating what
moved and how a v1 project is read: a v1 `SPEC.md` on an unfinished project resumes unchanged, the
same precedent a pre-M7.5 coherence block and a pre-M8.1 deliverable block set. M8.0 mismatch 7 is
folded in — the character resource and ordered-buffer envelopes moved from `spec.md` into
`surfaces/character.md`, joining their proof.

**Step 3 — hook-participation declarations.** One new authoring route,
`reference/model-hook-participation.md`, declaring 71 capability ids across five grouped
declarations. It owns the two declaration shapes, the guard-value-neutral body, and four rules a
generated override gets wrong when they are not stated:

- **direction is the guard**, not the hook: the same method is "damage I receive" or "damage I
  deal" depending only on whether `target` or `dealer` is compared to the owner. `VulnerablePower`
  guards the first, `WeakPower` the second.
- **damage kind is a separate decision.** `IsPoweredAttack()` is true only for attack damage from
  a Card play or Monster move; Poison-style `Unblockable` loss and `Unpowered` relic/potion/power
  damage are excluded, and both vanilla multipliers guard on it. So "doubles incoming damage" is
  not yet a decision — SPEC has to record which damage.
- **the neutral return is load-bearing.** It is what keeps the element invisible to unrelated
  interactions, and the engine also uses it to decide whether to list the element as a modifier of
  that number in the UI.
- **composition order is the engine's.** Additive across all listeners, then multiplicative, then
  the minimum cap, then a floor at zero — so `+3` and `x2` on one hit yield `(base + 3) * 2`.

The per-surface owner property differs and every guard depends on it: `Owner` is a `Creature` on a
Power, a `Player` on Relic/Potion/Orb/Card (so a guard needs `Owner.Osty` too, as `PenNib` does),
and a Monster has no owner at all — just `Creature`. Card carries one further constraint:
`ShouldReceiveCombatHooks => Pile?.IsCombatPile ?? false`, so a combat-scope rule on a Card outside
the piles compiles and never fires.

Seven surfaces declare the envelope field with their own reachability note and owe the paired
neutral-case proof through `FIELD_PROOF_PAIRS`; the three no listener set contains must not declare
it. Seven recipes carry the matching authoring line. `author.md` dispatches to the new route.

**Step 4 — capability ids and the preflight validator.** `design_trace.py` resolves anchors against
real headings and pairs consumed capability ids against what the route page declares; the shipped
`art-contract.md#placeholder` example is fixed to a real anchor. `spec_envelope_trace.py` validates
a generated project's `SPEC.md` against its surface's v2 envelope — required sections present, no
invented top-level keys, contract line v2 or absent — closing the half of M8.0 mismatch 8 that the
envelope decision was blocking. Step 3 extended it to reject an unknown capability, a shape the
catalog contradicts, a route-owned hook, and a hook the declaring surface cannot receive.

**Step 5 — the conformance rule for a claimed-but-broken route.** `INV-9`: a route that claims a
semantic capability must maintain it, and when observed reality shows it does not, that route blocks
generation until repaired upstream or narrowed to the smallest exact recorded limitation. An
approximation inside the consumer project is not a repair — it leaves the shared route still
claiming something it does not deliver, so the next Mod that trusts it fails the same way. `INV-9`
is distinct from `INV-3`, where the route is simply absent; here it exists and is wrong, which is
harder to see because the citation resolves and the recipe reads as grounding. `repair.md` names it
and adds only its own stage detail.

## Six Defects Found While Spending The Catalog

Three were in earlier steps of this same Package, found only when step 3 became their first real
consumer:

1. **`design_trace.py`'s capability parser could not span lines.** Without `re.DOTALL` the first
   real declaration parsed as zero ids and the pairing check silently passed everything. This is
   also why step 4's end-to-end test was skipped rather than failing: no shipped route declared a
   capability, so nothing exercised the parser. Adding the first real declaration turned that skip
   into a live passing test.
2. **`COMBAT_LISTENERS` was missing `modifier` and `badge`.** Step 1's own second fix
   over-corrected: it concluded the combat-state form reached neither family, but
   `CombatState.IterateHookListeners()` walks `combatState.Modifiers` and `combatState.BadgeModels`
   — what the run-only branch adds is the run-scope *instances*, not the family. Re-extraction left
   authorable surfaces unchanged at 40/23/5 with zero contradictions, since neither is a surface
   this pack generates. Recorded as a third finding in the catalog findings file. **The vanilla
   cross-check could not have caught it:** all six vanilla Modifier hook overrides (`DeadlyEvents`,
   `NightTerrors`, `Flight`, `Hoarder`, `Midas`, `Vintage`) happen to be run-scope, so no vanilla
   evidence contradicted the narrowed set. A cross-check only fails where vanilla exercises the
   case; silence from one is not confirmation.
3. **`spec_envelope_trace.py` could not find the pack in a payload.** Its payload path candidate
   was `skills/surfaces`, missing the `modmaker` segment, so the validator `spec.md` tells every
   project to run resolved in the repo and in nothing else — it would have failed on the first
   installed project with what looks like a broken install. New
   `tools/tests/test_payload_tool_layout.py` builds a throwaway payload-shaped tree and runs the
   shipped tools inside it, so a repo-only path resolution fails a test instead of an install.
4. **A pre-existing test asserted no `INV-9` could exist** (M8.1). Narrowed to the
   deliverable-claim rule it was actually about: that rule fires at finalize only and stays in
   `verify.md`, which is a decision about that rule, not a blanket prohibition on a ninth
   invariant.
5. **Card hook ownership followed the nearest preceding marker instead of indentation.** The Card
   envelope declares its optional nested `enchantment:` before the Card's top-level hook block, so
   the parser attributed an ordinary Card capability to the Enchantment. The parser now keeps the
   Enchantment owner only inside that field's indented subtree; regressions cover both a reachable
   Card hook and an Enchantment-only redirect that must stay rejected on the Card.
6. **A reachable capability could omit the declaration that made it meaningful.** The validator
   checked `shape` only when present and did not require the player-facing rule, subject, condition,
   DynamicVar name, neutral result, or shape-specific value/edit fields. Preflight could therefore
   call an incomplete declaration well-formed. It now requires every common field plus `value`,
   `replaces`, or collection edit/preservation/ordering fields as the selected shape demands.

## Verification

Proportional and non-game for steps 1, 2, 4, and 5: prompt, tooling, catalog, and documentation
only, with no generated runtime behavior change. Step 3 does change generated runtime behavior and
therefore owed a real host; that proof was deferred to M8.6 and did not run.

- Focused Python suite `364 passed`, zero skipped, up from `298` at M8.1 closure. New files are
  `test_model_hook_catalog.py`, `test_spec_envelope_trace.py`, `test_design_trace_routes.py`,
  `test_m82_hook_participation.py`, and `test_payload_tool_layout.py`.
- **All six preflight rejection tests were verified to fail against a neutered validator.** A
  rejection test that passes when the check is removed proves nothing; each was confirmed to flip.
- Step 1's catalog was mutation-checked four ways: offering a run-only hook on a Power, an
  Enchantment on a redirected hook, a collection-edit hook mislabelled as a replacement, and a
  dropped route ownership each fail the specific test written to catch them.
- Every promoted C# fact was read from the pinned `0.107.1` decompile rather than from memory:
  `AbstractModel.ModifyDamageMultiplicative` and its `1m` default, `VulnerablePower`'s two guards
  and its `DamageIncrease` DynamicVar, `WeakPower`'s dealer guard, `PenNib`'s Osty comparison,
  `ValuePropExtensions.IsPoweredAttack`, the `ValueProp` flag meanings, `ModifyDamageInternal`'s
  composition order, `Hook.ModifyRewards`'s base-then-late dispatch, `BlackStar` and
  `AmethystAubergine` as add-under-guard, `Midas` as the clear-and-rebuild remover, the five
  `EnchantmentModel` replacement signatures with their split neutrals, and the six per-model
  `ShouldReceiveCombatHooks` values including `CardModel`'s pile dependence.
- The shipped payload copy was executed from its own bundled location: it rejects
  `try_modify_rewards` on a Power naming the four surfaces that can receive it, and accepts
  `modify_damage_multiplicative` on the same SPEC.
- Both payloads regenerated from source after every change set. The maintainer-only
  `collect_model_hooks.py` is excluded from both; the catalog and the new route page ship in both.
- After the two post-closure validator repairs, all six source/plugin/portable skill roots validate,
  source plus payload Python compilation passes, and the plugin/portable trees have 187 shared
  effective files with zero parity or repeatability mismatches (aggregate SHA-256
  `9898BAFE52073883B3041629D047E5698AA1AF470E1DF1CC263816F8F97ADB67`).

## Literal Boundaries

- **The two real-host proofs did not run and are deferred to M8.6.** No generated Mod declaring
  hook participation has been built, launched, or observed. Every hook route in the catalog is
  implemented-and-unproved. Per `AGENTS.md`, that is missing verification rather than missing
  support, and it is recorded here rather than rounded up.
- Preflight is static. A green run means a declaration is well-formed, reachable, correctly shaped,
  and paired with a route that claims the capability — not that the generated override fires,
  returns the right number, or leaves unrelated interactions alone.
- No Tier 1, Tier 2, headed review, or independent forward-model run was performed. The three cases
  in `games/sts2/tests/m82-capability-conformance-scenarios.md` are source-contract inspections, not
  run evidence.
- The catalog is a projection of a maintainer-only decompile whose DLL provenance sidecar was not
  retained. Recheck any fact against the pinned assembly or installed game before promoting it
  further.
- Reachability is derived from the pinned iterators. A host version bump can move a hook between
  listener sets, which is why the catalog is generated and tested rather than transcribed.
- The 100 async hooks on custom surfaces remain out of scope; the per-surface trigger tables already
  cover the selected ones and widening them is a separate decision.
- Full surface parity (behavior/lifecycle/rules text/keyword/Hover Tip/localization/preview/
  presentation), semantic-impact backtracking (M8.3), and cross-platform process ownership (M8.5)
  remain later work. M8.2 promoted no new engine capability beyond writing authoring for a public
  route that already existed — `INV-3`'s first clause, missing authoring work rather than an
  unsupported API.
- No payload publication, GitHub release, or acceptance Mod is authorized by this result.

## Documents Reviewed

Changed: `documents/IMPLEMENTATION_PLAN.md` (M8.2 contract restored to its own heading plus per-step
status; the heading had been overwritten onto M8.1's body by an interrupted session),
`AGENTS.md` (current status, supported surfaces, architecture),
`documents/PROJECT.md` (release state), `README.md` (status banner),
`documents/history/README.md` (index), `games/sts2/tests/README.md` (test ownership),
`games/sts2/tests/content-capability-graph.md` (one new Supported row with its unrun-proof
boundary), `games/sts2/tests/m80-surface-cross-check.md` (its three deferred mismatches, now
resolved in source).

Deleted: `documents/M82.md` — the working contract rescued from the interrupted session, superseded
by the contract now in `documents/IMPLEMENTATION_PLAN.md`.

Reviewed and left unchanged: `documents/BASELINE_RESEARCH.md` — the decompile's role as offline
maintainer research is already recorded there and M8.2 changed no baseline's role;
`documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md` and the other closed results — immutable
records, and the M8.1 note that the three cross-check mismatches were "M8.2's, untouched here"
remains true of M8.1.
