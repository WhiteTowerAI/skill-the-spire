# Recipe: Global Effect

Use only for a rule with no truthful obtainable or selectable model owner. The public route is one
registered `HookedSingletonModel` whose constructor permanently selects exactly one stream: Run or
Combat. It is an explicit product owner, never a shortcut around Card, Relic, Potion, Power, Orb,
Enchantment, Monster, Affliction, or Modifier ownership. Never use raw
`ModHelper.SubscribeFor*Hooks`, a process-wide service, or static mutable state when this route
expresses the same ownership.

## DESIGN and SPEC vocabulary

Settle and write:

- scope: run or combat, with the concrete lifecycle reason;
- the trigger or queried hook, subject/target, guard, order, result/edit, and neutral behavior;
- the state owner: the current `RunState`, `CombatState`, Player, or another concrete scoped object;
- initialization, reset, save/load if required, cleanup, and the no-effect boundary;
- exact player-facing text and presentation and its real consumer when the rule is visible (in the
  `reference/vanilla-text-style.md` row of that consumer: Relic, Power, Modifier, or Hover Tip);
  and
- the nearest real `RunStart`, `MapNode`, or `CombatPlayer` SelfTest, including a second
  run/combat that proves reset and no leakage.

A rule that needs both run-only and combat-only dispatchers is two explicit owners or a redesigned
truthful scope, never one singleton subscribed to both streams.

## Registration and scope

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Singleton<GlobalEffects.<EffectName>>()
    .Apply();
```

```csharp
using STS2RitsuLib.Models;

namespace <ModName>.GlobalEffects;

public sealed class <EffectName> : HookedSingletonModel
{
    public <EffectName>() : base(HookType.<Run-or-Combat>)
    {
    }
}
```

`HookType.Run` enters `RunState` subscription callbacks; `HookType.Combat` enters `CombatState`
callbacks and reports `ShouldReceiveCombatHooks = true`. Never choose `None` for an effect,
register raw `ModHelper` subscribers, or subscribe one singleton to two streams.

For a raw hook, follow `reference/model-hook-participation.md`. A Run singleton is surface
`global-effect-run` and a Combat singleton `global-effect-combat` in the catalog's
`authorable_surfaces`, derived from each hook's actual dispatcher. A stream that cannot receive
the hook is a compile-clean silent failure; Build reads the singleton's `HookType` and rejects it.

## The effect sequence

Select one real async hook on the chosen dispatcher before authoring a sequence. That callback,
not the canonical singleton, supplies every Player, Creature, target, Card, `CardPlay`, and
`PlayerChoiceContext` consumed through `reference/effect-primitives.md`. A queried
scalar/decision/collection hook returns its neutral or edited value and never enqueues side
effects. If the callback lacks a required input, report the exact hook/input mismatch; never fetch a
current global Player, retain a stale scope object, or broaden the singleton to the other stream.

## State ownership

The registered singleton is a canonical identity and callback entry point; never mutate its fields
as run/combat state. Attach transient state to `CurrentRunState`, `CurrentCombatState`, the
subject Player, or another concrete scoped object with `AttachedState`; use `RunSavedData` only
when the semantic value must survive save/load. State access fails neutral when the current scope
is unavailable and never leaks into a second run or combat. Read `reference/lifecycle-state-rng.md`
for state, events, RNG, save/load, and cleanup; `reference/shared-effect-hooks.md` for dedicated
services; and `reference/rest-site-options.md` for a standalone Rest Site action.

## Proof matrix

Drive the nearest real host:

1. assert exactly one registered singleton identity and the selected stream;
2. trigger the selected hook or event in scope and assert exact post-state and order;
3. drive a neutral subject or event in the same scope and assert it unchanged;
4. drive the other stream and assert the effect is absent;
5. cross combat/run teardown, enter a fresh scope, and assert state reset and no duplicate
   callbacks; and
6. for saved run state, perform the exact save/fill round trip without confusing persistence with
   the singleton's canonical identity.

Any selected presentation gets its own real consumer or headed check. A model lookup, a direct
method call, compile, or catalog reachability is not game observation.
