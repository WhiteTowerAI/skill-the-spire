using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace M89EffectPrimitiveProbes;

internal static class AttachedOwnerProbe
{
    internal static async Task ExerciseCardAttachment(
        PlayerChoiceContext choiceContext,
        CardModel hostCard,
        CardPlay cardPlay,
        Creature? selectedTarget,
        decimal amount)
    {
        await CreatureCmd.GainBlock(
            hostCard.Owner.Creature, amount, ValueProp.Unpowered, cardPlay);
        if (selectedTarget is not null)
        {
            await CreatureCmd.Damage(
                choiceContext,
                selectedTarget,
                amount,
                ValueProp.Unpowered,
                hostCard.Owner.Creature,
                hostCard);
        }
    }

    internal static async Task<IEnumerable<Creature>> ExerciseOrbCallback(
        PlayerChoiceContext choiceContext,
        OrbModel orb,
        Creature? selectedTarget,
        decimal amount)
    {
        Creature owner = orb.Owner.Creature;
        await CreatureCmd.GainBlock(owner, amount, ValueProp.Unpowered, cardPlay: null);
        if (selectedTarget is not null)
        {
            await CreatureCmd.Damage(
                choiceContext, selectedTarget, amount, ValueProp.Unpowered, owner, null);
            return [selectedTarget];
        }
        return [owner];
    }
}

internal sealed class AfflictionCallbackProbe : ModAfflictionTemplate
{
    public override async Task OnPlay(PlayerChoiceContext choiceContext, Creature? target)
    {
        await CreatureCmd.GainBlock(
            Card.Owner.Creature, Amount, ValueProp.Unpowered, cardPlay: null);
        if (target is not null)
        {
            await CreatureCmd.Damage(
                choiceContext,
                target,
                Amount,
                ValueProp.Unpowered,
                Card.Owner.Creature,
                Card);
        }
    }
}
