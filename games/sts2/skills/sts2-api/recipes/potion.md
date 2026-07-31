# Recipe: Potion

> Known-good on STS2 `0.107.1` with RitsuLib `0.4.67` compat. The hosted
> `RitsuCardProof` run registered `EmberDraft` through the public content pack,
> procured it, used it on a real enemy, and proved exact damage in a RitsuLib-only run.

## Contract

A Potion is a one-shot consumable. Its availability belongs in one content-pack
registration, its behavior belongs in `OnUse`, and its art belongs in one
`PotionAssetProfile`. Do not add `[Pool]`, a per-Mod potion base class, or a second
registration path.

When SPEC declares a filtered live-creature target, read
`reference/advanced-targeting.md`. The pinned profile supports a custom single-target
Potion only; `potion + many` must stop authoring because queued zero-target execution
cannot preserve the Potion.

Register once from `MainFile.RegisterContent()`:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Potion<SharedPotionPool, <PotionName>>()
    .Apply();
```

`SharedPotionPool` is the default. Use a character pool only when SPEC makes the Potion
character-specific. RitsuLib derives the public entry as `MOD_POTION_TYPENAME`, for
example `RitsuCardProof` + `EmberDraft` becomes
`RITSU_CARD_PROOF_POTION_EMBER_DRAFT`.

## Skeleton

```csharp
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Potions;

public sealed class <PotionName> : ModPotionTemplate
{
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyEnemy;

    public override PotionAssetProfile AssetProfile => new(
        ImagePath: "res://<ModName>/images/potions/<slug>.png");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        await CreatureCmd.Damage(
            choiceContext, target, 4m, ValueProp.Unpowered,
            Owner.Creature, null);
        MainFile.Logger.Info(
            "[T2MOD-SELFTEST] <ModName> <PotionName> used: damage=4");
    }
}
```

Omit the `AssetProfile` override in placeholder mode. For generated art, use one checked
256x256 PNG at `images/potions/<slug>.png`; `OutlinePath` may remain null so the original
fallback stays available.

## Target and effect rules

- Enemy damage uses `TargetType.AnyEnemy` and a non-null target.
- Player buffs normally use `TargetType.AnyPlayer`; the selected target is a player
  creature, unlike a self-targeting Card.
- Room-wide effects use the matching all-target `CreatureCmd` overload.
- A filtered single target uses the stable registered value and keeps
  `AssertValidForTargetedPotion(target)`. RitsuLib revalidates it before removal; follow
  `reference/advanced-targeting.md` for registration and mouse/controller proof.
- Never lower a filtered many-target Potion to `AllEnemies`, restore it after removal, or
  generate a patch. Report the pinned-profile gap.
- Potion damage, Block, and Power effects normally use `ValueProp.Unpowered`.
- `OnUse` must await every Cmd. A diagnostic `used:` line does not prove behavior.

Common grounded operations:

```csharp
await CreatureCmd.GainBlock(target, 12m, ValueProp.Unpowered, null);
await CreatureCmd.Heal(target, 10m);
await PowerCmd.Apply<StrengthPower>(
    choiceContext, target, 2m, Owner.Creature, null);
await PlayerCmd.GainEnergy(2m, Owner);
```

## Localization

Ship `localization/eng/potions.json` with flat public-entry keys:

```json
{
  "<MOD>_POTION_<TYPE>.title": "Display Name",
  "<MOD>_POTION_<TYPE>.description": "Deal 4 damage."
}
```

Add `.selectionScreenPrompt` only when the Potion opens a selector.

## Verification

The `CombatPlayer` harness must:

1. resolve the Potion from `ModelDb.AllPotions` and check its title;
2. call `PotionCmd.TryToProcure(potion.ToMutable(), player)`;
3. drive `potion.EnqueueManualUse(target)` and wait for the queued action;
4. assert the concrete post-state and emit one `state proof:` marker;
5. reach `selftest done` with no fresh error.

The R3 proof observed
`RITSU_CARD_PROOF_POTION_EMBER_DRAFT`, title `Ember Draft`, and enemy HP
`27 -> 23`. A missing custom atlas sprite warning is expected in placeholder mode; a
fresh error is not.
