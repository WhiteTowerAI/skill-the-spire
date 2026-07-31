# Reference: open-mod Scry helper

Use this page only when a Card's semantic effect is "look at the top X cards of Draw and
discard any number of them." RitsuLib `0.5.0` has no public Scry command, so the helper
is emitted as source inside the generated Mod. It is not another runtime dependency.

## Supported contract

- singleplayer only; multiplayer and replay callers fail clearly before opening a choice;
- `amount <= 0`, no active combat, ending combat, or an empty Draw pile returns an empty
  structured result without opening a selector or mutating piles/history;
- inspect at most the top `amount` cards in current Draw order;
- await the native simple-grid selector with minimum `0` and maximum `seen.Count`;
- move selected cards to Discard in their original seen order;
- record exactly one `CardDiscardedEntry` and await `Hook.AfterCardDiscarded` exactly once
  for each selected card;
- leave unselected cards in Draw in their original relative order;
- return requested, seen, and discarded cards for local composition and Tier-2 proof.

There is no global Scry modifier or completion hook. Add one only after a separate
cross-Mod interoperability contract and multiplayer proof exist.

## Source and lifecycle grounding

The ordering was independently reimplemented against STS2 `0.107.1` public commands and
history/hooks. BaseLib `3.3.8`'s MIT-licensed `ScryCmd` was used as a comparison source for
the established Scry lifecycle. Preserve this short attribution in generated source; do
not copy BaseLib assemblies or make BaseLib a project/manifest dependency.

```csharp
// Lifecycle ordering is grounded in STS2 0.107.1 public commands; BaseLib 3.3.8
// ScryCmd (MIT) was used as a compatibility reference.
```

## Copyable implementation

Emit `<ModName>Code/Helpers/OpenModScry.cs` and replace the namespace only:

```csharp
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Runs;

namespace <ModName>.Helpers;

public sealed record OpenModScryResult(
    int RequestedAmount,
    IReadOnlyList<CardModel> SeenCards,
    IReadOnlyList<CardModel> DiscardedCards)
{
    public bool Performed => SeenCards.Count > 0;
}

public static class OpenModScry
{
    // Lifecycle ordering is grounded in STS2 0.107.1 public commands; BaseLib 3.3.8
    // ScryCmd (MIT) was used as a compatibility reference.
    public static async Task<OpenModScryResult> Execute(
        PlayerChoiceContext choiceContext,
        Player player,
        int amount)
    {
        ArgumentNullException.ThrowIfNull(choiceContext);
        ArgumentNullException.ThrowIfNull(player);

        if (amount <= 0)
            return Empty(amount);

        if (RunManager.Instance.NetService.Type != NetGameType.Singleplayer)
            throw new NotSupportedException(
                "OpenModScry is verified for singleplayer only.");

        var combatState = player.Creature.CombatState;
        if (combatState == null || CombatManager.Instance.IsOverOrEnding)
            return Empty(amount);

        var drawPile = PileType.Draw.GetPile(player);
        var seen = drawPile.Cards.Take(amount).ToList();
        if (seen.Count == 0)
            return Empty(amount);

        var prefs = new CardSelectorPrefs(
            CardSelectorPrefs.DiscardSelectionPrompt, 0, seen.Count);
        var selected = (await CardSelectCmd.FromSimpleGrid(
                choiceContext, seen, player, prefs))
            .ToHashSet();
        var discarded = seen.Where(selected.Contains).ToList();
        var discardPile = PileType.Discard.GetPile(player);

        foreach (var card in discarded)
        {
            await CardPileCmd.Add(card, discardPile);
            CombatManager.Instance.History.CardDiscarded(combatState, card);
            await Hook.AfterCardDiscarded(combatState, choiceContext, card);
        }

        discardPile.InvokeContentsChanged();
        return new OpenModScryResult(amount, seen, discarded);
    }

    private static OpenModScryResult Empty(int requestedAmount) =>
        new(requestedAmount,
            Array.Empty<CardModel>(), Array.Empty<CardModel>());
}
```

The host Card uses an ordinary `DynamicVar("Scry", baseAmount)` if the amount scales and
awaits the helper from `OnPlay`. The Card itself retains its normal Play -> result-pile
lifecycle. A custom `CardKeyword` is optional presentation vocabulary, not part of this
helper's behavior.

## Focused Tier-2 proof

Use one `CombatPlayer` run and the driver in `selftest-harness.md`. Keep the complete
zero/empty/short/full matrix in this one run:

1. Assert the real run is `Singleplayer`.
2. With empty Draw, call amounts `0` and a positive value; assert empty results and no
   pile/history mutation or selector.
3. Put two known Cards in Draw, request five, and use `CardSelectCmd.UseSelector` to choose
   one. Assert seen order, one discard, one retained Card, one history entry, and one known
   discard-hook consequence such as `ToughBandages` Block `+3`.
4. Put four known Cards in Draw and play the real Scry Card for three. Wait for a visible
   `NSimpleCardSelectScreen`; while it is open assert the play task is incomplete. Select
   the first and third `NGridCardHolder`, capture the one useful screenshot, and confirm.
5. Assert seen `[1,2,3]`, discarded `[1,3]`, Draw `[2,4]`, two history entries, hook
   consequence Block `+6`, and the source Card in its normal result pile.
6. Emit `R6 scry helper complete expected=all observed=all`, then `selftest done`.

The 2026-07-23 `RitsuHelpersProof` run passed this contract against STS2 `0.107.1` and
RitsuLib `0.4.67`, with BaseLib absent, strict Tier 2, and no fresh error. The visible
selector evidence is
`C:\Users\YY\AppData\Roaming\SlayTheSpire2\r6_ritsu_scry_selector.png`.

## Not promoted

- multiplayer/replay selection or remote-player ownership;
- global before/after-Scry hooks or a cross-Mod Scry standard;
- modifier APIs that change the requested amount for unrelated Mods;
- arbitrary card-selection helpers, retained-card zones, or `CustomPile` gameplay.
