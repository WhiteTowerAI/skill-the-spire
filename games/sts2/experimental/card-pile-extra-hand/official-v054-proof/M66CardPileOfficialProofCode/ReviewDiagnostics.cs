using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using STS2RitsuLib.CardPiles;

namespace M66CardPileOfficialProof;

internal static class ReviewDiagnostics
{
    private static readonly HashSet<CardModel> MousePressedCards = [];

    internal static void Attach(ModExtraHandCardContext context)
    {
        context.Holder.Connect(
            NHandCardHolder.SignalName.HolderMouseClicked,
            Callable.From<NCardHolder>(_ => MousePressedCards.Add(context.Card)));
    }

    internal static void LogSuccessfulPlay(CardModel card)
    {
        var mousePressed = MousePressedCards.Remove(card);
        MainFile.Logger.Info(
            $"[M66-CARD-PILE-OFFICIAL] play card={card.Id.Entry} " +
            $"mousePressed={mousePressed} pileOnEffect={card.Pile?.Type}");
    }
}
