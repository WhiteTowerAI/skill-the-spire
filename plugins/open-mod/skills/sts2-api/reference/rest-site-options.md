# Relic-owned Rest Site options

This page owns the first bounded Package 3 route for a generated Mod to add one action to
the native Rest Site. It is grounded against STS2 `0.107.1` and RitsuLib `0.4.62`.

## Supported contract

The first slice is deliberately narrow:

- the owner is one concrete generated-Mod-local Relic;
- the run is singleplayer; multiplayer and replay hide the option and fail closed;
- the cost is free or one fixed nonnegative Gold amount;
- the outcome is deterministic and preflightable, using public commands with no player
  selection after payment;
- repeatability is once per Rest Site or once per run;
- success either follows the normal leave behavior or preserves the other native options
  for one subsequent choice;
- a custom icon is optional and falls back to the checked native Heal icon.

Card or Modifier owners, variable or non-Gold costs, arbitrary transactional outcomes,
remote-player ownership, multiplayer synchronization, and repeated successful use in one
Rest Site are unsupported. Do not generate Harmony, reflection, or UI patches to extend
this boundary.

## Semantic declaration

Record these fields before selecting the adapter:

```markdown
- **owned Rest Site option**:
  - owner: relic
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when the owned relic should contribute the option>
  - repeatability: once per Rest Site | once per run
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic game-term operations and exact values>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: singleplayer only
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

Extend `ModRestSiteOptionTemplate`, and contribute it from the owning Relic's
`TryModifyRestSiteOptions`. Use a stable Mod-namespaced `OptionId`; the host serializes the
selected ID into run history, so it is a compatibility value rather than display text.

The generated owner separates three questions:

- `ShouldOffer(player)`: correct owner, exact singleplayer mode, eligibility, and unused
  once-per-run state;
- `CanPay(player)`: `ShouldOffer` plus the fixed Gold predicate;
- `TryModifyRestSiteOptions`: `ShouldOffer`, duplicate-ID rejection, then one insertion.

Use `SavedAttachedState<SpecificRelic,bool>` only for once-per-run repeatability. Once per
Rest Site needs no extra state: the host removes a successful option from that visit's
logical list. A failed selection returns `false` and must not mark either form as used.

```csharp
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Utils;

namespace <ModName>.Relics;

public sealed class <RelicName> : ModRelicTemplate
{
    internal const int GoldCost = <cost>;
    internal const decimal MaxHpGain = <max-hp-gain>m;

    private static readonly SavedAttachedState<<RelicName>, bool> UsedState =
        new($"{MainFile.ModId}_rest_site_used", () => false);

    private bool _keepRemainingOnce;

    public override RelicRarity Rarity => RelicRarity.Common;

    internal bool ShouldOffer(Player player) =>
        player == Owner &&
        RunManager.Instance.NetService.Type == NetGameType.Singleplayer &&
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

public sealed class <RestSiteOptionName>(Player owner, <RelicName> source)
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
            description.Add("Gold", <RelicName>.GoldCost);
            description.Add("MaxHp", <RelicName>.MaxHpGain);
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
            <RelicName>.GoldCost, Owner, GoldLossType.Spent);
        await CreatureCmd.GainMaxHp(
            Owner.Creature, <RelicName>.MaxHpGain);

        source.MarkSuccessfulUse(keepRemaining: <true-or-false>);
        return true;
    }
}
```

For a free option, keep `GoldCost = 0`, let `CanPay` use the same predicate, and skip the
zero-value `LoseGold` command. All final checks happen before the first mutation. The
supported outcome must have no cancellation or expected failure after payment; arbitrary
rollback/transaction composition is outside this slice.

`ShouldDisableRemainingRestSiteOptions` is a global hook and defaults to `true` on every
model. The one-shot flag above returns `false` only immediately after this option's success
and is consumed by that query. Never return `false` unconditionally from the owner.

## Localization and icon

Keep the option's custom title and description in the owner's existing `relics.json`:

```json
{
  "<MOD>_REST_SITE_<OPTION>.title": "Reforge",
  "<MOD>_REST_SITE_<OPTION>.description": "Spend {Gold} Gold. Gain {MaxHp} Max HP."
}
```

The optional raster role is `rest_site_option`. It writes one opaque
`images/rest_site_options/<slug>.png` at `256x169`. Two pinned-version product references
use that exact canvas. The focused `M66RestSiteProof` headed check confirmed the packed
custom image framing and missing-art native Heal fallback in real `NRestSiteButton`
consumers.

Always resolve a missing custom file to
`res://images/ui/rest_site/option_heal.png` before creating the profile. Omitting the
profile or returning a missing custom path is not a valid fallback: vanilla derives its
fallback path from the custom `OptionId`, which has no built-in texture.

## Proof contract

Use one focused real Rest Site run. Do not substitute a generated list, model-only state,
or load marker for the native host.

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

The pinned dev-console `gold` command ignores negative values; `gold -N` cannot construct
the low-Gold or stale-button state. For manual review, spend Gold normally at a Shop before
entering the Rest Site to check the gray state. Step 3 requires a narrow proof driver that
uses a public Gold command after the button renders; if a human-led acceptance omits that
literal stale-button transition, record it as an exception instead of claiming it ran.

Tier 1 still requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof plus `selftest done`; when the human lead performs the hosted
matrix instead, record the unrun strict harness as an explicit exception, never a pass.
