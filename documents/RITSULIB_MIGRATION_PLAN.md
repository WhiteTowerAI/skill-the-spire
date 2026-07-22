# RitsuLib Migration Plan

> This is the execution plan for the project-wide BaseLib replacement. It deliberately
> precedes M7. Do not begin implementation from this document until the migration session
> confirms the repository state and the pinned RitsuLib stable asset.

## Outcome

Rebuild open-mod so a generated STS2 Mod uses RitsuLib as its only framework dependency on
the stable `0.107.1` host, while preserving the grounded M0-M6 capability boundary. Then
hand the repository to a separate RitsuLib expansion milestone before starting M7.

The migration is complete only when a fresh generated Mod loads with BaseLib absent and the
closest existing live suites prove the migrated behavior. A successful source build alone
does not close a phase.

## Current checkpoint - 2026-07-22

- **R0 complete:** environment/compat assets and the dependency migration matrix are frozen.
- **R1 complete:** authoring now starts from `sts2-content-semantic/v1` and routes selected
  surfaces through one lazy RitsuLib adapter.
- **R2 complete:** the open-mod-owned scaffold/build path pins
  `STS2.RitsuLib.Compat.0.107.1` `0.4.62`; an empty Mod loaded on stable `0.107.1` with
  BaseLib absent.
- **R3 complete:** Card, Relic, Potion, Power, Keyword, Enchantment, and Orb passed one
  RitsuLib-only `CombatPlayer` build/load/Tier 2 suite, each reached `selftest done`, and no
  fresh error block appeared. Active R3 recipes and generated payloads contain no BaseLib
  implementation path.
- **R4 not started:** only a read-only entry search occurred before session close; no
  Monster, Encounter, Event, or Character source was changed.

Next session starts at R4. Use `RITSULIB_MIGRATION_MATRIX.md` as the R0-R3 evidence record;
do not recreate those phases or restart M7.

## Working rules

- Work on `Henry's_cc`; do not merge to `main` or `Henry's_branch`.
- Do not commit until the human lead asks.
- Preserve unrelated dirty-worktree changes.
- Keep one armed harness Mod in the game at a time.
- Do not reopen completed M6 behavior canaries except to rebuild the closest proof against
  RitsuLib.
- Keep the stable host fixed at STS2 `0.107.1`; do not use the default beta-facing RitsuLib
  package by accident.
- Update source under `games/sts2/` and regenerate committed plugin/portable payloads;
  do not hand-edit generated payloads.

## Phase R0: Freeze the old contract

**Purpose:** create a clean comparison point before changing code.

- Record the current active support graph and the M0-M6 acceptance markers.
- Record the exact host, .NET SDK, BaseLib, Downfall, and RitsuLib baseline versions.
- Mark every active recipe/reference that names a BaseLib type, build target, namespace,
  manifest field, or proof assumption.
- Classify each item as `replace`, `rewrite`, `research-only`, or `historical`.
- Do not change runtime behavior in this phase.

**Gate R0:** a migration matrix exists for every current supported surface, every current
canary has an identified closest replacement proof, and the old plan remains reproducible.

## Phase R1: Define the framework-neutral contract

**Purpose:** prevent BaseLib names from leaking into the product-level Skill.

- Extract a common semantic envelope for content identity, registration, localization,
  effects, state/lifetime, presentation, fallback, and proof.
- Define the adapter inputs needed by each surface without embedding a framework class name.
- Decide where RitsuLib-specific source snippets live in the generator.
- Keep the existing interview/SPEC/PLAN/MEMORY resume model unchanged.
- Add a framework/version record to generated diagnostics.

**Gate R1:** a simple card and a simple relic can be described without BaseLib vocabulary;
the adapter can select RitsuLib implementation data from the same semantic SPEC.

### Consolidation targets

During R1, explicitly merge rather than duplicate these paths:

- one framework dependency/manifest generator;
- one model-registration adapter for pooled and standalone content;
- one asset-profile contract with per-surface fallback data;
- one framework/version diagnostic envelope used by build, load, and Tier 2 proofs;
- one capability matrix separating semantic support, framework support, and hosted evidence;
- one source location for RitsuLib compatibility gates and variant selection;
- one lazy reference-routing table instead of a full recipe branch for every framework.

BaseLib-specific recipes may remain in history, but they must not remain as a second active
implementation path after the migration.

## Phase R2: Replace scaffold and build packaging

**Purpose:** make the smallest possible RitsuLib-only Mod.

- Determine the exact `STS2.RitsuLib.Compat.0.107.1` compile-time reference and matching
  runtime asset.
- Author or adapt a minimal scaffold if RitsuLib does not ship an equivalent `dotnet new`
  template. Do not retain a hidden BaseLib template dependency.
- Replace project references, MSBuild targets, manifest generation, package-copy logic, and
  dependency validation.
- Generate a manifest with RitsuLib only and `min_game_version: 0.107.1`.
- Add an explicit diagnostic for missing/wrong compat variants.

**Gate R2:** an empty RitsuLib-only Mod builds, packages, appears in the stable game's Mod
list, and reaches the exact load marker with BaseLib absent.

## Phase R3: Port the low-risk content core

**Purpose:** establish the replacement path where RitsuLib is already broad.

Port and prove in this order:

1. Card and relic registration, localization, costs, effects, and placeholder art.
2. Potion and power registration, lifecycle, localization, and tooltip composition.
3. Keyword and enchantment text/behavior contracts.
4. Orb registration, icon/tooltip, and explicit combat fallback.

For each surface, remove duplicate BaseLib-specific branches instead of copying them and
adding a second condition. Reuse the nearest existing canary and record the exact structured
post-state proof.

**Gate R3:** the low-risk content suites build and load with RitsuLib only; no active source
path imports BaseLib.

## Phase R4: Port world content and Character Foundation

**Purpose:** move the larger model and presentation surfaces without broadening support.

- Port monster and encounter registration, move vocabulary, conditional sequencing, and
  static combat/bestiary fallback.
- Port normal Events, page/option localization, Cmd/selection/reward outcomes, bounded
  special combat, portrait assets, rich text, native presentation, and forced follow-up.
- Port Character registration, pools, starter deck/relic, loc keys, selection/run flow, and
  the current static presentation profiles.
- Recreate the five-layer full-energy and merchant/rest wrappers through RitsuLib's asset
  profile/runtime factories or a checked open-mod wrapper.
- Preserve all current unsupported Ancient, animation, materials, multiplayer, audio, and
  room-transition boundaries.

**Gate R4:** the closest `CombatEnemy`, `MapNode`, and Character Foundation suites pass Tier
  1/Tier 2 using RitsuLib only. Every custom visual either renders in the intended consumer
  or keeps its documented fallback.

## Phase R5: Port state, resources, and UI adapters

**Purpose:** replace the advanced mechanics without reintroducing an unbounded runtime.

- Map the current stateful relic cadence and save boundaries onto RitsuLib persistence or a
  small open-mod-owned holder.
- Use RitsuLib Secondary Resources for the current combat resource contract: nonnegative
  state, affordability, all-or-nothing spend, reset, card-hosted payoff, and bounded UI.
- Preserve the fixed icon+text control and text-only fallback; do not silently switch to a
  different native layout.
- Port the semantic ordered card buffer using normal Play -> Discard lifecycle. Do not
  resurrect retained-card CustomPile or `skipVisuals` workarounds.
- Keep the version/MVID-gated capability kernel only where RitsuLib and public STS2 expose no
  safe seam. Every adapter needs target, failure, conflict, and hosted proof diagnostics.

**Gate R5:** resource and buffer suites prove reset, payment, ordering, visible UI state, and
  second-combat behavior with no BaseLib dependency.

## Phase R6: Internalize small missing conveniences

**Purpose:** close useful gaps without making RitsuLib a second copy of BaseLib.

### Scry adapter

Implement an open-mod-owned Scry helper only if the migration needs it or the semantic
contract is selected by a test card. Use public `PlayerChoiceContext`, `CardSelectCmd`,
`CardPileCmd`, normal discard history/lifecycle, and a structured result. Keep modifier and
after-Scry hooks private to open-mod until cross-Mod interoperability is explicitly required.

Required proof before promotion:

- top-X selection overlay is visible;
- selected cards move to Discard and unselected cards retain order;
- zero, short, and full selection cases are correct;
- normal discard hooks/history fire once;
- the selector is correctly awaited;
- the chosen multiplayer context is either proven or explicitly restricted.

This closes the BaseLib Scry convenience gap without adding BaseLib to the dependency graph.

### Other helpers

Only add another helper when all of these are true: RitsuLib lacks a public equivalent, the
behavior is required by an existing supported contract, the implementation uses a grounded
game API, and one focused hosted proof can prove it. Do not create a generic compatibility
framework preemptively.

**Gate R6:** each internal helper has a narrow semantic contract, source attribution/license
handling where relevant, a checked fallback, and a focused proof.

## Phase R7: Regression, dependency, and packaging audit

**Purpose:** prove the migration as a product, not a collection of compiling files.

- Rebuild the closest existing acceptance suites one at a time.
- Run Tier 1 and structured Tier 2 checks with `selftest done` and no fresh error block.
- Remove BaseLib from the game's Mods directory and repeat the load/run proof.
- Search generated source, project files, manifests, package locks, and published payloads
  for `BaseLib`, `Alchyr.Sts2.BaseLib`, `BaseLib.dll`, and `BaseLib.pck`.
- Verify RitsuLib reports the stable `0.107.1` compat branch, not a beta variant.
- Test the failure message for a missing/wrong RitsuLib variant.
- Run publish, unit tests, Python compile checks, and `git diff --check`.

**Gate R7:** dependency audit is clean, the stable-host proof is green, and the migrated
source is the only active implementation path.

## Phase R8: Documentation and handoff

**Purpose:** make a fresh session start in the right project.

- Update `AGENTS.md` current status and active dependency language.
- Update active game-pack recipes, grounding rules, scaffold/build instructions, and
  capability references from BaseLib-first to RitsuLib-first.
- Keep completed BaseLib evidence in `documents/history/`; label it as pre-migration proof.
- Update `documents/PROJECT.md`, `documents/IMPLEMENTATION_PLAN.md`, and the content graph.
- Regenerate `plugins/open-mod/` and `skills/` from source.
- Write a short migration result record with exact versions, gates, residual gaps, and the
  first recommended expansion task.

**Gate R8:** a new session can read `AGENTS.md`, this plan, the migration spec, and the active
  game-pack entry point and immediately continue from the correct phase.

## Post-migration expansion: separate milestone

Do not mix these with parity work. Once R8 is complete, create a new expansion plan and
select one user-visible capability at a time. Recommended order:

1. Promote the proven Scry helper to a documented card recipe if its proof is complete.
2. Expand RitsuLib Secondary Resource authoring: richer payment choices, run-persistent
   resource contracts, and reusable resource UI profiles, each with its own live proof.
3. Add other RitsuLib-native content registrations or presentation profiles that reduce
   generated code without changing the semantic contract.
4. Revisit deferred motion/material/multiplayer/audio tracks only after their exact host
   consumers and fallbacks are grounded.
5. Start M7 proactive interview work after the migration and the first expansion slice are
   both stable, unless the human lead deliberately changes the order.

## New-session startup checklist

The session after the 2026-07-22 R3 checkpoint should:

1. Read `AGENTS.md`, `documents/RITSULIB_MIGRATION_SPEC.md`, this file, and
   `documents/RITSULIB_MIGRATION_MATRIX.md`.
2. Confirm branch `Henry's_cc`, clean/understood worktree, stable host `0.107.1`, and the
   pinned RitsuLib `0.4.62` compat variant.
3. Treat R0-R3 as closed evidence. Do not rebuild the empty scaffold or reopen the seven
   low-risk surfaces unless the closest R4 regression exposes a real cross-surface defect.
4. Inventory RitsuLib public Monster/Encounter APIs and asset profiles, port one combined
   vertical slice, and prove it through `CombatEnemy` before moving to Event.
5. Continue Event through `MapNode`, then Character Foundation/static presentation through
   the current Character hosts. Keep one armed harness Mod at a time.
6. Preserve the R3 dependency audit and all unsupported boundaries; do not start R5, R6,
   expansion work, or M7 early.
