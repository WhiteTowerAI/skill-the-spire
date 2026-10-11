# Model capabilities - attachable model-owned behavior

Status: **authorable with RitsuLib 0.6.7 on STS2 0.107.1**. The public registration,
default-attachment, typed owner/state, collection, clone, and owner-hook routes compile against the
pinned Compat assembly. These generalized shapes remain game-unobserved until their exact real-host
scenario runs.

Use this route when an effect is a separable behavior or state bundle owned by a Card, Relic,
Potion, Power, Orb, Enchantment, Affliction, Monster, or Character. Keep behavior in the model
itself when it is inseparable from that model. Do not register a process-wide listener merely to
avoid expressing the truthful owner. A rule with no obtainable model owner belongs to the
`Global Effect` surface, not to this page.

## SPEC contract

Describe the capability in game terms. Do not put interface names or registry calls in SPEC:

```markdown
- **model capability**:
  - owner: <exact model instance and surface>
  - attachment: default on every <model> | applied by <exact effect>
  - behavior: <ordered triggers, guards, values, targets, and neutral results>
  - stacking: separate instances | merge <rule> | replace | subtract <rule>
  - order: before owner | after owner | relative to <named capability>
  - state: none | <fields, bounds, lifetime, reset, persistence, visibility>
  - removal: never | after one owner-card play | after combat | after <N> owner turns |
    when <condition>
  - presentation: none | <localized text/DynamicVars/tips/overlay/value consumer>
  - cloning/transform: copy | drop | share | Card transform carry-over <condition>
```

The attachment point, stacking result, execution order, state lifetime, and removal boundary are
player-visible semantics. Ask rather than selecting whichever base class is easiest.

## Register and attach

Every `ModelCapability` subclass that can be saved or created by type needs one stable public ID.
Register it during normal content registration with
`RitsuLibFramework.RegisterModelCapability<T>(MainFile.ModId)` or the equivalent content-pack/
`[RegisterModelCapability]` route. Keep the ID stem stable after release.

For a capability present on every matching model, configure it once with
`ConfigureDefaultModelCapabilities<TModel>`. Add registered model-capability types through
`capabilities.Add<T>()`; do not call their constructors inside the default modifier. A custom Card
can instead derive from `CapabilityCardModel` and override `BuildDefaultCapabilities`.

For an effect applied at runtime, use the owner's set:

```csharp
var set = RitsuLibFramework.GetModelCapabilities(owner);
var capability = set.GetOrCreate<MyCapability>();
// or owner.ApplyCapability(incoming, new(AllowMerge: true));
```

Use typed bases whenever one exists:

- `CardCapability` / `CardPlayCapability`;
- `RelicCapability`, `PotionCapability`, `PowerCapability`, `OrbCapability`;
- `EnchantmentCapability`, `AfflictionCapability`, `MonsterCapability`; and
- `CharacterCapability` for character state/display behavior. Character capability does not opt
  into owner hook dispatch by default because Character is not a normal run/combat hook listener.

The typed base rejects a mismatched owner. Never attach one capability instance to two owners.

## State, cloning, and display

`ModelCapability` already supplies an owner-independent `DynamicVars` set, cloning, and JSON state
integration. Read the owner's variables through `Owner`; declare capability-local visible values in
the capability's `CanonicalVars`. Call `Modify(...)`, `MutateState(...)`, `SetState(...)`, or the
capability's protected dirty path whenever an in-place change must reach save/display consumers.

Choose `StatefulModelCapability<TModel,TState>` for a JSON-serializable capability payload. Override
`ReadState` only for an explicit old-schema migration and keep `SchemaVersion` stable/incremented as
the format requires. `OnLoadedFromSave(TModel)` is the first callback after the typed owner is
restored. See `lifecycle-state-rng.md` when state naturally belongs to a run/player/profile rather
than to this model.

Capabilities may also implement the public display contributors appropriate to their owner:

- any model: DynamicVars, Hover Tips, and asset-path contributions;
- Card: title/description fragments, tips, overlays, type text, glow, properties/tags, local
  Energy/Star costs, playability, result pile, and transform carry-over;
- Orb: passive/evoke value labels and ordered hover-description fragments; and
- supported Card/Relic/Power/Potion/Orb right-click behavior through the interaction route.

Preserve each contributor's real merge rule. Card title/description fragments order by declared
order then capability attachment order; tags append and deduplicate; first- or last-non-null
override contracts must not be converted into an additive merge. Presentation still needs its
real Card/Orb/UI consumer and headed review.

## Hook and collection order

Derive from `OwnerHookCapability<T>` to insert a capability into the owner's normal vanilla hook
stream. `OwnerHookOrder < 0` runs before the owner; zero or positive runs after it. Equal values
retain capability-set order. This ordering applies to owner model hooks, not every separate public
service callback; use the ordering stated by that service's reference.

The capability set supports apply/merge, subtractive merge, direct add, indexed or relative
insertion, replace, remove, and typed lookup. Implement `IModelCapabilityMergeHandler` only when
SPEC defines the algebra. A merge may keep the existing instance, replace it, or return `null` to
remove it. A subtractive merge that cannot apply returns no new capability. Do not call a sequence
of collection edits a transaction: `ApplyRange` keeps earlier edits if a later one throws.

Use ordered insertion only when relative behavior is part of SPEC. State what happens when the
anchor is absent (`append`, `prepend`, `skip`, or `throw`) rather than relying on a default.
Unknown saved capability records default to preservation so optional/future data can round-trip;
remove them only for an explicit compatibility decision.

## Bounded lifetime bases

- `CardPlayCapability` receives the owning Card's before/after `OnPlay` point; use
  `card-play-lifecycle.md` for suppression and ordering.
- `OneShotCardPlayCapability` removes itself in `finally` after one matching owner-card play.
- `UntilCombatEndCapability<T>` invokes its optional end callback, then removes itself in
  `finally`.
- `TurnLimitedCapability<T>` saves a nonnegative remaining-turn count, ticks on the selected side
  turn end, then calls its expiry callback and removes itself. Override `ShouldTickTurnLimit` to
  bind the count to the truthful owner side; the default ticks every side and is rarely the desired
  game rule.

Do not use a lifetime base whose automatic cleanup disagrees with SPEC. A removable capability
must leave its owner collection, display, and saved state clean after removal.

## Card transform behavior

Normal owner cloning and Card transformation are different decisions. Implement
`ICardTransformCarryOverCapability` only when the effect survives transformation. Its predicate
sees the original and replacement; its factory must return a distinct capability for the
replacement, normally through the clone handler. The original and replacement callbacks on
`CardCapability` are notifications, not automatic carry-over.

## SelfTest contract

Use the owner's nearest real host. Assert:

- default versus runtime attachment and exact owner identity;
- every behavior delta plus a neutral event outside the guard;
- merge/subtract/replace result and final capability order;
- state bounds, DynamicVar/display refresh, reset/removal, and no second firing after removal;
- mutable clone independence or intentional share/drop behavior;
- save/fill plus schema migration for persisted capability state; and
- for Card transform carry-over, original/replacement identities, selected copy/drop result, and
  exactly one attached result capability.

Build or a collection-only unit test establishes API compatibility, not hosted dispatch,
persistence, UI, or gameplay proof.
