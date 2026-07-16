# Character resource - combat state, payment, and live counter

Status: **pipeline-supported on STS2 0.107.1** by `CanaryResourceUi` plus the fresh
`WayfinderAcceptance` composition (2026-07-16). This is a selected character capability,
not a new content type.

## Semantic contract

Use this capability when cards or other character-owned effects gain and spend a named
nonnegative resource during combat. SPEC must record:

| Field | Required value |
|---|---|
| owner | the local `Player` through its `PlayerCombatState` |
| lifetime | `combat`; a new `PlayerCombatState` starts at zero |
| amount domain | integer, floor `0`; no implicit debt |
| gain | positive amount and exact source event |
| affordability | `amount >= cost`, checked before payment |
| spend | all-or-nothing `TrySpend`; a rejection leaves amount and payoff unchanged |
| reset/save | combat reset; no run persistence or save claim |
| UI | generic `Label` under `NCombatUi.EnergyCounterContainer`, refreshed after every change |
| scenario | gain, affordable/unaffordable checks, successful/rejected spend, UI refresh, second-combat reset |

Do not reinterpret this contract as alternative energy payment. Patching
`CardModel.SpendResources` or `PlayerCombatState.HasEnoughResourcesFor` is a separate
game seam and is not verified by this page. The proven payoff pattern checks and spends
inside the generated card/domain behavior before applying its consequence.

## Generated layout

```text
<ModName>Code/
  CapabilityKernel/       # only the selected 6c combat-UI adapter
  Domain/
    <ResourceName>Resource.cs
  Cards/
    <GainCard>.cs
    <SpendCard>.cs
```

Keep the named resource rules in `Domain/`. Copy the self-contained kernel primitives
and exact `CombatUiActivate` descriptor from `capability-kernel.md`; do not call
`PatchAll`, change its target, or add `OpenMod.Runtime`.

## Resource state and payment

Scope combat state to `PlayerCombatState`, not a process-wide integer:

```csharp
internal sealed class ResourceState
{
    public int Amount { get; set; }
}

internal static class <ResourceName>Resource
{
    private static readonly ScopedState<PlayerCombatState, ResourceState> States =
        new(StateLifetime.Combat, () => new ResourceState());

    private static ResourceState State(Player player) =>
        States.Get(player.PlayerCombatState ??
            throw new InvalidOperationException("resource requires combat state"));

    public static int Get(Player player) => State(player).Amount;

    public static bool CanAfford(Player player, int cost)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(cost);
        return Get(player) >= cost;
    }

    public static void Gain(Player player, int amount)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(amount);
        State(player).Amount += amount;
        RefreshMountedCounter(player);
    }

    public static bool TrySpend(Player player, int cost)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(cost);
        var state = State(player);
        if (state.Amount < cost) return false;
        state.Amount -= cost;
        RefreshMountedCounter(player);
        return true;
    }
}
```

The spend-host card applies its payoff only after successful payment:

```csharp
bool paid = <ResourceName>Resource.TrySpend(Owner, cost);
if (paid)
    await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
```

The generated domain may expose the last payment result for Tier-2 observation, but it
must not put canary counters or assertions into the reusable capability primitive.

## Generic live counter

Register one typed `CombatUiKernel.Activated` listener before installing the exact 6c
descriptor. In the listener:

1. resolve the local player with `LocalContext.GetMe(context.State)`;
2. mount a `UiHostDescriptor` under `context.Ui.EnergyCounterContainer`;
3. create a fallback `Label` named for the resource;
4. render `<ResourceName>: <amount>` plus resource/lifetime metadata;
5. retain only the current mounted label and refresh it after gain/spend.

Visibility must guard the local player. The patch body only dispatches the typed UI
context; resource rules never enter Harmony code. The verified adapter remains:

```text
risk=B
target=NCombatUi.Activate(CombatState)
STS2=0.107.1
MVID=97f10687-c306-4798-ab75-8b9f23f34dfb
conflict=compatible-postfix-composition
```

## Type and Scenario proof

Tier 1 requires build `0 warnings / 0 errors`, `.dll/.pck/.json`, the exact load marker,
no fresh error block, and `targets=1`, `ownedPostfixes=1` diagnostics.

Tier 2 uses two real `CombatPlayer` combats and asserts:

- initial amount/counter `0`;
- gain changes amount and counter;
- one affordable and one unaffordable result;
- successful payment changes amount and payoff exactly once;
- rejected payment leaves amount/payoff unchanged and never goes negative;
- the second combat has a distinct `PlayerCombatState`/resource state at amount `0`;
- the second counter renders the reset value.

Only then emit:

```text
[T2MOD-SELFTEST] <ModName> state proof: resource UI complete expected=all observed=all
[T2MOD-SELFTEST] <ModName> selftest done
```

`CanaryResourceUi` observed amount `0 -> 3 -> 1`, affordability `true/false`,
Block `+4` only for the successful spend, rejected-spend amount `1`, a real live
`Charge: 0/3/1` Label, and distinct-combat amounts `1/0`.

## Unsupported extensions

- run-persistent resources and save round trips;
- partial/hybrid/alternative energy payment through engine cost hooks;
- custom resource art or a top-bar host;
- remote-player/multiplayer resource UI;
- any patch target other than the exact 6c combat-UI postfix.

Preserve these as explicit pack gaps; do not silently approximate them.
