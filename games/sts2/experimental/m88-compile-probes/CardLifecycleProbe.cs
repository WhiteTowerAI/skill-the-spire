using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib;
using STS2RitsuLib.Cards;
using STS2RitsuLib.Cards.FreePlay;
using STS2RitsuLib.Cards.Transforms;

namespace M88CompileProbes;

public sealed class ProcessCardPlayListener : ICardOnPlayHookListener
{
    public Task<bool> BeforeCardOnPlay(BeforeCardOnPlayContext context) => Task.FromResult(false);

    public Task AfterCardOnPlay(AfterCardOnPlayContext context) => Task.CompletedTask;
}

public static class CardLifecycleProbe
{
    public static void Register(string modId)
    {
        RitsuLibFramework.RegisterCardOnPlayHookListener(new ProcessCardPlayListener());
        RitsuLibFramework.RegisterFreePlayBinding($"{modId}:probe", static play => play.IsAutoPlay);

        var transforms = RitsuLibFramework.GetCardTransformRegistry(modId);
        transforms.Register("all", static (ModCardTransformContext context) => { _ = context.OriginalPileIndex; });
        transforms.Register<CardModel, CardModel>("pair", static (_, _) => { });
        transforms.RegisterFrom<CardModel>("from", static (_, _) => { });
        transforms.RegisterTo<CardModel>("to", static (_, _) => { });
    }

    public static void ExerciseFreePlay(CardModel card, CardPlay play)
    {
        FreePlayBindingRegistry.MarkCardFreeNextPlay(card);
        FreePlayBindingRegistry.MarkCardFreeThisTurn(card);
        card.SetToFreeForRestOfTurn();
        FreePlayBindingRegistry.MarkCardFreeThisCombat(card);
        FreePlayBindingRegistry.MarkCurrentPlayFree(play);

        _ = FreePlayBindingRegistry.IsCardFreeForUpcomingPlay(card);
        _ = FreePlayBindingRegistry.Resolve(play);
        _ = FreePlayBindingRegistry.IsFreeForPlay(play);
    }
}
