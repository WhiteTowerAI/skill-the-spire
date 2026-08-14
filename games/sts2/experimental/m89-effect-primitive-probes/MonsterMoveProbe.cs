using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace M89EffectPrimitiveProbes;

internal static class MonsterMoveProbe
{
    internal static async Task ExerciseMove(
        MonsterModel monster,
        IReadOnlyList<Creature> targets,
        decimal amount)
    {
        var attack = await DamageCmd.Attack(amount)
            .FromMonster(monster)
            .Execute(null);

        var choiceContext = new ThrowingPlayerChoiceContext();
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, monster.Creature, amount, monster.Creature, null);
        await PowerCmd.Apply<WeakPower>(
            choiceContext, targets, amount, monster.Creature, null);
        await CreatureCmd.GainBlock(
            monster.Creature, amount, ValueProp.Move, cardPlay: null);
        await CreatureCmd.Heal(monster.Creature, amount);
        _ = attack.Results;
    }
}
