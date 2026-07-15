# Capability kernel - typed state, hooks, UI hosts, and versioned patches

Status: **scenario-verified for one B-risk postfix on STS2 0.107.1** by
`CanaryPatchKernel` (2026-07-15). This page is a capability-module contract, not a
standalone content recipe. It does not make character resources, payment rules, custom
zones, dynamic cards, vanilla editing, Publicizer access, or transpilers user-facing.

## Route here only after the public/BaseLib check

Use this boundary only when all of the following are true:

1. The semantic SPEC names the state owner, lifetime/reset/save behavior, host event,
   UI meaning, and independently observable consequence.
2. Public STS2 commands/hooks and BaseLib cannot expose the required host event.
3. The selected adapter has an exact target, version/fingerprint, risk band, conflict
   boundary, and a hosted Scenario proof in this pack.

Otherwise use the public/BaseLib path or report a pack gap. Never generate a new patch
target from intuition. A green build or a `patch applied` line is not behavior proof.

## Ownership boundaries

```text
generated domain code
  named state/transitions, numbers, UI text, gameplay assertions
        |
selected self-contained capability module
  ScopedState + HookBus + UiHostDescriptor + one PatchDescriptor
        |
Harmony / STS2 exact host seam
```

- **Domain code owns gameplay.** It registers a typed listener and decides what state
  changes and what the UI displays.
- **The capability module owns plumbing.** It scopes state, orders typed listeners,
  mounts/refreshes descriptors, and applies the selected patch once.
- **Harmony owns only the exact bridge.** The postfix converts game arguments into a
  typed context and dispatches it. Do not put character rules in the patch body.
- **No `OpenMod.Runtime` yet.** Emit this module into the generated mod. Promote only
  after two independent generated mods require the same cross-mod patch/registry seam.

Recommended generated layout:

```text
<ModName>Code/
  CapabilityKernel/
    ScopedState.cs
    HookBus.cs
    UiHostDescriptor.cs
    PatchRegistry.cs
    CombatUiKernel.cs       # only when this proven adapter is selected
  Domain/
    <MechanicName>Domain.cs
```

## Required module record

Before authoring, SPEC must carry these fields:

| Field | Requirement |
|---|---|
| semantic host | the real game object/event that owns the state |
| lifetime | `turn`, `combat`, or `run`; exact reset and save behavior |
| public surface | typed context/listener API exposed to domain code |
| patch | risk A-D, exact target, supported game version and fingerprint |
| multiplayer | dispatch/aggregation order and owner/local-player guard |
| UI | host node, visibility predicate, refresh event, no-art fallback |
| conflict | additive/exclusive behavior and fallback on target mismatch |
| Type proof | 0/0 build, load marker, resolved/applied diagnostics |
| Scenario proof | hosted state consequence; never patch-only |

Only B-level structural prefix/postfix is verified here. C-level internal/Publicizer and
D-level transpiler modules need separate fingerprinted canaries before use.

## Semantic state primitive

Scope state to the actual host object. For combat lifetime, a new `CombatState` gets a
new value and the old value becomes collectible with its host. Do not use a process-wide
singleton field and call it combat state.

```csharp
using System.Runtime.CompilerServices;

internal enum StateLifetime { Combat }

internal sealed class ScopedState<THost, TState>
    where THost : class
    where TState : class
{
    private readonly ConditionalWeakTable<THost, TState> _values = new();
    private readonly Func<TState> _factory;

    public ScopedState(StateLifetime lifetime, Func<TState> factory)
    {
        Lifetime = lifetime;
        _factory = factory;
    }

    public StateLifetime Lifetime { get; }
    public TState Get(THost host) => _values.GetValue(host, _ => _factory());
    public bool TryGet(THost host, out TState state) =>
        _values.TryGetValue(host, out state!);
}
```

This primitive proves combat ownership only. Run lifetime still needs a supported saved
holder/property and a save round trip; see `stateful-mechanics.md`.

## Typed hook primitive

Listener ids make registration idempotent and ordinal sorting makes dispatch deterministic.
Keep one context type per semantic game event, not one interface per named character.

```csharp
internal sealed class HookBus<TContext>
{
    private readonly SortedDictionary<string, Action<TContext>> _listeners =
        new(StringComparer.Ordinal);

    public int ListenerCount => _listeners.Count;

    public bool Register(string id, Action<TContext> listener)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        ArgumentNullException.ThrowIfNull(listener);
        return _listeners.TryAdd(id, listener);
    }

    public int Dispatch(TContext context)
    {
        foreach (var listener in _listeners.Values.ToArray())
            listener(context);
        return _listeners.Count;
    }
}
```

The patch adapter should catch and log a listener failure so a mod cannot break the base
UI lifecycle silently. The Scenario harness must still fail because its state consequence
will be absent.

## UI-host descriptor

The descriptor owns placement mechanics, visibility, fallback creation, and refresh. The
domain module supplies the label text/metadata or richer control behavior.

```csharp
using Godot;

internal sealed record UiMountResult(Control Node, bool Created);

internal sealed record UiHostDescriptor<TContext>(
    string NodeName,
    Func<TContext, bool> IsVisible,
    Func<TContext, Control> CreateFallback,
    Action<Control, TContext> Refresh)
{
    public UiMountResult? Mount(Node host, TContext context)
    {
        if (!IsVisible(context)) return null;
        var node = host.GetNodeOrNull<Control>(NodeName);
        bool created = node == null;
        if (node == null)
        {
            node = CreateFallback(context);
            node.Name = NodeName;
            host.AddChild(node);
        }
        Refresh(node, context);
        return new UiMountResult(node, created);
    }
}
```

A generic Godot `Label` is the verified no-art fallback. Custom character UI art is not
required for programming proof.

## Versioned patch registry

Each selected patch declares:

```csharp
internal enum PatchRisk { B }

internal sealed record PatchDescriptor(
    string Id,
    PatchRisk Risk,
    string SupportedGameVersion,
    Guid ExpectedTargetModuleVersionId,
    Type TargetModuleType,
    string ExactTarget,
    Func<IReadOnlyList<MethodBase>> ResolveTargets,
    MethodInfo Postfix);
```

Registry behavior is mandatory:

1. Return the stored status on a repeated id; never apply twice.
2. Compare `TargetModuleType.Module.ModuleVersionId` before target resolution.
3. Resolve by exact name and parameter types; require exactly one target.
4. Apply one explicitly supplied prefix/postfix. Do not call assembly-wide `PatchAll`.
5. Inspect `Harmony.GetPatchInfo(target)` and require exactly one patch owned by this
   Harmony id; log foreign patches separately.
6. Record version mismatch, resolver exception, zero/multiple targets, apply exception,
   and owned-count mismatch as `status=FAILED` with a one-line reason.

Required marker vocabulary:

```text
[OPENMOD-PATCH] id=<id> risk=B supportedGame=<version> mvid=<guid> target=<signature> targets=1 status=resolved
[OPENMOD-PATCH] id=<id> ownedPostfixes=1 foreignPostfixes=<n> conflict=<policy> status=applied
[OPENMOD-PATCH] id=<id> status=already-applied ownedPostfixes=1
[OPENMOD-PATCH] id=<id> ... targets=0 ownedPostfixes=0 status=FAILED reason=<reason>
```

Do not treat foreign postfixes as an automatic conflict. The verified combat-UI bridge is
additive and reports `conflict=compatible-postfix-composition`; an exclusive prefix or
return-value rewrite needs its own policy and canary.

## Verified B adapter - combat UI activation

This is the only non-public kernel seam promoted by 6c:

| Contract | Verified value |
|---|---|
| STS2 | stable `0.107.1` |
| target module MVID | `97f10687-c306-4798-ab75-8b9f23f34dfb` |
| exact target | public `NCombatUi.Activate(CombatState)` |
| patch kind | Harmony postfix (risk B) |
| typed context | `CombatUiActivateContext(NCombatUi Ui, CombatState State)` |
| public UI host | `NCombatUi.EnergyCounterContainer` |
| conflict policy | additive postfix composition; log foreign count |
| failure fallback | skip domain UI; keep base combat UI intact; emit `status=FAILED` |

Exact resolver:

```csharp
private static IReadOnlyList<MethodBase> ResolveCombatUiActivate() =>
    typeof(NCombatUi)
        .GetMethods(BindingFlags.Instance | BindingFlags.Public)
        .Where(method => method.Name == nameof(NCombatUi.Activate))
        .Where(method =>
        {
            var parameters = method.GetParameters();
            return parameters.Length == 1 &&
                   parameters[0].ParameterType == typeof(CombatState);
        })
        .Cast<MethodBase>()
        .ToArray();
```

Postfix body:

```csharp
private static void Postfix(NCombatUi __instance, CombatState state)
{
    try
    {
        CombatUiKernel.RaiseActivated(
            new CombatUiActivateContext(__instance, state));
    }
    catch (Exception exception)
    {
        MainFile.Logger.Error(
            $"[OPENMOD-HOOK] hook=CombatUiActivate status=FAILED " +
            $"reason={exception.GetType().Name}:{exception.Message}");
    }
}
```

Initialization order is domain listener registration, patch install, intentional second
install only in the canary's idempotence assertion, load marker, then optional self-test.
A normal generated mod calls `Install` once.

## Domain-module shape

Domain code composes the primitives without moving its rules into the kernel:

```csharp
internal sealed class MyCombatState(int generation)
{
    public int Generation { get; } = generation;
    public int Activations { get; set; }
}

internal static class MyMechanicDomain
{
    private static int _generation;
    private static readonly ScopedState<CombatState, MyCombatState> State =
        new(StateLifetime.Combat, () => new MyCombatState(++_generation));

    public static void Register() =>
        CombatUiKernel.Activated.Register("<ModName>.MyMechanic", OnActivated);

    private static void OnActivated(CombatUiActivateContext context)
    {
        var state = State.Get(context.State);
        state.Activations++;
        // Domain-owned rule and descriptor refresh go here.
    }
}
```

The comment is not permission to invent a resource/payment/zone rule. Route those only
after their 6d contracts and Scenario canaries exist.

## Type and Scenario proof

Tier 1 must prove all of the following in the fresh game log:

- exact load marker and no fresh error block;
- `targets=1 status=resolved` with supported version and MVID;
- `ownedPostfixes=1 status=applied`;
- idempotence in the canary (`already-applied`), with no second owned postfix.

Tier 2 enters two real combats. In combat 1 assert one typed dispatch/listener/state
activation and a real UI node with exact text/metadata. Finish combat through public
combat flow, enter combat 2, then assert a distinct state object/generation with both
combat activation counts still equal to one. Only then emit:

```text
[T2MOD-SELFTEST] <ModName> state proof: patch kernel complete expected=all observed=all
[T2MOD-SELFTEST] <ModName> selftest done
```

Verify with:

```bash
python ${CLAUDE_PLUGIN_ROOT}/tools/launch.py --self-test --mod-name <ModName>
python ${CLAUDE_PLUGIN_ROOT}/tools/grep_log.py --mod-name <ModName> \
  --tier2-pattern "patch kernel complete.*observed=all"
```

`CanaryPatchKernel` built with 0 warnings / 0 errors and passed strict Tier 1 + Tier 2
on 2026-07-15. The live run observed target/owned/idempotent `1/1/1`, three compatible
foreign postfixes, typed dispatch/state/listeners `1/1/1`, the mounted fallback Label,
and distinct combat generations `1/2` with activation counts `1/1`.
