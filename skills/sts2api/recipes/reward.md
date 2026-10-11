# Recipe: Custom Reward

Use a Mod-owned dynamic reward type for a real native reward-screen option. Register each type once
before it can be serialized or reconstructed. Keep grant side effects in `OnSelect()`; factories
only rebuild pending state.

## Registration and identity

Prefer a typed source-generated JSON payload whenever type alone cannot reproduce the pending
reward:

```csharp
using System.Text.Json.Serialization;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Saves.Runs;
using STS2RitsuLib.Combat.Rewards;

internal sealed record RewardPayload(int Amount, int Version = 1);

[JsonSerializable(typeof(RewardPayload))]
internal sealed partial class RewardJsonContext : JsonSerializerContext;

internal static class RewardIds
{
    internal static ModRewardDefinition Insight { get; set; } = null!;
}

RewardIds.Insight = ModRewardRegistry.For(MainFile.ModId).RegisterOwned(
    "insight",
    RewardJsonContext.Default.RewardPayload,
    static (save, player, payload) =>
        new InsightReward(player, payload?.Amount ?? 0));
```

The qualified ID is `{MODID}_REWARD_{LOCALSTEM}`. Keep the returned definition and use its
`RewardType`; do not derive or cast the dynamic enum yourself. A raw-global ID or replacing a
native `RewardType` is reserved for a SPEC-declared named interop contract, not normal generated
content.

The factory receives base `SerializableReward`, the owning `Player`, and the optional payload. It
must return one Reward, must tolerate a missing payload according to the declared migration/default
policy, and must not grant content, consume RNG, publish UI, or repeat selection side effects.

## Reward implementation

Read `reference/effect-primitives.md` for deterministic ordinary child effects in `OnSelect()`.
The Reward supplies its owner Player and blocking success/refusal boundary, not a generic combat
choice context or target.

Derive from `ModCustomReward(Player)`. The base supplies `RewardsSetIndex == 9`,
`IsPopulated == true`, a `gameplay_ui` description keyed by the registered qualified ID, optional
icon loading, and save-data creation. Implement the dynamic type, claim, and seen-state behavior:

```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Saves.Runs;
using STS2RitsuLib.Combat.Rewards;

internal sealed class InsightReward(Player player, int amount) : ModCustomReward(player)
{
    internal int Amount { get; } = amount;

    public override RewardType ModRewardType => RewardIds.Insight.RewardType;
    protected override string? RewardIconPath => "res://<ModName>/images/rewards/insight.png";

    protected override async Task<bool> OnSelect()
    {
        if (Amount <= 0 || !<final availability check>)
            return false;

        await <complete deterministic public-Cmd outcome>;
        return true;
    }

    public override void MarkContentAsSeen()
    {
        // Mark only concrete content whose native discovery lifecycle the reward exposes.
    }

    public override SerializableReward ToSerializable() =>
        ToSerializable(new RewardPayload(Amount), RewardJsonContext.Default.RewardPayload);
}
```

Returning `false` means unavailable/cancelled: the reward is not successfully taken and must not
partially mutate state. Complete every failure-prone selection/check before the first mutation.
Await all queued public Cmds before returning `true`. Do not call `SelectUnsynchronized()` from
generated code; the native reward host owns synchronized selection. Multiplayer-specific outcome
synchronization is deferred, so included generated outcomes must remain singleplayer and no
Multiplayer route is emitted.

Ship matching `localization/eng/gameplay_ui.json` and `localization/zhs/gameplay_ui.json` entries
under the qualified reward ID. Override `DescriptionLocTable`/`DescriptionLocKey` only when SPEC
requires another established table. A missing or invalid `RewardIconPath` produces an empty
control, not proof of a valid visible icon; custom icons require headed review.

## Presenting and inserting

Use the normal blocking custom-offer command for an Event, Relic, Rest Site, or another awaited
flow:

```csharp
await RewardsCmd.OfferCustom(player, new List<Reward>
{
    new InsightReward(player, amount),
});
```

It returns after the custom reward screen disappears. For a reward earned during combat that must
appear with room-end rewards, insert it into the concrete current `CombatRoom`:

```csharp
combatRoom.AddExtraReward(player, new InsightReward(player, amount));
```

Do not both offer and insert the same instance. `GenerateCustom` builds a set without displaying
it and is not a substitute for either normal route without a separately grounded consumer.
`RewardTakenEvent` observes a successful native claim; `RewardsScreenContinuingEvent` observes the
terminal screen continuing. They are optional lifecycle consumers, not replacements for the
Reward's own `OnSelect()` result.

## Linked reward sets

Use a base-game `LinkedRewardSet` configured by RitsuLib when the player chooses one child or takes
all children as one displayed option:

```csharp
Reward linked = LinkedRewardSets.Create(
    children,
    player,
    LinkedRewardSelectionMode.ChooseOne); // or TakeAll
```

Children stay in display order. A set requires `1..128` unique, non-null Reward instances owned by
the same `Player`; no child may be another linked set or already belong to one. Each serialized
child plus extension is limited to 256 KiB characters and one set to 4 MiB. Validate payload size
and all child construction before offering. `ChooseOne` claims the selected child and skips the
rest. `TakeAll` tries the selected child first, then the remaining children in order; a failure
before any success keeps the set pending, while a later failure skips the rest after prior gains.

## SelfTest

Follow `surfaces/reward.md`. Drive the real reward screen and the exact claim/refusal, insertion,
linked-set, save/load, localization, and headed cases selected by SPEC. A round-tripped
`SerializableReward`, direct `OnSelect` surrogate, or registration lookup is static/developer
evidence only and does not make the Reward game-observed.
