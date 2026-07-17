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
using MegaCrit.Sts2.Core.Helpers;

namespace <ModName>.<ModName>Code.Orbs;

public sealed class <Name>Orb : CustomOrbModel
{
    public const string FallbackIconPath = "res://images/orbs/frost_orb.png";
    public static string ModIconPath =>
        $"{MainFile.ResPath}/images/orbs/<slug>.png";
    public static string FallbackSpritePath =>
        SceneHelper.GetScenePath("orbs/orb_visuals/frost_orb");

    public override string? CustomIconPath =>
        ResourceLoader.Exists(ModIconPath) ? ModIconPath : FallbackIconPath;
    public override string? CustomSpritePath => FallbackSpritePath;
    public override string? CustomChannelSfx =>
        "event:/sfx/characters/defect/defect_frost_channel";

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

## Presentation contract

BaseLib exposes three custom seams:

- `CustomIconPath` for the tooltip/icon Texture2D;
- `CustomSpritePath` for a PackedScene used by the combat orb visual;
- `CreateCustomSprite()` to construct a `Node2D` directly (takes precedence when non-null).

These are two independent contracts. The **icon pipeline is supported**: one transparent
`images/orbs/<slug>.png`, normalized to 100x100 with `contain` fit and chroma-key on. The
existence-checked `CustomIconPath` above selects it when packed and otherwise returns the
verified Frost icon. The same `OrbModel.Icon` feeds both:

- the real orb smart hover tooltip (`HoverTip(orb, ...)`);
- `NOrb/%Flash`, whose `CpuParticles2D.Texture` emits when `orb.Trigger()` fires.

The **persistent combat body is still a separate Spine scene**, not a bitmap. `NOrb`
unconditionally gets `SpineSkeleton` from `OrbModel.CreateSprite()` and starts
`idle_loop`; a plain `Sprite2D` or the generated 100x100 icon is not a safe substitute.
Keep the explicit Frost `CustomSpritePath` fallback. Custom skeleton/animation lifecycle
belongs to the later animation expansion and does not block M6 or M7. Never describe an
icon-only run as full custom orb art.

The explicit `CustomChannelSfx` is also required for a clean placeholder path.
`OrbCmd.Channel` always calls `PlayChannelSfx`; leaving the custom value null/empty makes
the game probe `res://debug_audio/<custom-id>_channel.mp3`, producing a fresh global error
even though channeling succeeds.

## Type + Scenario proof

1. **Type:** clean build/package/load and OrbLoc keys.
2. **Channel:** drive the real host Card and assert the custom orb is present in
   `player.PlayerCombatState.OrbQueue` (including capacity).
3. **Passive:** call/advance the real passive lifecycle and assert its state delta.
4. **Evoke:** evoke the queued orb and independently assert its state delta/removal.
5. **Icon presentation (headed `CombatPlayer`):** identify the real `NOrb`, assert its
   `%Flash.Texture` and hover-tooltip `%Icon.Texture` both use the custom 100x100 path,
   trigger the flash, and capture the orb plus tooltip together. Separately assert the
   rendered sprite is the declared fallback scene and contains `SpineSkeleton`.

Known-good live canary (2026-07-17): `Take Shelter` channels custom `ShelterOrb`; the same
custom 100x100 icon rendered in the real smart tooltip and trigger flash, while the combat
body remained the explicit Frost Spine fallback. The headed screenshot captured both,
queue capacity was 1, passive Block was `0 -> 2`, evoke Block was `2 -> 7`, and strict
Tier 2 passed with no fresh error block. An earlier run exposed the required channel-SFX
fallback through a missing `debug_audio/..._channel.mp3` error; the clean rerun fixed it.

## Checklist

- [ ] `CustomOrbModel`; no `[Pool]`
- [ ] PassiveVal/EvokeVal/DarkenedColor and OrbLoc all supplied
- [ ] behavior reads mutable `Owner`, not canonical state
- [ ] host uses `OrbCmd.Channel<T>`
- [ ] checked custom icon path with an explicit vanilla icon fallback
- [ ] explicit Spine scene and channel-SFX fallbacks; no missing custom-id probes
- [ ] any variable `AddSlots`/`RemoveSlots` amount is clamped nonnegative before the Cmd
- [ ] channel + passive + evoke are separately observed
- [ ] custom icon appears in tooltip + trigger flash at 100x100
- [ ] combat scene remains labeled fallback; custom Spine body is later animation work
