# Character resource - RitsuLib combat state, payment, and live counter

Status: **implemented with RitsuLib on STS2 0.107.1**. `RitsuResourceProof` proved
the resource in isolation and `RitsuWayfinderProof` proved the final Character
composition on 2026-07-23 with RitsuLib 0.4.67 as the sole framework dependency.

Use this capability when cards or other character-owned effects gain and spend a named
nonnegative resource during combat. It is a selected Character capability, not a new
content type and not a replacement for native Energy.

## Semantic contract

SPEC must record:

| Field | Required value |
|---|---|
| owner | the local `Player` and its current `PlayerCombatState` |
| lifetime | `combat`; a new combat starts at the registered default |
| amount domain | integer, minimum `0`; no implicit debt |
| gain | positive amount and exact source event |
| affordability | `amount >= cost`, checked explicitly |
| spend | all-or-nothing; rejection leaves amount and payoff unchanged |
| reset/save | `SecondaryResourcePersistencePolicy.Combat`; no run-save claim |
| UI | public `RegisterCombatUi` attachment under `NCombatUi.EnergyCounterContainer` |
| layout | fixed 220x32 icon+text control at offset `(160,0)`; checked text-only fallback |
| scenario | gain, affordability, successful/rejected spend, UI refresh, and combat-2 reset |

Do not reinterpret this contract as alternative Energy payment. Patching card resource
cost hooks is unsupported. The proven payoff pattern spends inside generated domain/card
behavior and applies the consequence only when RitsuLib reports successful payment.

## Registration and commands

Register the resource and its UI once from Mod initialization, before the content pack is
used in combat:

```csharp
using STS2RitsuLib;
using STS2RitsuLib.Combat.SecondaryResources;
using STS2RitsuLib.Scaffolding.Godot.NodeAttachments;

private static readonly ModSecondaryResourceRegistry Resources =
    RitsuLibFramework.GetSecondaryResourceRegistry(MainFile.ModId);
private static readonly ModNodeAttachmentRegistry Attachments =
    RitsuLibFramework.GetNodeAttachmentRegistry(MainFile.ModId);

public static SecondaryResourceDefinition Definition { get; private set; } = null!;
public static string Id => Definition.Id;

public static void Register()
{
    Definition = Resources.Register("ink", new SecondaryResourceDefinition(
        defaultAmount: 0,
        minAmount: 0,
        turnStartPolicy: SecondaryResourceTurnStartPolicy.None,
        persistencePolicy: SecondaryResourcePersistencePolicy.Combat,
        smallIconPath: IconPath,
        largeIconPath: IconPath));
    Resources.AlwaysShowInCombatUi("ink");
    Resources.RegisterCombatUi(
        "ink-counter",
        _ => InkCounter.Create(),
        UpdateCounter,
        new NodeAttachmentOptions
        {
            Name = "<ModName>InkCounter",
            AttachParentSelector = node =>
                ((NCombatUi)node).EnergyCounterContainer,
        });
}
```

Use `SecondaryResourceCmd` as the only amount store and mutation route:

```csharp
public static int Get(Player player) =>
    SecondaryResourceCmd.Get(player, Id);

public static bool CanAfford(Player player, int cost)
{
    ArgumentOutOfRangeException.ThrowIfNegative(cost);
    return Get(player) >= cost;
}

public static Task<int> Gain(
    Player player, int amount, AbstractModel? source = null)
{
    ArgumentOutOfRangeException.ThrowIfNegativeOrZero(amount);
    return SecondaryResourceCmd.Gain(player, Id, amount, source);
}

public static Task<bool> TrySpend(
    Player player,
    int cost,
    CardModel? card = null,
    AbstractModel? source = null)
{
    ArgumentOutOfRangeException.ThrowIfNegative(cost);
    return SecondaryResourceCmd.Spend(player, Id, cost, card, source);
}
```

Do not add a duplicate `int`, `ScopedState`, save property, or combat-start reset hook.
RitsuLib owns the amount and creates the combat-lifetime value from the registered
definition. Keep `CanAfford` for intent/UI decisions; `Spend` remains the authoritative
all-or-nothing payment.

The spender applies its payoff only after payment:

```csharp
bool paid = await InkResource.TrySpend(Owner, cost, this, this);
if (paid)
    await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
```

## Public combat UI attachment

`RegisterCombatUi` is the promoted host seam. Do not emit the historical Harmony
`NCombatUi.Activate` postfix or separate patch module for this resource.

The update callback must use the context's local player and `VisibleDefinitions`, keep the
control hidden when this resource is not visible, and render the current resource plus any
bounded mechanic state:

```csharp
private static void UpdateCounter(
    SecondaryResourceCombatUiContext<NCombatUi, InkCounter> context)
{
    var visible = context.Player != null &&
        context.VisibleDefinitions.Any(definition => definition.Id == Id);
    context.Node.Visible = visible;
    if (!visible) return;

    context.Node.ValueLabel.Text =
        $"Ink: {Get(context.Player!)} | Route: " +
        RouteBuffer.RouteText(context.Player!);
}

public static bool TryGetMounted(NCombatUi ui, out InkCounter counter) =>
    Attachments.TryGetAttached(ui, "ink-counter", out counter);

public static void Refresh(Player player)
{
    if (NCombatRoom.Instance?.Ui is { } ui)
        SecondaryResourceUiRuntime.UpdateCombatUi(ui, player);
}
```

The fixed control is an `HBoxContainer` with:

- `CustomMinimumSize = new Vector2(220, 32)`;
- `Position = new Vector2(160, 0)` so it does not overlap the 128x128 native Character
  energy counter;
- an optional existence-checked 24x24 `TextureRect`;
- a minimum 188x32 live `Label`;
- resource/lifetime metadata for diagnostics;
- identical live text when the icon is missing.

RitsuLib owns attachment and combat-UI lifecycle. Call `Refresh(player)` after a state
change that does not itself mutate the secondary resource, such as clearing a composed
ordered buffer. Resource gain/spend already travels through `SecondaryResourceCmd`.

## Required Tier 2 proof

Use two real `CombatPlayer` combats and assert:

1. the first mounted control starts at amount `0` and the fallback retains live text;
2. gain changes amount, affordability, and visible text;
3. one successful spend changes amount and payoff exactly once;
4. one rejected spend leaves amount/payoff unchanged and never goes negative;
5. the icon is 24x24, root/label are 220x32 and 188x32, offset is `(160,0)`, and the
   resource and native energy global rects do not intersect;
6. combat 2 has a distinct `PlayerCombatState`, amount `0`, and reset UI.

`RitsuResourceProof` observed resource `0 -> 3 -> 1`, affordability `true/false`, Block
`+4` only on successful payment, rejection at `1`, and a distinct combat-2 value `0`.
The final `RitsuWayfinderProof` observed Ink `0 -> 4 -> 0`, paid Block `20`, rejected
payment with no extra Block, route composition in the same control, resource rect
`(260,828,220,32)` disjoint from energy rect `(100,828,128,128)`, and combat-2 Ink `0`.
Both reached `selftest done`, strict Tier 2, and no fresh error.

## Unsupported extensions

- run-persistent Character resources and save round trips;
- partial, hybrid, or alternative-Energy engine payment;
- arbitrary top-bar hosting, animated UI, or custom-zone presentation;
- remote-player or multiplayer resource UI;
- a private patch fallback when the public attachment is unavailable.

Preserve these as explicit pack gaps; do not silently approximate them.
