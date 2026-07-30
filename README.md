# open-mod

open-mod is a free, open-source Codex plugin that turns a plain-language idea into a
working Slay the Spire 2 mod. It interviews only when a decision matters, writes a
semantic spec, scaffolds and authors the project, builds it, launches the real game, and
checks both load and behavior.

The first supported game is **Slay the Spire 2 (STS2)**.

> **Unreleased development version: 0.6.0.** The generated-mod pipeline now targets only RitsuLib
> `0.4.62` on STS2 stable `0.107.1`. The BaseLib implementation path has been retired.
> The migration and external clean-workspace Codex acceptance are complete; details are
> archived in `documents/history/RITSULIB_MIGRATION_RESULTS.md`. A GitHub release is
> deliberately deferred while remaining bugs are fixed. M6.5 acceptance is closed; its
> lead-approved Prismwright result is archived in
> `documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`. M6.6 computed values, bounded
> advanced targeting, native custom-Character Ancient dialogue, and bounded Relic-owned
> Rest Site options are individually pipeline-supported; M6.6 itself remains open.

The provisional M6.6 capability roadmap and planned M6.7 version-bound vanilla-content
override track are maintained in `documents/IMPLEMENTATION_PLAN.md`. Planned items are not
part of the supported surface until their individual implementation and real-game proof
gates pass.

## Requirements

1. Slay the Spire 2 stable `0.107.1`, installed through Steam.
2. .NET SDK `9.0` or newer (`dotnet --version`).
3. Python 3. On Windows, use a real python.org/Anaconda installation rather than the
   non-working Windows Store `python3` shim.
4. RitsuLib `0.4.62`, installed in the STS2 Mods directory with the `0.107.1` compat
   variant. Use the release from
   [BAKAOLC/STS2-RitsuLib](https://github.com/BAKAOLC/STS2-RitsuLib); the installed
   runtime must contain `lib/0.107.1/STS2-RitsuLib.dll` or the equivalent direct compat
   asset.
5. Codex with plugin support.

You do not need BaseLib, an Alchyr template, Godot, MegaDot, or PckPacker. The generated
project uses open-mod's pinned scaffold and bundled Python build/packaging tools.

## Install In Codex

Until `0.6.0` is merged and published from GitHub, install the current local checkout as a
repo marketplace:

```powershell
codex plugin marketplace add D:\path\to\open-mod
codex plugin add open-mod@open-mod
```

Start a new Codex thread after installation so it loads the new skills and tools. The
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

Then describe the mod in ordinary language, for example:

> A relic that gives 5 Block at the start of every third turn.

The skill will:

1. Ask at most one compact round of questions when the answer changes the implementation.
2. Show a plain-language plan and record the accepted semantic contract.
3. Create a pinned RitsuLib project and author the required content.
4. Build and install the mod into STS2's Mods directory.
5. Launch the real game for Tier 1 load verification.
6. Run the closest hosted self-test for Tier 2 behavior verification when that host is
   supported; otherwise report the exact manual fallback without pretending it passed.

## Supported Surface

The current RitsuLib-only pipeline supports:

- cards, relics, potions, powers, keywords, enchantments, and orbs;
- filtered live-creature targeting for single-target Cards/Potions and multi-target Cards,
  including native mouse/controller selection and cancellation;
- singleplayer top-X Scry through a generated-Mod-local helper;
- monsters and encounters with deterministic and conditional move vocabularies;
- Events / World Nodes with pages, options, public Cmd outcomes, selections, rewards,
  resumable or terminal special combat, bounded rich text and VFX, and one bounded solo
  Quest Card to forced-Event composition;
- playable Character Foundation with exact pools, starters, HP, and Energy;
- custom-Character localization dialogue in the nine cataloged native Ancient and
  Architect scenes, preserving native models, layouts, options, and outcomes;
- singleplayer Relic-owned Rest Site options with free/fixed Gold, deterministic outcomes,
  once-per-site/run repeatability, native stay/leave behavior, and checked custom/fallback
  button art;
- stateful relic cadence with combat-local and run-persistent state;
- combat-only secondary resources with all-or-nothing payment and a public fixed live UI;
- ordered semantic card-play buffers whose source Cards follow normal Play -> Discard;
- placeholder, local, or generated static art for the grounded content families, including
  nine verified Character profiles;
- optional private combat-only Character `Idle`/`Attack`/`Hit`/`Dead` frame cues with an
  all-or-nothing static fallback.

Static art acquisition prefers a callable host-native raster tool (`image_gen` in Codex),
then the explicitly selected Vofy, compatible HTTP backend, or local-image route. Tool
availability is detected at runtime. A skill file or model name alone is not proof that
image generation is callable, and open-mod never silently switches to a paid backend.

## Current Limits

The following remain unsupported unless a later milestone explicitly opens and proves
them:

- all unproved M6.6 capability packages and M6.7 vanilla-content override categories;
- custom multi-target Potions and arbitrary Card/object/map targeting;
- Card/Modifier-owned Rest Site options, variable or non-Gold Rest Site costs, arbitrary
  transactions, same-site repeat, or multiplayer Rest Site extensions;
- retained-card custom-zone UI or hidden retained played cards;
- alternative Energy engine hooks;
- run-persistent or remote-player Character resources and UI;
- multiplayer/replay Scry or global cross-Mod Scry hooks;
- production Character animation beyond the bounded combat cues, arbitrary materials,
  audio, or multiplayer presentation;
- custom Character Ancient models/layouts/options/rewards/audio/VFX, global dialogue
  replacement, and unproved locked-selection/map-marker art;
- arbitrary Event VFX/layouts, direct merchant/rest/treasure transitions, or more than one
  special combat from the same mutable Event instance;
- one-click Steam Workshop publishing.

## Verification Model

Tier 1 requires the exact load marker and no fresh error block. Tier 2 additionally
requires a structured post-state marker and `selftest done`. A successful build, a trigger
log, or a screenshot by itself is not behavior proof. Player-visible state is part of
correctness whenever open-mod owns UI or presentation.

Fresh natural-language acceptance mods are disposable. Durable contract and hosted proof
ownership live in `games/sts2/tests/`; completed evidence is indexed under
`documents/history/`.

## For Contributors

Edit only the source under `games/sts2/`:

- `games/sts2/skills/modmaker/`: staged orchestrator;
- `games/sts2/skills/sts2-api/`: lazy recipes and grounded references;
- `games/sts2/tools/`: scaffold, build, launch, log, and art tools.

Regenerate, do not hand-edit, the two committed payloads:

```powershell
& '<Git-install>\bin\bash.exe' './publish.sh' '--plugin'
& '<Git-install>\bin\bash.exe' './publish.sh' '--portable'
```

The local Codex development shape is generated with `./publish.sh --agent codex` under
`.agents/skills/` and is git-ignored.

Run the normal checks before handing off:

```powershell
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

Read `AGENTS.md` before changing the repository. See `LICENSE` for licensing.
