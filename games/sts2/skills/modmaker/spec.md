# Spec — write the design contract

Goal: freeze the intake into `SPEC.md` in the work dir. This is the contract every
later stage reads. Also seed `PLAN.md` (stage checklist) and `MEMORY.md`.

## Write `SPEC.md`

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

**Derive the ids now**, not later — the loc-key derivation is the #1 silent
failure. Query the sts2-api skill ("relic loc-key derivation rule") or read
`recipes/relic.md` if unsure. Worked example: class `GamblersCoin` in namespace
`GamblersCoin.*` → `GAMBLERSCOIN-GAMBLERS_COIN`.

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

> I'll build **<Title>**, a Common relic. At the start of combat it <effect in
> plain words>. It'll drop for any character, with placeholder art for now. Sound right?

If they change something, update `SPEC.md` before moving on. Then go to `scaffold.md`.
