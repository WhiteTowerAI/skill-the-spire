---
name: sts2api
description: |
  Query the STS2 game pack for concrete modding knowledge: element recipes,
  command APIs, localization rules, error fixes. Use when the main pipeline
  needs a specific answer (hook signature, Cmd name, loc-key rule) rather than
  loading the whole pack into context.
---

# STS2 API Lookup

## Design grammar and planning routing

After `../modmaker/route.md` classifies the request, load only the design references named in
its handoff:

- read `../sts2api/design/character-foundation.md` for a playable Character,
  its Foundation, or a Character/content-set design, before creative questions or a
  starter-deck proposal; load it only for that Character surface;
- read `../sts2api/design/mechanic-planning.md` when a mechanic, resource,
  stateful loop, risk/reward structure, or interacting system lacks an exact core
  decision;
- read `../sts2api/design/content-set-planning.md` for a Character card pool,
  archetype, multi-element set, or another content ecosystem; and
- read `../sts2api/design/balance-planning.md` when balance, numeric resource
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
read `../modmaker/semantic-contract.md` before selecting an implementation.
Lazily read `reference/ritsulib-adapter.md` next. It
maps each semantic surface to one public
registration/template and asset profile, and owns the framework/version diagnostic
record. Only then load the surface recipe or reference needed for the request.

Official tutorial semantics plus public members in the pinned profile make all documented
consumers in that feature family supported. A missing shipped recipe means only that no
maintained route exists; ground a Mod-local route under `grounding.md` § Mod-local Routes and
never guess a symbol.

RitsuLib is the only active adapter. Do not add BaseLib or another framework dependency, copy another
scaffold, or infer a runtime dependency from a recipe name.

When the request edits an existing vanilla model, read
`../sts2api/reference/vanilla-overrides.md` before any new-content recipe. Its
grounding kernel resolves the pinned target, then routes to the Card, visual, Ancient,
availability, or non-Card override reference listed in the table below. Never derive a patch body
from the prompt or silently convert the request into new content.

An override changes only what the request names. A changed number or behavior keeps the
model's name and its other surfaces vanilla, and rewrites the rules text only as far as the
change requires: `card.vars.base` for a number the text already shows, and
`card.description.localization` (or the Relic/Potion equivalent) for new behavior. Never add
a title change unless the request asks for a new name.

## How to answer

1. Find the element's recipe under `../sts2api/recipes/`, then read only the
   references it and the table below name for the selected behavior.
2. For error signatures, read `../sts2api/errors.md`.
3. For a vanilla analog or realistic numbers, resolve the element with
   `python ../modmaker/scripts/vanilla_overrides.py resolve <name> --category <card|relic|potion|power>`
   and read its values and rules text. For a symbol the recipe lacks, read
   `../sts2api/grounding.md`. For an exact public signature, run
   `python ../modmaker/scripts/api.py search <Type> [<member>]` or `api.py find <member>`. If
   the pack has no maintained route, follow `grounding.md` § Mod-local Routes rather than
   guessing.
4. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

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
| `recipes/relic.md` | Relic trigger/effect/state behavior, hidden inventory presence, localization fields, fallback, and proof obligations | Authoring a relic after adapter selection |
| `recipes/potion.md` | Potion usage/target/effect behavior, localization fields, fallback, and proof obligations | Authoring a potion after adapter selection |
| `recipes/card.md` | Card play/target/scaling/upgrade behavior, custom Card tags, localization fields, fallback, and proof obligations | Authoring a card after adapter selection |
| `recipes/power.md` | Power stack domains, trigger behavior, safe mutation, display fields, and proof obligations | Authoring or consuming a custom buff/debuff after adapter selection |
| `recipes/keyword.md` | Keyword behavior-vs-display boundary, host attachment, text-only fallback, and proof | Authoring shared card-mechanic vocabulary after adapter selection |
| `recipes/enchantment.md` | Enchantment host restrictions, persistent change, 64x64 icon consumers/fallback, and proof | Authoring a persistent Card modification after adapter selection |
| `recipes/orb.md` | Orb channel/passive/evoke behavior, 100x100 icon consumers, explicit body/SFX fallbacks, and proof | Authoring an orb plus its host after adapter selection |
| `recipes/monster.md` | Separate Monster/Encounter nodes, explicit rosters, HP ranges, deterministic/conditional/weighted-random moves, static combat+bestiary body, fallback, and selected `CombatEnemy` checks | Authoring a fought enemy graph after adapter selection |
| `recipes/event.md` | Event / World Node pages/options, outcomes, checked portraits, and `MapNode` proof | Authoring a map event after adapter selection |
| `recipes/character.md` | Character Foundation pools, starters, Dusty Tome and Orobas starter upgrades, localization, selection/run behavior, fallbacks, and proof | Authoring a playable character shell after adapter selection |
| `recipes/act.md` | Complete Act model, required content pools/assets, explicit singleplayer force/uniform/weighted entry, and transition proof | Authoring a playable chapter |
| `recipes/ancient.md` | New Shared/Act-scoped Ancient identity, options, localization dialogue, presentation, and native-room proof | Authoring a new Ancient rather than editing a vanilla one |
| `recipes/reward.md` | Mod-owned Reward type, native claim/refusal, typed save reconstruction, offer/combat insertion, linked sets, and proof | Authoring a custom pending reward-screen option |
| `recipes/card-pile.md` | Independent Card Pile owner and route into the complete documented API | Authoring one or more Mod-owned Card piles |
| `recipes/affliction.md` | Combat Card Affliction validity, stack/application/play/removal lifecycle, text/tips/overlay, and proof | Authoring a new Affliction and its application source |
| `recipes/modifier.md` | Good/bad run Modifier registration, ordering/exclusivity, new/load lifecycle, text/icon, and proof | Authoring a daily/custom-run Modifier |
| `recipes/global-effect.md` | Truthful Run/Combat singleton ownership, hook scope, scoped state, reset, and proof | Authoring a rule with no obtainable/selectable model owner |
| `recipes/rest-site.md` | Standalone/Card/Relic/Modifier owner selection for native Rest Site options | Authoring an independently requested Rest Site action |
| `recipes/runtime-ui.md` | One Mod-owned local UI workflow: top bar, Toast, runtime hotkeys, Capstone, floating window, Catalog, search expansion, fixed node attachment, shell tokens; lifetimes, focus, cleanup, and proof | Authoring a Runtime UI workflow |
| `reference/ancient-dialogue.md` | Pinned vanilla Ancient catalog, semantic visit groups, flat RitsuLib localization, structural validator, native priority, Architect attackers, and focused proof | Authoring or verifying custom-Character dialogue in native Ancient scenes |
| `reference/character-presentation.md` | RitsuLib Character profile/consumer matrix; nine live static profiles; no-editor raw-scene packing; five-layer energy scene; split card/text Energy icons; bounded theme; native Ancient/Architect proof boundary | Authoring or verifying Character static/native presentation |
| `reference/character-combat-cues.md` | Bounded non-Spine Idle/Attack/Hit/Dead cues from one anchored sheet, deterministic frame normalization, private combat cue wiring, shared geometry, all-or-nothing static fallback, and hosted proof | Authoring or verifying Character combat cues |
| `reference/event-outcomes.md` | Full normal-Event outcome vocabulary: immediate Cmd combinations, multi-page/locked options, blocking card selections, custom rewards, resumable/terminal special combat, extra combat rewards, one-combat-per-instance boundary, and unsupported room transitions | Authoring an Event beyond the one-Cmd fast path |
| `reference/event-vfx.md` | Bounded code-native normal-layout `portrait_halo`: page parameters, Fast Mode behavior, `OnRoomEnter`/portrait host, explicit named-node cleanup, and headed acceptance contract | Authoring the supported Event portrait VFX profile |
| `reference/vanilla-text-style.md` | Default vanilla text style for every surface: glossary-backed eng/zhs terms and highlight colors, per-surface number/line/tag rules, Simplified Chinese punctuation and measure words, hover tips for named terms, and the Build style check | Writing **any** player-facing text, on every surface |
| `reference/event-text-effects.md` | Extra, user-requested normal-Event atmosphere beyond the default style: vanilla-observed color/emphasis/`jitter`/`sine` tags, safe nesting, native host lifecycle, headed proof, completed native-presentation inventory, and the speech-bubble future boundary | Authoring requested atmospheric Event text or preserving adjacent presentation gaps |
| `reference/content-text-effects.md` | Extra, user-requested emphasis beyond the default style on Card bodies/Card previews and standard relic/potion/power Hover Tips; SmartFormat and auto-keyword composition; headed proof contract | A user asks for colored words the default style would not color |
| `reference/event-option-presentation.md` | Enabled Event option typed Hover Tips, normal `CreateModRelicOption<T>` text/metadata plus its Ancient-only image blocker, and native exact-lethal HP/Max HP warning glow | Authoring those normal-layout Event option presentation contracts |
| `reference/event-native-presentation.md` | Ordered native Card/relic acquisitions, allowlisted preference-respecting `weak_short`/`strong_normal` shake, and curated `trial_noble` Event VFX | Authoring native presentation items 4-6 for a normal Event |
| `reference/forced-followup-event.md` | Finite prioritized Quest Card -> act-set -> custom Event mappings/sequences, pool exclusion, saved progress, terminal consumption, and fail-closed conflicts | Authoring a bounded delayed/conditional Event follow-up |
| `reference/character-resource.md` | Multiple bounded RitsuLib secondary resources, combat/run policies, fixed/X and required/optional/extra payment ledger, selected counter/Card UI, and exact lifecycle boundaries | Authoring resource and explicit-payoff loops |
| `reference/ordered-card-buffer.md` | Ordered buffer: `AttachedState<PlayerCombatState,TState>`, native source-card Discard, visible order, non-destructive overflow, deterministic output/`CardGeneratedEntry`, and combat reset; retained-card `CustomPile` remains unsupported | Authoring an ordered card-play record and dynamic output |
| `reference/card-computed-values.md` | Computed Card value roles, one-formula preview/execution parity, upgrade/timing/domain rules, Energy/Star formatters, typed Power amount-given behavior, variable tooltips, and focused proof | Authoring a Card with calculated text/effects or DynamicVar tooltips |
| `reference/card-hand-emphasis.md` | Conditional Card hand emphasis: ordered fixed-color rules, priority/ties, native gold/red versus typed outline lowering, unplayable visibility, refresh boundary, and headed proof | Authoring a Card with hand emphasis |
| `reference/extra-corner-labels.md` | Bounded extra badges: Relic up to three safe corners, Power one top-left label, text/rich-text limits, specs providers, invalidation/removal, cleanup, and headed proof | Authoring supplemental values on a Relic or Power |
| `reference/advanced-targeting.md` | RitsuLib custom live-Creature targets: stable Mod-local registration, single Card/Potion and multi Card resolution, revalidation/payment lifecycle, multi-Potion limitation, and headed selection proof | Authoring a filtered Card/Potion target |
| `reference/model-right-click.md` | Right-click and controller-cancel actions on Mod Cards, Relics, Powers, Potions, and Orbs: hosts, model interfaces, synchronized execution, guards, boundary, and real-dispatch proof | Authoring an action the player triggers by right-clicking a Mod model |
| `reference/rest-site-options.md` | Standalone/Card/Relic/Modifier native Rest Site option: exact owner/state handle, singleplayer contribution, free/fixed Gold, final recheck, run/site repeatability, stay/leave, and checked icon fallback | Authoring any included Rest Site action |
| `reference/card-piles.md` | Complete Custom Card Piles API: combat/run lifetime; headless/top-bar/bottom-corner/ExtraHand UI; preset/custom anchors; open/view/visibility/hotkeys; native movement; localization; ExtraHand layout, play, and callbacks | Authoring one or more Mod-owned Card piles |
| `reference/model-capabilities.md` | Registered model-owned behavior/state bundles: typed owners, default/runtime attachment, merge/order, clone/save/display, bounded lifetime, and Card transform carry-over | Authoring separable behavior or state on a Card, Relic, Potion, Power, Orb, Enchantment, Affliction, Monster, or Character |
| `reference/lifecycle-state-rng.md` | Truthful lifecycle subscriptions, attached/model/run/player/profile state, persistence and migrations, deterministic host/Mod RNG, cleanup, and deferred-family boundaries | Authoring included behavior that crosses callback, combat, room, run, save, or profile boundaries or makes gameplay-random choices |
| `reference/shared-effect-hooks.md` | Owner-bound per-hit attack, healing, Energy/Stars gain, and maximum-hand-size effects with exact passes, guards, neutral results, and Global Effect boundary | Authoring those shared effects on a reachable model/capability or explicit Global Effect |
| `reference/card-play-lifecycle.md` | Before/after Card OnPlay, suppression, free-play durations, transform listeners/carry-over, type-text composition, phase order, cleanup, and real-host proof | Authoring behavior around Card play rather than only the Card's ordinary OnPlay body |
| `reference/effect-primitives.md` | Shared ordinary player-result lowering: exact commands, required context/owner/source/target, await order, result/rejection behavior, and lifecycle bounds; also in-combat Card choice, top-of-Draw-Pile placement, free-this-turn, and Stun | Authoring an ordered `effects.sequence` on a truthful executable surface |
| `reference/model-hook-participation.md` | Raw model-hook participation: the three declaration shapes, per-surface owner property, guard/neutral body, and the declared capability list the preflight reads | A SPEC `Hook:` line |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/stateful-mechanics.md` | Bounded state schemas with exact owner/listener transitions, lifetime/reset/persistence, visibility, consumers/outputs, and selected proof derivation | Any effect that remembers progress, limits uses, or compares turns |
| `reference/build-constraints.md` | Current pinned RitsuLib build/load, registration, localization, packaging, and runtime-variant constraints | Before writing resolved localization/registration output; on a build diagnostic |
| `reference/selftest-harness.md` | The tier-2 self-test kit: what the scaffold-generated `SelfTestKit.cs` does (roll call, navigation, shared combat and reset, real manual play, settling, face checks, `--only`, report), which content gets which check, the `SelfTestScenarios.cs` API, combat scenario recipes, and the `CombatEnemy`, `MapNode`, Ancient, Rest Site, and Character `RunStart` hosts through `plan.Custom`. Public Cmds/UI only — `ProcessCommand(string)` is unreachable | Writing Tier 2 scenarios (author.md step 2.5); any tier-2 automation question |
| `reference/art-contract.md` | Custom-sprite contract: exact paths/sizes for the eight established static families and nine promoted Character profiles; per-consumer file counts; checked fallbacks; animation boundaries; source-grounded prompts; source-independent import | The art sub-step (author.md §4); any custom-sprite path/size/style question |
| `reference/art-samples/` | Type-matched real STS2 reference pools for card/relic/power/potion/enchantment/orb/monster/event (© Mega Crit, reference-only — see ATTRIBUTION.md); tools select the matching family and randomly sample three distinct images | Passed as the root `--reference` in the art step; never mix families |
| `grounding.md` | Where facts come from, the runtime lookup order, and the Mod-local route procedure for an operation no maintained route covers: ground public signatures, implement with public APIs only, verify through Tier 2 | An answer the recipe lacks |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |
