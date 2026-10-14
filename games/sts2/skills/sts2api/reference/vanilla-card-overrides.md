# Public overrides for existing vanilla Cards

Use this reference after `vanilla-overrides.md` resolves an exact `CARD.*` target. This route
is pinned to STS2 `0.107.1` and RitsuLib `0.6.7`. It changes the existing Card in place
through three public mechanisms, never by registering a second Card or generating Harmony,
reflection, Publicizer, or IL:

- a registered default `CardCapability` attached to every instance of the target;
- the target's canonical `DynamicVars` values, assigned once when `ModelDb` is ready; and
- the game's own localization merge, which lets a Mod table replace a vanilla key.

The checked catalog lists route family `public-card-overrides` as authorable. One generated
capability class owns all ordered capability operations for one target Card type. Generate
another class for another target.

## Pick routes from what the player asked for

Start every vanilla Card change here. Each request maps to the smallest route set that makes
the Card play and read the new way, and to nothing else.

| The user asks to... | Operations |
|---|---|
| change a number the Card already has ("Strike deals 9", "upgrade gives +4") | `card.vars.base` only. The vanilla body and the vanilla description already read that variable, so both follow it. |
| change what the Card does | `card.play.on-play` `replace` with the complete new body, plus `card.description.localization` with matching rules text, plus `card.hover-tips` for each Power, keyword, or Card the new text names. |
| keep the Card and add an effect | `card.play.on-play` `compose`, plus either `card.description.localization` (the whole text rewritten as one vanilla-style body) or a `card.description.fragments` line before/after the original. |
| change cost, type, rarity, target, tags, playability, result pile, or glow | the matching property/cost/state route. The vanilla rules text never states these, so no text operation follows unless the user names one. |
| rename the Card | `card.title.localization`, only when the user asked for a new name. |

**Unchanged by default.** Every surface the user did not name stays vanilla: name, cost,
type, rarity, art, keywords, tags, and the parts of the rules text the change does not touch.
A behavior or number change never renames the Card or adds a prefix, suffix, `+`, or "modified"
marker; the changed rules text is how the player sees the change. When the request is
ambiguous about a surface, keep it vanilla and say so at confirmation instead of guessing.

Every behavior change keeps the Card's rules text true. If the new behavior and the vanilla
description would disagree, the plan is incomplete until it carries the text operation from
the table above.

## Promoted public surface

| Semantic surface | Route id | Public contract |
|---|---|---|
| Card type | `card.property.type` | `ICardPropertyContributor.GetCardType` |
| rarity | `card.property.rarity` | `ICardPropertyContributor.GetCardRarity` |
| target | `card.property.target` | `ICardPropertyContributor.GetTargetType` |
| appended tags | `card.property.tags` | `ICardPropertyContributor.GetTags`; all contributions append and deduplicate |
| evaluated Energy cost | `card.cost.energy` | `ICardEnergyCostContributor.ModifyEnergyCost` |
| evaluated Star cost | `card.cost.stars` | `ICardStarCostContributor.ModifyStarCost` |
| conditional playability | `card.play-state.can-play` | `ICardPlayStateContributor.CanPlay`; no decision returns `null` |
| result pile | `card.play-result.pile` | `ICardPlayResultContributor.GetResultPileTypeForCardPlay` |
| vanilla variable values | `card.vars.base` | canonical `DynamicVars[name].BaseValue` at `ModelRegistryInitializedEvent`; optional upgrade fixup in `CardCapability.OnOwnerCardUpgraded` |
| rules text replacement | `card.description.localization` | the Mod's `cards.json` overrides the vanilla `<ENTRY>.description` key through the game's localization merge |
| name replacement | `card.title.localization` | the Mod's `cards.json` overrides the vanilla `<ENTRY>.title` key through the game's localization merge |
| description fragments | `card.description.fragments` | `ICardDescriptionContributor`; before/after only |
| displayed type text | `card.type-text` | `ICardTypeTextModifier`; `{Type}` wraps, omission replaces |
| hover tips | `card.hover-tips` | `ICardHoverTipContributor` plus typed factories or localized `HoverTip` |
| native gold/red glow | `card.glow.gold`, `card.glow.red` | `ICardGlowContributor` |
| capability-owned variables | `card.capability.dynamic-vars` | `CardCapability.CanonicalVars` and its saved/cloned `DynamicVars` |
| compose/replace `OnPlay` | `card.play.on-play` | `CardPlayCapability` before/after owner play and public suppression |
| owner lifecycle composition | `card.owner-hooks` | typed owner hook stream for owner draw/discard/exhaust |

Card frame/portrait/banner material providers are promoted separately in
`vanilla-visual-overrides.md` because they require asset packaging and presentation
contracts. `HasTurnEndInHandEffect` alone only asks the game to call the vanilla Card's own
protected handler; do not turn it on without a grounded compatible owner behavior. A
target-bound override must not implement `ICardTransformCarryOverCapability`: transforming
into another Card identity must drop the old target's capability.

These routes do not change Energy/Star X-cost identity, remove tags, change keywords,
acquisition pools, or Card materials. `card.vars.base` changes only the values of variables
the vanilla Card already declares; a new number belongs to a capability variable.

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
- a vanilla variable's new `base_value` and optional new `upgrade_delta`;
- the target's own title or description key for a name or rules-text replacement;
- a playability `decision` plus a declarative `when` predicate;
- a vanilla result pile (`Draw`, `Hand`, `Discard`, or `Exhaust`) or a stable owned-pile
  semantic id already authored through `card-piles.md`;
- a localization table/key plus a checked description-fragment or type-text placement;
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
type-text, description key, `OnPlay` surface, or vanilla variable conflict.

## Vanilla variable values

`card.vars.base` sets one existing vanilla variable. The baseline copies the target's
`properties.dynamic_vars` and `properties.upgrade_levels` from the catalog:

```json
{
  "order": 0,
  "operation_id": "strike.damage",
  "target_model_id": "CARD.STRIKE_IRONCLAD",
  "mode": "adjust",
  "surface": "card.dynamic_vars",
  "route": { "class": "public", "id": "card.vars.base", "fingerprint": null },
  "expected_baseline": {
    "category": "CARD",
    "type": "MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad",
    "properties": {
      "dynamic_vars": [
        { "name": "Damage", "type": "MegaCrit.Sts2.Core.Localization.DynamicVars.DamageVar", "base_value": 6 }
      ],
      "upgrade_levels": [
        { "level": 1, "energy_cost": 1, "star_cost": -1, "dynamic_vars": [
          { "name": "Damage", "type": "MegaCrit.Sts2.Core.Localization.DynamicVars.DamageVar", "base_value": 9 }
        ] }
      ]
    }
  },
  "semantics": { "variable": "Damage", "base_value": 9, "upgrade_delta": 4 }
}
```

`upgrade_delta` is the new amount one upgrade adds; `null` keeps the vanilla upgrade. The
validator rejects an unknown variable, a computed `Calculated*` variable (set its
`CalculationBase`/`CalculationExtra` input instead), an `upgrade_delta` equal to the vanilla
one, and a second operation on the same variable.

Assign the new base on the canonical model when `ModelDb` is ready. Every mutable Card is
cloned from the canonical model, including the starter deck, rewards, generated combat
Cards, a downgrade, and a Card restored from a save, so they all inherit it. The event can
publish more than once; assign the absolute value, never `+=`:

```csharp
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using STS2RitsuLib;

static partial void RegisterContent()
{
    RitsuLibFramework.SubscribeLifecycle<ModelRegistryInitializedEvent>(_ =>
        ModelDb.Card<StrikeIronclad>().DynamicVars["Damage"].BaseValue = 9m);
}
```

A changed upgrade adds the difference after the vanilla upgrade body runs. Vanilla Strike
adds 3, so a new `upgrade_delta` of 4 adds 1 more. Put it in the target's capability:

```csharp
protected override void OnOwnerCardUpgraded(CardModel card) =>
    card.DynamicVars["Damage"].UpgradeValueBy(1m);
```

The vanilla Card has a single upgrade level, and a downgrade re-clones the canonical
values, so this fixup needs no downgrade handler. This is the only owner-variable write a
capability makes.

Observed on the pinned host with Strike `Damage` 9 / `upgrade_delta` 4: canonical, new
mutable copy, starter deck, upgraded copy 13, save round trip 13, downgrade 9, combat
damage 9 and 13, and hand text `Deal 9 damage.` / `Deal 13 damage.` all followed.

## Rules text replacement

`card.description.localization` replaces the Card's whole vanilla description. The game
merges each Mod's `localization/<lang>/<table>.json` into the base table and the Mod value
wins, so the Mod ships the vanilla key itself:

```json
{
  "order": 1,
  "operation_id": "strike.description",
  "target_model_id": "CARD.STRIKE_IRONCLAD",
  "mode": "replace",
  "surface": "card.description_text",
  "route": { "class": "public", "id": "card.description.localization", "fingerprint": null },
  "expected_baseline": {
    "category": "CARD",
    "type": "MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad",
    "description_localization": {
      "key": "STRIKE_IRONCLAD.description",
      "localized_descriptions": {
        "eng": "Deal {Damage:diff()} damage.",
        "zhs": "造成{Damage:diff()}点伤害。"
      }
    }
  },
  "semantics": { "localization": { "table": "cards", "key": "STRIKE_IRONCLAD.description" } }
}
```

```text
<ModName>/localization/eng/cards.json  {"STRIKE_IRONCLAD.description": "Deal {Damage:diff()} damage.\nDraw 1 card."}
<ModName>/localization/zhs/cards.json  {"STRIKE_IRONCLAD.description": "造成{Damage:diff()}点伤害。\n抽1张牌。"}
```

The baseline's vanilla text is drift protection: a game update that rewrites the vanilla
description fails the build instead of silently replacing new text. No C# is generated for
this route. Do not also write the title key unless SPEC renames the Card.

The vanilla description is formatted before any capability runs, so it can reference only
the Card's own `DynamicVars`, variables the vanilla text already uses, and the fixed Card
description variables (`IfUpgraded`, `OnTable`, `InCombat`, `IsTargeting`, `TargetType`,
`GainsBlock`, `IsOstyAlive`, `energyPrefix`, `singleStarIcon`). Build rejects any other
variable. For a new number, write a fixed literal when it never changes, or put that line in
a `card.description.fragments` fragment, which does see capability variables.

The replacement is global: the Card library and every view of the Card show it. Build
requires `eng` and `zhs`; every other language the Mod does not ship keeps the vanilla text,
so report that. If another loaded Mod replaces the same key, the later-loaded Mod wins.

## Name replacement

`card.title.localization` renames the Card the same way, through its vanilla
`<ENTRY>.title` key: `mode: replace`, surface `card.title`, baseline `title_localization`
with its key and vanilla `eng`/`zhs` titles, and semantics
`{"localization": {"table": "cards", "key": "<ENTRY>.title"}}`. Use it only when the user
asked for a new name. Write the complete new name; the game still appends `+` to an
upgraded Card. A title is formatted without variables, so Build rejects any `{...}` in it.
Every consumer that reads the title key sees the new name, including the hover text of
Powers and timeline entries that name the Card. Observed on the pinned host: Defend renamed
`Brace`/`架势` resolved through `Title`, the raw title key, and the upgraded `Brace+`/`架势+`.

## Registration

Create a capability through the content registry so `ModelDb` owns its identity, clone,
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
A manifest with only `card.vars.base` (no `upgrade_delta`) and text replacement needs no
capability.

## Capability lowering

Start with `CardPlayCapability` when any play behavior is selected. Otherwise
`CardCapability` is enough. Implement only the contributor interfaces selected by the
manifest. A combined shape for "Strike becomes a cheaper Common that gains Block before its
attack and exhausts" is:

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

    public IEnumerable<CardDescriptionFragment> GetDescriptionFragments(
        CardDescriptionContext context) =>
        [new(new LocString("cards", $"{Id.Entry}.extraDescription"),
            CardDescriptionFragmentPlacement.BeforeBase, 0)];

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

The Card keeps its vanilla name. The Block line is a fragment because it reads the
capability's `Block` variable. This is a shape, not a request to emit every interface. Keep
generated code as small as the accepted manifest. Use the catalog's concrete target type.
Emit fragments and effects in manifest order, and use each operation order as the fragment
`Order` when RitsuLib exposes one.

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
silently retain part of the vanilla body. A replacement that still deals the vanilla
damage reads the owner's `Damage` variable, so a `card.vars.base` change reaches it too.

Capability-owned variables clone and save through RitsuLib. Apply their upgrade deltas in
`OnOwnerCardUpgraded`. The default capability follows clones of the same target identity.
It does not carry to a different transformed Card. On downgrade, rebuild capability-owned
values from the manifest baseline and current owner upgrade level rather than subtracting
from an unknown state.

## Localization and checks

Capability localization lives in the normal Mod resource tree. Use stable capability-entry
keys such as `<MOD>_MODEL_CAPABILITY_<TYPE>.extraDescription` in the selected table; only
`card.description.localization` and `card.title.localization` write a vanilla key. Supply required `eng` and `zhs` plus
every additional language named by the accepted SPEC, and preserve SmartFormat variables.
Write every replacement, fragment, name, and type text in the Card row of
`reference/vanilla-text-style.md` so it reads like a vanilla Card: glossary terms in `[gold]`
with their exact `eng`/`zhs` names, uncolored `:diff()` numbers, one effect per line, and
Chinese full-width punctuation. Text that names a Power, keyword, or Card also adds its tip
through `card.hover-tips`.

Tier 2 resolves the changed Card's title and description through the real Card in both
`eng` and `zhs`, asserts the title still equals the catalog's vanilla title unless SPEC
renamed it, and asserts the description shows the new numbers. Never claim real-game
behavior, preview, clone/save, transform, payment, targeting, result-pile, or presentation
proof that was not observed in a real host. A focused manifest test and a successful compile
establish neither. Report every unrun path as an explicit exception rather than a pass.
