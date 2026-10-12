# Recipe: Power

> A custom Power under the pinned STS2 `0.107.1` / RitsuLib `0.6.7` profile.
> When SPEC declares supplemental corner values, also read
> `reference/extra-corner-labels.md`; it owns provider, bounds, refresh/removal, and headed
> consumer proof.

## Contract

A Power is a persistent buff or debuff on one Creature. Prefer a vanilla Power when its
semantics match. A custom Power uses RitsuLib's public `ModPowerTemplate` and must be
registered exactly once:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Power<<PowerName>>()
    .Apply();
```

Do not add `[Pool]` and do not rely on reflection auto-discovery. RitsuLib
derives `MOD_POWER_TYPENAME`; a CLR class named `ChargePower` in `ExampleMod` therefore becomes
`EXAMPLE_MOD_POWER_CHARGE_POWER`, including the `Power` suffix.

## Skeleton

```csharp
using MegaCrit.Sts2.Core.Entities.Powers;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Powers;

public sealed class <PowerName> : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://<ModName>/images/powers/<slug>.png",
        BigIconPath: "res://<ModName>/images/powers/big/<slug>.png");
}
```

Omit `AssetProfile` in placeholder mode. Generated Power art is two checked 256x256 PNGs:
the status icon and `big/` apply/expire icon.

## Optional extra badges

Implement `IPowerExtraIconAmountLabelSpecsProvider` on the same Power class. Return zero to
one `ExtraIconAmountLabelSpec.Plain(...)` or bounded `RichText(...)` entry at `TopLeft`.
Preserve the native bottom-right `Amount` display and the six-visible-character limit. Do
not combine Power presets: the pinned preset bands are not clipped and multiple labels can
intrude into adjacent Powers in a crowded row.

If badge text follows `Amount`, use the normal amount mutation and
`InvokeDisplayAmountChanged()`. For a separate field with no host display refresh,
implement `IPowerExtraIconAmountLabelsChangeSource`, declare
`event Action? PowerExtraIconAmountLabelsInvalidated`, and invoke it once after the state
mutation. Returning no spec after the removal condition makes RitsuLib remove the label.
Do not poll or generate custom rectangles.

## Amount domain

Every `Counter` must have an explicit SPEC domain. Default to nonnegative. Use
`AllowNegative => true` only when SPEC defines signed behavior. Clamp every caller-owned
gain or spend before invoking a Cmd, then re-read the retained live instance because hooks
may rewrite the requested offset.

Apply or gain:

```csharp
await PowerCmd.Apply<<PowerName>>(
    choiceContext, target, amount, applier, cardSource);
```

Consume an existing nonnegative Counter:

```csharp
var power = target.GetPower<<PowerName>>();
if (power is { Amount: > 0 })
{
    var spend = Math.Min(power.Amount, Math.Max(0, requested));
    await PowerCmd.ModifyAmount(choiceContext, power, -spend, null, null);
}
```

Never use a negative `PowerCmd.Apply<T>` to consume. With no existing instance it can
create invalid negative state.

## Optional shared capability routes

For a separable Power-owned behavior/state bundle, read `reference/model-capabilities.md`; for
lifecycle/persistence/RNG, read `reference/lifecycle-state-rng.md`; and for reachable per-hit
attack, healing, Energy/Stars-gain response, or maximum hand size, read
`reference/shared-effect-hooks.md`. Implement on the Power or typed capability and preserve amount,
duration, owner guard, phase/order, neutral behavior, display refresh, and removal cleanup.
Process-wide registration is not a Power route.

## Hooks

Override only the hook selected by SPEC. Examples:

- turn start: `AfterSideTurnStart(...)`, guarded by `participants.Contains(Owner)`;
- turn end/duration: `AfterSideTurnEnd(...)` plus `PowerCmd.TickDownDuration(this)`;
- flat outgoing damage: `ModifyDamageAdditive(...)`, guarded by owner/props;
- application/removal: `AfterApplied(...)` / `AfterRemoved(...)`.

Use `Owner` for the attached Creature, `Amount` for current stacks, and `Flash()` for a
real trigger. Await all command hooks.

## SPEC `hook participation`: modify a value the host is computing

When SPEC declares `hook participation`, the Power is not acting at a trigger — the engine is
asking it for a number or a decision while resolving someone else's event. Read
`reference/model-hook-participation.md` for the full contract; a Power reaches the combat-scope
set, and `Owner` is the attached `Creature` directly.

The shape is a guard, then the value, with the hook's neutral default on every other path:

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (target != Owner) return 1m;               // SPEC `subject`: incoming, not outgoing
    if (!props.IsPoweredAttack()) return 1m;      // SPEC `condition`: attack damage only
    return DynamicVars["DamageIncrease"].BaseValue;
}
```

That is vanilla `VulnerablePower`. Copy its structure, and keep three things straight:

- **`target` versus `dealer` is the whole difference** between "damage I take" and "damage I
  deal". `VulnerablePower` guards `target`; `WeakPower` guards `dealer`. SPEC's `subject` line
  says which.
- **Return the neutral default outside the guard**, never a stored modifier. It is also what the
  engine uses to decide whether to list this Power as a modifier of that number in the UI.
- **Read the number from `DynamicVars`** and declare it in `CanonicalVars`, so the value in the
  rules text is the same value the body applies. Two literals will diverge.

Do not use `ModifyDamageMultiplicative` or the other four redirected hooks on an
**Enchantment**; see `recipes/enchantment.md`.

## Localization

Ship matching `localization/eng/powers.json` and `localization/zhs/powers.json` with the
exact public entry:

```json
{
  "<MOD>_POWER_<TYPE>.title": "Display Name",
  "<MOD>_POWER_<TYPE>.description": "At the start of your turn, gain [gold]Block[/gold].",
  "<MOD>_POWER_<TYPE>.smartDescription": "At the start of your turn, gain [blue]{Amount}[/blue] [gold]Block[/gold]."
}
```

```json
{
  "<MOD>_POWER_<TYPE>.title": "显示名称",
  "<MOD>_POWER_<TYPE>.description": "在你的回合开始时，获得[gold]格挡[/gold]。",
  "<MOD>_POWER_<TYPE>.smartDescription": "在你的回合开始时，获得[blue]{Amount}[/blue]点[gold]格挡[/gold]。"
}
```

The two descriptions have different jobs. The pinned `PowerModel.HoverTips` uses
`.smartDescription` for a live, mutable Power, with `{Amount}` bound to its stacks. A Card,
Relic, or Potion tooltip built from `HoverTipFactory.FromPower<T>()` shows the canonical
model's `.description` with `{Amount}` bound to the canonical amount, usually 0. So
`.description` states the general rule without `{Amount}` (a fixed number may appear as
`[blue]2[/blue]`), and `.smartDescription` states the live rule with `[blue]{Amount}[/blue]`,
as vanilla `DEMON_FORM_POWER` does. Both follow the Power row of
`reference/vanilla-text-style.md`. The active authoring contract always emits all three keys.

## Verification

The nearest `CombatPlayer` suite must resolve the model from `ModelDb.AllPowers`, check
title and entry, apply it through `PowerCmd.Apply<T>`, mutate the live instance through
the intended path, and assert final state.

For extra badges, also assert zero/one provider output, exact `TopLeft` corner and text, the
selected invalidation path, removal, and unchanged native `Amount`. The real
`NPower` label layout remains a headed observation; provider data alone is not proof.
