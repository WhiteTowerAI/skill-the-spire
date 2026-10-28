# Native Rest Site options

This page owns the bounded route for a standalone Rest Site action or for a generated Card,
Relic, or selected Modifier to add an action to the native Rest Site.


## Supported contract

The authorable slice is deliberately bounded:

- the owner is one standalone Run singleton, exactly one concrete generated-Mod-local Card in
  the deck, one concrete generated-Mod-local Relic in the run, or one selected mutable Modifier
  in `RunState.Modifiers`;
- every player's Rest Site asks every Mod owner for that player, on every peer, and the game's
  Rest Site synchronizer replays each choice for its player, so the option works in
  singleplayer and multiplayer alike (§ Multiplayer);
- the cost is free or one fixed nonnegative Gold amount;
- the outcome is deterministic and preflightable, using public commands with no player
  selection after payment;
- repeatability is once per Rest Site or once per run;
- success either follows the normal leave behavior or preserves the other native options
  for one subsequent choice;
- a custom icon is optional and falls back to the checked native Heal icon.

Variable or non-Gold costs, post-payment choices, arbitrary transactional outcomes,
and repeated successful use in one Rest Site are unsupported.
Do not generate Harmony, reflection, or UI patches to extend this boundary.

Card reachability is pinned rather than inferred: both Rest Site hooks dispatch through
`runState.IterateHookListeners(null)`, whose fixed listener set includes deck Cards; the
`0.107.1` catalog marks Card authorable, and vanilla `ByrdonisEgg` implements
`TryModifyRestSiteOptions`. Modifier reachability is equally pinned by the run listener set;
standalone ownership is supplied by RitsuLib's Run `HookedSingletonModel` subscription.

## Semantic declaration

Record these fields before writing code:

```markdown
- **owned Rest Site option**:
  - owner: standalone | card | relic | modifier
  - owner multiplicity: exactly one
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when the selected owner should contribute the option>
  - repeatability: once per Rest Site | once per run
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic game-term operations and exact values>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: both
```

Absence and disabled state are different. `eligibility` decides whether the option exists;
the enabled rule decides whether an existing option is natively clickable or gray.

## Public host lifecycle

`RestSiteSynchronizer.BeginRestSite()` calls `RestSiteOption.Generate(player)` once per
visit. Generation starts with Heal and Smith, adds Mend in multiplayer, then calls every
run hook listener's `TryModifyRestSiteOptions`. The generated list is the logical source
for the real `NRestSiteRoom` buttons.

The pinned host has these consequences:

1. `NRestSiteButton.Create` snapshots `!option.IsEnabled` into its click guard. A Gold
   change after rendering does not refresh that guard, so `OnSelect()` must repeat the
   complete final eligibility and payment check.
2. `OnSelect() == false` keeps the option in the logical list, records no Rest Site choice,
   runs no success VFX, and re-enables the current buttons.
3. `OnSelect() == true` records `OptionId`, then clears all options by default. When one
   hook returns `false` from `ShouldDisableRemainingRestSiteOptions`, only the selected
   option is removed and the native UI rebuilds from the remaining logical list.
4. A successful option can never remain available in that same visit through these public
   APIs. "Keep remaining" therefore preserves other options, not another use of itself.

Never call `RestSiteOption.Generate` merely to refresh a button. It may advance RNG and
other run state. Do not retain an `NRestSiteButton` or mutate its private clickability.

## RitsuLib route

Extend `ModRestSiteOptionTemplate`, and contribute it from the selected owner's
`TryModifyRestSiteOptions`. Standalone ownership uses a Run `HookedSingletonModel`; Card,
Relic, and Modifier ownership use their exact mutable model instances. Use a stable
Mod-namespaced `OptionId`; the host serializes the selected ID into run history, so it is a
compatibility value rather than display text.

The generated owner separates three questions:

- `ShouldOffer(player)`: correct owner, eligibility, and unused
  once-per-run state;
- `CanPay(player)`: `ShouldOffer` plus the fixed Gold predicate;
- `TryModifyRestSiteOptions`: `ShouldOffer`, duplicate-ID rejection, then one insertion.

Use `SavedAttachedState<SpecificCard,bool>` or `SavedAttachedState<SpecificRelic,bool>` only
for those owners' once-per-run repeatability. A Modifier may use its normal saved model state;
a standalone owner uses a declared run/player saved slot only when once-per-run state must
survive save/load. Once per Rest Site needs no persistent state: the host removes a successful
option from that visit's logical list. A failed selection returns `false` and must not mark any
form as used.

A Card-owned option also guards `player == Owner`, verifies the exact owner Card remains in
`player.Deck.Cards`, and requires exactly one matching instance before contribution. This
fail-closed multiplicity rule prevents duplicate deck copies from contributing duplicate
stable option ids or disagreeing over once-per-run state. The option keeps the concrete
owner instance it was created from; never re-resolve a canonical Card through `ModelDb`.

```csharp
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Utils;

namespace <ModName>.<CardsOrRelics>;

public sealed class <OwnerName> : <ModCardOrRelicTemplate>
{
    internal const int GoldCost = <cost>;
    internal const decimal MaxHpGain = <max-hp-gain>m;

    private static readonly SavedAttachedState<<OwnerName>, bool> UsedState =
        new($"{MainFile.ModId}_rest_site_used", () => false);

    private bool _keepRemainingOnce;

    public override RelicRarity Rarity => RelicRarity.Common;

    internal bool ShouldOffer(Player player) =>
        player == Owner &&
        <exact-owner-presence-and-multiplicity-guard> &&
        !UsedState[this];

    internal bool CanPay(Player player) =>
        ShouldOffer(player) && player.Gold >= GoldCost;

    public override bool TryModifyRestSiteOptions(
        Player player,
        ICollection<RestSiteOption> options)
    {
        if (!ShouldOffer(player) ||
            options.Any(option => option.OptionId == <RestSiteOptionName>.StableOptionId))
            return false;

        options.Add(new <RestSiteOptionName>(player, this));
        return true;
    }

    internal void MarkSuccessfulUse(bool keepRemaining)
    {
        AssertMutable();
        UsedState[this] = true;
        _keepRemainingOnce = keepRemaining;
    }

    public override bool ShouldDisableRemainingRestSiteOptions(Player player)
    {
        if (player != Owner || !_keepRemainingOnce)
            return true;

        _keepRemainingOnce = false;
        return false;
    }
}

public sealed class <RestSiteOptionName>(Player owner, <OwnerName> source)
    : ModRestSiteOptionTemplate(owner)
{
    public const string StableOptionId = "<MOD>_REST_SITE_<OPTION>";
    private const string CustomIcon =
        "res://<ModName>/images/rest_site_options/<slug>.png";
    private const string NativeFallbackIcon =
        "res://images/ui/rest_site/option_heal.png";

    public override string OptionId => StableOptionId;

    public override RestSiteOptionAssetProfile AssetProfile => new(
        ResourceLoader.Exists(CustomIcon) ? CustomIcon : NativeFallbackIcon);

    public override LocString? CustomTitle =>
        new("relics", "<MOD>_REST_SITE_<OPTION>.title");

    public override LocString Description
    {
        get
        {
            var description = new LocString(
                "relics", "<MOD>_REST_SITE_<OPTION>.description");
            description.Add("Gold", <OwnerName>.GoldCost);
            description.Add("MaxHp", <OwnerName>.MaxHpGain);
            return description;
        }
    }

    public override bool IsEnabled => source.CanPay(Owner);

    public override async Task<bool> OnSelect()
    {
        // Button clickability is a render-time snapshot. This is the final guard.
        if (!source.CanPay(Owner))
            return false;

        await PlayerCmd.LoseGold(
            <OwnerName>.GoldCost, Owner, GoldLossType.Spent);
        await CreatureCmd.GainMaxHp(
            Owner.Creature, <OwnerName>.MaxHpGain);

        source.MarkSuccessfulUse(keepRemaining: <true-or-false>);
        return true;
    }
}
```

For standalone ownership, register one `HookedSingletonModel(HookType.Run)` through
`.Singleton<T>()`. The singleton is a canonical callback owner: do not mutate its fields as
current-run state or call `AssertMutable()` on it. Attach the transient keep-remaining signal to
the exact `Player` and consume it in `ShouldDisableRemainingRestSiteOptions`; attach persistent
state to the concrete run/player through `RunSavedData` only when SPEC selects once-per-run
save/load behavior.

For Modifier ownership, put the same two owner overrides on the concrete
`ModModifierTemplate`. The host walks the selected mutable Modifier in
`RunState.Modifiers`, so no singleton or process subscription is needed. Guard the exact player
and selected run, and let the Modifier's normal serialized properties own persistent state.

For a free option, keep `GoldCost = 0`, let `CanPay` use the same predicate, and skip the
zero-value `LoseGold` command. All final checks happen before the first mutation. The
supported outcome must have no cancellation or expected failure after payment; arbitrary
rollback/transaction composition is outside this slice.

`ShouldDisableRemainingRestSiteOptions` is a global hook and defaults to `true` on every
model. The one-shot flag above returns `false` only immediately after this option's success
and is consumed by that query. Never return `false` unconditionally from the owner.

## Multiplayer

No mode gate: in a multiplayer Rest Site every player's option list is built on every peer by
calling each owner's `TryModifyRestSiteOptions(player, ...)`, so the `player == Owner` guard in
`ShouldOffer` is what keeps the option on its owner's list only. A chosen option reaches the other
peers as the game's Rest Site message and runs its outcome there for the same player, so the
outcome stays deterministic and preflightable exactly as in singleplayer. Vanilla also adds
Mend to every list in multiplayer; never count on a fixed native option set.

## Localization and icon

Keep the option's custom title and description in the owner's existing `cards.json`,
`relics.json`, or `modifiers.json` when one of those models owns it. A standalone option uses a
Mod-local `rest_site_ui.json`. In every case, point `CustomTitle` and `Description` at that exact
table and key:

```json
{
  "<MOD>_REST_SITE_<OPTION>.title": "Reforge",
  "<MOD>_REST_SITE_<OPTION>.description": "Spend [blue]{Gold}[/blue] [gold]Gold[/gold]. Gain [green]{MaxHp}[/green] Max HP."
}
```

```json
{
  "<MOD>_REST_SITE_<OPTION>.title": "重铸",
  "<MOD>_REST_SITE_<OPTION>.description": "花费[blue]{Gold}[/blue][gold]金币[/gold]。获得[green]{MaxHp}[/green]点最大生命值。"
}
```

The button title stays plain; the description follows the Rest Site row of
`reference/vanilla-text-style.md`.

The optional raster role is `rest_site_option`. It writes one opaque
`images/rest_site_options/<slug>.png` at `256x169`. Two pinned-version product references
use that exact canvas. A focused headed check confirmed the packed
custom image framing and missing-art native Heal fallback in real `NRestSiteButton`
consumers.

Always resolve a missing custom file to
`res://images/ui/rest_site/option_heal.png` before creating the profile. Omitting the
profile or returning a missing custom path is not a valid fallback: vanilla derives its
fallback path from the custom `OptionId`, which has no built-in texture.

## Proof contract

Use one real Rest Site per case, each a `plan.RestSite` self-test scenario that sets up the
owner and Gold in `beforeEnter` and reads or clicks the native buttons through
`t.RestSiteOptions()` and `t.ChooseRestSiteOption(id)` (`recipes/rest-site.md` § Proof
matrix). Do not substitute a generated list, model-only state, or load marker for
the native host.

1. Enter without the owner: custom option absent.
2. Obtain the owner with Gold below cost, then enter: option present, localized, gray,
   hoverable, and controller-focusable beside Heal and Smith.
3. Enter with enough Gold, then lower Gold after the button renders. Click the still-lit
   option: it returns failure; Gold, Max HP, run-use state, history, and options are
   unchanged.
4. Restore enough Gold and click: assert exact Gold and Max HP deltas, one matching history
   entry, and complete awaited outcome.
5. For keep-remaining, verify the UI rebuild contains native options, no duplicate custom
   option, and a usable controller focus loop. For normal leave, verify the ordinary
   proceed state.
6. Enter a second Rest Site and verify the declared once-per-site or once-per-run rule.
7. Run one custom-icon build and one missing-icon build; the latter must visibly use the
   native Heal image without missing-resource or UI errors.
8. Assert the selected owner boundary: standalone state does not leak to a new run; Card
   zero/duplicate instances do not contribute; a removed Relic does not contribute; or an absent
   Modifier does not contribute and a selected saved Modifier restores without replaying success.

The pinned dev-console `gold` command ignores negative values; `gold -N` cannot construct
the low-Gold or stale-button state. For manual review, spend Gold normally at a Shop before
entering the Rest Site to check the gray state. Step 3 lowers Gold with a public command
inside the scenario body, after the button rendered, then chooses the option; if a human-led
acceptance omits that literal stale-button transition, record it as an exception instead of
claiming it ran.

Tier 1 still requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof plus `selftest done`; when the user performs the hosted
matrix instead, record the unrun strict harness as an explicit exception, never a pass.
