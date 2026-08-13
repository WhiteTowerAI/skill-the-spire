# Surface: Global Effect

Use this surface only for a rule with no truthful obtainable or selectable model owner. The public
route is a registered `HookedSingletonModel` whose constructor permanently selects exactly one
stream: Run or Combat. It is an explicit product owner, not a shortcut around Card, Relic, Potion,
Power, Orb, Enchantment, Monster, Affliction, or Modifier ownership.

## DESIGN and SPEC vocabulary

Settle and write:

- scope: run or combat, with the concrete lifecycle reason;
- trigger or queried hook, subject/target, guard, order, result/edit, and neutral behavior;
- state owner: the current `RunState`, `CombatState`, Player, or another concrete scoped object;
- initialization, reset, save/load if required, cleanup, and no-effect boundary;
- exact player-facing text/presentation and its real consumer when the rule is visible; and
- the nearest real `RunStart`, `MapNode`, or `CombatPlayer` SelfTest, including a second run/combat
  that proves reset and no leakage.

Do not store mutable run/combat state on the canonical singleton instance. Use scoped attached or
saved state from `reference/lifecycle-state-rng.md`. A rule that needs both run-only and
combat-only dispatchers is two explicit owners or a redesigned truthful scope, never one singleton
subscribed to both streams.

## Authoring route

- Read `recipes/global-effect.md` for `HookedSingletonModel`, `.Singleton<T>()`, scope selection,
  model access, and state ownership.
- Read `reference/model-hook-participation.md` for raw scalar/decision/collection hook participation.
  A Run
  singleton declares `surface: global-effect-run`; a Combat singleton declares
  `surface: global-effect-combat`. The thin preflight rejects a hook whose dispatcher cannot reach
  that selected stream.
- Read `reference/lifecycle-state-rng.md` for state, events, RNG, save/load, and cleanup;
  `reference/shared-effect-hooks.md` for selected dedicated services; and
  `reference/rest-site-options.md` for an independent Rest Site action.

Do not use raw `ModHelper.SubscribeFor*Hooks`, a process-wide service, or static mutable state when
the maintained singleton route expresses the same ownership.

## Proof matrix

Drive the nearest real host:

1. assert exactly one registered singleton identity and the selected stream;
2. trigger the selected hook/event in scope and assert exact post-state/order;
3. drive a neutral subject/event in the same scope and assert it is unchanged;
4. drive the other stream and assert the effect is absent;
5. cross combat/run teardown, then enter a fresh scope and assert state reset and no duplicate
   callbacks; and
6. for saved run state, perform the exact save/fill round trip without confusing persistence with
   the singleton's canonical identity.

Compile and catalog reachability are not game observation. Each selected global rule remains
game-unobserved until this exact host sequence runs.
