# Recipe: Custom Orb

> Known-good on STS2 `0.107.1` with RitsuLib `0.4.67` compat. The R3 proof registered
> `ShelterOrb`, channeled it on a zero-slot Ironclad, proved passive and evoke Block,
> and verified removal in a RitsuLib-only run.

## Contract and registration

A useful Orb has four distinct invariants: registration, channel presence, passive
behavior, and evoke behavior/removal. Register it once:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Orb<<Name>Orb>()
    .Apply();
```

Use `ModOrbTemplate`; do not add `[Pool]` or rely on historical constructor discovery.
RitsuLib derives `MOD_ORB_TYPENAME`, so `ShelterOrb` becomes
`RITSU_CARD_PROOF_ORB_SHELTER_ORB`.

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

```csharp
await OrbCmd.Channel<<Name>Orb>(choiceContext, player);
await OrbCmd.Passive(choiceContext, orb, null);
await OrbCmd.EvokeNext(choiceContext, player);
```

`Channel<T>` adds one slot when both base slots and queue capacity are zero. Clamp variable
slot changes nonnegative before `AddSlots`/`RemoveSlots`; negative values can reverse the
intended direction.

## Localization

Ship `localization/eng/orbs.json` using the exact public entry:

```json
{
  "<MOD>_ORB_<TYPE>.title": "Display Name",
  "<MOD>_ORB_<TYPE>.description": "Passive and Evoke rules.",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]Passive:[/gold] {Passive}.\n[gold]Evoke:[/gold] {Evoke}."
}
```

## Verification

The nearest `CombatPlayer` suite must assert queue capacity/presence after channel, the
passive post-state, evoke post-state, and removal. The R3 proof observed capacity 1,
channel count 1, Block `0 -> 2 -> 7`, remaining 0, and title `Shelter Orb`.

Visible icon support additionally needs the real smart tooltip and trigger flash. The
persistent body must remain labeled as the Frost fallback until a compatible custom Spine
scene is separately proven.
