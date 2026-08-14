# Recipe: Modifier

Use for a new good or bad daily/custom-run rule. Extend `ModModifierTemplate`, register one
polarity once, and let the selected mutable instance in `RunState.Modifiers` own behavior.

## Registration

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .GoodModifier<Modifiers.<GoodName>>(modifierListSortOrder: <integer>)
    .BadModifier<Modifiers.<BadName>>(modifierListSortOrder: <integer>)
    .MutuallyExclusiveModifierGroup(typeof(Modifiers.<GoodName>), typeof(Modifiers.<BadName>))
    .Apply();
```

Generate only the selected good/bad classes. Negative sort order places a Mod entry before the
built-in segment; nonnegative places it after. Within a Mod slice, order is integer then fully
qualified type name. Exclusivity needs at least two distinct concrete Modifier types, and
overlapping groups merge. Do not register the same type with both polarities.

## Model and lifecycle

```csharp
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Modifiers;

public sealed class <ModifierName> : ModModifierTemplate
{
    public override bool ClearsPlayerDeck => <true-or-false>;

    protected override void AfterRunCreated(RunState runState)
    {
        // New run only. Initialize immediate state; do not replay this on load.
    }

    protected override void AfterRunLoaded(RunState runState)
    {
        // Restore only nonserialized/runtime bindings.
    }
}
```

`ModifierModel` is run-lifetime and serializes through its Model ID plus saved properties. The
host sets `RunState` before either callback. Persist semantic fields with the normal model saved
property/state route; use `AfterRunLoaded` for transient wiring, not to duplicate new-run grants.
`ClearsPlayerDeck` happens before `AfterRunCreated` and must be an explicit design choice.

Override `GenerateNeowOption(EventModel)` only when SPEC selects a real Neow option. Return a
function that awaits the complete deterministic outcome, or `null` for no option. Override
`NeowOptionTitle`, `NeowOptionDescription`, and `HoverTips` only when their distinct presentation
is selected.

## Text and icon

Use matching `eng`/`zhs` `modifiers.json` entries:

```json
{
  "<MOD>-<MODIFIER>.title": "<title>",
  "<MOD>-<MODIFIER>.description": "<description>",
  "<MOD>-<MODIFIER>.additionalRestSiteHealText": "<optional heal text>"
}
```

Use the optional heal-text key only with a selected Rest Site Heal hook. Custom icon code returns
a `ModifierAssetProfile` pointing to an existing packed texture. With no custom path, the native
Modifier getter uses the checked missing-Power icon fallback; visual quality still requires the
real selection list.

## Effects and proof

For raw model hooks, use `reference/model-hook-participation.md` with `surface: modifier`. For
state/RNG/shared effect services use the selected shared references. A Modifier-owned independent
Rest Site action uses `reference/rest-site-options.md`; it is not a Global Effect.

SelfTest must select the Modifier through the real setup host, assert exclusivity/order, start a
run, test effect and neutral cases, then save/load without replaying new-run behavior. Headed review
owns the good/bad list, icon, controller interaction, and Neow option layout.
