# Reference: computed Card values and variable tooltips

> Pinned to STS2 `0.107.1` and RitsuLib `0.5.11`. Use this page only when a
> Card description contains a value calculated from live state. Static upgrade
> values continue to use the ordinary `DamageVar`, `BlockVar`, or `PowerVar<T>`
> patterns in `recipes/card.md`.

<!-- open-mod-surface-contract/v1
{
  "family": "computed_card_values",
  "owner": "reference/card-computed-values.md",
  "spec_key": "computed_card_values",
  "profile": {"sts2": "0.107.1", "ritsulib_compat": "0.5.11"},
  "fields": {
    "values": {"type": "list<object>", "cardinality": "0..*", "default": []},
    "values[].card_id/name": {"type": "text", "cardinality": "1 each", "unique": "name per card_id"},
    "values[].role/evaluation_point/text_binding": {"type": "enum", "cardinality": "1 each"},
    "values[].formula/upgrade_rule": {"type": "text", "cardinality": "1 each"},
    "values[].inputs/declared_inputs": {"type": "list<text>", "cardinality": "0..*"},
    "values[].domain.min/max": {"type": "integer", "cardinality": "1 each"},
    "values[].preview_point/execution_point": {"type": "evaluation enum", "cardinality": "1 each"},
    "values[].native_modifiers": {"type": "none or exactly_once", "cardinality": "1"},
    "values[].route": {"type": "declared route", "cardinality": "1"}
  },
  "enums": {
    "role": ["plain", "damage", "block", "energy_icons", "star_icons", "raw_power", "applied_power"],
    "evaluation_point": ["before_payment", "after_payment", "after_source_moves_to_play"],
    "text_binding": ["dynamic_var", "icon_formatter"]
  },
  "conditions": [
    "names are unique per Card",
    "formula inputs exactly match declared_inputs",
    "preview_point and execution_point equal evaluation_point"
  ],
  "mutually_exclusive": [
    "icon_formatter with non-icon role",
    "hook-modified preview value reused as execution input"
  ],
  "routes": [
    "reference/card-computed-values.md#semantic-gate",
    "reference/card-computed-values.md#one-formula-for-base-upgrade-preview-and-execution"
  ],
  "hard_boundaries": [
    "formula is pure and has no RNG Cmd or mutation",
    "native modifiers apply exactly once for damage block and applied Power",
    "zero rendering remains role-specific"
  ],
  "generated_obligations": [
    "emit one DynamicVar factory per declared value",
    "reuse one formula across preview and execution",
    "bind every declared player-facing value to text or icons"
  ],
  "evidence": {"framework_expressible": true, "open_mod_authorable": true, "game_observed": false},
  "legacy": "v1/v2 single-value projects resume unchanged; revised calculated values write the v3 list"
}
-->

## Semantic gate

Before writing C#, every calculated value in SPEC must declare independently:

- a stable value name and one role: plain, damage, block, Energy icons, Star icons,
  raw typed Power, or applied typed Power;
- one deterministic formula and its complete input list;
- an integer domain with an explicit lower bound and any finite upper bound required by
  gameplay or layout;
- base-card and upgraded behavior;
- the evaluation point relative to the source Card paying its cost and moving from Hand
  to Play; and
- either no tooltip or a localized title/description plus an optional checked icon.

The formula must be pure: no RNG, Cmd, state mutation, logging, or dependence on wall-clock
or render-call count. Preview evaluation can happen repeatedly. If payment, pile movement,
or another normal play transition changes an input, the preview factory must simulate the
declared evaluation point through the same helper used for live execution. Stop authoring
when the two phases cannot be reconciled deterministically.

Energy and Star icon counts are nonnegative integers. Star counts also need a finite
layout-tested maximum because `starIcons()` emits one image per Star. Damage, Block, and
Power domains follow the effect's declared semantics; do not rely on a formatter or Cmd to
repair an invalid formula.

## RitsuLib variable selection

All helpers below come from `STS2RitsuLib.Cards.DynamicVars`:

| Semantic role | Factory | Localization | Execution read |
|---|---|---|---|
| plain computed number | `ModCardVars.Computed` | `{Name}` or `{Name:diff()}` | `ComputeDynamicValue("Name", target: target)` |
| normal attack damage | `ModCardVars.ComputedDamage` | `{Damage:diff()}` | `ComputeDynamicValue("Damage", target: target)` |
| normal Card Block | `ModCardVars.ComputedBlock` | `{Block:diff()}` | `ComputeDynamicValue("Block", target: target)` |
| Energy icon count | `ModCardVars.ComputedEnergy` | `{EnergyGain:energyIcons()}` | `ComputeEnergyValue("EnergyGain", target: target)` |
| Star icon count | `ModCardVars.ComputedStars` | `{StarGain:starIcons()}` | `ComputeStarsValue("StarGain", target: target)` |
| raw typed Power number | `ModCardVars.ComputedPower<T>` | `{PowerKey:diff()}` | `ComputePowerValue<T>("PowerKey", target: target)` |
| Power amount being applied | `ModCardVars.ComputedPowerAmountGiven<T>` | `{PowerKey:diff()}` | `ComputePowerValue<T>("PowerKey", target: target)` |

Use plain `Computed` only when damage, Block, and Power-application hooks intentionally do
not apply. `ComputedDamage` previews normal damage hooks such as Strength and Vulnerable;
`ComputedBlock` previews normal Block hooks such as Dexterity and Frail.
`ComputedPower<T>` displays the raw typed amount. `ComputedPowerAmountGiven<T>` sends its
preview through `ModifyPowerAmountGiven`; use it when the Card will apply that Power.

## One formula for base, upgrade, preview, and execution

Put each declared calculation in one helper and emit one matching DynamicVar factory. A Card
may compose zero or more uniquely named values; names need only be unique on that Card.
`CardPreviewMode.Upgrade` must select the upgraded
branch even when the preview host has not yet exposed a normally upgraded Card instance.
Live execution calls the same helper indirectly through the matching `Compute*Value`
extension:

```csharp
using System;
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Cards.DynamicVars;

private static decimal ResolveDamage(
    CardModel? card,
    CardPreviewMode previewMode,
    Creature? target)
{
    bool upgraded = previewMode == CardPreviewMode.Upgrade || card?.IsUpgraded == true;
    decimal liveInput = card?.Owner.Creature.Block ?? 0m;
    return Math.Clamp(liveInput + (upgraded ? 2m : 0m), 0m, 20m);
}

protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
{
    ModCardVars.ComputedDamage(
        "Damage",
        0m,
        (card, target) => ResolveDamage(card, CardPreviewMode.None, target),
        (card, mode, target, _) => ResolveDamage(card, mode, target),
        ValueProp.Move),
};
```

The `baseValue` argument is the stable baseline/fallback used by DynamicVar display
machinery. It is not a second formula. A computed-only upgrade normally branches in the
shared helper; do not call `UpgradeValueBy` on it as a substitute and do not duplicate the
formula in `OnUpgrade()`.

`PreviewValue` is display-only. `BaseValue` is not the live result of a computed variable.
Never use either one to execute a computed effect.

## Execute the raw amount exactly once

The hook-aware Damage, Block, and applied-Power factories preview their normal modifiers.
The corresponding game Cmd applies those modifiers during execution. Therefore execution
reads the raw calculation and passes it to the Cmd; it never feeds the already modified
`PreviewValue` back into the Cmd. Plain, Energy, Stars, and raw typed-Power factories do
not add those modifier families.

```csharp
ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
decimal rawDamage = base.DynamicVars.ComputeDynamicValue(
    "Damage", target: cardPlay.Target);
await DamageCmd.Attack(rawDamage)
    .FromCard(this)
    .Targeting(cardPlay.Target)
    .WithHitFx("vfx/vfx_attack_slash")
    .Execute(choiceContext);
```

For computed Block, use the decimal overload with `ValueProp.Move` and `cardPlay`. This
keeps the Card source and runs normal Block hooks once:

```csharp
decimal rawBlock = base.DynamicVars.ComputeDynamicValue("Block");
await CreatureCmd.GainBlock(
    base.Owner.Creature, rawBlock, ValueProp.Move, cardPlay);
```

For Energy and Stars, the icon variable represents the requested amount. Pass that raw
amount to the matching public Cmd. A neutral proof expects the observed delta to match;
normal Energy/Star gain hooks may still change or reject the final runtime result.

```csharp
decimal energy = base.DynamicVars.ComputeEnergyValue("EnergyGain");
decimal stars = base.DynamicVars.ComputeStarsValue("StarGain");
await PlayerCmd.GainEnergy(energy, base.Owner);
await PlayerCmd.GainStars(stars, base.Owner);
```

For a Power that the Card applies, the preview is hook-aware but the execution amount is
still raw. `PowerCmd.Apply<T>` runs `ModifyPowerAmountGiven` once:

```csharp
protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
{
    ModCardVars.ComputedPowerAmountGiven<PoisonPower>(
        2m,
        (card, target) => ResolvePoison(card, CardPreviewMode.None, target),
        (card, mode, target, _) => ResolvePoison(card, mode, target)),
};

// In OnPlay, after the target null-check:
decimal rawPoison = base.DynamicVars.ComputePowerValue<PoisonPower>(
    nameof(PoisonPower), target: cardPlay.Target);
await PowerCmd.Apply<PoisonPower>(
    choiceContext,
    cardPlay.Target,
    rawPoison,
    base.Owner.Creature,
    this);
```

## Icon formatter behavior

The pinned SmartFormat names are exactly `energyIcons()` and `starIcons()`.

- Energy values 1 through 3 render repeated Energy icons.
- Energy 0 and values outside 1 through 3 render the highlighted number plus one Energy
  icon; Energy 0 is therefore not an empty result.
- Stars render one Star image per count; Stars 0 renders no image.

Describe these as zero-valued rendering, not as a universal "zero icons" rule. The headed
proof must inspect zero, multiple icons, the finite maximum, line wrapping, and stale-glyph
cleanup after the input changes.

## Variable tooltips

Attach a shared tooltip only when SPEC declares its text. Use a deterministic entry stem
derived from the Card public entry and variable name, then author the same two flat keys in
both required languages' `static_hover_tips.json`:

```csharp
ModCardVars.ComputedEnergy(
        "EnergyGain",
        0m,
        card => ResolveEnergy(card, CardPreviewMode.None),
        (card, mode, _, _) => ResolveEnergy(card, mode))
    .WithSharedTooltip("<MOD>_CARD_<TYPE>_ENERGY_GAIN")
```

```json
{
  "<MOD>_CARD_<TYPE>_ENERGY_GAIN.title": "Stored Charge",
  "<MOD>_CARD_<TYPE>_ENERGY_GAIN.description": "This is the Energy this card will gain."
}
```

Omitting the `iconPath` argument intentionally creates the native null-icon Hover Tip.
Pass an icon only when the generated Mod owns an existence-checked resource path; a blank
or invented fallback image is not required. RitsuLib copies the tooltip registration when
a `DynamicVar` is cloned, and the real `CardModel.HoverTips` consumer appends the result.
The focused proof must still observe both behaviors on a mutable hand Card.

## Focused proof contract

Use one disposable `CombatPlayer` suite, not a fresh natural-language acceptance Mod:

1. Damage and Block: zero, positive, changing input, base and upgrade previews,
   Strength/Vulnerable and Dexterity/Frail, then exact final HP/Block deltas.
2. Energy and Stars: zero-valued rendering, multiple icons, finite maximum, text reflow,
   no clipping/stale glyphs, and exact neutral `GainEnergy`/`GainStars` deltas.
3. Typed Power: obtain vanilla `SneckoSkull`; with raw Poison 2, prove
   `ComputedPower<PoisonPower>` remains 2, `ComputedPowerAmountGiven<PoisonPower>` previews
   3, and `PowerCmd.Apply` leaves Poison 3.
4. Tooltip: localized title/description, omitted-icon fallback, clone survival, and the
   real hand-Card hover consumer.

Behavior proof records structured expected/observed state and ends with `selftest done`.
The headed reviewer separately confirms Card text, icons, reflow, and Hover Tips. A trigger
or calculation log is diagnostic only and cannot replace either observation.
