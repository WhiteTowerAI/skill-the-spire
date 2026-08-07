# Surface: card

Everything the pipeline needs for one Card, in one place: the SPEC envelope it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `surface: card`.

Shared declarations that several surfaces use — advanced targeting, stateful mechanics,
interaction contracts, the art plan — stay in `spec.md`. Shared proof machinery stays in
`verify.md`.

## SPEC envelope

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

## Author the element class

**Card** — add `<ModName>Code/Cards/<CardName>.cs` and extend `ModCardTemplate`:

- Pass `cost, CardType, CardRarity, TargetType` to `base(...)`. A card that targets the
  player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions).
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
- If SPEC selects Scry, read `reference/scry-helper.md`, emit its attributed
  `<ModName>Code/Helpers/OpenModScry.cs`, and await `OpenModScry.Execute` from `OnPlay`
  using the real `PlayerChoiceContext`, `Owner`, and a scaling `DynamicVar("Scry", X)`.
  Do not add BaseLib, a global hook/service, or a multiplayer fallback.
- For hand emphasis, keep one native gold/red rule on the Card or append one typed ordered
  ruleset to the existing content-pack builder. Generate fixed colors with
  `RefreshEveryFrame: false`; stop if the condition can change without a normal combat-state
  refresh.

## Self-test driver body

**card** → `InCombat` (`GainEnergy` → spawn into hand → `CardCmd.AutoPlay`);

A **Scry card** selects the focused `CombatPlayer` variant in
`reference/scry-helper.md`: cover zero/empty/short with an automated selector, then
play the real Card and prove the visible `NSimpleCardSelectScreen`, pending play task,
selected/unselected order, normal source result pile, discard history, and one known
`AfterCardDiscarded` effect. Keep the whole matrix in one headed run and retain the
singleplayer assertion.
A **calculated-value Card** uses the focused matrix in
`reference/card-computed-values.md`: cover Damage/Block modifiers, zero and changing
Energy/Star icon counts, raw versus amount-given typed Power, base/upgrade display, and
the real hand-Card tooltip. Structured post-state proves behavior; headed observation
separately proves text, icon reflow, and tooltip presentation.

## Proof matrix

- For a Scry Card, follow `reference/scry-helper.md`: require one visible native selector
  and a pending Card play task before
  confirmation, plus zero/empty/short/full cases, exact seen/discarded/unselected order,
  source result pile, one history/hook dispatch per discarded Card, and an explicit
  singleplayer restriction. Do not require another headed run after this combined proof.

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
