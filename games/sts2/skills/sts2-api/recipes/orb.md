# Recipe: Custom Orb

> A grounded pattern for an STS2 Orb hosted by an orb-capable Player. A useful orb has
> channel presence plus distinct passive and evoke behavior; prove all three rather than
> merely registering the model.

## Registration and localization

Subclass `BaseLib.Abstracts.CustomOrbModel`. ModelDb auto-discovers it and the constructor
adds the canonical instance to BaseLib's custom-orb list; no `[Pool]` or manual registration.
Return `OrbLoc(title, description, smartDescription)` from `Localization`:

```csharp
public override List<(string, string)> Localization =>
    new OrbLoc("<Title>", "<fallback description>",
        "[gold]Passive:[/gold] ... {Passive} ...\n[gold]Evoke:[/gold] ... {Evoke} ...");
```

`OrbLoc` requires title, description, and smartDescription. The smart tooltip receives
`Passive`, `Evoke`, and `energyPrefix` at runtime.

## Skeleton

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace <ModName>.<ModName>Code.Orbs;

public sealed class <Name>Orb : CustomOrbModel
{
    public override decimal PassiveVal => ModifyOrbValue(<N>m);
    public override decimal EvokeVal => ModifyOrbValue(<M>m);
    public override Color DarkenedColor => new("<hex>");
    public override List<(string, string)> Localization => new OrbLoc(...);

    public override async Task Passive(PlayerChoiceContext choiceContext, Creature? target)
    {
        await <confirmed passive Cmd>;
    }

    public override async Task<IEnumerable<Creature>> Evoke(PlayerChoiceContext choiceContext)
    {
        await <confirmed evoke Cmd>;
        return new[] { Owner.Creature }; // or the creatures actually affected
    }
}
```

`Owner` exists only on the mutable channeled orb. `ModifyOrbValue` applies Focus/other orb
value hooks. Optional `IncludeInRandomPool => true` makes the orb eligible for random-orb
effects such as Chaos.

## Host Card and commands

A Card/relic/power normally channels the orb:

```csharp
await OrbCmd.Channel<MyOrb>(choiceContext, player);
```

`OrbCmd.Channel` automatically adds one slot when a character has zero base slots and the
current queue has zero capacity. A full queue evokes the next orb before enqueueing.
Other confirmed commands:

- `OrbCmd.AddSlots(player, amount)` / `RemoveSlots`
- `OrbCmd.Passive(choiceContext, orb, target)`
- `OrbCmd.EvokeNext(...)` / `EvokeLast(...)`

Slot amounts are a caller-owned nonnegative domain. Clamp a variable request first
(`amount = Math.Max(0, amount)`) and skip the Cmd at zero. Do not pass a negative amount
to `AddSlots` as a shortcut for removal or to `RemoveSlots` as a shortcut for addition:
their internal upper-bound clamps do not reject negatives, so the operation can run in
the opposite direction. `EvokeNext`/`EvokeLast` are safe on an empty queue (they check
`Orbs.Count > 0`).

## Art contract (provisional until live-rendered)

BaseLib exposes three custom seams:

- `CustomIconPath` for the tooltip/icon Texture2D;
- `CustomSpritePath` for a PackedScene used by the combat orb visual;
- `CreateCustomSprite()` to construct a `Node2D` directly (takes precedence when non-null).

Extracted vanilla orb icons are 100×100, but a loose custom PNG alone is not the whole
combat visual: the sprite is a scene/Node2D. Keep placeholder/default visuals during the
mechanic proof and do not advertise custom orb art until both icon and combat sprite render
live.

## Type + Scenario proof

1. **Type:** clean build/package/load and OrbLoc keys.
2. **Channel:** drive the real host Card and assert the custom orb is present in
   `player.PlayerCombatState.OrbQueue` (including capacity).
3. **Passive:** call/advance the real passive lifecycle and assert its state delta.
4. **Evoke:** evoke the queued orb and independently assert its state delta/removal.

Known-good live canary (2026-07-10): `Take Shelter` channels custom `ShelterOrb`; queue
presence was true with capacity 1, passive Block `0 -> 2`, evoke Block `2 -> 7`.

## Checklist

- [ ] `CustomOrbModel`; no `[Pool]`
- [ ] PassiveVal/EvokeVal/DarkenedColor and OrbLoc all supplied
- [ ] behavior reads mutable `Owner`, not canonical state
- [ ] host uses `OrbCmd.Channel<T>`
- [ ] any variable `AddSlots`/`RemoveSlots` amount is clamped nonnegative before the Cmd
- [ ] channel + passive + evoke are separately observed
- [ ] custom icon/sprite claims remain provisional until rendered live
