# M8.8 Surface Effect Composability Generalization Result

Date: 2026-08-13

Status: closed by explicit human-lead acceptance on 2026-08-13. Closure applies only to the
confirmed M8.8 scope and does not authorize M8.6, installation, game launch, commit, push,
publication, or release.

## Result

M8.8 refreshed the complete documented and relevant public RitsuLib `0.5.11` Mod-authoring
surface, resolved user-facing ownership, and made the human-confirmed WP1-WP5 scope authorable
through open-mod's normal DESIGN, SPEC, Author, Build, and SelfTest workflow. Authoritative source,
the committed Codex plugin payload, and the portable Agent Skills payload are synchronized.

The final scope deliberately defers Progression, post-run Badge, Settings, Telemetry, Multiplayer,
Update Check, WP6 asset/scene/animation/audio/shared-presentation generalization, WP7 named typed
interoperability generalization, and new integrations whose purpose is to connect another element
to any deferred group. Those decisions are product-scope deferrals, not claims that their public
APIs do not exist. Existing asset, presentation, audio, interoperability, Extra Badges, and M8.7
routes remain intact at their previous literal boundaries.

No new M8.8 shape was observed in a real game. Static source, compile probes, tests, and payload
synchronization establish authorability and API compatibility only.

## Inventory Basis

The inventory used the following pinned evidence:

- RitsuLib tag `v0.5.11`, commit `8a2eb7c756d926287078f953f2fac1d47ec014b4`;
- STS2 stable `0.107.1`, host commit `59260271`;
- Workshop item `3747602295`, RitsuLib manifest `0.5.11`;
- `STS2.RitsuLib.Compat.0.107.1` DLL SHA-256
  `6c2f65d2245207226aba80d3ea83b928871bd6e9fb7584d28b2669e10d335413`;
- all 25 pages in the current RitsuLib guide navigation;
- all 41 English RitsuLib pages in the pinned official tutorial checkout;
- all public RitsuLib source namespaces, registration routes, templates, callbacks, lifecycle
  events, commands, services, and utilities grouped by user-requestable capability family; and
- a metadata omission pass over 1,603 public or nested-public Compat types. Per-symbol output was
  intentionally not retained as a permanent product ledger.

The durable family-level inventory and ownership reasoning remain in
`games/sts2/experimental/M88_CAPABILITY_INVENTORY.md`.

## Implemented Scope

### Existing surface expansion and shared routes

Card, Character, Enchantment, Event, Keyword, Monster/Encounter, Orb, Potion, Power, and Relic
retain their established ownership. M8.8 added or completed shared authoring for:

- model capabilities, merge/subtract/replace behavior, clone/save/display state, and bounded
  owner lifecycle;
- typed lifecycle events, attached/saved state, Mod data stores, migrations, cache invalidation,
  and deterministic supplied-host or stable Mod RNG;
- dedicated per-hit attack, healing, Energy/Stars-gain, and maximum-hand-size services;
- Card before/after play, suppression, bounded free-play lifetimes, transform completion and
  carry-over, and localized type-text composition;
- exact model-hook reachability for Affliction, Modifier, and Run/Combat Global Effect streams;
  and
- truthful cross-surface composition without inventing a combined owner.

### New independent surfaces

- **Affliction:** combat-only Card attachment, amount/stacking, apply/remove/play lifecycle,
  capabilities/hooks, commands, text/tips, and optional overlay.
- **Modifier:** good/bad registration, deterministic placement, merged exclusions, new-run/load
  lifecycle, save identity, run/combat behavior, presentation, and selected Rest Site ownership.
- **Global Effect:** one registered Run or Combat singleton stream with scoped state, exact
  dispatcher reachability, neutral behavior, reset, and cleanup.
- **Rest Site:** standalone Run-singleton plus truthful Card/Relic/Modifier ownership under the
  existing singleplayer, free/fixed-Gold, preflight-before-mutation contract.
- **Act:** complete registered Act models with explicit force/uniform/weighted singleplayer entry,
  map RNG, room pools, scoped Encounter/Event/Ancient composition, localization, and checked assets.
- **Ancient:** Shared or Act-scoped registration, validity, deterministic option pools, native
  outcome/page completion, dialogue selection, localization, and checked presentation resources.
- **Reward:** owned dynamic reward type, typed payload reconstruction, claim/refusal semantics,
  blocking offer, combat-room insertion, successful-claim/continue lifecycle, and bounded linked
  reward sets.
- **Card Pile:** independent combat/run ownership, documented UI styles and anchors, visibility,
  native awaited movement, run persistence, hotkeys, localization, and ExtraHand behavior.
- **Runtime UI:** top-bar entry, Toasts, retained hotkeys, local Capstone screens, Catalog/search,
  floating windows, stable node attachments, Mod-scoped shell themes, and explicit cleanup.

WP8 added a representative composition in which an Event offers a Reward, the successful Reward
creates one exact Card, the same instance moves into a run-persistent Card Pile, and Runtime UI
shows the pile count and searchable Catalog. Event, Reward, Card Pile, and Runtime UI remain
independent owners.

## Deferred Scope And Retained Boundaries

The human lead explicitly deferred these whole capability families and every new integration to
them: Progression, post-run Badge, Settings, Telemetry, Multiplayer, and Update Check. WP6
asset/scene/animation/audio/shared-presentation expansion and WP7 named typed interoperability were
also deferred in full after WP1-WP5, including new integrations to either group. They are recorded
as Future Outlook rather than M8.8 closure work.

Existing routes in those domains were preserved. In particular, M8.8 did not remove existing art
profiles, Character presentation and bounded combat cues, Event presentation/VFX, rich-text
effects, Extra Badges, native audio fallbacks, vanilla visual overrides, or the existing rule that
cross-Mod use requires a named public contract and declared dependency.

The smallest retained technical boundaries include:

- creature-only advanced targeting, with no unsafe multi-target Potion approximation;
- no arbitrary rollback transaction for post-mutation Rest Site failure;
- no process-wide listener used to disguise a model-owned rule;
- no arbitrary object/Card/map targeting or global custom-target registration;
- no ungrounded registration, presentation host, or consumer-local substitute;
- no prompt-derived Harmony, reflection, Publicizer, IL, private API, or BaseLib dependency; and
- no framework bootstrap, patch infrastructure, diagnostics, generic wire protocol, or standalone
  low-level utility promoted into a player-facing surface.

## Verification Facts

### Framework-expressible

`yes` for the included public API shapes exercised by the pinned compile probes. The combined
probe project compiled against STS2 `0.107.1` and Compat/RitsuLib `0.5.11` with `0` warnings and
`0` errors. This is API and compiler evidence, not a generated-Mod Build or runtime result.

### Open-mod-authorable

`yes` for the confirmed WP1-WP5 scope. Each included family has an existing or accepted new
surface/shared route, normal Interview/SPEC/Author/Verify routing, exact API/lifecycle guidance,
focused requirement-to-authoring coverage, and structured SelfTest obligations. The authoritative
source and both generated payloads contain those routes.

### Game-observed

`no` for every newly generalized M8.8 shape. Historical observations retain only their original
version, owner, and scenario boundary; they do not transfer to RitsuLib `0.5.11` variants or new
compositions.

The following checks did not run:

- no generated M8.8 Mod Build or packaging run;
- no payload installation and no installed-skill execution;
- no game launch, Tier 1 load proof, or Tier 2 structured SelfTest;
- no save/load, profile switch, language-switch, or real lifecycle-dispatch proof;
- no headed UI, mouse, controller, focus, layout, drag/resize, theme, targeting, animation, VFX,
  audio, or subjective presentation review;
- no Reward claim/cancel/reload, Card Pile persistence/ExtraHand, Rest Site, Act/Ancient, Runtime UI,
  Affliction, Modifier, or Global Effect real-host behavior;
- no Multiplayer, telemetry, update service, macOS, or external-service proof; and
- no M8.6 fresh natural-language whole-skill acceptance.

## Checks Run

- Focused requirement-to-authoring suite: `8/8` passed.
- Focused model-hook/catalog suite: `25/25` passed.
- Focused payload-layout and thin-preflight suite: `15/15` passed.
- Full `games/sts2/tools/tests` regression: `244/244` passed after payload delivery.
- RitsuLib `0.5.11` combined compile probe: `0` warnings, `0` errors.
- Source, plugin, and portable `modmaker` and `sts2-api` roots: all six passed
  `quick_validate.py`.
- Python `compileall` passed for source tools, publish scripts, and both payload trees.
- `capability_preflight.py` itself has no M8.8 diff and remains limited to shipped-route and exact
  raw-hook silent-failure checks.
- Residual scans found no restored management/schema/trace validator and no new deferred-family,
  WP6, or WP7 authoring route/integration.
- All nine M8.7 generalized families and their literal evidence boundaries remain present.
- `git diff --check` passed.

## Payload Delivery

After explicit authorization, `publish.sh --plugin` and `publish.sh --portable` regenerated both
committed payloads. Repeated publication was byte-repeatable for each whole tree. Excluding the
existing portable-only `GENERATED.md` wrapper, authoritative-source projection, plugin, and
portable contain `211` identical relative paths and SHA-256 values.

Shared payload manifest SHA-256:

`3801af28bcf9b90e49a1341e8193a36d2c3e5beea2dd8ab1071d7c2d0f1d7c88`

Portable-only `GENERATED.md` SHA-256:

`653398fe2a62b77c86c7afb0aac3adcbc021a1acb245573eede6b1b2eda9bcac`

Each payload contains the same 14 maintained Python tools, includes only the sole thin preflight,
and contains no `__pycache__`, `.pyc`, or retired/replacement management validator. No installed
plugin or user Mod was modified.

## Close-Criteria Audit

- Complete `0.5.11` documentation/source/API/Compat inventory: satisfied.
- Included capability ownership and concrete exclusions/boundaries: satisfied.
- Six deferred product families and their new integrations absent: satisfied.
- WP6/WP7 expansion and new integrations absent; existing routes preserved: satisfied.
- Requirement, API compatibility, reachability, SelfTest guidance, and payload tests: passed.
- Sole thin preflight boundary: preserved.
- M8.7 capabilities and evidence boundaries: preserved.
- Active source and both payloads synchronized and repeatable: satisfied.
- Framework-expressible, open-mod-authorable, game-observed, and unrun checks stated literally:
  satisfied.
- Explicit human-lead acceptance and closure: satisfied on 2026-08-13.

The human lead accepted this result and closed M8.8 on 2026-08-13. This closure does not install a
payload, authorize a commit/push/release, close M8.7, or start M8.6.

## Files And Documents

Authoritative implementation lives under `games/sts2/skills/`, the model-hook collector/catalog,
focused tests, and the current capability graph. Repository-only research and compile probes live
under `games/sts2/experimental/`. Generated delivery is under `plugins/open-mod/skills/` and
top-level `skills/`.

Current status and future scope are recorded in `AGENTS.md`, `README.md`,
`documents/IMPLEMENTATION_PLAN.md`, `documents/PROJECT.md`, and
`games/sts2/tests/content-capability-graph.md`. No pre-existing result record was modified; the
history index now includes this record.
