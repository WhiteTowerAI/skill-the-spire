# open-mod project

## Product

open-mod is a free, open-source Codex plugin that turns a non-programmer's description into a
working game Mod. Slay the Spire 2 is the first supported game. The strategy is one game deep,
then a reusable platform once independent consumers justify shared abstractions.

The product combines adaptive design collaboration with grounded implementation. It asks only
material questions, records human intent separately from the exact implementation work order,
authors against pinned public/fixed routes, builds the Mod, and reports real verification results
literally.

## Release State

`0.7.0` is an unreleased RitsuLib-only development baseline for STS2 stable `0.107.1` and
RitsuLib `0.5.11`. BaseLib is absent from generated projects. M6.5-M6.7, M7, M8.0-M8.3, and
M8.5 are closed; their detailed results and exceptions live under `documents/history/`.

M8.7 Product Boundary Generalization is implemented in authoritative source and both payload
forms, but remains open pending its result record and explicit human closure. Its nine generalized
families remain part of the product boundary and must not be narrowed or reimplemented.

M8.8 Surface Effect Composability Generalization is paused and unimplemented. Its previous
trace/schema-oriented draft has been replaced in the active plan with a simplified future plan:
refresh the RitsuLib `0.5.11` effect surface, place durable knowledge in concise
recipes/references, extend the sole thin preflight only when all three admission criteria hold,
and prove requirement-to-code plus autotest readiness with behavior-level tests. It still requires
a refreshed guide/source/API audit and explicit human confirmation before implementation.

M8.6 remains the final clean installed whole-skill acceptance. It is ineligible until M8.7 and
M8.8 close and the human lead selects the exact request, host, and execution contract. No new
acceptance run, payload installation, commit, push, GitHub release, or game launch is implied by
the current source state.

## User Experience

A user describes a Mod in ordinary language. The skill resumes unfinished work when present,
otherwise chooses a fast, co-design, or revision route and asks only questions that change the
result materially.

The active workflow is:

```text
idea
  -> concise DESIGN
  -> implementable SPEC
  -> thin capability authenticity/reachability preflight
  -> Author + SelfTest
  -> Build
  -> Tier 1
  -> Tier 2 / SelfTest
  -> optional headed human review
  -> direct evidence-bounded report
```

A complete narrow request keeps a zero-question fast path. Character work lazily loads pinned
native foundation facts and proposes one exact starter shape before asking for deck detail.
Co-design may compare alternatives and preserve deliberate departures, but it must label pinned
facts, observed conventions, creative decisions, and open playtest hypotheses distinctly.

## Artifact Boundary

`DESIGN.md` contains the human-owned product meaning:

- the intended player experience;
- confirmed creative and scope decisions;
- the current playable slice; and
- explicit `Not Now` items.

It contains no machine-readable coherence, deliverable, impact, settlement, repair, or evidence
management contracts. Design quality is a human judgment, not a Markdown validator result.

`SPEC.md` is the only implementation work order. It records concrete content, triggers, targets,
conditions, values, ordering, state/lifetime/reset behavior, bilingual text and presentation,
selected recipe/reference routes, and the exact autotest scenarios required for the current
behavior. Simple Mods stay compact.

`PLAN.md` is a plain stage checklist. `MEMORY.md` stores technical discoveries, stable resolved
IDs/keys, exact commands/results, and repair attempts. Existing projects may retain old metadata;
the workflow ignores it and does not force migration.

## Thin Preflight

Author runs one checker before writing source:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

It verifies only facts that a compiler cannot detect and whose violation would produce unsupported
or silently ineffective code:

- selected support routes exist in the shipped pack;
- selected hook capabilities exist in the pinned catalog;
- the cited route declares the hook;
- hook shape matches the catalog;
- route-owned hooks are not authored as raw participation; and
- the selected surface belongs to the dispatcher's authorable listener set.

It does not validate prose, Markdown headings, ordinary fields, business rules, C# signatures,
manifest/resources/localization, runtime state, presentation, evidence status, or project stage.
Those remain owned by recipes/references, Scaffold/Build, real-host SelfTest, and headed review.

## Architecture

- `games/sts2/skills/modmaker/`: routing, DESIGN/SPEC, scaffold, authoring, build, verification,
  repair guidance, and direct reporting.
- `games/sts2/skills/sts2-api/`: lazy design references, pinned recipes/API contracts, catalogs,
  and diagnostic signatures.
- `games/sts2/tools/`: scaffold, build, launch, log, art, catalog, and thin preflight tooling.
- `games/sts2/tests/`: current capability graph and verification ownership.
- `games/sts2/experimental/`: maintainer research excluded from shipped payloads.
- `plugins/open-mod/`: generated Codex plugin payload.
- `skills/`: generated portable Agent Skills payload.

Authoritative edits happen under `games/sts2/`. Both payloads are regenerated through
`publish.sh`; they are never hand-edited.

## Runtime Profile

Generated Mods target STS2 `0.107.1` and the RitsuLib Compat `0.5.11` authoring/API baseline.
Scaffold pins the exact validated local Compat DLL version and hash used to compile. Runtime
manifests depend on `STS2-RitsuLib >= 0.5.11`; a newer local compile input does not raise that
minimum while generated code stays inside the baseline.

Generated projects have no framework `PackageReference`. The scaffold supplies Godot.NET SDK
imports and resolves STS2, RitsuLib, GodotSharp, Harmony, and other required assemblies from the
validated local game/runtime. Runtime discovery accepts a checked game-local install or official
Workshop item `3747602295`. BaseLib, Alchyr templates, maintainer decompiles, and research
checkouts are never generated-project dependencies.

## Product Boundary

Support, authorability, and observation are separate facts:

- `framework-expressible`: the pinned public/fixed route can express the operation;
- `open-mod-authorable`: the shipped recipes/references fully guide its implementation and proof;
- `game-observed`: its exact declared shape ran successfully in the real host.

Missing runtime proof does not automatically make a public capability unsupported. Conversely,
static source or Build success is not game observation. The exact inventory and narrow limitations
live in `games/sts2/tests/content-capability-graph.md`.

Generated code may combine the pinned public STS2/RitsuLib APIs, ordinary C#/BCL, Mod-owned helper
types/state, and maintained fixed Adapters. It must not invent prompt-derived Harmony, reflection,
Publicizer, or IL. A missing or broken shared route blocks authoring rather than inviting a local
approximation.

M8.7 generalized these nine families without claiming runtime observation for every new shape:
secondary resources; Monster move graphs/Encounter composition/HP ranges; Character starting
fields; Card- or Relic-owned Rest Site options; multiple computed Card values; reusable bounded
state; bounded forced Event mappings; new-Card Star costs; and bounded Event acquisition/shake
profiles.

## Design Intelligence

The design layer distinguishes pinned facts, observed native conventions, creative decisions, and
open hypotheses. Balance uses a Mod-forward preference: favor a clearly rewarding working value,
while constraining values that erase choices, setup, costs, ordinary opposition, or produce
deterministic, self-funding, or unbounded loops. This is a creative posture, not a fixed percentage
or proof of fun.

Coherence review is conversational and proportional. It examines only selected mechanics, naming,
localization, visuals, Event text, and Character identity. Deliberate tension may remain when the
user accepts it. No validator decides that a design is coherent, complete, fun, or balanced.

## Localization And Presentation

A Mod with no localization tables is language-neutral. Once any table exists, `eng` and `zhs` are
both required with identical table/key sets, identical SmartFormat token multisets, and nonempty
values. Build checks the static files. Tier 2 changes languages through the real localization
consumer and restores the original language. Translation quality remains human-owned.

Art normalization is defined in code (`gen_sprite.SPECS` and
`character_art.CHARACTER_ART_BUNDLE`) and projected into the checked art catalog. Generated raster
assets use `gen_sprite.py import`; the selected RitsuLib asset profile/provider owns runtime wiring.
Placeholder art is the default. A paid or external generation backend is never selected silently.

## Verification Philosophy

Build and real-host autotest prove code; authoring contracts guide code.

- Build proves compilation, packaging, manifests, resources, localization shape, PCK output, and
  deployable static artifacts under the pinned profile.
- Tier 1 proves the exact load marker, exact framework/host/compat identity, and no fresh error
  block.
- Tier 2 runs the arg-gated `SelfTest.cs` inside real STS2, drives the selected hosted behavior,
  waits for queued actions, asserts exact post-state and object identity, and requires
  `selftest done`.
- `played`, `fired`, and `used` logs are diagnostics, never pass evidence.
- Headed review owns real images, UI, mouse/controller interaction, animation, and subjective
  quality.

The final report states actual Build, Tier 1, Tier 2, and human results directly. A skipped or
failed check stays visible. Historical evidence is immutable and version-literal; older `0.5.4`
results do not become `0.5.11` runtime proof.

Verification is proportional. Reuse the nearest maintained host for a changed behavior. A fresh
natural-language acceptance Mod is reserved for an explicitly scheduled full-pipeline gate or a
direct human request. M8.6 is that future final gate, but is not currently eligible or started.

## Distribution

The repository publishes two generated forms from the same authoritative source:

- a Codex plugin under `plugins/open-mod/`; and
- portable Agent Skills under top-level `skills/`.

Regenerate both only through `publish.sh`, then verify repeatability, source/payload parity, payload
tool layout, Python compilation, and `git diff --check`. Installation and release are separate,
explicitly authorized operations.
