# Lifecycle, state, and deterministic RNG

Use this page when behavior crosses one callback, combat, room, run, save, or profile boundary.
Storage is not a product owner: the model, Card Pile, Runtime UI, or Global Effect that uses the
state remains responsible for its semantics and proof.

## Select the truthful scope

| Meaning | Route | Required boundary |
|---|---|---|
| local field on one model | ordinary bounded field | explicit turn/combat reset |
| runtime state attached to a reference owner | `AttachedState<TKey,TValue>` | dies with the key/process; never claimed saved |
| saved value owned by one serialized model | `ModelCapability` JSON or `ModelSavedData<TModel,T>` | clone policy, write policy, schema/migration, save/fill |
| bounded legacy Card/Relic/Enchantment scalar | `SavedAttachedState<TModel,bool/int/string>` | owner must pass through normal `SavedProperties`; stable Mod-qualified name |
| value owned by the run | `RunSavedData<T>` | early stable slot registration, write policy, real save/load |
| value owned separately by each player | `PlayerRunSavedData<T>` | exact player/net-id identity; one value per player, saved with the run in both modes |
| Mod feature data outside a run | `ModDataStore` Global/Profile/InMemory | explicit save, profile invalidation, migrations as selected |

Do not put model-owned state into run/profile storage just because it is easier to reach. Do not
use static dictionaries for owner state. Run/player slots use only their in-run accessors;
the `Lobby` accessors and `SyncLobbyOnChange` are used only for a lobby option
(`reference/lobby-options.md`).
`ModDataStore` may persist an included feature, but it must not be used to author deferred
Settings or Progression.

## SPEC vocabulary

```markdown
- **state**:
  - owner: <model | combat | run | player | profile | global feature>
  - fields: <typed names, defaults, and bounds>
  - transitions: <trigger, before/after phase, guard, order, mutation>
  - consumers: <behavior and every visible output>
  - lifetime: turn | combat | room | run | profile | process
  - reset/cleanup: <exact boundary and value/action>
  - persistence: runtime-only | model save | run save | profile/global JSON
  - clone: copy | drop | share | not applicable
  - schema/migration: none | <version and ordered migrations>
- **randomness**:
  - scope: supplied host RNG | Mod run stream | Mod per-player stream
  - stream id: <stable semantic name>
  - draw point: <exact lifecycle point and ordered branch>
```

## Typed lifecycle subscriptions

Subscribe with `RitsuLibFramework.SubscribeLifecycle<TEvent>(handler, replayCurrentState)` and
retain/dispose the returned subscription at the owner's cleanup boundary. Use
`SubscribeLifecycleOnce<TEvent>` only for a concrete sealed/struct event that should run at most
once for that subscription. Replay may invoke synchronously before the subscribe call returns;
the overload that passes its own `IDisposable` is the safe route when a replayed callback may
unsubscribe itself.

Select the event whose context actually supplies the value the behavior needs:

- framework/game readiness: initialization, model registry, scene tree, main menu, game ready,
  deferred initialization, profile services;
- profile/save: profile switching/switched/deleting/deleted, run saving/saved, profile-data
  invalidation, and run-saved-data preparing;
- run/world: run starting/started/loaded/ending/ended, room entering/entered/exited, act entering/
  entered, and map generated;
- combat: combat starting/ended/victory, side turn starting/started/ending/ended, player turn,
  creature add/die, attack/block/HP, shuffle/flush, summon, and extra turn;
- Card/resources: playing/played/auto-play, entered/generated/removed, pile movement, draw/discard/
  exhaust, Energy/Stars gain/reset/spend, and Rest Site heal/smith; and
- included rewards/inventory: Gold, Potion, Relic, reward-taking, purchase, and reward-screen
  continuation.

Lifecycle events are observations, not automatically cancellable commands. Use a model hook or
the dedicated service reference when behavior must modify or suppress an operation. Do not use
Progress/Epoch/unlock events, telemetry startup snapshots, update scheduling, lobby/session, or
multiplayer synchronization.

## Persistence routes

`AttachedState` supports get/create, update, lookup without creation, and removal. It follows the
reference key's lifetime and has no serialization. For saved models prefer `ModelCapability` when
state and behavior form one unit. Otherwise register `ModelSavedData<TModel,TPayload>` early,
choose `WhenSet`/`WhenNonDefault`/`AlwaysWhenPresent`, and explicitly choose clone `Copy`, `Drop`,
or `Share`. `Share` means the same live object and is valid only when shared identity is intended.

Register run and per-player slots during Mod initialization through
`GetRunSavedDataStore(ModId)`. Payloads are plain JSON-serializable classes with public
properties. Keep keys stable, mutate through the handle, and use `RunSavedDataPreparingEvent` only
when a value must be finalized immediately before snapshot export. Keep
`SyncLobbyOnChange = false` in this confirmed scope.

Register `ModDataStore` slots inside `BeginModDataRegistration(ModId)`. Select `Global`, `Profile`,
or `InMemory`, keep logical key and file name stable, and call `Save` after mutations unless a
confirmed included owner explicitly owns persistence. A long-lived profile accessor must use
`CreateCache<T>` so profile reload/invalidation replaces stale roots. A breaking JSON shape needs
an ordered public migration and version rule before release. Cloud participation is an explicit
storage choice, never implied by persistence.

## Deterministic RNG

Use the RNG already supplied by the exact host (for example Act/Ancient/reward resolution) when
available. Otherwise use a stable semantic stream:

```csharp
var shared = RitsuLibFramework.GetModRunRng(runState, MainFile.ModId, "reward-roll");
var perPlayer = RitsuLibFramework.GetModPlayerRng(player, MainFile.ModId, "personal-draw");
```

The run stream is shared by the run; the player stream is separated by player. Reuse the same
stream ID only for one intentional draw sequence. Draw at the authoritative resolution point,
iterate candidates in stable order before drawing, and never consume RNG for preview, disabled
choices, or rejected actions. Do not use `System.Random`, wall-clock time, GUIDs, process hash
order, or UI frame timing for gameplay decisions.

## Composition and failure

All failure-prone validation should occur before the first mutation when the operation promises
no partial outcome. Await queued game commands before observing post-state. Lifecycle callbacks
that merely report an already-completed action cannot retroactively roll it back. Always dispose
subscriptions, detach temporary state/capabilities, stop scoped presentation/audio, and clear
visible consumers at the declared boundary.

## SelfTest contract

Drive the exact owner host and assert:

- callback count/order, replay/no-replay behavior, and no callback after disposal;
- state defaults, every transition/consumer, neutral guard, bounds, and exact reset;
- clone copy/drop/share identity where selected;
- real save/fill and reload for model/run state, and profile switch/cache invalidation for profile
  state;
- deterministic repeated results from the same saved seed/state and a distinct per-player stream
  where selected; and
- no RNG draw or state delta on rejected/disabled/preview paths.

Static serialization or direct callback invocation is development evidence only. Save/load,
profile-switch, and lifecycle claims require their actual game host.
