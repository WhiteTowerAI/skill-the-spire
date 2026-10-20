# Surface: character (Character Foundation)

Everything the pipeline needs for one playable Character, in one place: the SPEC fields it
must declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `element: character`.

One selectable character shell plus its starter ecosystem; scenarios are `RunStart` +
`CombatPlayer`. Selected advanced capabilities — capability module, character resource,
ordered semantic buffer — keep their separate contracts in this same page, below the
Foundation SPEC. The Foundation proof matrix owns the complete verification contract.


## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown character name>
  - surface: character
  - logical id: <stable character stem>
  - starting HP: <positive int; native 66–80 is an analogy, see `design/character-foundation.md`>
  - starting Gold: <nonnegative int; native 99 is the default analogy>
  - max energy: <positive int; native 3 is the default analogy>
  - base Orb slots: <nonnegative int; native values are analogies>
  - description: <short identity/theme>
  - pronouns: <subject/object/possessive adjective/possessive pronoun>
- **registration**:
  - availability: character-scoped card/relic/potion pools
  - ownership: player
  - placement: character select screen
- **localization**:
  - languages: [eng, zhs]
  - fields: character name, description, and pronouns (in `characters.json`); all pool Card
    and Power titles/descriptions; all Ancient dialogue lines
  - table intent: `characters.json` plus element-specific tables
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); description is two
    short lines joined by `\n`; Cards and Powers follow their own surface rows
- **effects**:
  - trigger: run start
  - target: player
  - starter deck: <exact Basic-card multiset, base effects, upgrades, and total count>
  - starter deck rationale: <how its first-run decisions teach the core mechanic>
  - starter relic: <exact Starter relic>
  - starter potions: <exact potion multiset, including empty>
  - Orobas upgrades: none | <Archaic Tooth: starter Card -> Ancient Card>; <Touch of Orobas:
    starter Relic -> refined Starter Relic> (`recipes/character.md`; without them Archaic Tooth
    is never offered and Touch of Orobas gives Circlet)
  - hosted mechanic: <one starter card/relic grounded public mechanic with exact numbers>
  - pool cards: <every non-Basic pool card, each with its exact effect and numbers; each one
    with a non-trivial mechanic also needs its own `surfaces/card.md` envelope>
  - scaling: <named values for each pool card or hosted mechanic, or none>
- **state**:
  - lifetime: run
  - owner: player
  - advance/check: pools and starter state initialized at RunStart
  - reset: run end
  - persistence: ordinary
  - visible state: character select button/background, HP, energy display
- **presentation**:
  - assets: placeholder | generate (Character static profiles and optional combat cues;
    list each consumer and acquisition count)
  - art source: host-tool | backend:<name> | local-image (generate only)
  - character art tier: minimal | standard | full (generate only; see `interview.md` step 4)
  - native presentation: character select screen + combat UI
  - character art bundle: one `CharacterArtBundle` row per selected slot; record
    required/optional, output path, dimensions, alpha policy, fallback, and real consumer
  - character identity route: selection portrait is the sole identity bootstrap;
    combat/rest/merchant use identity + type-matched style; the combat cue sheet uses the
    approved combat body as its anchor + combat style;
    background/icon/Energy use palette/motif brief + type-matched style only
  - palette/motif brief: concise colors, motif, material, and silhouette derived from
    the user's description and reviewed selection portrait; never a second canonical image
  - character theme contract:
    - name color: `<RRGGBB>`
    - energy-label outline: `<RRGGBB>` (outline of the combat "3/3"; never a free pick:
      use the color `character_art.py` reports for the counter, see below)
    - deck-entry color: `<RRGGBB>`
    - energy outline: `<RRGGBB>` (outline of the card cost and the counter's edge ring;
      derived from the large Energy icon with `--energy-colors <frame>,auto`)
    - card-frame target RGB: `<0..1, 0..1, 0..1>`
    - card-frame brightness: `<0..2>`
    - energy-icon palette: `<primary/accent/outline colors plus motif/material>`
    - full Energy counter: rendered from the card-frame target RGB and energy outline
      (`character_art.py --energy-colors`); no generation call
    - energy resource prefix: `<stable Mod-owned lookup key; never a palette name>`
    - placeholder Energy fallback: Ironclad counter, large Card icon, and rich-text icon
  - character art profiles: none | selection | locked selection | top-panel icon |
    map marker | select background | combat body | rest body | merchant body | energy |
    large energy icon | text energy icon (do not infer one profile from another; mark
    unsupported consumers as explicit gaps per `reference/character-presentation.md`)
  - character combat cues: none | fixed bounded bundle
    - actions: Idle `4 x 250ms, loop` (the anchor breathing); Attack `9 x 60ms, one-shot ->
      Idle`; Hit `6 x 70ms, one-shot -> Idle`; Dead `5 x 170ms, terminal final frame`
    - acquisition: one 2048x2048 sheet (shared anchor + 6 Attack + 4 Hit + 5 Dead poses),
      one call, after the body sheet;
      the normalized `charui/combat.png` as anchor reference; a route that cannot return
      2K keeps the static body (1K frames were rejected as too blurry)
    - poses: <signature item, attack wind-up and strike, in the SPEC's words>
    - continuity lock: same identity, costume, proportions, equipment, handedness, facing,
      camera, apparent scale, and baseline in every cell
    - frame motion: one concrete, distinct pose per cell; Attack/Hit start on the shared
      anchor, Hit recovers through Attack's recovery, holds repeat a cell; Dead lowers the
      full-size body to the ground
    - attack timing: `AttackAnimDelay` `0.30f` (strike at frame 5 x 60ms), so damage lands
      on the strike
    - geometry: shared 512x512 content box/baseline/style and Bounds/Intent/Center/Orb/Talk anchors
    - fallback: one missing or invalid frame disables all cues and uses static combat body
    - explicit gaps: Cast, Spine, trails, audio, animated merchant/rest bodies
- **fallback**:
  - missing asset: Foundation-only template; selected profiles fill only their matched fields;
    Energy uses `ironclad_energy_counter.tscn`, `EnergyIconHelper.GetPath("ironclad")`
    (`energy_ironclad.tres`), and
    `res://images/packed/sprite_fonts/ironclad_energy_icon.png`, never a theme-derived path
  - unavailable seam: preserve Foundation behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: RunStart + CombatPlayer
  - driver: locate the real custom character-select button, click it, then assert runtime state
  - invariants:
    - the character is registered exactly once and appears in character selection
    - real character-select button present and clicked
    - runtime identity, HP, three pool types/members, exact deck/relic multisets
    - combat `MaxEnergy` and base Orb slots equal current SPEC plus the hosted mechanic's
      independent state delta
    - every pool card whose mechanic SPEC describes behaviorally is played and asserted
  - boundary cases: Shop-pool card slot fill; art consumer assertions when profiles are selected
- **advanced mechanic**: none | <maintained route or Mod-local route>
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
- **native design basis**:
  - grammar profile: `design/character-foundation.md @ STS2 0.107.1`
  - pinned facts used: <exact native identities/values used in the proposal>
  - observed convention: <native shape used as the recommendation>
  - creative decision: <exact selected deck shape and teaching intent>
- **deliberate native departure**: none | <departure plus onboarding, compatibility, and
  balance consequences accepted by the user>
- **adapter output** (written to MEMORY after acceptance): character logical id, every
  starter content logical id and localization fields, flat Ancient dialogue keys and
  zero-based visit metadata from the semantic groups, and framework diagnostic record
```

Do not add a manual registration line or invent a nonstandard energy override. The maintained
routes for an `advanced mechanic` are `reference/character-resource.md` and
`reference/ordered-card-buffer.md`. If neither can express the mechanic, implement it as a
Mod-local route under `../sts2api/grounding.md` § Mod-local Routes.

## Character capability and state routes

Read `reference/model-capabilities.md` only when the Character owns a separable state/display
bundle. A `CharacterCapability` can own typed state, DynamicVars, tips, and supported display
contributions, but Character is not a normal run/combat hook listener; do not claim owner-hook
dispatch. Read `reference/lifecycle-state-rng.md` when Character-owned player/run/profile state
crosses lifecycle, save, or deterministic RNG boundaries.

Append only the selected reference's game-term SPEC block. Keep Card/Relic/Power effects on those
models, preserve exact player/run identity, cleanup and persistence rules, and prove the real
Character consumer plus save/profile host where selected. Do not use these routes to create a
Settings, Progression, Multiplayer, or process-wide effect surface.

## Pool cards are content, not filler

A Foundation needs enough unlocked non-Basic cards to fill the merchant's colored slots, so
the natural failure is to treat them as inventory that only has to *exist*. Pool membership is
what the Foundation proof asserts, and membership is satisfied by a card whose behavior is
entirely broken.

Declare every pool card's effect in `pool cards`. Any pool card carrying a real mechanic —
anything beyond a plain damage or block number — also gets its own `surfaces/card.md` envelope
and owes that surface's proof. A Foundation whose signature mechanic lives in a pool card has
not been verified until that card has been played.

## Author the element class

**Character Foundation** - use the pinned scaffold and `recipes/character.md`:

- Fill `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` with every required public
  abstract member. Extend the three public `TypeList*PoolModel` bases.
- Register the Character, exact Card/Relic/Potion starter multisets, every concrete pool member,
  and every supporting Power once through one content pack. Do not instantiate the
  character, add pool attributes, or add a second registration path.
- If Shop/static merchant is selected, author enough unlocked non-Basic cards to provide
  at least two Attacks, two Skills, and one Power after filters; the native merchant fills
  those exact slots and otherwise throws before its UI appears. Author each one through
  `surfaces/card.md`, not as a bare pool entry. Do not add a static-merchant
  patch; the RitsuLib Shop profile needs none.
- Add all 14 normalized `characters.json` values and a complete repeating Architect
  dialogue. When SPEC selects other Ancient targets or richer Architect groups, lower the
  semantic blocks through `reference/ancient-dialogue.md`; do not author an injection patch.
- Keep `CharacterAssetProfile` partial fallback semantics; selected Character static
  profiles fill only the matching fields after headed proof. Set the placeholder Character to
  `ironclad`, and keep a stable Mod-owned `EnergyColorName` prefix for custom resource mapping;
  never use a palette name such as `red` as the prefix or fallback. When combat cues are selected,
  read `reference/character-combat-cues.md` and emit only its private combat-owned
  Idle/Attack/Hit/Dead state machine; never fill profile-global `VisualCues`. A
  Foundation-only SPEC emits no patch infrastructure. A resource SPEC
  registers one `SecondaryResourceDefinition`, uses `SecondaryResourceCmd` for amount and
  all-or-nothing payment, and mounts the fixed control through public `RegisterCombatUi`.
  An ordered-buffer SPEC uses `AttachedState<PlayerCombatState,TState>`, native source-card
  result piles, visible state text, and one configured output card. Never emit a retained-
  card `CustomPile` without a separately grounded UI lifecycle. Keep proof-only observers
  and assertions out of generated gameplay.

Ancient dialogue text may use the engine's `{character}` and pronoun tokens. Prefer them over
a hardcoded character name in any line that refers to the Character, so shipped non-English
dialogue keeps grammatical agreement.

## Self-test driver body

**character** → the **`RunStart` + `CombatPlayer`** variant: set
`plan.Character<TCharacter>()`, so the kit selects the real character-select button by model
type, confirms it, and waits for the run UI and local Player; then assert runtime identity in a
`plan.RunStart` scenario, which runs before any combat. The focused body is in
`reference/selftest-harness.md` § The `RunStart` + `CombatPlayer` scenario.

Assert runtime HP/Gold/pools/starter multisets there (`t.DeckCounts()`, `t.RelicNames()`).
Give the starter Cards face checks. Enter combat, then assert
designed `MaxEnergy` and the starter mechanic's independent state delta. When those profiles
are selected, also enter the real RestSite and Shop hosts and assert background/rest/merchant/
full-energy resources through `CharacterAssetProfile`. Never select the first unlocked vanilla
character.

## Proof matrix

The final proof is valid only after the harness has asserted exactly one content-pack-
registered model, the real selected/unlocked button, runtime identity and exact SPEC HP/Max HP,
exact typed Card/Relic/Potion pools and member models, every independently registered
supporting Power, exact starter deck/relic/potion multisets, and SPEC StartingGold, MaxEnergy,
and BaseOrbSlotCount. The unlocked Card
pool must also fill Shop's native colored Attack, Skill, and Power slots without falling back
to another character's pool.

- Derive every expected identity, count, value, and terminal summary from the current
  `SPEC.md`; never reuse a retired proof Mod's constants or marker.
- Assert the hosted mechanic's independent state delta.
- **Play every behavioral pool card.** Pool assertions prove membership, not `OnPlay`: a
  Foundation whose pool cards are entirely broken passes as long as the right models appear in
  the right multisets. For each pool card with its own `surfaces/card.md` envelope, drive it
  and assert its concrete state delta in the same run.
- For secondary resources, derive only the definitions, uses, policies, and UI consumers
  selected by current SPEC. Require bounded gain/payment, authoritative committed payoff,
  rejected nondestructive cases, live values, public UI attachment, and non-overlapping stable
  geometry for every selected visible consumer. Exercise a second combat or run-save boundary
  only when the selected persistence/turn-start policy requires it.
- For an ordered semantic buffer/dynamic output, require exact source/compile-card result
  piles, visible order, capacity and overflow behavior, one generated-history entry, exact
  configured output/effect, `AttachedState` ownership, and a distinct empty state/UI in
  combat 2. Reject retained-card, hidden-zone, and `skipVisuals` substitutions.
- The Character-wide theme contract asserts all four colors, shader parameters, distinct
  paths, exact 256x256/24x24 textures, and both real consumers before it emits the theme
  marker.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **character:** select the custom character on the real character screen and click
     Confirm; there is no console shortcut that proves character-select presence.

Trigger it:

   **character** → confirm SPEC HP, Gold, Energy, Orb slots, and starter deck/relic/potions after run start;
   enter combat and observe the named starter mechanic's exact state delta. When combat
   cues are selected, watch one full Idle loop, play an Attack, take one Hit, and reach Dead;
   confirm the first two return to Idle, Dead holds its last pose, and no anchor jumps.

## Advanced capability capability sections

When `advanced mechanic` is not `none`, also record the matching block from this section.
Author it only when the named semantic capability has its own recipe in the shipped pack.
The current implemented public framework routes are exactly `reference/character-resource.md`
and `reference/ordered-card-buffer.md`. If neither can express the mechanic, mark it
unsupported and name the gap; these fields never imply non-public access or a
patch target.

### Capability module

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

### Secondary resources

The adapter lowers the selected secondary-resource fields to one or more framework-owned
bounded resources, exact combat/run and turn-start policies, declared payment planner/commit
uses, and selected built-in or explicit UI consumers. Implementation records belong in
`MEMORY.md`, not SPEC.

```markdown
- **resources**: <stable id, min/default/max, combat|run persistence, turn-start policy>
- **uses**: <stable use id, Card, resource, required|optional|repeatable-extra,
  fixed|X amount, shortfall, replacement resource when selected, post-commit payoff>
- **UI consumers**: <resource, combat counter row|Card payment line, route, stable geometry>
- **owner**: local Player; native Energy remains separate
- **adapter route**: public registry/commands/payment planner selected after SPEC
- **observe**: only selected definitions, uses, rejection/commit, bounds, lifecycle, and UI
```

### Ordered semantic buffer

The adapter lowers this block to combat-attached semantic state. Implementation records
belong in `MEMORY.md`, not SPEC.

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
