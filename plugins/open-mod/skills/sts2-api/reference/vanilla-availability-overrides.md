# Existing vanilla availability overrides

Use this reference after `vanilla-overrides.md` resolves an exact vanilla target. M6.7.4
is pinned to STS2 `0.107.1` and RitsuLib `0.5.4`. It changes fresh unlock filtering or
Card/Relic/Potion pool membership while preserving the existing model type, `ModelId`,
save identity, and already-created instances.

The checked catalog promotes package `m6.7.4-availability`. Every operation is
`mode: availability` and `multiplayer: singleplayer`. The generated Mod must install all
registrations and fixed patches before `ModelDb` pool caches are read. Prompts select only
the semantic routes below; they never supply a method name, Harmony body, reflection,
Publicizer, or IL.

## Promoted routes

| Route id | Class | Targets | Operation |
|---|---|---|---|
| `availability.epoch.require` | public | Card, Character, ordinary Event, and shared `EVENT.DARV` | require one of the 57 pinned vanilla epochs |
| `availability.relic.epoch-gate` | adapter | Relic | require a pinned epoch or permanently disable fresh pool results |
| `availability.potion.epoch-gate` | adapter | Potion | require a pinned epoch or permanently disable fresh pool results |
| `availability.card.pool-add` | public | Card | add the vanilla type to one additional non-debug Card pool |
| `availability.relic.pool-add` | public | Relic | add the vanilla type to one additional non-debug Relic pool |
| `availability.potion.pool-add` | public | Potion | add the vanilla type to one additional non-debug Potion pool |
| `availability.card.pool-membership` | adapter | Card | remove from one current pool, or move between two pools |
| `availability.relic.pool-membership` | adapter | Relic | remove from one current pool, or move between two pools |
| `availability.potion.pool-membership` | adapter | Potion | remove from one current pool, or move between two pools |

Act-owned Ancients are not filtered by RitsuLib's shared-Ancient host, so only shared Darv
uses the public Ancient gate. Ordinary Event filtering preserves the original generated
event set when filtering would leave an act with no event; do not claim that one gated
Event can make an act's event pool empty. Permanent disable is promoted only for Relic and
Potion in this Package. Card/Character/Event permanent-disable hosts need a separately
reviewed route rather than an invented epoch id.

No global acquisition-weight API exists. Pool membership changes eligibility, not reward
weight. Weighting remains unsupported until each concrete reward/source algorithm has its
own grounded route.

## Epoch manifest

The public route uses category-specific surface `<category>.epoch_gate`, a null
fingerprint, and state `require_epoch`:

```json
{
  "order": 0,
  "operation_id": "strike.require-ironclad-2",
  "target_model_id": "CARD.STRIKE_IRONCLAD",
  "mode": "availability",
  "surface": "card.epoch_gate",
  "route": {
    "class": "public",
    "id": "availability.epoch.require",
    "fingerprint": null
  },
  "expected_baseline": {
    "category": "CARD",
    "type": "MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad",
    "content_kind": "card"
  },
  "semantics": {
    "state": "require_epoch",
    "epoch_id": "IRONCLAD2_EPOCH",
    "multiplayer": "singleplayer"
  }
}
```

`epoch_id` must be one of the 57 exact values in `vanilla_overrides.py`'s
`VANILLA_EPOCH_IDS`. Do not accept a display title, type name, Mod epoch, or arbitrary
sentinel. The public lowering is one registration before RitsuLib freezes unlock rules:

```csharp
var unlocks = RitsuLibFramework.GetUnlockRegistry(MainFile.ModId);
unlocks.RequireEpoch(typeof(StrikeIronclad), "IRONCLAD2_EPOCH");
```

`ModUnlockRegistry.RequireEpoch(Type, string)` keys the requirement by `ModelId` and does
not require the target type to be Mod-owned. This is why it can re-gate a vanilla model.
Do not call `SetEpochRequirementsIgnoredForMod`; vanilla types have no generated-Mod owner
to which that bypass should apply.

Do not substitute the public `RequireAllCardsInPool`, `RequireAllRelicsInPool`, or
`RequireAllPotionsInPool` content-pack helpers. Their pinned `0.5.4` implementation reads
`ModContentRegistry.GetRegisteredModelsInPool(context.ModId, poolType)`, so it intentionally
sees only types registered to the current Mod. Making a vanilla type visible there would
require the forbidden ownership-changing content registration. Whole-vanilla-pool gating
therefore lowers to validated per-model `RequireEpoch` rules (plus the fixed Relic/Potion
filters below), never to the Mod-owned whole-pool helpers.

Relic and Potion use the same semantic object, but their route class is `adapter`. State
`require_epoch` carries a pinned `epoch_id`; state `disabled` requires `epoch_id: null`.
The primary route fingerprint and all six sorted character/shared override dependencies
must match the catalog. For example, a Relic route includes:

```json
{
  "class": "adapter",
  "id": "availability.relic.epoch-gate",
  "fingerprint": "dca9123b8b3be8c27ce197513801232e0a640fa673f4ee314dbdeb3c39619ba1",
  "dependencies": [
    {"id": "availability.relic.epoch-gate.defect", "fingerprint": "b01ea54ca8727c2fe76cccd5f7ab6787bc8d029ba491443adfb96b0aff3ddc98"},
    {"id": "availability.relic.epoch-gate.ironclad", "fingerprint": "a4e14f2271c3df24593bca6118137ceaaceb24dae34d1e2a0b71f895155c0b11"},
    {"id": "availability.relic.epoch-gate.necrobinder", "fingerprint": "8b8c7559b12baadb0f5248c0649932e7081c39ce81ab605fff8536795054fce9"},
    {"id": "availability.relic.epoch-gate.regent", "fingerprint": "5012519dcf514196cecd9565853ca78649d17fb6e02f2f56868fdef56b4d90cf"},
    {"id": "availability.relic.epoch-gate.shared", "fingerprint": "37e2b57af7e86019b5af9923b946411fd0fa5b33d148d6ac9635611909358058"},
    {"id": "availability.relic.epoch-gate.silent", "fingerprint": "60108f1b02458188337f1b5bb937b7afce9d535f923afe87553380e436eecef1"}
  ]
}
```

The Potion primary and dependency ids are:

```text
availability.potion.epoch-gate
availability.potion.epoch-gate.defect
availability.potion.epoch-gate.ironclad
availability.potion.epoch-gate.necrobinder
availability.potion.epoch-gate.regent
availability.potion.epoch-gate.shared
availability.potion.epoch-gate.silent
```

The fixed Adapter patches `GetUnlockedRelics(UnlockState)` or
`GetUnlockedPotions(UnlockState)` on the base pool plus Defect, Ironclad, Necrobinder,
Regent, Shared, and Silent overrides. Consolidate all selected targets of one category in
one immutable rule table. For `require_epoch`, also call public `RequireEpoch` and keep a
copy of the exact epoch id for the override filters. For `disabled`, filter that exact
model unconditionally. Every other model passes through unchanged.

```csharp
internal sealed class VanillaRelicEpochGatePatch : IPatchMethod
{
    public static string PatchId => "openmod_m674_relic_epoch_gate";
    public static string Description => "Apply checked vanilla Relic epoch gates";
    public static ModPatchTarget[] GetTargets() =>
    [
        new(typeof(RelicPoolModel), nameof(RelicPoolModel.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(DefectRelicPool), nameof(DefectRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(IroncladRelicPool), nameof(IroncladRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(NecrobinderRelicPool), nameof(NecrobinderRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(RegentRelicPool), nameof(RegentRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(SharedRelicPool), nameof(SharedRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(SilentRelicPool), nameof(SilentRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
    ];

    public static void Postfix(
        UnlockState unlockState,
        ref IEnumerable<RelicModel> __result) =>
        __result = __result.Where(model => AvailabilityRules.Allows(model.Id, unlockState));
}
```

`AvailabilityRules.Allows` is generated only from the validated semantic table. It reads
`unlockState.ToSerializable().UnlockedEpochs`, returns false for a selected disabled id,
tests the selected exact epoch for a selected gated id, and returns true for every
unselected id. The Potion patch is the same fixed shape with the seven cataloged Potion
targets. Install selected patch classes once through `RitsuLibFramework.CreatePatcher`,
and fail Mod load when `PatchAll()` fails. Do not add another host method from prompt text.

## Pool manifest

Pool operations use `<category>.pool_membership`. `expected_baseline.sources` copies the
complete original membership list from the catalog. `existing_instances` is always
`preserve`; the route changes future pool enumeration and never removes a Card from a
deck, a Relic from inventory, or a Potion from a belt/save.

Public add records only a destination:

```json
{
  "order": 0,
  "operation_id": "strike.add-silent-pool",
  "target_model_id": "CARD.STRIKE_IRONCLAD",
  "mode": "availability",
  "surface": "card.pool_membership",
  "route": {
    "class": "public",
    "id": "availability.card.pool-add",
    "fingerprint": null
  },
  "expected_baseline": {
    "category": "CARD",
    "type": "MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad",
    "sources": {"card_pools": ["CARD_POOL.IRONCLAD_CARD_POOL"]}
  },
  "semantics": {
    "action": "add",
    "destination_pool_model_id": "CARD_POOL.SILENT_CARD_POOL",
    "expected_primary_pool_model_id": "CARD_POOL.IRONCLAD_CARD_POOL",
    "existing_instances": "preserve",
    "multiplayer": "singleplayer"
  }
}
```

Lower it through the public game API before pool caches are populated:

```csharp
ModHelper.AddModelToPool(typeof(StrikeIronclad), typeof(SilentCardPool));
```

This public call adds an existing type to the selected pool without declaring ownership.
Never use `ModContentRegistry.RegisterCard`, `RegisterRelic`, or `RegisterPotion` for a
vanilla type: those registries prime Mod ownership and would corrupt the vanilla identity
contract.

Adapter `remove` has `source_pool_model_id`; `move` has both source and destination. Move
lowers as the public destination add plus the fixed source filter. The route fingerprints
are:

```text
availability.card.pool-membership   34a9ad59b7a7c2d05b312f2ba515969d3e78e09f903b0180025afeecb6a652d9
availability.relic.pool-membership  3d6c4629d05021df4baeb0aed24b59c8af2d25bd8170194f28eac9fad9bd170b
availability.potion.pool-membership c1ea2c083548614d1ec4a46c49c67a8db9720361d3826a67c8166a4b26cc967b
```

Each fixed patch targets only `CardPoolModel.AllCards`, `RelicPoolModel.AllRelics`, or
`PotionPoolModel.AllPotions` and filters a validated set of exact `(pool ModelId, content
ModelId)` pairs. It never edits private cache fields and never removes another Mod's model.
Install it before any `All*` or `All*Ids` cache read.

## Ordered membership and primary pool

The validator starts with the catalog's membership and simulates every same-target
operation in manifest order. It rejects:

- adding an already-present destination or removing/moving a missing source;
- a Card/Relic/Potion paired with the wrong pool category;
- any debug/mock target or pool;
- a move whose destination is already present;
- removing the final membership; and
- an `expected_primary_pool_model_id` that differs from pinned `ModelDb` order.

The final-membership guard is required because existing vanilla instances may resolve
their `.Pool`; hiding the model from every pool can turn a valid save/deck into a lookup
failure. `expected_primary_pool_model_id` makes the author acknowledge when adding an
earlier pool changes type text, frame/energy identity, or another primary-pool consumer.
Do not infer primary from manifest order.

## Verification boundary

During the M6.7 batch window, run focused manifest/catalog/document-route tests only. The
representative C# compile, cache timing, unlock UI, fresh rewards, seeded order/RNG,
duplicate absence, existing-save survival, and singleplayer real-host behavior remain
unrun until consolidated M6.7 closure. Pool membership does not prove source weighting,
and an automated manifest pass is not headed availability proof.
