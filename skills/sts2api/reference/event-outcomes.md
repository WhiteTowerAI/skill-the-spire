# Event Outcome Vocabulary

Grounded against STS2 0.107.1 by inventorying all 68 vanilla `EventModel` classes. This page extends
`recipes/event.md`; it does not change event registration, localization, or portrait rules.

## Supported outcome families

| Family | Public surface | Required behavior |
|---|---|---|
| Immediate run-state effect | `PlayerCmd`, `CreatureCmd`, `CardPileCmd`, `CardCmd`, `RelicCmd`, `PotionCmd` | `await` asynchronous Cmds, then change the event page |
| Multi-page choice | `SetEventState(description, options)` | Localize every page and every option key |
| Conditional/locked option | condition plus an `EventOption` callback or null callback | Decide from the mutable event owner/run, never the canonical model |
| Card-selection overlay | `CardSelectCmd.FromDeckFor*` | Await the selection screen before mutating the card or event state |
| Custom reward overlay | `RewardsCmd.OfferCustom` | Await the reward screen before marking the event finished or advancing |
| Special combat, then resume | `EnterCombatWithoutExitingEvent<T>(..., true)` plus `Resume` | Event must be shared; restore an explicit post-combat page |
| Special combat, then map | `EnterCombatWithoutExitingEvent<T>(..., false)` | Event must be shared; do not call `Resume` |
| Extra special-combat rewards | the first argument to `EnterCombatWithoutExitingEvent` | Construct rewards for their owning player before entering combat |

An option method may compose several immediate effects in order. Keep the order visible in
the option description and await each blocking operation. Do not mutate raw HP, gold,
deck, relic, potion, or reward collections.

## Immediate effects

These are the grounded Event-level forms. Use `DynamicVars` for displayed numbers when the
value appears in localized text.

```csharp
using MegaCrit.Sts2.Core.Entities.Gold;

var owner = Owner ?? throw new InvalidOperationException("Event has no owner");

await PlayerCmd.GainGold(gold, owner);
await PlayerCmd.LoseGold(cost, owner, GoldLossType.Spent);

await CreatureCmd.Heal(owner.Creature, heal);
await CreatureCmd.GainMaxHp(owner.Creature, maxHpGain);
await CreatureCmd.LoseMaxHp(
    new ThrowingPlayerChoiceContext(), owner.Creature, maxHpLoss, isFromCard: false);
await CreatureCmd.Damage(
    new ThrowingPlayerChoiceContext(), owner.Creature, hpLoss,
    ValueProp.Unblockable | ValueProp.Unpowered, null, null);
```

For a known card, create it through the run and add it to the real deck:

```csharp
var card = owner.RunState.CreateCard<MyCard>(owner);
CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck));
```

For relics and potions, prefer their public procurement commands or a reward screen:

```csharp
await RelicCmd.Obtain<MyRelic>(owner);
await PotionCmd.TryToProcure(ModelDb.Potion<MyPotion>().ToMutable(), owner);
```

`TryToProcure` honestly handles potion-slot constraints. Use a `PotionReward` when the
design intentionally lets the reward UI own that interaction.

## Blocking card selections

The supported deck-selection families are add, remove, upgrade, transform, and enchant.
Selection screens are blocking UI: await them, apply the result, and only then call
`SetEventState` or `SetEventFinished`.

```csharp
var selected = (await CardSelectCmd.FromDeckForUpgrade(
    owner,
    new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 1)))
    .FirstOrDefault();
if (selected != null)
    CardCmd.Upgrade(selected);
```

```csharp
var selected = (await CardSelectCmd.FromDeckForRemoval(
    owner,
    new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 1)))
    .ToList();
await CardPileCmd.RemoveFromDeck(selected);
```

```csharp
var selected = (await CardSelectCmd.FromDeckForTransformation(
    owner,
    new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1)))
    .FirstOrDefault();
if (selected != null)
    await CardCmd.TransformToRandom(selected, Rng, CardPreviewStyle.EventLayout);
```

```csharp
var enchantment = ModelDb.Enchantment<MyEnchantment>();
var selected = (await CardSelectCmd.FromDeckForEnchantment(
    owner,
    enchantment,
    amount,
    new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
    .FirstOrDefault();
if (selected != null)
    CardCmd.Enchant<MyEnchantment>(selected, amount);
```

Filter candidates before presenting a selection when the effect has eligibility rules.
If no candidate exists, generate a localized locked option rather than an option that opens
an empty selection screen.

## Custom rewards

`RewardsCmd.OfferCustom` is the normal blocking overlay for a chosen reward or a bundle of
rewards. Reward constructors own a `Player`.

```csharp
await RewardsCmd.OfferCustom(owner, new List<Reward>
{
    new GoldReward(17, owner),
});

SetEventFinished(PageDescription("CACHE_CLAIMED"));
```

Other grounded reward types include `CardReward`, `SpecialCardReward`, `RelicReward`, and
`PotionReward`. Do not advance the Event before the awaited overlay completes.

## Multi-page and conditional options

Use `SetEventState` when the Event should remain active:

```csharp
SetEventState(
    PageDescription("PREPARED"),
    new[]
    {
        new EventOption(this, ChallengeGuardian,
            ModOptionKey("PREPARED", "CHALLENGE_GUARDIAN")),
    });
```

RitsuLib's `ModOptionKey(pageKey, optionKey)` keeps an explicit `EventOption` aligned with
the flat nested localization key. Pass a null callback to generate a locked option when
its precondition is false. Recompute conditions from `Owner` and its `RunState`; the
canonical model has no owner.

## Special combat

Any Event that enters another room must be shared:

```csharp
public override bool IsShared => true;
```

### Resume the Event after combat

Use this for a fight that unlocks another Event page:

```csharp
private Task ChallengeGuardian()
{
    EnterCombatWithoutExitingEvent<MyEncounter>(
        Array.Empty<Reward>(),
        shouldResumeAfterCombat: true);
    return Task.CompletedTask;
}

// How many times the engine resumed this instance; the SelfTest asserts it.
public int ResumeCount { get; private set; }

public override Task Resume(AbstractRoom exitedRoom)
{
    if (exitedRoom is not CombatRoom { Encounter: MyEncounter })
        throw new InvalidOperationException($"Unexpected room resumed into event: {exitedRoom}");

    ResumeCount++;
    SetEventState(
        PageDescription("RETURNED"),
        new[]
        {
            new EventOption(this, ClaimReward,
                ModOptionKey("RETURNED", "CLAIM_REWARD")),
        });
    return Task.CompletedTask;
}
```

The engine recreates the Event room and invokes `Resume`. A combat-layout Event cannot use
the resumable form because it has no normal Event layout to return to.

### Continue directly to the map

Use this when combat is the Event's terminal branch:

```csharp
private Task FightAndLeave()
{
    EnterCombatWithoutExitingEvent<MyEncounter>(
        Array.Empty<Reward>(),
        shouldResumeAfterCombat: false);
    return Task.CompletedTask;
}
```

The combat's normal completion path opens the map. Do not call `SetEventFinished` first and
do not expect `Resume` afterward.

### Extra combat rewards

Pass owned rewards in the first argument:

```csharp
var rewards = new List<Reward>
{
    new RelicReward(owner),
    new PotionReward(owner),
};
EnterCombatWithoutExitingEvent<MyEncounter>(rewards, shouldResumeAfterCombat: false);
```

### Hard boundary: one special combat per Event instance

Generate at most one special-combat transition from a mutable Event instance. A second
combat started by the same resumed instance failed the live harness at
`CombatReplayWriter.RecordInitialState`. If a story needs another fight, finish this Event
and model the later fight through another map node or another supported content surface.

## Unsupported room transitions

The vanilla Event inventory contains no production Event path that transitions into a
merchant room, rest-site room, or treasure room. Do not synthesize those transitions from
debug APIs or internal room constructors. Express their public effects through the Cmd and
reward vocabulary above, or report the room-transition request as unsupported.

## Verification contract

One `MapNode` hosted suite can cover the independent invariants without one project per
outcome. Drive only the branches required by SPEC and assert:

1. every real `NEventOptionButton` used by the scenario;
2. exact Cmd post-state after blocking overlays finish;
3. the expected page and localized option after `SetEventState`;
4. custom encounter identity in special combat;
5. `Resume` count/page for the resumable branch;
6. open map and no Event resumption for the terminal branch;
7. one structured marker listing expected and observed outcome families.

A hosted Event proof covered page Cmd, upgrade selection, resumable custom combat, custom Gold
reward, terminal custom combat, and Event VFX cleanup in one final headed run. The marker
was `event outcome vocabulary complete`; it reached `selftest done` with no fresh error.
