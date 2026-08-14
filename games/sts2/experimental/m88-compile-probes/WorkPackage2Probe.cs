using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Models;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Utils;

namespace M88CompileProbes;

public sealed class AfflictionProbe : ModAfflictionTemplate
{
    public override bool HasExtraCardText => true;
    public override bool IsStackable => true;

    public override bool CanAfflict(CardModel card) =>
        base.CanAfflict(card) && card.Type == CardType.Skill;
}

public sealed class GoodModifierProbe : ModModifierTemplate
{
    protected override void AfterRunCreated(RunState runState)
    {
        _ = runState;
    }

    protected override void AfterRunLoaded(RunState runState)
    {
        _ = runState;
    }
}

public sealed class BadModifierProbe : ModModifierTemplate;

public sealed class RunGlobalEffectProbe : HookedSingletonModel
{
    public RunGlobalEffectProbe() : base(HookType.Run)
    {
    }
}

public sealed class CombatGlobalEffectProbe : HookedSingletonModel
{
    public CombatGlobalEffectProbe() : base(HookType.Combat)
    {
    }
}

public sealed class StandaloneRestSiteOwnerProbe : HookedSingletonModel
{
    private static readonly AttachedState<Player, bool> KeepRemainingOnce = new();

    public StandaloneRestSiteOwnerProbe() : base(HookType.Run)
    {
    }

    public override bool TryModifyRestSiteOptions(
        Player player,
        ICollection<RestSiteOption> options)
    {
        if (options.Any(static option => option.OptionId == RestSiteOptionProbe.StableOptionId))
            return false;

        options.Add(new RestSiteOptionProbe(player));
        return true;
    }

    public override bool ShouldDisableRemainingRestSiteOptions(Player player)
    {
        _ = player;
        if (!KeepRemainingOnce.GetValueOrDefault(player))
            return true;

        KeepRemainingOnce.Remove(player);
        return false;
    }

    internal static void MarkSuccessfulUse(Player player, bool keepRemaining)
    {
        if (keepRemaining)
            KeepRemainingOnce[player] = true;
    }
}

public sealed class RestSiteOptionProbe(Player owner) : ModRestSiteOptionTemplate(owner)
{
    public const string StableOptionId = "M88_PROBE_REST_SITE";

    public override string OptionId => StableOptionId;

    public override LocString Description =>
        new("rest_site_ui", "OPTION_HEAL.description");

    public override Task<bool> OnSelect()
    {
        StandaloneRestSiteOwnerProbe.MarkSuccessfulUse(Owner, keepRemaining: true);
        return Task.FromResult(true);
    }
}

public static class WorkPackage2Probe
{
    public static ModContentPackBuilder BuildPack(string modId) =>
        ModContentPackBuilder.For(modId)
            .Affliction<AfflictionProbe>()
            .GoodModifier<GoodModifierProbe>(modifierListSortOrder: 10)
            .BadModifier<BadModifierProbe>(modifierListSortOrder: 20)
            .MutuallyExclusiveModifierGroup(
                typeof(GoodModifierProbe),
                typeof(BadModifierProbe))
            .Singleton<RunGlobalEffectProbe>()
            .Singleton<CombatGlobalEffectProbe>()
            .Singleton<StandaloneRestSiteOwnerProbe>();

    public static async Task ExerciseAffliction(CardModel card, IEnumerable<CardModel> cards)
    {
        _ = await CardCmd.Afflict<AfflictionProbe>(card, amount: 2m);
        _ = await CardCmd.AfflictAndPreview<AfflictionProbe>(cards, amount: 1m);
        CardCmd.ClearAffliction(card);
    }
}
