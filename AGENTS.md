# AGENTS.md

Repository guidance for Codex and other AI coding agents working in this repository.

These are the repo-specific rules and project context. Follow this file as the
authoritative agent instruction entry point; read the relevant documents under
`documents/` before substantive work.

## Project

open-mod is a free, open-source **skill** (for Claude Code, later Codex) that lets
a non-programmer describe a game mod in one sentence and get back a mod that
actually loads and runs in-game. First — and currently only — target: **Slay the
Spire 2 (STS2)**. It will be published publicly, so keep `main` clean.

Strategy is **one game deep, then a platform**: Phase 1 nails STS2 end to end;
Phase 2 abstracts the game-specific knowledge into a reusable "game pack" template
for more games. Full rationale, scope, and decisions are in `documents/` — read
those before substantive work; do not restate them here.

## Current status — M6 Core IN PROGRESS: 6c capability kernel DONE; direct next = 6d advanced cells

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
beta branch, which we don't target). Planning first identified **M6** from BaseLib's
full registration surface (beyond the current 3 pooled families + auto-discovered power),
with anti-bloat as a hard constraint. The M6 execution model was redesigned 2026-07-10
around playable vertical slices and real hosted-scenario proofs; see the current M6
section below and `IMPLEMENTATION_PLAN.md`.

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
tiers in one call. At M4, *editing existing* vanilla content was deferred because it needs
Harmony rather than a BaseLib wrapper; the current Character Capability Program now treats
curated, versioned Harmony/Publicizer adapters as valid future capability modules, but none
is user-facing until its own scenario canary passes. **M4 round 1** (potion, 2026-07-02): `recipes/potion.md`
+ `grounding.md` + a 63-potion snapshot; "Firebomb" scaffolded → built → tier-1 →
tier-2 observed, zero repair; console command `potion <id>` (exact, no `add`). What exists now:
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
pipeline-produced mod per element type (relic/potion/card/power) plus one multi-element
interaction canary (historical project name `CanaryCombo`), each build +
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
DRIVER bodies for relic/card/potion plus multi-element interaction observations + 3-way marker vocabulary); `author.md` step
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

**M5 tier-2 automation is DONE — card/relic/potion source drivers plus the card→power
interaction (historical `CanaryCombo`) PASS
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

**M5.5 managed-credit art follow-up LIVE-VERIFIED ON WINDOWS 2026-07-14.** The user-provided
`WhiteTowerAI/imagine-skill` baseline remains gitignored at `baselines/imagine-skill/`
(snapshot `1163a79`); it is research only, not a runtime dependency. New cross-platform
`tools/acquire_sprite.py` owns the optional Vofy CLI edge: silent `status` + live-model
preflight, an explicit per-job `--yes` approval gate, one synchronous paid task into an
isolated directory, exactly-one-image discovery, then the existing `gen_sprite.py import`
normalizer/placer. It never calls `/imagine`, installs/logs into Vofy, reads credentials,
records account/credit output, parses Vofy stdout for filenames, or automatically retries
a possibly charged task. Eleven Windows acquisition tests cover missing CLI/auth/model,
approval, task failure/timeout, zero/multiple output, card import, relic two-path/chroma,
invalid local references, prompt normalization, and an npm-style `.cmd` shim; the 19-test
tools suite passes. A fresh Codex acceptance mod (`HonedEdge`) used Vofy `gpt-image-2` plus
type-matched STS2 references for three card portraits and power/relic cut-outs, then imported,
built, and visually passed in game. The first multiline prompt was rejected; the wrapper now
folds all prompt whitespace to one line before the Windows CLI boundary. macOS/Linux and live
provider rejection/insufficient-credit paths remain unverified. Details:
`documents/BASELINE_RESEARCH.md` §5 and `IMPLEMENTATION_PLAN.md` M5.5 follow-up.

**Stateful timing/counter follow-up LIVE-VERIFIED 2026-07-15.** The pipeline now has an
explicit state contract for remembered mechanics: advancing event, threshold phase,
`turn|combat|run` lifetime, reset, persistence, UI meaning, and boundary proof. Happy
Flower-style relic counters use `[SavedProperty]` and continue across combat/save; Stone
Calendar-style timing reads `PlayerCombatState.TurnNumber` and resets with each combat.
`CadenceCanary` built 0/0 and passed Tier 1 + a two-combat Tier 2 with save round trip.
Adjacent grounded/unsupported families are recorded honestly in
`games/sts2/tests/mechanic-capability-audit.md`; see `IMPLEMENTATION_PLAN.md` follow-up.

**Monster Move Vocabulary hardening LIVE-VERIFIED 2026-07-15.** The existing Enemy
Encounter slice now covers grounded/copyable self custom-Power, player Debuff, Block/Heal,
multi-attack, attack+effect, explicit cycles, and conditional branches. The multi-turn
`CombatEnemy` harness asserts `NextMove`/move history, hit count, and exact player/monster
HP/Block/Power state. `CanaryMonsterVocabulary` built 0/0 and passed strict Tier 1 + an
eight-turn Tier 2 through both half-HP branches; a fresh Chinese one-sentence `EmberWarden`
run used different numbers and passed 0/0 + Tier 1 + Tier 2 with zero repair. Strict
verification also retired initialization-time `SetFtuesEnabled` and implicit missing-scene
fallback errors. Custom monster Spine art remains provisional. Full evidence:
`games/sts2/tests/canary-results.md` + `IMPLEMENTATION_PLAN.md` §5 M6.

**Downfall advanced-character baseline + capability planning LANDED 2026-07-15.** The
gitignored maintainer baseline is `baselines/downfall/`, pinned at `ee2f801` (Downfall
0.0.30; STS2 0.107.1; BaseLib 3.3.5; MIT); it is never shipped or read at runtime. The
maintainer audit `games/sts2/tests/downfall-character-capability-audit.md` decomposes all
ten source characters into reusable programming families rather than role-named recipes:
scoped state/FSMs, custom zones, dynamic content, resources/payment, owned entities,
run-start choices, hosted rewards/rest actions, semantic hooks, UI adapters, save/network
contracts, and versioned Harmony/Publicizer bridges. Collector and Gremlins are marked
source-only because the current combined Downfall project does not compile them. Direct
registration correction: BaseLib 3.3.5 `CustomCharacterModel` constructor auto-calls
`AddCharacter(this)`; generated code must not call it explicitly. BaseLib is now the first
choice, not the feature ceiling. Art/animation is deliberately non-gating for this
programming phase; use fallback/built-in/generic visuals until code behavior is green.

**M6 6b Character Foundation PIPELINE-SUPPORTED / LIVE-VERIFIED 2026-07-15.**
`CanaryCharacter` uses `alchyrsts2charmod` + `PlaceholderCharacterModel`, contains no
manual `AddCharacter` call, built 0 warnings / 0 errors, and passed strict Tier 1 plus
unattended `RunStart` + `CombatPlayer` Tier 2. Evidence independently proves constructor
registration count 1, the real selection icon present/clicked, run HP `72/72`, concrete
card/relic/potion pools and members, starters `10/5/5/1`, standard `MaxEnergy=3`, and
`TrailMarker` Energy `3 -> 4`. The run grounded the exact four Architect loc keys, Windows
`res://` separator normalization, and the `NRun.GlobalUi` gate before local-player lookup.
`recipes/character.md` and compact pipeline routing are shipped; character art/animation
remains non-gating and unclaimed.

**M6 6c Capability Kernel SCENARIO-VERIFIED / LIVE-VERIFIED 2026-07-15.**
`CanaryPatchKernel` is a self-contained content-mod module: combat-scoped state,
deterministic typed hook dispatch, descriptor-based fallback UI, and a version/MVID/
signature-gated patch registry. It built 0 warnings / 0 errors and passed strict Tier 1
plus two-combat Tier 2. The single B-risk postfix targets public
`NCombatUi.Activate(CombatState)` on STS2 0.107.1; Tier 1 observed exact target/owned/
idempotent `1/1/1` plus three compatible foreign postfixes. Tier 2 observed typed
dispatch/state/listeners `1/1/1`, a real fallback Label, and distinct combat generations
`1/2` with activations `1/1`. Domain behavior stays outside the kernel. The shipped
`reference/capability-kernel.md` records zero-target/failure/conflict diagnostics and
compact pipeline routing. This is infrastructure, not user-facing 6d semantics; no
Publicizer, transpiler, or `OpenMod.Runtime` was added.

**Next-session handoff:** Treat 6a-6c as complete at their stated boundaries. Do not repeat
the Downfall audit, live-decompile STS2, regenerate the Foundation shell, or build another
kernel-only canary. Begin **6d Resource/UI**, reusing the self-contained 6c module only for
its verified combat-UI seam, then build the bounded custom-Zone/dynamic-output cell. Keep
gameplay rules in generated domain code. Do not create `OpenMod.Runtime` until a second
independent generated mod earns the same shared Harmony/Publicizer seam.

**M6 Core — playable content-breadth slices (M6.0 contracts LANDED 2026-07-10;
Character Foundation LANDED and 6c kernel scenario-verified 2026-07-15; direct next 6d).** Do
not execute M6 as a flat "one BaseLib class → one recipe → one canary" checklist: many
new types only matter through a host relationship (monster→encounter, keyword→card,
reward→post-combat). Start with **M6.0**, a lightweight maintainer-only Content Capability
Graph recording registration mode, host/dependency, verification scenario, observable
proof, art, composition, and support level. Support advances
`inventoried → grounded → build-verified → scenario-verified → pipeline-supported`; only
the last is user-facing support. Tier-2 grows through reusable scenario adapters
(`CombatPlayer`, `CombatEnemy`, `MapNode`, `PostCombat`, `RunStart`) and dual proof:
Type Canary for build/load plus Scenario Canary for real hosted behavior.

M6.0 is now landed as a maintainer-only graph at
`games/sts2/tests/content-capability-graph.md`: Existing / M6 Core / Extras / Deferred
capabilities record registration, real host, scenario, observable proof, art, composition,
support level, and evidence/blockers. STS2 engineering evidence is kept separate from STS1
or cross-game design analogies; only the former advances the support ladder. M6.0 also fixed
the Tier-2 proof seam: `launch.py --self-test` now returns nonzero for FAILED/timeout/early
process exit, and `grep_log.py` requires exact load + an asserted structured state proof +
`selftest done` (a terminal line alone can never prove behavior). Standard-library synthetic
log regressions cover this contract. No registry/schema or hypothetical adapter fleet was
added. The `CombatPlayer` seam is reused by the three live Mechanic Vocabulary canaries;
`CombatEnemy` and `MapNode` have since been earned by their own vertical slices. Their lazy
recipes and compact pipeline routing are shipped.

M6 Core ships vertical slices in this order: ① Mechanic Vocabulary (**DONE / live
pipeline-supported 2026-07-10**: keyword + card enchantment + orb; BaseLib
`CustomModifierModel` is a separate run-modifier capability, not a card-enchantment
synonym), ② Enemy Encounter (monster + encounter) — **pipeline-supported 2026-07-13**
(`CanaryEncounter`: custom monster + encounter build 0/0, first earned
`CombatEnemy` seam — encounter entered, monster present, PECK move executed, player HP
delta=6; recipe + pipeline wired; full natural-language user acceptance run completed;
key correction: monster attacks use
`.FromMonster(this).Execute(null)`, **never** `.Targeting()`; monster Spine/scene art stays
provisional/fallback). ③ World Node (event) — **pipeline-supported 2026-07-14**
(`CanaryEvent`: `CustomEventModel` build 0/0, first earned `MapNode` seam — real event room,
nested title/option/result loc, real option UI click, Gold delta=25; `recipes/event.md` +
pipeline wired; separate one-sentence `ForgottenCache` acceptance passed 0/0 + Tier 1 +
Tier 2 with Gold delta=30 and zero repair; event art remains a verified vanilla placeholder,
custom generation provisional); the **Monster Move Vocabulary hard gate passed 2026-07-15**
(richer actions and multi-turn `CombatEnemy` proof). ④ the **Character Capability
Program** now has its Foundation pipeline-supported (selectable, run-start, valid
pools/starters, HP/energy, public mechanic) and its typed advanced-mechanic kernel
scenario-verified. Direct next is Resource/UI and custom-Zone/dynamic-output canaries,
and a fresh natural-language character that composes at least two capability families and
crosses one verified non-BaseLib seam. A selectable shell alone no longer closes M6. All
four Core slices must be `pipeline-supported` at their stated boundaries. Reward,
rest-site option, and pet are **M6 Extras** and do not block M7; Act is outside the M6
completion gate. Anti-bloat applies to every stage: evolve toward a common SPEC envelope +
lazy type/scenario contracts instead of adding full per-type prose branches to
`interview/spec/author/scaffold/verify`. Full plan: `IMPLEMENTATION_PLAN.md` §5 M6.

Then **M7 — interactive, proactive interview for non-programmers** (the former "M5.7 harder
interview" promoted to a major milestone 2026-07-09). **The headline is the user's
experience, not design theory:** our audience is complete beginners with no programming
experience, so the interview should feel like a knowledgeable collaborator that
*proactively* asks about the details of what they're making — helping them think through
what they wouldn't know to consider: **edge cases, balance, interplay/联动, and
extensibility** — not passively transcribe one sentence into one element. The hard part is
being proactive *without* being exhausting (beginners overwhelm easily): raise only the few
concerns that apply, one or two at a time, plain language, with a default offered; keep the
one-line fast path un-regressed. The interplay concern is itself a four-level ladder (L1
technical dependency — already shipped via the interaction harness; L2 resource loop; L3 archetype
identity; L4 run-rhythm & risk-reward), grounded in MegaCrit's design language. M7 L3/L4
wait specifically for the **M6 Core gate** (Mechanic Vocabulary + the Character Capability
Program provide the keyword/orb vocabulary, buildable character target, and an advanced
composition path); they do not wait for every Downfall-derived capability, M6
Extras or Act. See `documents/BASELINE_RESEARCH.md` ("MegaCrit design language") +
IMPLEMENTATION_PLAN.md §5 M7 + memory `[[sts2-m7-design-advisor]]`.

## Architecture (the intended shape; substrate validated by M0/M1)

The design is a **combination baseline**, not a fork (see BASELINE_RESEARCH.md):

- **Pipeline** mirrors `htdt/godogen` (primary reference, Godot+C#): a single
  orchestrator `SKILL.md` drives lazy-loaded stage files — interview → spec →
  scaffold → author → build → verify (tier 1 + tier 2) → repair → finalize. **Files
  are state** (`SPEC.md`/`PLAN.md`/`MEMORY.md`) so the pipeline resumes after
  context compaction — resume-check first.
- **Mod substrate** is `Alchyr/ModTemplate-StS2` + **BaseLib-first capability
  composition**: scaffolding is `dotnet new` (pure CLI); normal behavior is built from
  `Custom*Model` + `Cmd`s. When no public seam exists, only maintainer-grounded,
  versioned Harmony/Publicizer modules with patch diagnostics and Scenario proof are
  eligible. A mod remains `Mod.json` + `.dll` + `.pck`; an optional automatically installed
  `OpenMod.Runtime` may later own shared cross-mod patch registries after two real canaries
  earn that boundary.
- **The moat is the `sts2-api` "game pack"** — curated, on-demand knowledge
  (`recipes/`, semantic capability contracts, versioned patch adapters, shared
  mechanics/build constraints, the self-test/art contracts, and append-only `errors.md`)
  that pre-digests STS2's community-reverse-engineered conventions so the LLM writes
  correct code without live-decompiling. Preserve imaginative mechanics in SPEC; compose
  or ground the missing primitive instead of silently simplifying the idea.
- **Verification is on observed reality, never "it compiled."** Tier 1 proves load
  via the real game log. Tier 2 is the live-verified, arg-gated in-process self-test:
  the headed game navigates with `ForceClick`, calls public Cmds, and logs the actual
  effect marker; all four driving cells pass. Manual dev-console steps are fallback
  only when navigation misses. Never claim an effect was verified when only load was.
- **Keep live verification evidence-dense.** Prove each semantic behavior once. Do not
  extend a scenario merely to observe another additive value (for example Power
  `2 -> 4` or attack `5 -> 7`) or repeat the same downstream consequence. Repeat an
  action only to cover a distinct control-flow or lifecycle boundary such as another
  conditional branch, a required cycle return, reset/persistence, or a cap/floor.
  Prefer the fewest game turns and assertions that cover all independent invariants.
- **Reuse at the edges:** `spire-codex` (queryable decompiled API) for grounding,
  `STS2MCP`/`autoSpire` for live-state behavior checks — optional dependencies, not
  the core loop.

The current directory layout and game-pack file table are in
IMPLEMENTATION_PLAN.md §1–3. Source lives under `games/sts2/`; `publish.sh` renders a
gitignored Claude dev shape plus the committed plugin (`plugins/open-mod/`) and portable
Agent Skills (`skills/`) payloads.

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
- **You write the commit message yourself** — follow Conventional Commit style
  (`feat(...)`, `fix(...)`, `docs(...)`, etc.).
- Keep an AI co-author trailer appropriate to the agent making the commit, so AI
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

## Toolchain & commands (current verified path)

The Windows dev box has live-verified the full scaffold → build → tier-1 → tier-2 loop
under STS2 stable v0.107.1, .NET 9.0.300, and BaseLib v3.3.5. The shipped wrappers are
cross-platform Python; macOS/Linux defaults are best-effort until tested there.

Environment required:
- **STS2 installed**.
- **.NET SDK 9.0+** (`dotnet --version`).
- **BaseLib**, normally via Steam Workshop id `3737335127`.
- **Python 3** for the shipped wrappers.

Scaffold once per mod from a dedicated empty work directory whose name differs from the
mod name:
```bash
dotnet new install Alchyr.Sts2.Templates
dotnet new alchyrsts2contentmod -n <ModName> -M <Author>
```

Uncomment the template's `BSchneppe.StS2.PckPacker` package reference, then use:
```bash
python <tools>/build.py --project-dir <mod-project> --mod-name <ModName>
python <tools>/launch.py
python <tools>/grep_log.py --mod-name <ModName>
python <tools>/launch.py --self-test --mod-name <ModName>
python <tools>/grep_log.py --mod-name <ModName> --tier2-pattern "fired|used|played"
```

PckPacker makes normal `dotnet build -c Release` emit and copy `.dll`, `.pck`, and
`.json`; MegaDot/`dotnet publish` is a historical fallback, not the pipeline default.
`launch.py` ensures `steam_appid.txt`, starts the real game, and in self-test mode waits
for the harness terminal marker. `grep_log.py` reads the fresh current `godot.log` and
checks markers plus mod-named errors. Test one harness mod at a time because
`--t2selftest` arms every loaded harness mod.
