# Recipe: Rest Site

Use for an independently requested native Rest Site action rather than one a Card or Relic owns.
This recipe chooses the truthful owner; `reference/rest-site-options.md` owns the option
implementation and host lifecycle (native generation, stale-button final recheck, option removal,
stay/leave, state, localization, icon fallback, and proof). Read and follow that reference
completely. Card, Relic, and Modifier owners keep their own identities and use the same reference.

## DESIGN and SPEC vocabulary

Settle and write:

- owner: standalone, one concrete Card, one concrete Relic, or one selected Modifier;
- availability versus enabled/affordability, the exact singleplayer boundary, and the duplicate-id
  rule;
- free or one fixed nonnegative Gold cost;
- every failure-prone preflight check before the first mutation;
- the ordered deterministic outcome, repeatability once per site or once per run, and leave
  versus keep other options;
- a stable option id, the English/Simplified Chinese title (plain Title Case) and description (one
  sentence with `[blue]` counts, `[green]` heals and Max HP gains, `[gold]` glossary terms, e.g.
  `[gold]Upgrade[/gold] a card in your [gold]Deck[/gold].`), and the icon choice/fallback; and
- the real Rest Site state matrix plus headed mouse/controller/icon review.

The route never promises variable or non-Gold costs, a player choice after payment, arbitrary
rollback, same-visit successful repeat, or multiplayer.

## Owner selection

- standalone action: one Run `HookedSingletonModel`, registered through `.Singleton<T>()`;
- Card action: the exact single mutable Card instance in the owner's deck;
- Relic action: the exact owned Relic instance; or
- Modifier action: the selected mutable instance already in `RunState.Modifiers`, with no second
  global owner.

Each owner overrides `TryModifyRestSiteOptions` and, only for keep-remaining behavior,
`ShouldDisableRemainingRestSiteOptions`. The option extends `ModRestSiteOptionTemplate` and is not
registered separately. Never declare these two hooks as raw hook participation; the shared
reference owns their bounded transaction and UI lifecycle.

Standalone registration and owner:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Singleton<RestSite.<OptionOwner>>()
    .Apply();
```

```csharp
using MegaCrit.Sts2.Core.Entities.Players;
using STS2RitsuLib.Models;
using STS2RitsuLib.Utils;

public sealed class <OptionOwner> : HookedSingletonModel
{
    private static readonly AttachedState<Player, bool> KeepRemainingOnce = new();

    public <OptionOwner>() : base(HookType.Run) { }

    // Contribute <Option> from TryModifyRestSiteOptions.
    // Store/consume the one-shot keep signal on the concrete Player, never on this singleton.
}
```

The standalone singleton's transient keep-remaining signal and repeat state attach to the
concrete Player/run, never the canonical singleton. Modifier ownership uses the same flow without
a singleton, because the run listener set already walks the selected Modifier; its once-per-run
state lives in that Modifier's saved model state or a declared run/player saved slot, and
per-visit signaling uses attached state.

## The effect sequence

The selected `ModRestSiteOptionTemplate.OnSelect()` owns a blocking run transaction and provides
its exact owner Player. After the reference's stale-button final recheck, lower only deterministic
run-safe child effects (Gold, healing/Max HP gain, known acquisition) through
`reference/effect-primitives.md`. Finish every failure-prone check before payment or any other
mutation, await every command, inspect rejected results, then mark success and apply the declared
stay/leave behavior. The option has no live combat `PlayerChoiceContext`, target, Card play,
combat piles, Energy/Stars, or Orb queue; those primitives are blocked, never simulated.

## Proof matrix

Drive each case as a `plan.RestSite` scenario (`reference/selftest-harness.md` § Rest Site
options) with the owner and Gold set up in `beforeEnter`. Follow the complete matrix in
`reference/rest-site-options.md`: absent, disabled, enabled, render-then-invalidate rejection,
exact success, option-history identity, keep/leave behavior, repeat edge, unrelated native option
preservation, custom icon, native fallback, localization, and controller focus. Add the
owner-specific assertions:

- standalone: fresh run ownership and no state leak into a second run;
- Card: zero, one, and duplicate concrete deck instances;
- Relic: the exact owned instance and its removal boundary; or
- Modifier: selected versus absent run, and save/load restoration.
