---
name: sts2-api
description: |
  Query the STS2 game pack for concrete modding knowledge: element recipes,
  command APIs, localization rules, error fixes. Use when the main pipeline
  needs a specific answer (hook signature, Cmd name, loc-key rule) rather than
  loading the whole pack into context.
---

# STS2 API Lookup

## Design grammar and planning routing

After `modmaker/route.md` classifies the request, load only the design references named in
its handoff:

- read `../sts2-api/design/character-foundation.md` for a playable Character,
  its Foundation, or a Character/content-set design, before creative questions or a
  starter-deck proposal; load it only for that Character surface;
- read `../sts2-api/design/mechanic-planning.md` when a mechanic, resource,
  stateful loop, risk/reward structure, or interacting system lacks an exact core
  decision;
- read `../sts2-api/design/content-set-planning.md` for a Character card pool,
  archetype, multi-element set, or another content ecosystem; and
- read `../sts2-api/design/balance-planning.md` when balance, numeric resource
  sources/sinks/cadence, a formula, or materially unresolved values are a current design
  question.

The references separate pinned facts, observed conventions, creative decisions, and open
hypotheses. Load the smallest applicable set: an exact simple Card does not load balance
planning merely because it contains a number. These files provide design guidance, not an
adapter, runtime route, playtest result, or expanded capability boundary.

This skill is a narrow reference tool. Answer only what the caller asked — do
not dump entire files into the response.

## Adapter routing

For generated content, the semantic contract is the product-level source of truth:
read `./semantic-contract.md` before selecting an implementation.
Lazily read `reference/ritsulib-adapter.md` next. It
pins RitsuLib `0.5.11` against STS2 `0.107.1`, maps each semantic surface to one public
registration/template and asset profile, and owns the framework/version diagnostic
record. Only then load the surface recipe or reference needed for the request.

Official tutorial semantics plus public members in the pinned profile make all documented
consumers in that feature Package supported. A missing shipped recipe means only that the
authoring route is not implemented here; report that plainly and never guess the absent
implementation.

RitsuLib is the only active adapter. Do not select a historical dependency, copy another
scaffold, or infer a runtime dependency from a recipe name.

When the request edits an existing vanilla model, read
`../sts2-api/reference/vanilla-overrides.md` before any new-content recipe. The
grounding kernel there resolves and validates the pinned target. For a selected visual surface,
continue to `../sts2-api/reference/vanilla-visual-overrides.md`, which owns
all 44 public Card-material and external-asset providers. For a non-asset exact Card
target, continue to `../sts2-api/reference/vanilla-card-overrides.md`, which owns
its property/cost/play-state/text/tip/glow/capability/behavior routes. For an
exact Relic/Potion/Power/Orb/Enchantment/Affliction/Monster/Encounter/ordinary Event data
or behavior request, continue to
`../sts2-api/reference/vanilla-non-card-overrides.md`, which owns the complete
public owner-hook surface plus checked intrinsic-data and complete-body Adapters. For an
exact Card/Character/ordinary Event/shared Darv
epoch gate, or a Card/Relic/Potion pool membership change, continue to
`../sts2-api/reference/vanilla-availability-overrides.md`, which owns the
public `RequireEpoch`/`AddModelToPool` routes plus the reviewed Relic/Potion and pool getter
Adapters. For an exact existing Ancient's option/branch request:
continue to `../sts2-api/reference/vanilla-ancient-overrides.md`, which owns
public multi-option append plus one fixed fingerprinted replacement/page-flow Adapter.
Other operations remain grounding-only. Never derive a patch body from the prompt or
silently convert the request into new content.

A request to replace, remove, or hide a vanilla Card's original description is a blocking
base-description replacement gap under RitsuLib `0.5.11`. Report that only before/after
fragments exist and stop. Do not return an appended-text implementation unless the user has
explicitly accepted composition instead.

## How to answer

1. Check `../sts2-api/recipes/` for the element or mechanic type (relic, potion,
   card, power, keyword, enchantment, orb, monster+encounter, event, character). For a **fought enemy** read
   `recipes/monster.md`; it owns separate Monster/Encounter registrations, explicit roster
   edges, HP ranges, and deterministic/conditional/fixed-weight-random move graphs.
   For a **World Node/event** read `recipes/event.md` — it covers RitsuLib registration,
   flat nested `events.json`, explicit option keys, the fast-path consequence, checked
   portraits, and the `MapNode` proof. Also
   read `../sts2-api/reference/event-outcomes.md` when options use selections,
   custom rewards, conditional pages, or special combat. Read
   `../sts2-api/reference/event-vfx.md` only when SPEC selects the bounded
   normal-layout `portrait_halo` profile. Read
   `../sts2-api/reference/event-text-effects.md` when Event page/option
   descriptions use the bounded vanilla rich-text vocabulary. Read
   `../sts2-api/reference/event-option-presentation.md` when enabled Event
   options use typed Hover Tips, relic-backed presentation, or exact HP/Max HP costs.
   Read `../sts2-api/reference/event-native-presentation.md` when an Event
   option acquires a Card/relic with native presentation, selects the bounded one-shot
   screen shake, or uses the curated `trial_noble` built-in VFX profile.
   Read `../sts2-api/reference/forced-followup-event.md` when custom Quest Cards
   declare a finite prioritized act-set to custom-Event mapping or sequence.
   For a **playable character Foundation** read `recipes/character.md` — it covers the
   RitsuLib typed template, one content-pack registration, three pools, starters, two-table
   localization, static profile/fallback, and `RunStart` + `CombatPlayer` proof.
   When Character SPEC selects static art, combat cues, or richer resource/buffer UI, also read
   `../sts2-api/reference/character-presentation.md`. It separates the nine
   live-proven static consumers, combat cues, and dedicated native-Ancient dialogue route.
   When it selects custom-Character dialogue in a cataloged native Ancient or Architect,
   read `../sts2-api/reference/ancient-dialogue.md`; use its flat localization,
   build validation, native priority, and proof route without generating a patch.
   For the bounded non-Spine `Idle`/`Attack`/`Hit`/`Dead` frame sequences, additionally
   read `../sts2-api/reference/character-combat-cues.md`; keep its cue set private
   to the combat state machine and preserve its all-or-nothing static fallback.
   For one or more bounded **secondary resources with explicit payment and selected UI**,
   read `../sts2-api/reference/character-resource.md`. For a **bounded ordered
   semantic card-play buffer with deterministic dynamic output**, read
   `../sts2-api/reference/ordered-card-buffer.md`. Both use the public RitsuLib
   Secondary Resource/node-attachment APIs and follow the promoted generated-Character
   contracts. If a requested capability has no documented public game/RitsuLib
   seam, report a pack gap; do not invent a patch target or `OpenMod.Runtime`.
   Cards/powers/keywords/enchantments/orbs also read
   `../sts2-api/reference/mechanics.md` first (scaling numbers, SmartFormat
   descriptions, shared enums). When Card/relic/potion/power descriptions select bounded
   vanilla colors, also read `../sts2-api/reference/content-text-effects.md`.
   When a Card has calculated description values, Energy/Star icon counts, typed computed
   Power amounts, or variable tooltips, also read
   `../sts2-api/reference/card-computed-values.md`. It owns the shared-formula,
   evaluation-timing, formatter, execution-helper, and tooltip proof contracts.
   When a Card selects conditional hand emphasis, read
   `../sts2-api/reference/card-hand-emphasis.md`. It owns ordered rules,
   priority/tie resolution, native gold/red versus typed outline lowering, unplayable
   visibility, refresh boundaries, and headed hand proof.
   When a Relic or Power selects supplemental corner values, read
   `../sts2-api/reference/extra-corner-labels.md`. It owns safe-corner/count/text
   bounds, plain/bounded-rich specs, refresh/removal, and real-consumer proof. Do not route
   that generated authoring guidance to Intent.
   When a Card or Potion selects one or many live creatures through a declarative filter,
   read `../sts2-api/reference/advanced-targeting.md`. It owns the custom target
   registration, selection/resolution lifecycle, supported consumer matrix, and headed
   mouse/controller proof.
   When a Relic contributes an owned action to the native Rest Site, read
   `../sts2-api/reference/rest-site-options.md`. It owns the singleplayer-only
   free/fixed-Gold contract, absence versus disabled state, final payment recheck,
   repeatability, stay/leave lifecycle, icon fallback, and focused real-host proof.
   When the Mod declares one or more custom Card piles, read
   `../sts2-api/reference/card-piles.md`. It owns the complete documented Card
   Piles Package: combat/run scope, every public UI style and anchor, open/view/visibility/
   hotkey behavior, native movement, localization, and ExtraHand layout/manual play/
   callbacks. Do not reduce routing to only the consumers already exercised by a focused
   proof.
   For any effect that remembers progress (every N events, once per combat, previous
   turn, limited run uses), read `../sts2-api/reference/stateful-mechanics.md`.
2. For error signatures → fix, read `../sts2-api/errors.md`.
3. For content facts (what effects exist, a vanilla analog, realistic numbers) or a
   symbol the recipe lacks, read `../sts2-api/grounding.md` and, for
   potions, `../sts2-api/reference/potions-snapshot.md`.
4. For the **tier-2 self-test harness** (`SelfTest.cs`, the automated effect check), read
   `../sts2-api/reference/selftest-harness.md`.
5. For **custom art** (a card portrait's path + size, the prompt template, host-native
   `image_gen` routing when callable, and `gen_sprite.py` usage), read
   `../sts2-api/reference/art-contract.md`.
6. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

**Never read all files at once.** Each file is loaded on demand.

## Files in this pack

| File | Content | When to read |
|------|---------|--------------|
| `design/character-foundation.md` | Pinned five-Character starter inventory, Strike/Defend facts, native-shaped recommendation, and deliberate-departure consequences | Designing or revising a playable Character or Character/content set, before creative questions |
| `design/mechanic-planning.md` | Player fantasy, core decision, loop, risk/reward, singleplayer pressure, edge cases, tuning knobs, and dominant-strategy review | Designing or revising a materially unresolved mechanic, resource, stateful loop, or interacting system |
| `design/content-set-planning.md` | Foundation/access/payoff/consistency/defense/scaling/bridge/release roles, directed interaction graph, coverage, and dominance review | Designing a Character card pool, archetype, multi-element set, or content ecosystem |
| `design/balance-planning.md` | Evidence hierarchy, Mod-forward power bias, formulas, resource economy audit, sensitivity, tuning knobs, and open hypotheses | Answering a balance/economy question or selecting materially unresolved numeric values |
| `reference/ritsulib-adapter.md` | Pinned RitsuLib compat profile, public registration/template routing, asset profiles, lifecycle/persistence/resource routes, and diagnostics | After the semantic SPEC and before a surface recipe |
| `reference/vanilla-overrides.md` | Pinned vanilla catalog, exact alias resolution, semantic manifest, promotion, baseline/fingerprint, and conflict checks | Any request targeting existing vanilla content; before category-specific routing |
| `reference/vanilla-card-overrides.md` | public existing-Card operations: properties, evaluated costs, play state/result, localized text/tips, native glow, capability variables, owner hooks, and `OnPlay` composition/replacement | Authoring an override for an exact existing `CARD.*` target |
| `reference/vanilla-visual-overrides.md` | complete 44-route visual registry matrix, Mod-local resource manifest, typed loading/fallback, conflicts, cleanup, and art/complex-resource boundary | Authoring a visual override for an exact existing vanilla model |
| `reference/vanilla-ancient-overrides.md` | existing-Ancient option append/replacement, conditions/costs/tips/effects/pages, Mod-local localization, and exact finish/page/replacement Adapter fingerprints | Authoring options or page progression for an exact existing `content_kind: ancient` target |
| `reference/vanilla-availability-overrides.md` | pinned epoch gates, Relic/Potion override filters, and Card/Relic/Potion pool add/remove/move routes with primary-pool checks | Authoring a grounded availability or pool-membership operation for an exact vanilla target |
| `reference/vanilla-non-card-overrides.md` | complete non-Card owner-hook surface, sixteen intrinsic data routes, and complete Relic/Potion/Power/Orb/Enchantment/Affliction/Monster/Encounter/ordinary Event behavior replacements | Authoring grounded data or behavior for an exact existing non-Card target |
| `recipes/relic.md` | Relic trigger/effect/state behavior, localization fields, fallback, and proof obligations | Authoring a relic after adapter selection |
| `recipes/potion.md` | Potion usage/target/effect behavior, localization fields, fallback, and proof obligations | Authoring a potion after adapter selection |
| `recipes/card.md` | Card play/target/scaling/upgrade behavior, localization fields, fallback, and proof obligations | Authoring a card after adapter selection |
| `recipes/power.md` | Power stack domains, trigger behavior, safe mutation, display fields, and proof obligations | Authoring or consuming a custom buff/debuff after adapter selection |
| `recipes/keyword.md` | Keyword behavior-vs-display boundary, host attachment, text-only fallback, and proof | Authoring shared card-mechanic vocabulary after adapter selection |
| `recipes/enchantment.md` | Enchantment host restrictions, persistent change, 64x64 icon consumers/fallback, and proof | Authoring a persistent Card modification after adapter selection |
| `recipes/orb.md` | Orb channel/passive/evoke behavior, 100x100 icon consumers, explicit body/SFX fallbacks, and proof | Authoring an orb plus its host after adapter selection |
| `recipes/monster.md` | Separate Monster/Encounter nodes, explicit rosters, HP ranges, deterministic/conditional/weighted-random moves, static combat+bestiary body, fallback, and selected `CombatEnemy` checks | Authoring a fought enemy graph after adapter selection |
| `recipes/event.md` | Event / World Node pages/options, outcomes, checked portraits, and `MapNode` proof | Authoring a map event after adapter selection |
| `recipes/character.md` | Character Foundation pools, starters, localization, selection/run behavior, fallbacks, and proof | Authoring a playable character shell after adapter selection |
| `reference/ancient-dialogue.md` | Pinned vanilla Ancient catalog, semantic visit groups, flat RitsuLib localization, structural validator, native priority, Architect attackers, and focused proof | Authoring or verifying custom-Character dialogue in native Ancient scenes |
| `reference/character-presentation.md` | RitsuLib Character profile/consumer matrix; nine live static profiles; no-editor raw-scene packing; five-layer energy scene; split card/text Energy icons; bounded theme; native Ancient/Architect proof boundary | Authoring or verifying Character static/native presentation |
| `reference/character-combat-cues.md` | Bounded non-Spine Idle/Attack/Hit/Dead sheets, deterministic frame normalization, private combat cue wiring, shared geometry, all-or-nothing static fallback, and hosted proof | Authoring or verifying Character combat cues |
| `reference/event-outcomes.md` | Full normal-Event outcome vocabulary: immediate Cmd combinations, multi-page/locked options, blocking card selections, custom rewards, resumable/terminal special combat, extra combat rewards, one-combat-per-instance boundary, and unsupported room transitions | Authoring an Event beyond the one-Cmd fast path |
| `reference/event-vfx.md` | Bounded code-native normal-layout `portrait_halo`: page parameters, Fast Mode behavior, `OnRoomEnter`/portrait host, explicit named-node cleanup, and headed acceptance contract | Authoring the supported Event portrait VFX profile |
| `reference/event-text-effects.md` | Bounded normal-Event rich text: vanilla-observed color/emphasis/`jitter`/`sine` tags, safe nesting, native host lifecycle, headed proof, completed native-presentation inventory, and the speech-bubble future boundary | Authoring styled Event text or preserving adjacent presentation gaps |
| `reference/content-text-effects.md` | Per-surface vanilla rich-text allowlists for Card bodies/Card previews and standard relic/potion/power Hover Tips; SmartFormat and auto-keyword composition; headed proof contract | Authoring styled Card/relic/potion/power descriptions |
| `reference/event-option-presentation.md` | Enabled Event option typed Hover Tips, normal `CreateModRelicOption<T>` text/metadata plus its Ancient-only image blocker, and native exact-lethal HP/Max HP warning glow | Authoring those normal-layout Event option presentation contracts |
| `reference/event-native-presentation.md` | Ordered native Card/relic acquisitions, allowlisted preference-respecting `weak_short`/`strong_normal` shake, and curated `trial_noble` Event VFX | Authoring native presentation items 4-6 for a normal Event |
| `reference/forced-followup-event.md` | Finite prioritized Quest Card -> act-set -> custom Event mappings/sequences, pool exclusion, saved progress, terminal consumption, and fail-closed conflicts | Authoring a bounded delayed/conditional Event follow-up |
| `reference/character-resource.md` | Multiple bounded RitsuLib secondary resources, combat/run policies, fixed/X and required/optional/extra payment ledger, selected counter/Card UI, and exact lifecycle boundaries | Authoring resource and explicit-payoff loops |
| `reference/ordered-card-buffer.md` | Ordered buffer: `AttachedState<PlayerCombatState,TState>`, native source-card Discard, visible order, non-destructive overflow, deterministic output/`CardGeneratedEntry`, and combat reset; retained-card `CustomPile` remains unsupported | Authoring an ordered card-play record and dynamic output |
| `reference/card-computed-values.md` | Computed Card value roles, one-formula preview/execution parity, upgrade/timing/domain rules, Energy/Star formatters, typed Power amount-given behavior, variable tooltips, and focused proof | Authoring a Card with calculated text/effects or DynamicVar tooltips |
| `reference/card-hand-emphasis.md` | Conditional Card hand emphasis: ordered fixed-color rules, priority/ties, native gold/red versus typed outline lowering, unplayable visibility, refresh boundary, and headed proof | Authoring a Card with hand emphasis |
| `reference/extra-corner-labels.md` | Bounded extra badges: Relic up to three safe corners, Power one top-left label, text/rich-text limits, specs providers, invalidation/removal, cleanup, and headed proof | Authoring supplemental values on a Relic or Power |
| `reference/advanced-targeting.md` | RitsuLib custom live-Creature targets: stable Mod-local registration, single Card/Potion and multi Card resolution, revalidation/payment lifecycle, multi-Potion limitation, and headed selection proof | Authoring a filtered Card/Potion target |
| `reference/rest-site-options.md` | Card- or Relic-owned native Rest Site option: exact owner/state handle, singleplayer contribution, free/fixed Gold, final recheck, run/site repeatability, stay/leave, and checked icon fallback | Authoring an owned Rest Site action on a Card or Relic |
| `reference/card-piles.md` | Complete Custom Card Piles Package: combat/run lifetime; headless/top-bar/bottom-corner/ExtraHand UI; preset/custom anchors; open/view/visibility/hotkeys; native movement; localization; ExtraHand layout, play, and callbacks | Authoring one or more Mod-owned Card piles |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/stateful-mechanics.md` | Bounded state schemas with exact owner/listener transitions, lifetime/reset/persistence, visibility, consumers/outputs, and selected proof derivation | Any effect that remembers progress, limits uses, or compares turns |
| `reference/build-constraints.md` | Current pinned RitsuLib build/load, registration, localization, packaging, and runtime-variant constraints | Before writing resolved localization/registration output; on a build diagnostic |
| `reference/selftest-harness.md` | The tier-2 self-test harness: arg-gated menu→run navigation plus hosted scenario drivers (`CombatPlayer`, `CombatEnemy`, `MapNode`, Character Foundation `RunStart`), independent post-state assertions, structured state-proof markers, and multi-element observations. Public Cmds/UI only — `ProcessCommand(string)` is unreachable | Authoring the tier-2 harness (author.md step 2.5); any tier-2 automation question |
| `reference/art-contract.md` | Custom-sprite contract: exact paths/sizes for the eight established static families and nine promoted Character profiles; per-consumer file counts; checked fallbacks; animation boundaries; source-grounded prompts; source-independent import | The art sub-step (author.md §4); any custom-sprite path/size/style question |
| `reference/art-samples/` | Type-matched real STS2 reference pools for card/relic/power/potion/enchantment/orb/monster/event (© Mega Crit, reference-only — see ATTRIBUTION.md); tools select the matching family and randomly sample three distinct images | Passed as the root `--reference` in the art step; never mix families |
| `grounding.md` | Where facts come from (official semantics→Package purpose, content→spire-codex, C# signatures→pinned source, implementation/proof→open-mod) + the runtime-vs-maintainer split: at runtime you read only the pack; a genuine recipe miss is reported, not researched live | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

*Editing existing* vanilla content starts at `reference/vanilla-overrides.md`, not a new-
content recipe. Existing Cards use the promoted public route in
`reference/vanilla-card-overrides.md` and may reuse a grounded effect recipe only for its
semantic lowering. Existing Ancient option/page behavior uses the promoted bounded route in
`reference/vanilla-ancient-overrides.md`; its visuals remain separate visual-override operations.
Existing non-Card data/behavior uses
`reference/vanilla-non-card-overrides.md`. Do not infer that every edit needs Harmony, and
do not author an operation outside a listed catalog package.

## Key rules to remember (recite these when relevant)

- **Adapter first:** resolve `reference/ritsulib-adapter.md` from the semantic SPEC before
  reading a recipe. Registration, template bases, concrete ids, localization keys, and
  asset paths are adapter output; do not place them in the semantic contract.
- **Support rule:** a documented Package with public members in the pinned profile is
  supported. A missing recipe or unrun check does not make it unsupported; report the exact
  authoring or verification gap.
- **Custom Card Piles:** route the complete documented Package through
  `reference/card-piles.md`; preserve exact Card identity and awaited movement, and let the
  generated SPEC select any public scope/style/anchor/view/ExtraHand consumer.
- **Monster/Encounter graph:** declare separate registered nodes and explicit roster edges,
  every visible move, ordered successor, exhaustive conditional or requested weighted-random
  branch, hit count, and downstream state consequence. Keep one checked 360x360 body per
  Monster for combat and bestiary with the explicit built-in fallback; animation and
  phobia variants remain later work.
- **Event/World Node:** preserve real page/option UI, blocking overlay completion,
  resume-vs-map choice, one special combat per mutable Event, and the bounded portrait,
  rich-text, native presentation, and cleanup profiles. Direct merchant/rest/treasure
  transitions, custom layouts, arbitrary VFX, and speech bubbles remain unsupported for new
  normal Events. Exact existing Ancient visuals/options route through the separate
  `reference/vanilla-visual-overrides.md` and `reference/vanilla-ancient-overrides.md`; do not
  treat those override routes as new Ancient authoring.
- **Forced Event follow-up:** use only a finite prioritized list of token/act-set/custom-
  Event sequences with exact saved progress, terminal consumption, pool exclusion, neutral
  returns, and fail-closed conflicts. Do not generalize it to arbitrary graphs, vanilla
  edits, multiplayer, or save-roundtrip claims.
- **Character Foundation:** the adapter owns exactly-once registration, character-scoped
  pools, exact starters, localization, and the real selection/run proof. Static consumers
  remain separate profiles: selection `132x195`, background `1920x1200`, top icon main and
  outline `88x88`, static bodies `512x512`, five energy layers `256x256`, and distinct
  256x256 large/24x24 rich-text Energy icons. The bounded pool-frame/color theme and
  deterministic top-icon/generated-Relic outlines are implemented. Locked
  selection and map marker still need separate headed evidence. Character-specific native
  Ancient/Architect dialogue is supported only through the dedicated localization contract.
- **Character combat cues:** support exactly the private combat-only Idle/Attack/Hit/Dead
  contract. Require all eighteen 512x512 frames, one shared style/geometry, one-shot return
  and terminal behavior, cleanup, and all-or-nothing static fallback. Never publish the set
  through `CharacterAssetProfile.VisualCues`; Cast, Spine, trails, audio, and animated world
  hosts remain unsupported.
- **Capability kernel:** prefer the game or RitsuLib public API. A missing public seam may
  use one selected, version/fingerprint-gated adapter with zero-target/failure markers,
  conflict policy, fallback, and a hosted proof. Do not invent C/D targets or a shared
  runtime binary.
- **Character resource:** combat-owned integer state is nonnegative; check affordability
  before RitsuLib's all-or-nothing spend, use public `RegisterCombatUi`, refresh the fixed
  icon+text counter, retain the text-only fallback, keep its offset disjoint from native
  Energy, and prove a distinct zero state in combat 2. This does not replace Energy.
- **Ordered combat buffer:** record semantic values in combat state, send source cards
  through their normal result pile, use `AttachedState<PlayerCombatState,TState>`, expose
  order through grounded UI, enforce capacity before mutation, and create one deterministic
  output. Retained-card custom zones remain unsupported.
- **Localization keys:** derive concrete keys once in the adapter, keep them flat where the
  selected host requires flat tables, and record the result in `MEMORY.md`; never infer a
  framework prefix from a class or namespace inside SPEC.
- **Relic combat-start energy:** trigger after the combat turn-start reset and guard the
  first owner turn. A pre-combat energy grant is not equivalent because the reset erases it.
- **Counter lifetime is semantic:** run-persistent progress uses the selected run-save
  route; "on turn N of each combat" reads the native combat turn; never duplicate that
  counter or silently shorten a run lifetime.
- **Potions and cards:** model potion use as a use/target effect and card play as a play
  effect. Self, one-enemy, all-enemy, and advanced filtered targets stay semantic until
  adapter lowering. Advanced targets route only through `reference/advanced-targeting.md`;
  the pinned profile supports Card one/many and Potion one, while `potion + many` stops
  authoring. Scaling values and upgrade deltas are data, not literals in the SPEC.
- **Content rich text is per surface:** Card descriptions author only `gold`/`purple`
  (SmartFormat may emit `green`/`red`); relic descriptions allow
  `blue`/`gold`/`green`/`purple`/`red`; potion descriptions allow
  `blue`/`gold`/`green`; power descriptions allow `blue`/`gold`. Titles stay plain.
- **Counter Power amounts need a SPEC domain** (nonnegative by default). Consumption must
  clamp to the existing amount and never create a missing instance with a negative value.
- **Never use process-local random state** for in-game RNG; use the game's seeded random
  source through the selected adapter.
- **Don't guess an API** — if the recipe lacks it, check the rest of the pack (`reference/mechanics.md`, `reference/build-constraints.md`, snapshots, `errors.md`) per `grounding.md`. If it's genuinely not in the pack, report a pack gap rather than digging or guessing.
