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
---

# STS2 API Lookup

This skill is a narrow reference tool. Answer only what the caller asked — do
not dump entire files into the response.

## How to answer

1. Check `${STS2_API_SKILL_DIR}/recipes/` for the element type (relic, potion, card,
   power). Cards/powers also read `${STS2_API_SKILL_DIR}/reference/mechanics.md` first
   (scaling numbers, SmartFormat descriptions, shared enums).
2. For error signatures → fix, read `${STS2_API_SKILL_DIR}/errors.md`.
3. For content facts (what effects exist, a vanilla analog, realistic numbers) or a
   symbol the recipe lacks, read `${STS2_API_SKILL_DIR}/grounding.md` and, for
   potions, `${STS2_API_SKILL_DIR}/reference/potions-snapshot.md`.
4. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

**Never read all files at once.** Each file is loaded on demand.

## Files in this pack

| File | Content | When to read |
|------|---------|--------------|
| `recipes/relic.md` | Full known-good relic pattern (skeleton, hooks, energy Cmds, RNG, loc-key derivation, checklist, golden example) | Authoring a relic |
| `recipes/potion.md` | Full known-good potion pattern (OnUse trigger, Rarity/Usage/TargetType, effect Cmds, loc table `potions`, checklist, worked examples) | Authoring a potion |
| `recipes/card.md` | Full known-good card pattern (OnPlay, CardType/rarity/target, DamageCmd fluent builder + GainBlock + PowerCmd.Apply, DynamicVars/upgrade, loc table `cards`, `card <id>` console cmd, worked examples) | Authoring a card |
| `recipes/power.md` | Full known-good custom-power pattern (Type/StackType, trigger hooks, PowerCmd.Apply, loc table `powers`) — usually a dependency of a card/relic | Authoring a custom buff/debuff |
| `reference/mechanics.md` | Cross-element foundations: DynamicVars, SmartFormat descriptions, shared enums (TargetType/CardType/rarities/…) | Before writing a card or power |
| `reference/build-constraints.md` | What the toolchain refuses to BUILD/LOAD: full analyzer diagnostic set STS001–004 + the exact required-loc-key table per model type (cards/potions/relics/powers/…) + `[Pool]` rule | Before writing any element's loc keys + attributes; on any STS0NN build error |
| `grounding.md` | Where facts come from (three sources: content→spire-codex, C# signatures→decompile, build/load→validators) + the runtime-vs-maintainer split: at runtime you read only the pack; a genuine miss is a pack gap to report, not a dig | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

*Editing existing* vanilla content (relics/cards/potions) is not a recipe — it needs
Harmony patching and is deferred. The recipes make **new** elements.

## Key rules to remember (recite these when relevant)

- **`[Pool]` is required** on every `CustomRelicModel` / `CustomPotionModel` / `CustomCardModel` subclass or BaseLib throws at registration. (A **power** is the exception — auto-discovered, NO `[Pool]`.)
- **Loc-key derivation** (same for relics, potions, cards, powers): `Id.Entry = "<NS_UPPER>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split + UPPER_SNAKE). Keys are **flat strings**, not nested JSON. Table is `relics` / `potions` / `cards` / `powers` per type.
- **Relic combat-start energy**: use `AfterSideTurnStart` + `TurnNumber <= 1` guard. `BeforeCombatStart()` is wrong — energy reset wipes it.
- **Potions fire in `OnUse`** (they're actively used) — no combat hook. Self-buff potions target `AnyPlayer`, not `Self`. Damage/block use `ValueProp.Unpowered`.
- **Cards fire in `OnPlay`**; a card targeting the player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions). Numbers come from `DynamicVars` (scaling), not literals; attacks use the `DamageCmd.Attack(...)` fluent builder. Loc table `cards`, no separate upgrade key (SmartFormat `:diff()` handles it).
- **Never `System.Random`** for in-game RNG — use `MegaCrit.Sts2.Core.Random.Rng`.
- **Don't guess an API** — if the recipe lacks it, check the rest of the pack (`reference/mechanics.md`, `reference/build-constraints.md`, snapshots, `errors.md`) per `grounding.md`. If it's genuinely not in the pack, report a pack gap rather than digging or guessing.
