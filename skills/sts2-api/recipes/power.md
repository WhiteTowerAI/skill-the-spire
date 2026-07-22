# Recipe: Power

> Known-good on STS2 `0.107.1` with RitsuLib `0.4.62` compat. The hosted
> `RitsuCardProof` run explicitly registered a `Counter` Power, applied it at amount 2,
> changed the live instance to 3, and resolved its localization in a RitsuLib-only run.

## Contract

A Power is a persistent buff or debuff on one Creature. Prefer a vanilla Power when its
semantics match. A custom Power uses RitsuLib's public `ModPowerTemplate` and must be
registered exactly once:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Power<<PowerName>>()
    .Apply();
```

Do not add `[Pool]` and do not rely on historical reflection auto-discovery. RitsuLib
derives `MOD_POWER_TYPENAME`; a CLR class named `ChargePower` therefore becomes
`RITSU_CARD_PROOF_POWER_CHARGE_POWER`, including the `Power` suffix.

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

## Hooks

Override only the hook selected by SPEC. Examples:

- turn start: `AfterSideTurnStart(...)`, guarded by `participants.Contains(Owner)`;
- turn end/duration: `AfterSideTurnEnd(...)` plus `PowerCmd.TickDownDuration(this)`;
- flat outgoing damage: `ModifyDamageAdditive(...)`, guarded by owner/props;
- application/removal: `AfterApplied(...)` / `AfterRemoved(...)`.

Use `Owner` for the attached Creature, `Amount` for current stacks, and `Flash()` for a
real trigger. Await all command hooks.

## Localization

Ship `localization/eng/powers.json` with the exact public entry:

```json
{
  "<MOD>_POWER_<TYPE>.title": "Display Name",
  "<MOD>_POWER_<TYPE>.description": "Rules text using {Amount}.",
  "<MOD>_POWER_<TYPE>.smartDescription": "Rules text using {Amount}."
}
```

The game falls back from smart description at runtime, but the active authoring contract
always emits all three keys.

## Verification

The nearest `CombatPlayer` suite must resolve the model from `ModelDb.AllPowers`, check
title and entry, apply it through `PowerCmd.Apply<T>`, mutate the live instance through
the intended path, and assert final state. The R3 proof observed
`RITSU_CARD_PROOF_POWER_CHARGE_POWER`, title `Charge`, `Counter`, and `2 -> 3`.
