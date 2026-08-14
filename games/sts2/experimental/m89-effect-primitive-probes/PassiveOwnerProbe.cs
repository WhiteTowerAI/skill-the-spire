using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.ValueProps;

namespace M89EffectPrimitiveProbes;

internal static class PassiveOwnerProbe
{
    internal static async Task ExerciseAsyncOwnerHook(Player owner, Creature subject, decimal amount)
    {
        await PlayerCmd.GainEnergy(amount, owner);
        await PlayerCmd.GainStars(amount, owner);
        await CreatureCmd.GainBlock(subject, amount, ValueProp.Unpowered, cardPlay: null);
        await CreatureCmd.Heal(subject, amount);

        CardModel generated = owner.Creature.CombatState!.CreateCard<Dazed>(owner);
        CardPileAddResult result = await CardPileCmd.AddGeneratedCardToCombat(
            generated, PileType.Discard, owner, CardPilePosition.Bottom);
        _ = result;
    }
}
