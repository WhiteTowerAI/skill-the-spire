# Recipe: Custom Orb

> A custom Orb under the pinned STS2 `0.107.1` / RitsuLib `0.6.7` profile.

## Contract and registration

A useful Orb has four distinct invariants: registration, channel presence, passive
behavior, and evoke behavior/removal. Register it once:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Orb<<Name>Orb>()
    .Apply();
```

Use `ModOrbTemplate`; do not add `[Pool]` or rely on constructor discovery.
RitsuLib derives `MOD_ORB_TYPENAME`, so `ShelterOrb` in `ExampleMod` becomes
`EXAMPLE_MOD_ORB_SHELTER_ORB`.

## Skeleton

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Orbs;

public sealed class <Name>Orb : ModOrbTemplate
{
    protected override string ChannelSfx =>
        "event:/sfx/characters/defect/defect_frost_channel";

    public override Color DarkenedColor => new("7860a7");
    public override decimal PassiveVal => ModifyOrbValue(2m);
    public override decimal EvokeVal => ModifyOrbValue(5m);
    public override ModOrbValueDisplayMode ValueDisplayMode =>
        ModOrbValueDisplayMode.Contextual;

    public override OrbAssetProfile AssetProfile =>
        ContentAssetProfiles.Orb("frost_orb");

    public override Task BeforeTurnEndOrbTrigger(PlayerChoiceContext choiceContext) =>
        Passive(choiceContext, null);

    public override async Task Passive(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        if (target is not null)
            throw new InvalidOperationException("This Orb does not target creatures");
        Trigger();
        await CreatureCmd.GainBlock(
            Owner.Creature, PassiveVal, ValueProp.Unpowered, null);
    }

    public override async Task<IEnumerable<Creature>> Evoke(
        PlayerChoiceContext choiceContext)
    {
        await CreatureCmd.GainBlock(
            Owner.Creature, EvokeVal, ValueProp.Unpowered, null);
        return new[] { Owner.Creature };
    }
}
```

`ContentAssetProfiles.Orb("frost_orb")` is the checked placeholder contract: Frost icon
plus Frost Spine combat scene. A generated 100x100 icon may replace only `IconPath`; it
does not promote a custom combat body. Keep the explicit native `ChannelSfx`, because
channeling always plays one and an empty custom value probes a missing debug-audio file.

## Host commands and domains

Read `reference/effect-primitives.md` for channel/evoke/slot signatures and boundaries. The host
Card/Relic/Power owns channeling; the Orb's native passive and evoke callbacks supply their own
`choiceContext`, `Owner`, and optional passive target. Direct `OrbCmd.Passive` remains diagnostic
only and is not authoring or proof of the per-turn trigger.

## Optional shared capability routes

Keep channel/passive/evoke in their native methods. For a separable Orb-owned behavior/state
bundle, read `reference/model-capabilities.md`; for lifecycle/persistence/RNG, read
`reference/lifecycle-state-rng.md`; and for reachable per-hit attack, healing, Energy/Stars-gain
response, or maximum hand size, read `reference/shared-effect-hooks.md`. Implement on the Orb or
typed capability, with queue reachability, neutral behavior, display refresh, and combat cleanup.

## SPEC `hook participation`

Channel, passive, and evoke are the Orb acting. A SPEC `hook participation` block is the engine
asking the queued Orb for a number or a decision while resolving something else — a fourth,
independent behavior. Read `reference/model-hook-participation.md`.

An Orb reaches the combat-scope set only, and `Owner` is a `Player`, so a subject guard goes
through `Owner.Creature`. The participation holds while the Orb is in the queue, so it stops when
the Orb is evoked out — state that in SPEC if the design depends on it.

## Localization

Ship matching `localization/eng/orbs.json` and `localization/zhs/orbs.json` using the exact
public entry:

```json
{
  "<MOD>_ORB_<TYPE>.title": "Display Name",
  "<MOD>_ORB_<TYPE>.description": "Orb: Gains [gold]Block[/gold].",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]Passive:[/gold] At the end of turn, gain [blue]{Passive}[/blue] [gold]Block[/gold].\n[gold]Evoke:[/gold] Gain [blue]{Evoke}[/blue] [gold]Block[/gold]."
}
```

```json
{
  "<MOD>_ORB_<TYPE>.title": "显示名称",
  "<MOD>_ORB_<TYPE>.description": "充能球：获得[gold]格挡[/gold]。",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]被动：[/gold]在回合结束时，获得[blue]{Passive}[/blue]点[gold]格挡[/gold]。\n[gold]激发：[/gold]获得[blue]{Evoke}[/blue]点[gold]格挡[/gold]。"
}
```

This is the vanilla `FROST_ORB` shape (`reference/vanilla-text-style.md`, Orb row): a short
general `.description`, and a two-line `.smartDescription` whose values are `[blue]`.

## Verification

The nearest `CombatPlayer` suite must assert queue capacity/presence after channel, the
passive post-state, evoke post-state, and removal.

Visible icon support additionally needs the real smart tooltip and trigger flash. The
persistent body must remain labeled as the Frost fallback until a compatible custom Spine
scene is separately proven.
