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

## Current status — M3 PASSED (bounded automated repair loop works end to end)

**M0, M1, M2, and M3 gates all PASSED.** See `documents/M0_RESULTS.md`,
`M1_RESULTS.md`, `M2_RESULTS.md`, `M3_RESULTS.md`. **M3 passed 2026-07-02**: the
`repair.md` bounded loop diagnosed → fixed → re-verified two deliberately-broken
relic specs within the retry cap (1 attempt each) — a build-time guessed-API error
(`CS0103` → ground to the real Cmd) and the headline "green build ≠ loads" case
(missing `[Pool]`, compiles clean, throws at registration, caught by tier-1's
error-line check). M2 acceptance (2026-07-02) had already produced a fresh relic
("LuckyCoin") from one sentence that built clean, loaded, and fired in combat with
zero repair. What exists now:
- The research docs in `documents/`, `LICENSE`, `README.md`, this file.
- **The skill source tree** under `games/sts2/` (decided: use the existing repo
  root, not a `t2mod/` wrapper). Layout:
  - `games/sts2/skills/modmaker/` — orchestrator `SKILL.md` + stage files
    (`interview`, `spec`, `scaffold`, `author`, `build`, `verify`, `repair`,
    `quirks`).
  - `games/sts2/skills/sts2-api/` — the game pack (`SKILL.md`, `recipes/relic.md`,
    `errors.md`), moved here from `documents/sts2-api/` via `git mv`.
  - `games/sts2/tools/` — `build.ps1` / `launch.ps1` / `grep_log.ps1` (PowerShell,
    Windows dev box).
- **Publish layer** (godogen pattern): source files use `${VAR}` placeholders;
  `publish.sh --agent claude` renders them via `scripts/publish/*.py` into
  `.claude/skills/` (git-ignored — regenerate, don't commit). Codex branch is
  stubbed (M5). Note: on Windows the bare `python3` may be the Store shim;
  `publish.sh` probes `python3`/`python`/`py` for a working Python 3.

The hand-built golden mod ("Gambler's Coin" relic) lives **outside this repo** at
`D:\26summer_intern\m1-gamblers-coin` (like the M0 probe) — it's a reference, not
part of the published skill. It loads AND its effect fires in-game (both R2 tiers).

**Immediate next step is M4** (breadth within STS2: card/potion recipes, harder
interview, + the art/sprite pipeline). M3 is done: `repair.md` (the bounded
diagnose → fix → re-verify loop) is wired into `build.md`/`verify.md`, `errors.md`
grew a guessed-API entry (now incl. `CS0103`, found by running the acceptance) and
a tier-1 "loaded but no marker" entry, and both broken-spec tests converged in one
attempt. A notable M3 finding: tier-1's error-line check is load-bearing — a
missing `[Pool]` still logs the load marker (MainFile ran), so marker-alone would
false-PASS; only the "no mod-named errors" half caught it. Automated behavior
testing (M5) and art (M4) remain the frontier.

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
