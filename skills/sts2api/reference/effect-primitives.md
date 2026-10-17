# Ordinary effect primitives

Use this reference when a SPEC `effects.sequence` asks a truthful behavior owner to cause one or
more ordinary player-visible results. The selected surface recipe still owns the callback and its
lifetime. This page owns the exact lowering and the inputs that callback must supply.

Author the sequence in SPEC order and `await` each `Task` before starting the next effect. Do not
add a runtime EffectEngine, arbitrary `Cmd.Wait`, direct model mutation, or a substitute source,
target, owner, or `PlayerChoiceContext`. If the selected callback cannot supply a required input,
stop and name that input and the nearest specialized route.

## Bindings before commands

Resolve these values from the selected surface, not from canonical models or global lookups:

- `choiceContext`: the real callback context. A Monster move may use a fresh
  `ThrowingPlayerChoiceContext` for a command that requires one, while its attack builder executes
  with `null`. A world callback with no combat choice context cannot invent a combat target.
- `player`: the mutable Player that owns or receives the result.
- `sourceCreature`: the acting mutable Creature when one truthfully exists; otherwise `null` only
  where the command explicitly permits no applier/dealer.
- `cardSource`: the exact acting Card only for a Card-caused effect; otherwise `null`.
- `target` or `targets`: live mutable Creature instances supplied or selected by the callback.
- `cardPlay`: the current `CardPlay` only for Block directly caused by that play; otherwise `null`.

In-combat Card selection and moving a Card to the top of the Draw Pile are below. Target
selection, deck/Event selection, Reward/UI choices, Custom Pile movement, lifecycle listeners,
and state/RNG are separate routes. This page consumes their resolved results but does not
perform their transactions.

## Damage

Use an attack when the semantic result is a powered attack with normal attack hooks. Use direct
damage only for an effect that is explicitly not an attack.

```csharp
AttackCommand attack = await DamageCmd.Attack(amount)
    .FromCard(cardSource)
    .Targeting(target)
    .Execute(choiceContext);

ICombatState combatState = cardSource.CombatState ??
    throw new InvalidOperationException("Card attack requires a live combat state.");

AttackCommand allTargetAttack = await DamageCmd.Attack(amount)
    .FromCard(cardSource)
    .TargetingAllOpponents(combatState)
    .Execute(choiceContext);

AttackCommand randomMultiHitAttack = await DamageCmd.Attack(amount)
    .WithHitCount(hitCount)
    .FromCard(cardSource)
    .TargetingRandomOpponents(combatState)
    .Execute(choiceContext);

AttackCommand monsterAttack = await DamageCmd.Attack(amount)
    .FromMonster(monster)
    .Execute(null);

IEnumerable<DamageResult> results = await CreatureCmd.Damage(
    choiceContext, target, amount, props, sourceCreature, cardSource);
```

For Card attacks, use the Card's declared `DamageVar`/computed raw damage, `FromCard` preserves
Card provenance, and the selected Card target must be non-null. For declared all-enemy or random
attacks, require the acting Card's live `cardSource.CombatState` (inside the Card template,
`base.CombatState`) and pass that `ICombatState` to `TargetingAllOpponents` or
`TargetingRandomOpponents`; do not substitute a `PlayerCombatState` or continue outside combat.
Random targeting chooses a fresh opponent per hit and normally keeps its default
`allowDuplicates: true`. Use `WithHitCount(int)` for a multi-hit attack rather than an outer loop.
Call `Unpowered()` only for the rare semantic that is still a real attack but must skip Power
scaling; ordinary non-attack fixed damage uses `CreatureCmd.Damage` instead. Monster attacks use
`FromMonster(monster)`; the builder derives the opposing targets and must not add `.Targeting(...)`.
Other owners use `CreatureCmd.Damage` with an exact `ValueProp` selected by the semantic route.
The returned `DamageResult` sequence is the actual per-target result; target death, Block, hooks,
and combat ending can make it differ from the requested amount. Do not use direct damage as an
approximation for attack semantics or use an attack builder without a truthful Card/Monster
source. Advanced Card/Potion target selection remains `reference/advanced-targeting.md`.
`AttackCommand.Execute` returns the same executed builder; its `Results` is grouped by actual hit
and contains the resulting `DamageResult` entries. Inspect it when a later effect depends on hit
count, target, or damage outcome rather than assuming the requested attack fully landed.

## Block, healing, and bounded HP changes

```csharp
decimal modifiedBlock = await CreatureCmd.GainBlock(
    target, amount, props, cardPlay);
await CreatureCmd.LoseBlock(target, amount);
await CreatureCmd.Heal(target, amount);
await CreatureCmd.GainMaxHp(target, amount);
await CreatureCmd.LoseMaxHp(choiceContext, target, amount, isFromCard);
```

- Card Block passes its `BlockVar` or raw amount with the declared props and current `cardPlay`;
  non-Card Block passes `cardPlay: null`. `ValueProp.Move` is the Monster-move convention.
- `GainBlock` clamps the hook-modified request to zero and returns that modified amount. Combat
  ending returns zero; current Block before/after remains the observed state delta.
- `LoseBlock` is neutral for nonpositive amounts, dead targets, or over/ending combat and cannot
  remove more Block than exists.
- `Heal` caps current HP at Max HP and runs native presentation/history/hooks. A nonpositive heal
  is not a damage route. Use before/after current HP for the actual healed amount.
- Max HP gain/loss requires a nonnegative amount. Gain also heals by the actual Max HP increase.
  Bounded ordinary loss must not exceed `target.MaxHp - 1`: the command later floors Max HP at 1,
  but first deals unblockable unpowered damage against the raw requested new Max HP and an
  oversized request can be lethal. Pass `isFromCard: true` only for an actual Card source. A
  callback without a real `PlayerChoiceContext` cannot author Max HP loss through this primitive.

Absolute HP/Max HP setters are setup/lifecycle control and are not ordinary effects. Rest Site
healing/payment remains `reference/rest-site-options.md` when that transaction owns the result.

## Apply, change, or remove a Power

```csharp
TPower? applied = await PowerCmd.Apply<TPower>(
    choiceContext, target, amount, sourceCreature, cardSource);

IReadOnlyList<TPower> appliedMany = await PowerCmd.Apply<TPower>(
    choiceContext, targets, amount, sourceCreature, cardSource);

int newAmount = await PowerCmd.ModifyAmount(
    choiceContext, existingPower, offset, sourceCreature, cardSource);

await PowerCmd.Remove<TPower>(target);
await PowerCmd.Remove(existingPower);
```

`Apply<T>` returns `null` when combat is ending, the target rejects Powers, a hook blocks or
zeros the application, or stacking removes the instance. Multi-target application preserves
target order but returns only successful non-null results. A custom Power's identity, amount
domain, stacking, localization, and hooks remain `recipes/power.md`.

For a bounded nonnegative Counter, resolve the existing instance, clamp a negative offset to its
current amount, then call `ModifyAmount`; never apply a negative amount to manufacture a missing
Power. `ModifyAmount` returns the new integer amount and may remove the Power at its removal
threshold. Remove only an existing exact instance/type; an absent instance is neutral. Preserve
the real choice context, applier, and Card provenance for all hook/history passes.

## Native player resources

```csharp
await PlayerCmd.GainEnergy(amount, player);
await PlayerCmd.LoseEnergy(amount, player);
await PlayerCmd.GainStars(amount, player);
await PlayerCmd.LoseStars(amount, player);
await PlayerCmd.GainGold(amount, player, wasStolenBack: false);
await PlayerCmd.LoseGold(amount, player, GoldLossType.Lost); // or Spent / Stolen
await PlayerCmd.GainMaxPotionCount(amount, player);
await PlayerCmd.LoseMaxPotionCount(amount, player);
```

Energy and Stars are combat resources and require a live combat Player. Energy gain/loss ignores
nonpositive amounts and ending combat; gain runs the RitsuLib/game gain hooks. Star gain/loss
uses the native integer-backed combat state and gain hooks. Author nonnegative integral semantic
amounts for both resources rather than relying on decimal truncation or negative-input behavior.
Do not use setters for normal effects.

Gold and potion capacity are run-scoped. Gold gain is hook-modified, applies only a positive final
integer amount, and `wasStolenBack` is true only when reclaiming stolen Gold. Gold loss must name
`Lost`, `Spent`, or `Stolen`, use a nonnegative integral amount, update the corresponding history,
and floor Gold at zero; preflight an exact payment before mutation rather than treating a clamped
loss as successful payment. Potion-slot changes use a nonnegative integer; loss must not exceed
the current slot count, and removing occupied slots natively discards displaced Potions. Compare
before/after state for the actual delta. Secondary resources and payment use
`reference/character-resource.md`.

## Draw Cards

```csharp
IEnumerable<CardModel> drawn = await CardPileCmd.Draw(
    choiceContext, count, player, fromHandDraw: false);
```

Ordinary effects always pass `fromHandDraw: false`; `true` is reserved for the native initial
turn draw. `count` is decimal: a positive value is rounded up and a zero/negative value draws
nothing. The returned sequence contains only Cards actually drawn. Full hand, prevented draw,
empty Draw and Discard piles, native shuffle, and combat ending can make the result partial or
empty. The command owns shuffle, exact Card movement, history, hooks, and drawn callbacks. A
callback without a real `PlayerChoiceContext`, live combat Player, and normal Hand/Draw piles
cannot author this primitive.

## Discard or Exhaust known combat Cards

Selection is not part of these primitives. First obtain exact live Card instances through the
surface or § Choose Cards in combat, then preserve their owner and combat-pile identity:

```csharp
await CardCmd.Discard(choiceContext, card);
await CardCmd.Discard(choiceContext, cards);
await CardCmd.DiscardAndDraw(choiceContext, cards, cardsToDraw);
await CardCmd.Exhaust(choiceContext, card, causedByEthereal: false, skipVisuals: false);
```

Discarding a batch preserves native batch timing; `DiscardAndDraw` completes all selected
discards before drawing the declared nonnegative integer count. Set `causedByEthereal: true` only
for the native Ethereal lifecycle, and do not suppress visuals for ordinary effects. Commands are
neutral once combat is no longer in progress and reject Cards that do not belong to the expected
live combat lifecycle. Arbitrary movement, shuffle, Custom Piles, and retained zones remain
`recipes/card-pile.md` plus `reference/card-piles.md`.

## Choose Cards in combat

```csharp
var prefs = new CardSelectorPrefs(SelectionScreenPrompt, minCount, maxCount);   // or (prompt, count)

IEnumerable<CardModel> fromHand = await CardSelectCmd.FromHand(
    choiceContext, player, prefs, filter: null, source: this);
IEnumerable<CardModel> fromPile = await CardSelectCmd.FromCombatPile(
    choiceContext, PileType.Draw.GetPile(player), player, prefs);
IEnumerable<CardModel> fromList = await CardSelectCmd.FromSimpleGrid(
    choiceContext, cards, player, prefs);
CardModel? oneOfThree = await CardSelectCmd.FromChooseACardScreen(
    choiceContext, cards, player, canSkip: false);
```

Every call needs the effect's real `PlayerChoiceContext`, so it runs only from a hook or
callback that receives one (`OnPlay`, `AfterPlayerTurnStart`, a Potion use; never
`AfterSideTurnStart`). `SelectionScreenPrompt` is the owning model's protected
`<id>.selectionScreenPrompt` localization key; Cards, Relics, and Powers throw when it is
missing, so emit it in both languages whenever SPEC selects a choice. The vanilla prompts
`CardSelectorPrefs.ExhaustSelectionPrompt`, `DiscardSelectionPrompt`, and the other static
ones are reusable when the wording matches. `FromHandForDiscard` is the discard variant.

`FromChooseACardScreen` accepts at most three Cards and returns `null` for an empty list or a
skip. `FromHand` returns the whole filtered Hand without asking when it holds no more Cards
than `MinSelect` (unless `RequireManualConfirmation` is set). Always operate on the returned
instances, and inspect the count rather than assuming the requested number. Drive these in
Tier 2 with `reference/selftest-harness.md` § card that asks the player to choose.

## Put an existing Card on top of the Draw Pile

```csharp
await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Top);
CardModel? top = PileType.Draw.GetPile(player).Cards.FirstOrDefault();   // Cards[0] is the top
await CardPileCmd.ShuffleIfNecessary(choiceContext, player);
```

`CardPileCmd.Add` moves a live combat Card from its current pile; inspect the returned
`CardPileAddResult` when later steps depend on it. The Draw Pile's top is `Cards[0]`, the
next Card a draw takes. `ShuffleIfNecessary` shuffles the Discard Pile into an empty Draw
Pile and does nothing otherwise; call it before reading or revealing the top of a pile that
may be empty. Generated Cards use § Create a known Card in combat instead.

## Make a Card free this turn

```csharp
card.SetToFreeThisTurn();      // Energy and Star cost 0 until played or the turn ends
card.SetToFreeThisCombat();    // for the rest of this combat
```

Both are synchronous and apply to that one live instance. Assert the instance's current cost,
not the canonical model's.

## Stun an enemy

```csharp
await CreatureCmd.Stun(target);                     // as vanilla Whistle does
await CreatureCmd.Stun(target, nextMoveId: "MOVE"); // choose the move after the stun
```

The target must be a monster; stunning a player throws. The stun replaces the monster's
next move with `MonsterModel.stunnedMoveId` (`"STUNNED"`), shows the stun intent, and then
continues with `nextMoveId`, or with the move it last performed when that is null. Assert
`target.Monster!.NextMove.Id == MonsterModel.stunnedMoveId` right after the call, and the
skipped damage after the enemy turn.

## Create a known Card in combat

```csharp
CardModel generated = player.Creature.CombatState.CreateCard<TCard>(player);
CardPileAddResult result = await CardPileCmd.AddGeneratedCardToCombat(
    generated, destination, player, CardPilePosition.Bottom);
```

Create through the receiving Player's live combat scope. `destination` must be a combat
`PileType`; use the SPEC-selected `Top`/`Bottom` position and truthful creator (`player` for a
player-owned source, or the nullable creator the actual callback supplies). The Card must not
already have a pile. Combat ending returns an unsuccessful/default result. Inspect
`result.success`, `result.cardAdded`, and its pile rather than assuming the request succeeded;
the command owns generated history, pile movement, and generated hooks.

This primitive creates a known registered Card type. Choosing a random type uses the RNG route;
moving an existing Card uses § Put an existing Card on top of the Draw Pile or the Card Pile
route.

## Acquire known run content

```csharp
CardModel card = player.RunState.CreateCard<TCard>(player);
CardPileAddResult cardResult = await CardPileCmd.Add(
    card, PileType.Deck, CardPilePosition.Bottom);

TRelic relic = await RelicCmd.Obtain<TRelic>(player);

PotionProcureResult potionResult = await PotionCmd.TryToProcure<TPotion>(player);
```

Create a deck Card through the receiving Player's run scope, then await the exact Deck add and
inspect `success`/`cardAdded`. Preview that same result only when the selected presentation route
requires it; never create a second preview Card. `RelicCmd.Obtain<T>` returns the exact mutable
Relic after inventory/history/`AfterObtained` completes. `TryToProcure<T>` returns
`success`, the attempted mutable Potion, and a `failureReason`; a full belt or hook rejection is a
normal rejected result and must not be reported as acquisition.

These calls acquire a known type directly. Reward offers/claims, Event selection, linked rewards,
deck transform/remove/upgrade/enchant, and option presentation remain their specialized blocking
routes. The owning callback must await the acquisition before completing its transaction.

## Channel, evoke, and change Orb slots

```csharp
await OrbCmd.Channel<TOrb>(choiceContext, player);
await OrbCmd.EvokeNext(choiceContext, player);
await OrbCmd.EvokeLast(choiceContext, player);
await OrbCmd.AddSlots(player, amount);
OrbCmd.RemoveSlots(player, amount);
```

These are combat-only and require the live owner Player. Channeling creates the registered Orb,
adds one slot when a zero-base-slot character has no capacity, evokes the oldest Orb first when
full, and then queues the new Orb if possible. Evoking an empty queue and all operations during
over/ending combat are neutral. `dequeue: true` is the ordinary evoke contract.

Slot amounts are nonnegative integers. Capacity is capped at 10; removal is capped at current
capacity and removes occupied slots from the back. `RemoveSlots` is synchronous, so execute it at
its exact position in the ordered sequence without `await`. Orb passive/evoke implementation and
real turn-trigger proof remain `recipes/orb.md`; calling `OrbCmd.Passive` directly is diagnostic,
not proof of the per-turn lifecycle.

## Composition and rejection

For each SPEC step:

1. resolve its exact live inputs from the surface projection;
2. perform any declared preflight before the first mutation;
3. call the lowering above and await it when it returns `Task`;
4. inspect nullable, collection, or result-object outcomes when later effects depend on success;
5. only then continue to the next effect or complete the owning world transaction.

Do not continue a success-only branch after a rejected/partial result. If a required binding is
absent, report it literally, for example: `draw Cards requires PlayerChoiceContext and a live
combat Player; this run-load callback supplies neither`. Grounding is for a genuinely new API
family, not for any primitive maintained here.
