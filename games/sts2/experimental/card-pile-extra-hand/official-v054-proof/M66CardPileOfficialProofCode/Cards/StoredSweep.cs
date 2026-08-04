using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace M66CardPileOfficialProof.Cards;

public sealed class StoredSweep : ModCardTemplate
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(4m, ValueProp.Move)];

    public StoredSweep()
        : base(1, CardType.Attack, CardRarity.Basic, TargetType.AllEnemies, false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .TargetingAllOpponents(CombatManager.Instance.DebugOnlyGetState()!)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
        ReviewDiagnostics.LogSuccessfulPlay(this);
    }

    protected override void OnUpgrade()
    {
    }
}
