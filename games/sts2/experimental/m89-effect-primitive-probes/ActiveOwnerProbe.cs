using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Orbs;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace M89EffectPrimitiveProbes;

internal static class ActiveOwnerProbe
{
    internal static async Task ExerciseCardLikeSequence(
        PlayerChoiceContext choiceContext,
        CardModel cardSource,
        CardPlay cardPlay,
        Creature target,
        IReadOnlyList<Creature> targets,
        decimal amount)
    {
        Player player = cardSource.Owner;
        Creature sourceCreature = player.Creature;
        ICombatState combatState = cardSource.CombatState ??
            throw new InvalidOperationException("Card attack requires a live combat state.");

        var attack = await DamageCmd.Attack(amount)
            .FromCard(cardSource)
            .Targeting(target)
            .Execute(choiceContext);
        var allTargetAttack = await DamageCmd.Attack(amount)
            .FromCard(cardSource)
            .TargetingAllOpponents(combatState)
            .Execute(choiceContext);
        var randomMultiHitAttack = await DamageCmd.Attack(amount)
            .WithHitCount(2)
            .FromCard(cardSource)
            .TargetingRandomOpponents(combatState)
            .Execute(choiceContext);
        var unpoweredAttack = await DamageCmd.Attack(amount)
            .FromCard(cardSource)
            .Targeting(target)
            .Unpowered()
            .Execute(choiceContext);
        IEnumerable<DamageResult> directDamage = await CreatureCmd.Damage(
            choiceContext, target, amount, ValueProp.Unpowered, sourceCreature, cardSource);

        decimal modifiedBlock = await CreatureCmd.GainBlock(
            sourceCreature, amount, ValueProp.Move, cardPlay);
        await CreatureCmd.LoseBlock(sourceCreature, amount);
        await CreatureCmd.Heal(sourceCreature, amount);
        await CreatureCmd.GainMaxHp(sourceCreature, amount);
        await CreatureCmd.LoseMaxHp(choiceContext, sourceCreature, amount, isFromCard: true);

        StrengthPower? applied = await PowerCmd.Apply<StrengthPower>(
            choiceContext, target, amount, sourceCreature, cardSource);
        IReadOnlyList<StrengthPower> appliedMany = await PowerCmd.Apply<StrengthPower>(
            choiceContext, targets, amount, sourceCreature, cardSource);
        if (applied is not null)
        {
            int newAmount = await PowerCmd.ModifyAmount(
                choiceContext, applied, -amount, sourceCreature, cardSource);
            await PowerCmd.Remove(applied);
            _ = newAmount;
        }
        await PowerCmd.Remove<StrengthPower>(target);

        await PlayerCmd.GainEnergy(amount, player);
        await PlayerCmd.LoseEnergy(amount, player);
        await PlayerCmd.GainStars(amount, player);
        await PlayerCmd.LoseStars(amount, player);

        IEnumerable<CardModel> drawn = await CardPileCmd.Draw(
            choiceContext, amount, player, fromHandDraw: false);
        await CardCmd.Discard(choiceContext, cardSource);
        await CardCmd.Discard(choiceContext, drawn);
        await CardCmd.DiscardAndDraw(choiceContext, drawn, cardsToDraw: 1);
        await CardCmd.Exhaust(
            choiceContext, cardSource, causedByEthereal: false, skipVisuals: false);

        CardModel generated = player.Creature.CombatState!.CreateCard<Dazed>(player);
        CardPileAddResult generatedResult = await CardPileCmd.AddGeneratedCardToCombat(
            generated, PileType.Discard, player, CardPilePosition.Bottom);

        await OrbCmd.Channel<FrostOrb>(choiceContext, player);
        await OrbCmd.EvokeNext(choiceContext, player);
        await OrbCmd.EvokeLast(choiceContext, player);
        await OrbCmd.AddSlots(player, 1);
        OrbCmd.RemoveSlots(player, 1);

        _ = directDamage;
        _ = attack.Results;
        _ = allTargetAttack.Results;
        _ = randomMultiHitAttack.Results;
        _ = unpoweredAttack.Results;
        _ = modifiedBlock;
        _ = appliedMany;
        _ = generatedResult;
    }
}
