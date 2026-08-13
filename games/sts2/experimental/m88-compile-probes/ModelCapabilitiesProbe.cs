using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib;
using STS2RitsuLib.Cards;
using STS2RitsuLib.Combat.AttackHits;
using STS2RitsuLib.Combat.HandSize;
using STS2RitsuLib.Combat.Healing;
using STS2RitsuLib.Combat.PlayerResources;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Models.Capabilities;

namespace M88CompileProbes;

public sealed class CapabilityState
{
    public int Count { get; set; }
}

[RegisterModelCapability(StableEntryStem = "m88_card_play")]
[RegisterDefaultModelCapability(typeof(CardModel), ModifierId = "m88_card_play_default")]
public sealed class CardPlayCounterCapability : CardPlayCapability
{
    protected override Task OnOwnerCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        return Task.CompletedTask;
    }
}

[RegisterModelCapability(StableEntryStem = "m88_card_state")]
public sealed class CardStateCapability : StatefulModelCapability<CardModel, CapabilityState>
{
    public void Increment()
    {
        MutateState(static state => state.Count++);
    }
}

[RegisterModelCapability(StableEntryStem = "m88_card_shared_effects")]
public sealed class CardSharedEffectsCapability : CardCapability, IAttackHitHookListener,
    IHealHookListener, IPlayerResourceHookListener, IMaxHandSizeModifier, ICardTypeTextModifier
{
    public override int OwnerHookOrder => -10;

    public Task BeforeAttackHit(AttackHitContext context)
    {
        context.Damage += 1m;
        return Task.CompletedTask;
    }

    public Task AfterAttackHit(AttackHitContext context)
    {
        _ = context.Results;
        return Task.CompletedTask;
    }

    public decimal ModifyHealAdditive(HealContext context, decimal amount) => 1m;

    public decimal ModifyHealMultiplicative(HealContext context, decimal amount) => 1m;

    public decimal ModifyHealAmount(HealContext context, decimal amount) => amount;

    public Task AfterPlayerEnergyGained(PlayerResourceGainContext context) => Task.CompletedTask;

    public Task AfterPlayerStarsGained(PlayerResourceGainContext context) => Task.CompletedTask;

    public int ModifyMaxHandSize(Player player, int currentMaxHandSize) => currentMaxHandSize + 1;

    public int ModifyMaxHandSizeLate(Player player, int currentMaxHandSize) => currentMaxHandSize;

    public IEnumerable<LocString> GetTypeModifiers(CardModel card) => [];
}

public static class ModelCapabilitiesProbe
{
    public static void Register(string modId)
    {
        RitsuLibFramework.RegisterModelCapability<CardPlayCounterCapability>(modId);
        RitsuLibFramework.RegisterModelCapability<CardStateCapability>(modId);
        RitsuLibFramework.RegisterModelCapability<CardSharedEffectsCapability>(modId);
        RitsuLibFramework.ConfigureDefaultModelCapabilities<CardModel>(
            modId,
            "m88_card_play_default",
            static (_, capabilities) => capabilities.Add<CardPlayCounterCapability>());
    }

    public static void ExerciseCollection(CardModel card)
    {
        var capabilities = RitsuLibFramework.GetModelCapabilities(card);
        var playCounter = capabilities.GetOrCreate<CardPlayCounterCapability>();
        var state = capabilities.GetOrCreate<CardStateCapability>();
        state.Increment();

        _ = capabilities.All;
        _ = capabilities.Contains<CardPlayCounterCapability>();
        _ = capabilities.GetAll<CardStateCapability>();
        _ = capabilities.AddForUpgrade(playCounter, allowMerge: false);
        _ = capabilities.Remove<CardPlayCounterCapability>();
        _ = capabilities.Remove(state.CapabilityId);
    }
}
