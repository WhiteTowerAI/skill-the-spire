# Recipe: Potion

Everything one new Potion needs: the SPEC fields, the class, its text, and its proof. A Potion
is a one-shot consumable: availability is one content-pack registration, behavior lives in
`OnUse`, and art is one `PotionAssetProfile`. Read `reference/vanilla-text-style.md` for every
string. Never add `[Pool]`, a per-Mod Potion base class, or a second registration path.

Also read, only when SPEC selects it:

- a filtered live-creature target: `reference/advanced-targeting.md`;
- extra colored words beyond the default style: `reference/content-text-effects.md`;
- a raw hook rule: `reference/model-hook-participation.md`.

Changing an existing vanilla Potion's availability or pool membership resolves the target
through `reference/vanilla-overrides.md`, then `reference/vanilla-availability-overrides.md`;
never replace the vanilla model or register it as Mod content.

## SPEC fields

Usage and target replace the trigger line; the table is `potions` with no flavor and an
optional `selectionScreenPrompt`; art is one loose 256×256 PNG icon.

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: potion
  - logical id: <stable local stem, e.g. swift_brew>
  - rarity: Common | Uncommon | Rare | Event | Token
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language potion-pool rule>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<hover text>; optional selectionScreenPrompt
    (only if the effect prompts a choice)
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); dynamic value placeholders
  - extra emphasis: none | <description phrase -> color the default style would not apply>
  - displayed values: none | <value name -> declared scaling name; literal or placeholder>
- **effects**:
  - trigger: use
  - usage: CombatOnly | AnyTime | Automatic
  - target: self | one enemy | all enemies
  - advanced target: none | see `reference/advanced-targeting.md`
  - sequence: <precise game-terms effect with exact numbers>
  - scaling: <named values and bounds, or none>
- **hook participation**: none | one or more; see § Hook participation below
- **state**: none (a Potion is single-use and the engine owns its removal)
- **presentation**:
  - assets: potion icon; placeholder | generate (a loose 256×256 PNG; see
    `reference/art-contract.md`)
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: standard potion belt/tooltip display
  - hover tips: none | <each keyword, Power, Card, or Orb named in the description>
- **fallback**:
  - missing asset: checked template potion icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: procure the real Potion, then use it against its declared target
  - invariants: <exact expected/observed state, belt consumption, and dependent effects>
  - boundary cases: <resolved-target, usage-window, and dependent-element cases, or none;
    a Potion has no upgrade>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys (`title`, `description`), potion icon asset role, and framework
  diagnostic record
```

## Registration

Register once from `MainFile.RegisterContent()`:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Potion<SharedPotionPool, <PotionName>>()
    .Apply();
```

`SharedPotionPool` is the default; use a Character pool only when SPEC makes the Potion
Character-specific. RitsuLib derives the public entry `MOD_POTION_TYPENAME`, e.g. `ExampleMod` +
`EmberDraft` becomes `EXAMPLE_MOD_POTION_EMBER_DRAFT`.

## Skeleton

Add `<ModName>Code/Potions/<PotionName>.cs`:

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Potions;

public sealed class <PotionName> : ModPotionTemplate
{
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyEnemy;

    // The displayed number: the description shows it as [blue]{Damage}[/blue].
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new DamageVar(4m, ValueProp.Unpowered) };

    public override PotionAssetProfile AssetProfile => new(
        ImagePath: "res://<ModName>/images/potions/<slug>.png");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        DamageVar damage = DynamicVars.Damage;
        await CreatureCmd.Damage(
            choiceContext, target, damage.BaseValue, damage.Props,
            Owner.Creature, null);
        MainFile.Logger.Info(
            $"[T2MOD-SELFTEST] <ModName> <PotionName> used: damage={damage.BaseValue}");
    }
}
```

`Rarity`, `Usage` (`CombatOnly`/`AnyTime`), and `TargetType` are the three abstract
properties and the SPEC contract (§ Proof matrix). Omit `AssetProfile` in placeholder mode; for
generated art use one checked 256x256 PNG at `images/potions/<slug>.png` and leave
`OutlinePath` null so the original fallback stays available.

## Target and effect rules

`OnUse(PlayerChoiceContext choiceContext, Creature? target)` supplies the real
`choiceContext`, `Owner`, `Owner.Creature`, no Card source, and the nullable selected target.
Call `AssertValidForTargetedPotion(target)` before a targeted sequence, then lower
`effects.sequence` through `reference/effect-primitives.md` and await each command in SPEC
order. A `used:` diagnostic line does not prove behavior.

- Enemy damage uses `TargetType.AnyEnemy` and a non-null target.
- A player buff uses `TargetType.AnyPlayer`, **not** `Self`: the selected target is a player
  creature, unlike a self-targeting Card. Self effects bind `Owner.Creature`. In multiplayer the
  user may pick a teammate, so act on `target` (its player: `target.Player!`), never on `Owner`,
  and write "a player"/"target player" rather than "you" (vanilla `BloodPotion`). A Potion
  meant for teammates only is still `AnyPlayer`; a party-wide one iterates
  `Owner.Creature.CombatState!.GetTeammatesOf(Owner.Creature)` filtered to living players.
- Room-wide effects use the matching all-target `CreatureCmd` overload over live targets.
- Potion damage, Block, and Power effects normally use `ValueProp.Unpowered`.
- A filtered target uses the stable registered value; a single target keeps
  `AssertValidForTargetedPotion(target)`. Never lower a filtered many-target Potion to
  `AllEnemies`.
- `AnyTime` does not promise combat context: reject draw, combat-pile, Orb, Energy/Stars, or
  Creature-target effects when the use window cannot supply their live combat inputs.

## Displayed values the engine keeps current

`PotionModel` runs the same SmartFormat/DynamicVar substitution as `RelicModel`, so a value in
`CanonicalVars` renders live in native `[blue]`. Vanilla `FirePotion` declares
`new DamageVar(20m, ValueProp.Unpowered)` against `Deal [blue]{Damage}[/blue] damage.` Read the
effect amount from that same declared variable rather than repeating a literal in code and text.
A literal is acceptable only when the value can never change and appears in exactly one place;
record the choice in `localization.displayed values`.

## Keyword tips are not automatic here

As with a Relic, a Potion gets no keyword tooltip from naming a keyword. `ModPotionTemplate`
shows tips only through declared `RegisteredKeywordIds` and `AdditionalHoverTips`. Declare every
keyword the description names, and add an `AdditionalHoverTips` entry for each Power, Card, or
Orb it names.

## Hook participation

`OnUse` is the Potion being used. A SPEC `hook participation` block has the engine ask the
Potion for a number or decision while resolving someone else's event, **while the Potion still
sits in the belt**: participation starts when it is procured, not when it is drunk. Follow
`reference/model-hook-participation.md`. A held Potion reaches the same wide set as a Relic
(66 of 68). `Owner` is a `Player`, so a subject guard goes through `Owner.Creature` and
`Owner.Osty` wherever the Osty can be the subject.

## Optional routes

Keep the drinking action in `OnUse`. Read a route only when SPEC selects it, append only its SPEC
block for behavior while the Potion is held, and specify phase/order, subject guard, neutral
case, removal cleanup, and pre/post belt plus behavior assertions. State reachability ends when
the native Potion lifecycle removes it unless SPEC says otherwise. Never register a
Potion-owned rule process-wide.

- separable behavior/state while held: `reference/model-capabilities.md`;
- lifecycle/persistence/RNG: `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`;
- a right-click action other than native use: `reference/model-right-click.md`.

## Localization

Ship matching `localization/eng/potions.json` and `localization/zhs/potions.json` with flat
public-entry keys:

```json
{
  "<MOD>_POTION_<TYPE>.title": "Display Name",
  "<MOD>_POTION_<TYPE>.description": "Deal [blue]{Damage}[/blue] damage."
}
```

```json
{
  "<MOD>_POTION_<TYPE>.title": "显示名称",
  "<MOD>_POTION_<TYPE>.description": "造成[blue]{Damage}[/blue]点伤害。"
}
```

Add `.selectionScreenPrompt` only when the Potion opens a selector. Write the description in the
Potion row of `reference/vanilla-text-style.md`: displayed numbers in `[blue]` from
`CanonicalVars`, heals in `[green]`, glossary terms in `[gold]`
(`Apply [blue]{WeakPower}[/blue] [gold]Weak[/gold].` / `给予[blue]{WeakPower}[/blue]层[gold]虚弱[/gold]。`).
Only when SPEC selects `extra emphasis`, read `reference/content-text-effects.md`.

## Self-test driver body

A Potion gets a named `plan.Combat` scenario that uses it with `t.UsePotion<TPotion>(target)`
(procure the mutable Potion, drive `EnqueueManualUse(target)`, wait for the queued action) and
asserts SPEC state (`reference/selftest-harness.md` § potion). A missing custom atlas sprite
warning is expected in placeholder mode; a fresh error is not.

## Proof matrix

- Assert the declared effect's exact expected/observed state.
- **Assert belt consumption.** `PotionModel.OnUseWrapper` calls `RemoveBeforeUse()` before
  `OnUse`, and the effect delta alone passes for a Potion that is never consumed or is silently
  restored, so assert belt membership before/after, or `HasBeenRemovedFromState`, as its own
  invariant.
- **Assert the declared target, not the implemented one.** The driver derives its target from
  `potion.TargetType`, so a `TargetType` contradicting SPEC still passes the effect assertion.
  Assert the resolved target matches SPEC `effects.target`: for `one enemy`, an enemy took the
  effect and the player did not.
- Assert the declared `usage` when it restricts availability; `t.UsePotion` runs inside combat,
  so `CombatOnly` versus `AnyTime` is otherwise never observed.
- **Assert each declared keyword tip resolves**: the registered id and its title/description.
- **Assert each declared displayed value renders live**: the rendered description contains the
  current value, not an unresolved placeholder or a diverged literal.
- **Hook participation: assert the neutral case outside the guard.** A held Potion changes the
  run from the moment it enters the belt; drive one event the guard should ignore and assert the
  host's value is unchanged. For a collection edit, assert that an entry placed beforehand
  survives.
- Advanced targeting follows `reference/advanced-targeting.md`: the single Potion is one of its
  three required distinct real consumers.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: `potion <PREFIX>-<SLUG>` (**no `add`**, **exact** match; run in progress). Trigger it:
use it (pick a target if targeted) and confirm the belt slot empties.
