# Recipe: Card Enchantment

> A persistent Card modification under the pinned STS2 `0.107.1` / RitsuLib `0.6.7` profile.

## Contract and registration

An Enchantment is persistent state attached to one Card. Use the public template and
register exactly once:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Enchantment<<EnchantmentName>>()
    .Apply();
```

Do not add `[Pool]`, depend on auto-discovery, or substitute a run-level Modifier.
RitsuLib derives `MOD_ENCHANTMENT_TYPENAME`.

## Skeleton

```csharp
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Enchantments;

public sealed class <EnchantmentName> : ModEnchantmentTemplate
{
    public override bool HasExtraCardText => true;
    public override bool ShowAmount => true;

    public override EnchantmentAssetProfile AssetProfile => new(
        IconPath: "res://<ModName>/images/enchantments/<slug>.png");

    public override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay? cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay);
        await CreatureCmd.GainBlock(
            Card.Owner.Creature, Amount, ValueProp.Unpowered, null);
    }
}
```

Omit `AssetProfile` in placeholder mode. The supported custom icon is one checked 64x64
PNG at `images/enchantments/<slug>.png`, shared by the Card tab and hover tooltip.

Attach through the public game command:

```csharp
CardCmd.Enchant<<EnchantmentName>>(card, amount);
```

After attachment, assert `card.Enchantment is <EnchantmentName>` and read `Amount` from
that mutable instance. Preserve base restrictions when overriding `CanEnchant`.

## Optional shared capability routes

For a separable Enchantment-owned behavior/state bundle, read `reference/model-capabilities.md`.
For lifecycle/persistence/RNG, read `reference/lifecycle-state-rng.md`; for reachable per-hit
attack, healing, Energy/Stars-gain response, or maximum hand size, read
`reference/shared-effect-hooks.md`. Implement on the Enchantment or its typed capability, preserve
the host Card's combat-pile reachability, and prove neutral plus cleanup cases. Process-wide
registration is not an Enchantment route.

## SPEC `hook participation`: five hooks are replaced here

An Enchantment reaches 61 of the 68 cataloged hooks at their ordinary `AbstractModel` signature.
For damage, block, and card play count it must use `EnchantmentModel`'s own replacements instead.
The pinned assembly documents each as "Enchantments MUST use this hook instead of" its
counterpart, and each runs **before** every other modification hook for that value:

```csharp
// Correct on an Enchantment. Two parameters, no subject guard.
public override decimal EnchantDamageMultiplicative(decimal originalDamage, ValueProp props)
{
    if (!props.IsPoweredAttack()) return 1m;   // SPEC `condition`; the only guard left
    return 2m;
}

// WRONG on an Enchantment: compiles, and the framework's own docs forbid it.
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource) { ... }
```

The five, with their exact signatures and neutral returns:

| Replacement | Signature | Return when not applying |
|---|---|---|
| `EnchantBlockAdditive` | `decimal(decimal originalBlock)` | `0m` |
| `EnchantBlockMultiplicative` | `decimal(decimal originalBlock)` | `1m` |
| `EnchantDamageAdditive` | `decimal(decimal originalDamage, ValueProp props)` | `0m` |
| `EnchantDamageMultiplicative` | `decimal(decimal originalDamage, ValueProp props)` | `1m` |
| `EnchantPlayCount` | `int(int originalPlayCount)` | `originalPlayCount` |

There is no subject guard because the hook is already scoped to this enchantment's own card —
which also means it cannot reach any other card, so do not try to write a cross-card rule here.
Mind the neutral: additive returns `0m` and multiplicative returns `1m`, and a guard copied from
the wrong row is a silent `x0` or a stray `+1`. `EnchantPlayCount` passes through its argument
rather than a constant.

For every other hook, read `reference/model-hook-participation.md` and use the ordinary shape. An
Enchantment inherits its host Card's combat reachability, so a rule meant to hold for all of
combat does not apply while the enchanted Card sits outside the combat piles.

## Localization

Ship matching `localization/eng/enchantments.json` and
`localization/zhs/enchantments.json`:

```json
{
  "<MOD>_ENCHANTMENT_<TYPE>.title": "Display Name",
  "<MOD>_ENCHANTMENT_<TYPE>.description": "Increases [gold]Block[/gold] gained from this card by [blue]{Amount}[/blue].",
  "<MOD>_ENCHANTMENT_<TYPE>.extraCardText": "Gain [blue]{Amount}[/blue] additional [gold]Block[/gold]."
}
```

```json
{
  "<MOD>_ENCHANTMENT_<TYPE>.title": "显示名称",
  "<MOD>_ENCHANTMENT_<TYPE>.description": "这张牌获得的[gold]格挡[/gold]值增加[blue]{Amount}[/blue]点。",
  "<MOD>_ENCHANTMENT_<TYPE>.extraCardText": "额外获得[blue]{Amount}[/blue]点[gold]格挡[/gold]。"
}
```

Both strings follow the Enchantment row of `reference/vanilla-text-style.md`. Any other text
that names this Enchantment writes it in `[purple]`.

Emit `.extraCardText` only when `HasExtraCardText` is true.

## Verification

The `CombatPlayer` proof must independently check registration/localization, attachment
and amount, then drive the host Card and assert the changed outcome.

Custom icon support still requires a headed render in both the Card tab and hover tooltip;
a path getter alone does not promote visual support.
