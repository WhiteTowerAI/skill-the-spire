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
   card, power, keyword, enchantment, orb, monster+encounter, event). For a **fought enemy** read
   `recipes/monster.md` — it covers the monster AND its encounter as one vertical slice.
   For a **World Node/event** read `recipes/event.md` — it covers registration, nested
   `EventLoc`, option consequences, provisional portrait fallback, and the `MapNode` proof.
   Cards/powers/keywords/enchantments/orbs also read
   `./reference/mechanics.md` first (scaling numbers, SmartFormat
   descriptions, shared enums).
   For any effect that remembers progress (every N events, once per combat, previous
   turn, limited run uses), read `./reference/stateful-mechanics.md`.
2. For error signatures → fix, read `./errors.md`.
3. For content facts (what effects exist, a vanilla analog, realistic numbers) or a
   symbol the recipe lacks, read `./grounding.md` and, for
   potions, `./reference/potions-snapshot.md`.
4. For the **tier-2 self-test harness** (`SelfTest.cs`, the automated effect check), read
   `./reference/selftest-harness.md`.
5. For **custom art** (a card portrait's path + size, the prompt template, the
   `gen_sprite.py` usage), read `./reference/art-contract.md`.
6. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

**Never read all files at once.** Each file is loaded on demand.

## Files in this pack

| File | Content | When to read |
|------|---------|--------------|
| `recipes/relic.md` | Full known-good relic pattern (skeleton, hooks, energy Cmds, RNG, loc-key derivation, checklist, golden example) | Authoring a relic |
| `recipes/potion.md` | Full known-good potion pattern (OnUse trigger, Rarity/Usage/TargetType, effect Cmds, loc table `potions`, checklist, worked examples) | Authoring a potion |
| `recipes/card.md` | Full known-good card pattern (OnPlay, CardType/rarity/target, DamageCmd fluent builder + GainBlock + PowerCmd.Apply, DynamicVars/upgrade, loc table `cards`, `card <id>` console cmd, worked examples) | Authoring a card |
| `recipes/power.md` | Full known-good custom-power pattern (Type/StackType, amount domains, trigger hooks, `PowerCmd.Apply` gain + guarded `ModifyAmount` consumption, loc table `powers`) — usually a dependency of a card/relic | Authoring or consuming a custom buff/debuff |
| `recipes/keyword.md` | Custom `CardKeyword` pattern (`[CustomEnum]`, optional `[KeywordProperties]`, `card_keywords` loc, host attachment, behavior-vs-display boundary, Type+Scenario proof) | Authoring shared card-mechanic vocabulary |
| `recipes/enchantment.md` | Custom Card Enchantment pattern (`CustomEnchantmentModel`, `CardCmd.Enchant`, CardModifierLoc/extraCardText, host restrictions, attachment + altered-behavior proof); explicitly distinct from run `CustomModifierModel` | Authoring a persistent modifier attached to a Card |
| `recipes/orb.md` | Custom Orb pattern (`CustomOrbModel`, OrbLoc, Channel/Passive/Evoke, owner/slot behavior, provisional icon+sprite seams, three-part Scenario proof) | Authoring an orb plus its Card/relic/power host |
| `recipes/monster.md` | Custom Monster + Encounter as one vertical slice (`CustomMonsterModel` no-`[Pool]` auto-register, `MoveState`/`MonsterMoveStateMachine`/`SingleAttackIntent`, `CustomEncounterModel(RoomType.Monster)` auto-`AddEncounter`, `AllPossibleMonsters`/`GenerateMonsters`/`IsValidForAct`, `monsters`+`encounters` loc, provisional Spine art, `CombatEnemy` proof); **monster attacks use `.FromMonster(this).Execute(null)`, never `.Targeting()`** | Authoring a fought enemy |
| `recipes/event.md` | Custom Event / World Node pattern (`CustomEventModel` auto-`AddEvent`, all-act vs act-scoped placement, nested `EventLoc` pages/options, `Option(Method)` slug contract, Cmd consequence + `SetEventFinished`, provisional vanilla portrait, `MapNode` UI-click proof) | Authoring a map event with at least one consequential option |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/stateful-mechanics.md` | Stateful-effect contract: event/threshold/phase/lifetime/reset/persistence; turn/combat/run counter patterns; Happy Flower `[SavedProperty]` vs Stone Calendar `TurnNumber`; UI counter and Tier-2 boundary/save proofs | Any effect that remembers progress, limits uses, or compares turns |
| `reference/build-constraints.md` | What the toolchain refuses to BUILD/LOAD: full analyzer diagnostic set STS001–004 + the exact required-loc-key table per model type (cards/potions/relics/powers/…) + `[Pool]` rule | Before writing any element's loc keys + attributes; on any STS0NN build error |
| `reference/selftest-harness.md` | The tier-2 self-test harness: arg-gated menu→run navigation plus hosted scenario drivers (`CombatPlayer`, `CombatEnemy`, `MapNode`), independent post-state assertions, structured state-proof markers, and multi-element observations. Public Cmds/UI only — `ProcessCommand(string)` is unreachable | Authoring the tier-2 harness (author.md step 2.5); any tier-2 automation question |
| `reference/art-contract.md` | Custom-sprite contract: exact `res://` path + pixel size per sprite type (card `1000×760`; relic/power/potion `256×256` — all four verified live, each a loose PNG; relic/power write a small + `big/` path, potion writes ONE file, card writes only `big/`; 606×852 full art is Ancient-only, out of scope) + the placeholder-fallback mechanism + the STS2 style descriptor + few-shot references + the prompt template (incl. potion's ~45° tilt) + `acquire_sprite.py` (Vofy managed credits) / `gen_sprite.py` (BYO HTTP + deterministic import) usage | The art sub-step (author.md §4); any custom-sprite path/size/style question |
| `reference/art-samples/` | 18 real STS2 card portraits (© Mega Crit, reference-only — see ATTRIBUTION.md) used as **few-shot style references** by `gen_sprite.py --reference` so a generated portrait matches the game look | Passed to `--reference` in the art step; not read directly |
| `grounding.md` | Where facts come from (three sources: content→spire-codex, C# signatures→decompile, build/load→validators) + the runtime-vs-maintainer split: at runtime you read only the pack; a genuine miss is a pack gap to report, not a dig | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

*Editing existing* vanilla content (relics/cards/potions) is not a recipe — it needs
Harmony patching and is deferred. The recipes make **new** elements.

## Key rules to remember (recite these when relevant)

- **`[Pool]` is required** on every `CustomRelicModel` / `CustomPotionModel` / `CustomCardModel` subclass or BaseLib throws at registration. (Exceptions with **NO `[Pool]`**, auto-registered in their constructor: **power** `CustomPowerModel`, **orb** `CustomOrbModel`, **monster** `CustomMonsterModel`, **encounter** `CustomEncounterModel`, **event** `CustomEventModel`.)
- **Monster + encounter are one slice.** `CustomMonsterModel` auto-registers via `RegisterType`; `CustomEncounterModel(RoomType.Monster)` auto-`AddEncounter` in its constructor (no manual register). A **monster attack uses `.FromMonster(this).Execute(null)` — NEVER `.Targeting()`** (that's the card pattern and it hangs the enemy turn). Loc: `monsters.<ID>.name`, `encounters.<ID>.title`+`.loss`. See `recipes/monster.md`.
- **Event/World Node:** `CustomEventModel` auto-`AddEvent`s (no `[Pool]`); default empty
  `Acts` makes it available to every act. Prefer nested in-code `EventLoc`; the option
  method name slug must match its `EventOptionLoc` key. Prove it through `MapNode` by
  entering `ModelDb.Event<T>()`, clicking a real `NEventOptionButton`, and asserting the
  option's run-state consequence. Custom event art remains provisional.
- **Loc-key derivation** (same for relics, potions, cards, powers): `Id.Entry = "<NS_UPPER>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split + UPPER_SNAKE). Keys are **flat strings**, not nested JSON. Table is `relics` / `potions` / `cards` / `powers` per type.
- **Relic combat-start energy**: use `AfterSideTurnStart` + `TurnNumber <= 1` guard. `BeforeCombatStart()` is wrong — energy reset wipes it.
- **Counter lifetime is a design decision:** "every N turns" defaults to run-persistent
  Happy Flower semantics (`[SavedProperty]`); "on turn N of each combat" reads
  `PlayerCombatState.TurnNumber`. Never use a plain field for state that must survive
  save/resume, and never duplicate the combat turn counter.
- **Potions fire in `OnUse`** (they're actively used) — no combat hook. Self-buff potions target `AnyPlayer`, not `Self`. Damage/block use `ValueProp.Unpowered`.
- **Cards fire in `OnPlay`**; a card targeting the player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions). Numbers come from `DynamicVars` (scaling), not literals; attacks use the `DamageCmd.Attack(...)` fluent builder. Loc table `cards`, no separate upgrade key (SmartFormat `:diff()` handles it).
- **Counter Power amounts need a SPEC domain** (nonnegative by default). To consume a
  nonnegative Counter, find its existing instance, clamp the spend, and call
  `PowerCmd.ModifyAmount`; never consume with a negative `PowerCmd.Apply<T>` because a
  missing instance would be created negative.
- **Never `System.Random`** for in-game RNG — use `MegaCrit.Sts2.Core.Random.Rng`.
- **Don't guess an API** — if the recipe lacks it, check the rest of the pack (`reference/mechanics.md`, `reference/build-constraints.md`, snapshots, `errors.md`) per `grounding.md`. If it's genuinely not in the pack, report a pack gap rather than digging or guessing.
