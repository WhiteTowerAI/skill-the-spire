# Recipe: Custom Reward

Use a Mod-owned dynamic reward type for a custom option shown in the native rewards UI. A Reward
owns its displayed description and icon, selection success or refusal, its deterministic side
effect, an optional save payload, and reconstruction after a combat-room save/load. It is not a
generic immediate grant helper. Register each type once before it can be serialized or
reconstructed; keep grant side effects in `OnSelect()`, while factories only rebuild pending
state. Read the owner recipe for each concrete side effect, and `reference/lifecycle-state-rng.md`
only when the outcome subscribes beyond its own claim or needs deterministic RNG.

## DESIGN and SPEC vocabulary

Settle and write:

- the stable Mod-local reward identity and the player/context that creates it;
- the native offer route: a blocking custom reward screen, or insertion into the current
  combat's end rewards;
- the description in English and Simplified Chinese (one short sentence with `[blue]` counts and
  `[gold]` glossary terms and named Card/Relic/Potion names, per
  `reference/vanilla-text-style.md`), a checked icon or explicit empty-control fallback, display
  order only when the default custom slot is unsuitable, and content-seen behavior;
- availability and cancellation/refusal conditions, ordered selection side effects, and the exact
  success result (`false` keeps the reward untaken);
- every fact needed to reproduce the same pending reward after save/load, with a versioned typed
  payload when the type alone is insufficient;
- independent rewards versus one linked set, and for a set `choose one` versus `take all`, child
  display order, and failure behavior; and
- a real reward-screen SelfTest covering claim, refusal/cancel, leave/continue, and combat-room
  save/load reconstruction.

The selection outcome and the reconstructed payload describe the same deterministic reward.
In multiplayer each player claims its own rewards and the game's reward synchronizer replays the
claim on every peer, so a reward's claim effect acts on its own player only. Multiplayer claiming
of a Mod reward is unobserved, and host-authoritative side effects are deferred.

## Registration and identity

Prefer a typed source-generated JSON payload whenever the type alone cannot reproduce the pending
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

The qualified id is `{MODID}_REWARD_{LOCALSTEM}`. Keep the returned definition and use its
`RewardType`; never derive or cast the dynamic enum. A raw-global id or replacing a native
`RewardType` is reserved for a SPEC-declared named interop contract.

The factory receives the base `SerializableReward`, the owning `Player`, and the optional payload.
It returns one Reward, tolerates a missing payload per the declared migration/default policy, and
never grants content, consumes RNG, publishes UI, or repeats selection side effects.

## Reward implementation

Derive from `ModCustomReward(Player)`. The base supplies `RewardsSetIndex == 9`,
`IsPopulated == true`, a `gameplay_ui` description keyed by the qualified id, optional icon
loading, and save-data creation. Implement the dynamic type, claim, and seen-state behavior:

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

`OnSelect()` supplies its exact owner Player and an awaited blocking transaction, but no general
combat `PlayerChoiceContext`, target Creature, Card source, or `CardPlay`. Lower known run-content
acquisition and other primitives whose inputs truly exist through `reference/effect-primitives.md`;
a combat-only primitive needs a separately selected callback that exposes its context. Finish every
failure-prone check before the first mutation, await the ordered sequence, inspect Card/Potion
acquisition results, return `false` on rejection or cancellation with no partial mutation, and
return `true` only after the complete result. Serialization and reconstruction never run the
effect. Never call `SelectUnsynchronized()`; the native reward host owns synchronized selection.

Ship matching `localization/eng/gameplay_ui.json` and `localization/zhs/gameplay_ui.json` entries
under the qualified reward id. Override `DescriptionLocTable`/`DescriptionLocKey` only when SPEC
requires another established table. A missing or invalid `RewardIconPath` produces an empty
control, not proof of a visible icon; custom icons need headed review.

## Presenting and inserting

Use the blocking custom-offer command from an Event, Relic, Rest Site, or other awaited flow; it
returns after the custom reward screen disappears:

```csharp
await RewardsCmd.OfferCustom(player, new List<Reward>
{
    new InsightReward(player, amount),
});
```

For a reward earned during combat that must appear with room-end rewards, insert it into the
concrete current `CombatRoom`:

```csharp
combatRoom.AddExtraReward(player, new InsightReward(player, amount));
```

Never both offer and insert one instance. `GenerateCustom` builds a set without displaying it and
substitutes for neither route. `RewardTakenEvent` observes a successful native claim and
`RewardsScreenContinuingEvent` the terminal screen continuing; both are optional lifecycle
consumers, never replacements for the Reward's own `OnSelect()` result.

## Linked reward sets

Use a base-game `LinkedRewardSet` configured by RitsuLib when the player chooses one child or takes
all children as one displayed option:

```csharp
Reward linked = LinkedRewardSets.Create(
    children,
    player,
    LinkedRewardSelectionMode.ChooseOne); // or TakeAll
```

Children stay in display order. A set requires `1..128` unique, non-null Rewards owned by the same
`Player`; no child may be another linked set or already belong to one. Each serialized child plus
extension is limited to 256 KiB characters and one set to 4 MiB; validate payload size and all
child construction before offering. `ChooseOne` claims the selected child and skips the rest.
`TakeAll` tries the selected child first, then the rest in order; a failure before any success
keeps the set pending, while a later failure skips the rest after prior gains.

## Proof matrix

Drive the real native rewards host SPEC selects:

1. assert one registered qualified reward type and exact description/icon/order;
2. drive an unavailable or cancelled selection and assert `OnSelect()` returns `false`, no side
   effect occurs, and the reward stays untaken;
3. drive a successful selection, await its complete effect, and assert exact post-state, one
   `RewardTakenEvent`, and no duplicate application;
4. for combat insertion, finish the real combat and assert the extra reward appears once; for a
   blocking offer, assert the caller resumes only after the reward screen closes;
5. save/load with the reward pending and assert its owner, type, payload, description, and future
   outcome are reconstructed without applying the outcome early;
6. for linked sets, test the chosen mode, child order, failed first claim, skip behavior, and
   rejection of duplicates, cross-player children, nesting, already-linked children, and
   size-limit overflow; and
7. headed review checks icon, description, focus, controller selection, cancellation, and the
   continue flow.

Compile, serialized JSON, a round-tripped `SerializableReward`, a direct `OnSelect` surrogate, or
a registration lookup establishes neither a displayed reward nor a successful claim.
