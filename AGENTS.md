# AGENTS.md

Repository guidance for coding agents working in open-mod.

## Project

open-mod is a free, open-source Codex plugin that turns a non-programmer's description
into a working game mod. The current target is Slay the Spire 2 (STS2). The strategy is
one game deep, then a reusable platform.

Read `documents/IMPLEMENTATION_PLAN.md` before substantive work. Completed evidence lives
under `documents/history/` and is not current instruction.

## Current Status

`0.6.0` is the unreleased RitsuLib-only development baseline for STS2 stable `0.107.1`
and RitsuLib `0.5.4`. The BaseLib-to-RitsuLib migration and external clean-workspace
Codex acceptance are closed; details live in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. R7 was canceled by the human lead and
did not pass.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
implemented. The fresh Prismwright acceptance is closed and retired by explicit
human-lead decision; its headed result and waived Tier 2 harness are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`. Do not reopen that proof or
prepare/claim a GitHub release without later lead instruction.

M6.6 is closed by explicit human-lead decision. Package 2A computed Card values,
Package 5 custom-Character dialogue in native Ancient scenes, the bounded Package 1
advanced creature-targeting slice, and the bounded Package 3 Relic-owned Rest Site option
slice are implemented in the generation pipeline. Package 1 supports single-target Cards,
single-target Potions, and multi-target Cards; custom multi-target Potions have a pinned
lifecycle limitation. Package 3
supports singleplayer Relic-owned options with free/fixed Gold, deterministic outcomes,
once-per-site/run repeatability, native stay/leave behavior, and checked custom/Heal-fallback
icons. Its human-led result, skipped log check, and strict Tier 2 exception are recorded in
`documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`. Package 2B hand readability and
Package 2C Relic/Power corner-label authoring are implemented with bounded fixed-color hand
rules, up to three safe-corner Relic labels, and one top-left Power label. Their human-led
headed review and strict Tier 1 passed after the Power boundary was narrowed to fix crowded
row overflow; strict Tier 2 was not run. The result and exception are recorded in
`documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`. Intent corner-label authoring was removed
from M6.6 work by the human lead on 2026-07-30; Intent remains supported as part of the
public RitsuLib Extra Badges Package. Package 4 Custom Card Piles authoring is implemented
for the complete documented Package: combat/run scopes, headless/top-bar/bottom-corner/
ExtraHand styles, preset/custom anchors, public pile screens and view capabilities,
visibility/hotkeys, native Card movement, localization, and ExtraHand layout/manual play/
callbacks. Official RitsuLib `0.5.4` contains the native-Hand lifecycle repair missing from
`0.5.0`; the human lead accepted the focused unmodified-runtime result and promoted the
Package on 2026-08-02. The strict structured Tier 2 harness was waived, not run. Historical
and official-version proof records remain under `documents/history/` and
`games/sts2/experimental/card-pile-extra-hand/`.

M6.7 is closed by explicit human-lead decision on 2026-08-04. It delivers version-bound
vanilla content overrides and behavior composition. M6.7.0 implements the grounding
kernel: the pinned `0.107.1` catalog contains 1624 vanilla models, checked title table/key
metadata plus localized display-title
aliases in all 14 pinned languages and exact assembly identity. M6.7.1
Public Card Overrides source development is implemented as the first promoted operation
Package, covering the grounded non-asset Card contributors and public behavior composition.
M6.7.2 Public Visual Overrides source development is also implemented as the second promoted
Package. It covers all 44 public RitsuLib `0.5.4` Card-material/external-asset providers
across Card/CardPool, Relic, Power, Potion, Orb, Act, Event/Ancient, Encounter, Affliction,
Enchantment, and Modifier targets, with exact Mod-local resources, typed/path alternatives,
fallback, cleanup, and same-surface conflicts. There is no vanilla Monster-body external
provider. Focused manifest/resource tests pass; a representative M6.7.2 C# compile was not
run in the sandbox. M6.7.3 Existing Ancient Extensions source development is implemented as
the third promoted Package. It supports public multi-option append and one fixed,
fingerprinted complete initial-option replacement Adapter for the nine pinned native
Ancients, plus Mod-owned subsequent pages, nested conditions, fixed Gold/HP/Max HP costs,
typed option presentation, deterministic effects, deck selections, fixed custom rewards,
native `Done()` choice history, and separate M6.7.2 visual composition. Three reviewed
Adapter targets fail closed on IL drift. `TheArchitect` is an ordinary Event in `0.107.1`
and is rejected by the Ancient routes. Focused manifest/localization/catalog tests pass;
one Darv replacement/page/portrait route was included in the consolidated Mod that the
human lead accepted as a whole; no individual-route observation is inferred, and unselected
Ancient behaviors and presentation paths remain unrun.
M6.7.4 Existing Vanilla Availability source development is implemented as the fourth
promoted Package. It supports the public 57-epoch gate for vanilla Cards, Characters,
ordinary Events, and shared `EVENT.DARV`; Relic/Potion epoch or permanent-disable filters
through six-dependency fixed Adapters; and Card/Relic/Potion pool add plus fixed
remove/move membership Adapters. Pool edits preserve vanilla model identity and existing
instances, require the pinned primary pool, reject debug/empty transitions, and are
singleplayer-only. Focused manifest/catalog/document-route tests pass. One representative
pool move was included in the consolidated Mod that the human lead accepted as a whole;
no individual-route observation is inferred, and unselected cache timing, unlock UI,
fresh-reward ordering/RNG, duplicate, and existing-save paths remain unrun.
M6.7.5 Existing Vanilla
Non-Card Data and Behavior source development is
implemented as the fifth promoted Package. It covers seven typed owner-capability families
with all 100 asynchronous `AbstractModel` hooks, 26 numeric hooks, 28 decision hooks, and
four typed Orb callbacks; sixteen intrinsic data routes; complete Relic/Potion/Power/Orb/
Enchantment/Affliction lifecycle bodies; Monster move graphs; paired runtime/all-possible
Encounter rosters; and complete ordinary Event initial options plus Mod-owned pages. Public
owner hooks compose, while complete suppression/replacement uses checked `0.107.1`
Adapters. The catalog now contains 4165 reviewed Adapter fingerprints, including 4145 for
M6.7.5. Affliction `AfterApplied`/`BeforeRemoved` are synchronous and can only be suppressed
with empty effect lists; async `OnPlay` and owner hooks retain their full routes. Focused
40-test manifest/catalog/localization/documentation checks and Python syntax pass.
Representative Relic, Monster, and Encounter routes were included in the consolidated Mod
that the human lead accepted as a whole; no individual-route observation is inferred, and
unselected non-Card families and ordinary Event paths remain unrun. On 2026-08-03
the human lead declared the approved
M6.7.0-M6.7.5 source-development matrix complete and canceled M6.7.6; multiplayer vanilla
overrides moved to Future Outlook and are not part of M6.7. The final regression passed
`165/165`, synchronized payloads were repeatable and identical, the installed-plugin
independent Mod built successfully, and the human lead reported the in-game effects passed.
Tier 1, Tier 2/SelfTest, the current-catalog headed no-op, and all unselected paths remain
explicitly unrun. The durable result is
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. Record a documented public route or
fixed reviewed Adapter for each requested operation/category before implementation; never
generate ungrounded Harmony, reflection, or IL from a prompt.

M7 Design Intelligence and User Experience is closed by explicit human-lead decision on
2026-08-05. The human lead canceled M7.0 as a standalone up-front evaluation Package on
2026-08-04; its essential behavioral cases traveled with the Packages that changed those
behaviors. M7.1 through M7.5 are implemented in source.
M7.1 adaptive Interview and routing is implemented in the source workflow. It adds an
inferred fast/co-design/revision route before Interview, direct unfinished-project resume,
material-question filtering, constrained contradiction/unsupported handling, and bounded
revision deltas that preserve settled decisions. Its six semantic scenarios and focused
contract tests cover clear, ambiguous, contradictory, unsupported, resume, and revision
inputs. No independent forward-model run, real-game acceptance, Tier 1, or Tier 2 is
inferred from those prompt contracts. The durable result is
`documents/history/M71_ADAPTIVE_ROUTING_RESULTS.md`.
M7.2 STS2-native design grammar is implemented in the source workflow. Character and
Character/content-set requests lazily load one version-pinned Foundation reference before
creative questions. It separates pinned facts, observed conventions, and creative
decisions; proposes one exact native-shaped starter deck before asking for deck details;
and preserves deliberate implementable departures after explaining onboarding,
Strike/Defend-tag compatibility, and early-balance consequences. Its checked inventory is
bound to the pinned assembly identity and the five native starter decks; exact tests cover
all ten Character-specific Strike/Defend models. Three semantic scenarios cover an
unspecified starter deck, a Character/content-set request, and a deliberate departure. No
independent forward-model run, game acceptance, Tier 1, or Tier 2 is inferred. The durable
result is `documents/history/M72_NATIVE_DESIGN_GRAMMAR_RESULTS.md`. M8.0 change 2 added the
inventory's native HP range, the 99 Gold constant, and the five Starter relic ids to that
reference, since a custom Character SPEC must supply `starting HP`. The pinned catalog has no
relic effect text: name a native Starter relic as an analogy and never describe its behavior
from memory.
M7.3 mechanic, content-set, and balance planning is implemented in the source workflow.
It adds three independently lazy references for meaningful mechanic decisions and loops,
content-role/interaction coverage, and evidence-bounded formulas/economies. Balance uses a
human-lead-selected Mod-forward bias: prefer a clearly rewarding, modestly stronger working
value over an underpowered no-pick option, but reduce or constrain any value that erases
choices, setup, costs, ordinary opposition, or creates deterministic/self-funding/unbounded
loops. This is a creative product preference, not a pinned STS2 fact or fixed percentage.
Its three semantic cases cover one ambiguous mechanic, one Character/content set, and one
numeric resource economy. Missing data remains an open hypothesis; static reasoning does
not prove balance, enjoyment, or playtest results. M7.3 lowers only accepted, supported,
exact rules, values, content nodes, and directed interactions into `SPEC.md`; it does not
create M7.4's durable `DESIGN.md` or widen runtime support. The durable result is
`documents/history/M73_MECHANIC_CONTENT_BALANCE_RESULTS.md`.
M7.4 scope and design-to-SPEC translation is implemented in the source workflow. Every
route writes an adaptive `open-mod-design/v1` `DESIGN.md` before SPEC: a fast exact request
gets a compact capsule, while co-design/revision preserve only relevant rationale and
settled decisions. Its scope ledger uses stable `D-###` requirements with exactly
`MUST`, `PLACEHOLDER`, `DEFER`, or `OUT-OF-SCOPE`; unresolved unsupported intent remains a
blocking gap until the human explicitly selects a supported current version, deferral, or
removal. `SPEC.md` contains an `open-mod-spec-trace/v1` generation allowlist with stable
`OP-###` operations, current design IDs, exact semantic targets, and existing shipped
recipe/reference routes. `design_trace.py` rejects missing/extra operations, one-way links,
future-item leakage, unresolved gaps, invalid dispositions/fallbacks, invented route forms,
and missing route files. Three semantic scenarios cover supported-plus-unsupported scope,
a future vision larger than the first playable slice, and compact exact-Card authoring. No
independent forward-model run, game acceptance, Tier 1, or Tier 2 is inferred. The durable
result is `documents/history/M74_SCOPE_TRACEABILITY_RESULTS.md`.
M7.5 theme, narrative, presentation, and coherence is implemented in the source workflow.
It adds one lazily loaded coherence reference, proportional `A-###` identity anchors and
six selected expression surfaces, specific fail-closed conflict handling, deliberate-
tension preservation, and an ordered `Q-###` revision impact queue. `coherence_trace.py`
checks design references, current-surface ownership, resolved conflicts, and revision queue
structure before SPEC; it does not judge subjective quality. Three semantic scenarios cover
Event localization/visual contradiction, Character identity tension, and a bounded
terminology/palette revision that preserves settled and rejected decisions. Two focused
read-only independent forward-model prompts covered the Character identity
conflict and bounded revision. The first conflict run exposed a missing temporary
`conflict` status; after the contract repair, its focused rerun correctly stopped before
SPEC. The Event case and complete three-case matrix were not independently run. No human
artifact review, game acceptance, Tier 1, or Tier 2 is inferred.
The durable source result is `documents/history/M75_COHERENCE_RESULTS.md`.
M7.6 closed through a human-led external whole-skill evaluation on macOS rather than a new
source-workflow Package. The generated Watcher Character/content-set Mod built, loaded,
and completed a bounded SelfTest record; the human lead's controlling playtest observation
was that it was playable but the result was not very good. Scry, composed Draw, Rushdown,
Devotion, draw-pile exhaustion, complete presentation, and a post-feedback DESIGN/SPEC
revision/replay were not proved. Do not infer a polished Character, complete Tier 2 matrix,
successful tuning loop, or M7.6 source implementation. The durable result and exact
exceptions are in `documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`.

M7 improved how the skill understands, discusses, scopes, records, and revises a Mod
design; it did not expand the runtime support graph. Simple, unambiguous requests retain a
fast path rather than receiving a full GDD process.

M8 End-to-End Product Integrity is the active milestone. It addresses the whole
skill: literal deliverable contracts, exact semantic capability preflight, semantic
backtracking, cross-platform installed-workflow reproducibility, and one final clean
whole-skill acceptance. M8.0 is closed; **M8.1 Literal Deliverable Contract is next
selectable** and needs its execution contract written against the settled layout and confirmed
with the human lead before implementation. M8.1-M8.6 hold plain-language intent only until
selected. The human lead removed M8.4 on 2026-08-05; M8.5 and M8.6 retain their numbers. The
Watcher evaluation is baseline evidence, not the M8 final acceptance Mod.

M8.0 Skill Structure Restructuring is closed by explicit human-lead decision on 2026-08-10. It
reorganized the shipped pack so an author reads one file per element instead of three per
stage. All ten elements are co-located under `games/sts2/skills/modmaker/surfaces/`; the Card
pilot has a real `[PASS] Tier-2 verified` run behind it and the other nine are co-located and
cross-checked but never piloted. Its cross-check record now holds thirteen mismatches, of which
three remain open and are live contradictions in the shipped pack: the flat
`element:` envelope form on six surfaces contradicts the canonical nested form
`semantic-contract.md` declares itself source-of-truth for, the character resource/ordered
buffer keep their envelopes in `spec.md` while their proof moved to the surface page, and no
mechanical check compares a generated project's `SPEC.md` against its surface envelope. Read
`games/sts2/tests/m80-surface-cross-check.md` before treating any surface page as validated;
being co-located and checked is not the same as being correct.

Change 4 is closed in source. The shipped pack states what is supported, not which Package
promoted it: a milestone id remains only where it is load-bearing — a manifest key like
`m6.7.1-public-card-overrides`, a Tier 2 marker, a resume-compatibility boundary such as
`pre-M7.4`, or an evidence attribution naming the run that grounded a fact. Do not reintroduce
a milestone id into a section heading, and never leave an instruction scoped to a closed
process window; `test_surface_cross_check.py` fails on both. That sweep found six reference
pages still telling readers to follow the M6.7 batch-window verification exception, which
closed on 2026-08-04.

Change 3 is closed in source. Diagnostic scars ("signature X means cause Y") live in
`sts2-api/errors.md`; preventive rules live where they fire, with `modmaker/quirks.md` holding
the ones an author needs before writing C#. The split is by *when* a line is needed:
constraints followed before a failure, signatures matched after one. A stage page delegates to
`errors.md` rather than restating a cause-and-fix list, and
`test_surface_cross_check.py` resolves every `errors.md §` pointer.

Change 2 is also closed in source. The art contract's exact values stay in `gen_sprite.SPECS`
and `character_art.CHARACTER_ART_BUNDLE` and are projected into
`games/sts2/skills/sts2-api/reference/catalogs/art-contract-sts2-0.107.1.json` by
`gen_sprite.py export-contract`. Never hand-edit that catalog and never treat it as a second
definition; change a size in the code and re-export. `test_art_contract_catalog.py` fails when
the catalog is stale or when any of the three prose views disagrees with it. Comparing prose
against code found mismatch 12: the combat-cue sheet grid is columns-first everywhere in prose
but was printed rows-first by `list-specs`, live on the only non-square sheet.

Change 5 is closed in source. The eight rules that fire at every stage are stated once in
`modmaker/invariants.md` as `INV-1` through `INV-8`; a stage page names the invariant and adds
only its own stage-specific detail. That page is the one exception to lazy loading: it is read at
pipeline start and kept in context, because a pointer replacing a rule in a page that may not be
read leaves zero copies of it, which is worse than several drifting copies. Do not demote it to
lazy loading, do not restate an invariant in a stage page, and do not consolidate a rule that
fires at one stage only — the repair attempt cap and the art-consent boundary stay where they
fire. `test_invariants.py` fails on a dangling `INV-n`, an invariant no stage names, a
restatement of a canonical phrasing, and a lost eager-load registration.

Both committed payloads were regenerated from source on 2026-08-10 after change 5 and carry all
five changes; rendering is repeatable and no payload was installed or run. The three open
mismatches were deferred to M8.2 by the human lead on 2026-08-10: the envelope form is a
contract-version migration overlapping M8.2's recorded ownership, and the other two depend on that
decision. The durable result is `documents/history/M80_SKILL_STRUCTURE_RESULTS.md`. Do not
re-execute the closed M8.0 contract in `documents/IMPLEMENTATION_PLAN.md`; it is retained as a
record of what was found, not as a work order.
Its concrete Exhaust-text, Scry, Hover Tip, Wrath, and leaked-process observations are not
a Watcher repair queue. They define three whole-skill controls: complete player-facing
operation semantics, maintained semantic capabilities with conformance proof, and
cross-platform ownership of every process the tools start.
M8.1 is selectable, but write and confirm its execution contract with the human lead before
implementing it. Do not edit installed payloads in place, run a fresh acceptance, or publish a
payload/release without later human-lead instruction. The active Package plan is
`documents/IMPLEMENTATION_PLAN.md`. Its New-Session Start Protocol and Package Execution
Contracts are authoritative: when the lead says "start M8" or "continue M8", select or
resume the first eligible Package, read its listed source, and execute that contract rather
than re-planning the milestone or asking the lead to choose among later Packages. Never
skip a prerequisite. Closing a Package requires its named history result plus synchronized
status in the current documents that own changed facts; the result must also list current
documents reviewed but left unchanged.

Pre-M7 maintenance removed the retired Wayfinder proof identity and exact proof values from
generic Character verification/reference text. Historical facts remain under
`documents/history/`; shipped verification derives HP, pools, starters, resources, effects,
and terminal markers from the current `SPEC.md`. Keep the regression check that prevents a
retired proof identity from returning to source or generated payloads. `Pathfinder` is not
present in the current source or payloads.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.5.4`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.5.4`.
- Runtime discovery reuses a validated game-local install or official Steam Workshop item
  `3747602295`; newer RitsuLib versions are accepted only with the exact `0.107.1` compat
  variant, marker, and manifest hash. The compile package remains exactly `0.5.4`.
- Generated Mods must not reference, package, or depend on BaseLib.
- Do not use Alchyr templates or restore historical BaseLib implementation snippets.
- `baselines/BaseLib-StS2` and `baselines/downfall` are offline historical research only.
- `baselines/STS2-RitsuLib` is the maintainer research checkout; generated Mods consume
  the pinned package/runtime profile instead of copying it.
- `baselines/decomp` is the gitignored maintainer-only STS2 `0.107.1` decompiled research
  snapshot, as confirmed by the human lead. It contains the full game decompile, a focused
  `RelicModel` extract, and decompiled Mod analyzers. The original DLL hash/provenance
  sidecar was not retained, so recheck every promoted version-bound fact against the pinned
  `0.107.1` assembly/catalog or current installed game. Never copy, compile, package, or
  ship decompiled code; private/internal implementation does not establish a supported route.
- `baselines/SlayTheSpire2ModdingTutorials` is the official-tutorial product-semantics
  checkout pinned at `5a9110b`. It establishes intended use and documented feature-Package
  membership, not stable-version signatures; exact APIs still come from RitsuLib `0.5.4`.
- `baselines/Sts2-YuWanCard` is a same-game-version Character/content-depth research
  checkout pinned at `07d7daa`. Its gameplay and Character framework is self-built with
  Harmony/Publicizer; RitsuLib is optional settings UI only. Use it to inventory consumers
  and study product behavior, never as RitsuLib API authority or a source of shipped code,
  art, audio, Spine, shader, or other assets.
- `baselines/spire-codex` is a maintainer-only vanilla-content fact and analogy source. M7
  may use it to find design patterns, but every shipped version-bound fact must be checked
  against the pinned `0.107.1` catalog/game substrate before promotion.
- `baselines/Claude-Code-Game-Studios-main` is M7 workflow and behavioral-evaluation
  research only. Do not copy its large agent hierarchy, make it a runtime dependency, or
  treat its generic design advice as STS2 fact.

## Supported Boundary

Use one simple Package-level rule: when the official tutorials document a RitsuLib
feature's player-facing use and Package, and the needed public API exists in the pinned
RitsuLib/compat profile, all documented public consumers in that Package are supported.
They do not need separate support declarations, recipes, tests, or real-game proofs first.
Record a confirmed API or lifecycle problem as the smallest known limitation. Call a
feature unsupported only when the pinned profile has no documented public route, a required
public member is absent, or the only route requires forbidden Harmony, reflection,
Publicizer, or IL generation.

Missing recipes, validators, builds, Tier 1/Tier 2 runs, or headed reviews mean only that
implementation or verification is missing; state that directly. Do not add readiness levels
or evidence badges. Verification remains literal under the rules below, and skipped checks
or waivers remain exceptions rather than passes.

M7 design recommendations must remain inside this same runtime boundary. A broader future
vision may be recorded in `DESIGN.md`, but the current deliverable slice and `SPEC.md` must
contain only promoted operations or explicit gaps. General game-design confidence never
authorizes ungrounded Harmony, reflection, Publicizer, or IL.

M8 planning does not change the current support graph. M8.2 may promote a reusable generic
capability only through maintainer-owned pinned research, an exact public/fixed route,
semantic-conformance cases, documentation, and synchronized payload validation. Until
then, an identity-critical behavior with no maintained exact implementation is a blocking
generation gap, not permission for a consumer project to approximate or replace it. A
currently claimed route that fails its maintained semantic contract must also block until
the shared implementation is repaired or the limitation is narrowed. Machine-checkable M8.2
metadata belongs with the existing authoritative recipe/reference route; do not create a
separately maintained capability catalog beside those routes and the current capability
graph.

Surfaces open-mod currently generates include:

- card, relic, potion, power, keyword, enchantment, and orb;
- computed Card Damage/Block, Energy/Star icon counts, raw and amount-given typed Power
  values, and localized DynamicVar tooltips under one preview/execution formula;
- deterministic Mod-local live-creature filters for single-target Cards/Potions and
  multi-target Cards, with native mouse/controller selection and resolution-time checks;
- generated-Mod-local singleplayer top-X Scry with normal selection/discard history/hooks;
- monster + encounter and the complete grounded move vocabulary;
- Event / World Node outcomes, bounded rich text/VFX/native presentation, and one bounded
  solo Quest Card -> forced Event composition;
- playable Character Foundation, nine checked static art profiles, and bounded private
  `Idle`/`Attack`/`Hit`/`Dead` combat cues;
- custom-Character localization dialogue across the nine cataloged native Ancient and
  Architect scenes while preserving their native models, layouts, options, and outcomes;
- singleplayer Relic-owned custom Rest Site options with free/fixed Gold, deterministic
  preflightable outcomes, once-per-site/run use, native stay/leave behavior, and checked
  256x169 custom/Heal-fallback icons;
- stateful relic cadence, combat-only secondary resources, all-or-nothing payment, public
  fixed combat UI, and ordered semantic buffers using normal Play -> Discard.
- complete documented Custom Card Piles Package authoring across combat/run lifetime,
  headless/top-bar/bottom-corner/ExtraHand presentation, public screens/views/hotkeys,
  deterministic visibility, native Card movement, localization, and ExtraHand interaction.
- the M6.7.0 vanilla grounding kernel: checked `0.107.1` catalog, exact internal and
  localized-display-title alias resolver,
  empty semantic manifest, expected-baseline/fingerprint/conflict validation, and no-op
  scaffold/build/deployment wiring.
- M6.7.1 Public Card Overrides for type/rarity/target, appended tags, evaluated Energy/Star
  costs, conditional playability, result piles, title/description/type-text composition,
  hover tips, native gold/red glow, capability-owned variables, recipe-backed `OnPlay`
  before/after/replacement, and owner draw/discard/exhaust composition.
- M6.7.2 Public Visual Overrides for all 44 public Card-material/external-asset providers:
  exact vanilla Card/CardPool, Relic, Power, Potion, Orb, Act, Event/Ancient, Encounter,
  Affliction, Enchantment, and Modifier targets; Mod-local Material/texture/PackedScene/
  Spine/directory/list resources; deterministic raster normalization where an established
  `gen_sprite.py` role matches; typed/path fallback; same-surface conflicts; and cleanup.
- M6.7.3 Existing Ancient Extensions for the nine pinned `AncientEventModel` targets:
  public multi-option append or one fixed complete initial-option replacement; nested
  conditions, visible/locked rules, fixed Gold/HP/Max HP costs, typed Hover Tips and
  relic-backed presentation, ordered deterministic outcomes, deck upgrade/remove/
  transform/enchant selection, fixed custom rewards, Mod-owned subsequent pages, native
  finish/choice history, full shipped-language `events.json`, and separate M6.7.2 visuals.
- M6.7.4 Existing Vanilla Availability for pinned epoch gates and Card/Relic/Potion pool
  add/remove/move membership, with Relic/Potion fixed epoch/disable filters, complete
  baseline simulation, primary-pool checks, singleplayer scope, and existing-instance
  preservation.
- M6.7.5 Existing Vanilla Non-Card Data and Behavior for Relic/Potion/Power/Orb/
  Enchantment/Affliction/Monster public owner-hook composition; all pinned public effect,
  numeric, decision, and typed Orb callbacks; sixteen intrinsic data routes; complete
  checked lifecycle/body replacements; Monster move graphs; paired Encounter rosters; and
  ordinary Event options/pages with full shipped-language `events.json`.

Generated readability APIs include conditional Card Hand Glow, up to three safe-corner
Relic labels, and one top-left Power label from the RitsuLib Extra Badges family. Intent
remains a supported public Extra Badges consumer, but Intent authoring is not scheduled.

Preserve these important boundaries:

- Route stores semantic direction values, never retained played Card instances.
- A source Card follows STS2's normal result pile lifecycle.
- Scry is singleplayer and Mod-local; it is not a global interoperability service.
- Rest Site options are Relic-owned and singleplayer-only; Card/Modifier owners, variable
  or non-Gold costs, post-payment choices, arbitrary transactions, same-site repeat, and
  multiplayer remain unsupported.
- Custom Card Piles use official public RitsuLib APIs only. Generated Mods must not recreate
  the framework's native-Hand bridge, patch pile internals, or narrow the documented Package
  merely because a selected consumer lacks a focused proof.
- Pinned Affliction `AfterApplied()` and `BeforeRemoved()` are synchronous `void` methods.
  A complete M6.7.5 lifecycle replacement may suppress them only with empty generated
  effect lists; async `OnPlay` and public owner-hook composition remain available.
- The fixed Character resource control is 220x32 at offset 160 with a text fallback and
  must remain disjoint from native Energy.
- Custom locked-selection/map-marker presentation, new Ancient models, global native
  dialogue/room replacement, Ancient behavior outside the fixed M6.7.3 option/page/effect
  vocabulary, randomized outcome/RNG rewrites, special combat and direct merchant/rest/
  treasure transitions,
  production animation beyond the bounded cues, line audio,
  the custom multi-target Potion lifecycle limitation, global acquisition weighting,
  Card/Character/Event permanent disable without a reviewed route, behavior-bearing scene/material
  generation outside the promoted M6.7.2 resource routes, audio,
  remote-player UI, alternative Energy, retained-card zones, and one-click Workshop
  publishing retain their recorded boundaries. Outside the promoted M6.7.1 public Card,
  M6.7.2 public visual, M6.7.3 existing-Ancient, M6.7.4 availability, and M6.7.5 non-Card
  data/behavior routes, nonempty M6.7 operations are not generated until their delivery
  package records and promotes a documented public/fixed-Adapter route for the requested
  operation/category. Source-specific weighting and unpromoted disable surfaces remain
  unsupported. Multiplayer vanilla overrides are future work outside M6.7 and remain
  unsupported until a separately selected track promotes them.

For the exact active inventory, read
`games/sts2/tests/content-capability-graph.md`.

## Art Contract

`gen_sprite.py` is framework-neutral. RitsuLib `*AssetProfile` consumers or an exact
M6.7.2 external visual provider own runtime wiring. The verified Character profiles are
selection portrait/background, top-panel
main/outline icons, combat/rest/merchant static bodies, five full-energy layers, and
distinct large/text Energy icons. Optional combat cues are a private combat-only frame
set, not a profile-global animation replacement.

The exact paths, sizes, fit, chroma, and fallbacks live in `gen_sprite.SPECS` and
`character_art.CHARACTER_ART_BUNDLE`; read them as data in the generated
`sts2-api/reference/catalogs/art-contract-sts2-0.107.1.json` rather than re-deriving a size.
Cue sheet grids are columns x rows of 512x512 cells.

Host-native image generation is optional. Use it only when a callable raster tool returns
a local image. Do not infer availability from a text-model name or installed skill, and do
not silently select a paid backend. Every acquisition path converges on deterministic
`gen_sprite.py import` normalization and retains the supported fallback.

## Architecture

- Current `games/sts2/skills/modmaker/`: state check -> inferred fast/co-design/revision
  route -> adaptive interview -> coherence-checked `DESIGN.md` -> validated current-slice `SPEC.md` ->
  scaffold -> author -> build -> verify -> bounded repair. An unchanged unfinished project
  resumes directly at its first incomplete stage; a pre-M7.4 project backfills DESIGN from
  accepted SPEC without restarting its interview.
- Planned M8 flow adds a literal completion claim and exact semantic preflight before
  generation; treats behavior, lifecycle, rules text, keyword/DynamicVar and Hover Tip
  discoverability, localization, preview, and real-consumer presentation as one operation;
  semantic-impact repair returns to the artifact that owns the changed fact; and the
  installed workflow must reproduce without in-place skill edits or an owned child process
  left running. None of that planned flow is implemented yet.
- `games/sts2/skills/sts2-api/`: lazy recipes, references, and error catalog.
- `games/sts2/tools/`: cross-platform Python build/launch/log/art wrappers.
- `games/sts2/tests/`: current support graph and verification ownership.
- `games/sts2/experimental/`: repository-only implementation research excluded from formal
  skills and generated payloads.
- `plugins/open-mod/`: generated Codex plugin payload from `publish.sh --plugin`.
- `skills/`: generated portable Agent Skills payload from `publish.sh --portable`.
- `.agents/plugins/marketplace.json`: repo-local Codex marketplace entry.

Edit source under `games/sts2/`; never hand-edit generated payload contents. Regenerate and
validate both committed payloads after source changes. The M6.7 closure payloads were
synchronized from that source and accepted through the reinstalled plugin.

## Verification

Keep verification proportional:

1. Contract checks for deterministic calculations and state rules.
2. Reuse the closest hosted scenario (`CombatPlayer`, `CombatEnemy`, `MapNode`, or
   `RunStart`/Character) for live behavior.
3. For an ordinary feature or bug fix that affects generated-Mod behavior or presentation,
   stop after the changed behavior is proved in the nearest real game host. Reuse a
   maintained scenario when possible, or create one narrow disposable proof; do not run a
   complete demo Mod after every change.
4. Use a fresh natural-language acceptance Mod only when the current
   `documents/IMPLEMENTATION_PLAN.md` explicitly schedules a full-pipeline gate or the
   human lead asks for one. Record durable evidence, then retire the acceptance Mod.

M6.7 used a temporary milestone-level batching exception approved by the human lead on
2026-08-03 and closed on 2026-08-04 after one final source regression, synchronized
payloads, an independent installed-plugin build, and the lead's representative in-game
acceptance. Do not rerun that milestone gate or expand it into an exhaustive provider/hook
matrix. Preserve the unrun Tier 1, Tier 2/SelfTest, current-catalog no-op, and unselected
paths recorded in `documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`.

Do not turn a focused change into an unscheduled end-to-end acceptance exercise. Local
documentation or tooling changes that cannot affect generated runtime behavior need only
the proportionate non-game checks. Historical evidence stays immutable: do not modify an
archived acceptance project or reopen a retired migration proof to test new work.

Verification does not decide Package support. Preserve exact Tier 1/Tier 2/headed wording
and record missing checks as exceptions even when the surrounding Package is supported.

Tests protect semantic behavior, generated artifacts, and dependency boundaries. Do not
assert exact adapter API symbols or recipe wording merely to prove that a recipe uses
RitsuLib rather than BaseLib; enforce that product contract at scaffold, build, manifest,
and runtime-package boundaries. Assert a specific symbol or phrase only when it is itself
a pinned compatibility or output contract.

M7 prompt and authoring tests use behavioral scenarios and semantic rubrics, not exact prose
snapshots. They must cover question economy, preserved user decisions, meaningful
alternatives and trade-offs, STS2-native defaults, supported-slice grounding,
`DESIGN.md`-to-`SPEC.md` traceability, cross-artifact coherence, bounded change propagation,
and refusal to fabricate playtest evidence. A
documentation- or prompt-only M7 change does not require a real-game run unless it changes
generated runtime behavior or presentation.

M8 tests must preserve end-to-end product meaning rather than merely add another document
schema. Cases travel with the Package that changes the behavior and must cover literal
completion claims; exact maintained operation routes; behavior/lifecycle/rules-text/
keyword/Hover-Tip/localization/preview/presentation parity in real consumers; complex
mechanic selection, ordering, movement, hooks, degenerate states, and input modes; semantic
repair backtracking; and immutable installed workflows that clean up only their owned
process trees and leave no owned child running. M8.6 is the only planned fresh natural-
language whole-skill gate; it is not authorized to run yet.

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof plus `selftest done`. Trigger logs and model-only state do not
prove behavior or presentation. Run one armed harness at a time and preserve unrelated
user Mods.

Current commands:

```powershell
python games/sts2/tools/scaffold.py --project-dir <outer-dir> --mod-name <ModName> --author <Author>
python games/sts2/tools/build.py --project-dir <outer-dir> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured proof>"
```

The outer project directory name must differ from the Mod name.

## Branch And Commits

- Work on `Henry's_cc`.
- Never merge or open a PR to `main`.
- `Henry's_branch` is snapshot-only; merge `Henry's_cc` into it only when asked.
- Preserve unrelated dirty-worktree changes.
- Wait to be asked before committing.
- Use Conventional Commits and an appropriate AI co-author trailer.
- Stage specific files, never `git add .`.

## Windows

The verified environment uses PowerShell, STS2 `0.107.1`, .NET SDK `9.0.300`, Python 3,
and RitsuLib `0.5.4`. Use PowerShell syntax for normal commands. Invoke `publish.sh`
through an explicit Git Bash executable when needed; do not mix Bash path syntax into
PowerShell commands.

## Active Documents

- `documents/PROJECT.md`
- `documents/IMPLEMENTATION_PLAN.md`
- `documents/BASELINE_RESEARCH.md`
- `games/sts2/tests/README.md`
- `games/sts2/tests/content-capability-graph.md`

Migration results are in `documents/history/RITSULIB_MIGRATION_RESULTS.md`.
