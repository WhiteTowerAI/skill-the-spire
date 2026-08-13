# Surface: card

Everything the pipeline needs for one Card, in one place: the SPEC fields it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `surface: card`.

Shared declarations that several surfaces use — advanced targeting, stateful mechanics,
interaction contracts, the art plan — stay in `spec.md`. Shared proof machinery stays in
`verify.md`.


## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: card
  - logical id: <stable local stem, e.g. blade_dance>
  - kind: Attack | Skill | Power
  - rarity: Basic | Common | Uncommon | Rare
  - relations: <none | custom power/keyword/enchantment/orb dependencies>
  - keywords: none | <keyword name> — <the shared rule its tooltip states>
    native or mod: native | mod
    behavior owner: <the element that implements the rule>
  - enchantment: none | <name> — <what it adds to this card>
    amount: <value and bounds>
    host restriction: <which cards may legally carry it>
    stacking: replaces an existing enchantment | not stackable
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language card-pool rule>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<hover text>; optional selection prompt
  - formatting: dynamic value placeholders; plain | bounded vanilla rich text
  - text spans: <description phrase -> semantic color intent>
  - variable tooltips: none | <value name -> localized title; description; optional icon>
  - engine-composed text: none | <each native keyword, mod keyword, or enchantment
    `extraCardText` the engine appends to this card's rendered description>
- **effects**:
  - trigger: play
  - target: one enemy | all enemies | self
  - advanced target: none | use the shared declaration below
  - native costs:
    - energy: fixed <nonnegative integer> | X
      upgrade: same | fixed delta <integer>
    - stars: none | fixed <nonnegative integer> | X
      upgrade: same | fixed delta <integer>
    - payment/UI: native
    - combined X replay: game-unobserved
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named base values, e.g. damage 6; block 5; strength 2>
  - upgrade: <named value deltas, e.g. damage +3>
  - calculated values: none | one or more
    - <name>: role <plain | damage | block | Energy icons | Star icons | raw typed Power |
      applied typed Power>; formula <one deterministic expression>; inputs <complete list>;
      domain <integer [min,max]>; upgrade <same | exact change>; evaluation <before play |
      after normal payment and move>
- **hook participation**: none | one or more; see § Hook participation in `spec.md`
  - A Card reaches the widest set (66 of 68), but **which** it reaches depends on where it is:
    a deck Card always receives run-scope hooks, and it receives combat-scope hooks only while
    it sits in a combat pile. So a rule meant to hold all combat long must not live on a Card
    that leaves the piles. `Owner` is a `Player`; guard against `Owner.Creature` and
    `Owner.Osty` where an Osty can act. This is separate from `effects`: participation applies
    while the Card is held or in the deck, not when it is played.
- **state**: none | see the stateful-mechanic contract below
- **owned Rest Site option**: none | one
  - owner: card
  - owner multiplicity: exactly one in the owner's deck
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when this exact Card contributes the option>
  - repeatability: once per Rest Site | once per run
  - state handle: host visit removal | saved owner bool
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic preflightable operations>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: singleplayer only
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
    preview vs effect result, icon reflow, and variable tooltip; or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

## Author the element class

**Card** — add `<ModName>Code/Cards/<CardName>.cs` and extend `ModCardTemplate`:

- Pass `cost, CardType, CardRarity, TargetType` to `base(...)`. A card that targets the
  player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions).
- Lower Energy and Star declarations through `recipes/card.md` § Native Energy and Star
  costs. Fixed Stars override `CanonicalStarCost`; Star-X overrides `HasStarCostX`; fixed
  upgrades use `UpgradeStarCostBy`. Reject simultaneous Energy-X and Star-X, and never add
  a parallel Star store or manual `OnPlay` payment.
- For an advanced target, pass the registered value from
  `reference/advanced-targeting.md`. A single Card uses `cardPlay.Target`; a multi Card
  gates zero candidates through `IsPlayable`, executes once with `null`, and resolves the
  live creature list with `GetTargets()` inside `OnPlay`.
- Add exactly one `.Card<TPool,TCard>()` step to `MainFile.Content.cs`; use
  `ColorlessCardPool` unless SPEC selects a character pool. Do not add a pool attribute.
- Declare static scaling numbers in `CanonicalVars`
  (`DamageVar`/`BlockVar`/`PowerVar<T>`), never literals; bump them in `OnUpgrade()`.
  For a SPEC calculated value, instead follow `reference/card-computed-values.md`: emit
  one pure bounded helper, select the matching computed variable role, account for upgrade
  preview and play-transition timing, and execute through the matching `Compute*Value`
  extension. `PreviewValue` remains display-only and `BaseValue` is not a computed result.
- Fill **only** the `OnPlay` effect block with the recipe's confirmed Cmds
  (`DamageCmd.Attack(...).FromCard(this).Targeting(...).Execute(...)`, `CreatureCmd.GainBlock`
  with the `cardPlay` overload, `PowerCmd.Apply<T>`). Null-check `cardPlay.Target` on a
  targeted card. `await` every Cmd. If a custom power is needed, author it first
  (`recipes/power.md`) and register it once through `.Power<T>()`.
- For hand emphasis, keep one native gold/red rule on the Card or append one typed ordered
  ruleset to the existing content-pack builder. Generate fixed colors with
  `RefreshEveryFrame: false`; stop if the condition can change without a normal combat-state
  refresh.
- For a Card-owned Rest Site action, follow `reference/rest-site-options.md`. Require exactly
  one matching concrete Card in the owner's deck, keep that instance as option/state owner,
  contribute through `TryModifyRestSiteOptions`, and use `SavedAttachedState<SpecificCard,bool>`
  only for once-per-run state. Do not use canonical Cards, duplicate ids, or raw hook
  participation to bypass the transaction and host lifecycle.

## Self-test driver body

**card** → `InCombat` (`GainEnergy` → spawn into hand → `CardCmd.AutoPlay`);

A **calculated-value Card** uses the focused matrix in
`reference/card-computed-values.md`: cover Damage/Block modifiers, zero and changing
Energy/Star icon counts, raw versus amount-given typed Power, base/upgrade display, and
the real hand-Card tooltip. Structured post-state proves behavior; headed observation
separately proves text, icon reflow, and tooltip presentation.

## Proof matrix

- **For the Card play effect — assert the expected result pile.** Drive the real Card through
  its normal play lifecycle and verify that it reaches the SPEC-selected result pile after
  its awaited effects complete.
- **For a selected native Star cost — use the native play lifecycle.** Assert the rendered
  Energy/Star costs, a successful payment and effect exactly once, and an unaffordable
  rejection with Energy, Stars, Card state, and payoff unchanged. For X, include the
  selected captured-X/replay boundary; do not infer other combinations from this case.
- **For a Card-owned Rest Site option — assert exact owner identity and multiplicity.** The
  option is absent with zero or duplicate matching Cards, present for exactly one, and then
  follows the shared native-room matrix for disabled/enabled, stale click rejection,
  deterministic success, repeatability, stay/leave, and icon fallback. This route is
  authorable but game-unobserved until that concrete generated Mod runs it.
- **For hook participation — assert the neutral case outside the guard.** Play assertions
  observe none of it, since participation is not the Card's play effect. Assert the modified
  value through the real path, then drive one event the guard should ignore and assert it is
  unchanged. When the declaration needs combat scope, assert it from a combat pile rather than
  from the deck: a deck Card outside the piles receives no combat hook, so the same declaration
  silently does nothing. For a collection edit, also assert an unrelated entry survives.
### Gameplay-readability headed acceptance

For Card hand emphasis, read `reference/card-hand-emphasis.md`. Put the real Card in hand
and drive no-active, activation, deactivation, conflict winner, unplayable show/hide,
hover/drag, and hand enter/leave states. Confirm that cost, art, rules text, rarity,
selection, and native playable feedback remain readable.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **card:** `card <PREFIX>-<SLUG>` spawns into **hand** (**no `add`**, **exact** match;
     run in progress, hand not full).

Trigger it:

   **card** → play it (target an enemy for an attack; `energy 3` first for headroom);
