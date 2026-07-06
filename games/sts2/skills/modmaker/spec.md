# Spec — write the design contract

Goal: freeze the intake into `SPEC.md` in the work dir. This is the contract every
later stage reads. Also seed `PLAN.md` (stage checklist) and `MEMORY.md`.

> **Work dir = a dedicated empty outer folder whose name is NOT `<ModName>`** (e.g.
> `<modname>-mod`). Create it now and write these three files there; `scaffold.md`
> then `cd`s into it and runs `dotnet new` (the template scatters into CWD and makes
> a `<ModName>/` resource subdir, so the outer name must differ — see scaffold.md
> step 1). Do **not** name the work dir `<ModName>`.

## Write `SPEC.md`

Use the block for the element type. **Relic:**

```markdown
# SPEC — <Mod Name>

- **element**: relic
- **class name**: <PascalCase, no spaces>   e.g. GamblersCoin
- **mod name**: <PascalCase = csproj/assembly/manifest id>   usually = class name for a single-element mod
- **author**: <author>
- **rarity**: Common | Uncommon | Rare | Shop | Event | Ancient | Starter
- **pool**: SharedRelicPool | Ironclad/Silent/Defect/Regent/Necrobinder
- **trigger**: <plain language> → hook: <AfterSideTurnStart + TurnNumber<=1 | ...>
- **effect**: <precise game-terms description, with numbers>
- **display**:
  - title: <shown name>
  - description: <hover text the player reads>
  - flavor: <flavor line>
- **art**: placeholder
- **derived ids** (compute now, using the recipe's loc-key rule):
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys: `<NS_UPPER>-<SLUG>.{title,description,flavor}`
  - icon slug: `<slug>.png`
```

**Potion** (usage/target replace trigger; loc table is `potions`, no flavor, plus an
optional `selectionScreenPrompt`; no relic icon slug — art is a `.tres` atlas):

```markdown
# SPEC — <Mod Name>

- **element**: potion
- **class name**: <PascalCase, no spaces>   e.g. SwiftBrew
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **author**: <author>
- **rarity**: Common | Uncommon | Rare | Event | Token
- **pool**: SharedPotionPool | Ironclad/Silent/Defect/Regent/Necrobinder
- **usage**: CombatOnly | AnyTime | Automatic
- **target**: AnyPlayer (self-buff) | AnyEnemy (one enemy) | AllEnemies
- **effect**: <precise game-terms description, with numbers>
- **display**:
  - title: <shown name>
  - description: <hover text the player reads>
  - selectionScreenPrompt: <only if the effect prompts a choice; else omit>
- **art**: placeholder (default potion icon; custom .tres atlas is M4)
- **derived ids** (compute now, using the recipe's loc-key rule):
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys (table `potions`): `<NS_UPPER>-<SLUG>.{title,description}`
```

**Card** (cost/type/target + upgrade replace trigger; loc table is `cards`, no flavor,
plus an optional `selectionScreenPrompt`; art is the scaffolded card portrait):

```markdown
# SPEC — <Mod Name>

- **element**: card
- **class name**: <PascalCase, no spaces>   e.g. BladeDance
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **author**: <author>
- **cost**: <energy int, default 1>
- **type**: Attack | Skill | Power
- **rarity**: Basic | Common | Uncommon | Rare
- **pool**: ColorlessCardPool | Ironclad/Silent/Defect/Regent/Necrobinder
- **target**: AnyEnemy (one enemy) | AllEnemies | Self (block / self-buff)
- **effect**: <precise game-terms description, with numbers>
- **vars**: <the DynamicVars, e.g. DamageVar 6; BlockVar 5; PowerVar<StrengthPower> 2>
- **upgrade**: <what OnUpgrade bumps, e.g. Damage +3>
- **needs custom power?**: <no | name of the buff/debuff to author via recipes/power.md>
- **display**:
  - title: <shown name>
  - description: <hover text; use {Damage:diff()} style placeholders for scaling numbers>
  - selectionScreenPrompt: <only if the effect prompts a choice; else omit>
- **art**: placeholder (scaffolded card portrait; custom art is M4)
- **derived ids** (compute now, using the recipe's loc-key rule):
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys (table `cards`): `<NS_UPPER>-<SLUG>.{title,description}`
```

**Derive the ids now**, not later — the loc-key derivation is the #1 silent
failure, and it's identical for relics and potions. Query the sts2-api skill
("relic/potion loc-key derivation rule") or read the recipe if unsure. Worked
example: class `GamblersCoin` in namespace `GamblersCoin.*` → `GAMBLERSCOIN-GAMBLERS_COIN`.

## Seed `PLAN.md`

```markdown
# PLAN — <Mod Name>
- [x] interview
- [x] spec
- [ ] scaffold
- [ ] author
- [ ] build
- [ ] verify (tier-1 load)
- [ ] verify (tier-2 effect, best-effort via dev console)
```

Update the checkboxes as you finish each stage — this is what resume-check reads.

## Seed `MEMORY.md`

Start it with the derived ids and any decisions, so nothing is re-derived later:

```markdown
# MEMORY — <Mod Name>
- Id.Entry: <...>
- loc keys: <...>
- decisions: rarity=Common (default), pool=Shared (default)
```

## Confirm with the user

Show a **plain-language** summary and get a yes before scaffolding:

> (relic) I'll build **<Title>**, a Common relic. At the start of combat it <effect
> in plain words>. It'll drop for any character, with placeholder art for now. Sound right?
>
> (potion) I'll build **<Title>**, a Common potion you can use <in combat / any
> time>. When used it <effect in plain words>. Placeholder art for now. Sound right?
>
> (card) I'll build **<Title>**, a Common <Attack/Skill/Power> card that costs
> <N> energy. When played it <effect in plain words>; upgrading it <upgrade in plain
> words>. It'll appear for any character, placeholder art for now. Sound right?

If they change something, update `SPEC.md` before moving on. Then go to `scaffold.md`.
