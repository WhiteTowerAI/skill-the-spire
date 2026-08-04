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

Use the block for the element type. **Existing vanilla model override:**

```markdown
# SPEC - <Mod Name>

- **contract**: sts2-content-semantic/v1
- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - surface: vanilla model override
  - requested target: <the user's exact name plus Character qualifier when needed>
  - resolved target: <exact checked ModelId, category, and current display title>
  - preserve: vanilla identity and every untouched behavior/presentation surface
- **operations** (accepted order):
  - id: <stable semantic id>
    mode: adjust | compose | replace | availability | visual
    surface: <named player-facing behavior/data/visual surface>
    desired result: <plain game terms and exact values>
    base expectation: <the player-facing current value checked with the catalog>
    upgrade behavior: unchanged | <exact changed behavior>
    localization effect: none | <exact new/replacement player text>
    timing/order: <set then delta; before/after original; fragment/rule order>
    multiplayer scope: singleplayer | deterministic all peers
    compatibility: required | optional
- **effects** (only for behavior operations):
  - trigger: <play/owner/non-Card lifecycle or exact game event>
  - condition: <bounded declarative live-state condition>
  - sequence: <ordered grounded Card recipe effects and exact values>
  - target: owner | play target | event target | all enemies | random enemy
- **non-Card behavior** (only for promoted M6.7.5 operations):
  - family: owner hook | intrinsic data | lifecycle | monster moves | encounter roster |
    ordinary event options
  - composition: before original | after original | replace complete selected surface
  - scope: any | owner | owner side
  - replacement body: <all lifecycle effects, move states, roster entries, or Event pages>
- **ancient flow** (only for an existing Ancient initial-options operation):
  - initial choices: append | replace all
  - rule condition: <bounded singleplayer owner/run/deck/model condition>
  - priority: <integer, append only>
  - duplicate text: skip | keep (append only)
  - options:
    - id: <stable Mod-local id>
      text: <player-facing title and description>
      visible when: <condition>
      enabled when: <condition>
      cost: none | <fixed Gold/HP/Max HP amount and lethal policy>
      hover: none | <known Card/Relic/Potion/Power entries>
      relic image: none | <known relic>
      effects: <ordered fixed effects, deck selectors, rewards, and optional weak shake>
      next: stay | page <PAGE_ID> | finish
  - pages:
    - id: <PAGE_ID>
      description: <player-facing text>
      options: <same complete option shape>
- **visual resources** (only for promoted visual operations):
  - operation: <operation id>
    role: <frame/portrait/icon/scene/layers/etc.>
    source: generate | local-authored-resource
    requirement: required | optional
    fallback: preserve the exact vanilla surface
- **explicit non-goals**: <unselected behavior/data/visual surfaces and any applicable
  package boundaries>
- **verification scenario**: <nearest real consumer for every selected operation>
```

Resolve and disambiguate the target through `reference/vanilla-overrides.md` before
freezing this block. Put catalog digest,
concrete type, required baseline subset, public route ids, capability class, localization
keys, exact resource paths, and manifest operations in `MEMORY.md`, not in the user-facing
SPEC. Read `reference/vanilla-visual-overrides.md` for selected visual surfaces and
`reference/vanilla-card-overrides.md` for non-asset Card surfaces. For an exact existing
Ancient, read `reference/vanilla-ancient-overrides.md`, preserve its model/room/opening
dialogue/save identity/native finish history, and freeze every replacement option and
reachable page explicitly. Stop if any required operation falls outside those promoted
Packages. One Mod may target multiple existing models; repeat the `content` and ordered
`operations` blocks per exact target.

Record each requested `mode` literally. Never rewrite a vanilla Card base-description
replacement (replace, remove, or hide the original body) as `compose` or as
`before_base`/`after_base` text. RitsuLib `0.5.4` has no promoted route for that request, so
stop before accepting the SPEC. A composition may enter the SPEC only after the user
explicitly accepts that visibly different result, even when every numeric value is already
final or the user asked not to repeat questions.

For M6.7.4 availability, record one exact target and one ordered operation per requested
epoch or pool change. An epoch operation records `state: require_epoch | disabled`, the
exact pinned epoch when required, and `multiplayer: singleplayer`. Public epoch gating is
limited to Cards, Characters, ordinary Events, and shared Darv; Relic/Potion gating uses
the fixed reviewed Adapter and its complete dependency list. A pool operation records
`action: add | remove | move`, the source/destination pool ModelIds, `existing_instances:
preserve`, `expected_primary_pool_model_id`, and `multiplayer: singleplayer`. Copy the
complete catalog pool membership into the baseline and reject a debug pool, duplicate
transition, missing source, or removal of the final pool. Read
`reference/vanilla-availability-overrides.md` before freezing the SPEC. Source weighting,
act-owned Ancient gating, permanent Card/Character/Event disable, and multiplayer remain
explicit gaps rather than prompt-derived patches.

For M6.7.5, read `reference/vanilla-non-card-overrides.md`. Record public owner-hook
composition in game terms with exact trigger/scope/condition/order/result. Record intrinsic
data as a final enum/boolean/integer or integer delta. A complete lifecycle/body replacement
must freeze every callback field, Monster state and edge, Encounter monster/slot entry, or
ordinary Event option/reachable page in the selected surface. Ordinary Event text uses
Mod-local `<MOD_ID>_EVENT_*` keys in every shipped `events.json`; Ancient targets stay on
M6.7.3. All M6.7.5 operations remain singleplayer. Do not turn missing event context,
undeclared capability state, synchronous Affliction effects, multiplayer, or another
uncataloged body into generated patch code.

**Relic:**

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
  - extra badges: none | one to three
    - meaning: <player-facing auxiliary value, e.g. charges remaining>
      value: <state value or bounded display rule>
      corner: top-left | top-right | bottom-left (one label per corner)
      format: plain | bounded color rich text; at most 4 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
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

When a Relic contributes a Rest Site action, add this block to the same Relic SPEC. The
current slice does not accept a Card or Modifier owner:

```markdown
- **owned Rest Site option**:
  - owner: relic
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when the owned relic contributes the option>
  - repeatability: once per Rest Site | once per run
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic game-term operations and exact values>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: singleplayer only
  - proof: absent owner; present disabled/enabled; stale-render failed payment with no
    mutation; exact successful cost/outcome/history; no duplicate; stay/leave; second visit;
    custom icon and missing-icon fallback
```

Absence and disabled are separate. `eligibility` controls contribution; `enabled rule`
controls the native gray/clickable state. A fixed-Gold outcome must be completely
preflightable before its first mutation. Stop authoring for a post-payment selection,
random branch, or other result that would require rollback.

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
- **advanced target**: none | use the shared declaration below
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

**Custom card pile** (repeat once per pile; Mod-level Package surface):

```markdown
- **content**:
  - name: <player-facing pile name>
  - surface: custom card pile
  - logical id: <stable local pile stem>
  - relations: <Cards/effects/screens that move, inspect, or present this pile>
- **registration**:
  - availability: host-owned
  - ownership: player
  - placement: custom Card Piles Package
  - scope: combat | run
- **localization**:
  - fields: title, description, empty
  - table intent: static hover tips
  - formatting: plain
- **effects**:
  - trigger: <every entry/exit/open/arrival interaction>
  - target: <this pile and exact source/destination pile>
  - sequence: <ordered movements and requested callbacks>
  - scaling: none
  - movement: <trigger, exact Card identity, source, destination, top | bottom, rejection rule>
- **state**:
  - lifetime: combat | run
  - owner: player combat state | player
  - advance/check: <capacity/order/duplicate rules and transition timing>
  - reset: combat end | run end
  - persistence: none | run save
  - visible state: <hidden | pile count | visible Cards>
- **presentation**:
  - assets: <none | pile icon and optional view styling assets>
  - text effects: none
  - native presentation: custom Card Piles Package
  - style: headless | top bar deck | bottom left | bottom right | extra hand
  - anchor: style default | <matching preset + offset> | <custom position + pivot>
  - open behavior: default pile screen | public custom screen
  - visibility: always | <deterministic player/pile/room condition>
  - hover tip: auto | below trailing | above centered | below centered; offset <x,y>
  - hotkeys: none | <existing input action ids>
  - view: vanilla | deck-like | explicit capabilities
  - extra hand: <none | direction/spacing/scales/glow/manual play/layout/callback behavior>
- **fallback**:
  - missing asset: RitsuLib placeholder or named built-in resource
  - unavailable seam: fail clearly without changing unrelated piles
  - failure policy: preserve source/destination state or stop authoring
- **proof**:
  - scenario: <matching combat/run/card-pile UI host>
  - driver: <real movement/open/hotkey/manual-play interaction>
  - invariants: <identity/order/count/state/UI/result-pile outcomes>
  - boundary cases: <empty/full/rejection/reset/save/cancel/aspect ratio as selected>
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
  - variable tooltips: none | <value name -> localized title; description; optional icon>
- **effects**:
  - trigger: play
  - target: one enemy | all enemies | self
  - advanced target: none | use the shared declaration below
  - cost: <energy integer, default 1>
  - sequence: <ordered game-term effect with exact values>
  - helper: none | Scry top <X>, discard any number, singleplayer only
  - scaling: <named base values, e.g. damage 6; block 5; strength 2>
  - upgrade: <named value deltas, e.g. damage +3>
  - calculated values: none | one or more
    - <name>: role <plain | damage | block | Energy icons | Star icons | raw typed Power |
      applied typed Power>; formula <one deterministic expression>; inputs <complete list>;
      domain <integer [min,max]>; upgrade <same | exact change>; evaluation <before play |
      after normal payment and move>
- **state**: none | see the stateful-mechanic contract below
- **presentation**:
  - assets: card portrait; placeholder | generate
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
  - native presentation: standard card body/preview
  - hand emphasis: none | one or more ordered rules
    - rule: <stable local rule name; repeat in precedence order>
      meaning: <actionable bonus, warning, or other player-facing state>
      condition: <plain-language active rule>
      color: gold | red | custom <plain color>
      priority: <integer; highest active rule wins>
      while unplayable: show | hide
- **fallback**:
  - missing asset: checked template card portrait
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: play the real card against its declared target
  - invariants: <exact expected/observed state, result pile, and dependent effects>
  - boundary cases: <upgrade/state/relationship cases; for calculated values include
    zero/positive/changing input, domain bounds, base/upgrade, normal modifiers, final
    preview vs effect result, icon reflow, and variable tooltip; for Scry include
    zero/empty/short/full, order, discard hooks/history, awaited selector, and
    singleplayer restriction; or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

When a Card or Potion selects a filtered live-creature target, replace that surface's
`advanced target: none` field with this block at the same indentation (top-level for a
Potion, inside `effects` for a Card). It remains semantic; no framework class or enum
belongs here:

```markdown
- **advanced target**:
  - consumer: card | potion
  - mode: one | many
  - target id: <stable Mod-local stem>
  - candidate conditions: <alive side/intent/Block/current-or-maximum-HP rules>
  - acting-player conditions: none | <plain-language player-relative rules>
  - source conditions: none | <single-target source Card/Potion rule>
  - zero-target behavior: reject or cancel without payment/consumption
  - resolution: apply the effect exactly once to each resolved creature
```

The current pinned adapter accepts `card + one`, `card + many`, and `potion + one`.
`potion + many` stops authoring because the pinned host cannot recheck an empty resolved
group before consumption. Do not rewrite it as ordinary `all enemies`, restore a consumed
Potion, or generate a patch.

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
  - extra badges: none | one
    - meaning: <player-facing auxiliary value distinct from Amount>
      value: <state value or bounded display rule>
      corner: top-left
      format: plain | bounded color rich text; at most 6 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
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

Hand emphasis and extra badges are product semantics, not styling escape hatches. Record
why the player needs the signal and the game-state rule that owns it; never record RitsuLib
interfaces, predicates, `Color` objects, raw markup, rectangles, or invalidation event names
in SPEC. Hand rules remain in declared order; the highest active priority wins and a tie is
resolved by the later listed rule. Relics use at most three distinct safe corners; Powers
use at most one top-left label because their preset label bands overlap in crowded rows.
Every extra badge supplements the native Relic/Power main amount instead of replacing it. Intent belongs to
the public Extra Badges Package, but it has no current generated SPEC block because its
authoring recipe is not scheduled in M6.6.

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
Cmd cost; a relic-backed Event option does not itself grant the relic.

All six native-presentation families are implemented: cross-content Card/standard-
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
- **art**: placeholder | generate (Character static profiles and optional combat cues;
  list each consumer and acquisition count)
- **art source**: runtime-imagegen | vofy | byo-http | local-image (generate only)
- **character art bundle**: one `CharacterArtBundle` row per selected slot; record
  required/optional, output path, dimensions, alpha policy, fallback, and real consumer
- **character identity route**: selection portrait is the sole identity bootstrap;
  combat/rest/merchant and combat cue sheets use identity + type-matched style;
  background/icon/Energy use palette/motif brief + type-matched style only
- **palette/motif brief**: concise colors, motif, material, and silhouette derived from
  the user's description and reviewed selection portrait; never a second canonical image
- **character theme contract**:
  - name color: `<RRGGBB>`
  - energy-label outline: `<RRGGBB>`
  - deck-entry color: `<RRGGBB>`
  - energy outline: `<RRGGBB>`
  - card-frame target RGB: `<0..1, 0..1, 0..1>`
  - card-frame brightness: `<0..2>`
  - energy-icon palette: `<primary/accent/outline colors plus motif/material>`
- **character art profiles**: none | selection | locked selection | top-panel icon |
  map marker | select background | combat body | rest body | merchant body | energy |
  large energy icon | text energy icon (do not infer one profile from another; mark
  unsupported consumers as explicit gaps per `reference/character-presentation.md`)
- **character combat cues**: none | fixed bounded bundle
  - actions: Idle `4 x 180ms, loop`; Attack `4 x 90ms, one-shot -> Idle`;
    Hit `4 x 80ms, one-shot -> Idle`; Dead `6 x 140ms, terminal final frame`
  - acquisition: four action sheets, normalized selection portrait as identity reference
  - neutral combat anchor: <one concise pose sentence derived once and repeated verbatim>
  - continuity lock: same identity, costume, proportions, equipment, facing, camera,
    apparent scale, pivot, and baseline across all four sheets
  - frame motion: adjacent cells are small, substantially overlapping in-between pose
    steps, not distant key poses; Attack/Hit begin near and recover toward Idle; Dead falls
    through six adjacent steps
  - geometry: shared 512x512 content box/baseline/style and Bounds/Intent/Center/Orb/Talk anchors
  - fallback: one missing or invalid frame disables all cues and uses static combat body
  - explicit gaps: Cast, Spine, trails, audio, animated merchant/rest bodies
- **Ancient dialogue**: none | one block per cataloged vanilla target
  - target: <natural-language Ancient name; adapter resolves the pinned entry>
  - groups:
    - visit rule: first | visit <one-based N> | repeat from visit <one-based N>
      - lines: ordered `speaker: Character|Ancient`, `text`, and a transition prompt on
        every non-terminal line
      - Architect only: start attackers and end attackers, each
        `None|Player|Architect|Both`
  - native priority: preserve the global first-visit-ever introduction before Character
    exact-visit and repeating dialogue
  - explicit gaps: custom Ancient/model/background/layout/options/rewards/audio/multiplayer
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - character logical id
  - every starter content logical id and localization fields
  - flat Ancient dialogue keys and zero-based visit metadata from the semantic groups
```

`author.md` dispatches `element: character` to `recipes/character.md`. Do not add a
manual registration line or invent a nonstandard energy override. If `advanced mechanic`
is not `none`, also record the envelope below. Author it only when the named semantic
capability has its own recipe in the shipped pack. Package support alone does not provide
missing runtime instructions. The current implemented public framework
routes are exactly `reference/character-resource.md` and
`reference/ordered-card-buffer.md`.

```markdown
- **capability module**: <family/name>
- **semantic host**: <real owner/event>
- **lifetime/reset/save**: <turn|combat|run; exact reset and persistence>
- **public surface**: <semantic context/listener used by domain code>
- **adapter route**: public-api | owned-adapter
- **adapter constraints**: <exact supported version and implementation-only limits>
- **multiplayer ordering**: <owner/local guard and deterministic order>
- **UI host/fallback**: <host, visibility, refresh, generic fallback>
- **conflict/failure**: <composition policy and fallback>
- **scenario/invariant**: <real host plus exact expected/observed state>
```

If neither documented route can express the mechanic, mark it unsupported and report a
pack gap. Never infer non-public access or a patch target from this envelope.

For a selected **character resource**, also record:

```markdown
- **resource**: <name>
- **owner/lifetime**: local Player / combat; new PlayerCombatState resets to 0
- **amount domain**: nonnegative integer, floor 0
- **gain sources**: <source -> positive amount>
- **spend/payoff**: <cost -> exact consequence>; all-or-nothing
- **affordability boundary**: <one affordable and one unaffordable case>
- **UI**: fixed 220x32 icon+text counter under combat energy UI; checked text-only fallback
- **placement**: offset 160 from native Energy; the two global rects must not intersect
- **adapter route**: public-api selected after SPEC; no private patch fallback
- **observe**: gain/spend/rejection/floor/counter/non-overlap plus distinct zero state in combat 2
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

The adapter lowers the resource block to one framework-owned combat resource with
all-or-nothing commands and a public UI attachment. It lowers the buffer block to combat-
attached semantic state. These implementation records belong in `MEMORY.md`, not SPEC.

Retained-card zone UI is unsupported. If the user requires real played-card instances to
remain in a custom zone, preserve that idea as a pack gap. Do not silently generate a no-UI
`CustomPile`.

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
  `reference/art-contract.md`), plus the verified opaque `rest_site_option` 256x169
  role with checked custom and Heal-fallback button consumers, **plus nine promoted
  Character static specs**:
  `character_select`, `character_background`, `character_icon`, `character_combat`,
  `character_rest`, `character_merchant`, `character_energy`, `character_energy_large`,
  and `character_energy_text`. `character_energy` means five 256x256 layer assets. Locked
  selection and map marker remain explicit gaps until headed consumer proof passes. The
  optional bounded cue bundle adds four source specs: `character_cue_idle`,
  `character_cue_attack`, `character_cue_hit`, and `character_cue_dead`; they normalize to
  eighteen combat-only frames and fall back as one all-or-nothing unit.
  `character_energy_large` is the distinct 256x256 pool icon, while
  `character_energy_text` belongs exclusively to the 24x24 formatter consumer.
- **Orb generation is icon-only.** Keep the recipe's explicit Frost icon/Spine scene/
  channel-SFX fallbacks; `gen_sprite.py` does not emit a combat scene.
- **Enemy generation is static-body only.** One 360×360 PNG feeds combat and bestiary
  through RitsuLib's `TryCreateCreatureVisuals()` route; keep the explicit fallback scene.
  Supported Character generation is consumer-specific: selection portrait/background,
  top-panel icon, static combat/rest/merchant bodies, five-layer full energy, and the
  large/text Energy split use the exact profiles in `reference/art-contract.md`. Background/rest/
  merchant use bundled raw scene packing without a Godot/MegaDot prerequisite. RitsuLib's
  `CharacterAssetProfile` accepts the static Shop wrapper without a merchant prefix.
  Full energy generates only the Character-specific layer 1 once; layers 2-5 are installed
  from the committed `reference/energy_template/layer_2.png` through `layer_5.png` templates
  and are not generation targets. Generated-mod authors do not manually install or run PckPacker; the character template
  declares it and `build.py` owns both package paths.
  Locked/map consumers need headed proof. Keep their fallback getters. Event raster
  support includes only the initial and explicitly authored later-page portraits; it does
  not include custom phobia, custom-layout, or Ancient assets. The separate code-native
  `portrait_halo` profile has no raster generation step.
  Cast, Spine, trails, audio, and all animation beyond the fixed four-cue bundle remain a
  later expansion.
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
