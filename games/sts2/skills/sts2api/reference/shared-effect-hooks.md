# Shared effect hooks - attack hits, healing, resources, and hand size

Use this route for effect APIs that are not raw `AbstractModel` value/query hooks. A Card, Relic,
Potion, Power, Orb, Enchantment, Affliction, or Monster effect implements the relevant interface
on that model or a typed `ModelCapability`. A process-wide registration is reserved for the
accepted `Global Effect` surface when no truthful obtainable model owns the rule.

## SPEC contract

```markdown
- **shared effect**:
  - owner: <exact model/capability or Global Effect>
  - operation: per-hit attack | healing amount | after Energy gain | after Stars gain |
    maximum hand size
  - trigger/phase: <exact before/after or early/additive/multiplicative/late pass>
  - subject/source guard: <complete identity and condition>
  - value/action: <exact delta, multiplier, replacement, or awaited sequence>
  - ordering: <pass and relative owner/capability order>
  - neutral result: <unchanged value or no command>
  - state/text: <named state/DynamicVars/localized explanation or none>
```

Every modifier must return the neutral value outside its guard. Do not add a raw Hook declaration
for this route; `capability_preflight.py` owns only the cataloged model-hook dispatcher facts.

## Per-hit attack

Implement `IAttackHitHookListener`. `BeforeAttackHit(AttackHitContext)` runs immediately before
one hit's damage command and may await commands or change that hit's `Damage`, `DamageProps`,
`Dealer`, `CardSource`, and `Targets`. `HitIndex` is zero-based; `HitNumber` is one-based;
`TotalHitCount` is the attack loop count. `AfterAttackHit` runs after damage and exposes the
resolved `Results`.

Dispatch includes combat hook listeners plus the attack's model source and Card source. Put a
Card-owned per-hit effect on that Card/capability so its source identity follows the attack. A
before-hit target replacement affects only the current hit. Never mutate an input and then assert
only that the callback fired; assert the actual result per target and hit.

There is no public process-listener registration for this hook. A global per-hit rule must have a
registered Run/Combat `HookedSingletonModel` participating in the normal listener stream.

## Healing amount

Implement `IHealHookListener`. RitsuLib calculates:

```text
original amount
  + sum of ModifyHealAdditive(context, original amount)
  * each ModifyHealMultiplicative(context, post-additive amount)
  -> each ModifyHealAmount(context, current amount)
  -> clamp to at least zero
```

The context includes the receiving Creature, original amount, animation request, optional combat,
optional run, and current missing HP. Additive listeners return only their delta; multiplicative
listeners return `1` when neutral; late listeners return the current amount unchanged when neutral.
Do not clamp early unless SPEC explicitly needs an intermediate bound.

Model/capability listeners are preferred. Only a true Global Effect may use
`RegisterHealHookListener`. Assert both the computed heal request and the real HP delta because
missing HP can cap the latter.

## Built-in Energy and Stars gained

Implement `IPlayerResourceHookListener`. `AfterPlayerEnergyGained` and
`AfterPlayerStarsGained` run after `PlayerCmd.GainEnergy`/`GainStars` only when the resulting delta
is positive. `PlayerResourceGainContext` provides combat, player, `Energy`/`Stars`, positive
`Amount`, `OldAmount`, and `NewAmount`.

These callbacks do not cover spend, reset, direct field mutation, secondary resources, or a zero/
negative result. Use the exact lifecycle event only for observation of those other built-in
resource operations, and use `reference/character-resource.md` for custom secondary resources.
An owner-bound listener must guard the player identity; co-op support is not inferred or claimed.

## Maximum hand size

Implement `IMaxHandSizeModifier`. The calculation starts from the host base, applies every
`ModifyMaxHandSize` result in listener order, then every `ModifyMaxHandSizeLate` result in the same
order, and finally clamps to at least zero. Return `currentMaxHandSize` outside the owner/condition
guard. Query the effective value through `RitsuLibFramework.GetMaxHandSize(player)`; do not cache
it when conditions can change.

There is no separate global registration API. A truly global rule uses a registered Run/Combat
singleton owner. The maximum only changes capacity; it does not itself draw, discard, or rearrange
Cards, so SPEC must separately state any desired action.

## Ownership and composition

Use `model-capabilities.md` for separable, stackable, temporary, or saved effects. Owner hook order
determines the model/capability listener sequence where the dispatcher supplies those listeners;
the pass order above remains fixed. Preserve every component's independent guard and text when
multiple effects compose. A Power/Relic/Card effect must not become process-wide just because it
also affects attacks, healing, resources, or hand size.

## SelfTest contract

- per-hit: drive a real multi-hit attack; assert each pre-hit input, target/result, hit count/order,
  after-hit results, and an unrelated attack left unchanged;
- healing: wound the real target, assert additive then multiplicative then late composition,
  zero-floor/missing-HP edges, and an unrelated creature unchanged;
- Energy/Stars: drive the real gain command, assert old/new/delta and dependent awaited effect;
  also drive spend/reset or zero gain and assert the callback-owned effect did not run; and
- hand size: assert early/late order, final zero clamp, real draw/capacity consequence, condition
  deactivation, and an unrelated player/owner-neutral path.

Log lines that say a listener fired are diagnostics only. The structured proof follows exact
post-state assertions and command-queue completion.
