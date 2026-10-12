# Surface: Rest Site

Use this surface when the requested product is an independent action in the native Rest Site,
rather than an action owned by a Card or Relic. It lowers to a Run `HookedSingletonModel` that
contributes a `ModRestSiteOptionTemplate` through the normal owner hooks. Card, Relic, and Modifier
owners keep their own truthful identities and use the same shared reference.

## DESIGN and SPEC vocabulary

Settle and write:

- owner: standalone, one concrete Card, one concrete Relic, or one selected Modifier;
- availability versus enabled/affordability, exact singleplayer boundary, and duplicate-ID rule;
- free or one fixed nonnegative Gold cost;
- all failure-prone preflight checks before the first mutation;
- ordered deterministic outcome, repeatability once per site or once per run, and leave versus
  keep other options;
- stable option ID, English/Simplified Chinese title and description, icon choice/fallback; and
- real Rest Site state matrix plus headed mouse/controller/icon review.

This maintained route does not promise variable/non-Gold costs, a player choice after payment,
arbitrary rollback, same-visit successful repeat, or multiplayer.

## Text style

Write every player-facing string in the default style of `reference/vanilla-text-style.md`:
the button title stays plain Title Case; the description is one sentence with `[blue]`
counts, `[green]` heals and Max HP gains, and `[gold]` glossary terms
(`[gold]Upgrade[/gold] a card in your [gold]Deck[/gold].`).

## Authoring route

Read `recipes/rest-site.md` and `reference/rest-site-options.md`. The recipe selects the owner
class; the reference owns native generation, stale-button final recheck, option removal,
stay/leave, state, localization, icon fallback, and proof. Do not declare either Rest Site hook as
raw hook participation.

Standalone ownership uses one Run `HookedSingletonModel` registered through `.Singleton<T>()`.
Its transient keep-remaining signal and repeat state attach to the concrete Player/run, not the
canonical singleton. Modifier ownership uses the selected mutable Modifier instance already in
`RunState.Modifiers`; it does not create a second global owner.

## Ordinary effect projection

The selected `ModRestSiteOptionTemplate.OnSelect()` owns a blocking run transaction and provides
its exact owner Player. After the shared route's stale-button final recheck, use
`reference/effect-primitives.md` only for deterministic run-safe child effects such as Gold,
healing/Max HP gain, or known acquisition. Complete all failure-prone checks before payment or any
other mutation, await every command, inspect rejected results, then mark success and apply the
declared stay/leave behavior. The option has no live combat `PlayerChoiceContext`, target, Card
play, combat piles, Energy/Stars, or Orb queue; those primitives block instead of being simulated.

## Proof matrix

Follow the complete matrix in `reference/rest-site-options.md`: absent, disabled, enabled,
render-then-invalidate rejection, exact success, option-history identity, keep/leave behavior,
repeat edge, unrelated native option preservation, custom icon, native fallback, localization,
and controller focus. Add owner-specific assertions:

- standalone: fresh run ownership and no state leak to a second run;
- Card: zero/one/duplicate concrete deck instances;
- Relic: exact owned instance and removal boundary; or
- Modifier: selected/absent run and save/load restoration.

No new owner profile is game-observed merely because the existing Relic proof passed.
