# AGENTS.md

Repository guidance for coding agents working in open-mod.

## Project

open-mod is a free, open-source Codex plugin that turns a non-programmer's description into a
working game Mod. Slay the Spire 2 (STS2) is the first supported game. Read
`documents/IMPLEMENTATION_PLAN.md` before substantive work. Completed evidence under
`documents/history/` is immutable history, not current instruction.

## Current Status

`0.7.0` is the unreleased RitsuLib-only development baseline for STS2 stable `0.107.1` and
RitsuLib `0.5.11`. The BaseLib migration, M6.5-M6.7, M7, M8.0-M8.3, and M8.5 are closed.
Their exact evidence and exceptions remain in `documents/history/`.

M8.7 Product Boundary Generalization closed by explicit human-lead acceptance on 2026-08-14 after
its authoritative source and both payload forms were implemented and its result record completed.
Preserve its nine generalized product families and their independent `framework-expressible`,
`open-mod-authorable`, and `game-observed` facts. Do not reimplement or narrow them. Its durable
record is `documents/history/M87_PRODUCT_BOUNDARY_GENERALIZATION_RESULTS.md`.

M8.8 Surface Effect Composability Generalization closed by explicit human-lead acceptance on
2026-08-13 after its inventory, WP1-WP5 implementation, WP8 source/static closeout, and authorized
plugin/portable payload delivery completed. Its result and literal verification boundaries are in
`documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`. Progression, post-run Badge,
Settings, Telemetry, Multiplayer, Update Check, WP6 asset/scene/animation/audio/shared-presentation
expansion, WP7 named typed interoperability, and new interactions with those deferred groups remain
Future Outlook. Preserve all asset, presentation, audio, and interoperability routes that already
existed before or were implemented in WP1-WP5; do not retract or reimplement them. This does not
narrow M8.7's existing availability routes or the unrelated Power/Relic/Intent Extra Badges
feature. `documents/IMPLEMENTATION_PLAN.md` owns the exact closed scope and boundaries.

M8.9 Ordinary Effect Primitive Coverage completed its authoritative-source/static stage and its
separately authorized plugin/portable payload delivery on 2026-08-14. Its audit, shared lowering
reference, truthful surface projections, grouped compile probes, three authoring smoke scenarios,
and generated payload projections are complete; payload repeatability/parity and repository static
validation passed. M8.9 remains open for human review, a durable result record, and explicit
closure. Do not regenerate or install a payload, run the game, create an acceptance Mod, record
results, close M8.9, or start M8.6 without the corresponding later instruction.

M8.6 is the final clean installed whole-skill acceptance. M8.7 and M8.8 are closed, but M8.6 has
not been selected and still has no request, host, or execution contract; it also waits for
explicit M8.9 closure. Do not start it
automatically. Do not install a payload, launch the game, create an acceptance Mod, commit, push,
or publish without explicit instruction.

## Current Workflow

The generated-project workflow is deliberately small:

```text
human idea
  -> concise DESIGN.md
  -> implementable SPEC.md
  -> capability_preflight.py
  -> scaffold
  -> author + SelfTest
  -> build
  -> Tier 1
  -> Tier 2 / SelfTest
  -> headed human review when needed
  -> direct report from actual results
```

`DESIGN.md` records only human intent, confirmed decisions, current scope, and explicit `Not Now`
items. It does not contain machine-readable coherence, deliverable, impact, settlement, or repair
management contracts, and it does not require management IDs.

`SPEC.md` is the single implementation work order. Write concrete content, trigger, target,
conditions, values, order, state/lifetime, player-facing text and presentation, selected support
routes, and exact autotest scenarios. Keep simple Mods simple. Do not duplicate DESIGN or maintain
parallel scope, evidence, or surface ledgers.

The `## Implementation` section selects shipped routes and, only for raw model-hook participation,
declares the hook selection:

```markdown
- Support: `recipes/card.md`
- Hook: modify_damage_multiplicative | surface: power | shape: value | route: reference/model-hook-participation.md
```

Run exactly one pre-Author checker:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

It checks only facts that are mechanically exact, invisible to C# Build, and capable of producing
unsupported or silently ineffective code:

- each selected recipe/reference file exists in the shipped support pack;
- each selected hook exists in the pinned model-hook catalog;
- the cited route declares that hook;
- the declaration shape matches the catalog;
- route-owned hooks use their owning route; and
- the selected surface is in the dispatcher's authorable listener set for that hook.

Do not expand this preflight into Markdown/schema validation, ordinary field completeness, C# API
type checking, manifest/resource/localization validation, runtime lifecycle proof, visual review,
or evidence accounting. Recipes and references guide authoring; Scaffold/Build own static project
checks; real-host SelfTest owns behavior; people own visual, controller, animation, and subjective
judgment.

Existing projects may keep old metadata. Ignore it and resume from the current human-readable
meaning. Do not force a migration. A revised current operation adopts the small current format.

`PLAN.md` is a plain stage checklist. `MEMORY.md` records technical discoveries, stable IDs/keys,
commands/results, and repair attempts. Do not mirror DESIGN/SPEC state across files. On failure,
identify the observed difference, fix the artifact that owns it, clear any no-longer-valid stage
result, and rerun the nearest affected check. A different player-visible result returns to DESIGN
and SPEC for acceptance; a missing or broken shared route blocks consumer authoring until repaired
or narrowed.

## Source Ownership

Authoritative source lives under `games/sts2/`:

- `games/sts2/skills/modmaker/` owns routing and the generation stages;
- `games/sts2/skills/sts2-api/` owns lazy design references, recipes, API contracts, and errors;
- `games/sts2/tools/` owns scaffold, build, launch, log, art, and the thin preflight;
- `games/sts2/tests/` owns the current capability graph and verification guidance; and
- `games/sts2/experimental/` is repository-only research excluded from payloads.

`plugins/open-mod/` and top-level `skills/` are generated payloads. Never hand-edit them. After
authoritative source validation and explicit delivery authorization, regenerate them through
`publish.sh --plugin` and `publish.sh --portable`, then check repeatability, parity, and payload
layout.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and the `STS2.RitsuLib.Compat.0.107.1` API baseline at
  RitsuLib `0.5.11`.
- Each scaffold pins the validated local Compat DLL version and hash it compiles against. Runtime
  manifests depend only on `STS2-RitsuLib >= 0.5.11` while generated code stays inside the
  `0.5.11` authoring/API baseline.
- Runtime discovery accepts a validated game-local install or official Steam Workshop item
  `3747602295`, with exact host/compat identity checks.
- Generated projects have no framework `PackageReference`. The scaffold supplies bundled
  Godot.NET SDK imports and Build resolves game/runtime assemblies locally.
- Generated Mods must not reference, package, or depend on BaseLib. Do not restore Alchyr/BaseLib
  snippets.
- `baselines/STS2-RitsuLib` is maintainer research, not generated-project input.
- `baselines/decomp` is maintainer-only research. Never copy, compile, package, or ship decompiled
  code; private implementation does not establish a supported route.
- Official tutorials establish intended Package semantics. Exact APIs and lifecycle behavior come
  from the pinned RitsuLib `0.5.11` source/API and Compat metadata.

## Supported Boundary

The authoritative inventory is `games/sts2/tests/content-capability-graph.md`. Preserve its product
capabilities when simplifying workflow. Missing proof means unobserved, not automatically
unsupported; a confirmed public/API/lifecycle problem is recorded as the smallest exact
limitation.

Generated code may use the pinned public STS2/RitsuLib APIs, ordinary C#/BCL, Mod-owned helpers and
state, and already maintained fixed Adapters. Never generate prompt-derived Harmony, reflection,
Publicizer, or IL. A requested operation with no maintained public/fixed route blocks rather than
receiving a consumer-local approximation.

M8.7's generalized families remain authorable with their documented hard boundaries:

- secondary resources and bounded payment/UI;
- Monster move graphs, Encounter composition, and HP ranges;
- Character starting fields;
- Card- or Relic-owned Rest Site options;
- multiple computed Card values;
- reusable bounded state;
- bounded forced Event mappings;
- new-Card Star costs; and
- bounded Event acquisition/shake profiles.

Newly generalized variants remain game-unobserved until their exact real-host cases run. Do not
relabel source/static evidence as game proof.

## Localization And Art

Mods without localization tables remain language-neutral. Once any table exists, generated Mods
require both `eng` and `zhs`, identical table/key sets, identical SmartFormat token multisets, and
nonempty values. DESIGN and SPEC own the exact bilingual text. Build checks the static contract;
Tier 2 switches through both languages, resolves real consumers, and restores the original
language. Translation quality is human-owned.

Art normalization facts live in `gen_sprite.SPECS`, `character_art.CHARACTER_ART_BUNDLE`, and their
generated `art-contract-sts2-0.107.1.json` projection. Never hand-edit that catalog. Generated art
must pass through `gen_sprite.py import`; runtime wiring belongs to the selected RitsuLib asset
profile or exact visual provider. Placeholder is the default unless the user chooses a callable
image route. Do not silently select a paid backend.

## Verification

Verification reports what actually ran:

- Build proves the project compiles/packages under the pinned static contract.
- Tier 1 proves the exact load marker, framework/host/compat identity, and no fresh error block.
- Tier 2 runs the arg-gated `SelfTest.cs` in the real STS2 host, drives the selected scenario, waits
  for queued behavior, asserts exact structured post-state, and requires `selftest done`.
- `played`/`fired`/`used` logs are diagnostics only. They never establish a Tier 2 pass.
- Headed review owns images, UI, mouse/controller interaction, animation, and subjective quality.
- The final report directly names Build, Tier 1, Tier 2, and headed results. An unrun check is
  reported as unrun; it is never hidden behind a completion ledger.

Keep verification proportional. Use the nearest maintained host (`CombatPlayer`, `CombatEnemy`,
`MapNode`, real Rest Site, or `RunStart`/Character). Use a fresh natural-language acceptance Mod
only when the active plan or human lead explicitly selects a full-pipeline gate. Run one armed
harness Mod at a time and preserve unrelated user Mods.

Historical results keep their literal versions and evidence boundaries. In particular, older
`0.5.4` proof does not become `0.5.11` runtime evidence, and static/payload checks do not become
macOS, Tier 1, Tier 2, or gameplay proof.

## Tests

Keep tests that protect actual product behavior and artifacts: scaffold/build/profile/manifest,
localization, art, catalogs, packaging, payload layout, capability existence and hook reachability,
vanilla routes, load/log verification tools, and modest requirement-to-authoring scenarios.

Do not recreate tests that only enforce prose, heading names, management schemas, bidirectional ID
ledgers, repair state, milestone wording, or evidence tables. A test should protect a supported
authoring route, generated artifact, static build boundary, or real verification mechanism.

Use UTF-8 explicitly for multilingual validators:

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

## Git And Scope

Check `git status` before editing. Preserve unrelated dirty/untracked work. Stage only explicit
intended paths when asked to commit. A planned milestone is not authorization to execute it, and
closing one Package does not start another. Never reset, clean, commit, push, publish, install, or
launch without the corresponding instruction.

## Active Documents

- `documents/PROJECT.md`: current product and architecture.
- `documents/IMPLEMENTATION_PLAN.md`: active Package gates and work authorization.
- `documents/BASELINE_RESEARCH.md`: current dependency/research basis.
- `games/sts2/tests/content-capability-graph.md`: exact supported/limited/unsupported inventory.
- `games/sts2/tests/README.md`: current test and real-host verification ownership.
- `documents/history/README.md`: index of completed evidence only.
