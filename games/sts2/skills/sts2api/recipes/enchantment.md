# Recipe: Card Enchantment

An Enchantment is persistent state attached to one Card. It is always host-scoped, so it has no
standalone element; its SPEC, proof, and scenario ride on the host Card (`recipes/card.md`).

## SPEC fields

Declare it inside the host Card's SPEC fields:

```markdown
  - enchantment: <name> — <what it adds to the host card>
    amount: <value and bounds>
    host restriction: <which cards may legally carry it>
    stacking: replaces an existing enchantment | not stackable
    hook participation: none | one or more (see § Hook participation)
```

The host Card's `localization` section records the exact English and Simplified Chinese
title/description/optional `extraCardText`; the stable entry and SmartFormat variables are
identical between languages. `host restriction` is required: it is the Enchantment's identity
and the thing its proof must exercise.

## Registration

Register exactly once; never add `[Pool]`, depend on auto-discovery, or substitute a run-level
Modifier. RitsuLib derives `MOD_ENCHANTMENT_TYPENAME`.

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Enchantment<<EnchantmentName>>()
    .Apply();
```

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

Omit `AssetProfile` in placeholder mode. The supported custom icon is one checked 64x64 PNG at
`images/enchantments/<slug>.png`, shared by the Card tab and the hover tooltip.

Attach through the public game command, then read `Amount` from the mutable instance:

```csharp
CardCmd.Enchant<<EnchantmentName>>(card, amount);
```

Preserve the base restrictions when overriding `CanEnchant`: the engine already rejects
Status/Curse/Quest Card types and `Unplayable` deck Cards, and a second Enchantment unless
`IsStackable`. An override may **add** restrictions; removing one is out of contract.

## The effect sequence

The awaited attached callback is `OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)`.
It supplies `choiceContext`, the host Card `Card`, its owner `Card.Owner` and
`Card.Owner.Creature`, and the nullable host `cardPlay`; use `cardPlay?.Target` only when the
effect truly follows that target. Lower the sequence through `reference/effect-primitives.md`,
keep the host Card as `cardSource`, pass the real `cardPlay` for Card-caused Block, and reject
target-dependent effects when `cardPlay` or its target is absent. Synchronous
attachment/restriction hooks cannot await commands.

## Hook participation: five hooks are replaced here

An Enchantment reaches 61 of the 68 cataloged hooks at their ordinary `AbstractModel` signature
(`reference/model-hook-participation.md`). For damage, Block, and Card play count it must use
`EnchantmentModel`'s replacements; the assembly documents each as "Enchantments MUST use this
hook instead of" its counterpart, and Build fails the general hook on an Enchantment. Each runs
**before** every other modification hook for that value, so the Enchantment's contribution is
applied first:

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

| Replacement | SPEC id | Signature | Return when not applying |
|---|---|---|---|
| `EnchantBlockAdditive` | `enchant_block_additive` | `decimal(decimal originalBlock)` | `0m` |
| `EnchantBlockMultiplicative` | `enchant_block_multiplicative` | `decimal(decimal originalBlock)` | `1m` |
| `EnchantDamageAdditive` | `enchant_damage_additive` | `decimal(decimal originalDamage, ValueProp props)` | `0m` |
| `EnchantDamageMultiplicative` | `enchant_damage_multiplicative` | `decimal(decimal originalDamage, ValueProp props)` | `1m` |
| `EnchantPlayCount` | `enchant_play_count` | `int(int originalPlayCount)` | `originalPlayCount` |

There is no subject guard: the hook is already scoped to this Enchantment's own Card, so it
cannot reach any other Card; never write a cross-card rule here. Mind the neutral: additive
returns `0m`, multiplicative `1m`, and a guard copied from the wrong row is a silent `x0` or a
stray `+1`. `EnchantPlayCount` passes its argument through.

Every other hook uses the ordinary shape. An Enchantment inherits its host Card's combat
reachability: combat-scope hooks reach it only while the Card is in a combat pile.

## Optional routes

Read a route only when SPEC selects it, append only its nested SPEC block, and preserve the five
replacements, each service's phase/order, the unchanged neutral case, and removal/cleanup proof.
The Enchantment or its typed capability stays the owner with the host Card's reachability.
Process-wide registration is not an Enchantment route.

- a separable behavior/state bundle: `reference/model-capabilities.md`;
- lifecycle/persistence/RNG: `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`.

## The engine writes `extraCardText` onto the host card

When `HasExtraCardText` is true, the engine stamps the Enchantment's localized `extraCardText`
into the host Card's rendered description and folds the Enchantment's Hover Tip into that Card's
`HoverTips`. The Enchantment owns two strings and the host Card owns neither:

- `.description`: the Enchantment's own hover text;
- `.extraCardText`: what the engine appends to the host Card, emitted only when
  `HasExtraCardText` is true.

**Never write either string into the host Card's own description.** The example values below
are near-duplicates by design; that is a localization shape, not a license for a third copy.

## Localization

Ship matching `localization/eng/enchantments.json` and `localization/zhs/enchantments.json`:

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

Both strings follow the Enchantment row of `reference/vanilla-text-style.md`: plain title,
`[blue]` numbers, `[gold]` glossary terms. Any other string that names the Enchantment wraps it in
`[purple]`, as vanilla does (`[gold]Enchant[/gold] it with [purple]Instinct[/purple].`), and
declares `HoverTipFactory.FromEnchantment<T>()` in its `AdditionalHoverTips`.

## Self-test driver body

An Enchantment has no scenario of its own. Add the assertions below to its host Card's scenario
(`recipes/card.md`).

## Proof matrix

- Assert registration and localization resolve, then attachment: `card.Enchantment is
  <EnchantmentName>` with the SPEC amount read from that mutable instance.
- Drive the host Card and assert the changed outcome the Enchantment causes.
- Assert the composed host-Card text contains the `extraCardText` exactly **once**.
- **Assert the host restriction with an illegal host.** Attachment plus a changed outcome passes
  for an Enchantment that attaches to anything, including Curses and `Unplayable` Cards. Attempt
  one host the SPEC forbids and assert refusal with the Card unchanged.
- When `stacking` is `not stackable`, attempt a second Enchantment on an enchanted Card and
  assert the declared outcome, refusal or replacement.
- **Hook participation: assert the neutral case outside the guard.** Assert the modified value
  through the host Card, then drive one excluded case and assert it unchanged. For one of the
  five replacements, also assert the value on an **unenchanted** Card of the same kind is
  untouched, which proves the contribution is scoped to its own host.
- A custom icon needs a headed render in both the Card tab and the hover tooltip; a path getter
  alone is not visual proof.
