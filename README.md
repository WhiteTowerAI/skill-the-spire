# open-mod

open-mod is a free, open-source Codex plugin that turns a plain-language idea into a working
Slay the Spire 2 Mod. It can help shape the idea, records a concise design and implementable work
order, authors against grounded RitsuLib routes, builds the project, and uses real-game autotest to
prove behavior when authorized.

> **Unreleased development version: `0.7.0`.** Generated Mods target STS2 stable `0.107.1`
> with RitsuLib `0.5.11`. A GitHub release is not currently authorized.

## Requirements

1. Slay the Spire 2 stable `0.107.1`, installed through Steam.
2. .NET SDK `9.0` or newer.
3. Python 3. On Windows, use a working python.org or Anaconda installation.
4. RitsuLib `>=0.5.11` with the `0.107.1` Compat variant, installed locally or through official
   Steam Workshop item `3747602295`.
5. Codex with plugin support.

Generated projects compile against the checked local runtime and have no framework
`PackageReference`. You do not need BaseLib, an Alchyr template, Godot, MegaDot, or PckPacker;
open-mod supplies its scaffold, Godot.NET SDK imports, and Python build/packaging tools.

## Install In Codex

Until `0.7.0` is published, install the checkout as a repository marketplace:

```powershell
codex plugin marketplace add D:\path\to\open-mod
codex plugin add open-mod@open-mod
```

Start a new Codex task after installation. The portable Agent Skills payload remains available for
compatible hosts:

```powershell
npx skills add WhiteTowerAI/open-mod
```

## Make A Mod

Invoke the skill:

```text
$modmaker
```

Then describe the Mod in ordinary language, for example:

> A relic that gives 5 Block at the start of every third turn.

The skill follows this pipeline:

```text
idea
  -> concise DESIGN
  -> implementable SPEC
  -> thin capability preflight
  -> Author + SelfTest
  -> Build
  -> Tier 1
  -> Tier 2 / SelfTest
  -> headed human review when needed
  -> direct report from actual results
```

A complete narrow request keeps a zero-question fast path. `DESIGN.md` preserves intent, accepted
decisions, current scope, and explicit `Not Now` items. `SPEC.md` is the sole implementation work
order: exact behavior, values, state, text/presentation, support routes, and autotest scenarios.

Before Author, one small checker confirms that selected support routes exist and that raw model
hooks are real and reachable by the chosen surface. Build owns compilation, manifests, resources,
localization, packaging, and deployment. Real STS2 SelfTest owns behavior. Headed human review owns
images, UI, controller behavior, animation, and subjective quality.

Existing projects may retain older metadata. The current workflow ignores it and does not force a
migration.

## Supported Surface

The RitsuLib-only generator covers:

- Cards, Relics, Potions, Powers, Keywords, Enchantments, Orbs, Monsters, and Encounters;
- computed Card values, native Energy/Star costs, typed Power values, and DynamicVar tips;
- native single/multi creature targeting within the documented Card/Potion boundary;
- reusable bounded state, secondary resources/payment/UI, and ordered semantic buffers;
- Events/World Nodes, bounded native presentation, acquisition/shake profiles, and forced Event
  mappings;
- playable Character Foundation, static presentation, bounded combat cues, and native
  Ancient/Architect dialogue;
- Card- or Relic-owned singleplayer Rest Site options within the documented boundary;
- complete documented Custom Card Piles authoring, including ExtraHand;
- conditional Card hand glow and bounded Relic/Power corner labels;
- promoted vanilla Card, visual, Ancient, availability, and non-Card data/behavior overrides; and
- declared custom-content model-hook participation, restricted to the hooks each surface can
  actually receive.

Some generalized shapes are implemented but not yet observed in a running game. The authoritative
inventory and exact limitations live in
[`games/sts2/tests/content-capability-graph.md`](games/sts2/tests/content-capability-graph.md).

Generated Mods do not invent prompt-derived Harmony, reflection, Publicizer, or IL. A missing
maintained public/fixed route blocks authoring rather than being replaced with a silent
approximation.

## Verification

- **Build** means the project compiled and packaged under the pinned static contract.
- **Tier 1** means the exact load marker and framework/host/compat profile were observed with no
  fresh error block.
- **Tier 2** means `SelfTest.cs` drove the behavior in real STS2, asserted structured post-state,
  and emitted `selftest done`.
- `played`, `fired`, and `used` logs are diagnostics only, not Tier 2 evidence.
- Headed review covers only the concrete visual/UI/controller/animation observations a person
  actually made.

Reports state passed, failed, and unrun checks directly. Source/static/payload validation is not a
gameplay result.

## Development Status

The BaseLib migration, M6.5-M6.7, M7, M8.0-M8.3, and M8.5 are closed; completed evidence and
literal exceptions are indexed under `documents/history/`.

M8.7 Product Boundary Generalization is implemented in source and both payload forms, but remains
open pending its result record and explicit human closure. M8.8 Surface Effect Composability is
paused and unimplemented; its refactored future plan uses refreshed RitsuLib `0.5.11` research,
concise recipe/reference guidance, the sole thin preflight, behavior-level developer tests, and
Build/real-host SelfTest rather than new trace/schema machinery. It still needs explicit human
confirmation before implementation. M8.6 final installed acceptance waits for both Packages to
close and explicit human selection. None of these states authorizes a game run, install, commit,
push, or release.

## For Contributors

Read `AGENTS.md` and active documents before changing the repository. Edit authoritative source
under `games/sts2/`; never hand-edit generated `plugins/open-mod/` or top-level `skills/` payloads.

Regenerate both payloads through:

```powershell
& '<Git-install>\bin\bash.exe' './publish.sh' '--plugin'
& '<Git-install>\bin\bash.exe' './publish.sh' '--portable'
```

Run the normal source checks:

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

The active plan is `documents/IMPLEMENTATION_PLAN.md`. See `LICENSE` for licensing.
