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
- **state**: none | see the stateful-mechanic contract below
- **display**:
  - title: <shown name>
  - description: <hover text the player reads>
  - flavor: <flavor line>
- **art**: placeholder | generate  (one mod-level choice — see "Art plan" below; `relic`
  icons are wired for generate, 256×256, live-verified)
- **art source**: vofy | byo-http | local-image  (generate only; never record credentials,
  account details, or credit balance)
- **derived ids** (compute now, using the recipe's loc-key rule):
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys: `<NS_UPPER>-<SLUG>.{title,description,flavor}`
  - icon slug: `<slug>.png`
```

**Potion** (usage/target replace trigger; loc table is `potions`, no flavor, plus an
optional `selectionScreenPrompt`; art is a loose 256×256 PNG icon, like relic/power):

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
- **art**: placeholder | generate (a `potion` icon is a loose 256×256 PNG, generate-wired
  and live-verified — same as relic/power; see `reference/art-contract.md`)
- **art source**: vofy | byo-http | local-image  (generate only)
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
- **custom keywords**: <none | name + shared plain-language rule; author via recipes/keyword.md>
- **card enchantments**: <none | enchantment name + compatible host + persistent change;
  author via recipes/enchantment.md; this is not a run modifier>
- **custom orbs**: <none | orb name + host that channels it + passive effect + evoke effect;
  author via recipes/orb.md>
- **display**:
  - title: <shown name>
  - description: <hover text; use {Damage:diff()} style placeholders for scaling numbers>
  - selectionScreenPrompt: <only if the effect prompts a choice; else omit>
- **art**: placeholder | generate  (one mod-level choice — see "Art plan" below;
  generate is wired for all four types: `card` / `relic` / `power` / `potion`)
- **art source**: vofy | byo-http | local-image  (generate only)
- **derived ids** (compute now, using the recipe's loc-key rule):
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys (table `cards`): `<NS_UPPER>-<SLUG>.{title,description}`
```

**Custom power** (standalone or a dependency of a card/relic/potion; include one block
for every authored custom Power):

```markdown
- **element**: power
- **class name**: <PascalCase, no spaces>
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **type**: Buff | Debuff
- **stack type**: Counter | Single
- **amount domain**: `[0, unbounded]` (default for Counter) | `[<min>, <max>]`
- **signed amounts**: no (default) | yes - <what negative stacks mean>
- **effect**: <precise hook/passive behavior, with numbers>
- **display**:
  - title: <shown name>
  - description: <hover text using {Amount}>
  - smartDescription: <usually the same text; required>
- **art**: placeholder | generate
- **art source**: vofy | byo-http | local-image  (generate only)
- **derived ids**:
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - loc keys (table `powers`): `<NS_UPPER>-<SLUG>.{title,description,smartDescription}`
```

`amount domain` is mandatory for every custom `Counter`. Keep the nonnegative default
unless the design explicitly defines negative-stack behavior; `AllowNegative` is an
implementation property, not a substitute for this SPEC decision. Write finite bounds
as numbers rather than leaving them implicit. `Single` is a flag-like Power with hidden
amount 1, so it does not need a Counter domain.

**Stateful-mechanic contract** (add when any element remembers progress; omit for a
stateless effect). This is state owned by the real relic/card/power, not a new element:

```markdown
- **state**:
  - event: <the exact owner-scoped event that advances state>
  - threshold: <N>
  - phase: advance-then-check | check-then-consume
  - lifetime: turn | combat | run
  - reset: <owner turn start | enter CombatRoom | never during the run>
  - persistence: ordinary field | `[SavedProperty]` int/bool
  - display: hidden | progress | current combat turn | uses remaining
  - observe:
    - below threshold: <N-1 progress and no effect>
    - at threshold: <exact effect delta + wrap/consume result>
    - boundary: <turn/combat reset OR carry-over into a second combat>
    - save round trip: <required for run lifetime; restored property value>
```

Use `run` + `[SavedProperty]` for Happy Flower-style progress that crosses combat and
survives save/resume. Use `combat` + `PlayerCombatState.TurnNumber` for Stone Calendar-
style "on turn N"/"every N turns this combat"; do not duplicate the game's turn counter.
Use an ordinary field with an explicit reset for turn-local and once-per-combat state.
Query `reference/stateful-mechanics.md` before authoring or verifying this block.

**Enemy encounter** (a monster + the encounter that spawns it — always authored as one
slice; scenario is `CombatEnemy`, not `CombatPlayer`; loc tables are `monsters` + `encounters`;
art is a Spine scene and stays placeholder — custom monster art is not yet supported):

```markdown
# SPEC — <Mod Name>

- **element**: enemy encounter
- **monster class name**: <PascalCase>   e.g. CanaryMite
- **encounter class name**: <PascalCase>   e.g. CanaryMiteEncounter
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **author**: <author>
- **hp**: <int>   (Min == Max for deterministic HP)
- **moves**:
  - id: <UPPER_SNAKE>
    intents: <attack N | multi N x R | buff | debuff | defend | heal; list every visible intent>
    effect: <ordered Cmd effects with exact numbers and targets>
    next: <move id | branch id>
- **branches**: none | <branch id>: if <exhaustive condition> -> <move id>; else -> <move id>
- **loop**: <deterministic move/branch cycle; every move and branch has a reachable successor>
- **group**: single | <the monsters the encounter spawns>
- **valid acts**: all | <Glory | Hive | Overgrowth | Underdocks>
- **scenario**: CombatEnemy
- **observe**:
  - every advertised move id executes in the declared order
  - self buff/custom Power: exact monster Power amount plus a later changed attack/result
  - player debuff: exact player Power amount immediately after application
  - block/heal: exact monster Block and HP deltas from a wounded pre-state
  - multi-attack: `CreatureAttackedEntry.DamageResults.Count` equals the repeat count
  - composite action: every effect from the same move is observed
  - branch: each advertised outcome is forced by its real condition and observed
- **art**: explicit built-in placeholder (`SceneHelper.GetScenePath("creature_visuals/fallback")`;
  custom monster Spine scene not yet supported)
- **derived ids** (compute now, using the recipe's loc-key rule):
  - monster Id.Entry: `<NS_UPPER>-<MONSTER_SLUG>`; loc key (table `monsters`): `<NS_UPPER>-<MONSTER_SLUG>.name`
  - encounter Id.Entry: `<NS_UPPER>-<ENCOUNTER_SLUG>`; loc keys (table `encounters`): `<NS_UPPER>-<ENCOUNTER_SLUG>.{title,loss}`
```

The monster and encounter are **not** modeled as two `elements` + an interaction edge (that
form is for source→dependent links like card→power). They are one indivisible slice with a
single recipe (`recipes/monster.md`) and a single `CombatEnemy` proof. `author.md` dispatches
to that recipe when `element: enemy encounter`. A one-move enemy may keep one self-looping
move. A multi-move enemy must fill the compact move/branch contract above before authoring;
an intent label or a green build is not behavior proof.

**Event / World Node** (one `CustomEventModel` with nested pages/options; scenario is
`MapNode`; custom event art is provisional and stays on the verified vanilla placeholder):

```markdown
# SPEC — <Mod Name>

- **element**: event
- **class name**: <PascalCase>   e.g. GildedSignpost
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **author**: <author>
- **acts**: all | <Glory | Hive | Overgrowth | Underdocks>
- **opening**: <initial page description>
- **options**:
  - method: <PascalCase method, e.g. FollowTheSign>
    key: <UPPER_SNAKE derived from method, e.g. FOLLOW_THE_SIGN>
    title: <button title>
    description: <button consequence text>
    effect: <precise Cmd consequence with numbers>
    result page: <key + result description>
- **scenario**: MapNode
- **observe**: custom event room entered; formatted title/option/result loc; real option UI clicked; run-state consequence
- **art**: placeholder (verified vanilla `res://images/events/this_or_that.png`; custom event art not yet supported)
- **derived ids**:
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - code loc keys: `<ID>.title`, `<ID>.pages.INITIAL.description`,
    `<ID>.pages.INITIAL.options.<OPTION_KEY>.{title,description}`,
    `<ID>.pages.<RESULT_KEY>.description`
```

`Option(Method)` slugifies the method name, so its derived `<OPTION_KEY>` must exactly
match `EventOptionLoc`. `author.md` dispatches `element: event` to `recipes/event.md`.

**Multi-element contract** (add only when the mod contains more than one authored element;
omit it for the single-element fast path). `elements` are real content nodes. `interactions`
are directed relationships between them — never use `combo` as an element type.

Each interaction records the source driver, relationship, dependent, scenario, and the
independent observations that prove the link rather than merely proving both nodes loaded:

```markdown
- **elements**:
  - name: <SourceElement>
    type: card | relic | potion | power
    id: `<NS_UPPER>-<SRC_SLUG>`
  - name: <DependentElement>
    type: card | relic | potion | power
    id: `<NS_UPPER>-<DEP_SLUG>`
- **interactions**:
  - source: <SourceElement>
    relation: <applies | grants | creates | triggers | consumes>
    dependent: <DependentElement>
    scenario: CombatPlayer
    observe:
      - source marker: `[T2MOD-SELFTEST] <SourceName> played/fired/used: <what>`
      - dependent marker: `[T2MOD-SELFTEST] <DependentName> fired: <what>`
      - state invariant: <the concrete HP/block/energy/stack change, when applicable>
```

A card with an authored custom power dependency automatically gets two `elements` and an
`interaction` edge. The harness drives the source according to its real type, then checks
every observation in dependency order. This is the old M5 “combo” proof generalized into a
relationship contract; `combo` is not a BaseLib model or a user-selectable element.

For a `consumes` edge on a nonnegative Counter (for example, "consume up to N"), add
three boundary observations: zero stacks, fewer than N, and at least N. Each observation
must state the expected remaining amount/removal and assert that no instance with
`Amount < 0` appears. These become required self-test cases, not prose-only edge cases.

**Derive the ids now**, not later — the loc-key derivation is the #1 silent
failure, and it's identical for relics and potions. Query the sts2-api skill
("relic/potion loc-key derivation rule") or read the recipe if unsure. Worked
example: class `GamblersCoin` in namespace `GamblersCoin.*` → `GAMBLERSCOIN-GAMBLERS_COIN`.

## Art plan (one mod-level choice — the §7.1 decision)

The mod gets **one** art decision, taken from the interview (asked at most once, never
per sprite): **placeholder** (the default — do nothing, the template's built-in art
shows; keeps the loop fast and the mod immediately testable) or **generate** (produce
custom sprites via `author.md`'s art step). Record it in `SPEC.md`'s `**art**` line,
plus the selected `**art source**` and one overall subject/style note if `generate`, so
`author.md` can build each prompt. When the mod has several cards, `author.md` fills the
per-card subject from each card's SPEC at generate time — but the placeholder-vs-generate
choice was made once, for the whole mod.

Rules for this round:

- **Placeholder is the default and needs no backend, no key, no dev box.** If the user
  didn't ask for custom art, leave it placeholder — this is exactly the current,
  already-verified behavior (no regression).
- **`generate` is wired for all four element types — `card`, `relic`, `power`, `potion`**
  (all live-verified — card 1000×760; relic/power/potion 256×256 loose PNGs;
  `reference/art-contract.md`).
- **Event and enemy-encounter art stays placeholder.** Do not call `gen_sprite.py` for
  either; their scene/portrait contracts have not been live-grounded.
- **`generate` has three source routes:** an already-installed/authenticated Vofy CLI
  (managed credits), a user-supplied OpenAI-compatible endpoint (`art-backend.json`), or
  an existing local image. Every route converges on the `gen_sprite.py` normalization
  contract; Vofy is only acquisition and calls `import`. If the selected route is
  unavailable, offer another route or fall back to
  placeholder — never silently spend through a second backend and never block on art.

## Seed `PLAN.md`

```markdown
# PLAN — <Mod Name>
- [x] interview
- [x] spec
- [ ] scaffold
- [ ] author
- [ ] art (per SPEC art plan: placeholder = nothing to do; generate = gen_sprite.py)
- [ ] build
- [ ] verify (tier-1 load)
- [ ] verify (tier-2 effect, automated via the self-test harness)
```

Update the checkboxes as you finish each stage — this is what resume-check reads.

## Seed `MEMORY.md`

Start it with the derived ids and any decisions, so nothing is re-derived later:

```markdown
# MEMORY — <Mod Name>
- Id.Entry: <...>
- loc keys: <...>
- decisions: <type-specific defaults, e.g. rarity/pool OR event acts=all>
- state: <none OR event/threshold/phase/lifetime/reset/persistence + required proofs>
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
> words>. It'll appear for any character. <art line>. Sound right?
>
> (event) I'll build **<Title>**, a map event available in <all acts / the chosen acts>.
> The player sees <opening>, can choose <option summary>, and that choice <consequence>.
> It will use a placeholder event portrait for now. Sound right?

For the **<art line>**, reflect the SPEC art plan: "with placeholder art for now" (the
fast default), or "with custom art I'll generate for the portrait" if they chose
generate for a card. Keep it one clause — don't turn the confirmation into an art
interview (that already happened in `interview.md` / this stage's art plan).

If they change something, update `SPEC.md` before moving on. Then go to `scaffold.md`.
