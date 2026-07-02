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

1. Check `${STS2_API_SKILL_DIR}/recipes/` for the element type (relic, card, potion).
2. For error signatures → fix, read `${STS2_API_SKILL_DIR}/errors.md`.
3. Return only the relevant snippet (hook, Cmd, loc-key rule, error fix).

**Never read all files at once.** Each file is loaded on demand.

## Files in this pack

| File | Content | When to read |
|------|---------|--------------|
| `recipes/relic.md` | Full known-good relic pattern (skeleton, hooks, energy Cmds, RNG, loc-key derivation, pre-flight checklist, golden example) | Authoring a relic |
| `errors.md` | Error signature → cause → fix catalog; append-only | Build or load failure; repair loop |

More recipes (card, potion) will be added in M4.

## Key rules to remember (recite these when relevant)

- **`[Pool]` is required** on every `CustomRelicModel` subclass or BaseLib throws at registration.
- **Loc-key derivation**: `Id.Entry = "<NS_UPPER>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split + UPPER_SNAKE). Keys in `relics.json` are **flat strings**, not nested JSON.
- **Combat-start energy**: use `AfterSideTurnStart` + `TurnNumber <= 1` guard. `BeforeCombatStart()` is wrong — energy reset wipes it.
- **Never `System.Random`** for in-game RNG — use `MegaCrit.Sts2.Core.Random.Rng`.
