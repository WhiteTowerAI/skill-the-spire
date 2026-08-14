# Author — write the element, localization, and marker

Goal: translate the accepted framework-neutral SPEC through the selected adapter,
fill only the effect logic, add localization, and inject the shared diagnostics.
Registration, model templates, localization-key derivation, and asset profiles come
from the adapter rather than the user-facing SPEC.

Before writing source, validate selected support routes and raw model-hook reachability:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

Emit only current operations written in the human-readable SPEC. Every emitted content
registration, behavior/data operation, selected presentation, and placeholder must follow its
stated recipe/reference. Never emit deferred, out-of-scope, or unresolved-gap intent, and never
add an unrequested convenience feature.

If authoring reveals that the selected route cannot produce the accepted complete operation,
stop before a workaround and follow `repair.md` from the observed failure. A local lowering
omission may be corrected directly; a different visible result returns to DESIGN and SPEC for
acceptance; an absent or broken shared route blocks consumer authoring.

On revision, update only the confirmed delta and its direct consumers: behavior, localization,
Event text, visual prompts/resources, Character identity, generated source, and SelfTest.
Preserve stable runtime/localization identifiers unless the user changes identity. Re-run only
affected PLAN stages and the nearest proportional host/check; do not schedule a full acceptance
unless the user or active project plan explicitly selects it.

Read `semantic-contract.md` first, then read the selected framework reference
(`sts2-api/reference/ritsulib-adapter.md` for the current target). RitsuLib-specific
snippets live in that reference and the surface recipe it routes to; do not copy a
second framework branch into this file.

> **Adapter guard:** the pinned RitsuLib scaffold/build path and its recipes are the only
> active implementation. No historical-framework branch is available.

## 0. Read the quirks and the recipe first

- Read `quirks.md` before writing any C#.
- For `surface: vanilla model override`, read `reference/vanilla-overrides.md`. Read
  `reference/vanilla-visual-overrides.md` for selected visual operations and
  `reference/vanilla-card-overrides.md` for non-asset Card operations, or
  `reference/vanilla-ancient-overrides.md` for an exact existing Ancient's initial options
  and subsequent pages. Read `reference/vanilla-availability-overrides.md` for availability
  and `reference/vanilla-non-card-overrides.md` for exact existing non-Card data/behavior,
  before any new-content recipe. Resolve the exact catalog target,
  lower only promoted public/fixed-Adapter routes, and use `recipes/card.md` solely for
  selected effect commands. Do not register a replacement vanilla model.
  If the SPEC requests vanilla Card base-description replacement, removal, or hiding, stop:
  do not convert it to description fragments or author code until the user explicitly
  accepts before/after composition and the SPEC records `compose`.
- Query the **sts2-api** skill for the recipe matching SPEC's **element**:
  `recipes/relic.md` for a relic, `recipes/potion.md` for a potion, `recipes/card.md`
  for a card. For a **card or power**, also read `reference/mechanics.md` first
  (DynamicVars, SmartFormat descriptions, shared enums). For a Card whose SPEC has
  non-`none` `calculated values` or `variable tooltips`, also read
  `reference/card-computed-values.md`; it owns formula timing, preview/execution parity,
  icon formatters, typed Power semantics, and shared tooltip localization. If a
  Card/relic/potion/power
  display selects bounded vanilla text effects, also read
  `reference/content-text-effects.md` and apply only its per-surface allowlist. If the effect needs a
  buff/debuff no vanilla power covers, read `recipes/power.md` and author the custom
  power as a dependency. If SPEC declares custom keywords, also read
  `recipes/keyword.md`: emit the generated enum field and `card_keywords.json`, attach
  it to each host Card, and implement the named rule separately from its tooltip. If SPEC
  declares a card enchantment, read `recipes/enchantment.md`, author
  `ModEnchantmentTemplate`, register it through `.Enchantment<T>()`, and attach it through
  `CardCmd.Enchant<T>`; never substitute an unrelated run-level Modifier. If SPEC declares
  a combat Card Affliction, read `recipes/affliction.md`, register one
  `ModAfflictionTemplate` through `.Affliction<T>()`, and apply/clear it only through
  `CardCmd.Afflict<T>` / `AfflictAndPreview<T>` / `ClearAffliction`. If SPEC declares a selected
  run Modifier, read `recipes/modifier.md`, register exactly one good/bad polarity and its selected
  sort/exclusivity contract, and keep new-run and load behavior distinct. If SPEC declares a
  Global Effect, read `recipes/global-effect.md`, register `HookedSingletonModel` through
  `.Singleton<T>()`, select exactly Run or Combat, and attach mutable state to the concrete scope.
  If SPEC declares an independent Rest Site action, read `recipes/rest-site.md` plus
  `reference/rest-site-options.md` and select its standalone/Card/Relic/Modifier owner. If SPEC declares
  a complete Act, read `recipes/act.md`, implement every required `ModActTemplate` gameplay
  member, register it through `.Act<T>()`, and select exactly one force/uniform/weighted
  singleplayer entry policy. Registration alone is not reachability. If SPEC declares a new
  Ancient, read `recipes/ancient.md`, implement `ModAncientEventTemplate`, and register it
  exactly once through `.SharedAncient<T>()` or `.ActAncient<TAct,T>()`; do not lower it as an
  ordinary Event or as an existing-Ancient override. If SPEC declares a custom Reward, read
  `recipes/reward.md`, register its Mod-owned dynamic type once, implement `ModCustomReward`, and
  keep payload reconstruction separate from awaited `OnSelect()` effects. If SPEC declares
  a custom orb, read `recipes/orb.md`, author `ModOrbTemplate`, register it through
  `.Orb<T>()`, and make the real host channel it via
  `OrbCmd.Channel<T>`; preserve separate passive and evoke observations, and keep the
  recipe's checked icon plus explicit Spine-scene/channel-SFX fallbacks. For an **enemy
  encounter graph** (`element: enemy encounter`), read `recipes/monster.md`. Author every
  selected `ModMonsterTemplate` and `ModEncounterTemplate` as a separate registered node,
  then lower the exact roster edges; register each identity once with an explicit encounter
  `RoomType`. Implement SPEC's move contract with `MoveState`, explicit `FollowUpState`,
  `ConditionalBranchState`, and the supplied move-machine RNG for selected positive-weight
  random branches only. Use the recipe's grounded intent/effect
  patterns for buff/Power, debuff, block/heal, multi-hit, and composite actions. Monster
  attacks use `.FromMonster(this).Execute(null)` (**never** `.Targeting()`), and the
  diagnostic trigger marker goes on the enemy's move. Keep the recipe's checked static-body
  factory plus explicit
  fallback scene; animation is outside this pass. For an **event / World Node** (`element: event`),
  read `recipes/event.md`: author one `ModEventTemplate`, flat nested `events.json`,
  explicit `EventOption` keys, public-Cmd consequences, and explicit page/finish flow;
  register it once with `.SharedEvent<T>()` or `.ActEvent<TAct,T>()` and add no `[Pool]` or
  manual `AddEvent`.
  If SPEC declares **`hook participation`** on any surface, also read
  `reference/model-hook-participation.md` before writing the override. It owns the three
  declaration shapes, the per-surface owner property, and the guard-value-neutral body. Write the
  neutral return on every path outside the guard and read a rules-text number back from
  `DynamicVars` rather than repeating a literal. An Enchantment uses its five `Enchant*`
  replacements for damage, block, and play count; the general hooks are wrong there. Never
  contribute a Rest Site option through the raw hook — use `reference/rest-site-options.md`.
  Also read `reference/event-outcomes.md` when SPEC includes selections, rewards,
  conditional pages, or special combat; read `reference/event-vfx.md` when it selects
  `portrait_halo`; read `reference/event-text-effects.md` when descriptions select bounded
  vanilla text effects; read `reference/event-option-presentation.md` when enabled options
  select typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings; read
  `reference/event-native-presentation.md` when options select ordered native Card/relic
  acquisitions, `weak_short`/`strong_normal` screen shake, or built-in `trial_noble` VFX;
  read `reference/forced-followup-event.md` when SPEC selects any finite prioritized Quest
  Card mapping or sequence. For a
  **Character Foundation** (`element: character`), read
  `recipes/character.md`: use `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` and
  the three `TypeList*PoolModel` bases, fill exact HP/Gold/MaxEnergy/Orb slots, starters,
  typed pools, and localization, and register the Character plus starters/members once
  through the content pack.
  If SPEC selects any Character art profile or richer resource/buffer presentation, also
  read `reference/character-presentation.md` and obey its per-consumer promotion/fallback
  boundary. If SPEC selects native Ancient/Architect dialogue, read
  `reference/ancient-dialogue.md` and use only its localization route.
  If SPEC selects one or more secondary resources, read `reference/character-resource.md`; if it
  selects a bounded ordered semantic buffer/dynamic output, read
  `reference/ordered-card-buffer.md`.
  For every **card pile**, read `recipes/card-pile.md` and `reference/card-piles.md`. Register all piles in
  the same deferred content pack, lower every documented scope/style/anchor/open/view/
  visibility/hotkey/ExtraHand consumer selected by SPEC, and use awaited native pile Cmds
  for every movement. The Package route is not limited to ExtraHand or to previously
  exercised UI presets.
  For a **runtime UI** workflow, read `recipes/runtime-ui.md` and
  `reference/lifecycle-state-rng.md`. Keep selected top-bar, Toast, runtime-hotkey, local Capstone,
  Catalog/floating-window, search-expansion, fixed public node-attachment, and Mod-scoped shell-token
  pieces under one coordinator. Register at the recipe's required host phase, use only
  `NetScreenType.None`, keep per-frame/search callbacks within their purity and bounded-work
  contracts, and dispose every retained handle and owned node/content at the declared lifetime.
  Do not emit Settings, Progression, post-run Badge, Telemetry, Multiplayer, Update Check, or a
  connection to one of those deferred families.
  A selected resource UI uses RitsuLib's public `RegisterCombatUi` route from
  `reference/character-resource.md`. A capability with no documented public game/framework
  route is a pack authoring gap; the specific substitutes to refuse here are alternative-energy patches,
  C/D access, assembly-wide `PatchAll`, and `OpenMod.Runtime`.
  Pull the skeleton, the trigger/usage rules, the effect
  building blocks, and the loc-key derivation rule. When SPEC has an ordered
  `effects.sequence` containing an ordinary player-visible effect, read
  `reference/effect-primitives.md` once. Take exact command lowering and required inputs from
  that reference, take callback/context/owner/source/target bindings from the selected surface
  page, and emit each awaited call in SPEC order. If the callback lacks a required input, stop
  and name that input plus the applicable specialized route; do not use live grounding or invent
  a substitute for a maintained primitive. For a different family the selected recipe lacks,
  follow `grounding.md` through the rest of the shipped pack (`reference/mechanics.md`,
  `build-constraints.md`, snapshots, `errors.md`). An invented Cmd is the #1 way the repair loop
  burns its attempts.
- If a Card SPEC selects non-`none` **hand emphasis**, read
  `reference/card-hand-emphasis.md`. Preserve every ordered rule, lower a lone gold/red
  rule through its native channel, or lower all competing/custom rules through one typed
  `CardHandOutline<TCard>` registration. Never mix the two resolvers on one generated Card.
- If a Relic or Power SPEC selects non-`none` **extra badges**, read
  `reference/extra-corner-labels.md`. Enforce its Relic three-safe-corner or Power
  one-top-left boundary and host text limits, implement the matching specs provider, and use
  exactly one host-display or independent invalidation path per mutation. Intent authoring
  remains outside the active schedule.
- If a Card or Potion has a non-`none` **advanced target**, read
  `reference/advanced-targeting.md` before authoring either model. Emit one stable
  Mod-local target registration, use only its implemented consumer/mode matrix, and stop
  authoring for the limited `potion + many`; do not generate a lifecycle patch or
  restore a consumed Potion.
- If SPEC selects **bounded state**, also read `reference/stateful-mechanics.md`.
  Emit only the selected bounded schemas, exact owners/listeners, transitions, reset,
  persistence, visibility, consumers, and outputs; never infer lifetime or a transition from
  the C# field or hook that happens to be easiest.
- For every standalone/Card/Relic/Modifier **Rest Site option**, read `recipes/rest-site.md` and
  `reference/rest-site-options.md` before writing owner/option classes. Keep its
  singleplayer/free-or-fixed-Gold boundary and stop for a post-payment choice, arbitrary
  transaction, same-site repeat, or multiplayer request.
- Make every generated `.cs` file namespace-complete on its own. Copy the `using` required
  by every symbol into the file that uses it; never rely on a different snippet, file, or
  non-global import. In particular, `RegisterPatch<T>()` requires
  `using STS2RitsuLib.Patching.Core;`, and `GoldLossType` requires
  `using MegaCrit.Sts2.Core.Entities.Gold;`. Recheck imports per file before the first build.

## 1. Write the element class

**Existing vanilla visual override** - add
`<ModName>Code/VanillaOverrides/VisualOverrides.cs`:

- Group accepted operations by public provider surface. Register one provider per selected
  surface with the stable Mod key from `vanilla-visual-overrides.md`; match every exact
  catalog concrete type inside that provider and return `null` for all other models.
- Return checked Mod-local paths for path providers and typed `ResourceLoader` results for
  Material/Texture/PackedScene providers. Filter directories and resource lists as the
  reference requires. Never register a second model or use a new-content `AssetProfile` as
  a substitute for an external provider.
- Emit every selected surface as a separate visual manifest operation. Path/resource
  alternatives for one target surface conflict. Keep optional-resource absence as vanilla
  fallback and stop before build when a required resource is absent.
- Use existing `gen_sprite.py` specs only for matching raster roles. Material, PackedScene,
  Spine, and layer-directory inputs must already be authored local resources; do not ask an
  image model to fabricate them.

**Existing vanilla Card behavior override** - add one
`<ModName>Code/VanillaOverrides/<TargetType>Override.cs` per exact target:

- Start from `CardCapability`, or `CardPlayCapability` when any `OnPlay` operation is
  present. Implement only contributor interfaces selected by the accepted operations.
- Add one registered capability and one stable
  `ConfigureDefaultModelCapabilities<TargetType>` modifier in `MainFile.Content.cs`. Never
  register the vanilla Card as Mod content and never construct a model-backed capability
  directly.
- Aggregate all operations for that target into the one class. Preserve manifest order in
  costs, rules, fragments, effects, and owner hooks. One replacement may coexist with
  ordered composition; a second replacement is a conflict.
- Capability variables live on the capability, update from the owner upgrade callbacks,
  and are the only new variables allowed. Reading a checked owner variable is allowed;
  mutating the vanilla Card's canonical variable set is not.
- `BeforeOwnerCardOnPlay` returns `false` after compose-before effects and `true` after a
  complete replacement. Do not reproduce payment, target selection, history, result-pile,
  enchantment, affliction, or later-hook stages from the native wrapper.
- Owner draw/discard/exhaust composition guards the exact owner instance. Do not implement
  transform carry-over; a transformed Card with a different identity must not inherit the
  old target's override.
- Write every accepted operation to `openmod/vanilla-overrides.json` with the exact checked
  baseline and public route. Keep the manifest, class, and localization behavior in sync.
- If one requested operation is outside the promoted table, stop that operation explicitly;
  do not hide a patch, reflection expression, or raw method name inside otherwise valid C#.

**Existing vanilla Ancient initial-options override** - add
`<ModName>Code/VanillaOverrides/AncientOverrides.cs` and follow
`reference/vanilla-ancient-overrides.md` exactly:

- For `append`, register one `ModAncientOptionRule` per manifest operation before ModelDb
  freezes. Its factory may return multiple options in manifest order after applying each
  `visible_when`; use the public priority and duplicate-text policy literally.
- For `replace`, install the Package's one fixed fingerprinted postfix through RitsuLib's
  patcher. Dispatch only by exact catalog type, let the original wrapper retain its
  `_generatedOptions` list, mutate that same list, preserve the native blocked Proceed
  state, and run before RitsuLib's append postfix. Do not generate any other patch shape.
- Use the full public `EventOption` localization constructor with Mod-local `events.json`.
  Recompute visibility, lock state, and affordability whenever a page is built; pay one
  fixed cost first, then await effects/selectors/rewards in manifest order before the next
  step. Build typed Hover Tips and relic-backed presentation only through their public
  factories.
- Lower `stay` directly. Lower `page` and `finish` only through the two fixed fingerprinted
  `SetEventState` and `Done` UnsafeAccessor helpers in the reference. `Done()` owns native
  choice history; never substitute `StartPreFinished()` or hand-edit Ancient state.
- Put every option `.title`/`.description` and page description in both required languages'
  `<ModName>/localization/<lang>/events.json`. Do not put these behavior keys in
  `ancients.json`, which remains the custom-Character dialogue table.
- Emit one exact checked manifest operation per target route. Multiple appends may compose;
  one same-target replacement conflicts with every append/replacement in this Mod. Selected
  Ancient/Event visual overrides remain separate manifest operations and contain no scripts.
- Preserve the vanilla Ancient class, ModelId, room, opening dialogue, save identity,
  allowance gate, ambient audio, and native finish lifecycle. A request for a new Ancient
  routes separately through `recipes/ancient.md`; it is never implemented by changing this
  override package. Stop this override route for global dialogue replacement, random/RNG
  rewrite, special combat, direct room transition, multiplayer, or any prompt-derived
  private/patch route.

**Existing vanilla availability** — add `<ModName>Code/VanillaOverrides/AvailabilityOverrides.cs`
and follow `reference/vanilla-availability-overrides.md` exactly:

- For public epoch routes, call `RequireEpoch` once per exact target before unlock rules
  freeze. Accept only the catalog's 57 epoch IDs. Cards, Characters, ordinary Events, and
  shared Darv are the public host slice; act-owned Ancients and permanent Card/Character/
  Event disable are not silently substituted.
- For public pool `add`, call `ModHelper.AddModelToPool` with the catalog concrete model
  and pool types before `ModelDb` reads `All*` or `All*Ids`. Never register a vanilla model
  through `ModContentRegistry` or claim its ownership.
- For Relic/Potion epoch gates and pool `remove`/`move`, install only the fixed cataloged
  `IPatchMethod` targets and fingerprints. Relic/Potion epoch patches cover the base pool
  and all six concrete vanilla overrides because the game overrides `GetUnlocked*`.
  Dispatch by exact ModelId from the validated manifest table and pass unrelated models
  unchanged. A failed `PatchAll()` is a load failure.
- Lower a pool move as public destination add plus the fixed source getter filter. Keep
  existing Cards/Relics/Potions in their current deck/inventory/belt and preserve every
  instance. Use the simulated manifest order and the declared primary pool; never patch
  private caches or invent a reward-weight hook.
- Emit the exact source baseline, route fingerprint/dependencies, action, source/destination,
  `existing_instances: preserve`, `expected_primary_pool_model_id`, and singleplayer scope
  in `openmod/vanilla-overrides.json`. Stop for debug pools, wrong pool category, duplicate
  add, missing source, final-pool removal, weighting, multiplayer, or prompt-derived patch
  code.

**Existing vanilla non-Card data/behavior** - add one target-grouped file under
`<ModName>Code/VanillaOverrides/` and follow
`reference/vanilla-non-card-overrides.md` exactly:

- Public owner-hook composition uses the matching typed RitsuLib capability. Register and
  attach one capability per semantic order group to the exact vanilla type. Override only
  the selected pinned hook signature; implement real owner/side/context guards and await
  every effect. Do not register the vanilla model or accept an unavailable hook context.
- Complete owner-hook replacement installs only the checked run/combat stream postfixes
  after RitsuLib capability expansion. Remove the selected original owner by exact ModelId,
  retain all capabilities, and pass every unrelated model through unchanged.
- Intrinsic data uses only the target-specific checked getter Adapter. Consolidate inherited
  getter targets, dispatch on exact ModelId, and apply the validated set/delta result. Do
  not edit canonical instances or backing fields.
- Complete lifecycle/body replacement installs every required fingerprinted dependency and
  suppresses the original exactly once. Task bodies return one awaited generated helper;
  synchronous Affliction apply/remove fields remain empty. Build complete Monster state
  machines, keep Encounter actual/all-possible rosters identical, and keep ordinary Event
  options/pages under the required `<MOD_ID>_EVENT_*` localization namespace.
- Emit each operation, exact baseline, fingerprint/dependencies, singleplayer scope, and
  complete semantic body in `openmod/vanilla-overrides.json`. Stop one unsupported operation
  explicitly instead of hiding raw Harmony/reflection/IL in an otherwise valid file.

**Relic** — see `surfaces/relic.md` § Author the element class.

**Potion** — see `surfaces/potion.md` § Author the element class.

**Card** — see `surfaces/card.md` § Author the element class.

**Custom power** — see `surfaces/power.md` § Author the element class.

**Custom keyword** — see `surfaces/keyword.md` § Author the element class.

**Card enchantment** — see `surfaces/enchantment.md` § Author the element class.

**Custom orb** — see `surfaces/orb.md` § Author the element class.

**Enemy encounter graph** — see `surfaces/monster.md` § Author the element classes. Emit
the selected Monster and Encounter nodes plus exact roster edges, with no `[Pool]` on either.

**Event / World Node** — see `surfaces/event.md` § Author the element class.

**Character Foundation** — see `surfaces/character.md` § Author the element class.

**Counter Power amount-domain gate (applies to every source element)** — before writing
any custom Counter mutation, read that Power's `amount domain` from SPEC. The default
nonnegative domain means:

- positive gain/application may use `PowerCmd.Apply<T>`;
- consumption must call `GetPower<T>()`, spend zero when absent, clamp the actual spend
  to the existing `Amount`, then call `PowerCmd.ModifyAmount` on that instance with
  `null, null` applier/card source (the vanilla internal-consumption context);
- a negative `PowerCmd.Apply<T>` is forbidden for consumption because it can create a
  missing Power with a negative amount;
- every finite SPEC bound must be enforced by clamping gain/consumption to current
  headroom, and a signed domain is allowed only with explicit negative-stack semantics;
- because amount hooks can rewrite a requested offset, capture the Cmd return and re-read
  the retained Power. The domain and Tier-2 assertion apply to that final post-hook state,
  and logs must distinguish requested offset, actual offset, and remaining amount.

Use the exact copyable sequence in `recipes/power.md`; do not treat `PowerVar<T>` or
`AllowNegative` as min/max validation.

## 2. Inject the load and diagnostic markers

The selected scaffold must emit the framework diagnostic and exact **load** marker, or
tier-1 verify silently finds nothing. Use the shared envelope from
`semantic-contract.md`:

```csharp
Logger.Info($"[OPENMOD-FRAMEWORK] phase=load mod=<mod-id> framework=RitsuLib frameworkVersion={Const.Version} host=0.107.1 compat=0.107.1 adapter=<surface>/sts2-content-semantic-v1 status=resolved");
Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");
```

The adapter must derive these values from the selected compat profile. Do not hardcode
a beta-facing fallback or emit `status=resolved` before the host/compat check succeeds.

Then log a **diagnostic** marker inside the trigger showing what code ran
(a relic's combat-start hook, a potion's `OnUse`, a card's `OnPlay`, an enemy's move body,
or an event option method):

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ElementName> fired/used: <requested outcome>");
```

The load marker proves Tier 1. The trigger marker stays for diagnosis, but it is **not**
Tier-2 proof: preview/calculation hooks may log without committing state. The harness in
the next step independently asserts post-state and emits the only accepted proof marker.

## 2.5 Emit the tier-2 self-test harness

This is what makes tier-2 automatic — the effect fires and is grepped with **no human at
the keyboard, no dev-console typing**. Query the **sts2-api** skill for
`reference/selftest-harness.md` and follow it. In short:

1. Emit `<ModName>Code/SelfTest.cs` from that page. The arg gate, menu→run navigation,
   timeout, catch, terminal markers, and ship-safety are shared by every type; the hosted
   room entry is scenario-specific. Keep it in the **same namespace as `MainFile.cs`**
   (`<ModName>.<ModName>Code`) so it reaches `MainFile.Logger`.
2. Fill **exactly one** source DRIVER body based on the source element's real type:
   Each surface owns its driver body in `surfaces/<element>.md` § Self-test driver body:
   **relic**, **card**, **potion**, **enemy encounter**, **event**, and **character**. A
   **power**, **keyword**, or **enchantment** has no scenario of its own and adds its
   assertions to its host Card's run; an **orb** is driven through its channel host.
   The shared declarations below apply across those drivers.
   **advanced target** → keep the same real Card/Potion driver, then use
   `reference/advanced-targeting.md` to assert exact affected creature IDs, payment or
   Potion retention on cancellation, normal Card result pile, zero/one/multiple legal
   candidates, and queued target invalidation. Headed mouse/controller/reticle checks stay
   separate from the structured state proof.
   **secondary resources** → use `reference/character-resource.md`: derive checks only for
   the definitions, persistence/turn-start policies, Card uses, shortfall behavior, committed
   payoffs, and UI consumers selected by SPEC. Drive affordable/unaffordable and rejected
   cases for each selected payment role, assert authoritative ledger results and resource
   bounds, and inspect non-overlap for each selected visible consumer. Add a second combat or
   run-save boundary only when that selected lifecycle requires it.
   **ordered semantic buffer/dynamic output** → use `reference/ordered-card-buffer.md`: drive
   real source cards through their native result piles, assert attached-state order/capacity/
   non-destructive overflow and visible state, compile/clear the ordered snapshot, assert
   one `CardGeneratedEntry`, play the configured output, then prove a distinct empty state
   in combat 2. Reuse the owning character or `CombatPlayer` suite; do not create a project
   solely for this capability.
   For a multi-element SPEC, use
   that same source driver, then walk `interactions` in dependency order and
   observe each dependent marker/state invariant. There is no `combo` element or separate
   registration path; the reference page's card→power example shows the additional waits
   and `EndTurn` needed by that particular interaction. A nonnegative Counter `consumes`
   edge must also run the reference page's zero/fewer-than-N/at-least-N boundary matrix and
   assert that no negative instance appears. Its § CombatEnemy shows the full enemy-encounter
   driver body.
   A stateful source must instead use the page's **stateful cadence** variant: assert the
   `N-1` no-fire state, the exact threshold delta, and the reset/carry-over boundary. A
   run-lifetime `SavedAttachedState` additionally round-trips through
   `SavedProperties.From`/`Fill`; a run cadence must enter a second combat rather than
   mutating the attached value directly to simulate carry-over.
   A **calculated-value Card** selects its focused matrix in
   `surfaces/card.md` § Self-test driver body.
   A **standalone/Card/Relic/Modifier Rest Site option** uses the focused real-host matrix in
   `reference/rest-site-options.md`: absent owner, insufficient-Gold gray state,
   render-then-remove-Gold failed selection with zero deltas, exact successful
   Gold/Max-HP/history deltas, rebuilt list without duplication, declared stay/leave,
   second-visit repeatability, controller focus, custom icon, and missing-icon native
   fallback. Keep the run explicitly singleplayer; for a Card owner also assert exactly one
   matching deck instance and the same concrete owner/state handle.
   A **Reward** selects the real native-screen matrix in `surfaces/reward.md`: failed claim with
   no mutation, successful awaited effect, correct offer/insertion, pending save/load
   reconstruction, linked-set semantics when selected, localization, and headed input/UI. Do not
   call reconstruction or serialization behavior proof.
    A **card pile** selects the matching host matrix in
   `reference/card-piles.md`. Prove the generated Mod's selected scopes, UI styles,
   anchors, open/view/hotkey behavior, explicit Card movements, localization, and
   ExtraHand interactions. Do not require one proof per documented public consumer merely
    to preserve Package support; verify every behavior the generated SPEC actually uses.
    A **runtime UI** workflow follows `surfaces/runtime-ui.md`: drive the real top bar and input
    router, the selected Toast/Capstone/window/Catalog hosts, search invalidation/disposal, and the
    exact stable node attachment. Assert open/selected/count/visibility, input suppression, item/
    filter/action state, content ownership, replacement/close, and cleanup for only the selected
    variants. Keep mouse/controller focus, layout, animation, drag/resize, and theme appearance in
    the separate headed review; constructed nodes and direct callback calls are not host proof.
3. In every driver, snapshot concrete state, drive the real source, assert the SPEC's exact
   post-state, then call the shared `StateProof(...)`. Its structured
   `[T2MOD-SELFTEST] <ModName> state proof:` line must include the selected framework,
   framework version, host, compat target, expected value, and observed value. A broad
   `played/fired/used` marker never qualifies.
4. Add the **gated arm line** to `MainFile.Initialize()`, right after the load marker:

```csharp
if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();   // verification-only; dormant for end users
```
`using MegaCrit.Sts2.Core.Helpers;` for `CommandLineHelper`. The arg gate means a normal
user launch never arms it — no menu driving, fully inert. It ships dormant inside the mod.

**Grounding rule still holds:** the harness uses only the confirmed public Cmds in
`selftest-harness.md` (`CardCmd.AutoPlay`, `PowerCmd.Apply`, `RelicCmd.Obtain`, potion
`EnqueueManualUse`, …). Do **not** invent an API or try `NDevConsole…ProcessCommand(string)`
— that path is unreachable (private field); the page explains why.

## 3. Write localization

For every player-facing string, author both
`<ModName>/localization/eng/` and `<ModName>/localization/zhs/` from the exact bilingual
SPEC text. The directory trees, table names, keys, and SmartFormat tokens are identical;
only the localized prose differs. Do not satisfy the Chinese table by copying its English
value unchanged.

When display `text effects` is `vanilla`, apply semantic `text spans` only after the plain
description and SmartFormat placeholders are correct. Validate every tag against
`reference/content-text-effects.md`, keep tags balanced, do not wrap `:diff()` values in
another color, and never copy user-supplied raw markup. Titles, flavor, and selection
prompts stay plain.

For a **character**, write the 14 normalized flat keys to `characters.json` and the
complete `THE_ARCHITECT.talk.<CHAR_ID>` dialogue to `ancients.json`, as listed in
`recipes/character.md`. Lower every selected semantic Ancient group through
`reference/ancient-dialogue.md`: explicit zero-based `-visit`, one consistent repeat mode,
one speaker per line, and `.next` only on non-terminal lines. Generated Mods rely on
RitsuLib's registered population patch and emit no Harmony/reflection injection. For an
**event**, write the normalized title/page/option/result keys
to `events.json`; `InitialOptionKey` and `ModOptionKey` must match those explicit segments.

For the JSON-backed types, add the same keys to
`<ModName>/localization/<lang>/<table>.json` for both `eng` and `zhs` — **`relics.json`** for a
relic, **`potions.json`** for a potion, **`cards.json`** for a card, **`powers.json`**
for a custom power, **`monsters.json`** + **`encounters.json`** for an enemy encounter,
**`events.json`** for an Event, and **`characters.json`** + **`ancients.json`** for a
Character.
**Keys are FLAT and prefixed** (recipe's loc-key rule + errors.md "raw-key title"):

```json
{
  "<MOD>_<CATEGORY>_<TYPE>.title": "<title from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.description": "<hover text from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.flavor": "<relic flavor - relics only>"
}
```

Relics take `.title/.description/.flavor`; potions take `.title/.description` (plus
`.selectionScreenPrompt` only if the effect prompts a choice — no `.flavor`); cards take
`.title/.description` (plus `.selectionScreenPrompt` if it prompts a choice — no
`.flavor`, no separate upgrade key). A **card description uses SmartFormat placeholders**
for scaling numbers — `"Deal {Damage:diff()} damage."` not `"Deal 6 damage."` — so the
upgraded value renders automatically (`reference/mechanics.md` §2). A **power** takes
`.title/.description` with `{Amount}` for the stack count. An **enemy encounter** takes
two tables: `monsters.json` with just `<MOD>_MONSTER_<TYPE>.name`, and `encounters.json`
with `<MOD>_ENCOUNTER_<TYPE>.title` + `.loss`. Use the exact normalized public entries
produced by the RitsuLib adapter. Not nested JSON — a flat `Dictionary<string,string>`.
An owned Rest Site option adds its stable namespaced `.title` and `.description` keys to
the same `relics.json`; these are separate from the owner Relic's three model keys.
When a calculated Card value declares a tooltip, also add its resolved `.title` and
`.description` keys to each required language's `static_hover_tips.json`; omit the icon argument
for the native null-icon fallback.

## 4. Art (per SPEC's art plan — placeholder or generate)

Read `SPEC.md`'s `**art**` line — it holds the **one mod-level** art choice made at
interview time (placeholder or generate). Do NOT re-ask here. Two branches follow. If
generate, apply it to every supported asset in the mod using each element's own SPEC
subject.

### Placeholder (the default — do nothing)

Leaving the art file absent makes the scaffolded base class fall back to the template
default, and the mod loads fine on it: a **relic** falls back to `relic.png` if
`images/relics/<slug>.png` is absent; a **potion** falls back to `potion.png` when
`images/potions/<slug>.png` is absent (the base's `PotionImagePath` `Exists()` check); a
**card** renders on the default portrait when `images/card_portraits/big/<slug>.png` is
absent. This is the fast path — nothing to build, no backend, no dev box. For an **event**,
the class uses the recipe's `ResourceLoader.Exists` branch and returns the verified vanilla
portrait when `images/events/<slug>.png` is absent; the default event layout always preloads
a portrait. For an owned **Rest Site option**, resolve an absent
`images/rest_site_options/<slug>.png` to the checked native Heal-option image; the custom
`OptionId` cannot derive a valid implicit vanilla fallback. For an **enchantment**, its
`CustomIconPath` existence check returns `null`
when `images/enchantments/<slug>.png` is absent, preserving the game's missing-icon
fallback.
For an **orb**, placeholder mode keeps the recipe's Frost icon, Spine scene, and channel
SFX fallbacks; it must not rely on the custom-id path convention. Skip to §5.
For an **enemy encounter**, the recipe checks `images/monsters/<slug>.png` and returns
`null` from `TryCreateCreatureVisuals()` when absent, so the explicit
`MonsterAssetProfile` fallback scene loads without a missing-resource error. Skip to §5.
For a **character**, leave optional `CharacterAssetProfile` rows unset so RitsuLib resolves
the explicitly selected Ironclad placeholder/native fallback. Set
`PlaceholderCharacterId => "ironclad"`: the full combat counter resolves
`ironclad_energy_counter.tscn`; an absent large Card Energy icon resolves through
`EnergyIconHelper.GetPath("ironclad")` (`energy_ironclad.tres`); and an absent rich-text
Energy icon resolves `res://images/packed/sprite_fonts/ironclad_energy_icon.png`. Never
derive an Energy fallback such as `energy_red` from the Character theme. The combat override
returns `null` when its checked PNG is absent, so RitsuLib resumes that resolved profile
fallback without a missing-resource load. Placeholder mode emits no Character asset or
combat cue set. The static combat body remains the cue fallback; Cast, Spine, and
unpromoted consumers are not supported.
For an **existing vanilla visual override**, placeholder is valid only when its manifest
resource is optional: emit the checked provider, let the missing resource return `null`,
and preserve that vanilla surface. A required visual operation cannot use placeholder;
stop and obtain the accepted resource before build.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

Supported sprite specs (see `sts2-api` → `reference/art-contract.md` and
`reference/character-presentation.md` and `reference/character-combat-cues.md` for the full
contracts). For an existing vanilla texture override, select a matching established spec
by consumer role, normalize into the manifest's Mod-local path, and preserve every
unselected surface. Do not use this branch for Material, PackedScene, Spine, or directory
resources. Character generation covers
nine promoted static profiles and one optional bounded cue bundle; locked selection and
map marker remain explicit gaps.
- **`--spec card`** — the one portrait a normal card loads, **1000×760 landscape**, full-
  bleed (chroma OFF), written to `card_portraits/big/<slug>.png`. **Live-verified in-game.**
  The 606×852 "full art" size is **Ancient-rarity only and out of scope — we never make it**.
- **`--spec relic` / `--spec power`** — a **256×256** cut-out icon, `fit: contain`, magenta
  chroma-key ON (so the prompt must ask for a solid flat `#FF00FF` background — see the
  contract). **Live-verified in-game.** A relic writes the main and big icons plus
  `relics/<slug>_outline.png`; a power writes only its main and big icons. The outline is
  an opaque-white silhouette expanded by `round(3% * 256) = 8` pixels from the final main
  icon alpha; main normalization reserves the same 8-pixel inset so the expansion cannot
  be clipped by the fixed canvas. It is deterministic and spends no additional acquisition call. A missing
  outline retains the adapter's checked fallback. **power** has no outline.
  **Prereq:** the relic/power subclass must extend `ModRelicTemplate` / `ModPowerTemplate`
  and expose the checked `RelicAssetProfile` / `PowerAssetProfile`. Direct game-model
  subclasses bypass the adapter's asset fallback (see the surface recipes).
- **`--spec potion`** — a **256×256** cut-out icon, `fit: contain`, magenta chroma-key ON
  (prompt asks for a solid flat `#FF00FF` background), a loose PNG like relic/power — **not**
  a `.tres` atlas. **Live-verified in-game.** Writes **ONE file**, `potions/<slug>.png` (the
  bar icon, hover tooltip, and use VFX all reuse that single texture — no `big/`). Art
  direction: draw the bottle **tilted ~45° leaning right** (STS2's potion display angle; see
  `art-contract.md`). **Prereq:** the potion subclass must extend `ModPotionTemplate` and
  expose the checked `PotionAssetProfile`; omit that override in placeholder mode.
- **`--spec enchantment`** — one **64×64** cut-out icon, `fit: contain`, magenta
  chroma-key ON, written to `enchantments/<slug>.png`. **Live-verified in the real hand-card
  tab and its hover tooltip.** Both consumers reuse the same `EnchantmentModel.Icon`; there
  is no `big/` variant. The subclass must use the recipe's checked
  `EnchantmentAssetProfile`; omit it so placeholder mode retains the fallback.
- **`--spec orb`** - one **100x100** cut-out icon, `fit: contain`, magenta chroma-key ON,
  written to `orbs/<slug>.png`. **Live-verified in the real smart tooltip and trigger
  flash.** This does not generate the persistent combat Spine scene; retain the recipe's
  Frost scene and channel-SFX fallbacks.
- **`--spec monster`** - one **360x360** transparent static body, `fit: contain`, magenta
  chroma-key ON, written to `monsters/<slug>.png`. **Live-verified in both the real combat
  `NCreature` and default bestiary layout.** The concrete monster must use the recipe's
  existence-checked `TryCreateCreatureVisuals()` factory and keep `MonsterAssetProfile`
  on the built-in scene fallback. This does not add Spine, move animation, or a phobia
  variant.
- **`--spec event`** — one opaque **3440×1613** normal/default-layout portrait slot per
  invocation, `fit: cover`, chroma-key OFF, written to `events/<slot-slug>.png`.
  **Live-verified in the real MapNode host for the initial and a later page.** Generate the
  initial slot plus only the later-page slots explicitly listed in SPEC. The event class
  must retain the checked initial fallback and keep the current portrait when optional
  page art is absent. This does not generate a phobia variant, custom layout, or Ancient
  background scene. The optional code-native `portrait_halo` is authored from
  `reference/event-vfx.md` and has no `gen_sprite.py` invocation.
- **`--spec rest_site_option`** - one opaque **256x169** native-button image,
  `fit: cover`, chroma-key OFF, written to `rest_site_options/<slug>.png`. This size and
  custom-button framing are live-verified in the focused real Rest Site host. The owning
  option must explicitly fall back to the native Heal icon when this file is absent.
- **`--spec character_select` / `character_background` / `character_icon` /
  `character_combat` / `character_rest` / `character_merchant` / `character_energy` /
  `character_energy_large` / `character_energy_text`** — respectively opaque **132x195** and **1920x1200** assets,
  transparent **88x88** and three **512x512** static bodies, five transparent **256x256**
  full-energy layers, one transparent **256x256** large Energy icon, and one transparent
  **24x24** text Energy icon. Never point both pool getters at the same file. The existing
  static profiles are live-proven in
  real selection, top-panel, CombatPlayer, RestSite, Shop, and energy consumers. Author the
  raw icon/background/rest/merchant/energy wrappers and the existence-checked combat resource
  factory from `character-presentation.md`; `build.py`
  packs them without Godot/MegaDot. Full energy uses five loose PNGs inside one raw scene;
  RitsuLib's Shop profile needs no historical `_Ready()` prefix. Keep checked profile/text
  fallbacks. Do not emit
  locked selection or map-marker art as supported.
- **`--spec character_cue_idle` / `character_cue_attack` / `character_cue_hit` /
  `character_cue_dead`** - four identity-referenced action sheets (2x2, 2x2, 2x2, 2x3)
  normalized to 4/4/4/6 transparent 512x512 frames. Import each with the matching lowercase
  action slug. The first three sheets only stage under `art-sources/character-cues`; after
  all four exist, deterministic QC atomically replaces `images/charui/cues` and writes GIF,
  contact-sheet, and metadata review output. A failed or incomplete bundle leaves existing
  runtime cues unchanged. Runtime support is combat-only and all-or-nothing.

1. **Build the prompt (three segments — see `art-contract.md`).** For card and the
   `relic`/`power`/`potion` icon specs,
   use ① the fixed STS2 style
   descriptor (verbatim, incl. the "reference images = STYLE ONLY, don't reuse their
   objects" guard), ② the visual subject you *translate* from the element's **name**
   (flavor secondary) — NOT its damage/keyword numbers; mechanics have no picture, and
   painting them ("two blood drops" for "lose 2 HP") looks literal and awkward. Write ②
   as **two-to-four sentences describing one dramatic, centered, frozen-mid-motion
   subject with a warm rim light** (e.g. "Firebolt" → *a blazing arrow of living fire
   streaking diagonally mid-flight, trailing embers, orange-to-yellow rim light on its
   edge*), not a keyword list. ③ the fixed structural/negative constraints. You write
   it — don't make the user do it. Only ② differs per element; ①③ are shared guardrails.
   **For a `relic`/`power`/`potion` icon** the same name→subject translation applies,
   but since it's a cut-out (chroma ON), ③ must also ask for a **solid flat `#FF00FF`
   magenta background, no gradient** so the tool can key it out cleanly.
   **For `rest_site_option`**, use the dedicated compact opaque scene-tile template in
   `art-contract.md`: one centered readable action/object, a complete background, and no
   chroma key, text, border, or UI.
   **For `enchantment`**, use the contract's dedicated micro-emblem template: bold slightly
   irregular silhouette, broad matte fills, one dominant hue with only one or two value
   steps, and almost no fine detail so it survives at 64x64. Do not turn it into a relic,
   glossy app icon, badge, or miniature scene.
   **For `orb`**, use the dedicated elemental-core template: a large irregular near-circle,
   chunky layered material forms, three-to-five broad values, dark internal occlusion,
   selective highlights, and contained glow. Do not request a generic vector glyph, glass
   marble, UI frame, detached particles, or persistent combat body.
   **For `monster`**, use the dedicated softly hand-painted render template, not Card's hard
   cel shading/radial burst. Translate the concept into one complete creature with broad
   values, gently modeled volume, controlled brush texture, selective edges, a restrained
   base palette, and focused accents. Keep a neutral front/3/4 pose, both feet on one
   baseline, the full silhouette inside the frame, and no ground/shadow/attack effect; the
   same still is shown for every move and in bestiary.
   **For `event`**, use the separate event template: derive one concrete opening situation,
   place the focal subject in the left third, and reserve darker low-detail center-right and
   lower-right space for the game's title, description, and options. Do not reuse the card
   prompt's centered-subject constraint or paint option reward numbers into the scene.
**Character art profiles.** When `SPEC.md` selects Character art, emit only the nine
selected static profiles and optional bounded cue bundle above. Selection and background
are opaque (`--chroma` off); icon,
combat/rest/merchant bodies, full-energy layers, and large/text Energy icons use `--chroma`.
Do not set `CharacterAssetProfile.Scenes.VisualsPath` to the combat PNG: the texture-only
factory has no per-Character footprint style. Instead, existence-check the PNG in
`TryCreateCreatureVisuals()` and call RitsuLib's public resource factory with the reviewed
`VisualNodeStyle` scale/position; return `null` when absent so the resolved profile fallback
continues normally. Emit minimal raw scenes for background/rest/merchant and the five-layer
energy counter. Its missing scene resolves through `PlaceholderCharacterId => "ironclad"`,
never through the theme palette. The icon wrapper layers `icon_outline.png` behind `icon.png`; set
`Ui.IconTexturePath`, `Ui.IconOutlineTexturePath`, and `Ui.IconPath` to the main PNG,
outline PNG, and wrapper scene respectively. Return `energy_large.png` from
`BigEnergyIconPath` and `energy_text.png` from `TextEnergyIconPath`, checking each resource
independently before returning it. Their checked fallbacks are
`EnergyIconHelper.GetPath("ironclad")` and
`res://images/packed/sprite_fonts/ironclad_energy_icon.png`, respectively.
Locked/map consumers remain explicit gaps with inherited profile fallbacks.

The character prompt must describe one original subject in the STS2 painterly style-only
reference pool. Selection portraits keep the full source composition inside the reviewed
132x195 safe box; backgrounds use the exact 16:10 host composition, place the focal
character on the right, and reserve the calm left-center information-panel area at
1920x1200; top-panel icons are bold at 88x88; static combat/rest/
merchant bodies are centered on one baseline at 512x512; full energy requests five
complementary layers. The 256x256 large pool icon and 24x24 text icon share the SPEC's
palette/motif but are normalized separately for their own consumers. Combat cue sheets use
the same identity route and shared combat footprint. Derive the SPEC's neutral combat
anchor once, then repeat the fixed identity/geometry continuity lock from
`art-contract.md` verbatim in all four cue prompts. Adjacent cells are closely spaced
in-between poses with substantial silhouette overlap, not distant key poses; Attack/Hit
start near and recover toward Idle, while Dead falls through six small steps. Do not
request Cast, Spine, trails, transition shaders, remote hands, phobia art, audio, or a
custom Ancient layout. The Ancient name-banner/Architect line is a separate native headed
proof, not a normal Event rich-text shortcut.

**CharacterArtBundle routing.** Generate/import the required `character_select` asset
first. Its normalized `charui/select.png` is the sole identity bootstrap; do not create a
separate character sheet. For identity-sensitive `character_combat`, `character_rest`,
`character_merchant`, and all four `character_cue_*` assets, pass that selection portrait as
`--identity-reference` alongside up to three type-matched STS2 style references. For the
selection background, top-panel icon, five Energy layers, and large/text Energy icons,
derive a concise palette/motif brief from the user's description and the reviewed
selection portrait, but do not pass the portrait as an image reference. `character_icon`
also writes `charui/icon_outline.png` as an opaque-white silhouette expanded by
`round(3% * 88) = 3` pixels from final main alpha. This derived file and every Relic
outline use the same rule; normalization reserves the matching main-icon inset, and the
derivation never triggers an acquisition call. Keep all generation/import calls at one acquired image;
the existing explicit per-paid-call approval remains mandatory.

**Combat cue runtime.** Generate the helper and Character overrides exactly from
`reference/character-combat-cues.md`. Require all eighteen paths and sizes before building
the private `VisualCueSet`; use `Idle/00` plus the shared geometry for the initial visual;
pass the set directly to `ModAnimStateMachines.StandardCue` from
`SetupCustomCombatAnimationStateMachine`. Do not set `CharacterAssetProfile.VisualCues`,
because RitsuLib can reuse that fallback in merchant/rest hosts. On any missing/invalid
frame, mount no playback node and use `combat.png`, then the resolved profile fallback.

**Character-wide theme contract.** Emit one Character-local theme class and copy every
explicit value from SPEC into it: `NameColor`, `EnergyLabelOutlineColor`,
`DeckEntryCardColor`, `EnergyOutlineColor`, the card-frame target RGB/brightness, both
Energy-icon paths, and the shared icon palette/motif. Keep one stable Mod-owned
`EnergyColorName` prefix for all three pools; it is a lookup key, not a palette name. The
Character and card-pool models
must delegate to that class instead of repeating literals. Use RitsuLib's public
`MaterialUtils.CreateReplaceHueShaderMaterial` once and return the cached material from
`TypeListCardPoolModel.PoolFrameMaterial`; do not ship a custom shader or generate a card
frame image. The pool's missing-file fallback is per icon: one absent file must not disable
the other route. The self-test asserts all four colors, shader parameters, distinct paths,
exact 256x256/24x24 textures, and both real consumers before it emits the theme marker.

1a. **Respect the selected route's consent boundary.** For `runtime-imagegen`, the user's
   mod-level `generate` choice authorizes the initial one-image-per-asset native-tool run;
   it needs no separate API key, but follow any approval or usage warning presented by the
   host and never claim that host usage is free. For Vofy or BYO HTTP, show the assembled
   prompt, chosen model/backend, output count (**one**), and credit-spending action, then
   get a one-line yes for this exact paid generation. Never treat an earlier art preference
   as approval to spend through an external route. Every regeneration, on any route, needs
   a new confirmation after the user sees the current result.
2. **Locate the mod's images dir**: `<work dir>/<ModName>/images` (the resource subdir
   the template made; `<slug>` = lowercased prefix-stripped id, same as the loc keys).
3. **Acquire through the SPEC's `art source`, then import** (`${GAME_TOOLS_DIR}` resolves
   per install — same as `build.py`). Use the `--spec` matching SPEC's element.

   **Host-native image generation (`runtime-imagegen`):** use this route only when the
   current runtime actually exposes a callable raster image-generation tool. In Codex,
   follow the installed `imagegen` skill and use its built-in `image_gen` mode; do not
   switch to that skill's CLI/API fallback, which requires `OPENAI_API_KEY`, unless the
   user explicitly selected the separate `byo-http` route. A model name or installed skill
   file alone does not prove that the native tool is available.

   Issue one native image call per distinct asset with the assembled prompt. For a full-
   bleed card, request the landscape composition without a keyed background. For relic,
   power, potion, enchantment, orb icons, and monster bodies, keep the prompt's perfectly flat `#FF00FF`
   background; do not
   remove it with a runtime-specific helper because `gen_sprite.py import --chroma` owns
   that deterministic step. When the native tool supports reference images, randomly choose
   up to three type-matched files from
   `${STS2_API_SKILL_DIR}/reference/art-samples/<spec>/`, make them visible using the
   runtime's normal local-image viewing mechanism, and label them STYLE REFERENCE ONLY. If reference inputs
   are unavailable, use the fixed text style descriptor alone.

   Inspect the generated image, then use the actual local file path reported by the host
   (Codex normally saves built-in results below `$CODEX_HOME/generated_images/`; do not
   assume that path for other runtimes). The route is unavailable if it produces no local
   image file. Pass that file through the existing normalizer:
   ```
   python ${GAME_TOOLS_DIR}/gen_sprite.py import \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|rest_site_option|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --input "<native-output.png>" \
     --out "<work dir>/<ModName>/images" [--chroma]
   ```
   Add `--chroma` for `relic`, `power`, `potion`, `enchantment`, `orb`, `monster`, and
   selected Character icon/combat/rest/merchant/full-energy/large-energy/text-energy specs. Leave it
    off for Character selection/background. For full energy, invoke `character_energy`
    exactly once with slug `orb_layer_1`. Install the lead-supplied
    `reference/energy_template/layer_2.png` through `layer_5.png` with
    `character_art.py --install-energy-templates`; those four normalized project assets
    are fixed byte-for-byte and are what the mod references and packages. Never spend a
    generation call on layers 2-5.
   For the other Character slots use the bundle's stable slugs `select`, `background`,
   `icon`, `combat`, `rest`, `merchant`, `energy_large`, and `energy_text`; do not invent a second identity
   filename or a separate character sheet.

   **Vofy managed credits:** the user installs/authenticates Vofy themselves. Never run
   `vofy login`, inspect credential files, or put status/credit output in SPEC/MEMORY/logs.
   First run the read-only checks:
   ```
   python ${GAME_TOOLS_DIR}/acquire_sprite.py preflight --model <chosen-model>
   vofy models <chosen-model>
   ```
   Read the live model capabilities before choosing `--image`, `--aspect-ratio`, or
   `--resolution`; do not hardcode a model or current price. Use the bundled pool only when
   that model supports image-to-image references. Pass the root directory once;
   `acquire_sprite.py` selects the matching spec and randomly samples three files. After
   step 1a's confirmation, submit exactly one synchronous paid task:
   ```
   python ${GAME_TOOLS_DIR}/acquire_sprite.py create \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|rest_site_option|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --model <chosen-model> \
     [--aspect-ratio <confirmed-ratio>] [--resolution <confirmed-resolution>] \
     [--reference ${STS2_API_SKILL_DIR}/reference/art-samples] \
     [--identity-reference <normalized-charui/select.png>] --yes
   ```
   `--yes` means the user approved this exact prompt/model/one-image spend. The tool reruns
   preflight, downloads into a unique empty directory, requires exactly one image, then
   calls `gen_sprite.py import` (including chroma for cut-out specs). It never parses Vofy
   stdout for a filename. On timeout or ambiguous output, inspect `vofy tasks --plain`;
   never auto-resubmit because the first task may already have spent credits.

   **BYO HTTP backend:** run the existing generator:
   ```
   python ${GAME_TOOLS_DIR}/gen_sprite.py generate \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|rest_site_option|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --config <path to art-backend.json> \
     --reference ${STS2_API_SKILL_DIR}/reference/art-samples
   ```
   `--reference` passes the shipped STS2 style samples (Layer 2 few-shot) — keep it on, and
   point it at the **root** `art-samples` dir (as shown). The tool auto-picks the matching
   established family or `character_select`/`character_background`/`character_icon`/
   `character_combat`/`character_rest` reference subdir and randomly samples three distinct files; families
   are never mixed. Backends
   that accept reference images (gpt-image edits or Gemini/nano-banana) imitate the
   game style far better, and plain text-to-image backends just ignore it.
   Add `--identity-reference <normalized-charui/select.png>` only for
   `character_combat`, `character_rest`, and `character_merchant`; omit it for
   `character_background`, `character_icon`, `character_energy`, `character_energy_large`, and
   `character_energy_text`.
   The tool POSTs to the user's backend, then chroma-keys (per spec — OFF for a full-bleed
   `card`/`event`/`rest_site_option`/Character selection-background, ON for the cut-out icon/body/energy specs) / fits /
   resizes to the exact contract size and writes every required path: one
   card/potion/enchantment/orb/monster/event/rest-site-option/Character main asset, two power files, or a
   relic's main/big/derived-outline triplet. `character_icon` similarly adds its derived
   outline beside the main PNG. Pass `--identity-reference` only for
   identity-sensitive Character body assets; palette-driven Character background/icon/
   Energy requests must omit it.
   **Local image:** use `gen_sprite.py import --input <file> ...`; for a magenta-backed
   relic/power/potion/enchantment/orb/monster or Character cut-out source add `--chroma`.
   After all required Character slots are normalized, validate and review them outside the
   runtime asset directory:
   ```
   python ${GAME_TOOLS_DIR}/character_art.py \
     --images-root <work dir>/<ModName>/images \
     --install-energy-templates \
     --out-dir <work dir>/art-review
   ```
4. **Unavailable/failure → bounded fallback, don't block.** A missing native image tool,
   native output with no local file, host-tool failure, missing Vofy/auth/credits,
   unsupported model flags, task failure/timeout, zero or multiple downloads, missing BYO
   config, or import failure must stop that route. Keep the placeholder unless the user
   explicitly selects BYO HTTP, Vofy, or local import instead. Never silently choose a paid
   backend or retry a possibly charged task. Record only the route/outcome in `MEMORY.md`,
   never account or credit output.
5. **Regenerate/tweak** means adjusting the subject/prompt, obtaining fresh approval, then
   rerunning the chosen acquisition + import. The `.pck` rebuild in `build.md` picks up
   whatever PNG is at the path — placeholder if none, the custom one if present.

Whether placeholder or generated, the `.pck` build (`build.md`) is what makes the art
reach the game — a code-only `dotnet build` won't (same rule as localization).

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
any Cmd choices, the state lifetime/reset/persistence (when present), which DRIVER body
the harness uses, and the **art outcome**
(placeholder, or generated `<slug>.png`/`big/<slug>.png` — and if generate was chosen
but fell back to placeholder, why). Mark `author and SelfTest` done in `PLAN.md`. Then go
to `build.md`.
