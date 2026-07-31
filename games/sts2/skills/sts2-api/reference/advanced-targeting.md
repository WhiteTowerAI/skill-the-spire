# Reference: advanced Card and Potion creature targeting

This page owns the bounded custom-target contract for STS2 `0.107.1` with RitsuLib
`0.4.67`. Use it only when a Card or Potion needs a creature filter beyond `Self`,
`AnyEnemy`, or `AllEnemies`. The target remains a live combat `Creature`; selecting Cards,
corpses, map nodes, or arbitrary objects is unsupported.

## Supported matrix

| Consumer | Mode | Current status | Resolution |
|---|---|---|---|
| Card | one | supported by this recipe | selected creature, revalidated before payment |
| Card | many | supported by this recipe | one play with `null`; call `GetTargets()` in `OnPlay` |
| Potion | one | supported by this recipe | selected creature, revalidated before removal |
| Potion | many | supported API with a known lifecycle limitation | stop authoring |

`potion + many` is not a generated fallback. On the pinned host, a queued multi-target
Potion has a valid `null` target and `UsePotionAction` does not recheck
`PassesCustomUsabilityCheck`. If all candidates disappear after enqueue, `OnUseWrapper`
removes the Potion before its effect sees an empty `GetTargets()` result. Do not promise
zero-target retention, restore a consumed Potion after the fact, or emit Harmony,
reflection, IL, or Publicizer code. Report the known limitation and offer a
single-target Potion or multi-target Card instead.

## Semantic input

An advanced target declaration contains:

- `consumer`: `card` or `potion`;
- `mode`: `one` or `many`;
- `target id`: one stable Mod-local stem;
- `candidate conditions`: side, alive state, intent, Block, or current/maximum HP;
- `acting-player conditions`: only state readable from the acting `Player`;
- `source conditions`: `none` unless a single-target rule genuinely depends on the
  source Card/Potion;
- `zero-target behavior`: reject/cancel without Card payment, Potion consumption, or a
  stranded Card;
- `resolution`: apply the declared effect exactly once to every resolved creature.

Prefer named deterministic families such as attacking enemies, blocking/nonblocking
enemies, tied highest/lowest-HP enemies, full-life enemies, anyone, or everyone. Predicates
return a Boolean only: no Cmds, mutation, RNG, logging, async work, or retained creature
references. Include `IsAlive` explicitly and express enemy/ally relative to the acting
player when that distinction matters.

## Registration timing

Register every target type exactly once during the generated Mod initializer. Target
registration is immediate and separate from the deferred content-pack builder. Put one
call before the content pack in `MainFile.Content.cs`:

```csharp
public static partial class MainFile
{
    static partial void RegisterContent()
    {
        ModTargetTypes.RegisterTargetTypes();

        RitsuLibFramework.CreateContentPack(ModId)
            .Card<ColorlessCardPool, Cards.<CardName>>()
            .Apply();
    }
}
```

The returned dynamic enum value is deterministic for the same Mod id and local stem; its
qualified identity is `MODID_TARGETTYPE_STEM`. Do not use a process-order integer, parse a
made-up enum name, or register the same identity as both `one` and `many`.

## Public RitsuLib routes

Use the facade overload matching the semantic inputs:

```csharp
RitsuLibFramework.RegisterSingleTargetType(
    ModId, "wounded_enemy",
    static candidate => candidate.IsAlive && candidate.IsEnemy &&
                        candidate.CurrentHp < candidate.MaxHp);

RitsuLibFramework.RegisterSingleTargetType(
    ModId, "weaker_enemy",
    static (candidate, player) => candidate.IsAlive &&
        candidate.Side != player.Creature.Side &&
        candidate.CurrentHp < player.Creature.CurrentHp);

RitsuLibFramework.RegisterSingleTargetTypeWithContext(
    ModId, "upgraded_source_enemy",
    static context => context.TargetCreature.IsAlive &&
        context.TargetCreature.Side != context.Player.Creature.Side &&
        context.Card is { CurrentUpgradeLevel: > 0 });

RitsuLibFramework.RegisterMultiTargetType(
    ModId, "blocking_enemies",
    static (candidate, player) => candidate.IsAlive &&
        candidate.Side != player.Creature.Side && candidate.Block > 0);
```

`CustomTargetContext` exposes `TargetCreature`, acting `Player`, source `Card`, and source
`Potion`. Use `RegisterSingleTargetTypeWithContext` only when the source fields are part of
the accepted SPEC. There is no source-aware multi-target registration.

Keep the returned values in one generated type:

```csharp
using MegaCrit.Sts2.Core.Entities.Cards;
using STS2RitsuLib;

namespace <ModName>;

internal static class ModTargetTypes
{
    public static TargetType BlockingEnemy { get; private set; }
    public static TargetType BlockingEnemies { get; private set; }

    public static void RegisterTargetTypes()
    {
        BlockingEnemy = RitsuLibFramework.RegisterSingleTargetType(
            MainFile.ModId,
            "blocking_enemy",
            static (candidate, player) => candidate.IsAlive &&
                candidate.Side != player.Creature.Side && candidate.Block > 0);

        BlockingEnemies = RitsuLibFramework.RegisterMultiTargetType(
            MainFile.ModId,
            "blocking_enemies",
            static (candidate, player) => candidate.IsAlive &&
                candidate.Side != player.Creature.Side && candidate.Block > 0);
    }
}
```

## Card consumers

Pass the registered value to the normal `ModCardTemplate` constructor. A single-target
Card keeps `cardPlay.Target`, while the RitsuLib patch routes mouse and controller
selection through the same registered predicate. The selected creature is revalidated
before Energy or Stars are spent; an invalid target cancels the `PlayCardAction`.

For `mode: one`, keep the normal selected-target effect shape:

```csharp
public <CardName>()
    : base(1, CardType.Attack, CardRarity.Common, ModTargetTypes.BlockingEnemy)
{
}

protected override async Task OnPlay(
    PlayerChoiceContext choiceContext, CardPlay cardPlay)
{
    Creature? target = cardPlay.Target;
    ArgumentNullException.ThrowIfNull(target);
    await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
        .FromCard(this)
        .Targeting(target)
        .Execute(choiceContext);
}
```

For `mode: many`, the Card executes once with a null selected target. Gate the zero-target
case through `IsPlayable`, which `PlayCardAction` rechecks before payment, then resolve the
live list inside `OnPlay` through `CardModelTargetingExtensions.GetTargets`:

```csharp
using STS2RitsuLib.Combat.CardTargeting;

protected override bool IsPlayable => base.IsPlayable && this.GetTargets().Count > 0;

protected override async Task OnPlay(
    PlayerChoiceContext choiceContext, CardPlay cardPlay)
{
    foreach (Creature target in this.GetTargets())
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .Targeting(target)
            .Execute(choiceContext);
    }
}
```

Do not cache the selection-time list. Every returned creature is processed once, and the
Card then follows its normal result pile and play hooks.

## Potion consumers

Only `mode: one` is supported. Pass the registered value from `TargetType`, retain the
normal `AssertValidForTargetedPotion(target)` guard, and execute the ordinary Potion
effect. RitsuLib routes mouse/controller selection and `PotionModel.IsValidTarget` through
the predicate. The selected creature is revalidated before the Potion is removed by
`OnUseWrapper`; an invalid target cancels the `UsePotionAction`.

```csharp
public override TargetType TargetType => ModTargetTypes.BlockingEnemy;

protected override async Task OnUse(
    PlayerChoiceContext choiceContext, Creature? target)
{
    AssertValidForTargetedPotion(target);
    await CreatureCmd.Damage(
        choiceContext, target, 4m, ValueProp.Unpowered,
        Owner.Creature, null);
}
```

`PotionModelTargetingExtensions.GetTargets(potion, selectedTarget)` is available when one
effect implementation intentionally shares a target-resolution helper with another
consumer. It is not permission to author the limited `potion + many` combination.

## Verification contract

Use one disposable `CombatPlayer` proof with at least two enemies. A complete proof for
the current supported matrix uses a source-aware single Card, a single Potion, and a
player-aware multi Card. The automated state proof records exact target creature IDs,
before/after values, Card result pile, Card Energy/Stars, and Potion belt membership.

Cover these states without inferring one route from another:

1. zero, one, and multiple legal candidates;
2. one invalid and one valid candidate;
3. selected target becoming invalid before queued single-target execution;
4. a multi Card losing all candidates before execution;
5. normal cancellation, unchanged payment/Potion belt, and normal Card result pile;
6. exact affected creature IDs and one state delta per returned target.

The headed reviewer separately checks real mouse and controller selection, normal cancel,
invalid-creature rejection, single-target highlight, multi-target reticles, and absence of
stale reticles after resolution. Build output, predicates invoked in isolation, and
model-only target lists do not prove those UI claims.
