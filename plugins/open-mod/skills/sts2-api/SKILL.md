---
name: sts2-api
description: |
  Query the STS2 game pack for concrete modding knowledge: element recipes,
  command APIs, localization rules, error fixes. Use when the main pipeline
  needs a specific answer (hook signature, Cmd name, loc-key rule) rather than
  loading the whole pack into context.
---

# STS2 API Lookup

This skill is a narrow reference tool. Answer only what the caller asked — do
not dump entire files into the response.

## Adapter routing

For generated content, the semantic contract is the product-level source of truth:
read `./semantic-contract.md` before selecting an implementation.
Lazily read `reference/ritsulib-adapter.md` next. It
pins RitsuLib `0.4.62` against STS2 `0.107.1`, maps each semantic surface to one public
registration/template and asset profile, and owns the framework/version diagnostic
record. Only then load the surface recipe or reference needed for the request.

RitsuLib is the only active adapter. Do not select a historical dependency, copy another
scaffold, or infer a runtime dependency from a recipe name.

## How to answer

1. Check `../sts2-api/recipes/` for the element or mechanic type (relic, potion,
   card, power, keyword, enchantment, orb, monster+encounter, event, character). For a **fought enemy** read
   `recipes/monster.md` — it covers the monster AND its encounter as one vertical slice.
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
   Read `../sts2-api/reference/forced-followup-event.md` when a custom Quest
   Card should force one custom Event in a specified act.
   For a **playable character Foundation** read `recipes/character.md` — it covers the
   RitsuLib typed template, one content-pack registration, three pools, starters, two-table
   localization, static profile/fallback, and `RunStart` + `CombatPlayer` proof.
   When Character SPEC selects static art, combat cues, richer resource/buffer UI, or native
   Ancient/Architect presentation, also read
   `../sts2-api/reference/character-presentation.md`. It separates the four
   live-proven loose-PNG consumers from scene-export and headed-Ancient blockers.
   For the bounded non-Spine `Idle`/`Attack`/`Hit`/`Dead` frame sequences, additionally
   read `../sts2-api/reference/character-combat-cues.md`; keep its cue set private
   to the combat state machine and preserve its all-or-nothing static fallback.
   For a combat-lifetime **character resource with explicit payment and a live counter**,
   read `../sts2-api/reference/character-resource.md`. For a **bounded ordered
   semantic card-play buffer with deterministic dynamic output**, read
   `../sts2-api/reference/ordered-card-buffer.md`. Both use the public RitsuLib
   Secondary Resource/node-attachment APIs and are pipeline-supported by the final
   Wayfinder composition. If a requested capability has no documented public game/RitsuLib
   seam, report a pack gap; do not invent a patch target or `OpenMod.Runtime`.
   Cards/powers/keywords/enchantments/orbs also read
   `../sts2-api/reference/mechanics.md` first (scaling numbers, SmartFormat
   descriptions, shared enums). When Card/relic/potion/power descriptions select bounded
   vanilla colors, also read `../sts2-api/reference/content-text-effects.md`.
   When a Card looks at the top X Draw cards and discards any number, also read
   `../sts2-api/reference/scry-helper.md`. It owns the singleplayer-only
   open-mod helper, native selector/discard lifecycle, structured result, and proof.
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
| `reference/ritsulib-adapter.md` | Pinned RitsuLib compat profile, public registration/template routing, asset profiles, lifecycle/persistence/resource routes, and diagnostics | After the semantic SPEC and before a surface recipe |
| `recipes/relic.md` | Relic trigger/effect/state behavior, localization fields, fallback, and proof obligations | Authoring a relic after adapter selection |
| `recipes/potion.md` | Potion usage/target/effect behavior, localization fields, fallback, and proof obligations | Authoring a potion after adapter selection |
| `recipes/card.md` | Card play/target/scaling/upgrade behavior, localization fields, fallback, and proof obligations | Authoring a card after adapter selection |
| `recipes/power.md` | Power stack domains, trigger behavior, safe mutation, display fields, and proof obligations | Authoring or consuming a custom buff/debuff after adapter selection |
| `recipes/keyword.md` | Keyword behavior-vs-display boundary, host attachment, text-only fallback, and proof | Authoring shared card-mechanic vocabulary after adapter selection |
| `recipes/enchantment.md` | Enchantment host restrictions, persistent change, 64x64 icon consumers/fallback, and proof | Authoring a persistent Card modification after adapter selection |
| `recipes/orb.md` | Orb channel/passive/evoke behavior, 100x100 icon consumers, explicit body/SFX fallbacks, and proof | Authoring an orb plus its host after adapter selection |
| `recipes/monster.md` | Monster + Encounter as one vertical slice: grounded moves, cycles/branches, static combat+bestiary body, fallback, and `CombatEnemy` proof | Authoring a fought enemy or its move cycle after adapter selection |
| `recipes/event.md` | Event / World Node pages/options, outcomes, checked portraits, and `MapNode` proof | Authoring a map event after adapter selection |
| `recipes/character.md` | Character Foundation pools, starters, localization, selection/run behavior, fallbacks, and proof | Authoring a playable character shell after adapter selection |
| `reference/character-presentation.md` | RitsuLib Character profile/consumer matrix; nine live static profiles; no-editor raw-scene packing; five-layer energy scene; split card/text Energy icons; bounded theme; native Ancient/Architect proof boundary | Authoring or verifying Character static/native presentation |
| `reference/character-combat-cues.md` | Bounded non-Spine Idle/Attack/Hit/Dead sheets, deterministic frame normalization, private combat cue wiring, shared geometry, all-or-nothing static fallback, and hosted proof | Authoring or verifying Character combat cues |
| `reference/event-outcomes.md` | Full normal-Event outcome vocabulary: immediate Cmd combinations, multi-page/locked options, blocking card selections, custom rewards, resumable/terminal special combat, extra combat rewards, one-combat-per-instance boundary, and unsupported room transitions | Authoring an Event beyond the one-Cmd fast path |
| `reference/event-vfx.md` | Bounded code-native normal-layout `portrait_halo`: page parameters, Fast Mode behavior, `OnRoomEnter`/portrait host, explicit named-node cleanup, and headed acceptance contract | Authoring the supported Event portrait VFX profile |
| `reference/event-text-effects.md` | Bounded normal-Event rich text: vanilla-observed color/emphasis/`jitter`/`sine` tags, safe nesting, native host lifecycle, headed proof, completed native-presentation inventory, and the speech-bubble future boundary | Authoring styled Event text or preserving adjacent presentation gaps |
| `reference/content-text-effects.md` | Per-surface vanilla rich-text allowlists for Card bodies/Card previews and standard relic/potion/power Hover Tips; SmartFormat and auto-keyword composition; headed proof contract | Authoring styled Card/relic/potion/power descriptions |
| `reference/event-option-presentation.md` | Enabled Event option typed Hover Tips, normal `CreateModRelicOption<T>` text/metadata plus its Ancient-only image blocker, and native exact-lethal HP/Max HP warning glow | Authoring those normal-layout Event option presentation contracts |
| `reference/event-native-presentation.md` | Native Card/relic acquisition presentation, the preference-respecting `weak_short` screen shake, and the curated built-in `trial_noble` Event VFX path/host/placement/pause/cleanup contract | Authoring native presentation items 4-6 for a normal Event |
| `reference/forced-followup-event.md` | Public-hook Quest Card -> forced custom Event contract: one act, Unknown room forcing, target pool exclusion, token completion/removal, and one-run MapNode proof | Authoring a bounded delayed/conditional Event follow-up |
| `reference/character-resource.md` | RitsuLib combat resource: `SecondaryResourceDefinition`/`SecondaryResourceCmd`, combat reset, all-or-nothing spend, public `RegisterCombatUi`, fixed 220x32 counter at offset 160, text fallback, and two-combat proof | Authoring a character resource and explicit-payoff loop |
| `reference/ordered-card-buffer.md` | Ordered buffer: `AttachedState<PlayerCombatState,TState>`, native source-card Discard, visible order, non-destructive overflow, deterministic output/`CardGeneratedEntry`, and combat reset; retained-card `CustomPile` remains unsupported | Authoring an ordered card-play record and dynamic output |
| `reference/scry-helper.md` | open-mod Scry helper: top-X native selector, structured result, normal Discard history/hooks, zero/empty/short/full boundaries, await proof, and explicit singleplayer restriction | Authoring a Card that looks at the top X Draw cards and discards any number |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/stateful-mechanics.md` | Stateful-effect contract: event/threshold/phase/lifetime/reset/persistence; run-save progress vs native combat turn; UI counter and Tier-2 boundary/save proofs | Any effect that remembers progress, limits uses, or compares turns |
| `reference/build-constraints.md` | Current pinned RitsuLib build/load, registration, localization, packaging, and runtime-variant constraints | Before writing resolved localization/registration output; on a build diagnostic |
| `reference/selftest-harness.md` | The tier-2 self-test harness: arg-gated menu→run navigation plus hosted scenario drivers (`CombatPlayer`, `CombatEnemy`, `MapNode`, Character Foundation `RunStart`), independent post-state assertions, structured state-proof markers, and multi-element observations. Public Cmds/UI only — `ProcessCommand(string)` is unreachable | Authoring the tier-2 harness (author.md step 2.5); any tier-2 automation question |
| `reference/art-contract.md` | Custom-sprite contract: exact paths/sizes for the eight established static families and nine promoted Character profiles; per-consumer file counts; checked fallbacks; animation boundaries; source-grounded prompts; source-independent import | The art sub-step (author.md §4); any custom-sprite path/size/style question |
| `reference/art-samples/` | Type-matched real STS2 reference pools for card/relic/power/potion/enchantment/orb/monster/event (© Mega Crit, reference-only — see ATTRIBUTION.md); tools select the matching family and randomly sample three distinct images | Passed as the root `--reference` in the art step; never mix families |
| `grounding.md` | Where facts come from (three sources: content→spire-codex, C# signatures→decompile, build/load→validators) + the runtime-vs-maintainer split: at runtime you read only the pack; a genuine miss is a pack gap to report, not a dig | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

*Editing existing* vanilla content (relics/cards/potions) is not a recipe — it needs
Harmony patching and is deferred. The recipes make **new** elements.

## Key rules to remember (recite these when relevant)

- **Adapter first:** resolve `reference/ritsulib-adapter.md` from the semantic SPEC before
  reading a recipe. Registration, template bases, concrete ids, localization keys, and
  asset paths are adapter output; do not place them in the semantic contract.
- **Scry helper:** use `OpenModScry.Execute` only for the bounded top-X/discard-any Card
  effect. Await the native selector and every pile/hook command, preserve seen order, and
  keep the result and hooks local to the generated Mod. Multiplayer/replay remains
  unsupported; do not silently fall back to local selection.
- **Monster + encounter are one slice.** Declare every visible move, ordered successor,
  exhaustive branch, hit count, and downstream state consequence. Keep one checked
  360x360 body for combat and bestiary with the explicit built-in fallback; animation and
  phobia variants remain later work.
- **Event/World Node:** preserve real page/option UI, blocking overlay completion,
  resume-vs-map choice, one special combat per mutable Event, and the bounded portrait,
  rich-text, native presentation, and cleanup profiles. Direct merchant/rest/treasure
  transitions, custom layouts, Ancient layouts, arbitrary VFX, and speech bubbles remain
  unsupported.
- **Forced Event follow-up:** one token, one target Event, one act, one Unknown MapPoint
  route, and one named completion option. Do not generalize it to arbitrary chains,
  vanilla edits, multiplayer, or save-roundtrip claims.
- **Character Foundation:** the adapter owns exactly-once registration, character-scoped
  pools, exact starters, localization, and the real selection/run proof. Static consumers
  remain separate profiles: selection `132x195`, background `1920x1200`, top icon main and
  outline `88x88`, static bodies `512x512`, five energy layers `256x256`, and distinct
  256x256 large/24x24 rich-text Energy icons. The bounded M6.5 pool-frame/color theme and
  deterministic top-icon/generated-Relic outlines are pipeline-supported. Locked
  selection, map marker, and native Ancient/Architect presentation need separate headed
  evidence.
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
  effect. Self, one-enemy, and all-enemy targets stay semantic until adapter lowering.
  Scaling values and upgrade deltas are data, not literals in the SPEC.
- **Content rich text is per surface:** Card descriptions author only `gold`/`purple`
  (SmartFormat may emit `green`/`red`); relic descriptions allow
  `blue`/`gold`/`green`/`purple`/`red`; potion descriptions allow
  `blue`/`gold`/`green`; power descriptions allow `blue`/`gold`. Titles stay plain.
- **Counter Power amounts need a SPEC domain** (nonnegative by default). Consumption must
  clamp to the existing amount and never create a missing instance with a negative value.
- **Never use process-local random state** for in-game RNG; use the game's seeded random
  source through the selected adapter.
- **Don't guess an API** — if the recipe lacks it, check the rest of the pack (`reference/mechanics.md`, `reference/build-constraints.md`, snapshots, `errors.md`) per `grounding.md`. If it's genuinely not in the pack, report a pack gap rather than digging or guessing.
