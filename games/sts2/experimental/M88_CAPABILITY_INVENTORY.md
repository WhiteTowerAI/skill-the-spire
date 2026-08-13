# M8.8 capability inventory and ownership research

This repository-only record makes the selected M8.8 research phase resumable. It is organized by
user-requestable capability family, not by public symbol. It is neither a generated-project
contract nor capability implementation. The human lead confirmed a revised implementation scope
on 2026-08-13, then explicitly deferred WP6 and WP7 after WP1-WP5 completed. WP8 source/static
closeout and authorized plugin/portable payload delivery are complete. The human lead accepted the
final result and closed M8.8 on 2026-08-13; the durable record is
`documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`.

## Pinned evidence and coverage

- RitsuLib checkout: tag `v0.5.11`, commit
  `8a2eb7c756d926287078f953f2fac1d47ec014b4`.
- Installed stable host: `release_info.json` reports `v0.107.1`, commit `59260271`.
- Installed official Workshop runtime: item `3747602295`, manifest `0.5.11`.
- Stable Compat variant: marker `0.107.1`, DLL SHA-256
  `6c2f65d2245207226aba80d3ea83b928871bd6e9fb7584d28b2669e10d335413`.
- Current RitsuLib guide: the guide hub and all 25 pages in the complete
  `docs/valaxy.config.ts` sidebar.
- Official Package semantics: all 41 English RitsuLib pages in the pinned
  `SlayTheSpire2ModdingTutorials` checkout at `5a9110b3c1b1c428f9f349e51cd4a155266b92e3`.
  Its two remote-only commits change BaseLib and beta-migration pages, not RitsuLib pages.
- Public-source pass: `RitsuLibFramework`, content-pack and direct registries, templates,
  registration attributes, callbacks, lifecycle events, and every public source namespace were
  grouped by user outcome.
- Compat omission pass: the repository-only `m88-api-inventory` metadata reader found 1,603
  public/nested-public types in the stable DLL without loading it. Its per-symbol JSON output is
  deliberately not retained; the family outcomes below are the durable result.

## Progress and gate

- [x] Active documents and immutable-history boundary read.
- [x] Exact source, host, runtime, Compat, and documentation identities refreshed.
- [x] Every official guide/tutorial area and relevant public API namespace assigned a family-level
  outcome.
- [x] Existing ten surfaces, shared routes, proposed new surfaces, retained boundaries, and
  exclusions resolved for scope confirmation.
- [x] Real-host, headed, multiplayer, persistence, and external-service proof needs identified.
- [x] Human-lead scope-confirmation report prepared from this record.
- [x] Human lead revised and confirmed the implementation scope: defer Progression, post-run
  Badge, Settings, Telemetry, Multiplayer, Update Check, and their new cross-family interactions.
- [x] Implement and verify the final confirmed source capability work packages below one domain at
  a time.
  - [x] Work package 1: shared model effects, capabilities, lifecycle, state, RNG, Card play/text,
    and composition.
  - [x] Work package 2: Affliction, Modifier, Global Effect, and Rest Site ownership.
  - [x] Work package 3: Act and Ancient.
  - [x] Work package 4: Reward and Card Pile.
  - [x] Work package 5: Runtime UI and included interaction routes.
  - [x] Work package 6 disposition: deferred in full; no new asset/scene/animation/audio/shared-
    presentation expansion or integration; preserve all existing routes.
  - [x] Work package 7 disposition: deferred in full; no new named typed interoperability route or
    integration; preserve all existing routes.
  - [x] Work package 8 source/static closeout: revised-scope cross-surface composition, source
    tests, capability graph, results, and residual audit.
- [x] Work package 8 delivery gate: regenerated and verified both payloads after explicit human-
  lead authorization.
- [x] Final result record created under explicit authorization and submitted for human-lead
  acceptance.
- [x] Human lead explicitly accepted the result record and closed M8.8 on 2026-08-13.

M8.8 is closed. Do not repeat its inventory, source closeout, payload delivery, or result record
unless a newly selected Package changes a pinned input. Do not add a deferred-family, WP6, or WP7
route indirectly through another owner.

### Work package 1 result - 2026-08-13

- Added shipped authoritative routes for model capabilities, lifecycle/state/RNG, dedicated shared
  effect services, and Card play/free-play/transform/type-text lifecycle.
- Routed those references through `sts2-api/SKILL.md`, all truthful existing surfaces, and their
  recipes. Keyword remains vocabulary/tooltip-only; Character has state/display capability but no
  implied owner-hook dispatch; Card/Relic/Potion/Power/Orb/Enchantment/Monster rules cannot use a
  process-wide listener as an ownership shortcut.
- `capability_preflight.py` is unchanged. These APIs fail visibly at C# compile or require hosted
  behavioral proof, so no new fact met all three thin-preflight admission criteria.
- Focused requirement-to-authoring tests passed `3/3`. They protect route selection, owner mapping,
  phase/order, neutral behavior, cleanup/removal, transform, deterministic RNG boundaries, and
  SelfTest obligations.
- The probe project compiled against STS2 `0.107.1` and Compat/RitsuLib `0.5.11` with `0` warnings
  and `0` errors. This establishes framework/API compatibility only.
- Verification facts: framework-expressible = yes for the probed public shapes;
  open-mod-authorable = yes through the new shipped source routes; game-observed = no. Real
  lifecycle delivery, save/load/profile switching, Card play/transform/UI, and effect dispatch
  remain unrun and require the separately authorized real-host/headed gates.

### Work package 2 result - 2026-08-13

- Added authoritative Affliction, Modifier, Global Effect, and independent Rest Site surfaces and
  recipes. Expanded the shared Rest Site route from Card/Relic ownership to truthful standalone
  Run-singleton and selected mutable Modifier ownership without changing its singleplayer,
  free/fixed-Gold, preflight-before-mutation, no-rollback, or headed-proof boundaries.
- Corrected the inventory's Affliction model: it is combat-only state attached to one concrete
  Card, applied by `CardCmd.Afflict<T>` / `AfflictAndPreview<T>` and removed by
  `CardCmd.ClearAffliction`; it is not a run affliction.
- Added `affliction` and `modifier` to the generated model-hook surface projection. Added exact
  `global-effect-run` and `global-effect-combat` projections from each hook's dispatcher iterator
  (including both subscribers when a Run-with-child-Combat iterator composes the streams),
  so thin preflight catches a compile-clean wrong-stream singleton. Rest Site hooks remain
  route-owned rather than raw declarations; `capability_preflight.py` itself remains unchanged.
- Confirmed good/bad Modifier registration, integer before/after-list placement, overlapping
  mutual-exclusion group merge, new-run versus load callbacks, and saved run-model identity.
  Confirmed that a registered `HookedSingletonModel` selects exactly one Run or Combat stream and
  must keep mutable state on the concrete run/combat/player rather than on its canonical identity.
- The focused work-package compile probe covers Affliction registration/application/preview/clear,
  good/bad Modifier ordering and exclusivity, Run/Combat singleton registration, and standalone
  Rest Site option/owner hook signatures. It compiled against STS2 `0.107.1` and Compat/RitsuLib
  `0.5.11` with `0` warnings and `0` errors.
- Focused hook/requirement tests passed `13/13`; they include positive Run/Combat reachability and
  rejection of compile-clean wrong-stream Global Effect declarations. The generated catalog check
  reports `68` hooks and remains current.
- Verification facts: framework-expressible = yes; open-mod-authorable = yes through the shipped
  source surfaces/routes; game-observed = no for all new shapes. Real Card attachment/overlay,
  custom-run/daily selection and save/load, singleton dispatcher/reset, standalone/Card/Modifier
  Rest Site owners, localization, icons, controller input, and visuals remain unrun and require
  separately authorized real-host/headed verification. The historical Relic Rest Site observation
   remains literal and does not transfer to the new owners.

### Work package 3 result - 2026-08-13

- Added authoritative Act and new-Ancient surfaces and recipes, plus normal Interview, SPEC,
  Author, Verify, API-index, adapter, and capability-graph routing. New Ancient authoring is kept
  distinct from ordinary Events, existing-Ancient overrides, and Character dialogue in existing
  native Ancient scenes.
- Confirmed that `.Act<T>()` registers but does not make a run enter the Act. Generated Acts select
  exactly one explicit singleplayer force/uniform/weighted entry policy; all candidate predicates
  reject multiplayer, weighted pools declare the existing-Act baseline explicitly, and
  `AllowInRandomActList` remains false because it has no singleplayer predicate.
- Confirmed every `ModActTemplate` still owes complete gameplay members and nonempty weak,
  regular, elite, and Boss runtime pools. The probe uses the complete Overgrowth resource family
  with an exact numbered Act 1 chest override; the folder-derived chest path is not trusted.
- Confirmed exactly-one Shared/Act-scoped Ancient registration, `IsValidForAct` filtering,
  mutable-event `Rng`, distinct all/initial option sets, `Func<Task>` wrapping of `Done()`, and
  localization-driven first-visit-ever, exact-Character, then `ANY` dialogue.
- Focused requirement-to-authoring tests passed `5/5`. The Act/Ancient compile probe passed against
  STS2 `0.107.1` and Compat/RitsuLib `0.5.11` with `0` warnings and `0` errors.
- Verification facts: framework-expressible = yes; open-mod-authorable = yes through the shipped
  source surfaces/routes; game-observed = no. Real Act selection/transition, map and every room
  family, save/load identity, Ancient dialogue/options/choice history, localization, assets, UI,
  controller, animation, and audio remain unrun and require separately authorized real-host/headed
  verification.

### Work package 4 result - 2026-08-13

- Added independent Reward and Card Pile surfaces and recipes, then routed both through Interview,
  SPEC, Author, Verify, the API index, adapter, and capability graph. Card Pile keeps the existing
  complete `reference/card-piles.md` Package instead of duplicating or narrowing it to historical
  ExtraHand cases.
- Confirmed Mod-owned Reward registration through `ModRewardRegistry.For(modId).RegisterOwned`,
  `ModCustomReward` claim/refusal semantics, default description/icon/order behavior, typed
  source-generated JSON payload reconstruction, blocking `RewardsCmd.OfferCustom`, current-combat
  `AddExtraReward`, and the successful-claim/continue lifecycle events. Factories rebuild pending
  state only; they never grant the outcome.
- Confirmed linked `ChooseOne`/`TakeAll` sets with ordered children, no nesting, one same-player
  owner, unique/not-already-linked instances, at most 128 children, 256 KiB serialized characters
  per child, and 4 MiB per set. Multiplayer-specific synchronization remains deferred and no
  connection to it was added.
- Confirmed Card Pile's independent combat/run owner, RitsuLib run persistence, all documented UI
  styles/anchors/views/hotkeys/visibility, exact-instance awaited native movement, and ExtraHand
  native-play ownership. No shadow persistence or consumer patch was introduced.
- `capability_preflight.py` is unchanged: these type/lifecycle rules fail visibly at C# compile or
  require real-host behavior and do not satisfy the thin preflight's silent-failure criteria.
- Focused requirement-to-authoring tests passed `6/6`. The combined Reward/Card Pile probe compiled
  against STS2 `0.107.1` and Compat/RitsuLib `0.5.11` with `0` warnings and `0` errors; generated
  build output was cleaned.
- Verification facts: framework-expressible = yes; open-mod-authorable = yes through the new
  shipped source routes; game-observed = no for M8.8 Reward and `0.5.11` Card Pile variants. Real
  reward claim/refusal/continue/reload, linked-set behavior, combat insertion, pile scope/movement/
  persistence, localization, UI, controller, and ExtraHand behavior remain unrun and require the
  separately authorized real-host/headed gates. Historical `0.5.4` ExtraHand observations retain
  their literal boundary and do not transfer to this package result.

### Work package 5 result - 2026-08-13

- Added the independent Runtime UI surface and recipe, then routed it through Interview, SPEC,
  Author, Verify, the Mod Maker/API skill indexes, adapter, capability graph, and focused
  requirement-to-authoring coverage.
- Confirmed top-bar registration and null-player/per-frame provider rules, queued and tracked Toast
  lifecycle, retained runtime-hotkey registration/rebind/disposal, local-only Capstone replacement,
  Catalog construction/limits/detail ownership, floating-window geometry/content ownership,
  deterministic bounded search expansion/invalidation/disposal, stable public node attachment, and
  Mod-scoped shell-token registration/consumption.
- The route explicitly does not add Settings, Progression, post-run Badge, Telemetry, Multiplayer,
  Update Check, or an interaction to one of those deferred families. The Card Piles reference was
  also corrected so normal public commands do not imply M8.8 Multiplayer authoring or proof.
- `capability_preflight.py` remains unchanged: these API/type/lifecycle rules either fail visibly at
  C# compile or require real-host behavior and do not satisfy the thin preflight admission criteria.
- The focused requirement-to-authoring suite passed after making the shell-theme public entry point
  directly reachable. The Runtime UI probe compiled against STS2 `0.107.1` and Compat/RitsuLib
  `0.5.11` with `0` warnings and `0` errors.
- Verification facts: framework-expressible = yes; open-mod-authorable = yes through the shipped
  source surface/recipe; game-observed = no. Real top-bar/input/Toast/Capstone/window/Catalog/search/
  attachment hosts, localization, focus, controller, layout, animation, drag/resize, theme response,
  and cleanup remain unrun and require separately authorized real-host/headed verification.

### Work package 8 source/static result - 2026-08-13

- Added one representative composition scenario in which an Event offers a Reward, the successful
  Reward creates one exact Card, the same Card instance moves through the native awaited command
  into a run-persistent Card Pile, and Runtime UI exposes that pile's count and searchable Catalog.
  Event, Reward, Card Pile, and Runtime UI remain independently owned; no combo surface or hidden
  owner was introduced.
- Corrected the semantic owner list so Act, Ancient, Reward, Card Pile, and Runtime UI remain
  reachable through normal ownership and composition guidance.
- The focused requirement-to-authoring suite passed `8/8`. The focused model-hook/catalog suite
  passed `25/25`; its singleton reachability expectation now includes the collector's existing
  `GLOBAL_EFFECT_SURFACE_ITERATORS` without weakening catalog, dispatcher, or preflight behavior.
  The full surviving source suite passed `244/244`.
- The complete probe project compiled against STS2 `0.107.1` and Compat/RitsuLib `0.5.11` with `0`
  warnings and `0` errors. Both authoritative skill validators and Python `compileall` passed.
- Residual audit found no new WP6/WP7 surface or recipe, no new authoring route or integration for
  any deferred family, no deleted existing route, and no restored management schema/trace/
  validator. `capability_preflight.py` has no diff and remains thin. All nine M8.7 generalized
  families remain present in the Mod Maker guidance and capability graph.
- Verification facts for the confirmed WP1-WP5 scope: framework-expressible = yes for the pinned
  compiled public shapes; open-mod-authorable = yes through the authoritative source routes;
  game-observed = no for every newly generalized M8.8 shape. Existing historical observations keep
  only their original literal boundary. No payload installation, game launch, generated-Mod Build,
  Tier 1, Tier 2, save/load, controller, UI/headed, animation, audio, multiplayer, macOS, or gameplay
  verification ran.

### Work package 8 payload result - 2026-08-13

- After explicit human-lead authorization, regenerated the committed plugin and portable payloads
  only through `publish.sh --plugin` and `publish.sh --portable`; no installed plugin or user Mod was
  modified. Repeated publication produced the same whole-tree content for each payload.
- Authoritative-source projection, plugin, and portable contain `211` identical shared relative
  paths and SHA-256 values. Their shared manifest digest is
  `3801af28bcf9b90e49a1341e8193a36d2c3e5beea2dd8ab1071d7c2d0f1d7c88`. Portable retains its one
  existing `GENERATED.md` wrapper file with SHA-256
  `653398fe2a62b77c86c7afb0aac3adcbc021a1acb245573eede6b1b2eda9bcac`.
- All six source/plugin/portable skill roots passed `quick_validate.py`; Python `compileall`, the
  focused payload-layout/preflight suite (`15/15`), and the full source suite (`244/244`) passed.
  Both payloads contain the same `14` maintained tools, include the sole thin
  `capability_preflight.py`, contain no Python cache output, and contain no retired or replacement
  management/schema/trace validator.
- Payload synchronization is static delivery evidence only. It adds no game observation: no
  install, launch, generated-Mod Build, Tier 1, Tier 2, headed/UI/controller, save/load, animation,
  audio, multiplayer, macOS, or gameplay check ran.
- The human lead accepted the final history result and closed M8.8 on 2026-08-13. Commit, push,
  release, installation, game launch, and M8.6 remain separately gated; closure authorized none of
  them.

## Family-level inventory outcomes

### Content models, registration, and composition

The current Card, Character, Enchantment, Event, Keyword, Monster/Encounter, Orb, Potion, Power,
and Relic surfaces remain the natural owners of those model families. Their authoring must expand
to the full public `0.5.11` behavior relevant to each owner, rather than remaining limited to old
examples or observed cases.

Public registration also exposes independently requestable families that current surfaces cannot
truthfully own. Act, Affliction, Ancient, good/bad Modifier, custom Reward, custom Card Pile, and
Singleton/global effects are included through the accepted new surfaces below. Achievement, Badge,
Story/Epoch/Timeline/unlock progression, Settings, Multiplayer, Update Check, and Telemetry were
accounted for by the inventory but are deferred by explicit product decision. Registration style
is implementation detail: generated Mods keep one readable content-pack source of truth unless a
selected public feature requires its direct registry.

Shared content-authoring knowledge includes stable public entries and model identity, pool
registration, Card tags, dynamic enum values, placeholder entries, trash-heap and Ancient option
extensions, registration inheritance/order/freeze timing, manifests, model cloning, and
`ModelCapability` attach/merge/subtract/clone/save behavior. Shared Card/Relic/Potion pools remain
cross-owner content composition rather than separate products.

### Combat and model-owned effects

The common effect route must cover the normal public model hooks plus the `0.5.11` effect APIs that
older open-mod guidance did not completely expose:

- Card before/after-on-play, type-text composition, free-next-play/turn/combat/current-play
  bindings, transform callbacks and carry-over, playability/result-pile/property/cost/title/
  description/overlay/glow/hover contributors, and computed DynamicVars;
- per-hit attack before/after callbacks with mutable hit inputs and resolved results;
- additive, multiplicative, and late healing modification;
- after-Energy-gained and after-Stars-gained callbacks;
- maximum-hand-size early/late modification;
- health-bar forecast lanes and visual grafts;
- Relic visibility rules and explicit refresh;
- native temporary Power helpers;
- source-aware custom Card/Potion targets and live execution-time resolution;
- Power, Relic, and Monster Intent extra corner labels;
- model/capability right-click behavior for Card, Relic, Power, Potion, and Orb; and
- M8.7 secondary resources, native Energy/Star costs, multiple computed Card values, bounded state,
  Rest Site ownership, forced Events, Monster/Encounter graphs, Character starts, and Event
  acquisition/shake without narrowing or upgrading their evidence status.

Prefer a real model or `ModelCapability` owner. A `HookedSingletonModel` is the public owner for a
genuinely global run/combat rule. Process-wide listener registration is not a shortcut for effects
that have a truthful model owner. Each component retains its own trigger, guard, ordering, neutral
result, visible text, and SelfTest assertion when effects compose.

### State, identity, lifecycle, and deterministic behavior

Shared references must distinguish:

- runtime object state through `AttachedState`;
- game-serialized model state through `SavedAttachedState`, `ModelSavedData`, and capability JSON
  state, including clone and migration policies;
- run-wide and per-player state through `RunSavedData`, including write policy, commit timing,
  migrations, and save/load; pre-run lobby and multiplayer synchronization are deferred;
- global/profile/in-memory JSON slots through `ModDataStore`, including explicit save, cache
  invalidation, profile switching, format migration, and optional Steam Cloud participation;
- stable model/public IDs and clone notification; and
- Mod-scoped deterministic run/player RNG rather than `System.Random`.

Lifecycle subscriptions cover framework/model bootstrap, game tree, profile/save, run/room/act,
combat/turn/card/resource, reward/inventory, and unlock events. Replayable subscriptions, one-shot
subscriptions, disposal, queued command completion, and obsolete-event replacements belong in one
shared lifecycle route. Persistence is shared capability ownership; a saved concept that is itself
the product belongs to its included model or Global Effect owner rather than to a generic storage
surface. Settings, Progression, and Multiplayer ownership are deferred and must not be
approximated through storage.

### Text, assets, scenes, animation, audio, and presentation

Shared presentation knowledge includes both native localization tables and RitsuLib `I18N`, exact
entry/Event/Ancient keys, bilingual parity, keyword hover tips, LocString placeholder resolution,
custom SmartFormat sources/formatters, DynamicVars, custom rich-text effects, model title
resolution, and language-change refresh.

Asset profiles/fallbacks cover every included registered model profile exposed by `0.5.11`,
including Act, Affliction, Modifier, Ancient, Rest Site, Character, creature, Encounter, and
existing surfaces. The Badge asset profile is accounted for but deferred with Badge. Godot C#
script registration, `.tscn`/factory ownership, node attachments, catalog/window controls,
creature visual cues, animation state machines, and cleanup remain public routes. Audio
includes loose files, FMOD banks/events/GUID mappings, buses, one-shots, loops/music, and lifecycle
cleanup. Visual, animation, controller, input, audio balance, and subjective quality remain headed
human judgments even when source and Build pass.

### Interaction and runtime UI; Settings deferred

Settings is a real documented product family: fluent or documented schema registration; global/profile/
in-memory/projected/callback bindings; toggles, text/password/multiline, integer/float sliders,
choices, color, key/input binding, lists, image/info/header/button/custom controls; visibility,
enabled/read-only host predicates; page/sidebar order; reset/copy/paste; localization; and main/
pause-menu hosts. It and all cross-family settings bindings are deferred by the confirmed scope.

Runtime UI is another composable family: top-bar buttons and hover tips, Toasts and actions,
runtime hotkeys and Steam Input exposure, capstone screens, floating windows, catalog list/grid and
detail views, search-expansion providers, node attachments, and coherent shell themes. These share
one UI surface because their normal use is one Mod-owned player workflow. Card Piles remain
separate because they have distinct registration, persistence, and host lifetimes. Runtime UI must
not grow a settings page, settings binding, update prompt, telemetry consent flow, or multiplayer
control as part of M8.8.

### Progression, rewards, and world flow

Progression includes Achievement models, Story/Epoch models, story-epoch binding, timeline
columns/placement/icons, model/content epoch requirements, Card/Relic/Potion pool unlocks,
Character unlocks, run/win/ascension/elite/boss/count rules, and reveal events. Badge remains a
separate run-summary family: it computes rarity and obtained state from a serialized run/player,
with win and multiplayer filters plus an optional icon. Both families and new unlock/progression
interactions from Card, Character, Relic, and Potion are deferred. M8.7's already implemented
existing-vanilla availability/epoch routes remain preserved and are not reclassified as new M8.8
progression authoring.

Act owns its assets, random-list eligibility, forced/uniform/weighted act entry, and scoped
Encounter/Event/Ancient composition. Ancient owns its special dialogue, option pools, deterministic
RNG, act/shared validity, scene/presentation, and public augmentation of existing Ancient options.
Reward owns dynamic type registration, icon/text, selection/cancellation, deterministic side
effects, serialized payload reconstruction, and reward-room insertion. Card Pile owns combat/run
scope, persistence restoration where selected, all documented UI styles/anchors, visibility,
open/view behavior, native movement, ExtraHand behavior, hotkeys, and localization.

### Typed interop, Multiplayer, updates, and telemetry deferred

Public typed Mod/assembly interop was accounted for as a distinct user-requestable family, but WP7
and all new integrations to it are deferred in full. M8.8 adds no shared interop route, SPEC
vocabulary, implementation, test, or proof. Existing interoperability capabilities remain intact
at their prior literal boundary: they require a named public external API, declared dependency/load-
order behavior, and exact compile/runtime identity; generated code does not perform reflection,
discover private members, or invent an optional Mod contract.

Multiplayer was identified as a possible system surface: managed synchronized game actions; high-level
typed messages, request/reply, host-authoritative sync, required-capability checks, and config-topic
sync; plus the documented `RunSavedData` lobby/per-player synchronization. The whole family and all
connections from included surfaces are deferred, so M8.8 does not author or test these routes.

Update checks and telemetry are real documented Mod behaviors. They were identified as separate
possible surfaces because release discovery and player-data collection have different intent,
lifecycle, consent, and proof ownership. Update Check
requires a maintained mirrored/self-hosted HTTP(S) manifest, release page, and Workshop-source
policy. Telemetry requires human-authored data purpose/categories, visible consent text, a fixed
HTTPS applicant endpoint, no secrets in the Mod, queue/error policy, and source-specific consent
for cross-Mod contributions. Both families and their connections to Runtime UI, persistence, or any
other included surface are deferred.

## Ownership resolution

### Existing surfaces

- **Card:** Card model/pools/tags, costs, DynamicVars, targeting, free play, transforms, hand
  emphasis, model capabilities, on-play/type-text effects, right-click, and Card-owned shared
  routes.
- **Character:** typed pools/starts, character assets/scenes/animation/audio, combat cues,
  secondary-resource theme, and Character-owned content composition.
- **Enchantment:** Enchantment model, asset/text lifecycle, mandatory enchant replacements, model
  capabilities, and every reachable shared effect with exact owner guards.
- **Event:** ordinary/combat Events, option/outcome/presentation/VFX, forced mappings, acquisition,
  and shared Event extensions; custom Ancient identity belongs to Ancient.
- **Keyword:** keyword registration, native/mod hover tips, Card-keyword semantics, and shared
  localization/SmartFormat knowledge.
- **Monster/Encounter:** Monster moves/HP/visuals, Encounter rosters/placement/assets, health-bar
  presentation, and Intent labels; Act identity belongs to Act.
- **Orb:** Orb model, passive/evoke/turn behavior, value/hover display, capabilities, right-click,
  targeting where applicable, and assets.
- **Potion:** Potion model/pools, use/targeting/cancellation, capabilities, right-click, and reachable
  shared effects.
- **Power:** Power lifecycle/stacking/temporary wrappers, capabilities, extra label, combat effects,
  health-bar presentation, and right-click.
- **Relic:** Relic lifecycle/pools/visibility/capabilities, extra labels, right-click, and Relic-owned
  shared routes.

### Accepted new surfaces

Each proposal has a public/fixed `0.5.11` route. The vocabulary below is player-facing SPEC
vocabulary, not a new schema.

- **Act:** a complete playable world chapter. Route: `ModActTemplate`, `.Act<T>()`, act-entry pool
  and scoped-content registrations. Vocabulary: placement policy, eligibility/weight/priority,
  Encounter/Event/Ancient sets, assets/backgrounds/chest/map/Rest Site. Related: Monster/Encounter,
  Event, Ancient. Boundary: deterministic supplied RNG and registered referenced content. Proof:
  real act transition, map/rooms, combat, chest, and Rest Site; headed for all visuals.
- **Affliction:** a combat-only condition attached to one concrete Card, with behavior, tips, and
  overlay. Route: `ModAfflictionTemplate`, `.Affliction<T>()`, `CardCmd.Afflict<T>` /
  `AfflictAndPreview<T>` / `ClearAffliction`, model hooks/capabilities. Vocabulary: application
  source, Card validity, integer amount/stacking, attached triggers, apply/play/remove lifecycle,
  keywords, overlay. Related: Card, Global Effect, and presentation. Boundary: one attached
  Affliction type per Card and only combat-reachable public hooks. Proof: real application,
  attached Card play/removal/combat reset plus headed overlay.
- **Modifier:** a selectable good/bad run modifier. Route: `ModModifierTemplate`, good/bad
  registrations, sort order, mutually-exclusive groups, model hooks. Vocabulary: polarity,
  availability/exclusion, effect, lifetime, icon/order. Related: Global Effect and Rest Site.
  Boundary: no invented setup-screen host. Proof: real modifier selection, new run, effects, and
  headed icon/list.
- **Ancient:** a shared or Act-scoped Ancient encounter. Route: `ModAncientEventTemplate`,
  `.SharedAncient<T>()`/`.ActAncient<TAct,T>()`, `AncientOption<T>`. Vocabulary: validity, dialogue
  groups/speakers, deterministic option pools, outcomes, scene/colors/icons. Related: Character,
  Event, Act. Boundary: public option/dialogue lifecycle only. Proof: real Ancient `MapNode`, every
  selected option/dialogue branch, localization, and headed presentation.
- **Reward:** a custom reward option. Route: `ModRewardRegistry`, `ModCustomReward`, dynamic reward
  type registration. Vocabulary: grant context, description/icon, selection/cancel behavior,
  deterministic outcome, payload/save reconstruction. Related: Card/Relic/Event/combat rewards.
  Boundary: side effects and reconstruction must remain deterministic. Proof: real reward screen,
  claim/cancel, leave, and reload. Multiplayer integration is deferred.
- **Card Pile:** an independently registered pile. Route: `ModCardPileRegistry`/`.CardPileOwned`,
  `CardPileCmd`. Vocabulary: scope, UI style/anchor, visibility/open behavior, movement rules,
  persistence, ExtraHand behavior, hotkey/text/icon. Related: Card, Runtime UI, persistence.
  Boundary: run-persistent contents require explicit save/restore; no retained Card zone disguised
  as ordinary state. Proof: matching combat/run hosts, movement and reload; headed/controller for UI.
- **Runtime UI:** a Mod-owned screen/workflow composed from top-bar, Toast, hotkey, screen/window,
  catalog/search, node attachment, and theme APIs. Route: their public registries/services and Godot
  scenes/factories. Vocabulary: entry point, host/lifetime, layout/content/action, close/back/focus,
  search, notification, input, theme. Related: Card Pile and all included presentation owners.
  Boundary: custom shell theme only for a coherent multi-control identity; no arbitrary injection
  into an unregistered host; no deferred-family UI or binding. Proof: every selected host with
  cleanup/resizing; headed/controller.
- **Global Effect:** a rule not owned by an obtainable model. Route: registered
  `HookedSingletonModel` with explicit Run or Combat stream, lifecycle events, model capabilities,
  and public global effect APIs only when no model route exists. Vocabulary: scope, trigger, guard,
  target, order, state/reset, effect/text/presentation. Related: every effect owner. Boundary: one
  truthful lifecycle, neutral behavior outside it, no process listener as hidden ownership. Proof:
  nearest real run/combat host plus reset/cleanup edges.
- **Rest Site:** an independently requested Rest Site option, while preserving Card/Relic and newly
  reachable truthful owners. Route: `ModRestSiteOptionTemplate` plus the route-owned
  `TryModifyRestSiteOptions`/`ShouldDisableRemainingRestSiteOptions`; standalone ownership lowers to
  a Run `HookedSingletonModel`. Vocabulary: owner/availability, affordability, cost, preflight,
  outcome, repeat rule, stay/leave, title/icon. Related: Card, Relic, Modifier, Global Effect.
  Boundary: all choices/failure checks before first mutation; no arbitrary rollback transaction.
  Proof: real Rest Site state matrix and headed controller/icon review.

### Deferred future surfaces

Progression, post-run Badge, Settings, Multiplayer, Update Check, and Telemetry have grounded public
routes but are not M8.8 surfaces. Their public facts above remain inventory evidence only. M8.8 does
not ship their surface routing, SPEC vocabulary, recipe/reference guidance, implementation, tests,
or proof, and does not add connections to them from any accepted owner. Reconsidering one requires a
new explicit product-scope decision and its own lifecycle and verification contract.

## Retained boundaries and exclusions

### Retained product boundaries

- Custom Card/Potion targeting remains creature-only and source-aware; multi-target Potion and
  arbitrary object/Card/map targeting still lack a grounded complete lifecycle.
- A Rest Site operation may compose public effects only when all failure-prone choices/checks occur
  before the first mutation. There is no public rollback transaction for arbitrary post-mutation
  cancellation.
- Existing Cross-Mod interop keeps its named-public-contract and declared-dependency boundary. WP7
  adds no new authoring route or integration, and guessed members, private access, or arbitrary
  runtime discovery remain prohibited.
- Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, and their new
  cross-family interactions are deferred by explicit human-lead product decision.
- Custom shell themes require a coherent Mod-owned UI experience. This prevents global appearance
  changes unrelated to the requested product and does not authorize a deferred Settings surface.
- M8.7's hard boundaries remain until an M8.8 work package proves a broader public lifecycle; all
  existing generalized variants keep their literal game-observed or game-unobserved facts.

### Excluded public areas

- **RitsuLib patching, Harmony, private access, dynamic patches, transpilers, IL helpers, and
  original-IL inspection:** generated use directly violates the repository's hard prohibition.
- **Reflection settings providers, BaseLib/JmcModLib/ModConfig mirrors, and runtime reflection
  interop:** generated reflection and BaseLib dependencies are prohibited; Settings itself is also
  deferred from M8.8.
- **Raw progress bridge:** this is transaction/recovery infrastructure for replacing the game's
  raw progress document, not a stable semantic Mod-data operation. Progression is deferred, while
  `ModDataStore` covers ordinary included Mod-owned state without rewriting vanilla progress.
- **Sidecar wire/envelope/opcode allocation, binary headers, chunking/compression, handshake,
  transport, reachability discovery, packet traces, and traffic counters:** Multiplayer is deferred
  in full; these lower-level facilities are additionally framework/protocol infrastructure rather
  than a user behavior.
- **Debug log viewer, dev-console/diagnostic commands, debug-tools pages, Card/compendium PNG
  exporters, and diagnostic relay internals:** these are developer/maintainer inspection and export
  tools, not shipped player behavior or normal SelfTest evidence.
- **Speculative-execution sessions and generic JSON patch/canonicalization/pointer helpers as
  standalone products:** they have no player host or semantic outcome. Author may use an ordinary
  public helper internally only when a confirmed owner behavior actually needs it.
- **Framework bootstrap, compatibility shims, patch registries, internal auto-registration
  discovery, diagnostics/logging internals, and embedded framework assets:** framework
  implementation, not generated-Mod capability ownership.

Common public utilities such as `WeightedList`, dynamic enum registries, resource-path helpers,
materials, I18N, file operations, saved-state/migration helpers, and node factories are not
excluded; they belong in the shared route that owns the concrete user behavior rather than in a
utility surface.

## Verification boundary

No M8.8 gameplay or host proof has run. The included WP1-WP5 shapes are framework-expressible under
the pinned compile probes and open-mod-authorable through their shipped authoritative source
routes. None becomes game-observed until that exact shape runs in STS2 `0.107.1` with RitsuLib
`0.5.11`. Deferred families and WP6/WP7 remain inventory facts only and gain no new M8.8 authoring
claim.

- Focused compile fixtures are required for every materially distinct registration/template,
  callback signature, included UI binding, and persistence shape used by the implementation
  packages.
- Behavior-level developer tests must protect ownership, ordering, neutral/edge behavior,
  persistence/cleanup, requirement-to-code ingredients, and structured SelfTest verification.
- Real game plus headed review is required for all included new models, Act/Ancient, Reward, Card
  Pile, Rest Site, UI/search/windows/themes, right-click/controller, and targeting. Existing asset,
  scene, animation, rich-text, audio, and interoperability proof keeps its literal historical
  boundary; WP8 neither broadens those claims nor requires new WP6/WP7 proof.
- Save/load and profile-switch hosts are required for included persisted model/run/profile state.
  Language switching must resolve and restore both `eng` and `zhs` consumers.
- Build/static/source/payload checks never count as Tier 1, Tier 2, headed, multiplayer, save/load,
  external-service, or gameplay proof. Tier 1/Tier 2, game launch, installation, and headed review
  require separate human-lead authorization.

## Confirmed implementation work packages

Implement and verify one independently testable domain at a time:

1. shared model effects, capabilities, lifecycle, state, RNG, text, and composition;
2. missing content models: Affliction, Modifier, Global Effect, and Rest Site ownership;
3. world content: Act and Ancient;
4. Reward and Card Pile;
5. Runtime UI and included interaction routes;
6. deferred by explicit human-lead decision: assets/scenes/animation/audio and shared-presentation
   expansion, including new cross-family integrations;
7. deferred by explicit human-lead decision: named typed interoperability and new integrations;
8. full cross-surface compositions, capability graph/results, source tests, then separately
   authorized payload delivery.

Each package performs exact API/lifecycle research, SPEC vocabulary and owner routing, concise
recipe/reference implementation, focused compile probes, behavior tests, capability-graph and this
record's progress update, then its nearest verification before moving on. Preflight changes only
if a newly confirmed silent-failure fact independently passes all three admission criteria.

## Scope confirmation decision

On 2026-08-13 the human lead confirmed the existing-surface expansions, shared ownership, Act,
Affliction, Modifier, Ancient, Reward, Card Pile, Runtime UI, Global Effect, and Rest Site surfaces,
the retained boundaries, and the revised package order. The lead explicitly deferred Progression,
post-run Badge, Settings, Telemetry, Multiplayer, Update Check, and every new interaction with
those families.

After WP1-WP5 completed, the human lead explicitly revised M8.8 again: WP6 asset/scene/animation/
audio and shared-presentation expansion and WP7 named typed interoperability are deferred in full,
are no longer closure conditions, and receive no new integrations from other elements. Existing
asset, presentation, audio, and interoperability capabilities must remain intact. WP8 revised-scope
source/static closeout was selected directly and is complete; authorized plugin/portable payload
delivery is also complete.

Authoritative capability implementation, payload synchronization, final reporting, human
acceptance, and closure for the confirmed scope are complete. Proof Mods, installation, game
launch, Tier 1/Tier 2, headed review, M8.6, commit, push, and publication retain their separate
authorization gates.
