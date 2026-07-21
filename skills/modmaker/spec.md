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
  - text effects: none | vanilla
  - text spans: <description phrase -> blue/gold/green/purple/red; see per-surface allowlist>
- **art**: placeholder | generate  (one mod-level choice — see "Art plan" below; `relic`
  icons are wired for generate, 256×256, live-verified)
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only; never record credentials,
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
  - text effects: none | vanilla
  - text spans: <description phrase -> blue/gold/green; selection prompt stays plain>
- **art**: placeholder | generate (a `potion` icon is a loose 256×256 PNG, generate-wired
  and live-verified — same as relic/power; see `reference/art-contract.md`)
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
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
  - text effects: none | vanilla
  - text spans: <description phrase -> gold/purple; SmartFormat owns green/red differences>
- **art**: placeholder | generate  (one mod-level choice — see "Art plan" below;
  generate is wired for `card` / `relic` / `power` / `potion` / `enchantment` / `orb` /
  `monster` / normal-event portrait slots)
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
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
  - text effects: none | vanilla
  - text spans: <description phrase -> blue/gold; apply to smartDescription too>
- **art**: placeholder | generate
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
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
generated art is one static body shared by combat and bestiary; animation is later):

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
- **art**: placeholder | generate: <one full creature in a neutral combat-ready pose>
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
- **art boundary**: one checked `images/monsters/<slug>.png`, 360x360, shared by combat and
  bestiary; `CustomVisualPath` remains the explicit built-in fallback scene; no
  Spine/attack/hurt/death animation or separate phobia body
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
`MapNode`; supported outcomes include blocking selections/rewards and one resumable or
terminal special combat per mutable Event instance; normal portraits and the bounded
`portrait_halo` profile plus bounded vanilla description rich text are supported, while
custom phobia art, arbitrary VFX, and custom/Ancient scenes are not):

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
    effect: <ordered public-Cmd consequence with numbers, including any blocking overlay>
    hover tips: none | enabled-only <Card class + upgrade state; relic class; potion class;
      Power class + amount>
    relic presentation: none | <relic class; normal title/description/metadata; image gap>
    lethal warning: none | HP cost <exact decimal> | Max HP cost <exact decimal>
    acquisition presentation: none | native Card <class> to Deck | native relic <class>
    screen shake: none | `weak_short`
    next: finish <RESULT_KEY> | page <PAGE_KEY> | special combat <ENCOUNTER>
- **special combat**: none | <encounter class + monster/group HP and grounded move cycle>
- **combat completion**: resume page <PAGE_KEY> | map (exactly one when combat exists)
- **extra combat rewards**: none | <owned reward types and amounts>
- **scenario**: MapNode
- **observe**: custom event room entered; formatted loc and real option UI; exact Cmd/
  selection/reward post-state; encounter identity; expected Resume page or direct map
- **art**: placeholder | generate (normal/default layout only; every selected slot is an
  opaque `3440×1613` `images/events/<slot-slug>.png`)
- **portrait slots**:
  - initial: `<event-slug>`
  - `<PAGE_KEY>`: `<event-slug>_<page-key-lower>` (only when explicitly requested)
- **art source**: runtime-imagegen | vofy | byo-http | local-image (generate only)
- **art subject/style**: <opening situation; focal subject left, darker UI space right>
- **art fallback**: initial uses verified vanilla `res://images/events/this_or_that.png`;
  absent page art retains the current portrait
- **event VFX**: none | `portrait_halo` | `trial_noble`
- **VFX pages**: <PAGE_KEY -> unique node name, color/mood; normal layout only>
- **VFX cleanup**: free owned named nodes before page/portrait/combat/finish transitions;
  Instant Fast Mode is static for `portrait_halo`; `trial_noble` inherits host process mode
- **event text effects**: none | vanilla
- **text spans**: <PAGE/OPTION_KEY -> exact phrase -> one or more of emphasis, aqua/blue/
  gold/green/orange/purple/red, jitter, sine; descriptions only; titles plain>
- **forced follow-up**: none | Quest token <class> -> target Event <class>
- **forced act**: none | <exact zero-based act index plus player-facing act name>
- **forced trigger**: carrying one token; next entered Unknown MapPoint in the forced act
- **target pool rule**: target `IsAllowed` is false; token hook is its only supported route
- **token completion**: <named target option> calls `CompleteQuest`, removes all matching
  tokens from the deck, and restores ordinary room/Event hook outputs
- **forced-follow-up boundary**: solo; one token class/target/act; no arbitrary chains,
  vanilla edits, duplicate-token rewards, multiplayer, or new save-roundtrip claim
- **option presentation gaps**: <locked-option tips, normal-layout relic image, or none>
- **unsupported transitions**: merchant, rest site, and treasure room
- **derived ids**:
  - Id.Entry: `<NS_UPPER>-<SLUG>`
  - code loc keys: `<ID>.title`, `<ID>.pages.INITIAL.description`,
    `<ID>.pages.INITIAL.options.<OPTION_KEY>.{title,description}`,
    `<ID>.pages.<RESULT_KEY>.description`
```

`Option(Method)` slugifies the method name, so its derived `<OPTION_KEY>` must exactly
match `EventOptionLoc`. If special combat exists, the spec also owns the custom monster +
encounter dependency from `recipes/monster.md`; do not leave `<ENCOUNTER>` abstract.
`author.md` dispatches Event mechanics to `recipes/event.md`, full outcomes to
`reference/event-outcomes.md`, the optional halo to `reference/event-vfx.md`, and bounded
description styling to `reference/event-text-effects.md`. Enabled typed option tips,
normal relic-backed text/metadata, and exact HP/Max HP warnings route to
`reference/event-option-presentation.md`. A selected forced follow-up routes to
`reference/forced-followup-event.md` and adds the custom Quest Card plus target Event to
this same bounded Event composition. Native Card/relic acquisition presentation,
`weak_short` screen shake, and `trial_noble` route to
`reference/event-native-presentation.md`. The warning cost must be identical to the later
Cmd cost; a `RelicOption<T>` does not itself grant the relic.

All six native-presentation families are pipeline-supported: cross-content Card/standard-
Hover-Tip rich text; enabled Event option Hover Tips plus normal relic-backed text/metadata
with an explicit image blocker; native exact-lethal HP/Max HP warnings; native Card/relic
acquisition presentation; bounded `weak_short` screen shake; and the curated built-in
`trial_noble` Event VFX. Locked-option tips, normal-layout relic images, and positioned
Event speech/thought bubbles remain explicit gaps.

**Character Foundation** (one selectable character shell plus its starter ecosystem;
scenarios are `RunStart` + `CombatPlayer`; selected advanced capabilities use the
separate contracts below):

```markdown
# SPEC — <Mod Name>

- **element**: character
- **character class name**: <PascalCase>
- **mod name**: <PascalCase = csproj/assembly/manifest id>
- **author**: <author>
- **display**:
  - title: <shown character name>
  - description: <short identity/theme>
  - pronouns: <subject/object/possessive adjective/possessive pronoun>
- **starting HP**: <int>
- **energy per turn**: 3 (current grounded Foundation value)
- **pools**: <ModName>CardPool / <ModName>RelicPool / <ModName>PotionPool
- **starter deck**: <exact Basic-card multiset and total count>
- **starter relic**: <exact Starter relic>
- **hosted mechanic**: <one starter card/relic public/BaseLib effect with exact numbers>
- **scenario**: RunStart + CombatPlayer
- **observe**:
  - constructor auto-registration count=1; no manual `AddCharacter`
  - real character-select button present and clicked
  - runtime identity, HP, three pool types/members, exact deck/relic multisets
  - combat `MaxEnergy=3` plus the hosted mechanic's independent state delta
- **advanced mechanic**: none | <selected verified capability or explicit pack gap>
- **art**: placeholder | generate (Character static profiles only; list each consumer)
- **art source**: runtime-imagegen | vofy | byo-http | local-image (generate only)
- **character art profiles**: none | selection | locked selection | top-panel icon |
  map marker | select background | combat body | rest body | merchant body | energy |
  compact energy icon (do not infer one profile from another; mark unsupported consumers
  as explicit gaps per `reference/character-presentation.md`)
- **Ancient presentation**: native banner/dialogue researched but unverified |
  deferred (custom Ancient layout)
- **derived ids**:
  - character Id.Entry: `<NS_UPPER>-<CHARACTER_SLUG>`
  - every starter content Id.Entry and flat loc keys
  - four `THE_ARCHITECT.talk.<CHAR_ID>` keys from `recipes/character.md`
```

`author.md` dispatches `element: character` to `recipes/character.md`. Do not add a
manual registration line or invent a nonstandard energy override. If `advanced mechanic`
is not `none`, also record the envelope below. Author it only when the named semantic
capability has its own scenario-verified pack contract; the 6c kernel alone does not make
arbitrary advanced behavior supported. The scenario-verified 6d routes are exactly
`reference/character-resource.md` and `reference/ordered-card-buffer.md`.

```markdown
- **capability module**: <family/name>
- **semantic host**: <real owner/event>
- **lifetime/reset/save**: <turn|combat|run; exact reset and persistence>
- **public surface**: <typed context/listener used by domain code>
- **adapter**: public/BaseLib | <risk B-D, exact target, version/fingerprint>
- **multiplayer ordering**: <owner/local guard and deterministic order>
- **UI host/fallback**: <host, visibility, refresh, generic fallback>
- **conflict/failure**: <composition policy and fallback>
- **scenario/invariant**: <real host plus exact expected/observed state>
```

When `adapter` is not public/BaseLib, route AUTHOR to
`reference/capability-kernel.md`. Never infer C/D access or a patch target from this
envelope.

For a selected **character resource**, also record:

```markdown
- **resource**: <name>
- **owner/lifetime**: local Player / combat; new PlayerCombatState resets to 0
- **amount domain**: nonnegative integer, floor 0
- **gain sources**: <source -> positive amount>
- **spend/payoff**: <cost -> exact consequence>; all-or-nothing
- **affordability boundary**: <one affordable and one unaffordable case>
- **UI**: generic counter text `<name>: <amount>` under combat energy UI
- **adapter**: risk B `NCombatUi.Activate(CombatState)`, STS2 0.107.1,
  MVID `97f10687-c306-4798-ab75-8b9f23f34dfb`
- **observe**: gain/spend/rejection/floor/counter plus distinct zero state in combat 2
```

For a selected **ordered semantic buffer**, also record:

```markdown
- **buffer**: <name>; owner local PlayerCombatState; lifetime combat
- **recorded value/order**: <semantic value from accepted cards>; append order <matters|not>
- **capacity/overflow**: <positive N>; reject without mutating current contents
- **source destination**: normal STS2 result pile, default Discard
- **visibility**: <compact player-readable state through a grounded UI host>
- **compile**: <trigger>; snapshot <ordered fields>; formula <deterministic expression>
- **output**: <real card + configured DynamicVars + exact effect>
- **observe**: exact source/compile-card destinations, order/capacity/overflow/UI,
  one CardGeneratedEntry, output state/effect, and distinct empty state in combat 2
```

If the user requires real played-card instances to remain in a custom zone, preserve that
idea as a pack gap. Do not silently generate a no-UI `CustomPile`.

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
- **`generate` is wired for eight established static specs — `card`, `relic`, `power`, `potion`,
  `enchantment`, `orb`, `monster`, `event`** (all live-verified — card 1000×760;
  relic/power/potion 256×256; enchantment 64×64; orb icon 100×100; normal event portrait
  slots 3440×1613; static monster body 360×360;
  `reference/art-contract.md`) **plus eight promoted Character specs**:
  `character_select`, `character_background`, `character_icon`, `character_combat`,
  `character_rest`, `character_merchant`, `character_energy`, and
  `character_energy_text`. `character_energy` means five 256x256 layer assets. Locked
  selection and map marker remain explicit gaps until headed consumer proof passes.
- **Orb generation is icon-only.** Keep the recipe's explicit Frost icon/Spine scene/
  channel-SFX fallbacks; `gen_sprite.py` does not emit a combat scene.
- **Enemy generation is static-body only.** One 360×360 PNG feeds combat and bestiary
  through `CreateCustomVisuals()`; keep the explicit fallback scene. Supported Character
  generation is consumer-specific: selection portrait/background, top-panel icon, static
  combat/rest/merchant bodies, five-layer full energy, and compact resource icon use the
  exact profiles in `reference/art-contract.md`. Background/rest/merchant use bundled raw
  scene packing without a Godot/MegaDot prerequisite; merchant also records the versioned
  prefix and patch-failure fallback. Generated-mod authors do not manually install or run
  PckPacker; the character template declares it and `build.py` owns both package paths.
  Locked/map consumers need headed proof. Keep their fallback getters. Event raster
  support includes only the initial and explicitly authored later-page portraits; it does
  not include custom phobia, custom-layout, or Ancient assets. The separate code-native
  `portrait_halo` profile has no raster generation step.
  All other VFX and Spine/animation work is a later expansion.
- **`generate` has four source routes:** a host-native raster image tool that is actually
  callable in the current runtime (`runtime-imagegen`; Codex calls it `image_gen`), an
  already-installed/authenticated Vofy CLI (managed credits), a user-supplied OpenAI-
  compatible endpoint (`art-backend.json`), or an existing local image. Every route
  converges on the `gen_sprite.py` normalization contract; runtime-imagegen, Vofy, and
  local images call `import`. Do not infer native tool availability from a model name or
  installed skill file. If the selected route is unavailable, use placeholder unless the
  user explicitly selects another route — never silently spend through a second backend
  and never block on art.

## Seed `PLAN.md`

```markdown
# PLAN — <Mod Name>
- [x] interview
- [x] spec
- [ ] scaffold
- [ ] author
- [ ] art (per SPEC art plan: placeholder = nothing to do; generate = acquire + gen_sprite.py import)
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
> <art line> Sound right?
>
> (character) I'll build **<Title>**, a selectable character with <HP> HP, standard
> 3 energy, <starter deck summary>, and <starter relic/effect>. The first build uses
> character-template placeholders and proves selection, run start, and the starter effect.
> Sound right?

For the **<art line>**, reflect the SPEC art plan: "with placeholder art for now" (the
fast default), or "with custom art I'll generate for the portrait" if they chose
generate for a card. Keep it one clause — don't turn the confirmation into an art
interview (that already happened in `interview.md` / this stage's art plan).

If they change something, update `SPEC.md` before moving on. Then go to `scaffold.md`.
