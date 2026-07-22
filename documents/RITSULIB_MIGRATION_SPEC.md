# RitsuLib Migration Specification

> Status: active migration contract. Phases R0-R3 closed on 2026-07-22; Phase R4 is next.
> This document defines the target state and verified checkpoint, while
> `RITSULIB_MIGRATION_PLAN.md` owns execution order.
>
> Target host: Slay the Spire 2 stable `0.107.1` on Windows, with the matching
> `STS2.RitsuLib.Compat.0.107.1` build or a variant pack that contains `lib/0.107.1/`.
> Baseline currently reviewed: RitsuLib `v0.4.62`, BaseLib `v3.3.8`, Downfall `0.1.2`.

## 1. Decision

open-mod will move from a BaseLib-first runtime to a RitsuLib-first runtime. A generated
mod produced by the completed migration must require RitsuLib and must not require BaseLib.
Downfall remains a maintainer research baseline and is not a runtime dependency.

The migration is a compatibility and architecture project, not a new feature milestone.
The first obligation is to preserve the current grounded M0-M6 support boundary. New
RitsuLib features are considered only after that parity gate is closed.

Small missing conveniences, such as Scry, may be implemented as open-mod-owned source in
the generated mod. They must use the game's public command/lifecycle APIs where possible;
they must not reintroduce BaseLib as a hidden dependency.

## 2. Goals

1. Ship one generated Mod framework dependency: RitsuLib only.
2. Preserve the current user-facing behavior and honest unsupported boundaries.
3. Keep the natural-language interview, SPEC, art, build, repair, and verification workflow
   independent of the framework-specific implementation details.
4. Make framework-specific code easy to audit, replace, and re-ground when STS2 changes.
5. Reduce duplicated BaseLib assumptions by consolidating common semantic contracts and
   routing them through one RitsuLib adapter surface.
6. Leave a clean handoff for a later RitsuLib-based capability expansion.

## 3. Non-goals

- Do not start M7 proactive interview work during the migration.
- Do not claim vanilla-content editing, arbitrary Harmony patching, retained-card custom
  zones, alternative-energy replacement, production Character animation, multiplayer
  Character presentation, or audio merely because RitsuLib exposes a related API.
- Do not port all of Downfall. Use it to understand implementation depth and versioned
  contracts; only port a feature when it is required by the open-mod support boundary.
- Do not introduce `OpenMod.Runtime` as a shared binary before multiple independent
  generated consumers justify its install and versioning cost.
- Do not preserve BaseLib compatibility through a second mandatory dependency.

## 4. Target dependency contract

### Generated Mod

- Compile-time framework reference: `STS2.RitsuLib.Compat.0.107.1`.
- Runtime framework: RitsuLib's `0.107.1` compat DLL, either as the matching release asset
  or through the variant loader's `lib/0.107.1/` directory.
- Generated manifest: `dependencies` contains RitsuLib only; BaseLib is absent.
- `min_game_version` remains the formal host version `0.107.1`.
- No generated project copies a BaseLib DLL, PCK, package reference, namespace, or template
  rule.

### Research and build environment

- `baselines/BaseLib-StS2` remains available for historical comparison and license-aware
  source research, but it is not copied into generated projects.
- `baselines/downfall` remains a reference implementation and is not copied into generated
  projects.
- `baselines/STS2-RitsuLib` remains the current RitsuLib research checkout.
- Every RitsuLib update must re-check the compat target, final runtime DLL, generated
  manifest, and one stable-host load proof.

## 5. Capability parity contract

The migration must preserve these current surfaces before any expansion work begins:

| Surface | Required migration result | Notes |
|---|---|---|
| Card, relic, potion, power | New RitsuLib registration/templates, localization, costs, effects, and art paths | Preserve existing Tier 1/Tier 2 behavior |
| Keyword and enchantment | RitsuLib registration/display path with the current text-only or icon fallbacks | Keep behavior and tooltip composition |
| Orb | RitsuLib registration, icon, tooltip, and combat-body fallback contract | No automatic animation promotion |
| Monster and encounter | RitsuLib registration and move vocabulary, static body, bestiary fallback | Preserve deterministic move proofs |
| Event / World Node | RitsuLib event registration plus the current Cmd/page/selection/reward/combat/VFX boundary | Preserve one-combat-per-instance and forced-follow-up limits |
| Stateful mechanics | RitsuLib persistence or open-mod-owned state adapter with explicit lifetime | Preserve reset and save claims; do not broaden them |
| Character Foundation | RitsuLib character registration, pools, starter deck/relic, loc, and selection/run flow | Re-ground every static consumer |
| Character presentation | RitsuLib asset profiles/factories or a checked open-mod wrapper | Preserve fallback-first behavior and proof per consumer |
| Combat resource | RitsuLib Secondary Resources for the current auxiliary-resource contract, or a self-contained adapter | This does not authorize replacing native Energy |
| Ordered semantic buffer | Native Play -> Discard lifecycle plus open-mod state/UI | Retained custom card zones remain unsupported |
| Art pipeline | Framework-neutral `gen_sprite.py import` contract | Asset acquisition is not tied to BaseLib |
| Self-test and repair | Existing hosted scenarios and structured markers | Add framework-version markers to diagnostics |

### Explicit BaseLib convenience gaps

BaseLib 3.3.8 supplies a ready-made Scry command, Scry dynamic variable, and Scry-specific
modifier/completion hooks. RitsuLib `v0.4.62` has no matching public Scry API in its source.
The migration may close this gap with an open-mod-owned helper that:

1. accepts the real `PlayerChoiceContext`;
2. takes the top X cards from the draw pile;
3. uses the native card-selection overlay;
4. moves selected cards through the normal discard lifecycle and history;
5. returns a structured result; and
6. optionally dispatches an open-mod-owned Scry hook contract.

The helper is not promoted as a general cross-Mod Scry standard until a headed proof covers
the selector, pile order, lifecycle, zero/short piles, and multiplayer context. Scry is a
small migration-owned adapter, not a reason to retain BaseLib.

## 6. Architecture rules

### Semantic layer first

The interview and SPEC describe intent, state, lifetime, interaction, presentation, and
proof obligations. They must not emit BaseLib type names. A framework adapter translates
that semantic contract into RitsuLib templates, registrations, commands, and asset profiles.

### One adapter boundary

Keep RitsuLib-specific details in a small, searchable surface:

- registration and public-entry rules;
- model/template bases;
- localization and asset profile wiring;
- combat resource/payment;
- persistence and lifecycle subscriptions;
- optional patch/capability seams;
- manifest/build packaging;
- verification diagnostics.

Do not create separate handwritten branches for every content type when a shared contract
can express the difference as data. Keep lazy, surface-specific references so a simple card
request does not load Character, Event, or multiplayer details.

### Generated source before shared runtime

For the first migration, source-level helpers are preferred over a new runtime binary. This
keeps generated Mods self-contained and avoids giving users a second open-mod runtime to
install. Extract a shared runtime only after two or more independent generated consumers
need the same stable API and its versioning/cleanup contract is proven.

### Fallbacks and proof

An RitsuLib path, successful build, or model registration is not presentation evidence.
Every migrated consumer must retain its checked fallback and be re-proven in the closest
real host. A capability is not promoted merely because RitsuLib documents an API.

## 7. Compatibility and cleanup requirements

- Remove BaseLib from source templates, generated manifests, project references, package
  restore logic, analyzer assumptions, and active skill instructions.
- Replace BaseLib-specific wording in active recipes with RitsuLib wording or framework-
  neutral semantic language. Historical records remain historical and may mention BaseLib.
- Centralize the stable host target `0.107.1`; do not silently compile the default beta-facing
  RitsuLib package.
- Record the selected compat branch and host version in self-test output.
- Fail clearly when the required RitsuLib compat asset is missing or the host branch is
  mismatched.
- Keep unrelated user changes and all completed M0-M6 evidence intact.

## 8. Acceptance criteria

The migration is complete only when all of the following are true:

1. A fresh empty generated Mod builds with only RitsuLib and loads in the real stable host.
2. A dependency audit finds no BaseLib package, DLL, PCK, manifest dependency, or generated
   namespace in the migrated source path.
3. The current card/relic/potion/power/keyword/enchantment/orb, monster/encounter, Event,
   Character Foundation, resource, buffer, art, and self-test contracts each have a
   corresponding RitsuLib implementation or an explicit unchanged gap.
4. The closest existing hosted suites are rebuilt one at a time and reach Tier 1/Tier 2
   with `selftest done` and no fresh error block.
5. At least one run succeeds with BaseLib absent from the game's Mods directory.
6. A negative dependency check proves that a missing or wrong RitsuLib `0.107.1` variant
   fails with an actionable diagnostic rather than silently selecting a beta DLL.
7. The published plugin and portable skill are regenerated from source and pass the normal
   Python, compile, and diff checks.
8. Only after this gate is closed may a new RitsuLib capability expansion begin.

## 9. Implementation checkpoint - 2026-07-22

R0-R3 are complete. The exact inventory, package hashes, registration mappings, hosted
markers, and residual risks live in `RITSULIB_MIGRATION_MATRIX.md`.

Resolved decisions:

- open-mod owns one minimal scaffold instead of using an Alchyr/BaseLib template;
- compile-time dependency is `STS2.RitsuLib.Compat.0.107.1` `0.4.62` and runtime selection
  requires the matching `lib/0.107.1/STS2-RitsuLib.dll` variant;
- generated manifests depend only on `STS2-RitsuLib >= 0.4.62` and target
  `min_game_version: 0.107.1`;
- framework-specific registration, public-entry, asset-profile, diagnostics, and packaging
  details are concentrated in the RitsuLib adapter/scaffold/tooling boundary;
- `RitsuCardProof` was the disposable combined `CombatPlayer` proof for the seven R3
  surfaces; its durable evidence is the migration matrix, not a shipped runtime project.

Verified R3 result:

- Card, Relic, Potion, Power, Keyword, Enchantment, and Orb build and load with RitsuLib
  only; strict Tier 2 reached `selftest done` for every surface with no fresh error;
- the final build had zero warnings/errors, the generated manifest contained no BaseLib
  dependency, and source/proof/generated-payload audits found no active R3 BaseLib path;
- 73 Python tests, compile checks, both publish modes, and `git diff --check` passed;
- custom presentation remains bounded: the Orb keeps its Frost combat-body/SFX fallback,
  and historical visible Keyword/Enchantment/Orb evidence is regression input until the
  closest RitsuLib visual host is rerun.

Current handoff:

- no R4 source was changed in this checkpoint;
- begin R4 with Monster + Encounter API/asset mapping and the `CombatEnemy` proof, then
  Event / World Node through `MapNode`, then Character Foundation/static presentation;
- preserve every Ancient, animation, materials, multiplayer, audio, vanilla-editing,
  alternative-Energy, retained-zone, and room-transition boundary;
- defer the Scry implementation decision to R6 unless an earlier migrated semantic
  contract actually selects it.
