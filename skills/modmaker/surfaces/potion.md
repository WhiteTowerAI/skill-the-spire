# Surface: potion

Everything the pipeline needs for one Potion, in one place: the SPEC envelope it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `surface: potion`.

Shared declarations that several surfaces use — advanced targeting, interaction contracts,
the art plan — stay in `spec.md`. Shared proof machinery stays in `verify.md`.

## SPEC envelope

Usage/target replace the trigger line; the loc table is `potions`, with no flavor plus an
optional `selectionScreenPrompt`; art is a loose 256×256 PNG icon, like relic/power.

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
  - displayed values: none | <value name -> declared scaling name; literal or placeholder>
  - keyword tips: none | <native or mod keyword named in the description>
- **art**: placeholder | generate (a `potion` icon is a loose 256×256 PNG, generate-wired
  and live-verified — same as relic/power; see `reference/art-contract.md`)
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
- **proof**:
  - scenario: CombatPlayer
  - driver: procure the real Potion, then use it against its declared target
  - invariants: <exact expected/observed state, belt consumption, and dependent effects>
  - boundary cases: <resolved-target, usage-window, and dependent-element cases, or none;
    a Potion has no upgrade>
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - logical id: `<stable local stem>`
  - localization fields: `title`, `description`
  - asset role: potion icon
```

## Displayed values the engine keeps current

`PotionModel` runs the same SmartFormat/DynamicVar substitution as `RelicModel`, so a value
declared in `CanonicalVars` renders live and in native `[blue]` presentation. Vanilla relies
on it: `FirePotion` declares `new DamageVar(20m, ValueProp.Unpowered)` against a localized
`Deal [blue]{Damage}[/blue] damage.`

The default recipe shape puts the number in *two* places — the Cmd call and the localized
string — where they can silently diverge. Prefer one declared scaling name referenced as a
placeholder. A literal is acceptable only when the value can never change and appears in
exactly one place; record the choice in `display.displayed values`.

## Keyword tips are not automatic here

As with Relic, a Potion gets no keyword tooltip from naming a keyword in its description.
`ModPotionTemplate` surfaces tips only through explicitly declared `RegisteredKeywordIds`
and `AdditionalHoverTips`. Declare any keyword the description names, or the player reads a
term with nothing to hover.

## Author the element class

**Potion** — add `<ModName>Code/Potions/<PotionName>.cs` and extend `ModPotionTemplate`:

- Override the three abstract props: `Rarity`, `Usage` (`CombatOnly`/`AnyTime`),
  `TargetType` (self-buff = `AnyPlayer`, not `Self`; one enemy = `AnyEnemy`). These three
  are the SPEC contract, not implementation detail — see § Proof matrix.
- For an advanced `mode: one` target, use the registered value and the single-Potion
  route from `reference/advanced-targeting.md`. `mode: many` is unsupported on the pinned
  profile and must stop authoring.
- Add exactly one `.Potion<SharedPotionPool,TPotion>()` step to `MainFile.Content.cs`.
  Use another pool only when SPEC makes the Potion character-specific; do not add a pool
  attribute or a per-Mod Potion base.
- Fill **only** the `OnUse` effect block with confirmed Cmds (`CreatureCmd.Damage/
  GainBlock/Heal`, `PowerCmd.Apply<T>`, `PlayerCmd.*`), using `ValueProp.Unpowered`
  for damage/block. `await` every Cmd; call `AssertValidForTargetedPotion(target)` first.
- Declare a SPEC displayed value in `CanonicalVars` and reference it as a placeholder in the
  localized text; use a literal only under § Displayed values the engine keeps current.
- Put an optional loose PNG in `PotionAssetProfile`; omit the override for the checked
  placeholder fallback.

## Self-test driver body

**potion** → `InCombat` (`TryToProcure` → `EnqueueManualUse`);

The focused body is in `reference/selftest-harness.md` § potion.

## Proof matrix

- Assert the declared effect's exact expected/observed state.
- **Assert belt consumption.** A Potion is single-use, and the engine owns that:
  `PotionModel.OnUseWrapper` calls `RemoveBeforeUse()` before `OnUse`. The effect delta
  alone passes for a Potion that is never consumed or is silently restored, so assert belt
  membership before/after — or `HasBeenRemovedFromState` — as its own invariant.
- **Assert the declared target, not the implemented one.** The reference driver derives its
  target from `potion.TargetType`, so a `TargetType` contradicting SPEC is unfalsifiable:
  the driver retargets and the effect assertion still passes. Assert that the resolved
  target matches the SPEC `target` line — for `one enemy`, that an enemy took the effect and
  the player did not.
- Assert the declared `usage` when it restricts availability. `EnqueueManualUse` is driven
  directly from `InCombat`, so `CombatOnly` versus `AnyTime` is otherwise never observed.
- **Assert each declared keyword tip resolves.** As with Relic, naming a keyword in the
  description surfaces nothing without an explicit `RegisteredKeywordIds` entry. Assert the
  registered id and its resolved title/description.
- **Assert each declared displayed value renders live.** The default recipe shape puts the
  number in both the Cmd and the localized string. Assert the rendered description contains the
  current value, so neither an unresolved placeholder nor a diverged literal ships.
- For advanced targeting, follow `reference/advanced-targeting.md`: the single Potion is one
  of its three required distinct real consumers. `potion + many` remains a known lifecycle
  limitation.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **potion:** `potion <PREFIX>-<SLUG>` (**no `add`**, **exact** match; run in progress).

Trigger it:

   **potion** → use it (pick a target if targeted), and confirm the belt slot empties.
