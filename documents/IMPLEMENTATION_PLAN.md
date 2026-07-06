# Implementation Plan: STS2 Text-to-Mod Skill

> Companion to PROJECT.md, BASELINE_RESEARCH.md, R1_R2_FEASIBILITY.md,
> COMPETITIVE_LANDSCAPE.md. This is the build blueprint: directory layout, the
> skill pipeline, the game pack shape, and a phased milestone plan.
> Status: living plan. Written 2026-07-01. **M0–M3 + M4 (potion R1, card R2, and the
> BloodAndFury two-card/two-power R3) gates all PASSED** (see M0_RESULTS.md …
> M4_RESULTS.md). The skill under `games/sts2/` reproduces the golden relic from one
> sentence, the bounded `repair.md` loop fixes broken specs within the retry cap, and
> the potion/card/power recipes now produce loading, firing elements end to end.
> **NEXT = M4.5 (pre-mine the toolchain to kill runtime decompilation), NOT M5** —
> the BloodAndFury run showed spire-codex + baselib grounding misses build/load-time
> validator rules (analyzer STS001, baselib throws) that are offline-minable. Art
> pipeline + harder interview still open from M4. See M4.5 in §5 and memory
> `[[premine-offline-no-runtime-decompile]]`.

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

Mirrors godogen's engine-split so multi-game (Phase 2) is a copy-paste of the
game folder, and the runtime split so Claude Code / Codex both work.

```
t2mod/                              # repo root
├── README.md                       # human-facing
├── PROJECT.md / *.md               # the research docs (this set)
│
├── games/
│   └── sts2/                       # the STS2 "game pack" + skill (Phase 1)
│       ├── skills/
│       │   ├── modmaker/           # the orchestrator skill
│       │   │   ├── SKILL.md        # entry / pipeline (the only always-read file)
│       │   │   ├── interview.md    # one-round intake → mod spec
│       │   │   ├── spec.md         # write SPEC.md (the design contract)
│       │   │   ├── scaffold.md     # dotnet new + manifest wiring
│       │   │   ├── author.md       # write the C# element + localization + art
│       │   │   ├── build.md        # dotnet build/publish → .dll+.pck (R1)
│       │   │   ├── verify.md       # launch + log-assert self-test (R2 tier 1)
│       │   │   ├── behavior-test.md# in-game effect check (R2 tier 2, best-effort)
│       │   │   ├── repair.md       # read log → diagnose → fix → re-verify loop
│       │   │   ├── finalize.md     # package; optional Workshop publish
│       │   │   └── quirks.md       # STS2/BaseLib gotchas
│       │   └── sts2-api/           # the GAME PACK (knowledge, queried on demand)
│       │       ├── SKILL.md        # how to query the pack
│       │       ├── content-models.md   # Card/Relic/Potion/Power model + Custom*Model
│       │       ├── commands.md         # DamageCmd/PowerCmd/... command catalog
│       │       ├── recipes/            # known-good patterns per element type
│       │       │   ├── relic.md
│       │       │   ├── card.md
│       │       │   └── potion.md
│       │       ├── manifest.md         # Mod.json schema + rules
│       │       ├── localization.md     # *.json format + analyzer behavior
│       │       ├── art.md              # image sizes/paths/placeholders
│       │       ├── errors.md           # error → fix catalog (grows over time)
│       │       └── grounding.md        # how to use spire-codex / decompile when the pack lacks it
│       ├── scaffold/               # our thin wrapper over Alchyr templates
│       └── tools/                  # python/shell helpers (build, launch, log-grep)
│
├── runtimes/                       # per-agent adapters (godogen pattern)
│   ├── claude-code/                # Phase 1 target
│   └── codex/                      # Phase 2
│
└── shared/
    ├── hooks/                      # stop-hook completion gate (godogen pattern)
    └── skills/                     # anything game-agnostic
```

Note: the actual on-disk skill format for Claude Code (frontmatter, invocation)
is finalized in the runtimes layer — a `publish` step can render the same source
into Claude Code and Codex shapes (godogen does exactly this with
`scripts/publish/*`).

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
  6. VERIFY (verify.md)        — launch via steam_appid.txt, wait, grep godot.log
  |     for the self-test marker + absence of mod-referencing errors. (R2 tier 1.)
  |     On failure → REPAIR.
  |
  7. BEHAVIOR TEST (behavior-test.md) — BEST EFFORT: SceneTree test script and/or
  |     STS2MCP live-state to confirm the effect fires. Clearly report tier
  |     achieved. (R2 tier 2.)
  |
  8. REPAIR (repair.md)        — shared sub-loop invoked by 5/6/7: read the log,
  |     consult errors.md, diagnose, fix, re-run the failed stage. Bounded retries.
  |
  9. FINALIZE (finalize.md)    — the mod works locally; summarize; OFFER (opt-in)
        Workshop publish via megacrit/sts2-mod-uploader.
```

## 3. The game pack (`sts2-api`) — our moat, concretely

Purpose: pre-digest STS2's community-reverse-engineered knowledge so the LLM
writes *correct* code without live-decompiling every time. Queried on demand
(like godogen's `godot-api`), never dumped wholesale into context.

What each file holds and where it's sourced from:

| File | Content | Sourced from |
|------|---------|--------------|
| `content-models.md` | Every element = a `Model`; the BaseLib `Custom*Model` base classes and which properties to override | BaseLib-Wiki, ModTemplate |
| `commands.md` | Catalog of `Cmd`s (`DamageCmd.Attack`, `PowerCmd.Apply<T>`) + BaseLib `CommonActions` shortenings | decompiled base game, BaseLib |
| `recipes/*.md` | Copy-adaptable known-good pattern per element type, each a full working example | ModTemplate + base-game analogs |
| `manifest.md` | `Mod.json` schema, id-immutability, `affects_gameplay`, version rules | ModTemplate wiki |
| `localization.md` | `localization/eng/*.json` format; the analyzer auto-report/generate behavior | StS2ModAnalyzers |
| `art.md` | Image paths + exact sizes (card 1000x760, etc.); placeholder-first workflow AND the BYO-backend generate path (per-sprite placeholder-vs-generate choice, user-configured image-gen API/local model) — see PROJECT.md §7.1 | ModTemplate wiki |
| `errors.md` | **Error signature → fix** catalog; grows every time repair succeeds | our own runs (compounding asset) |
| `grounding.md` | When the pack lacks an answer: query spire-codex API / decompile sts2.dll | spire-codex, decompiling wiki |

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

- **R1 (build.md):** standardize on `dotnet build` + PckPacker if the prototype
  confirms it (no MegaDot); else `dotnet publish /p:GodotPath=...`. Path
  discovery is automatic (template props); we only pass overrides. Fail-fast
  errors from the template feed `repair.md`.
- **R2 tier 1 (verify.md):** the guaranteed check. Scaffolding always injects a
  `MainFile.Logger.Info("[T2MOD-SELFTEST] ...")` marker after registration.
  Launch (`steam_appid.txt`=2868840) → wait → grep `godot.log`. This proves
  "installs + loads + registered" — already beating raw-AI mods. **Note: this
  is exactly the tier modmixer stops at** ("a green build does NOT mean it
  loads"; their loop verifies loads-without-crashing, not behavior). Parity here,
  not advantage.
- **Bridge option (from modmixer):** instead of only grepping `godot.log`,
  consider a small companion "bridge" mod (BaseLib+Harmony) that streams
  load/runtime errors over localhost, attributed per-mod — cleaner than log
  scraping. Check first whether **STS2MCP already provides this channel** (fits
  "reuse at the edges"); decide during M0's tier-2 investigation.
- **R2 tier 2 (behavior-test.md) — THE differentiator:** best effort, two
  candidate mechanisms to prototype and pick between:
  1. **SceneTree test script** (godogen's `test/TestXxx.cs` pattern) — STS2 is
     Godot, so a `SceneTree` script may load the element and assert via
     `GD.Print("ASSERT PASS/FAIL")`, no full run needed. Cheapest if it works.
  2. **STS2MCP live-state** — drive a real run and read game state via the
     existing MCP mod. Most faithful, more setup.
  Always report which tier was reached; never claim effect-verified on tier 1.
  **This tier is where we beat modmixer** — the founder confirmed they explicitly
  cannot "play the game to test the mod" and hand behavioral correctness back to
  the user. Resource this; it is the headline, not a footnote.

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

**M4 — Breadth within STS2.** Add `recipes/card.md`, `recipes/potion.md`; handle
2-3 more element types (all pooled/combat: card, potion, power). Harden the interview
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
> **Scope note:** M4's "2-3 more element types" was *consumed* by card + potion +
> power — all **pooled/combat elements** sharing relic's foundation. The larger,
> structurally different content types (event, character, monster, orb, …) are **not**
> covered here; they are their own milestone line, **M6** below.

**M4.5 — Pre-mine the toolchain: kill runtime decompilation. ← NEXT (do before M5).**
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
already automates scaffold→build→verify. Build one minimal mod per element type
(relic / potion / card / power / combo), run build + tier-1, as a repeatable
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
dev-only — memory `[[baselines-local-reference]]`): `baselines/spire-codex/data/*.json`
is the offline **content** half of the index (eng-only parsed cards/powers/relics/…,
so content lookups stop hitting the live API), and `baselines/spire-codex/backend/`'s
regex parsers are a working model for "generate a structured table FROM the decompile"
as a **re-runnable generator** (the M4.5 deliverable), not a one-time dump.

Honest scope: the four suggestions + the API index mine *build/load + runtime-API* gaps
to ~near-completeness (finite code); *behavior* gaps (tier-2 effect fired but wrong) still
need execution and are NOT mined here — that's M5. And the analyzer/baselib/API gain
members on version bumps, so the deliverable is a **re-runnable generator + a
diff-on-upgrade habit**, not a one-time dump. Full rationale + the "three sources of
truth" diagnosis: memory `[[premine-offline-no-runtime-decompile]]`.

**M5 — Behavior test (R2 tier 2) + Codex runtime + one-command install + optional publish.**
Pick the tier-2 mechanism from M0/M1 findings; add the Codex adapter; **package
open-mod for one-command install from a skill registry** (e.g. `npx skills add
open-mod` / skills.sh — the committed distribution goal, PROJECT.md §3.1: no clone,
no manual `publish.sh`, no fixed working dir); wire opt-in Workshop publish. This is
the full-fat version.

**M5.5 — Art/sprite pipeline (REQUIRED; PROJECT.md §7.1).** Deferred out of M4 to
here (after M5): a no-art element loads cleanly with the default placeholder icon, so
custom art is a quality/parity feature, not on the critical path to a working mod.
Per needed sprite, the interview offers **placeholder vs. generate**; generation uses
a **user-configured backend** (their own image-gen API or a local model — we ship the
plumbing, not a bundled provider); output lands at the correct path/size for a
PckPacker rebuild (card 1000x760, etc. — see `art.md`). Closes the one concrete
feature gap vs. AgentTheSpire (memory `[[competitor-agentthespire]]`). Reference when
we build this: `baselines/spire-codex/spine-renderer/` (gitignored, dev-only — memory
`[[baselines-local-reference]]`) is a working Node.js STS2 Spine-skeleton→PNG/WebP/GIF
renderer — a solved implementation of "STS2 asset → image" to study or adapt for the
generate path. **Sequence: after M5, before M6** — M6's heavier content types
(characters especially) want real art, so the art path should exist first.

**M6 — Content-type breadth: beyond pooled combat elements.** Today the pipeline
covers the **four pooled/combat elements** (relic, potion, card, power). The authoritative
scope of "what else STS2 mods can be" is BaseLib's own registration surface, mined from
the decompile: `CustomContentDictionary` has a `PoolTypes` dict with **exactly 3 pooled
model families** (`CardModel`/`RelicModel`/`PotionModel` — these need `[Pool]`, are what
STS004 guards; power shares the `Custom*Model`+flat-loc base but is auto-discovered, no
pool), **plus 5 parallel non-pooled registration entry points** (`AddEncounter`,
`AddAncient`, `AddEvent`, `AddAct`, `AddCharacter`), **plus the full `Custom*Model` set
in `Abstracts/`** (also `CustomOrbModel`, `CustomEnchantmentModel`/`CustomModifierModel`,
`CustomMonsterModel`, `CustomPetModel`, `CustomRestSiteOption`, `CustomReward`, …). These
are structurally *different* from pooled elements (own registration path, nested loc
trees like `AncientEventModel`'s `.talk.*`, or ~14 loc keys + a select-screen for
characters) — each is a recipe-sized (or larger) unit of work, **not** a new field on an
existing recipe. Sequence by structural weight:
- **Tier A (medium, do first):** event, keyword (`CardKeyword`), enchantment/modifier, orb.
- **Tier B (medium-heavy):** monster **+** encounter (two layers), pet, rest-site option, reward.
- **Tier C (heaviest, defer):** character, act.

Each type follows the proven cadence: **scout the decompile structure → write
`recipes/<type>.md` → wire the interview/author dispatch → add one canary cell**.

**Anti-bloat is a hard design constraint of M6** (raised 2026-07-06): more types must
not fatten the pipeline. What the architecture already protects: recipes are
**lazy-loaded** (a run reads only the one matching SPEC's element — 4 recipes = 1115
lines total but any run pulls ~200–380), and the canary/golden set is **dev-only, never
shipped** (`publish.sh` excludes `tests/`), so neither grows per-run context. What *does*
grow and must be contained: the **always-loaded** triage in `interview.md` + the
`SKILL.md` routing table, and the **maintenance surface** (each type = recipe + canary +
errors entries to re-mine on version bump). M6 rules: (1) keep type triage as a compact
decision **table**, O(one row/type), never a paragraph per type; (2) recipes stay
lazy-loaded and `tests/` stays unshipped (don't regress the current architecture);
(3) shared foundations (pooling, loc derivation, hooks) live once in `mechanics.md` /
`build-constraints.md` — a new recipe states only what's **unique** to its type, never
restates the base. **Depends on M5**: tier-2 behavior automation must land first, or
verifying each new type's effect falls back on the user's eyes and the cost explodes.
Full type inventory + the "3 pooled vs 5 parallel entry points vs full Abstracts set"
structural finding: memory `[[sts2-content-type-inventory]]`.

## 6. Decisions (locked 2026-07-01)

1. **M0 machine: available.** We have a box with STS2 + .NET 9 we can run the
   de-risk prototype on. → M0 runs for real; its gate is live.
2. **First element type: relic.** Simplest trigger model, matches the
   "Gambler's Coin" example.
3. **Reuse posture: core self-contained + reuse at the edges.** The core loop
   (scaffold/author/build/verify/repair) is self-contained and portable.
   Tier-2 behavior verification and grounding reuse **STS2MCP** and
   **spire-codex** as optional dependencies.
4. **Repo: defer.** Do NOT `git init` or lay down the skeleton yet. Build the
   directory structure (§1) only after M0's gate passes, so we don't scaffold
   against unvalidated assumptions.

## 7. M0 de-risk checklist ✅ COMPLETED

> **This checklist is done** — M0 and M1 both passed on 2026-07-01 (M0_RESULTS.md,
> M1_RESULTS.md). Kept as the historical record of what was validated and how.
> The current next step is **M2** (skill skeleton driving `recipes/relic.md`).

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


