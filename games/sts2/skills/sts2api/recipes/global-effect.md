# Recipe: Global Effect

Use only when no obtainable/selectable model truthfully owns the rule. Register one
`HookedSingletonModel` and choose one immutable hook stream in its constructor.

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

`HookType.Run` enters `RunState` subscription callbacks; `HookType.Combat` enters
`CombatState` callbacks and reports `ShouldReceiveCombatHooks = true`. Do not choose `None` for an
effect, register raw `ModHelper` subscribers, or subscribe the same singleton to two streams.

For a raw hook, read `reference/model-hook-participation.md` and declare exactly:

```markdown
- Hook: <capability> | surface: global-effect-run | shape: <shape> | route: reference/model-hook-participation.md
```

or `surface: global-effect-combat`. The catalog derives each surface from the hook's actual
dispatcher iterator. Choosing a stream that cannot receive that hook is a compile-clean silent
failure and is rejected by `capability_preflight.py`.

## State ownership

The registered singleton is a canonical identity and callback entry point. Do not mutate its
fields as run/combat state. Attach transient state to `CurrentRunState`, `CurrentCombatState`, the
subject Player, or another concrete scoped object with `AttachedState`; use `RunSavedData` only
when the selected semantic value must survive save/load. State access must fail neutral when the
current scope is unavailable and must not leak to a second run/combat.

Read `reference/lifecycle-state-rng.md` for the selected state, event, RNG, save/load, and cleanup
contract; `reference/shared-effect-hooks.md` for dedicated services; and
`reference/rest-site-options.md` for a standalone Rest Site action.

## Proof

Drive the real dispatcher, assert the modified result and neutral case, assert the opposite scope
does not fire, then cross teardown and enter a fresh scope. A model lookup or direct method call
does not prove hook participation. Any selected presentation gets its own real consumer/headed
check.
