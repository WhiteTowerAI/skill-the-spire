using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Potions;
using MegaCrit.Sts2.Core.Models.Relics;

namespace M89EffectPrimitiveProbes;

internal static class WorldTransactionProbe
{
    internal static async Task<bool> ExerciseBlockingOutcome(Player owner, decimal amount)
    {
        await PlayerCmd.GainGold(amount, owner, wasStolenBack: false);
        await PlayerCmd.LoseGold(amount, owner, GoldLossType.Spent);
        await PlayerCmd.GainMaxPotionCount(1, owner);
        await PlayerCmd.LoseMaxPotionCount(1, owner);
        await CreatureCmd.Heal(owner.Creature, amount);
        await CreatureCmd.GainMaxHp(owner.Creature, amount);
        await CreatureCmd.LoseMaxHp(
            new ThrowingPlayerChoiceContext(), owner.Creature, amount, isFromCard: false);

        CardModel card = owner.RunState.CreateCard<StrikeIronclad>(owner);
        CardPileAddResult cardResult = await CardPileCmd.Add(
            card, PileType.Deck, CardPilePosition.Bottom);
        Anchor relic = await RelicCmd.Obtain<Anchor>(owner);
        PotionProcureResult potionResult = await PotionCmd.TryToProcure<EnergyPotion>(owner);

        _ = relic;
        return cardResult.success && potionResult.success;
    }
}
