# Ordered combat buffer and deterministic dynamic output

Status: **pipeline-supported on STS2 0.107.1** by the corrected
`WayfinderAcceptance` flow (2026-07-16). The supported default stores semantic values in
combat state while source cards use STS2's normal Play -> Discard lifecycle.

This page does **not** support retaining played card instances in a `CustomPile`. The old
model-only canary proved pile order and commands but missed overlapping/stale card visuals
in real player use. That implementation is historical evidence, not a player-facing recipe.

## Semantic contract

Use this capability when ordered card plays contribute values or symbols that later create
a deterministic output. SPEC must record:

| Field | Requirement |
|---|---|
| owner | one local `PlayerCombatState` |
| lifetime | combat; a new combat starts empty |
| recorded value | immutable semantic value such as direction, suit, or contribution |
| source destination | normal STS2 result, default `Discard`; never intercept `OnPlay` into a custom pile |
| order | append order and whether it changes the result |
| capacity | finite positive integer and non-destructive overflow behavior |
| visibility | compact current-state text through an already grounded UI host |
| compile | exact trigger, snapshot, clear point, and deterministic formula |
| output | one real mutable card added with `AddGeneratedCardToCombat` |
| scenario | source destinations, order, capacity, overflow, UI refresh, output/history/effect, combat reset |

If the user specifically wants physical cards to remain on screen, report a pack gap. A
retained-card zone needs its own grounded UI container, stable layout, entry/exit animation,
inspection behavior, and visual cleanup. Do not improvise it with `Vector2.Zero`,
`CardShouldBeVisible(false)`, or `skipVisuals: true`.

## Combat-owned ordered state

Scope the buffer to `PlayerCombatState` with the existing `ScopedState` primitive:

```csharp
internal sealed class BufferState<TValue>
{
    public List<TValue> Values { get; } = new();
}

private static readonly ScopedState<PlayerCombatState, BufferState<TValue>> States =
    new(StateLifetime.Combat, () => new BufferState<TValue>());

private static BufferState<TValue> State(Player player) =>
    States.Get(player.PlayerCombatState ??
        throw new InvalidOperationException("ordered buffer requires combat state"));
```

Reject overflow before mutation, append the semantic value, then refresh the mounted UI:

```csharp
public static bool TryAppend(Player player, TValue value)
{
    var state = State(player);
    if (state.Values.Count >= Capacity) return false;
    state.Values.Add(value);
    Refresh(player);
    return true;
}
```

The source card does not move itself. Returning from `OnPlay` lets the engine complete its
normal result-pile lifecycle:

```csharp
protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
{
    Accepted = OrderedBuffer.TryAppend(Owner, Value);
    return Task.CompletedTask;
}
```

Do not call `CardPileCmd.Add(this, customPile, ...)` from this path.

## Snapshot and dynamic output

Snapshot the ordered values, clear state at the specified compile point, refresh UI, then
configure one real output instance:

```csharp
var state = State(player);
if (state.Values.Count != Capacity) return null;

TValue[] values = state.Values.ToArray();
state.Values.Clear();
Refresh(player);

var combat = CombatManager.Instance.DebugOnlyGetState()
    ?? throw new InvalidOperationException("combat state missing");
var output = combat.CreateCard<TOutputCard>(player);
output.Configure(values);
await CardPileCmd.AddGeneratedCardToCombat(output, PileType.Hand, player);
return output;
```

Store the snapshot and configured `DynamicVars` on the mutable output card. Do not create a
new model type at runtime or encode the result only in text/logs.

## Player-visible state

An ordered mechanic must be legible. Render a compact value such as
`Route: N>E>S>W` through an already verified UI host and refresh it after append, overflow
(if feedback changes), compile, and combat reset. A hidden list with no player-readable
state is not pipeline-supported.

This does not authorize custom zone art or a new Harmony target. Wayfinder composes the
route text into the exact character-resource fallback Label under
`NCombatUi.EnergyCounterContainer`.

## Type and Scenario proof

Reuse the owning host suite; do not create a new project merely because a buffer was added.
The live proof asserts:

- every source card reaches its specified normal result pile;
- accepted values preserve exact order and refresh visible state;
- overflow leaves order/resource unchanged and the source still resolves normally;
- the compile card resolves normally, clears the buffer, and creates exactly one output
  `CardGeneratedEntry`;
- output fields/`DynamicVars` match the deterministic formula and its real effect fires;
- a second combat has a distinct empty state and reset UI.

`WayfinderAcceptance` observed four direction cards plus `Survey` in `Discard`, route text
`- -> N>E>S>W -> -`, capacity-4 overflow without mutation, one configured output/history
entry, exact geometry Block `20`, and a distinct empty second-combat route state.

## Unsupported extensions

- retained real-card `CustomPile` gameplay, visible or hidden;
- custom pile buttons, slots, counters, card layouts, or bespoke zone art;
- run-persistent buffer contents or save serialization;
- custom draw lifecycle and hand replacement;
- cross-player or shared multiplayer buffers.

Preserve these as explicit pack gaps until a real player-facing implementation is grounded.
