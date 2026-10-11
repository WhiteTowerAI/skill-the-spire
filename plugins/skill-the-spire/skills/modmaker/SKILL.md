---
name: modmaker
description: |
  Build a working Slay the Spire 2 mod from a one-sentence natural-language
  description. Use when the user wants Codex to create, generate, or
  build an STS2 mod end to end: design, author, build, and verify it in-game.
---

# STS2 Mod Maker

Turn the user's idea into supported, compilable Mod code, then prove selected behavior in the
real STS2 host. Contracts guide authoring; Build and host autotests establish results.

## Non-negotiable boundaries

- Target STS2 stable `0.107.1` and the RitsuLib `0.6.7` authoring/API baseline.
  Scaffold pins the checked local compat and shared modules; runtime manifests require only
  `STS2-RitsuLib >= 0.6.7`.
- Prefer maintained public RitsuLib routes and reviewed Adapters in this pack. When none
  covers an accepted operation, implement it as a Mod-local route from pinned public APIs
  under `../sts2api/grounding.md` § Mod-local Routes, and verify it with Build,
  Tier 1, Tier 2, and any needed headed review before reporting it as working. Never
  decompile, use private members, or ship Harmony, reflection, Publicizer, or IL.
- Preserve settled user decisions and unrelated project artifacts. A player-visible substitute
  needs explicit acceptance.
- Every player-facing localization table has matching `eng` and `zhs` tables/keys, nonempty
  values, and equal SmartFormat token multisets. A Mod with no localization tables is neutral.
- Never edit an installed skill payload from a generated project. Maintainers edit source under
  `games/sts2/` and publish it.
- Report only actual evidence. Build is not load, load is not behavior, trigger logs are not a
  state proof, and automated state is not a visual or subjective observation.

## Supported product boundary

The exact inventory and limitations live in the shipped surfaces and `sts2api` references.
Current authoring includes:

- Card, Relic, Potion, Power, Keyword, Enchantment, and Orb content;
- complete singleplayer Acts with explicit entry policies, and new Shared/Act-scoped Ancients;
- combat Card Afflictions, selectable good/bad run Modifiers, explicit Run/Combat Global
  Effects, and independently owned Rest Site actions;
- custom native-screen Rewards with deterministic save reconstruction, and independently owned
  Custom Card Piles across the complete documented API;
- local Mod-owned Runtime UI workflows using selected top-bar, Toast, runtime-hotkey, local
  Capstone, Catalog, floating-window, search-expansion, fixed node-attachment, and shell-token APIs;
- computed Card Damage/Block/Energy/Star/Power values under one preview/execution formula;
- deterministic advanced Card/Potion targeting with its pinned multi-target Potion limitation;
- Monster move graphs and Encounter rosters;
- ordinary Events, bounded native presentation, and Quest Card forced follow-up Events;
- playable Character Foundation, static presentation, bounded combat cues, native-scene
  dialogue, secondary resources, and ordered semantic buffers;
- standalone/Card/Relic/Modifier Rest Site options, bounded state, readability aids,
  and supported static art;
- grounded vanilla Card, visual, Ancient, availability, and non-Card overrides; and
- cataloged model-hook participation on only the custom surfaces the host dispatches to.

The nine generalized families remain authorable through their owner pages: secondary
resources; Monster/Encounter composition and HP; Character starting fields; Card/Relic Rest
Site options; computed Card values; bounded state; forced Event mappings; Card Star costs; and
Event acquisition/shake profiles. Their newly generalized variants remain game-unobserved until
a real current run proves them. Do not narrow a documented feature family merely because one consumer
lacks focused proof.

Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, and new integrations
whose purpose is to connect another element to those families are deferred. Do not route one
through Runtime UI, persistence, lifecycle, or another included owner.

Outside maintained routes, a missing recipe is not a stop condition; follow
`../sts2api/grounding.md` § Mod-local Routes. Stop only when the behavior requires private APIs, runtime
patching, or decompilation, or cannot be given a verifiable lifecycle. Known unsupported areas
include arbitrary behavior-bearing scenes/materials
without a public host, global room replacement, arbitrary transactions/transitions/RNG rewrites,
alternative Energy, retained played-Card zones, ungrounded disable/weighting surfaces, multiplayer
integrations, and one-click Workshop publishing.

## Read stages lazily

Read each file from `./` only when its stage begins:

| File | Purpose |
|---|---|
| `route.md` | Read state; choose fast, co-design, revision, or resume |
| `interview.md` | Resolve only material open decisions |
| `design.md` | Write concise human intent, decisions, scope, and not-now items |
| `semantic-contract.md` | Rules for the human-readable implementation work order |
| `spec.md` | Write exact operations, support routes, and autotest scenarios |
| `scaffold.md` | Create the pinned local-runtime project and manifest |
| `quirks.md` | Preventive STS2/RitsuLib rules needed before C# |
| `author.md` | Generate C#, localization, resources, markers, and `SelfTest.cs` |
| `build.md` | Compile, validate, pack, and deploy |
| `verify.md` | Tier 1, Tier 2, headed review, and direct final report |
| `repair.md` | Bounded repair from compiler/log/state evidence |

Query `../sts2api` narrowly when a concrete API, recipe, capability, error, art, or
SelfTest answer is needed. Do not load the full API pack.

For a playable Character or Character content set, load
`../sts2api/design/character-foundation.md` before creative questions. It supplies
the pinned starter inventory and native-shaped defaults; it does not constrain other surfaces.

## Pipeline

```text
human idea
  -> concise DESIGN
  -> implementable SPEC with autotest scenarios
  -> capability_preflight.py (route existence + hook reachability only)
  -> scaffold
  -> author C# + localization/resources + SelfTest.cs
  -> build
  -> Tier 1 load proof
  -> Tier 2 real-host structured state proof
  -> necessary headed human observation
  -> direct report from actual results
```

1. **State and route.** Read `DESIGN.md`, `SPEC.md`, `PLAN.md`, and `MEMORY.md` when present.
   Resume the first incomplete stage if the user requested no
   change; use revision for a requested change.
2. **Interview.** Ask only questions whose answers materially change behavior, scope, state,
   supported operations, or proof. The exact-content fast path asks zero questions when complete.
3. **DESIGN.** Preserve intent, accepted decisions, current scope, and explicit not-now items in
   concise Markdown. Do not create IDs, ledgers, trace blocks, coherence contracts, completion
   claims, settlements, or impact queues.
4. **SPEC.** Write the sole implementation work order: exact behavior/state/text/presentation,
   maintained support routes, and concrete SelfTest scenarios. Run:

   ```powershell
   python ../modmaker/scripts/capability_preflight.py --spec SPEC.md
   ```

   This preflight checks only selected route existence and model-hook capability, shape,
   route ownership, and surface reachability. The compiler, Build, Tier 2, and human review own
   everything else.
5. **Scaffold and Author.** Resolve the local profile, create the project, translate only the
   current SPEC through its recipes, author bilingual localization when used, add the load marker,
   and generate an arg-gated `SelfTest.cs` from `reference/selftest-harness.md`. Art defaults to
   checked placeholders unless the SPEC selects a supported custom route.
6. **Build.** `build.py` validates the pinned profile, compiles C#, validates manifest/resources/
   localization, packs a PCK when needed, and deploys only the Mod's own artifacts.
7. **Tier 1.** Launch normally and require the exact load marker with no fresh error block.
8. **Tier 2.** Isolate one harness Mod, run `launch.py --self-test`, and require independently
   asserted structured post-state plus `selftest done`. A fired/used line is diagnostic only.
9. **Headed review.** Use it only for selected image framing, UI, controller/mouse behavior,
   animation, or subjective experience that structured state cannot prove.
10. **Finalize.** Read the actual Build, Tier 1, Tier 2, and human outcomes. State what passed,
    failed, or was not run and where artifacts live. Do not infer missing evidence or route the
    report through a ledger.

On a failure, read `repair.md`, make one grounded change, rebuild where required, and rerun the
earliest meaningful check. Stop after the bounded attempt cap or when resolution needs a
player-visible design change or missing shared capability.

## Files are state

- `DESIGN.md`: human intent, accepted decisions, current scope, and explicit not-now work.
- `SPEC.md`: exact implementation, maintained routes, and required autotest scenarios.
- `PLAN.md`: a simple stage checklist only.
- `MEMORY.md`: technical discoveries, resolved IDs/keys, commands/results, and repair attempts.

## Core commands

```powershell
python ../modmaker/scripts/capability_preflight.py --spec SPEC.md
python ../modmaker/scripts/scaffold.py --project-dir <outer-dir> --mod-name <ModName> --author <Author>
python ../modmaker/scripts/build.py --project-dir <outer-dir> --mod-name <ModName>
python ../modmaker/scripts/launch.py
python ../modmaker/scripts/grep_log.py --mod-name <ModName>
python ../modmaker/scripts/launch.py --self-test --mod-name <ModName>
python ../modmaker/scripts/grep_log.py --mod-name <ModName> --tier2-pattern "<structured proof>"
```

The outer project directory name must differ from the Mod name.
