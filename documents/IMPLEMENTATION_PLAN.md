# Implementation Plan: STS2 Text-to-Mod Skill

> Companion to PROJECT.md, BASELINE_RESEARCH.md, R1_R2_FEASIBILITY.md,
> COMPETITIVE_LANDSCAPE.md. This is the build blueprint: directory layout, the
> skill pipeline, the game pack shape, and a phased milestone plan.
> Status: living plan. Written 2026-07-01 and updated through 2026-07-13.
> **M0–M5.5 are complete. M6 Core is in progress:** M6.0 contracts, Mechanic
> Vocabulary, and Enemy Encounter are complete and pipeline-supported. **NEXT = World
> Node**, followed by Minimal Character. M7 L3/L4 starts after the explicit M6 Core gate;
> see the M6/M7 sections below. Historical run details remain in `M0_RESULTS.md` …
> `M4_RESULTS.md`, while current M6 evidence lives in `games/sts2/tests/`.

## 0. Design principles (inherited from the research)

- **One orchestrator skill + lazy-loaded stage files** (godogen pattern), not a
  dozen parallel skills. Read a stage file only when you reach that stage → keeps
  context small.
- **Files are state, not chat memory** (godogen): `SPEC.md`, `PLAN.md`,
  `MEMORY.md` let the pipeline resume after compaction. Resume-check first.
- **Verify on observed reality, never "it compiled"** (godogen "trust the media";
  Cerebras "never loop without verifiers"). For us the observed reality is the
  **game log + live state**, not screenshots.
- **Game knowledge lives in a separate, swappable pack** (godogen `godot-api`
  skill; our future multi-game path). The orchestrator is game-agnostic; the
  pack is STS2-specific.
- **Auto-repair is bounded, not magical** (~70% convergence from the literature):
  cap retries, then hand back a clear "couldn't fix, here's the error."
- **Non-programmer UX is the wedge** (vs modmixer/the MCP tools): one sentence
  in, plain-language progress, no file/tooling knowledge required.
- **Zero runtime decompilation (pre-mine, don't live-dig).** A `/modmaker` run must
  never make the user wait on a live dig through the 3425-file `decomp/` tree — that
  "online-slow" cost belongs to *pack maintenance*, done once, not to every run.
  Decompiling is a maintainer's tool for *building the pack*; at runtime the skill
  only *reads the pack* (recipes, an API index, a constraints page, errors.md). The
  key enabler: **build-time and load-time constraints are enforced by finite,
  decompilable code, so they can be enumerated offline to near-completeness** — the
  analyzer's rules, the csproj/MSBuild targets, and BaseLib's registration-time
  `throw`s. Only *behavior* correctness (tier-2: effect fired but wrong) genuinely
  needs execution and cannot be mined offline. See milestone **M4.5**.

## 1. Repository layout

The original `t2mod/` wrapper + `runtimes/` proposal was superseded during M2/M5.
The current source and two committed distribution shapes are:

```
open-mod/                           # actual repo root
├── README.md / CLAUDE.md / AGENTS.md
├── documents/                     # plans, research, and historical run records
├── games/sts2/                    # authoritative editable source
│   ├── skills/
│   │   ├── modmaker/              # orchestrator + lazy stage files
│   │   │   ├── SKILL.md
│   │   │   ├── interview.md / spec.md / scaffold.md / author.md
│   │   │   └── build.md / verify.md / repair.md / quirks.md
│   │   └── sts2-api/              # lazy game pack
│   │       ├── SKILL.md / grounding.md / errors.md
│   │       ├── recipes/           # relic/card/potion/power known-good patterns
│   │       └── reference/         # mechanics, constraints, harness, art contract/samples
│   ├── tools/                     # build.py / launch.py / grep_log.py / gen_sprite.py
│   └── tests/                     # maintainer-only canary matrix; never shipped
├── scripts/publish/               # placeholder rendering helpers
├── publish.sh                     # renders the three install shapes
├── plugins/open-mod/              # COMMITTED Claude Code plugin payload (generated)
├── skills/                        # COMMITTED portable Agent Skills payload (generated)
└── .claude/skills/                # gitignored Claude development render (generated)
```

Edit only `games/sts2/` source, then regenerate committed ship payloads with
`./publish.sh --plugin` and `./publish.sh --portable`; never hand-edit those payloads.
The plugin uses `${CLAUDE_PLUGIN_ROOT}` for cwd-independent absolute paths. The portable
shape bundles Python tools under `skills/modmaker/scripts/` and uses relative paths for
Codex/Cursor/OpenClaw/other Agent Skills consumers.


## 2. The pipeline (what the orchestrator SKILL.md drives)

```
User: one sentence ("a relic that ...")
  |
  0. RESUME CHECK — if SPEC.md/PLAN.md exist, skip to the right stage
  |
  1. INTERVIEW (interview.md)  — ONE short round, only for what's genuinely
  |     ambiguous (element type? rarity? when does it trigger?). Non-blocking
  |     defaults for the rest. (Higgsfield-style, but minimal.)
  |
  2. SPEC (spec.md)            — write SPEC.md: element type, name, rarity/tier,
  |     trigger, effect in game terms, art placeholder. This is the contract.
  |     Show the user a plain-language summary.
  |
  3. SCAFFOLD (scaffold.md)    — dotnet new from Alchyr template (once per mod),
  |     set manifest fields, wire BaseLib. (R1 groundwork.)
  |
  4. AUTHOR (author.md)        — using sts2-api pack: pick the recipe, write the
  |     C# Custom*Model subclass with the right Cmd sequence, add localization
  |     JSON, drop placeholder art. Inject the [T2MOD-SELFTEST] log marker.
  |
  5. BUILD (build.md)          — dotnet build (+publish for .pck) → .dll/.pck/.json
  |     into mods/. (R1.)  On failure → REPAIR.
  |
  6. VERIFY (verify.md) — run tier 1 (load marker + no mod-named errors), then
  |     tier 2 through the arg-gated in-process harness. The headed game navigates
  |     itself into combat, drives public Cmds, and logs the observed effect marker.
  |     Manual dev-console verification is fallback only. On failure → REPAIR.
  |
  7. REPAIR (repair.md) — shared bounded sub-loop invoked by build/verify: read the
  |     real error, consult errors.md, apply one fix, re-run only the failed stage.
  |
  8. FINALIZE — summarize artifacts and the exact observed verification tier.
```

## 3. The game pack (`sts2-api`) — our moat, concretely

Purpose: pre-digest STS2's community-reverse-engineered knowledge so the LLM
writes *correct* code without live-decompiling every time. Queried on demand
(like godogen's `godot-api`), never dumped wholesale into context.

What each file holds and where it's sourced from:

| File | Content | Sourced from |
|------|---------|--------------|
| `SKILL.md` | Query/routing contract for the lazy game pack | current pipeline |
| `recipes/*.md` | Copy-adaptable known-good patterns for relic/card/potion/power | ModTemplate + base-game analogs + live canaries |
| `reference/mechanics.md` | Shared DynamicVars, SmartFormat, enum and Cmd/value foundations | decompiled game + live runs |
| `reference/build-constraints.md` | Complete STS001–004 and BaseLib registration/load constraints | analyzer + BaseLib decompile |
| `reference/selftest-harness.md` | Arg-gated tier-2 harness and current public-Cmd driver patterns | decompile + live canaries |
| `reference/art-contract.md` + `art-samples/` | Verified sprite paths/sizes, placeholder/generation contract, style references | live M5.5 runs + extracted assets |
| `errors.md` | **Error signature → fix** catalog; grows every time repair succeeds | our own runs |
| `grounding.md` | Runtime-vs-maintainer grounding doctrine and pack-gap handling | project policy |

Key design decisions:
- **`recipes/` are the heart.** A single-element mod should be ~90% templated:
  the recipe supplies the class skeleton, pool attribute, and localization stub;
  the LLM fills only the effect's `Cmd` sequence. This is what makes us reliable
  where raw-AI is a gamble.
- **`errors.md` is a compounding moat.** Every failure we diagnose becomes a
  permanent entry. Over time the repair loop gets faster and the pack gets
  harder to replicate — this is the "1-1.5 weeks others won't spend" made durable.
- **Reuse, don't rebuild grounding.** `spire-codex` already exposes a queryable
  decompiled API; `grounding.md` points there instead of us maintaining a full
  decompile. **Validated by modmixer**, whose "crown jewel" is exactly a local
  decompile+index of real game source so the agent grounds on real symbols
  (COMPETITOR_MODMIXER.md) — combine our curated `recipes/` with a spire-codex
  index rather than hand-writing everything.

## 4. R1 / R2 wired into the pipeline

- **R1 (build.md):** standardized on `dotnet build -c Release` with PckPacker;
  `games/sts2/tools/build.py` wraps it and reports copied `.dll/.pck/.json` artifacts.
  MegaDot publish is a historical fallback, not the user path.
- **R2 tier 1 (verify.md):** `launch.py` starts the real game and `grep_log.py` checks
  the load marker plus absence of mod-named errors. This proves installs + loads +
  registers.
- **R2 tier 2 (verify.md) — the differentiator, shipped in M5:** each generated mod
  carries an arg-gated `SelfTest.cs`. `launch.py --self-test` passes `--t2selftest`;
  the headed game navigates menu→combat with `ForceClick`, calls the public Cmd APIs the
  dev console wraps, and logs effect + terminal markers. All four driving cells pass
  live. Manual console steps are an honest fallback only when navigation fails; never
  claim Tier 2 from a green build or load marker alone.

## 5. Milestones (each ends in something demonstrable)

**M0 — De-risk (do before committing to the full build). ✅ DONE (2026-07-01, see M0_RESULTS.md).** On a machine with
STS2 + .NET 9 (+ MegaDot). Run the R1 and R2-tier-1 prototypes from
R1_R2_FEASIBILITY.md by hand (no skill yet): confirm one-command build produces
`.dll`+`.pck` in `mods/`, and a hand-injected self-test marker is greppable from
`godot.log` after launch. **Gate: if M0 fails, revisit the whole approach.**

**M1 — Manual golden mod. ✅ DONE (2026-07-01, see M1_RESULTS.md).** By hand, build ONE complete relic mod end to end
(the "Gambler's Coin" example): scaffold → author → build → loads in-game →
self-test passes → effect works. This becomes the reference the recipe is
distilled from, and the acceptance target for the skill. **Outcome:** both R2
tiers passed — the effect fired in real combat (log-verified), not just loaded.
`recipes/relic.md` + `errors.md` seeded from it. Notable finding: STS2's **dev
console** (`relic add <id>`, auto-enabled when modded) is a cheap tier-2 lever,
reshaping the M5 mechanism choice toward driving the console.

**M2 — Skill skeleton, happy path. ✅ DONE (2026-07-02, see M2_RESULTS.md).**
Orchestrator `SKILL.md` + interview/spec/scaffold/author/build/verify stages +
the seeded `recipes/relic.md`. **Outcome:** driving the stage files, one sentence
produced a fresh relic ("LuckyCoin", deliberately not the golden name) that built
clean (0/0), loaded (tier-1 marker), and fired in combat (tier-2, dev console,
energy 3→6 HEADS) with **zero repair to the generated mod**. Source lives under
`games/sts2/` (no `t2mod/` wrapper); `publish.sh` renders `${VAR}` source →
`.claude/skills/` (codex branch stubbed for M5). The run fixed two verify-tool bugs
(`grep_log.ps1` godot.log rotation; `build.ps1` localized dotnet-output path regex)
and one doc bug (`author.md` now injects the load marker — the template doesn't).

**M3 — Repair loop + errors.md. ✅ DONE (2026-07-02, see M3_RESULTS.md).** Added
`repair.md` (bounded diagnose → fix → re-verify sub-loop: max 3 attempts, stop if a
signature survives a fix, one change per attempt, never fake success), wired it into
`build.md`/`verify.md`, and grew `errors.md`. **Outcome:** two deliberately-broken
relic specs each repaired in 1 attempt driving the real tools — a build-time
guessed-API error (`CS0103` → ground to the real Cmd) and the headline "green build ≠
loads" case (missing `[Pool]`: compiles clean, throws at registration). Notable
finding: tier-1's error-line check is load-bearing — the load marker still fires when
`[Pool]` is missing (MainFile ran), so marker-alone would false-PASS. errors.md grew
from the run itself (CS0103 added to the guessed-API signature).

**M4 — Breadth within STS2.** Added card and potion recipes plus auto-discovered
power support, extending the combat-oriented foundation beyond relics. Hardened the interview
for ambiguous requests. **The art/sprite pipeline was originally scoped here but is
now its own milestone, M5.5** (below, after M5) — a no-art element loads cleanly with
the default placeholder icon, so custom art is not on the critical path to a working
mod and was deferred.
> **Round 1 PASSED 2026-07-02 (M4_RESULTS.md):** `recipes/potion.md` +
> `grounding.md` + a vanilla potion snapshot landed, and the "Firebomb" potion
> (20 dmg, single target) scaffolded → built (.pck emitted) → tier-1 loaded → tier-2
> effect observed, zero repair. Confirmed a no-art potion loads cleanly (default
> icon). Remaining: card recipe, harder interview, art/sprite pipeline.
> **Round 2 PASSED 2026-07-03:** card recipe (Firebolt) end to end, both tiers.
> **Round 3 (BloodAndFury, 2026-07-03):** two Ironclad Power cards + two custom
> powers, both tiers passed — but the run surfaced a recipe bug (power.md omitted
> the analyzer-required `.smartDescription` loc key → build STS001) and a scaffold
> footgun (template writes to CWD; outer dir must not equal `<ModName>`). Both fixed
> + published. That this slipped past full spire-codex + baselib grounding is what
> motivates **M4.5** below.
>
> **Scope note:** M4 delivered card + potion (pooled) and power (auto-discovered) —
> four combat-oriented model types including the original relic foundation. The larger,
> structurally different content types (event, character, monster, orb, …) are **not**
> covered here; they are their own milestone line, **M6** below.

**M4.5 — Pre-mine the toolchain: kill runtime decompilation. ✅ DONE (2026-07-06).**
Motivation: the BloodAndFury run proved that grounding on spire-codex (content) +
baselib decompile (runtime API) leaves a whole third category unmined — the
**toolchain's own validators** (Roslyn analyzer, csproj/MSBuild targets, BaseLib
registration `throw`s) — because those are enforced at *build/load* time and are
*stricter than runtime* (e.g. `SmartDescription` falls back to `.description` at
runtime, so baselib alone says "optional"; the analyzer hard-fails without it). These
constraints are finite, decompilable code → **enumerable offline once**, so the user
never triggers a live dig. The four suggestions, **in priority order (①=cheapest,
highest-leverage first)**:

**① Mine the analyzer whole, once (highest leverage, cheapest).** Decompile
`Sts2ModAnalyzers.dll` (NuGet cache: `alchyr.sts2.modanalyzers/0.1.9/analyzers/
dotnet/cs/`) and enumerate **STS001–00N — the FULL diagnostic set** (a `strings` grep
only *glimpsed* STS001–004; confirm the real count, don't assume 4) plus the complete
`RequiredLocalization` table (which loc keys each model type requires). Write it into a
pack **"build constraints" reference page** + `errors.md`. This isn't patching one
instance — it closes an entire *class* of bug. The `RequiredLocalization` table was
already partly dumped this run, so it's mostly ready to transcribe.

**② Self-test canary matrix — the skill verifies itself, no human.** The pipeline
already automates scaffold→build→verify. Build one minimal mod per content type
(relic / potion / card / power) plus one multi-element relationship canary (historical
project name `CanaryCombo`), run build + tier-1, as a repeatable
regression suite. The `.smartDescription` bug hits *anyone* the first time they build a
power mod — a "one canary per element type" matrix exposes it with **zero user tests**.
Sharper point: this bug landed on the *one recipe written from grounding but never
actually built* — card had Firebolt, potion had Firebomb, but `power.md` (commit
5536eee) was pure documentation, an unexecuted code path. **Hard rule to adopt: any
recipe is PROVISIONAL until it has one green build behind it.** This run treated a
provisional `power.md` as verified.

**③ Fix `grounding.md`'s doctrine (cheap but important).** Add the third source
explicitly: "content → codex; runtime code → decompile; **build/load constraints →
analyzer + csproj targets + baselib registration `throw`s**." And spell out the
asymmetry that hid this bug from a perfect decompile read: **"decompile shows it RUNS"
≠ "it BUILDS."**

**④ Ongoing: grep every `throw` in baselib's registration path.** The missing-`[Pool]`
exception is one load-time constraint; `CustomContentDictionary.AddModel` and neighbors
surely enforce more (required overrides, dup ids, …). Finite and enumerable — sweep
them into the constraints page + `errors.md`.

**Plus — API index (separate from the four above; user-approved 2026-07-03).** The four
suggestions close *build/load constraints*; this closes the *runtime-API* leak (layer ②
of the runtime model): an effect that needs a `Cmd`/hook/enum **not yet in a recipe**
today still leaks to a live dig. Generate a lookup table of all `Cmd` signatures, hooks,
and enums from `sts2.dll` + baselib so that case becomes a **table lookup, not a dig**.
Keep it strictly LOOKUP-shaped (fork + grep a local file), **never dumped into main
context** — sts2-api is already lookup-shaped, so it fits. This is the biggest of the
tasks; sequence it after ①–④ (which are smaller and higher-leverage per token).
Two local references make this cheaper than a from-scratch dig (both gitignored,
dev-only; see `BASELINE_RESEARCH.md` for their role): `baselines/spire-codex/data/*.json`
is the offline **content** half of the index (eng-only parsed cards/powers/relics/…,
so content lookups stop hitting the live API), and `baselines/spire-codex/backend/`'s
regex parsers are a working model for "generate a structured table FROM the decompile"
as a **re-runnable generator** (the M4.5 deliverable), not a one-time dump.

Honest scope: the four suggestions + the API index mine *build/load + runtime-API* gaps
to ~near-completeness (finite code); *behavior* gaps (tier-2 effect fired but wrong) still
need execution and are NOT mined here — that's M5. And the analyzer/baselib/API gain
members on version bumps, so the deliverable is a **re-runnable generator + a
diff-on-upgrade habit**, not a one-time dump. The full rationale and three-source
truth model are now canonical in `games/sts2/skills/sts2-api/grounding.md`; mined
build/load constraints live in `reference/build-constraints.md`.

**M5 — Behavior test (R2 tier 2) + Codex runtime + one-command install + optional publish.**
- ✅ **Tier-2 behavior automation — DONE (2026-07-06).** In-process self-test harness;
  card/relic/potion source drivers plus the card→power interaction all PASS live. The
  historical canary project remains named `CanaryCombo`, but combo is not a content type.
  See `games/sts2/tests/`.
- ✅ **One-command install (Claude Code) — DONE (2026-07-06).** Shipped as a native
  Claude Code plugin: repo root is the marketplace (`.claude-plugin/marketplace.json`),
  plugin at `plugins/open-mod/` (committed payload rendered by `publish.sh --plugin`),
  tool paths via `${CLAUDE_PLUGIN_ROOT}`. Install = `/plugin marketplace add
  WhiteTowerAI/open-mod` + `/plugin install open-mod@open-mod` — no clone, no manual
  `publish.sh`, no fixed cwd (the committed distribution goal, PROJECT.md §3.1). Real
  registry command is live once the files reach `main`; test locally via `/plugin
  marketplace add <repo path>`.
- ✅ **Cross-agent install + cross-platform tools — DONE (2026-07-07).** Added
  `publish.sh --portable`: renders the committed top-level `skills/` in the layout
  skills.sh (`npx skills add WhiteTowerAI/open-mod`) auto-discovers, installable into
  Codex / Cursor / OpenClaw / etc. The agent-neutral tool-path problem (no
  `${CLAUDE_PLUGIN_ROOT}` off Claude) is solved per the AgentSkills spec: tools live in
  `skills/modmaker/scripts/` and are referenced by **relative** path. The three tools
  were rewritten from Windows PowerShell to **cross-platform Python** (`build.py` /
  `launch.py` / `grep_log.py`) — regression-verified on Windows by re-running the
  CanaryCard tier-2 self-test (build 0/0 → self-drive → `Jolt played` marker → PASS).
  Also fixed a latent Git-Bash MSYS bug that had mangled `/modmaker` → `D:/Git/modmaker`
  in every rendered SKILL.md. **Not verified:** the mac/Linux tool paths (game/log dirs
  follow Steam/Godot conventions, best-effort — no non-Windows box), and the live
  `npx skills add` install into a non-Claude agent (needs that agent's env).
- ⏳ **Registry listing (later).** A lobehub / skills.sh directory entry so users can
  discover it, not just install by repo slug.
- ⏳ **Opt-in Steam Workshop publish** — still to wire.

**M5.5 — Art/sprite pipeline. ✅ COMPLETE & LIVE-VERIFIED (2026-07-08).**
Deferred out of M4 to here (after M5): a no-art element loads cleanly with the default
placeholder icon, so custom art is a quality/parity feature, not on the critical path to
a working mod.
Per needed sprite the pipeline offers **placeholder vs. generate** (placeholder = the
default, a missing sprite falls back to the template art so art never blocks). Generate
uses a **user-configured backend** (their own OpenAI-compatible image endpoint — cloud
or local; we ship the plumbing, not a bundled provider) via a provider-agnostic
`art-backend.json`. What landed this session:
- **Contract page** `sts2-api/reference/art-contract.md` — exact `res://` path + pixel
  size per sprite type (a normal card has one portrait the game loads, `1000×760`;
  606×852 full art is Ancient-rarity only and out of scope; relic/power/potion icons are
  256×256 loose PNGs — all four types now live-verified, see the M5.5 sub-steps below) +
  the placeholder-fallback mechanism + the card-portrait prompt template.
- **New tool** `tools/gen_sprite.py` (Python + Pillow; `publish.sh` auto-bundles it into
  both payloads alongside build/launch/grep). Subcommands `generate` (BYO OpenAI-compat
  HTTP), `import` (local file), `list-specs`. Normalizes any source → magenta chroma-key
  (per-spec: on for cut-out icons, off for full-bleed card portraits) → fit/resize to the
  exact contract size → place the required sprite(s) at the exact sub-paths. Verified
  live for card/relic/power/potion; relic and power emit normal + `big/`, potion emits
  one loose PNG, and card emits the `big/` portrait.
- **Pipeline wiring** — `interview.md` (art only when the user signals a custom look),
  `spec.md` (per-sprite art plan + PLAN.md art step + confirmation art clause),
  `author.md` §4 (rewritten placeholder→choice, generate branch calls `gen_sprite.py`,
  falls back to placeholder on no-backend/failure), `SKILL.md` (scope + pipeline art
  sub-step), `sts2-api/SKILL.md` (indexes art-contract.md).

Closes the art-pipeline feature gap identified in `COMPETITIVE_LANDSCAPE.md` and
`BASELINE_RESEARCH.md`.
Reference studied: `baselines/agent-sprite-forge/` (Codex sprite-gen skill — the
agent-writes-prompt + deterministic-Python-processes-pixels split, and the magenta
chroma-key/fit logic reused in `gen_sprite.py`) and `baselines/spire-codex/spine-renderer/`
(STS2 Spine-skeleton→PNG, the *reverse* direction — asset processing reference only).
**Card portrait is DONE** — live end-to-end on the dev box (BYO backend → real portrait →
`.pck` rebuild → confirmed in-game, 1000×760, 2026-07-08). **Sprite sub-steps:**
- **① relic + power — DONE & live-verified (2026-07-08).** Both are 256×256 cut-out icons
  (`fit: contain`, magenta chroma-key); size confirmed from the uniform 324 relic + 271
  power extracted PNGs and verified in-game (canary-relic "Bauble", canary-power "Smolder" —
  `verified: True`). Two findings that changed the pipeline, both fixed + re-verified:
  (a) **each needs TWO icon files** — `<slug>.png` (bar/status) + `big/<slug>.png` (relic
  detail popup / power apply-expire notification); `gen_sprite.py` now writes both via
  `extra_sub_paths`. (b) **a power/relic subclass must extend the template base**
  (`<ModName>Power`/`<ModName>Relic`), not `CustomPowerModel`/`CustomRelicModel` directly, or
  the loose-PNG icon getter stays null and the custom icon silently falls back to default
  (fixed in `recipes/power.md`). relic's `<slug>_outline.png` hover outline is left to the
  template fallback (looks fine live); we don't generate it. Also: `art-samples/` split into
  `card/relic/power/` subdirs, `--reference` auto-picks by `--spec`.
- **② potion — DONE & live-verified (2026-07-08).** The icon is 256×256 (63 extracted
  potions confirm). **This overturned the planned `.tres` emitter: potion takes a loose PNG,
  same as relic/power — no atlas.** BaseLib's `CustomPotionModel` Harmony-patches
  `PotionModel.ImagePath` to `CustomPackedImagePath`, whose docstring says a PNG path is a
  valid `Texture2D`; the "must be a `.tres`" belief was just because the un-overridden getter
  defaults to the atlas path (which a mod doesn't ship). Wiring mirrors relic/power: a
  `PotionImagePath` helper (`Exists()`+fallback) + the mod's `<ModName>Potion` base overrides
  `CustomPackedImagePath`. Two potion-specific facts: (a) **ONE file only** — potion exposes a
  single `Image` texture (bar/hover/use all reuse it), no `big/` variant (unlike relic/power);
  (b) art direction — potions are drawn **tilted ~45° right**, baked into the prompt. Generated
  "Fizz" via Poe/nano-banana, built, confirmed in-game. `gen_sprite.py` gained the `potion`
  spec; `art-samples/potion/` added (6 refs).
- **③ Ancient full art (606×852) stays out of scope** — we don't make Ancient cards.

**Sequence: after M5, before M6** — M6's heavier content types (characters especially)
want real art. orb (100×100) / enchantment (64×64) sprite sizes are also now known from
the same extracted set, but those content *types* are M6, so their art rides along there.

**M6 — Content breadth as playable vertical slices, not a checklist of classes.** Today
the pipeline covers four combat-oriented model types: **three pooled families** (card,
relic, potion — `[Pool]` required) plus **auto-discovered power** (no pool). BaseLib's
registration surface still defines the authoritative inventory of what else exists:
`CustomContentDictionary` has those 3 pooled families, **5 parallel explicit entry
points** (`AddEncounter`, `AddAncient`, `AddEvent`, `AddAct`, `AddCharacter`), and the
wider `Abstracts/` set (`CustomOrbModel`, card enchantment, run modifier, monster, pet,
rest-site
option, reward, …). But inventory is not the deliverable. Many of these types are not
useful alone: a monster needs an encounter, a keyword needs a card/power that uses it,
an enchantment needs a card to modify, and a reward needs a post-combat host. M6 is done
only when a non-programmer can describe a **playable unit**, the pipeline can build it,
and a real game scenario proves the relationship works.

### M6.0 — contracts before recipes: the Content Capability Graph

Create one lightweight, maintainer-only Markdown capability map before adding user-facing
types. For every inventoried type record seven capability facts: **registration mode**
(pooled / auto-discovered / explicit `Add*` / attached), **host or dependency**,
**verification scenario**, **observable proof**, **art contract**, **what it composes with**,
and **support level**. Keep a separate evidence ledger: STS2 engineering evidence may
advance support, while STS1/cross-game design analogies may shape scenarios but never count
as STS2 implementation proof. Keep it as documentation first — no registry code or schema
framework until a real consumer earns one. This graph prevents isolated recipes that
register but cannot participate in a mod, and becomes the common source for author routing,
scenario verification, and M7's honest capability boundary.

Support is a ladder, not a boolean:

`inventoried → grounded → build-verified → scenario-verified → pipeline-supported`

- **inventoried:** BaseLib/game surface found; no promise to users.
- **grounded:** constructor, registration, loc, host relationship and one vanilla analog
  are mined into the pack.
- **build-verified:** a Type Canary compiles, packages, loads, and registers.
- **scenario-verified:** a Scenario Canary exercises it through its real host and observes
  the intended state/behavior change.
- **pipeline-supported:** interview → common SPEC contract → scaffold/author → both proofs
  works from natural language. Only this final level may be advertised as "supported."

### Verification architecture — scenarios, not an ever-growing DRIVER switch

M5's combat harness is the first scenario adapter, not a template to duplicate per type.
M6 should factor tier-2 into a small set of reusable scenario adapters, each with
`setup → enter → drive → observe → terminal marker`:

| Scenario | Initial content families |
|----------|--------------------------|
| **CombatPlayer** | existing card/relic/potion/power; keyword, card enchantment, orb |
| **CombatEnemy** | monster + encounter; enemy intent/power |
| **MapNode** | event; later rest-site option |
| **PostCombat** | reward and encounter outcome (M6 Extra) |
| **RunStart** | character selection, starter content, character mechanic |
| **ActMap** | act/map ecosystem — explicitly deferred beyond the M6 gate |

A type contributes only its scenario contract (setup action, drive action, observable
invariant); navigation, waiting and terminal handling live once per scenario. The proof
rule therefore upgrades from "one type, one green build" to **two complementary proofs**:
(1) a **Type Canary** for registration/build/load and (2) a **Scenario Canary** for real
hosted behavior. One vertical-slice canary may prove several inseparable types — e.g. a
monster inside its encounter — rather than creating technically green but meaningless
single-class cells.

### Delivery order — playable vertical slices

1. **M6.0 Contracts & scenario foundation. ✅ LANDED 2026-07-10.** The maintainer-only
   graph is `games/sts2/tests/content-capability-graph.md`, with the support ladder,
   Type+Scenario proof rule, scenario contracts, and separate STS2-engineering vs.
   cross-game-design evidence ledgers. M6.0 also closes a verification-seam false positive:
   terminal `selftest done` is no longer eligible as an effect marker, and harness
   FAILED/timeout/early-exit return nonzero. It intentionally adds no new recipe, canary,
   registry/schema, or hypothetical adapters. Refactor only the verification seam needed
   by the first slice, not all hypothetical adapters up front.
2. **Mechanic Vocabulary Slice — keyword + card enchantment + orb. ✅ PIPELINE-SUPPORTED
   2026-07-10.** These are the language of archetypes and directly unlock M7 L2/L3.
   `CustomModifierModel` is a separate run-modifier capability (Good/Bad modifier lists),
   not a synonym for card enchantment; it is tracked outside this Core slice until its
   RunStart/UI scenario is defined. Three proof-first canaries now pass live through the
   existing `CombatPlayer` seam: Card+Keyword proves generated keyword membership plus its
   named Block rule; Card+Enchantment proves attachment/Amount plus altered `OnPlay`;
   Card+Orb proves zero-slot channel, queue presence, passive, and evoke. Lazy recipes and
   the common elements/interactions SPEC routing are wired. Custom enchantment/orb visual
   rendering remains a separate provisional art claim (mechanic support does not pretend
   it was eyeballed).
3. **Enemy Encounter Slice — monster + encounter. ✅ PIPELINE-SUPPORTED 2026-07-13.**
   Treated as one playable unit:
   enter the custom encounter, spawn the custom monster, advance an enemy action, and
   observe an intent/effect plus state delta through `CombatEnemy`. `CanaryEncounter`
   (`CanaryMite : CustomMonsterModel` + `CanaryMiteEncounter : CustomEncounterModel`) built
   0/0, and the first earned `CombatEnemy` seam observed all four signals: encounter entered,
   monster present in `Enemies`, `PECK` move executed via `MoveState`, player HP delta=6.
   `recipes/monster.md` (combined monster+encounter), the `CombatEnemy` harness section, and
   the modmaker stages (interview/spec/author/verify/SKILL) are wired. Registration:
   `CustomMonsterModel`/`CustomEncounterModel` both auto-register (no `[Pool]`); the
   correction logged is that a monster attack uses `.FromMonster(this).Execute(null)`, never
   the card `.Targeting()` (which hangs the enemy turn). Custom monster art (Spine scene) is
   provisional — enemies fall back to `creature_visuals/fallback`. A full natural-language
   user acceptance run completed on 2026-07-13 and produced a working verified mod, closing
   the final pipeline-support gate. During that run the open-mod 0.5.0 self-test template's
   nonexistent `TaskHelper` reference was found and corrected to `_ = RunAsync();`.
4. **World Node Slice — event.** Enter the custom event through `MapNode`, choose at least
   one option, and observe its consequence; nested talk/option localization is part of the
   proof, not merely a successful registration.
5. **Minimal Character Slice.** Use the character template where appropriate; prove the
   character appears in selection, starts a run, owns valid starter content, and exposes at
   least one small mechanic/vocabulary combination. This is a vertical slice, **not** a full
   production-size card pool, but it is enough for M7 to reason about archetype identity
   against a real buildable target.
6. **M6 Extras — reward, rest-site option, pet.** Add by user value and scenario reuse after
   Core is green. They do **not** block M7. **Act is outside the M6 completion gate**: it is
   an ecosystem-sized unit and gets a later milestone after the underlying node/encounter
   capabilities exist.

For every slice, use proof-first cadence: **declare host + observable invariant → ground
the exact APIs and loc/art contract → write only the type-unique recipe material → wire the
pipeline → run Type + Scenario canaries → append real failures to `errors.md`**. Designing
the proof before mining prevents a recipe whose only success condition is "it loaded."

### Anti-bloat — contain stage architecture and maintenance, not just token count

Recipes remain lazy-loaded and `tests/` remains maintainer-only/unshipped. Shared pooling,
loc and hook foundations remain single-sourced in `mechanics.md` /
`build-constraints.md`. But M6 must also stop per-type prose from spreading through every
stage: `spec.md` should evolve toward a **common SPEC envelope + lazy type contract**;
`interview.md` and `SKILL.md` keep compact capability/routing tables; `author.md`,
`scaffold.md`, and `verify.md` dispatch to the selected type/scenario contract rather than
accumulating another full branch per type. Refactor incrementally with each slice — do not
build a generic framework before two real shapes prove the abstraction.

**M6 Core completion gate:** Mechanic Vocabulary, Enemy Encounter, World Node, and Minimal
Character slices all reach **pipeline-supported**, with their Type and Scenario proofs
recorded. Reward/rest-site/pet are Extras and do not block M7; Act is separately deferred.
M5's live tier-2 foundation is already complete, so M6 begins at M6.0. The full
BaseLib inventory and its evidence are maintained in
`games/sts2/tests/content-capability-graph.md`; this section is the execution source of
truth.

**M7 — Interactive, proactive interview for non-programmers.** NEW major milestone
(promoted 2026-07-09 from the former "M5.7 harder interview" — that 0.x scope was only the
L1 decomposition slice; the real target is far bigger). **The headline is the user's
experience, not the design theory.** Our audience is complete beginners with **no
programming experience**; eventually the skill should feel like a knowledgeable
collaborator that *proactively interviews* the author about the details of what they're
making — not a passive transcriber that scaffolds whatever one sentence it's handed. It
should help them not only *design* the mod but also think through everything they wouldn't
know to consider on their own: **edge cases, balance, interplay/联动, and extensibility.**

Today the interview is a transcriber: one sentence → one element, no push-back, no "did you
think about X?". M7 turns it into an active partner that asks the right follow-up questions
at the right moments and surfaces the concerns below **so the author doesn't have to already
know them**:

- **Edge cases** — what happens on 0 targets, empty hand/draw pile, at 1 HP, when a value
  goes negative, when the effect stacks with itself, when combat ends mid-effect? A beginner
  won't anticipate these; the interview should raise the ones that apply to their element.
- **Balance** — is this trivially overpowered or dead-on-arrival? (grounded in the MegaCrit
  design language below — risk-vs-reward, "a card too weak to pick is basically not a card").
- **Interplay (联动)** — how this element interacts with itself, with other elements in the
  same mod, and with the base game. This is the ladder that used to *be* M7; it's now one of
  several proactive concerns (see the L1–L4 ladder below).
- **Extensibility** — is this a one-off, or the seed of something bigger (a set, an
  archetype, a character)? Shape the SPEC so growing it later doesn't mean a rewrite.

The **design-knowledge** that powers the balance + interplay questions is grounded in
MegaCrit's stated design language (research 2026-07-09, sources in BASELINE_RESEARCH.md):
*"The core design of Slay the Spire is risk versus reward"* (Giovannetti); cards are
tactical, **relics/mechanics are the strategic frame**; changing one card *"has ramifications
on the cards in that strategy"* — the unit of design is the **archetype**, not the card; a
run pivots from front-loaded power into an **exponential scaling engine**, never flat "the
math just gets bigger." STS2's own content is designed this way — a character's pool is 2-3
**archetypes** ("machines"), each built from cards that play distinct roles.

The **interplay (联动)** concern specifically is a **ladder of four levels**, not one thing:

- **L1 — technical dependency** (A triggers B; e.g. a card applies a custom power that
  fires on the enemy's turn). ✅ Already shipped: `spec.md`'s interaction block + the
  tier-2 interaction harness (historical `CanaryCombo`). M7 folds the old M5.7 multi-element **intake
  decomposition** in here: interview must split a multi-element sentence into elements,
  surface their dependency pairs (source → dependent + the dependent's own marker), keep
  the single-element fast path un-regressed, and feed the block spec/harness already
  consume.
- **L2 — resource loop** (an **enabler** produces a resource, a **payoff** spends it; e.g.
  Necrobinder "Gain X Souls" skills ↔ "Consume all Souls" attacks). The interview gains
  the vocabulary to ask: what's your resource, who produces it, who spends it, is the loop
  closed?
- **L3 — archetype identity** (a shared resource/keyword vocabulary + a play-feel that ties
  a *set* of elements into one coherent theme — Silent = poison/discard/Sly, Ironclad =
  Strength/Exhaust). Requires designing a small **content pack**, not one element — so it
  depends specifically on M6 Core's Mechanic Vocabulary + Minimal Character slices
  (keyword/orb and a real buildable character target), not on every BaseLib type being done.
- **L4 — run rhythm & risk-reward advisor** (the highest rung, closest to "think like
  MegaCrit"): does the design scale into act 3, or does the payoff never come online in a
  normal fight? where's the meaningful trade-off / commit moment? is it degenerate (needs a
  rarity/cost/scope constraint the way Dual Wield was limited to Skills)? The interview
  points out a design flaw *before* code is written.

**Sequenced AFTER the M6 Core gate (locked 2026-07-10):** the full L3/L4 advice
("help me design a character's three archetypes") becomes meaningful when Mechanic
Vocabulary and the Minimal Character Slice are both `pipeline-supported` — there is then
a real keyword/orb vocabulary and a buildable character target to advise against. M7 does
**not** wait for M6 Extras (reward/rest-site/pet), and Act is outside this dependency. The
L1 decomposition slice depends only on the already-live interaction harness and MAY be pulled
forward if a concrete multi-element need arises before M6 Core; the rest waits.

**The central tension: proactive, but not exhausting.** The whole point is that the
interview *proactively* raises edge cases / balance / interplay / extensibility a beginner
wouldn't think of — but a complete beginner is also the person most easily overwhelmed by a
wall of questions. So M7 is NOT "ask everything every time." The proactive concerns are
injected as **judgment** (a new pack page, likely `reference/design-principles.md`,
distilling the 9 MegaCrit principles + an edge-case checklist per element type), and the
interview raises **only the few that actually apply** to what this author is making,
**one or two at a time, in plain non-technical language**, with a sensible default offered
(the beginner can always say "you decide"). A one-line single-element ask must still finish
fast — proactive means "catches the important thing they'd have missed", not "interrogates".

**Reference baseline for the interview mode: CCGS's Collaborative Design Principle**
(`baselines/Claude-Code-Game-Studios-main/docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` — the user
found CCGS's interview UX good and asked us to model M7 on it). It's a mature, worked-out
version of exactly the proactive-collaborator interview M7 wants; borrow these patterns
(adapting them to *our* one-shot, non-programmer, single-mod scope — CCGS is a multi-agent
studio for full games, so we take the interaction shape, not its gate/agent machinery):
- **Question → Options → Decision → Draft → Approval** loop at every decision point — the
  agent is a *collaborative consultant*, never an autonomous generator or a passive
  order-taker. Maps onto our interview → spec → (approve) → scaffold flow.
- **Explain → Capture** two-step: write the full expert reasoning (pros/cons, trade-offs,
  comparable STS2 content) in conversation *first*, then present the decision as a compact
  selectable UI via **`AskUserQuestion`** (concise labels + one-line trade-off each). We
  already have this tool; M7 should use it for the constrained choices instead of walls of
  markdown.
- **Good vs bad question patterns** (their §"How Agents Should Ask Questions"): multiple-
  choice-with-reasoning / constrained-options-with-trade-offs / open-ended-with-context are
  good; too-open ("what should it be like?"), leading/assuming, and context-free binaries are
  bad. This is a ready-made rubric for `interview.md`'s question style.
- **Always recommend, but defer the decision** — mark a "(Recommended)" option and give the
  reasoning, but the author picks (they can always say "you decide"). Fits our beginner
  audience: never blocks, never bulldozes.
- **Scope-based depth routing** (their `/quick-design` vs `/design-system` split): a small,
  clearly-scoped ask gets a lightweight fast path; only a larger/ambiguous one escalates to
  the deeper design conversation. This is CCGS's own answer to our "proactive but not
  exhausting" tension — the depth of the interview scales with the request.
- **Incremental section writing** (skeleton first, write each section as approved) — matches
  our "files are state" architecture (SPEC.md/PLAN.md), keeps live context small, and lets a
  compacted/crashed session resume from the file.

**Acceptance bar** (how M7 stays testable despite being experience/judgment-driven):
1. **Edge case** — given a request with an obvious unhandled edge case (e.g. a card that
   targets an enemy with no "what if there's no valid target" story), the interview raises
   it rather than silently scaffolding a crash.
2. **Balance** — given a trivially overpowered or dead-on-arrival design, the interview
   flags it and offers a saner default.
3. **Interplay** — a multi-element / archetype request is decomposed into a coherent element
   set with its interaction block (the old M5.7 bar, now one of four).
4. **Extensibility** — a request that's clearly the seed of a set/character is shaped so it
   can grow without a rewrite.
5. **Not exhausting** — a clear one-line single-element ask still completes without a
   design interrogation (no regression to the fast path).

**Anti-bloat** (same constraint as M6): the always-loaded interview triage must not fatten —
the design/edge-case pages are lazy-loaded and consulted, not prepended to every run.

## 6. Decisions (locked 2026-07-01)

1. **M0 machine: available.** We have a box with STS2 + .NET 9 we can run the
   de-risk prototype on. → M0 runs for real; its gate is live.
2. **First element type: relic.** Simplest trigger model, matches the
   "Gambler's Coin" example.
3. **Reuse posture: core self-contained + reuse at the edges.** The core loop
   (scaffold/author/build/verify/repair) is self-contained and portable. The shipped
   tier-2 path is also self-contained (generated in-process harness); spire-codex and
   decompiles are maintainer grounding inputs, not runtime dependencies.
4. **Repo (historical decision, resolved in M2).** The gate passed and source was laid
   out under `games/sts2/` in this repo; see §1 for the current structure.

## 7. M0 de-risk checklist ✅ COMPLETED

> **Historical checklist:** M0 and M1 passed on 2026-07-01. The steps below are
> preserved as the original gate, not current operating instructions. Current build and
> tier-2 commands are in `CLAUDE.md` and `games/sts2/tests/canary.md`.

This was manual validation on the STS2 box (no skill code yet). Success here
unlocked M1+ and confirmed §1's structure is worth building.

**Prereqs to confirm on the machine:** STS2 installed (note the install path and
whether it's the main or beta branch), .NET SDK 9.0+ (`dotnet --version`), and —
only if needed — MegaDot 4.5.1 mono.

**R1 — build/publish (target: one command → `.dll`+`.pck` in `mods/`):**
1. `dotnet new install Alchyr.Sts2.Templates`
2. `dotnet new` a Content mod named `ProbeMod` (no spaces).
3. `dotnet build` → confirm `ProbeMod.dll` + `.json` land in `mods/ProbeMod/`.
4. Try the **PckPacker shortcut first** (uncomment the package ref) → does
   `dotnet build` alone produce `.pck` with NO MegaDot? Record yes/no.
5. If no: `dotnet publish /p:GodotPath="…MegaDot…"` → confirm `.pck` appears.
   Note whether `--export-pack "BasicExport"` needs export templates.
6. Launch STS2 → Settings → Mod Settings → confirm ProbeMod is listed.
→ **Deliverable:** the exact standardized build command(s) for `build.md`.

**R2 tier 1 — load verification (target: greppable proof from the log):**
7. Add `MainFile.Logger.Info("[T2MOD-SELFTEST] ProbeMod loaded ok")` to init;
   rebuild.
8. Create `steam_appid.txt` (contents `2868840`) in the game dir; launch
   `SlayTheSpire2.exe` from a script; wait N seconds; quit.
9. Grep `%appdata%/SlayTheSpire2/logs/godot.log` for the marker and for any
   error lines referencing ProbeMod.
→ **Deliverable:** the launch+wait+grep recipe for `verify.md`.

**R2 tier 2 — behavior probe (target: pick the mechanism, don't fully build):**
10. Check the dev console `help` list for a scripted-spawn / scripted-encounter
    command.
11. Try a minimal Godot `SceneTree` test script (godogen pattern) that loads the
    relic and `GD.Print("ASSERT PASS/FAIL")` — does STS2's setup allow this?
12. Skim STS2MCP's README for how it exposes live state.
→ **Deliverable:** a recommendation of tier-2 mechanism (SceneTree vs STS2MCP)
   for `behavior-test.md`, or "tier-2 deferred" with the reason.

**M0 gate:** R1 produces a loadable mod via CLI, and R2 tier-1 proof is
greppable. If both pass → proceed to M1 (hand-build the golden relic). If R1
fails → the CLI-publish assumption is wrong, revisit. If only R2 tier-1 fails →
reassess the verification approach before building the skill around it.


