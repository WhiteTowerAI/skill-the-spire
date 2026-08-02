using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib.CardPiles;
using STS2RitsuLib.Content;

namespace M66CardPileOfficialProof;

internal static class ArchivePile
{
    internal const string LocalStem = "archive";
    internal const int Capacity = 3;

    internal static string Id { get; } =
        ModContentRegistry.GetQualifiedCardPileId(MainFile.ModId, LocalStem);

    internal static PileType Type => ModCardPileRegistry.GetPileType(Id);

    internal static async Task<bool> TryMoveAsync(
        CardModel card,
        CardPilePosition position)
    {
        var destination = Type.GetPile(card.Owner);
        if (destination == null || destination.Cards.Count >= Capacity)
            return false;

        await CardPileCmd.Add(card, Type, position);
        return ReferenceEquals(card.Pile, destination);
    }
}
