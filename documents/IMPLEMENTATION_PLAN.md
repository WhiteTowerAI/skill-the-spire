# Implementation Plan: STS2 Text-to-Mod Skill

> Companion to PROJECT.md, BASELINE_RESEARCH.md, R1_R2_FEASIBILITY.md,
> COMPETITIVE_LANDSCAPE.md. This is the build blueprint: directory layout, the
> skill pipeline, the game pack shape, and a phased milestone plan.
> Status: living plan. Written 2026-07-01. **M0 and M1 gates PASSED** (see
> M0_RESULTS.md, M1_RESULTS.md); the `sts2-api` game pack is now being seeded
> (`documents/sts2-api/`). Next: M2 (skill skeleton).

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

**M2 — Skill skeleton, happy path.** Orchestrator `SKILL.md` + interview/spec/
scaffold/author/build/verify stages + a first `recipes/relic.md`. Goal: the
skill reproduces M1's relic from one sentence, no repair needed.

**M3 — Repair loop + errors.md.** Add `repair.md` and seed `errors.md` from the
failures hit during M1/M2. Deliberately feed a few broken specs and confirm the
loop diagnoses → fixes → re-verifies within the retry cap.

**M4 — Breadth within STS2 + art pipeline.** Add `recipes/card.md`,
`recipes/potion.md`; handle 2-3 more element types. Harden the interview for
ambiguous requests. **Build the art/sprite pipeline (PROJECT.md §7.1, REQUIRED):**
per needed sprite, the interview offers placeholder vs. generate; generation uses
a **user-configured backend** (their own image-gen API or a local model — we ship
the plumbing, not a bundled provider); output lands at the correct path/size for a
PckPacker rebuild. Closes the one concrete feature gap vs. AgentTheSpire.

**M5 — Behavior test (R2 tier 2) + Codex runtime + optional publish.** Pick the
tier-2 mechanism from M0/M1 findings; add the Codex adapter; wire opt-in
Workshop publish. This is the full-fat version.

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


