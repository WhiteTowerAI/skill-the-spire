using Godot;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Unlocks;
using STS2RitsuLib.Scaffolding.Content;

namespace M88CompileProbes;

public sealed class ActProbe : ModActTemplate
{
    public override int Index => 0;
    public override bool IsDefault => false;
    public override Color MapTraveledColor => new("28503c");
    public override Color MapUntraveledColor => new("8fba9b");
    public override Color MapBgColor => new("5d806a");
    public override string[] BgMusicOptions => ["event:/music/act1_a1_v1"];
    public override string[] MusicBankPaths => ["res://banks/desktop/act1_a1.bank"];
    public override string AmbientSfx => "event:/sfx/ambience/act1_ambience";
    protected override int BaseNumberOfRooms => 15;
    public override string ChestSpineSkinNameNormal => "act1";
    public override string ChestSpineSkinNameStroke => "act1_stroke";
    public override string ChestOpenSfx => "event:/sfx/ui/treasure/treasure_act1";

    public override ActAssetProfile AssetProfile =>
        ContentAssetProfiles.FromVanillaActId("overgrowth") with
        {
            ChestSpineResourcePath =
                "res://animations/backgrounds/treasure_room/chest_room_act_1_skel_data.tres",
        };

    public override IEnumerable<EncounterModel> BossDiscoveryOrder =>
        [ModelDb.Encounter<VantomBoss>()];

    public override IEnumerable<AncientEventModel> AllAncients =>
        [ModelDb.AncientEvent<AncientProbe>()];

    public override IEnumerable<EventModel> AllEvents =>
        [ModelDb.Event<AromaOfChaos>()];

    public override IEnumerable<EncounterModel> GenerateAllEncounters() =>
        [
            ModelDb.Encounter<FuzzyWurmCrawlerWeak>(),
            ModelDb.Encounter<FlyconidNormal>(),
            ModelDb.Encounter<ByrdonisElite>(),
            ModelDb.Encounter<VantomBoss>(),
        ];

    public override bool IsUnlocked(UnlockState unlockState) => true;

    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState unlockState) =>
        AllAncients;

    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
    }

    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) =>
        new(MapPointTypeCounts.StandardRandomUnknownCount(mapRng), restCount: 7);
}

public sealed class AncientProbe : ModAncientEventTemplate
{
    private EventOption LeaveOption =>
        new(this, () =>
        {
            Done();
            return Task.CompletedTask;
        }, InitialOptionKey("LEAVE"));

    public override IEnumerable<EventOption> AllPossibleOptions => [LeaveOption];

    public override bool IsValidForAct(ActModel act) => act is ActProbe;

    public override Color DialogueColor => new("28503c");

    public override EventAssetProfile AssetProfile =>
        ContentAssetProfiles.Event("NEOW");

    public override AncientEventPresentationAssetProfile AncientPresentationAssetProfile =>
        ContentAssetProfiles.AncientPresentation("NEOW");

    protected override IReadOnlyList<EventOption> GenerateInitialOptions() => [LeaveOption];
}

public static class WorkPackage3Probe
{
    public static ModContentPackBuilder BuildPack(string modId) =>
        ModContentPackBuilder.For(modId)
            .Act<ActProbe>()
            .ActAncient<ActProbe, AncientProbe>()
            .ActEnterForce<ActProbe>(0, priority: 100, static ctx => !ctx.IsMultiplayer)
            .ActEnterUniformPool(1)
            .ActEnterUniformPoolCandidate<ActProbe>(1, static ctx => !ctx.IsMultiplayer)
            .ActEnterWeightedPool(2)
            .ActEnterWeightedPoolBaseline(2, static ctx => 1d)
            .ActEnterWeightedPoolCandidate<ActProbe>(2, static ctx => !ctx.IsMultiplayer, static ctx => 2d);
}
