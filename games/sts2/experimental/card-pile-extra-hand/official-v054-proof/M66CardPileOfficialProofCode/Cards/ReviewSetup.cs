using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using STS2RitsuLib.CardPiles.Nodes;
using STS2RitsuLib.Scaffolding.Content;

namespace M66CardPileOfficialProof.Cards;

public sealed class ReviewSetup : ModCardTemplate
{
    public ReviewSetup()
        : base(0, CardType.Skill, CardRarity.Basic, TargetType.Self, false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var combat = CombatManager.Instance.DebugOnlyGetState()
            ?? throw new InvalidOperationException("combat state missing");
        var hand = PileType.Hand.GetPile(Owner)
            ?? throw new InvalidOperationException("native Hand missing");
        var archive = ArchivePile.Type.GetPile(Owner)
            ?? throw new InvalidOperationException("Archive missing");

        foreach (var card in hand.Cards.Where(card => !ReferenceEquals(card, this)).ToArray())
            await CardPileCmd.Add(card, PileType.Discard, CardPilePosition.Bottom);
        foreach (var card in archive.Cards.ToArray())
            await CardPileCmd.Add(card, PileType.Discard, CardPilePosition.Bottom);

        var shortcutProbes = Enumerable.Range(0, 5)
            .Select(_ => combat.CreateCard<StoredStrike>(Owner))
            .ToArray();
        foreach (var card in shortcutProbes)
            await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Bottom);

        var guard = combat.CreateCard<StoredGuard>(Owner);
        var strike = combat.CreateCard<StoredStrike>(Owner);
        var sweep = combat.CreateCard<StoredSweep>(Owner);
        if (!await ArchivePile.TryMoveAsync(guard, CardPilePosition.Bottom)
            || !await ArchivePile.TryMoveAsync(strike, CardPilePosition.Bottom)
            || !await ArchivePile.TryMoveAsync(sweep, CardPilePosition.Bottom))
        {
            throw new InvalidOperationException("could not fill Archive review row");
        }

        var overflowAccepted = await ArchivePile.TryMoveAsync(
            shortcutProbes[^1], CardPilePosition.Bottom);
        var nativeHandUi = NPlayerHand.Instance
            ?? throw new InvalidOperationException("native Hand UI missing");
        var extraHandUi = NCombatRoom.Instance?.Ui.GetChildren()
            .OfType<NModExtraHand>()
            .SingleOrDefault(node => node.Definition.Id == ArchivePile.Id)
            ?? throw new InvalidOperationException("ExtraHand UI missing");
        var archiveCards = archive.Cards.ToArray();
        var archiveInNativeHand = archiveCards.Count(
            card => nativeHandUi.GetCardHolder(card) != null);
        var archiveInExtraHand = archiveCards.Count(
            card => extraHandUi.GetHolder(card) != null);
        var probeHolders = shortcutProbes.Count(
            card => nativeHandUi.GetCardHolder(card) != null);

        if (overflowAccepted
            || hand.Cards.Count != 5
            || archiveCards.Length != ArchivePile.Capacity
            || nativeHandUi.ActiveHolders.Count != 5
            || probeHolders != 5
            || archiveInNativeHand != 0
            || archiveInExtraHand != ArchivePile.Capacity)
        {
            throw new InvalidOperationException(
                "review setup did not preserve native-Hand/ExtraHand ownership");
        }

        MainFile.Logger.Info(
            $"[M66-CARD-PILE-OFFICIAL] setup ready nativeHand={hand.Cards.Count} " +
            $"nativeActiveHolders={nativeHandUi.ActiveHolders.Count} " +
            $"archive={archiveCards.Length} archiveInNativeHand={archiveInNativeHand} " +
            $"archiveInExtraHand={archiveInExtraHand} overflowRejected={!overflowAccepted} " +
            $"archiveOrder={string.Join(">", archiveCards.Select(card => card.Id.Entry))}");
    }

    protected override void OnUpgrade()
    {
    }
}
