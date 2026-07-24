# Ordered combat buffer and deterministic dynamic output

Status: **RitsuLib pipeline-supported on STS2 0.107.1**. `RitsuResourceProof` proved the
mechanic in isolation and `RitsuWayfinderProof` proved the final Character composition on
2026-07-23. The buffer stores semantic values in combat-attached state while source cards
use STS2's normal Play -> Discard lifecycle.

This page does not support retaining played card instances in a `CustomPile`. The retired
model-only implementation missed overlapping/stale card views in real player use and is
historical evidence only.

## Semantic contract

SPEC must record:

| Field | Requirement |
|---|---|
| owner | one local `PlayerCombatState` |
| lifetime | combat; a new combat starts empty |
| recorded value | immutable semantic value such as direction, suit, or contribution |
| source destination | normal STS2 result, default `Discard`; never intercept into a custom pile |
| order | append order and whether it changes the result |
| capacity | finite positive integer and non-destructive overflow behavior |
| visibility | compact state in the public resource UI attachment with text-only fallback |
| compile | exact trigger, snapshot, clear point, and deterministic formula |
| output | one real mutable card added with `AddGeneratedCardToCombat` |
| scenario | destinations, order, overflow, UI, output/history/effect, and combat reset |

If the user wants physical played cards to remain on screen, report a pack gap. A retained
zone needs its own grounded container, stable layout, animation, inspection, and cleanup.
Do not improvise it with `Vector2.Zero`, hidden card views, or `skipVisuals: true`.

## Combat-attached semantic state

Use RitsuLib `AttachedState<PlayerCombatState,TState>` and key it by the current combat:

```csharp
using STS2RitsuLib.Utils;

internal sealed class RouteState
{
    public List<RouteDirection> Directions { get; } = [];
}

private static readonly AttachedState<PlayerCombatState, RouteState> States =
    new(() => new RouteState());

public static RouteState GetState(Player player) =>
    States.GetOrCreate(player.PlayerCombatState ??
        throw new InvalidOperationException("route requires combat state"));
```

Do not add a process-wide list, custom `ScopedState`, run-save holder, or explicit combat
reset. A distinct `PlayerCombatState` owns a distinct attached value.

Reject overflow before mutating the buffer or any coupled resource. Append the semantic
value first, then apply the accepted-play consequence:

```csharp
public static async Task<bool> TryPlot(
    Player player, RouteDirection direction)
{
    var state = GetState(player);
    if (state.Directions.Count >= Capacity)
        return false;

    state.Directions.Add(direction);
    await InkResource.Gain(player, 1);
    return true;
}
```

The source Card records only its semantic value. Returning from `OnPlay` lets STS2 finish
the normal result-pile lifecycle:

```csharp
protected override async Task OnPlay(
    PlayerChoiceContext choiceContext, CardPlay cardPlay)
{
    PlotAccepted = await RouteBuffer.TryPlot(Owner, Direction);
}
```

Do not call `CardPileCmd.Add(this, customPile, ...)` from this path.

## Snapshot and output

At the configured compile point, require the exact capacity, snapshot in append order,
clear the live buffer, refresh the shared UI, and create one real output:

```csharp
var state = GetState(player);
if (state.Directions.Count != Capacity)
    return null;

RouteDirection[] snapshot = state.Directions.ToArray();
state.Directions.Clear();
InkResource.Refresh(player);

var combat = CombatManager.Instance.DebugOnlyGetState()
    ?? throw new InvalidOperationException("combat state missing");
var output = combat.CreateCard<MappedRoute>(player);
output.Configure(snapshot);
await CardPileCmd.AddGeneratedCardToCombat(output, PileType.Hand, player);
return output;
```

Store the snapshot and configured `DynamicVars` on the mutable output Card. Do not create
a model type at runtime or encode the result only in UI/log text.

The proven Wayfinder formula interprets `N>E>S>W` as a closed path with three right turns
and computes Block `5 + 3 * rightTurns + leftTurns + (closed ? 6 : 0) = 20`. This exact
formula is proof data, not a universal buffer rule; a generated Mod uses its SPEC formula.

## Player-visible state

Render a compact value such as `Route: N>E>S>W` through the `RegisterCombatUi` route in
`character-resource.md`. The promoted composition renders `Ink: N | Route: ...` in the
fixed 220x32 control at offset `(160,0)`, with a checked 24x24 icon and the same live text
when that icon is missing. Refresh after append/resource mutation, compile/clear, and
combat reset. Overflow must leave both state and UI unchanged.

This does not authorize custom zone art, a Harmony patch, or a new UI host.

## Required Tier 2 proof

Reuse the owning `CombatPlayer` or Character suite and assert:

1. state and visible route start empty;
2. every source Card reaches its normal result pile;
3. accepted values preserve exact order and coupled resource changes;
4. overflow leaves order/resource/UI unchanged while its source still resolves normally;
5. the compile Card reaches its normal pile, clears the buffer, and creates exactly one
   output in Hand plus one `CardGeneratedEntry`;
6. output fields/`DynamicVars` match the deterministic formula and its real effect fires;
7. rejected output payment changes neither resource nor payoff;
8. combat 2 has a distinct attached state, empty route, reset resource, and reset UI.

The final `RitsuWayfinderProof` observed direction and Survey Cards in Discard, route
`- -> N>E>S>W -> -`, capacity-4 overflow without mutation, one generated `MappedRoute`,
Block `20`, successful Ink `4 -> 0`, rejected payment at `0`, and combat-2 Ink `0` / Route
`-`. It reached `wayfinder R5 parity complete expected=all observed=all`, `selftest done`,
strict Tier 2, and no fresh error with only the declared RitsuLib runtime dependency.

## Unsupported extensions

- retained real-card `CustomPile` gameplay, visible or hidden;
- custom pile buttons, slots, counters, layouts, or bespoke zone art;
- run-persistent buffer contents or save serialization;
- custom draw lifecycle or hand replacement;
- cross-player or shared multiplayer buffers.

Preserve these as explicit pack gaps until a real player-facing implementation is grounded.
