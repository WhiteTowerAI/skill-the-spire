# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Repo-specific rules for AI agents. General Git/PR conventions live in
[AGENTS.md](./AGENTS.md); read that too. This file overrides AGENTS.md on conflict.

## Project

open-mod is a free, open-source **skill** (for Claude Code, later Codex) that lets
a non-programmer describe a game mod in one sentence and get back a mod that
actually loads and runs in-game. First — and currently only — target: **Slay the
Spire 2 (STS2)**. It will be published publicly, so keep `main` clean.

Strategy is **one game deep, then a platform**: Phase 1 nails STS2 end to end;
Phase 2 abstracts the game-specific knowledge into a reusable "game pack" template
for more games. Full rationale, scope, and decisions are in `documents/` — read
those before substantive work; do not restate them here.

## Current status — M4.5 COMPLETE (toolchain pre-mined ①②③④; canary matrix green under BaseLib v3.3.5)

**M4.5 COMPLETE 2026-07-06 (all four steps).** Pre-mined the toolchain so runtime
never live-decompiles: ① analyzer mined whole → new pack page
`reference/build-constraints.md` (diagnostic set is exactly STS001–004 + the full
required-loc-key table); ② canary matrix (`games/sts2/tests/`, one minimal
pipeline-produced mod per element type — the NEW golden set, dev-only/not shipped);
③ `grounding.md` rewritten to three sources + runtime-vs-maintainer split, all
dev-box path fallbacks stripped from the shipped pack; ④ BaseLib load-time
registration throws swept into `build-constraints.md` §3 (the 3 `AddModel` throws;
no dup-id throw exists — `RegisterType` is a `HashSet.Add` no-op). Also this session:
verified the canary matrix still loads green under **BaseLib v3.3.5** (was 3.3.3; the
game itself is unchanged at stable **v0.107.1** — the v0.108.0 in Steam news is the
beta branch, which we don't target). Planning: added milestone **M6** (content-type
breadth beyond pooled combat elements — event/character/monster/orb/…, scoped from
the BaseLib decompile) to IMPLEMENTATION_PLAN.md, with anti-bloat as a hard design
constraint. Next execution milestone is still **M5** (tier-2 automation + one-command
install).

**M0–M3 gates all PASSED; M4 round 1 (potion) PASSED 2026-07-02; M4 round 2 (card)
PASSED 2026-07-03.** See `documents/M0_RESULTS.md` … `M4_RESULTS.md`. **M4 round 2**:
the pipeline now handles a third element type — `recipes/card.md` (new cards: attack/
block/power/combine) landed on top of the card foundations `reference/mechanics.md` +
`recipes/power.md`, and a one-sentence attack card ("Firebolt", 8 dmg, upgrade +3)
scaffolded → built (`.pck` via PckPacker) → tier-1 loaded → **tier-2 LOG-VERIFIED**
(`card FIREBOLT-FIREBOLT` into hand, played, marker grepped from the live log with the
game kept open), **zero repair**. This **closes round 1's tier-2 capture gap**. Two
findings: (1) the card console command is **`card <id> [pile]`** — spawns into hand,
no `add` subcommand, exact match (a third distinct grammar vs relic/potion); (2)
`grep_log.ps1` had a file-lock bug (exclusive `File.ReadAllText` threw while the game
was open) — fixed to `FileShare.ReadWrite` + a `-Tier2Pattern` arg that verifies both
tiers in one call. *Editing existing* vanilla content is deferred (needs raw Harmony
patching; no BaseLib wrapper). **M4 round 1** (potion, 2026-07-02): `recipes/potion.md`
+ `grounding.md` + a 63-potion snapshot; "Firebomb" scaffolded → built → tier-1 →
tier-2 observed, zero repair; console command `potion <id>` (exact, no `add`). What
exists now:
- The research docs in `documents/`, `LICENSE`, `README.md`, this file.
- **The skill source tree** under `games/sts2/` (decided: use the existing repo
  root, not a `t2mod/` wrapper). Layout:
  - `games/sts2/skills/modmaker/` — orchestrator `SKILL.md` + stage files
    (`interview`, `spec`, `scaffold`, `author`, `build`, `verify`, `repair`,
    `quirks`).
  - `games/sts2/skills/sts2-api/` — the game pack (`SKILL.md`, `recipes/relic.md`,
    `recipes/potion.md`, `recipes/card.md`, `recipes/power.md`,
    `reference/mechanics.md`, `grounding.md`, `reference/potions-snapshot.md`,
    `errors.md`), moved here from `documents/sts2-api/` via `git mv`.
  - `games/sts2/tools/` — `build.ps1` / `launch.ps1` / `grep_log.ps1` (PowerShell,
    Windows dev box).
- **Publish layer** (godogen pattern): source files use `${VAR}` placeholders;
  `publish.sh --agent claude` renders them via `scripts/publish/*.py` into
  `.claude/skills/` (git-ignored — regenerate, don't commit). Codex branch is
  stubbed (M5). Note: on Windows the bare `python3` may be the Store shim;
  `publish.sh` probes `python3`/`python`/`py` for a working Python 3.

The hand-built "Gambler's Coin" relic mod lives **outside this repo** at
`D:\26summer_intern\m1-gamblers-coin` (like the M0 probe) — it's a **substrate proof**
(the one artifact the pipeline can't reproduce, hand-built pre-pipeline), not part of
the published skill and no longer the "golden" reference for correct output. It loads
AND its effect fires in-game (both R2 tiers). The current **golden set** is the
**canary matrix** (`games/sts2/tests/canary.md`, M4.5 ②): one minimal
pipeline-produced mod per element type (relic/potion/card/power/combo), each build +
tier-1 verified — the live reference for "what correct current output looks like."

**Immediate next step**: M4.5 is done, so the next execution milestone is **M5** —
automate tier-2 so the effect check no longer needs the user's eyes. The decompile
confirms the entry points exist (`fight`/`card`/`potion`/`block` console commands +
`TestMode`, which skips VFX/waits under `--headless`); the `grep_log.ps1` fix
(shared-read + `-Tier2Pattern`) is a step toward it. After M5 the roadmap is
**M5.5 — art/sprite pipeline** (custom card portraits / `.tres` potion atlas / relic
png beyond placeholder default icons; user-configured image-gen backend — deferred out
of M4 since a no-art element loads fine on the default icon), then **M6 — content-type
breadth** (event/character/monster/orb/…, beyond the four pooled combat elements). A
harder multi-element interview (one sentence → several elements) is also still open.
Automated behavior testing (M5) and custom art (M5.5) remain the frontier.

## Architecture (the intended shape; substrate validated by M0/M1)

The design is a **combination baseline**, not a fork (see BASELINE_RESEARCH.md):

- **Pipeline** mirrors `htdt/godogen` (primary reference, Godot+C#): a single
  orchestrator `SKILL.md` drives lazy-loaded stage files — interview → spec →
  scaffold → author → build → verify → behavior-test → repair → finalize. **Files
  are state** (`SPEC.md`/`PLAN.md`/`MEMORY.md`) so the pipeline resumes after
  context compaction — resume-check first.
- **Mod substrate** is `Alchyr/ModTemplate-StS2` + **BaseLib**: scaffolding is
  `dotnet new` (pure CLI); each element is a `Custom*Model` subclass; behavior is a
  sequence of `Cmd`s; a mod = `Mod.json` + `.dll` + `.pck`.
- **The moat is the `sts2-api` "game pack"** — curated, on-demand knowledge
  (content models, command catalog, `recipes/` per element type, `errors.md`
  error→fix catalog) that pre-digests STS2's community-reverse-engineered
  conventions so the LLM writes correct code without live-decompiling. `recipes/`
  aims to make single-element mods ~90% templated; `errors.md` is append-only and
  compounds over time.
- **Verification is on observed reality, never "it compiled."** R2 has two tiers:
  tier 1 = load proof via log marker (guaranteed); tier 2 = "the effect actually
  fired" (best-effort, the headline differentiator) — candidate mechanisms are a
  Godot `SceneTree` test script or reusing `STS2MCP` live state. Never claim an
  effect was verified when only load was.
- **Reuse at the edges:** `spire-codex` (queryable decompiled API) for grounding,
  `STS2MCP`/`autoSpire` for live-state behavior checks — optional dependencies, not
  the core loop.

The full directory layout, pipeline diagram, and game-pack file table are in
IMPLEMENTATION_PLAN.md §1–3. Decided during M2: the skill source lives under
`games/sts2/` in this repo root (the `t2mod/` wrapper from the plan was dropped),
and `publish.sh` renders it into `.claude/skills/`.

## Branch model — READ THIS FIRST

There are three long-lived branches. Their roles are **not symmetric**. Know
which one you are on before doing anything.

| Branch          | Role                                                                 | Who writes                     |
| --------------- | -------------------------------------------------------------------- | ------------------------------ |
| `main`          | Public release branch. What the world / the boss sees. Must stay clean. | Boss, via PR only              |
| `Henry's_branch`| Henry's personal branch. Milestone snapshots and backups.            | Henry (the lead)               |
| `Henry's_cc`    | **Your working branch.** Edit freely here.                           | You (the AI agent)             |

### Hard rules

1. **`Henry's_cc` is your home.** Do all work here. You may modify anything and
   commit when it makes sense (see below).
2. **NEVER merge into `main`.** Not directly, not via PR, not ever. `main` is
   updated only by the human lead / boss through their own PR flow. This is a
   hard stop — if a task seems to require touching `main`, stop and ask.
3. **`Henry's_branch` is snapshot/backup only.** From time to time you may merge
   `Henry's_cc` into `Henry's_branch` locally to record a milestone, then commit
   there. Treat it as a checkpoint, not a place to develop.
4. Direction of merges is one-way: `Henry's_cc` → `Henry's_branch`. Never the
   reverse without the lead asking for it. Never anything → `main`.

## Commits

- **Wait to be asked before committing.** Don't commit automatically after every
  change. When work reaches a sensible checkpoint, either commit if the user has
  told you to, or ask if you should.
- **You write the commit message yourself** — follow the Conventional Commit
  style from AGENTS.md (`feat(...)`, `fix(...)`, `docs(...)`, etc.).
- Keep the `Co-Authored-By: Claude` trailer on commits you make, so AI
  authorship stays transparent in history.
- Commit specific files rather than blanket `git add .`, and flag anything that
  looks like a secret before staging it.

## Typical loop

1. Work on `Henry's_cc`.
2. Reach a checkpoint → commit on `Henry's_cc` (when asked / after confirming).
3. Occasionally merge `Henry's_cc` → `Henry's_branch` and commit there as a
   milestone/backup.
4. `main` is left alone. The lead PRs into it separately.

## Docs

Planning and research live in `documents/` (PROJECT.md, IMPLEMENTATION_PLAN.md,
BASELINE_RESEARCH.md, and the competitive-landscape notes). Read the relevant
ones before starting substantive work; keep them updated when plans change.

## Toolchain & commands (STS2 modding, for the M0 build/verify work)

There is no build/test/lint for *this repo* yet (no code). The commands below are
the STS2 mod toolchain M0 validates, sourced from ModTemplate-StS2 + BaseLib and
**still to be confirmed on a real machine** — treat as the starting hypothesis,
not verified fact. Details in R1_R2_FEASIBILITY.md.

Environment required on the STS2 box:
- **STS2 installed** (note install path; main vs beta branch).
- **.NET SDK 9.0+** (`dotnet --version`).
- **MegaDot 4.5.1 mono** (MegaCrit's Godot fork) — only if the PckPacker shortcut
  doesn't cover our assets.
- **BaseLib** — best via Steam Workshop subscribe (id `3737335127`).

Scaffold, build, verify:
```
dotnet new install Alchyr.Sts2.Templates          # install templates (once)
dotnet new <content-template> -n ProbeMod          # scaffold (no spaces in name)
dotnet build                                       # fast: .dll only → mods/
dotnet publish /p:GodotPath="<MegaDot exe>"        # full: .dll + .pck (headless) → mods/
```
- **`build` vs `publish`:** `build` compiles only the `.dll` (fine for code-only
  changes). `publish` also generates the `.pck` via headless Godot — **required
  for any localization/image/scene change to show up.**
- **Try PckPacker first:** uncomment the `BSchneppe.StS2.PckPacker` package ref;
  if `dotnet build` alone then emits the `.pck`, we avoid the MegaDot dependency.
- Paths (game/Godot) auto-discover via `Sts2PathDiscovery.props`; override with
  `/p:Sts2Path=...` / `/p:GodotPath=...`.

Launch + log-assert (R2 tier 1):
- Put `steam_appid.txt` containing `2868840` in the game dir → run
  `SlayTheSpire2.exe` directly (no Steam needed, scriptable).
- Log is `%appdata%/SlayTheSpire2/logs/godot.log` (Windows). Generated mods emit
  markers via `MainFile.Logger.Info(...)`; the verify loop launches, waits, then
  greps the log for the `[T2MOD-SELFTEST]` marker and for error lines naming the mod.

Platform note: **Windows-first** (current dev environment). STS2/Steam are
cross-platform, so mod paths and the game binary differ on macOS/Linux — handle
later.
