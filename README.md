# open-mod

open-mod is a free, open-source Codex plugin that turns a plain-language idea into a
working Slay the Spire 2 mod. It adapts the design conversation to the request, records a
durable design and exact supported spec, scaffolds and authors the project, builds it, and
uses proportional real-game verification when runtime behavior or presentation changes.

The first supported game is **Slay the Spire 2 (STS2)**.

> **Unreleased development version: 0.6.0.** Generated Mods target STS2 stable `0.107.1`
> with RitsuLib `0.5.4`. The BaseLib migration and M6.5-M6.7 implementation tracks are
> closed. M7.1-M7.5 design-intelligence work is implemented; M7.6 human-owned playtest
> tuning has not started. A GitHub release is not currently authorized.

## Requirements

1. Slay the Spire 2 stable `0.107.1`, installed through Steam.
2. .NET SDK `9.0` or newer (`dotnet --version`).
3. Python 3. On Windows, use a real python.org/Anaconda installation rather than the
   non-working Windows Store `python3` shim.
4. RitsuLib `0.5.4` with the `0.107.1` compat variant, installed locally or through the
   official Steam Workshop item `3747602295`.
5. Codex with plugin support.

You do not need BaseLib, an Alchyr template, Godot, MegaDot, or PckPacker. The generated
project uses open-mod's pinned scaffold and bundled Python build/packaging tools.

## Install In Codex

Until `0.6.0` is published, install the current checkout as a repo marketplace:

```powershell
codex plugin marketplace add D:\path\to\open-mod
codex plugin add open-mod@open-mod
```

Start a new Codex thread after installation so it loads the current skills and tools. The
plugin is defined by `.agents/plugins/marketplace.json` and
`plugins/open-mod/.codex-plugin/plugin.json`.

The portable Agent Skills payload remains available for compatible non-plugin hosts:

```powershell
npx skills add WhiteTowerAI/open-mod
```

## Make A Mod

Invoke the skill in Codex:

```text
$modmaker
```

Then describe the Mod in ordinary language, for example:

> A relic that gives 5 Block at the start of every third turn.

The skill will:

1. Resume an unfinished project or infer a fast, co-design, or revision route.
2. Ask only questions whose answers materially change the Mod.
3. Write `DESIGN.md` for intent, scope, coherence, and revision impact.
4. Write a validated `SPEC.md` containing only exact supported operations generated now.
5. Scaffold, author, build, package, and deploy the Mod.
6. Run the proportional load/behavior checks owned by the changed surface.
7. Report every pass, failure, fallback, and unrun check literally.

A complete narrow request keeps a zero-question fast path. Character requests receive an
exact native-shaped starter proposal rather than a blank deck questionnaire. Unsupported
current intent blocks before generation unless it is explicitly deferred, removed, or
changed to a supported version.

## Supported Surface

The RitsuLib-only generator currently covers:

- Cards, Relics, Potions, Powers, Keywords, Enchantments, Orbs, Monsters, and Encounters;
- computed Card Damage/Block, Energy/Star icons, typed Power values, and DynamicVar tips;
- native single/multi creature targeting within the recorded Card/Potion boundary;
- singleplayer top-X Scry, stateful cadence/resources, and ordered semantic card buffers;
- Events/World Nodes, bounded native presentation, and one Quest Card to forced Event route;
- playable Character Foundation, checked static art profiles, bounded private combat cues,
  and Character-local native Ancient/Architect dialogue;
- Relic-owned singleplayer Rest Site options;
- complete documented Custom Card Piles authoring, including ExtraHand;
- conditional Card hand glow and bounded Relic/Power corner labels; and
- the promoted M6.7 vanilla Card, visual, existing-Ancient, availability, and non-Card
  data/behavior override operation families.

Support follows one Package-level rule: when the official tutorials document a RitsuLib
feature's player-facing use and Package, and the needed public API exists in the pinned
profile, its documented public consumers are supported. Confirmed API/lifecycle problems
remain narrow limitations; missing implementation or verification is stated separately.

The exact active inventory and all exceptions live in
`games/sts2/tests/content-capability-graph.md`.

## Current Limits

Important boundaries include:

- custom multi-target Potions retain a confirmed lifecycle limitation;
- Rest Site options are Relic-owned and singleplayer-only;
- Scry and several generated state/UI systems are Mod-local and singleplayer-only;
- alternative Energy, arbitrary target systems, global acquisition weighting, and
  multiplayer vanilla overrides are unsupported;
- new Ancient models, arbitrary native room/dialogue replacement, unsupported transitions,
  production audio, and presentation outside promoted resource routes are unsupported;
- generated Mods do not invent Harmony, reflection, Publicizer, or IL from a prompt; and
- one-click Steam Workshop publishing is not implemented.

The capability graph is authoritative when this summary and a detailed boundary differ.

## Design Intelligence

M7.1-M7.5 add adaptive routing, pinned Character design grammar, mechanic/content/balance
planning, durable current/future scope, DESIGN-to-SPEC traceability, cross-surface coherence,
and bounded revision propagation. These are authoring-workflow capabilities; they do not
expand the runtime support graph.

Static scenarios and validators prove the shipped contracts, not balance, enjoyment,
translation quality, visual quality, or real-game behavior. M7.6 will cover human-owned
playtest feedback only after explicit selection.

## Verification Model

Tier 1 requires the exact load marker and no fresh error block. Tier 2 additionally requires
a structured post-state marker and `selftest done`. A successful build, trace validation,
trigger log, model response, or screenshot does not substitute for runtime behavior or
presentation evidence.

Fresh natural-language acceptance Mods are used only for an explicitly scheduled
full-pipeline gate or direct human-lead request. Durable ownership lives in
`games/sts2/tests/`; completed evidence is indexed under `documents/history/`.

## For Contributors

Read `AGENTS.md` and the active documents before changing the repository. Edit authoritative
source under `games/sts2/`:

- `games/sts2/skills/modmaker/`: staged design and implementation orchestrator;
- `games/sts2/skills/sts2-api/`: lazy design references and grounded API recipes; and
- `games/sts2/tools/`: scaffold, build, launch, log, art, and validation tools.

Regenerate, do not hand-edit, the committed payloads:

```powershell
& '<Git-install>\bin\bash.exe' './publish.sh' '--plugin'
& '<Git-install>\bin\bash.exe' './publish.sh' '--portable'
```

Run the normal checks before handoff:

```powershell
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

The active plan is `documents/IMPLEMENTATION_PLAN.md`; completed results and retired
snapshots are indexed by `documents/history/README.md`. See `LICENSE` for licensing.
