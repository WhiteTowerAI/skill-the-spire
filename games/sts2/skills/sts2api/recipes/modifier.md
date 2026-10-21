# Recipe: Modifier

Use for a selectable good or bad daily/custom-run rule that lasts one run. A Modifier is part of
`RunState.Modifiers`, is saved with that run, and receives both run and combat model hooks. It is
not a Settings toggle, a generic Global Effect, or a replacement for an obtainable model. Extend
`ModModifierTemplate`, register one polarity once, and let the selected mutable instance in
`RunState.Modifiers` own run-lifetime behavior and saved model properties; never keep current-run
state on the canonical `ModelDb` instance or a process static.

## DESIGN and SPEC vocabulary

Settle and write:

- identity and polarity: good or bad;
- custom/daily list placement, with an explicit integer sort order when placement matters;
- mutually exclusive groups and every other Modifier type in each group;
- effect triggers, guards, order, neutral behavior, and state owner;
- new-run initialization versus load restoration, including whether the starting deck is cleared;
- an optional Neow choice and its deterministic awaited outcome;
- title, description, Neow text, hover tips, optional Rest Site Heal text, and icon choice; and
- `RunStart`/`CombatPlayer` SelfTest, a save/load case when state persists, and headed
  selection/icon review.

## Registration

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .GoodModifier<Modifiers.<GoodName>>(modifierListSortOrder: <integer>)
    .BadModifier<Modifiers.<BadName>>(modifierListSortOrder: <integer>)
    .MutuallyExclusiveModifierGroup(typeof(Modifiers.<GoodName>), typeof(Modifiers.<BadName>))
    .Apply();
```

Generate only the selected classes. A negative sort order places a Mod entry before the built-in
segment, a nonnegative one after it; within a Mod slice, order is the integer then the fully
qualified type name. An exclusivity group needs at least two distinct concrete Modifier types, and
overlapping groups merge. Never register one type with both polarities or invent a setup-screen
host.

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

`ModifierModel` is run-lifetime and serializes through its Model id plus saved properties. The host
sets `RunState` before either callback. Persist semantic fields through the normal saved
property/state route; use `AfterRunLoaded` for transient wiring, never to duplicate new-run grants.
`ClearsPlayerDeck` happens before `AfterRunCreated` and is an explicit design choice.

`AfterRunCreated` and `AfterRunLoaded` are synchronous and cannot run awaited effects. Ordinary
effects go in an actual async run/combat hook whose signature matches the SPEC trigger, combining
only its concrete Player/Creature/Card/choice-context parameters with
`reference/effect-primitives.md`; the Modifier supplies identity and run lifetime, not an
automatic Player, target, Card source, or `PlayerChoiceContext`. Block with the exact missing
input rather than moving an effect into setup or a process listener.

Override `GenerateNeowOption(EventModel)` only when SPEC selects a real Neow option: return a
function that awaits the complete deterministic outcome, or `null` for no option. Override
`NeowOptionTitle`, `NeowOptionDescription`, and `HoverTips` only when their distinct presentation
is selected.

## Hook participation and optional routes

Raw hooks use `reference/model-hook-participation.md` with `surface: modifier`; the host exposes
the full run and combat listener reachability. Read `reference/model-capabilities.md`,
`reference/lifecycle-state-rng.md`, and `reference/shared-effect-hooks.md` only for their selected
separable behavior. A Modifier-owned independent Rest Site action uses
`reference/rest-site-options.md`. Never use a Global Effect for a rule whose visible identity is
the selected Modifier.

## Text and icon

Use matching `eng`/`zhs` `modifiers.json` entries:

```json
{
  "<MOD>-<MODIFIER>.title": "<plain title>",
  "<MOD>-<MODIFIER>.description": "Start each combat with [blue]3[/blue] [gold]Vulnerable[/gold].",
  "<MOD>-<MODIFIER>.additionalRestSiteHealText": "<optional heal text>"
}
```

Follow the Modifier row of `reference/vanilla-text-style.md`: plain title, `[blue]` numbers,
`[gold]` glossary terms, `[red]` only for a harsh downside, and the glossary's Chinese terms
(`每场战斗开始时获得[blue]3[/blue]层[gold]易伤[/gold]。`). Use the optional heal-text key only with a
selected Rest Site Heal hook.

Custom icon code returns a `ModifierAssetProfile` pointing to an existing packed texture. With no
custom path, the native getter uses the checked missing-Power icon fallback; visual quality still
needs the real selection list.

## Proof matrix

Use the real custom-run/daily selection host and the resulting run:

1. assert the registered polarity, deterministic placement, exact localization, icon fallback, and
   selection state;
2. select one member of an exclusivity group and assert every other group member is unticked;
3. start a new run and assert the exact mutable Modifier identity, `AfterRunCreated` behavior, the
   optional deck clear, and effect/neutral cases;
4. save and reload, and assert serialized properties and `AfterRunLoaded` restoration without
   replaying new-run-only mutations;
5. exercise any selected Neow option through the real Event and await its complete outcome; and
6. assert no effect in a run where the Modifier is absent.

Headed review owns list layout, color, icon framing, controller selection, and Neow presentation.
Compiling the registration and lifecycle is not game observation.
