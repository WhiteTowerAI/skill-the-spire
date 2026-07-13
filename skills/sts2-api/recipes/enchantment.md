# Recipe: Card Enchantment

> A grounded pattern for a custom STS2 Enchantment: a persistent modifier attached to one
> Card. This is **not** BaseLib `CustomModifierModel` (that is a run-level Good/Bad
> modifier). The host Card must be enchanted and its altered behavior observed.

## Registration and host

Subclass `BaseLib.Abstracts.CustomEnchantmentModel`. ModelDb auto-discovers it; no `[Pool]`
or manual registration. Apply it through the public command:

```csharp
CardCmd.Enchant<MyEnchantment>(card, amount);
```

`EnchantmentModel.Card` is set only on the mutable attached instance. A card can hold one
enchantment unless the existing enchantment is the same stackable type. Override
`CanEnchantCardType`/`CanEnchant` only to add restrictions and preserve base restrictions.

## Skeleton

```csharp
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace <ModName>.<ModName>Code.Enchantments;

public sealed class <Name> : CustomEnchantmentModel
{
    public override bool HasExtraCardText => true; // only when extraCardText loc exists
    public override bool ShowAmount => true;       // if Amount should render

    public override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)
    {
        // Card = the attached mutable host; Amount = CardCmd.Enchant amount
        await <confirmed Cmd sequence>;
    }
}
```

Other useful hooks include `AfterCardPlayed`, `AfterCardDrawn`, and
`AfterAutoPrePlayPhaseEntered`; copy the closest vanilla enchantment rather than guessing.
Use `RecalculateValues()` when the enchantment changes Card/DynamicVar values after attach
or deserialize.

## Localization

Use `localization/eng/enchantments.json`. `CardModifierLoc` establishes required
`.title` + `.description`; add `.extraCardText` iff `HasExtraCardText` is true:

```json
{
  "<PREFIX>-<SLUG>.title": "<Title>",
  "<PREFIX>-<SLUG>.description": "<Tooltip using {Amount} or DynamicVars>",
  "<PREFIX>-<SLUG>.extraCardText": "<Text appended to the host Card>"
}
```

## Icon

BaseLib patches custom enchantments to `CustomIconPath`. Override it for a mod-relative
resource path; otherwise the model falls back to the game's missing-enchantment icon.
BaseLib documents the default convention as
`res://images/enchantments/modid-enchantment_name.png`, but open-mod should use the mod's
own resource root consistently. Extracted vanilla icons are 64×64; do not advertise a
custom art path as verified until a live render check is recorded.

## Type + Scenario proof

1. **Type:** clean build/package/load and exact enchantment localization.
2. **Attachment:** create the host Card and call `CardCmd.Enchant<T>`; assert
   `card.Enchantment is T` and the expected Amount.
3. **Behavior (`CombatPlayer`):** drive the Card by its real card driver, then assert the
   enchantment hook's state delta and successful terminal marker.

Known-good live canary (2026-07-10): `Guarded` attached to `Etched Strike` with Amount 5,
then `OnPlay` logged `attached=True amount=5 block 0 -> 5`.

## Checklist

- [ ] `CustomEnchantmentModel`, not `CustomModifierModel`
- [ ] host restrictions are intentional and preserve `base.CanEnchant`
- [ ] title/description and optional extraCardText loc are exact
- [ ] `CardCmd.Enchant<T>` attaches the mutable instance
- [ ] attachment **and** altered behavior are independently observed
- [ ] icon claim stays provisional until rendered live
