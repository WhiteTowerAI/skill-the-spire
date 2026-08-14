using System.Text.Json.Serialization;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Saves.Runs;
using STS2RitsuLib.CardPiles;
using STS2RitsuLib.Combat.Rewards;
using STS2RitsuLib.Content;
using STS2RitsuLib.Scaffolding.Content;

namespace M88CompileProbes;

internal sealed record RewardPayload(int Amount, int Version = 1);

[JsonSerializable(typeof(RewardPayload))]
internal sealed partial class RewardProbeJsonContext : JsonSerializerContext;

internal static class RewardCardPileProbe
{
    private const string ModId = "M88_PROBE";

    internal static ModRewardDefinition RewardDefinition { get; private set; } = null!;

    internal static void Register()
    {
        RewardDefinition = ModRewardRegistry.For(ModId).RegisterOwned(
            "insight",
            RewardProbeJsonContext.Default.RewardPayload,
            static (_, player, payload) => new InsightReward(player, payload?.Amount ?? 0));

        ModContentPackBuilder.For(ModId)
            .CardPileOwned("archive", new ModCardPileSpec
            {
                Scope = ModCardPileScope.RunPersistent,
                Style = ModCardPileUiStyle.TopBarDeck,
                Anchor = ModCardPileAnchor.Default,
                View = ModCardPileViewSpec.DeckLike,
            })
            .Apply();
    }

    internal static async Task Offer(Player player)
    {
        var first = new InsightReward(player, 1);
        var second = new InsightReward(player, 2);
        Reward linked = LinkedRewardSets.Create(
            [first, second], player, LinkedRewardSelectionMode.ChooseOne);
        await RewardsCmd.OfferCustom(player, [linked]);
    }

    internal static void InsertCombatReward(CombatRoom room, Player player)
    {
        room.AddExtraReward(player, new InsightReward(player, 3));
    }

    internal static PileType ArchiveType => ModCardPileRegistry.GetPileType(
        ModContentRegistry.GetQualifiedCardPileId(ModId, "archive"));

    internal static async Task MoveToArchive(CardModel card)
    {
        await CardPileCmd.Add(card, ArchiveType, CardPilePosition.Bottom);
    }
}

internal sealed class InsightReward(Player player, int amount) : ModCustomReward(player)
{
    internal int Amount { get; } = amount;

    public override RewardType ModRewardType => RewardCardPileProbe.RewardDefinition.RewardType;

    protected override Task<bool> OnSelect()
    {
        return Task.FromResult(Amount > 0);
    }

    public override void MarkContentAsSeen()
    {
    }

    public override SerializableReward ToSerializable()
    {
        return ToSerializable(
            new RewardPayload(Amount),
            RewardProbeJsonContext.Default.RewardPayload);
    }
}
