# Spec — write the design contract

Goal: freeze the intake into `SPEC.md` in the work dir. This is the contract every
later stage reads. Also seed `PLAN.md` (stage checklist) and `MEMORY.md`.

Before choosing a surface block, read `semantic-contract.md`. Every SPEC must include
the `sts2-content-semantic/v1` envelope from that file. The blocks below collect
surface-specific inputs; they are semantic data, not implementation recipes. Do not
write framework class names, namespaces, hook signatures, pool attributes, project
references, manifest fields, or resource paths in the user-facing SPEC. The selected
adapter records those details in `MEMORY.md` after the SPEC is frozen.

> **Work dir = a dedicated empty outer folder whose name is NOT `<ModName>`** (e.g.
> `<modname>-mod`). Create it now and write these three files there; `scaffold.md`
> then `cd`s into it and runs `dotnet new` (the template scatters into CWD and makes
> a `<ModName>/` resource subdir, so the outer name must differ — see scaffold.md
> step 1). Do **not** name the work dir `<ModName>`.

## Write `SPEC.md`

Use the block for the element type. **Relic:**

```markdown
# SPEC — <Mod Name>

- **contract**: sts2-content-semantic/v1
- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: relic
  - logical id: <stable local stem, e.g. gamblers_coin>
  - rarity: Common | Uncommon | Rare | Shop | Event | Ancient | Starter
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language drop/pool rule>
- **localization**:
  - fields: title=<shown name>; description=<hover text>; flavor=<flavor line>
  - formatting: plain | bounded vanilla rich text
  - text spans: <description phrase -> semantic color intent>
- **effects**:
  - trigger: <plain-language event and boundary, e.g. start of combat>
  - target: owner
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named values and bounds, or none>
- **state**: none | see the stateful-mechanic contract below
- **presentation**:
  - assets: relic icon; placeholder | generate
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
  - native presentation: standard relic display
- **fallback**:
  - missing asset: checked template relic icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: <real trigger, e.g. enter combat>
  - invariants: <exact expected/observed state plus visible trigger>
  - boundary cases: <owner guard/reset/save cases, or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

**Potion** (usage/target replace trigger; loc table is `potions`, no flavor, plus an
optional `selectionScreenPrompt`; art is a loose 256×256 PNG icon, like relic/power):

```markdown
# SPEC — <Mod Name>

- **element**: potion
- **logical id**: <stable local stem, e.g. swift_brew>
- **mod id**: <stable mod identity>
- **author**: <author>
- **rarity**: Common | Uncommon | Rare | Event | Token
- **availability**: shared | character:<name>
- **usage**: CombatOnly | AnyTime | Automatic
- **target**: self | one enemy | all enemies
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
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - logical id: `<stable local stem>`
  - localization fields: `title`, `description`
  - asset role: potion icon
```

**Card** (cost/type/target + upgrade replace trigger; loc table is `cards`, no flavor,
plus an optional `selectionScreenPrompt`; art is the scaffolded card portrait):

```markdown
# SPEC — <Mod Name>

- **contract**: sts2-content-semantic/v1
- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: card
  - logical id: <stable local stem, e.g. blade_dance>
  - kind: Attack | Skill | Power
  - rarity: Basic | Common | Uncommon | Rare
  - relations: <none | custom power/keyword/enchantment/orb dependencies>
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language card-pool rule>
- **localization**:
  - fields: title=<shown name>; description=<hover text>; optional selection prompt
  - formatting: dynamic value placeholders; plain | bounded vanilla rich text
  - text spans: <description phrase -> semantic color intent>
- **effects**:
  - trigger: play
  - target: one enemy | all enemies | self
  - cost: <energy integer, default 1>
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named base values, e.g. damage 6; block 5; strength 2>
  - upgrade: <named value deltas, e.g. damage +3>
- **state**: none | see the stateful-mechanic contract below
- **presentation**:
  - assets: card portrait; placeholder | generate
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
  - native presentation: standard card body/preview
- **fallback**:
  - missing asset: checked template card portrait
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: play the real card against its declared target
  - invariants: <exact expected/observed state, result pile, and dependent effects>
  - boundary cases: <upgrade/state/relationship cases, or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

**Custom power** (standalone or a dependency of a card/relic/potion; include one block
for every authored custom Power):

```markdown
- **element**: power
- **logical id**: <stable local stem>
- **mod id**: <stable mod identity>
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
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - logical id: `<stable local stem>`
  - localization fields: `title`, `description`, `smartDescription`
  - asset role: power icon
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
  - persistence: ordinary | run save
  - display: hidden | progress | current combat turn | uses remaining
  - observe:
    - below threshold: <N-1 progress and no effect>
    - at threshold: <exact effect delta + wrap/consume result>
    - boundary: <turn/combat reset OR carry-over into a second combat>
    - save round trip: <required for run lifetime; restored property value>
```

Use `run` + `run save` for Happy Flower-style progress that crosses combat and survives
save/resume. Use the combat's native turn number for Stone Calendar-style "on turn N"/
"every N turns this combat"; do not duplicate it. Use ordinary state with an explicit
reset for turn-local and once-per-combat state.
Query `reference/stateful-mechanics.md` before authoring or verifying this block.

**Enemy encounter** (a monster + the encounter that spawns it — always authored as one
slice; scenario is `CombatEnemy`, not `CombatPlayer`; loc tables are `monsters` + `encounters`;
generated art is one static body shared by combat and bestiary; animation is later):

```markdown
# SPEC — <Mod Name>

- **element**: enemy encounter
- **monster logical id**: <stable local stem, e.g. canary_mite>
- **encounter logical id**: <stable local stem, e.g. canary_mite_encounter>
- **mod id**: <stable mod identity>
- **author**: <author>
- **hp**: <int>   (Min == Max for deterministic HP)
- **moves**:
  - id: <UPPER_SNAKE>
    intents: <attack N | multi N x R | buff | debuff | defend | heal; list every visible intent>
    effect: <ordered game-term effects with exact numbers and targets>
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
  - multi-attack: observed hit-result count equals the repeat count
  - composite action: every effect from the same move is observed
  - branch: each advertised outcome is forced by its real condition and observed
- **art**: placeholder | generate: <one full creature in a neutral combat-ready pose>
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
- **art boundary**: one checked 360x360 static body shared by combat and bestiary; an
  explicit built-in scene remains the fallback; no Spine/attack/hurt/death animation or
  separate phobia body
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - monster logical id and localization field: `name`
  - encounter logical id and localization fields: `title`, `loss`
```

The monster and encounter are **not** modeled as two `elements` + an interaction edge (that
form is for source→dependent links like card→power). They are one indivisible slice with a
single recipe (`recipes/monster.md`) and a single `CombatEnemy` proof. `author.md` dispatches
to that recipe when `element: enemy encounter`. A one-move enemy may keep one self-looping
move. A multi-move enemy must fill the compact move/branch contract above before authoring;
an intent label or a green build is not behavior proof.

**Event / World Node** (one semantic Event with nested pages/options; scenario is
`MapNode`; supported outcomes include blocking selections/rewards and one resumable or
terminal special combat per mutable Event instance; normal portraits and the bounded
`portrait_halo` profile plus bounded vanilla description rich text are supported, while
custom phobia art, arbitrary VFX, and custom/Ancient scenes are not):

```markdown
# SPEC — <Mod Name>

- **element**: event
- **logical id**: <stable local stem, e.g. gilded_signpost>
- **mod id**: <stable mod identity>
- **author**: <author>
- **acts**: all | <Glory | Hive | Overgrowth | Underdocks>
- **opening**: <initial page description>
- **options**:
  - id: <stable option stem, e.g. follow_the_sign>
    title: <button title>
    description: <button consequence text>
    effect: <ordered game-term consequence with numbers, including any blocking overlay>
    hover tips: none | enabled-only <content name + upgrade/amount state>
    relic presentation: none | <relic name; normal title/description/metadata; image gap>
    lethal warning: none | HP cost <exact decimal> | Max HP cost <exact decimal>
    acquisition presentation: none | native Card <name> to Deck | native relic <name>
    screen shake: none | `weak_short`
    next: finish <RESULT_KEY> | page <PAGE_KEY> | special combat <ENCOUNTER>
- **special combat**: none | <encounter logical id + monster/group HP and grounded move cycle>
- **combat completion**: resume page <PAGE_KEY> | map (exactly one when combat exists)
- **extra combat rewards**: none | <owned reward types and amounts>
- **scenario**: MapNode
- **observe**: custom event room entered; formatted text and real option UI; exact outcome/
  selection/reward post-state; encounter identity; expected Resume page or direct map
- **art**: placeholder | generate (normal/default layout only; every selected slot is an
  opaque 3440x1613 portrait)
- **portrait slots**:
  - initial: `<event-slug>`
  - `<PAGE_KEY>`: `<event-slug>_<page-key-lower>` (only when explicitly requested)
- **art source**: runtime-imagegen | vofy | byo-http | local-image (generate only)
- **art subject/style**: <opening situation; focal subject left, darker UI space right>
- **art fallback**: initial uses the verified vanilla portrait; absent page art retains
  the current portrait
- **event VFX**: none | `portrait_halo` | `trial_noble`
- **VFX pages**: <PAGE_KEY -> unique node name, color/mood; normal layout only>
- **VFX cleanup**: free owned named nodes before page/portrait/combat/finish transitions;
  Instant Fast Mode is static for `portrait_halo`; `trial_noble` inherits host process mode
- **event text effects**: none | vanilla
- **text spans**: <PAGE/OPTION_KEY -> exact phrase -> one or more of emphasis, aqua/blue/
  gold/green/orange/purple/red, jitter, sine; descriptions only; titles plain>
- **forced follow-up**: none | Quest token <logical id> -> target Event <logical id>
- **forced act**: none | <exact zero-based act index plus player-facing act name>
- **forced trigger**: carrying one token; next entered Unknown MapPoint in the forced act
- **target pool rule**: target is excluded from ordinary Event placement; the token route
  is its only supported entry
- **token completion**: <named target option> completes the quest, removes all matching
  tokens from the deck, and restores ordinary room/Event behavior
- **forced-follow-up boundary**: solo; one token class/target/act; no arbitrary chains,
  vanilla edits, duplicate-token rewards, multiplayer, or new save-roundtrip claim
- **option presentation gaps**: <locked-option tips, normal-layout relic image, or none>
- **unsupported transitions**: merchant, rest site, and treasure room
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - Event logical id plus title/page/option localization fields
```

Each option id is stable semantic input; the adapter derives any method and localization
keys from it. If special combat exists, the spec also owns the custom monster + encounter
dependency from `recipes/monster.md`; do not leave `<ENCOUNTER>` abstract.
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
- **logical id**: <stable character stem>
- **mod id**: <stable mod identity>
- **author**: <author>
- **display**:
  - title: <shown character name>
  - description: <short identity/theme>
  - pronouns: <subject/object/possessive adjective/possessive pronoun>
- **starting HP**: <int>
- **energy per turn**: 3 (current grounded Foundation value)
- **availability**: character-scoped card/relic/potion pools
- **starter deck**: <exact Basic-card multiset and total count>
- **starter relic**: <exact Starter relic>
- **hosted mechanic**: <one starter card/relic grounded public mechanic with exact numbers>
- **scenario**: RunStart + CombatPlayer
- **observe**:
  - the character is registered exactly once and appears in character selection
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
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - character logical id
  - every starter content logical id and localization fields
  - Architect dialogue fields from the character reference
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
- **public surface**: <semantic context/listener used by domain code>
- **adapter route**: public-api | owned-adapter | gated-host-seam
- **adapter constraints**: <risk, exact target, version/fingerprint; implementation-only>
- **multiplayer ordering**: <owner/local guard and deterministic order>
- **UI host/fallback**: <host, visibility, refresh, generic fallback>
- **conflict/failure**: <composition policy and fallback>
- **scenario/invariant**: <real host plus exact expected/observed state>
```

When `adapter route` is `gated-host-seam`, route AUTHOR to
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
- **adapter route**: selected after SPEC; must preserve the fixed icon+text UI and fallback
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
- **output**: <real card + configured scaling values + exact effect>
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
    id: `<source logical id>`
  - name: <DependentElement>
    type: card | relic | potion | power
    id: `<dependent logical id>`
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
relationship contract; `combo` is not a content model or a user-selectable element.

For a `consumes` edge on a nonnegative Counter (for example, "consume up to N"), add
three boundary observations: zero stacks, fewer than N, and at least N. Each observation
must state the expected remaining amount/removal and assert that no instance with
`Amount < 0` appears. These become required self-test cases, not prose-only edge cases.

**Freeze logical ids now**, then let the selected adapter derive concrete content and
localization keys. The semantic contract must not depend on a namespace or framework
prefix. Record the resolved keys in `MEMORY.md` after adapter selection and verify them
through the nearest hosted suite.

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

Start it with the semantic contract and adapter selection record, so implementation
details are derived once and remain resumable:

```markdown
# MEMORY — <Mod Name>
- semantic contract: sts2-content-semantic/v1
- logical ids: <...>
- framework profile: <selected adapter profile>
- adapter: <surface/contract-version>
- resolved content ids: <...>
- resolved localization keys: <...>
- framework diagnostics: <host/framework/compat/status>
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
