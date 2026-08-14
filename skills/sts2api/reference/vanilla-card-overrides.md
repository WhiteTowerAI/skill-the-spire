# Public overrides for existing vanilla Cards

Use this reference after `vanilla-overrides.md` resolves an exact `CARD.*` target. This route
is pinned to STS2 `0.107.1` and RitsuLib `0.5.11`. It changes existing Card instances by
attaching a registered default `CardCapability`; it does not register a second Card,
mutate `ModelDb`, or generate Harmony, reflection, Publicizer, or IL.

The checked catalog lists route family `public-card-overrides` as authorable. One generated
capability class owns all ordered operations for one target Card type. Generate another
class for another target. This keeps manifest order explicit and avoids one runtime model
type for every small text or number change.

## Promoted public surface

| Semantic surface | Route id | Public RitsuLib contract |
|---|---|---|
| Card type | `card.property.type` | `ICardPropertyContributor.GetCardType` |
| rarity | `card.property.rarity` | `ICardPropertyContributor.GetCardRarity` |
| target | `card.property.target` | `ICardPropertyContributor.GetTargetType` |
| appended tags | `card.property.tags` | `ICardPropertyContributor.GetTags`; all contributions append and deduplicate |
| evaluated Energy cost | `card.cost.energy` | `ICardEnergyCostContributor.ModifyEnergyCost` |
| evaluated Star cost | `card.cost.stars` | `ICardStarCostContributor.ModifyStarCost` |
| conditional playability | `card.play-state.can-play` | `ICardPlayStateContributor.CanPlay`; no decision returns `null` |
| result pile | `card.play-result.pile` | `ICardPlayResultContributor.GetResultPileTypeForCardPlay` |
| title fragments/replacement | `card.title.fragments` | `ICardTitleContributor`; before/replace/after-base/after-title |
| description fragments | `card.description.fragments` | `ICardDescriptionContributor`; before/after only |
| displayed type text | `card.type-text` | `ICardTypeTextModifier`; `{Type}` wraps, omission replaces |
| hover tips | `card.hover-tips` | `ICardHoverTipContributor` plus typed factories or localized `HoverTip` |
| native gold/red glow | `card.glow.gold`, `card.glow.red` | `ICardGlowContributor` |
| capability-owned variables | `card.capability.dynamic-vars` | `CardCapability.CanonicalVars` and its saved/cloned `DynamicVars` |
| compose/replace `OnPlay` | `card.play.on-play` | `CardPlayCapability` before/after owner play and public suppression |
| owner lifecycle composition | `card.owner-hooks` | typed owner hook stream for owner draw/discard/exhaust |

These routes include all non-asset Card contributor interfaces needed by the current
semantic authoring vocabulary. Card frame/portrait/banner material providers are promoted
separately in `vanilla-visual-overrides.md` because they require asset packaging
and presentation contracts. `HasTurnEndInHandEffect` alone
only asks the game to call the vanilla Card's own protected handler; do not turn it on
without a grounded compatible owner behavior. A target-bound override must not implement
`ICardTransformCarryOverCapability`: transforming into another Card identity must drop the
old target's capability.

The route does not change canonical variables, Energy/Star X-cost identity, tags by
removal, keywords, the base description body, acquisition pools, or Card materials. It may
read an existing owner variable in an effect. A newly declared variable belongs to the
capability, not to the vanilla Card's canonical `DynamicVars` collection.

**Fail-closed intent rule:** replacing, removing, or hiding the original description body
is a base-description replacement, not composition. RitsuLib `0.5.11` exposes no public
replacement placement for `ICardDescriptionContributor`. Tell the user that limitation and
stop; never turn the request into a before/after fragment automatically. Only an explicit
user choice to keep the original body and add text authorizes `compose`. Finalized values or
"do not ask again" wording does not authorize the change in meaning.

## Manifest contract

Resolve the target first, copy the exact required baseline fields from the checked
catalog, and preserve operation order. A rarity change is:

```json
{
  "order": 0,
  "operation_id": "strike.rarity",
  "target_model_id": "CARD.STRIKE_IRONCLAD",
  "mode": "adjust",
  "surface": "card.rarity",
  "route": {
    "class": "public",
    "id": "card.property.rarity",
    "fingerprint": null
  },
  "expected_baseline": {
    "category": "CARD",
    "type": "MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad",
    "properties": { "rarity": "Basic" }
  },
  "semantics": { "adjustment": "set", "value": "Common" }
}
```

`vanilla_overrides.py` owns the exact payload shapes. Important forms are:

- property `set`; tag `append`; and evaluated cost `set` or `delta`;
- a playability `decision` plus a declarative `when` predicate;
- a vanilla result pile (`Draw`, `Hand`, `Discard`, or `Exhaust`) or a stable owned-pile
  semantic id already authored through `card-piles.md`;
- a localization table/key plus a checked title/description/type-text placement;
- keyword, typed model-preview, or localized hover tips;
- capability variables with `dynamic`, `damage`, `block`, or typed `power` roles;
- ordered effects: attack, block, heal, apply Power, draw, gain Energy, gain Stars,
  and generate a Card into a combat pile; and
- owner lifecycle triggers `after_owner_drawn`, `after_owner_discarded`, and
  `after_owner_exhausted`.

An amount is either a nonnegative literal, an existing checked owner variable, or a
capability variable. A model reference is a complete vanilla or Mod `ModelId`, never a C#
type string supplied by the prompt. Predicates are recursive `all`/`any`/`not` combinations
of the checked kinds: always, upgraded, current pile, native playability, player numeric
state, Power amount, Card tag, Card keyword, and the draw/exhaust event flags. Lower only
these semantic values; never preserve a prompt as executable code.

A composed `OnPlay` operation records `timing` and `run_after_replacement`. The latter must
be false for compose-before and is an explicit choice for compose-after. Owner lifecycle
effects cannot select `play_target`, because those hooks have no `CardPlay` target.

The build preflight rejects wrong route/mode/surface combinations, missing baseline fields,
unknown enum values, malformed effects or predicates, non-Card targets, and unlisted
routes. It also rejects a cost `set` after a delta. One set followed by ordered deltas is
valid. Appended tags, fragments, tips, glow predicates, playability decisions, owner hooks,
and composed effects retain manifest order. Multiple replacements of the same title,
type-text, or `OnPlay` surface conflict.

## Registration

Create the capability through the content registry so `ModelDb` owns its identity, clone,
and save/load lifecycle. Never call its constructor in the default-capability lambda:

```csharp
using MegaCrit.Sts2.Core.Models.Cards;
using STS2RitsuLib;

static partial void RegisterContent()
{
    var content = RitsuLibFramework.GetContentRegistry(ModId);
    content.RegisterModelCapability<StrikeIroncladOverride>();
    content.ConfigureDefaultModelCapabilities<StrikeIronclad>(
        "override-card-strike-ironclad",
        (_, capabilities) => capabilities.Add<StrikeIroncladOverride>());
}
```

The modifier id is stable, Mod-scoped, lowercase, and specific to the target. Register the
capability before configuring it. Do both exactly once in `MainFile.RegisterContent()`.

## Capability lowering

Start with `CardPlayCapability` when any play behavior is selected. Otherwise
`CardCapability` is enough. Implement only the contributor interfaces selected by the
manifest. The combined shape is:

```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Models.Capabilities;

public sealed class StrikeIroncladOverride : CardPlayCapability,
    ICardPropertyContributor,
    ICardEnergyCostContributor,
    ICardPlayResultContributor,
    ICardTitleContributor,
    ICardDescriptionContributor,
    ICardHoverTipContributor,
    ICardGlowContributor
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new BlockVar(3m, ValueProp.Move)];

    public CardRarity? GetCardRarity(CardModel card) => CardRarity.Common;
    public IEnumerable<CardTag> GetTags(CardModel card) => [CardTag.Strike];
    public int ModifyEnergyCost(CardModel card, int currentCost, CostModifiers modifiers) =>
        Math.Max(0, currentCost - 1);
    public PileType? GetResultPileTypeForCardPlay(CardModel card) => PileType.Exhaust;

    public IEnumerable<CardTitleFragment> GetTitleFragments(CardTitleContext context) =>
        [new(new LocString("cards", $"{Id.Entry}.titlePrefix"),
            CardTitleFragmentPlacement.BeforeBase, 0)];

    public IEnumerable<CardDescriptionFragment> GetDescriptionFragments(
        CardDescriptionContext context) =>
        [new(new LocString("cards", $"{Id.Entry}.extraDescription"),
            CardDescriptionFragmentPlacement.AfterBase, 0)];

    public IEnumerable<IHoverTip> GetHoverTips(CardModel card) =>
        [HoverTipFactory.FromKeyword(CardKeyword.Exhaust)];

    public bool ShouldGlowGold(CardModel card) => card.IsUpgraded;

    protected override void OnOwnerCardUpgraded(CardModel card) =>
        DynamicVars.Block.UpgradeValueBy(2m);

    protected override async Task<bool> BeforeOwnerCardOnPlay(
        PlayerChoiceContext choiceContext,
        CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(Owner);
        await CreatureCmd.GainBlock(Owner.Owner.Creature, DynamicVars.Block, cardPlay);
        return false;
    }

    protected override Task OnOwnerCardPlayed(
        PlayerChoiceContext choiceContext,
        CardPlay cardPlay) => Task.CompletedTask;
}
```

This is a shape, not a request to emit every interface. Keep generated code as small as the
accepted manifest. Use the catalog's concrete target type. Emit fragments and effects in
manifest order, and use each operation order as the fragment `Order` when RitsuLib exposes
one.

For type text, return `LocString` entries from `GetTypeModifiers(CardModel)`. A wrapping
localization value must contain exactly one `{Type}` token; a replacement must contain
none. For a localized hover tip use `new HoverTip(titleLocString, descriptionLocString)`.
For model previews select the typed `HoverTipFactory.FromCard`, `FromRelic`, `FromPotion`,
`FromPower`, `FromEnchantment`, or `FromAffliction` overload matching the referenced model.

For conditional playability, evaluate rules in manifest order and return the last matching
decision; return `null` if none match. Gold and red glow rules combine with logical OR per
channel. Reuse `card-hand-emphasis.md` only when the request needs multiple priorities or a
custom color; do not mix that outline registry with these native gold/red contributors for
the same target.

## Play composition and replacement

Lower normal effects through the same checked commands and helpers used by `recipes/card.md`
and `card-computed-values.md`. Effects execute exactly once in manifest
order. Preserve typed Damage/Block/Power semantics and null-check a selected play target.

- compose-before: execute in `BeforeOwnerCardOnPlay`, then return `false`;
- replace: execute the complete replacement in `BeforeOwnerCardOnPlay`, then return `true`;
- compose-after: execute in the three-argument `OnOwnerCardPlayed` override, including the
  declared policy for whether it runs after a replacement; and
- owner draw/discard/exhaust: override the exact typed owner hook, guard with
  `ReferenceEquals(card, Owner)`, evaluate the event predicate, then execute effects.

Returning `true` suppresses only the vanilla Card's protected `OnPlay` body. The rest of
`CardModel.OnPlayWrapper` still owns payment, targeting, history, result-pile movement,
enchantments, afflictions, and later hooks. Do not reimplement or manually call those
stages. A replacement must include every effect the accepted SPEC promises; it must not
silently retain part of the vanilla body.

Capability-owned variables clone and save through RitsuLib. Apply their upgrade deltas in
`OnOwnerCardUpgraded`; do not write into `Owner.DynamicVars`. The default capability follows
clones of the same target identity. It does not carry to a different transformed Card. On
downgrade, rebuild capability-owned values from the manifest baseline and current owner
upgrade level rather than subtracting from an unknown state.

## Localization and checks

Capability localization lives in the normal Mod resource tree. Use stable capability-entry
keys such as `<MOD>_MODEL_CAPABILITY_<TYPE>.extraDescription` in the selected table. Supply
required `eng` and `zhs` plus every additional language named by the accepted SPEC, and
preserve SmartFormat variables.
Changing a gameplay effect and its player-facing text is one operation plan, even though
the manifest records separate ordered surfaces.

Never claim real-game behavior, preview, clone/save, transform, payment, targeting,
result-pile, or presentation proof that was not observed in a real host. A focused manifest
test and a successful compile establish neither. Report every unrun path as an explicit
exception rather than a pass.
