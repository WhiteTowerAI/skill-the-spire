# Reference: right-click actions on Mod models

This page owns the right-click contract. Use it
when a Mod Card, Relic, Power, Potion, or Orb does something when the player right-clicks
it (or presses the controller `cancel` action on it while it has focus). The model owns the
behavior; RitsuLib owns input, multiplayer-safe dispatch, and the action queue.

## Hosts

| Model | Where the input is read | Reached when |
|---|---|---|
| Card | hand Card; Card in the Draw, Discard, Exhaust, or a Mod Card Pile screen | combat, no Card play or target selection in progress, play phase |
| Relic | top-bar Relic inventory | any run screen without target selection; in combat only in the play phase |
| Potion | top-bar Potion slot | same as Relic |
| Power | Power icon on a creature | combat play phase, no target selection |
| Orb | the player's Orb | combat play phase, no target selection |

Outside these hosts, for example the deck view outside combat or a reward screen, nothing
dispatches. A handled right-click on a pile-screen Card consumes the input; an unhandled one
leaves native behavior alone. The pinned combat pile screen binds nothing to right-click, so
a Card without the action shows no reaction there.

## Route

Implement the matching interface on the Mod model class. No registration is needed:

```csharp
using STS2RitsuLib.Interactions.RightClick;

public sealed class <CardName> : ModCardTemplate, IModRightClickableCard
{
    // Optional local filter: only stable facts this client can see. Default true.
    public bool CanHandleRightClickLocal(ModRightClickContext context) => true;

    // Optional execution-time guard, re-checked on every peer. Default true.
    public bool CanExecuteRightClick(ModRightClickExecutionContext context) =>
        context.Player.PlayerCombatState?.Energy >= 1;

    public async Task OnRightClick(ModRightClickExecutionContext context)
    {
        if (context.PlayerChoiceContext is not { } choiceContext)
            return;   // no combat action context: nothing to do
        await PlayerCmd.LoseEnergy(1, context.Player);
        await CardPileCmd.Draw(choiceContext, 1, context.Player, fromHandDraw: false);
    }
}
```

The interfaces are `IModRightClickableCard`, `IModRightClickableRelic`,
`IModRightClickablePower`, `IModRightClickablePotion`, and `IModRightClickableOrb`.

- `OnRightClick` runs inside a synchronized game action after RitsuLib resolves the same
  model on every peer. Await ordinary effects there; `reference/effect-primitives.md` owns
  the exact Cmd shapes. `context.PlayerChoiceContext` is nullable: guard it before passing it
  to a Cmd that needs a choice context, as above.
- A Card resolves only while it is still in the pile it was clicked in; a removed Relic,
  Potion, Power, or Orb resolves to nothing. Re-check every mutable gameplay condition
  (cost, uses left, phase) in `CanExecuteRightClick` or at the start of `OnRightClick`,
  never in `CanHandleRightClickLocal`.
- `context.Trigger.Source` says where the input came from and `IsController` whether it was
  the controller action. Branch on them only when the SPEC gives the sources different
  behavior.
- After a successful action RitsuLib calls the model's execution-finished notification, so
  a Relic flashes as it does after a native trigger.
- A use limit or cooldown is Mod-owned state on the model (`reference/stateful-mechanics.md`).

Tell the player about the action: the model's `eng` and `zhs` descriptions name the input and
its effect on one line, as one sentence ("Right-click: Lose {Energy:energyIcons()} to draw
{Cards:diff()} {Cards:plural:card|cards}." / "右键：失去{Energy:energyIcons()}，抽{Cards:diff()}张牌。").
Build's style check flags two sentences sharing a line. The pinned glossary has no
right-click term, so write the input word plain and style the effect per
`reference/vanilla-text-style.md`.

## Boundary

- The Mod's `mod_manifest.json` must keep `"affects_gameplay": true` (the scaffold default).
  RitsuLib gives the models of a Mod that declares `false` no network identity, so
  `TryDispatch` returns `false` and nothing is sent, with no warning.
- Mod-owned models only. `RitsuLibFramework.RegisterRightClick<TModel>` binds every model of a
  type, including vanilla ones, and is not part of this route; neither are custom
  `IModRightClickHandler` handlers.
- One right-click action per model. If a capability on the same model also handles
  right-click, both run in priority order; do not author both.
- Input sources beyond the host table (map nodes, Event options, Character portrait) are
  unsupported.
- Multiplayer is not verified. A peer running an older RitsuLib without the right-click
  protocol blocks the request with one warning.

## Verification

Tier 2 drives the real dispatch path without synthetic mouse input. Put the model in its host
(for a Card, the hand), then call the public dispatcher with the matching source:

```csharp
var combat = player.PlayerCombatState!;
int energyBefore = combat.Energy;
var trigger = new ModRightClickTrigger(false, null, ModRightClickSource.HandCard);
var handled = ModRightClickRegistry.TryDispatch(new ModRightClickContext(player, card, trigger));
// The action resolves on the action queue; poll the SPEC post-state.
await WaitHelper.Until(() => combat.Energy == energyBefore - 1, ct,
    TimeSpan.FromSeconds(10), "right-click did not resolve");
```

`handled` only reports that the request was queued; `CanExecuteRightClick` and the pile check
run later, when the action executes. Poll for the expected post-state instead of a fixed
delay. Assert `handled`, the exact post-state, and one negative case: when
`CanExecuteRightClick` is false (or the Card has left the pile the trigger names), dispatch
changes nothing. A pile-screen Card uses
`new ModRightClickTrigger(false, null, ModRightClickSource.CombatPileCard, PileType.Discard)`
with the pile it sits in. Emit the structured `state proof:` line from
`reference/selftest-harness.md`.

Headed review right-clicks the model with the mouse in each selected host, repeats with the
controller `cancel` action, and confirms that an ordinary left-click, drag, or hover is
unchanged and that a pile-screen Card without the action keeps its native (empty) response.
