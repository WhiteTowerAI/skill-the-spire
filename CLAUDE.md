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

## Current status — M5.5 COMPLETE (art/sprite pipeline live-verified for all 4 element types); next major milestone M7 (interactive proactive interview for non-programmers) after M6 (content-type breadth)

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

**M5 IN PROGRESS 2026-07-06 — tier-2 behavior automation (docs+harness landed; live
end-to-end run pending the dev box).** Goal (user's words): make mod authors need as
little rework/debug as possible — so tier-2 ("the effect actually fires") is now driven by
an **in-process self-test harness** the pipeline emits into every mod, instead of the
user hand-typing dev-console commands. Design (locked with user): **Route A** — the mod
drives its own tier-2 check in-process (no keystroke injection, no external MCP); start
**headed but keystroke-free**; **zero-interaction** combat entry via `ForceClick`
navigation. Scope is **tier-2 only** (Codex adapter / one-command install / Workshop split
to later milestones), covering **runtime effect automation + combo/multi-element
interaction**. What landed this session (all from a fresh decompile grounding at
`D:\26summer_intern\decomp\sts2_full`): a new pack page
`reference/selftest-harness.md` (full arg-gated `SelfTest.cs` template + per-element
DRIVER bodies for relic/card/potion/combo + 3-way marker vocabulary); `author.md` step
2.5 (emit the harness + the gated `SelfTest.Arm()` line); `verify.md` rewritten to the
unattended `launch.ps1 -SelfTest` flow with an honest manual fallback; `spec.md` gained
an interaction/dependency block for combos; `launch.ps1` gained `-SelfTest` (passes
`--t2selftest`, polls for the `selftest done`/`FAILED` marker); `repair.md` gained the
3-way tier-2 signal split (harness-setup-miss vs no-effect vs wrong-value); `SKILL.md`
scope+pipeline updated. **Key grounding correction:** the string-in
`DevConsole.ProcessCommand(string)` is **NOT reachable** from a mod (the inner
`DevConsole` is a private field on `NDevConsole`), so the harness calls the **public
Cmds** the console commands wrap (`RunManager.EnterRoomDebug`, `RelicCmd.Obtain`,
`CardCmd.AutoPlay`, `PotionModel.EnqueueManualUse`, …) — see the M5 harness memory.
**Correction to the old plan:** `TestMode` does **NOT** give us usable `--headless`
VFX/wait-skipping — `TestMode.TurnOnInternal` is documented internal-CI-only ("NEVER CALL
THIS"), and `AutoSlayer`'s entry is gated by `IsReleaseGame()` (hardcoded `true` on the
Steam build). The reachable entry points are the console-command-wrapped public Cmds +
the subscribable `CombatManager.CombatSetUp`; the harness uses MegaCrit's own
`CombatRoomHandler` poll pattern (`WaitHelper.Until(IsInProgress)` → wait `Play` phase)
since it drives its own navigation.

**M5 tier-2 automation is DONE — all four driving cells (card/relic/potion/combo) PASS
live on the dev box 2026-07-06** (see `games/sts2/tests/canary-results.md`).

**M5 one-command install — LANDED 2026-07-06 (Claude Code shape; headless-verified).**
open-mod now ships as a **native Claude Code plugin**, so the install UX is two REPL
commands — `/plugin marketplace add WhiteTowerAI/open-mod` then `/plugin install
open-mod@open-mod` — with no clone, no manual `publish.sh`, and no fixed cwd (the
committed distribution goal). Mechanism: repo root is the marketplace
(`.claude-plugin/marketplace.json`), the plugin lives at `plugins/open-mod/`
(`.claude-plugin/plugin.json` + generated `skills/` + `tools/`), and the tool-path
coupling that forced a fixed cwd is solved by `${CLAUDE_PLUGIN_ROOT}` — the plugin's
absolute install dir, substituted by Claude Code at load time. `publish.sh` gained a
`--plugin` mode that renders the source `${VAR}` skills into the committed payload with
paths pointing at `${CLAUDE_PLUGIN_ROOT}/…` and bundles the three PowerShell tools
alongside. **The plugin payload under `plugins/open-mod/` IS committed** (unlike
git-ignored `.claude/skills/`) because the marketplace fetches it from git — don't
hand-edit it; edit the source under `games/sts2/` and re-run `./publish.sh --plugin`.
**Left:** the real `/plugin marketplace add WhiteTowerAI/open-mod` command only works
once these files reach `main` (it fetches the default branch); until then test with the
local path `/plugin marketplace add <repo path>`.

**M5 cross-agent install + cross-platform tools — LANDED 2026-07-07.** open-mod now
also installs into non-Claude agents (Codex, Cursor, OpenClaw, …) via
`npx skills add WhiteTowerAI/open-mod`. Mechanism: `publish.sh` gained a third mode
`--portable` that renders a **committed top-level `skills/`** tree in the layout
skills.sh auto-discovers (`skills/<name>/SKILL.md`, depth 2). The agent-neutral
tool-path problem (no `${CLAUDE_PLUGIN_ROOT}` off Claude) is solved the AgentSkills-spec
way: tools live in `skills/modmaker/scripts/` and are referenced by **relative** path.
The three tools were **rewritten from Windows PowerShell to cross-platform Python**
(`build.py`/`launch.py`/`grep_log.py`) — this also killed the `pwsh` dependency the dev
box never had (it only has Windows PowerShell 5.1). Regression-verified on Windows:
re-ran CanaryCard tier-2 end to end (`build.py` 0/0 → `launch.py --self-test` self-drive
→ `Jolt played` marker → `[PASS]`). Also fixed a latent Git-Bash MSYS bug that mangled
`/modmaker` → `D:/Git/modmaker` in every rendered SKILL.md `default_prompt` (fix: store
the command name slash-less, template writes the `/`). **Two committed payloads now:**
`plugins/open-mod/` (Claude, `${CLAUDE_PLUGIN_ROOT}` paths, `--plugin`) and top-level
`skills/` (cross-agent, relative paths, `--portable`) — both generated, both re-run +
commit after editing `games/sts2/` source; see their `GENERATED.md`. **Not verified:**
mac/Linux tool paths (best-effort, no non-Windows box) and the live `npx skills add`
into a real non-Claude agent. **Registry directory listing (lobehub/skills.sh) is still
open** — that's discoverability, separate from the install mechanism which now works.

**M5.5 — Art/sprite pipeline COMPLETE 2026-07-08.** All four element types live-verified
in-game (card portrait 1000×760 via `card_portraits/big/<slug>.png`; relic + power each
need TWO icons `<slug>.png` + `big/<slug>.png` 256×256; potion = one 256×256 loose PNG,
no .tres atlas). Gen tool: `tools/gen_sprite.py` (BYO OpenAI-compat backend, chat-mode
support for Poe/Gemini-native, magenta chroma-key for cut-out icons). Art samples shipped
in `reference/art-samples/` (card/relic/power/potion subdirs; 36 MegaCrit reference PNGs
+ ATTRIBUTION.md). Two pipeline corrections fixed + re-verified: relic/power must extend
the template base (not CustomPowerModel/CustomRelicModel directly), and both need the
`big/` variant. See `games/sts2/tests/canary-results.md` §M5.5 for the full run record.

**Next: M6 — content-type breadth** (event/character/monster/orb/enchantment/…), then
**M7 — interactive, proactive interview for non-programmers** (the former "M5.7 harder
interview" promoted to a major milestone 2026-07-09). **The headline is the user's
experience, not design theory:** our audience is complete beginners with no programming
experience, so the interview should feel like a knowledgeable collaborator that
*proactively* asks about the details of what they're making — helping them think through
what they wouldn't know to consider: **edge cases, balance, interplay/联动, and
extensibility** — not passively transcribe one sentence into one element. The hard part is
being proactive *without* being exhausting (beginners overwhelm easily): raise only the few
concerns that apply, one or two at a time, plain language, with a default offered; keep the
one-line fast path un-regressed. The interplay concern is itself a four-level ladder (L1
technical dependency — already shipped via the combo harness; L2 resource loop; L3 archetype
identity; L4 run-rhythm & risk-reward), grounded in MegaCrit's design language. Sequenced
AFTER M6 because L3/L4 + real balance advice need M6's content types (keyword/character/orb)
to design around. See `documents/BASELINE_RESEARCH.md` ("MegaCrit design language") +
IMPLEMENTATION_PLAN.md §5 M7 + memory `[[sts2-m7-design-advisor]]`.

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
