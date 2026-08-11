# Spec 鈥?write the design contract

Goal: lower the accepted current slice in `DESIGN.md` into exact `SPEC.md` operations in the
work dir. This is the generation contract every later stage reads. Also seed `PLAN.md`
(stage checklist) and `MEMORY.md`. For revision, change only the confirmed delta; unrelated
design IDs and semantic operations carry over under `INV-6`.

Read `DESIGN.md` first, then `semantic-contract.md`. Every SPEC must include
the `sts2-content-semantic/v2` envelope from that file. The blocks below collect
surface-specific inputs; they are semantic data, not implementation recipes. Do not
write framework class names, namespaces, hook signatures, pool attributes, project
references, manifest fields, or resource paths in the user-facing SPEC. The selected
adapter records those details in `MEMORY.md` after the SPEC is frozen.

## Lower accepted design state

The `design.md` stage owns the durable `DESIGN.md`: the deliverable claim and its required/
excluded player experiences, current/future slicing, design-to-SPEC traceability, accepted
identity anchors, selected surface checks, resolved coherence state, and the revision
impact/re-evaluation queue. Before lowering, run:

```powershell
python ${GAME_TOOLS_DIR}/coherence_trace.py --design DESIGN.md
python ${GAME_TOOLS_DIR}/deliverable_trace.py --design DESIGN.md
```

Do not write or update SPEC while a coherence conflict remains. Coherence rationale,
anchors, deliberate tensions, and queue entries stay in DESIGN; lower only an accepted
current decision that actually changes generated semantics or presentation.

Lower only user-accepted, supported, exact current behavior from `current_slice`:

- put selected rules, edge behavior, formulas, values, timing, caps, resets, and tuning
  values into the owning surface's semantic fields;
- put accepted real content nodes into their normal surface blocks and directed
  source-to-dependent relationships into `interactions`;
- preserve exact constraints and accepted working assumptions that implementation must
  obey; and
- keep unsupported operations in `gaps` and stop before silently substituting another
  behavior.

Do not dump player fantasy, alternatives, rationale, role-analysis prose, sensitivity
discussion, dominance review, future vision, or evidence claims into `SPEC.md`. If an open
hypothesis would change current generated behavior, such as an unknown payment rule, reset,
formula input, or selected value, pause before freezing SPEC. A playtest-only balance
hypothesis may remain explicitly unproven after its generous working value has been accepted;
what it may never become is a SPEC fact (`INV-4`).

Do not write SPEC while `blocking_gaps` is nonempty. `DEFER` and `OUT-OF-SCOPE` items map to
no operation and never appear as empty stubs, comments promising future code, or generated
fallback behavior.

## Write the design trace

Define one operation for each independently emitted semantic behavior, data change,
availability change, content registration, presentation route, or explicit placeholder/
fallback. Closely coupled fields lowered by one recipe may share an operation when they
cannot be independently omitted or changed. Explanatory rationale and proof expectations
are not generated operations.

Every operation uses one stable `OP-###` already listed by one or more current `D-###` items and
names a shipped semantic recipe/reference as its supported route. This is a product route,
not an API class or guessed patch target.

Place exactly one marked JSON block near the top of SPEC:

<!-- open-mod-trace:v1:start -->
```json
{
  "contract": "open-mod-spec-trace/v1",
  "design_contract": "open-mod-design/v1",
  "operations": [
    {
      "operation_id": "OP-001",
      "design_ids": ["D-001"],
      "semantic_target": "Card Ember Step: registration and exact play effect",
      "supported_route": "recipes/card.md"
    },
    {
      "operation_id": "OP-002",
      "design_ids": ["D-002"],
      "semantic_target": "Card portrait uses the checked placeholder fallback",
      "supported_route": "reference/art-contract.md#path-root"
    }
  ]
}
```
<!-- open-mod-trace:v1:end -->

The operation ledger is the generation allowlist. Every detailed surface block below must
belong to one listed operation, and Author must emit nothing outside it. After writing both
artifacts, run both validators (coherence first so a structurally valid SPEC cannot hide an
unresolved design conflict):

```powershell
python ${GAME_TOOLS_DIR}/coherence_trace.py --design DESIGN.md
python ${GAME_TOOLS_DIR}/deliverable_trace.py --design DESIGN.md
python ${GAME_TOOLS_DIR}/design_trace.py --design DESIGN.md --spec SPEC.md
python ${GAME_TOOLS_DIR}/spec_envelope_trace.py --spec SPEC.md
```

`spec_envelope_trace.py` checks the SPEC you just wrote against the envelope its own
`surface:` line claims: every shared section present, no invented top-level key, and the
`sts2-content-semantic/v2` contract line. It reads the allowed keys from
`surfaces/<element>.md`, so the page and the check cannot disagree. A pre-v2 project passes
through unchanged.

Stop before confirmation or scaffold on any validation error. Fix the artifact that owns
the mismatch; never delete a future requirement or invent a supported route to make the
validator green.

Every required experience must be reachable by the operations you just wrote. If an `E-###`
has no operation that could make it true, the claim is promising something this slice does
not build: either the operation is missing from SPEC, or the experience belongs in
`excluded_experiences`. Resolve it in `DESIGN.md` and revalidate — do not quietly drop the
experience, and do not add an operation the user never accepted.

For revision, update only operations named by confirmed UPDATE/REVIEW queue outcomes.
PRESERVE entries never become SPEC operations. Reopen Author/Build/Verify only when the
queue says their generated output or observed invariant changed.

> **Work dir = the dedicated outer folder created by `design.md`, whose name is NOT
> `<ModName>`** (e.g. `<modname>-mod`). Write SPEC, PLAN, and MEMORY beside DESIGN;
> `scaffold.md`
> then `cd`s into it and runs `dotnet new` (the template scatters into CWD and makes
> a `<ModName>/` resource subdir, so the outer name must differ 鈥?see scaffold.md
> step 1). Do **not** name the work dir `<ModName>`.

## Write `SPEC.md`

Use the block for the element type. **Existing vanilla model override:**

```markdown
# SPEC - <Mod Name>

- **contract**: sts2-content-semantic/v2
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
- **non-Card behavior** (only for promoted non-Card data/behavior operations):
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

For availability, record one exact target and one ordered operation per requested
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

For non-Card data and behavior, read `reference/vanilla-non-card-overrides.md`. Record public owner-hook
composition in game terms with exact trigger/scope/condition/order/result. Record intrinsic
data as a final enum/boolean/integer or integer delta. A complete lifecycle/body replacement
must freeze every callback field, Monster state and edge, Encounter monster/slot entry, or
ordinary Event option/reachable page in the selected surface. Ordinary Event text uses
Mod-local `<MOD_ID>_EVENT_*` keys in every shipped `events.json`; Ancient targets stay on
the existing-Ancient routes. All non-Card data/behavior operations remain singleplayer. Do not turn missing event context,
undeclared capability state, synchronous Affliction effects, multiplayer, or another
uncataloged body into generated patch code.

### Engine-composed text is not author-written text (all surfaces)

The engine and the framework compose part of what the player reads. Two obligations follow,
and they apply to every surface below:

1. **Do not hand-write text the engine appends.** A self-exhausting Card must not put
   "Exhaust" in its description — `CardKeywordOrder` adds the keyword text automatically, and
   vanilla `Impervious`/`Offering` carry none of it in their own descriptions. The same holds
   for a mod keyword attached to a card, and for an enchantment's `extraCardText` and folded
   Hover Tip. Writing it again shows the player the same rule twice.
2. **Do not hand-write a value the engine substitutes.** Declare the number once as a scaling
   value and reference it as a placeholder. Relic and Potion descriptions run
   SmartFormat/DynamicVar substitution; an Orb resolves `{Passive}`/`{Evoke}` only under
   `smartDescription`; a Power resolves `{Amount}`; an Event substitutes its `DynamicVars`
   into option titles, option descriptions, and page descriptions. A literal is acceptable
   only when the value can never change and appears in exactly one place.

A Monster's intent label is the strict case of both: the engine computes it from the move's
real damage with live Weak, Vulnerable, and Strength applied. Pass the base number to the
intent constructor and never write intent text, or it desyncs from the real hit.

Each surface page states its own instance of this rule and which of its fields records the
decision. A Card additionally declares the composed tokens it expects in
`localization.engine-composed text`, so "declared, therefore not re-authored" is checkable
rather than conventional.

**Relic:** its envelope, element class, and proof matrix live together in
`surfaces/relic.md`. Read that page for `surface: relic`. The Rest Site option block a Relic
owner adds to its own SPEC lives there too; the current slice does not accept a Card or
Modifier owner.

**Potion** (usage/target replace trigger; loc table is `potions`, no flavor, plus an
optional `selectionScreenPrompt`; art is a loose 256脳256 PNG icon, like relic/power): its
envelope, element class, and proof matrix live together in `surfaces/potion.md`.

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
its envelope, element class, and proof matrix live together in `surfaces/card.md`. Read
that page for `surface: card`.

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
for every authored custom Power): its envelope, element class, and proof matrix live
together in `surfaces/power.md`.

Hand emphasis and extra badges are product semantics, not styling escape hatches. Record
why the player needs the signal and the game-state rule that owns it; never record RitsuLib
interfaces, predicates, `Color` objects, raw markup, rectangles, or invalidation event names
in SPEC. Hand rules remain in declared order; the highest active priority wins and a tie is
resolved by the later listed rule. Relics use at most three distinct safe corners; Powers
use at most one top-left label because their preset label bands overlap in crowded rows.
Every extra badge supplements the native Relic/Power main amount instead of replacing it. Intent belongs to
the public Extra Badges Package and remains supported there, but it has no generated SPEC
block because no authoring recipe exists for it yet.

**Custom orb** (real content with its own identity and slot lifecycle, but no trigger of its
own — channel, passive, and evoke all run through a host Card, relic, or Power): its envelope,
element class, and proof matrix live together in `surfaces/orb.md`.

**Custom keyword** and **card enchantment** have no element block of their own. A keyword owns
shared vocabulary whose named behavior lives in a host; an enchantment is always attached to a
host Card. Both are declared as nested blocks inside their host Card's `content:` section, and
their envelope fields, element classes, and proof matrices live together in
`surfaces/keyword.md` and `surfaces/enchantment.md`.

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

### Hook participation (all surfaces that can receive hooks)

Add this block when an element changes a number or a decision the host is computing for
something else, rather than acting at a trigger of its own. "At the start of my turn, gain 3
Block" is a trigger and belongs in `effects`. "While I am attached, damage my owner receives is
doubled" is hook participation: nothing fires, and the engine consults the element while
resolving someone else's attack.

Keep the distinction, because the second kind is what the pipeline used to lose. Stated as prose
inside an effect sequence, a multiplier has no field to be declared in, nothing downstream can
check it, and a generated method with an empty body passes every local stage. Each field below
exists because its absence is a way that happens.

```markdown
- **hook participation**: none | one or more
  - capability: <semantic hook id from `reference/model-hook-participation.md`>
    shape: value | out-replacement | collection
    player-facing: <the rule exactly as the player would read it>
    subject: <whose value or decision this changes, in game terms>
    condition: <the exact cases it applies to, including which kinds of damage, block,
      or event count as "mine">
    value: <the number or one deterministic formula, with bounds>       # value shapes
    dynamic value name: none | <the name substituted into the rules text>
    outside the condition: <the unchanged result the host receives>
    replaces: yes when <condition>; declines otherwise                  # out-replacement only
    edit: add <entry and its values> | remove <which entries>            # collection only
    other entries: preserved unchanged                                  # collection only
    ordering: base | late - <why this one>                              # collection only
```

Four fields carry most of the weight, and none of them is optional:

- **`subject`** decides direction. The same host question serves "damage I receive" and "damage I
  deal", separated only by whose value the element is guarding. A declaration missing it produces
  an element whose rules text is right and whose behavior is inverted.
- **`condition`** must say which *kinds* count. In STS2, attack damage from a Card or a Monster
  move is a different thing from Poison-style HP loss and from damage dealt by relics, potions,
  and powers. Vanilla Vulnerable multiplies only the first. "Doubles incoming damage" is not yet a
  decision; the design has to choose, and this is the field that records the choice.
- **`outside the condition`** is the value the host gets in every case the element is not for. It
  is not boilerplate: an element that returns its modifier unconditionally changes every unrelated
  interaction in the run while passing an assertion that its own case works.
- **`dynamic value name`** is how the number in the rules text stays the same number as the
  behavior. Declare it once and let substitution place it; two literals will disagree after the
  first balance change.

`capability` and `shape` are the pairing keys, so they are the one place a semantic id belongs in
SPEC. Copy the id verbatim from the route page — the validator rejects an id no route declares, a
shape the catalog contradicts, and a hook the declaring surface cannot receive. Everything else in
the block stays in game terms; no method signature, parameter name, or type belongs here.

Repeat the `OP-###` in the generation trace with `capability_ids` naming the same ids, and cite
`reference/model-hook-participation.md` as its supported route.

**Two participations are not free-standing.** Rest Site option contribution and its stay/leave
behavior route through `reference/rest-site-options.md` instead, which owns four boundaries the
raw participation does not carry. An **enchantment** uses its own five replacements rather than
the general hooks for damage, block, and play count; `surfaces/enchantment.md` states which.
Composition order across contributors is the engine's, not the element's: every additive
contribution resolves before every multiplicative one. Never declare a combined adjustment that
assumes the element runs alone.

**Enemy encounter** (a monster + the encounter that spawns it 鈥?always authored as one
slice; scenario is `CombatEnemy`, not `CombatPlayer`; loc tables are `monsters` + `encounters`;
generated art is one static body shared by combat and bestiary; animation is later): its
envelope, element classes, and proof matrix live together in `surfaces/monster.md`.

The monster and encounter are **not** modeled as two `elements` + an interaction edge (that
form is for source鈫抎ependent links like card鈫抪ower). They are one indivisible slice with a
single recipe (`recipes/monster.md`) and a single `CombatEnemy` proof. `author.md` dispatches
to that recipe when `element: enemy encounter`. A one-move enemy may keep one self-looping
move. A multi-move enemy must fill the compact move/branch contract in that surface before
authoring. An intent label is not behavior proof (`INV-1`).

**Event / World Node** (one semantic Event with nested pages/options; scenario is
`MapNode`; supported outcomes include blocking selections/rewards and one resumable or
terminal special combat per mutable Event instance; normal portraits and the bounded
`portrait_halo` profile plus bounded vanilla description rich text are supported, while
custom phobia art, arbitrary VFX, and custom/Ancient scenes are not): its envelope, element
class, and proof matrix live together in `surfaces/event.md`.

Each option id is stable semantic input; the adapter derives any method and localization
keys from it. If special combat exists, the spec also owns the custom monster + encounter
dependency from `surfaces/monster.md`; do not leave `<ENCOUNTER>` abstract. The warning cost
must be identical to the later Cmd cost; a relic-backed Event option does not itself grant
the relic.

All six native-presentation families are implemented: cross-content Card/standard-
Hover-Tip rich text; enabled Event option Hover Tips plus normal relic-backed text/metadata
with an explicit image blocker; native exact-lethal HP/Max HP warnings; native Card/relic
acquisition presentation; bounded `weak_short` screen shake; and the curated built-in
`trial_noble` Event VFX. Locked-option tips, normal-layout relic images, and positioned
Event speech/thought bubbles remain explicit gaps.

**Character Foundation** (one selectable character shell plus its starter ecosystem;
scenarios are `RunStart` + `CombatPlayer`): its envelope, element class, proof matrix, and
all advanced capability sub-envelopes (capability module, character resource, ordered
semantic buffer) live together in `surfaces/character.md`. Read that page for everything
Character; the sub-envelopes have moved there from this file (M8.0 mismatch 7, closed in v2).

`author.md` dispatches `element: character` to `recipes/character.md`. Do not add a
manual registration line or invent a nonstandard energy override. If `advanced mechanic`
is not `none`, also record the capability-module sub-envelope in `surfaces/character.md`.
Author it only when the named semantic capability has its own recipe in the shipped pack;
the current implemented public framework routes are exactly
`reference/character-resource.md` and `reference/ordered-card-buffer.md`.

Retained-card zone UI is unsupported. If the user requires real played-card instances to
remain in a custom zone, preserve that idea as a gap (`INV-3`). A no-UI `CustomPile` is the
visible substitute to refuse (`INV-5`).

**Multi-element contract** (add only when the mod contains more than one authored element;
omit it for the single-element fast path). `elements` are real content nodes. `interactions`
are directed relationships between them 鈥?never use `combo` as an element type.

Each interaction records the source driver, relationship, dependent, scenario, and the
independent observations that prove the link rather than merely proving both nodes loaded:

```markdown
- **elements**:
  - name: <SourceElement>
    type: card | relic | potion | power
    id: `<source logical id>`
    design role: <foundation | access | payoff | consistency | defense | scaling | bridge | release, only when accepted>
  - name: <DependentElement>
    type: card | relic | potion | power
    id: `<dependent logical id>`
    design role: <accepted role, only when content-set planning applies>
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
every observation in dependency order. This is the old M5 鈥渃ombo鈥?proof generalized into a
relationship contract; `combo` is not a content model or a user-selectable element.

For a `consumes` edge on a nonnegative Counter (for example, "consume up to N"), add
three boundary observations: zero stacks, fewer than N, and at least N. Each observation
must state the expected remaining amount/removal and assert that no instance with
`Amount < 0` appears. These become required self-test cases, not prose-only edge cases.

**Freeze logical ids now**, then let the selected adapter derive concrete content and
localization keys. The semantic contract must not depend on a namespace or framework
prefix. Record the resolved keys in `MEMORY.md` after adapter selection and verify them
through the nearest hosted suite.

## Art plan (one mod-level choice 鈥?the 搂7.1 decision)

The mod gets **one** art decision, taken from the interview (asked at most once, never
per sprite): **placeholder** (the default 鈥?do nothing, the template's built-in art
shows; keeps the loop fast and the mod immediately testable) or **generate** (produce
custom sprites via `author.md`'s art step). Record it in `SPEC.md`'s `**art**` line,
plus the selected `**art source**` and one overall subject/style note if `generate`, so
`author.md` can build each prompt. When the mod has several cards, `author.md` fills the
per-card subject from each card's SPEC at generate time 鈥?but the placeholder-vs-generate
choice was made once, for the whole mod.

Rules for this round:

- **Placeholder is the default and needs no backend, no key, no dev box.** If the user
  didn't ask for custom art, leave it placeholder 鈥?this is exactly the current,
  already-verified behavior (no regression).
- **`generate` is wired for eight established static specs 鈥?`card`, `relic`, `power`, `potion`,
  `enchantment`, `orb`, `monster`, `event`** (all live-verified 鈥?card 1000脳760;
  relic/power/potion 256脳256; enchantment 64脳64; orb icon 100脳100; normal event portrait
  slots 3440脳1613; static monster body 360脳360;
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
- **Enemy generation is static-body only.** One 360脳360 PNG feeds combat and bestiary
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
  user explicitly selects another route 鈥?never silently spend through a second backend
  and never block on art.

## Seed `PLAN.md`

```markdown
# PLAN 鈥?<Mod Name>
- [x] route: fast | co-design | revision
- [x] interview
- [x] design
- [x] spec
- [ ] scaffold
- [ ] author
- [ ] art (per SPEC art plan: placeholder = nothing to do; generate = acquire + gen_sprite.py import)
- [ ] build
- [ ] verify (tier-1 load)
- [ ] verify (tier-2 effect, automated via the self-test harness)
- [ ] settle the deliverable claim (one entry per required experience)

## Deliverable settlement

<!-- open-mod-settlement:v1:start -->
```json
{
  "contract": "open-mod-settlement/v1",
  "settlements": []
}
```
<!-- open-mod-settlement:v1:end -->
```

Seed the ledger empty and leave it empty until Finalize. It is the run's record of which
required experiences were actually earned, so an entry written before its evidence exists is
the exact failure the ledger is here to prevent (`INV-1`). `verify.md` § Finalize fills it.

Update the checkboxes as you finish each stage 鈥?this is what state check reads.

## Seed `MEMORY.md`

Start it with the semantic contract and adapter selection record, so implementation
details are derived once and remain resumable:

```markdown
# MEMORY 鈥?<Mod Name>
- design contract: open-mod-design/v1 (creative intent and scope remain in DESIGN.md)
- semantic contract: sts2-content-semantic/v2
- logical ids: <...>
- framework profile: <selected adapter profile>
- adapter: <surface/contract-version>
- resolved content ids: <...>
- resolved localization keys: <...>
- framework diagnostics: <host/framework/compat/status>
- adapter defaults: <technical lowering defaults only; creative decisions stay in DESIGN.md>
- state: <none OR event/threshold/phase/lifetime/reset/persistence + required proofs>
```

## Confirm with the user

Show one **plain-language** DESIGN/current-slice/SPEC summary and get a yes before
scaffolding. Lead with the deliverable claim in one sentence, then **build now**,
**placeholder**, and **later/not included**, omitting empty groups; then use the applicable
compact element summary below. Do not request separate approval for DESIGN and SPEC:

State the claim in the user's terms and name what it does not include, in the same breath.
"You'll have one playable Attack card you can add to a run — placeholder art, no other
content" is the whole point of the claim: the user gets to disagree with the *shape* of the
finished thing now, instead of discovering it at the end. Keep it to a clause or two; the
excluded list is the short version of `excluded_experiences`, not a recital of it.

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
> 3 energy, <exact starter deck summary and why it teaches the mechanic>, and <starter
> relic/effect>. <If applicable: deliberate departure and its accepted player-facing
> consequences.> The first build uses
> character-template placeholders and proves selection, run start, and the starter effect.
> Sound right?

For the **<art line>**, reflect the SPEC art plan: "with placeholder art for now" (the
fast default), or "with custom art I'll generate for the portrait" if they chose
generate for a card. Keep it one clause 鈥?don't turn the confirmation into an art
interview (that already happened in `interview.md` / this stage's art plan).

If they change intent or scope, update `DESIGN.md` first — including the claim and any
affected `E-###` — then regenerate the affected SPEC operations and rerun both
`deliverable_trace.py` and `design_trace.py`. If they change only an exact current value, preserve
the design IDs and update the owning DESIGN decision plus SPEC value before moving on. Then
go to `scaffold.md`.

For revision, show the compact **keep / change / check / re-verify** delta before editing.
After confirmation, update only the affected DESIGN/SPEC fields and reopen only the PLAN
stages invalidated by that delta. A future-vision-only edit does not reopen author/build.
Do not replace unrelated content or restart the intake.
