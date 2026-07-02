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

1. Check `${STS2_API_SKILL_DIR}/recipes/` for the element type (relic, potion; card is M4+).
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
| `grounding.md` | Where facts come from: spire-codex (content) vs the local decompile (C# signatures); how to query each without guessing | An answer the recipe lacks |
| `reference/potions-snapshot.md` | Distilled spire-codex content facts: the 63 vanilla potions + enum values | Picking a potion effect / analog |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

More recipes (card) will be added later in M4.

## Key rules to remember (recite these when relevant)

- **`[Pool]` is required** on every `CustomRelicModel` / `CustomPotionModel` subclass or BaseLib throws at registration.
- **Loc-key derivation** (same for relics and potions): `Id.Entry = "<NS_UPPER>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split + UPPER_SNAKE). Keys are **flat strings**, not nested JSON. Table is `relics` for relics, `potions` for potions.
- **Relic combat-start energy**: use `AfterSideTurnStart` + `TurnNumber <= 1` guard. `BeforeCombatStart()` is wrong — energy reset wipes it.
- **Potions fire in `OnUse`** (they're actively used) — no combat hook. Self-buff potions target `AnyPlayer`, not `Self`. Damage/block use `ValueProp.Unpowered`.
- **Never `System.Random`** for in-game RNG — use `MegaCrit.Sts2.Core.Random.Rng`.
- **Don't guess an API** — if the recipe lacks it, use `grounding.md` (content → spire-codex; code → the decompile).
