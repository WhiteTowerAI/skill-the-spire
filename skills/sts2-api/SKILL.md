---
name: sts2-api
display_name: STS2 API Lookup
short_description: On-demand STS2 modding knowledge (recipes, commands, errors)
description: |
  Query the STS2 game pack for concrete modding knowledge: element recipes,
  command APIs, localization rules, error fixes. Use when the main pipeline
  needs a specific answer (hook signature, Cmd name, loc-key rule) rather than
  loading the whole pack into context.
allow_implicit_invocation: false
context: fork
model: sonnet
agent: Explore
---

# STS2 API Lookup

This skill is a narrow reference tool. Answer only what the caller asked — do
not dump entire files into the response.

## How to answer

1. Check `./recipes/` for the element or mechanic type (relic, potion,
   card, power, keyword, enchantment, orb, monster+encounter, event, character). For a **fought enemy** read
   `recipes/monster.md` — it covers the monster AND its encounter as one vertical slice.
   For a **World Node/event** read `recipes/event.md` — it covers registration, nested
   `EventLoc`, the fast-path consequence, checked portraits, and the `MapNode` proof. Also
   read `./reference/event-outcomes.md` when options use selections,
   custom rewards, conditional pages, or special combat. Read
   `./reference/event-vfx.md` only when SPEC selects the bounded
   normal-layout `portrait_halo` profile. Read
   `./reference/event-text-effects.md` when Event page/option
   descriptions use the bounded vanilla rich-text vocabulary. Read
   `./reference/event-option-presentation.md` when enabled Event
   options use typed Hover Tips, relic-backed presentation, or exact HP/Max HP costs.
   For a **playable character Foundation** read `recipes/character.md` — it covers the
   character template, constructor auto-registration, three pools, starters, two-table
   localization, placeholder shell, and `RunStart` + `CombatPlayer` proof.
   For a combat-lifetime **character resource with explicit payment and a live counter**,
   read `./reference/character-resource.md`. For a **bounded ordered
   semantic card-play buffer with deterministic dynamic output**, read
   `./reference/ordered-card-buffer.md`. Both are pipeline-supported
   through the live 6e Wayfinder composition acceptance.
   For a **grounded advanced capability that needs a non-public host seam**, read
   `./reference/capability-kernel.md` after the public/BaseLib check.
   It covers self-contained typed state/hooks/UI descriptors and the one verified B-risk
   combat-UI postfix. Resource UI may select that exact adapter through its own page; it
   is not permission to invent other patch targets, C/D patches, or `OpenMod.Runtime`.
   Cards/powers/keywords/enchantments/orbs also read
   `./reference/mechanics.md` first (scaling numbers, SmartFormat
   descriptions, shared enums). When Card/relic/potion/power descriptions select bounded
   vanilla colors, also read `./reference/content-text-effects.md`.
   For any effect that remembers progress (every N events, once per combat, previous
   turn, limited run uses), read `./reference/stateful-mechanics.md`.
2. For error signatures → fix, read `./errors.md`.
3. For content facts (what effects exist, a vanilla analog, realistic numbers) or a
   symbol the recipe lacks, read `./grounding.md` and, for
   potions, `./reference/potions-snapshot.md`.
4. For the **tier-2 self-test harness** (`SelfTest.cs`, the automated effect check), read
   `./reference/selftest-harness.md`.
5. For **custom art** (a card portrait's path + size, the prompt template, host-native
   `image_gen` routing when callable, and `gen_sprite.py` usage), read
   `./reference/art-contract.md`.
6. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

**Never read all files at once.** Each file is loaded on demand.

## Files in this pack

| File | Content | When to read |
|------|---------|--------------|
| `recipes/relic.md` | Full known-good relic pattern (skeleton, hooks, energy Cmds, RNG, loc-key derivation, checklist, golden example) | Authoring a relic |
| `recipes/potion.md` | Full known-good potion pattern (OnUse trigger, Rarity/Usage/TargetType, effect Cmds, loc table `potions`, checklist, worked examples) | Authoring a potion |
| `recipes/card.md` | Full known-good card pattern (OnPlay, CardType/rarity/target, DamageCmd fluent builder + GainBlock + PowerCmd.Apply, DynamicVars/upgrade, loc table `cards`, `card <id>` console cmd, worked examples) | Authoring a card |
| `recipes/power.md` | Full known-good custom-power pattern (Type/StackType, amount domains, trigger hooks, `PowerCmd.Apply` gain + guarded `ModifyAmount` consumption, loc table `powers`) — usually a dependency of a card/relic | Authoring or consuming a custom buff/debuff |
| `recipes/keyword.md` | Custom `CardKeyword` pattern (`[CustomEnum]`, optional `[KeywordProperties]`, `card_keywords` loc, host attachment, behavior-vs-display boundary, live card-text + no-icon tooltip presentation, Type+Scenario proof); no bitmap spec | Authoring shared card-mechanic vocabulary |
| `recipes/enchantment.md` | Custom Card Enchantment pattern (`CustomEnchantmentModel`, `CardCmd.Enchant`, CardModifierLoc/extraCardText, host restrictions, attachment + altered behavior, one checked 64×64 icon shared by card tab + tooltip); distinct from run `CustomModifierModel` | Authoring a persistent modifier attached to a Card |
| `recipes/orb.md` | Custom Orb pattern (`CustomOrbModel`, OrbLoc, Channel/Passive/Evoke, owner/slot behavior, one checked 100×100 icon shared by smart tooltip + trigger flash, explicit vanilla Spine scene/channel-SFX fallbacks, separate custom-scene boundary) | Authoring an orb plus its Card/relic/power host |
| `recipes/monster.md` | Custom Monster + Encounter as one vertical slice: registration/loc, checked 360×360 static body shared by combat+bestiary, explicit scene fallback, grounded move vocabulary for self buff/custom Power, target debuff, block/heal, multi-hit, composite moves, explicit cycles, and conditional branches; animation deferred; multi-turn `CombatEnemy` proof; **monster attacks use `.FromMonster(this).Execute(null)`, never `.Targeting()`** | Authoring a fought enemy or its move cycle |
| `recipes/event.md` | Custom Event / World Node pattern (`CustomEventModel` auto-`AddEvent`, all-act vs act-scoped placement, nested `EventLoc` pages/options, bounded description rich text, `Option(Method)` slug contract, Cmd consequence + `SetEventFinished`, checked initial/page portraits, `MapNode` UI-click proof) | Authoring a map event with at least one consequential option |
| `recipes/character.md` | Character Foundation (`alchyrsts2charmod`, `PlaceholderCharacterModel`, constructor auto-`AddCharacter`, card/relic/potion pools, starter deck/relic, exact character+Architect loc, placeholder visuals, `RunStart` + `CombatPlayer` proof) | Authoring a minimal playable custom character shell |
| `reference/event-outcomes.md` | Full normal-Event outcome vocabulary: immediate Cmd combinations, multi-page/locked options, blocking card selections, custom rewards, resumable/terminal special combat, extra combat rewards, one-combat-per-instance boundary, and unsupported room transitions | Authoring an Event beyond the one-Cmd fast path |
| `reference/event-vfx.md` | Bounded code-native normal-layout `portrait_halo`: page parameters, Fast Mode behavior, `OnRoomEnter`/portrait host, explicit named-node cleanup, and headed acceptance contract | Authoring the supported Event portrait VFX profile |
| `reference/event-text-effects.md` | Bounded normal-Event rich text: vanilla-observed color/emphasis/`jitter`/`sine` tags, safe nesting, native host lifecycle, headed proof, completed native-presentation items 1-3, remaining items 4-6, and the speech-bubble future boundary | Authoring styled Event text or preserving adjacent presentation gaps |
| `reference/content-text-effects.md` | Per-surface vanilla rich-text allowlists for Card bodies/Card previews and standard relic/potion/power Hover Tips; SmartFormat and auto-keyword composition; headed proof contract | Authoring styled Card/relic/potion/power descriptions |
| `reference/event-option-presentation.md` | Enabled Event option typed Hover Tips, normal `RelicOption<T>` text/metadata plus its Ancient-only image blocker, and native exact-lethal HP/Max HP warning glow | Authoring those normal-layout Event option presentation contracts |
| `reference/character-resource.md` | 6d combat resource contract: `PlayerCombatState` ownership, nonnegative gain/affordability/all-or-nothing spend, second-combat reset, card-hosted payoff, generic live Label, and selection of the exact 6c combat-UI adapter | Authoring a character resource and explicit-payoff loop |
| `reference/ordered-card-buffer.md` | Ordered combat-buffer contract: `PlayerCombatState` semantic values, native source-card Discard, visible state text, bounded order/overflow, deterministic per-instance output, `CardGeneratedEntry`, and combat reset; retained-card `CustomPile` gameplay is explicitly unsupported | Authoring an ordered card-play record and dynamic output |
| `reference/capability-kernel.md` | Character Systems 6c boundary: semantic combat-scoped state, deterministic typed hooks, descriptor-based fallback UI, version/MVID-gated patch registry with zero-target/failure/owned/foreign diagnostics, and the scenario-verified B-risk `NCombatUi.Activate(CombatState)` postfix. Self-contained only; no `OpenMod.Runtime`, unverified patch target, Publicizer, or transpiler support | Maintaining or emitting a specifically grounded advanced capability after public/BaseLib cannot expose its host seam |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/stateful-mechanics.md` | Stateful-effect contract: event/threshold/phase/lifetime/reset/persistence; turn/combat/run counter patterns; Happy Flower `[SavedProperty]` vs Stone Calendar `TurnNumber`; UI counter and Tier-2 boundary/save proofs | Any effect that remembers progress, limits uses, or compares turns |
| `reference/build-constraints.md` | What the toolchain refuses to BUILD/LOAD: full analyzer diagnostic set STS001–004 + the exact required-loc-key table per model type (cards/potions/relics/powers/…) + `[Pool]` rule | Before writing any element's loc keys + attributes; on any STS0NN build error |
| `reference/selftest-harness.md` | The tier-2 self-test harness: arg-gated menu→run navigation plus hosted scenario drivers (`CombatPlayer`, `CombatEnemy`, `MapNode`, Character Foundation `RunStart`), independent post-state assertions, structured state-proof markers, and multi-element observations. Public Cmds/UI only — `ProcessCommand(string)` is unreachable | Authoring the tier-2 harness (author.md step 2.5); any tier-2 automation question |
| `reference/art-contract.md` | Custom-sprite contract: exact `res://` path + pixel size/profile for card `1000×760`, relic/power/potion `256×256`, enchantment `64×64`, orb icon `100×100`, static monster body `360×360`, and normal-event portrait slots `3440×1613` (all verified live loose PNGs); per-consumer file counts; checked fallbacks; animation boundaries; card/icon/monster/event prompts; source-independent import | The art sub-step (author.md §4); any custom-sprite path/size/style question |
| `reference/art-samples/` | Type-matched real STS2 reference pools for card/relic/power/potion/enchantment/orb/monster/event (© Mega Crit, reference-only — see ATTRIBUTION.md); tools select the matching family and randomly sample three distinct images | Passed as the root `--reference` in the art step; never mix families |
| `grounding.md` | Where facts come from (three sources: content→spire-codex, C# signatures→decompile, build/load→validators) + the runtime-vs-maintainer split: at runtime you read only the pack; a genuine miss is a pack gap to report, not a dig | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

*Editing existing* vanilla content (relics/cards/potions) is not a recipe — it needs
Harmony patching and is deferred. The recipes make **new** elements.

## Key rules to remember (recite these when relevant)

- **`[Pool]` is required** on every `CustomRelicModel` / `CustomPotionModel` / `CustomCardModel` subclass or BaseLib throws at registration. (Exceptions with **NO `[Pool]`**, auto-registered in their constructor: **power** `CustomPowerModel`, **orb** `CustomOrbModel`, **monster** `CustomMonsterModel`, **encounter** `CustomEncounterModel`, **event** `CustomEventModel`.)
- **Monster + encounter are one slice.** `CustomMonsterModel` auto-registers via `RegisterType`; `CustomEncounterModel(RoomType.Monster)` auto-`AddEncounter` in its constructor (no manual register). Declare each move's intents/effects/successor; explicit `FollowUpState` cycles and exhaustive `ConditionalBranchState` predicates own sequencing. Multi-hit pairs `MultiAttackIntent(N, R)` with `.WithHitCount(R)`. A **monster attack uses `.FromMonster(this).Execute(null)` — NEVER `.Targeting()`** (that's the card pattern and it hangs the enemy turn). Static art is one checked 360×360 PNG through `CreateCustomVisuals()` and `NodeFactory<NCreatureVisuals>`, while `CustomVisualPath` remains the scene fallback; animation is later. Loc: `monsters.<ID>.name`, `encounters.<ID>.title`+`.loss`. See `recipes/monster.md`.
- **Event/World Node:** `CustomEventModel` auto-`AddEvent`s (no `[Pool]`); default empty
  `Acts` makes it available to every act. Prefer nested in-code `EventLoc`; the option
  method name slug must match its `EventOptionLoc` key. Prove it through `MapNode` by
  entering `ModelDb.Event<T>()`, driving every independent SPEC outcome through real UI,
  and asserting exact state/page/room results. Selection and reward overlays must finish
  before Event state changes. Special combat requires `IsShared`, chooses resume-vs-map
  explicitly, and is limited to one combat per mutable Event instance. Every selected
  normal initial/page portrait is one opaque
  3440×1613 PNG. `CustomInitialPortraitPath` must check the mod path and fall back to
  `this_or_that.png`; missing page art retains the current portrait. Normal-layout Event
  VFX supports only the code-native `portrait_halo` profile with explicit named-node
  cleanup. Page and option descriptions may use only the bounded vanilla rich-text tags
  from `reference/event-text-effects.md`; titles stay plain. Custom phobia art, arbitrary
  VFX, custom/Ancient layouts, and direct merchant/rest/treasure room transitions remain
  unsupported.
- **Character Foundation:** scaffold with `alchyrsts2charmod`; inherit
  `PlaceholderCharacterModel`; its `CustomCharacterModel` constructor already calls
  `AddCharacter(this)`, so never call it manually. Supply all three custom pool models,
  exact starter deck/relic, 14 `CharacterLoc` values plus four Architect keys, then prove
  the real selection button and run state through `RunStart` + `CombatPlayer`.
- **Capability kernel:** it is not a gameplay recipe. Prefer public/BaseLib; otherwise use
  only a pack-grounded adapter with exact version/MVID/signature, one owned patch,
  zero-target/failure markers, conflict policy, and a hosted state proof. The only verified
  non-public seam is the B-risk `NCombatUi.Activate(CombatState)` postfix, now selected by
  the scenario-verified character-resource UI contract. Keep it inside the generated mod;
  a maintainer canary is not the second generated consumer required for `OpenMod.Runtime`.
- **Character resource:** combat-owned integer state is nonnegative; check affordability
  before an all-or-nothing spend, refresh the generic counter after every change, and prove
  a distinct zero state in combat 2. This does not authorize alternative-energy patches.
- **Ordered combat buffer:** record semantic values in combat-scoped state and let every
  source card use its native result pile; expose current order through grounded UI, enforce
  capacity before mutation, and add the configured output through
  `AddGeneratedCardToCombat`. Retained-card `CustomPile`, persistence, and custom zone UI
  remain unsupported.
- **Loc-key derivation** (same for relics, potions, cards, powers): `Id.Entry = "<NS_UPPER>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split + UPPER_SNAKE). Keys are **flat strings**, not nested JSON. Table is `relics` / `potions` / `cards` / `powers` per type.
- **Relic combat-start energy**: use `AfterSideTurnStart` + `TurnNumber <= 1` guard. `BeforeCombatStart()` is wrong — energy reset wipes it.
- **Counter lifetime is a design decision:** "every N turns" defaults to run-persistent
  Happy Flower semantics (`[SavedProperty]`); "on turn N of each combat" reads
  `PlayerCombatState.TurnNumber`. Never use a plain field for state that must survive
  save/resume, and never duplicate the combat turn counter.
- **Potions fire in `OnUse`** (they're actively used) — no combat hook. Self-buff potions target `AnyPlayer`, not `Self`. Damage/block use `ValueProp.Unpowered`.
- **Cards fire in `OnPlay`**; a card targeting the player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions). Numbers come from `DynamicVars` (scaling), not literals; attacks use the `DamageCmd.Attack(...)` fluent builder. Loc table `cards`, no separate upgrade key (SmartFormat `:diff()` handles it).
- **Content rich text is per surface:** Card descriptions author only `gold`/`purple`
  (SmartFormat may emit `green`/`red`); relic descriptions allow
  `blue`/`gold`/`green`/`purple`/`red`; potion descriptions allow
  `blue`/`gold`/`green`; power descriptions allow `blue`/`gold`. Titles stay plain.
- **Counter Power amounts need a SPEC domain** (nonnegative by default). To consume a
  nonnegative Counter, find its existing instance, clamp the spend, and call
  `PowerCmd.ModifyAmount`; never consume with a negative `PowerCmd.Apply<T>` because a
  missing instance would be created negative.
- **Never `System.Random`** for in-game RNG — use `MegaCrit.Sts2.Core.Random.Rng`.
- **Don't guess an API** — if the recipe lacks it, check the rest of the pack (`reference/mechanics.md`, `reference/build-constraints.md`, snapshots, `errors.md`) per `grounding.md`. If it's genuinely not in the pack, report a pack gap rather than digging or guessing.
