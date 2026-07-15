# Project Brief: Text-to-Mod Skill

> This document describes the intent, scope, and design of the project.
> Its primary audience is an AI coding agent (Claude Code / Codex) that will
> help build and iterate on this project. It is written to convey *what we
> want to build and why*, so the agent can reason about tradeoffs and make
> good engineering decisions.
>
> Status: living brief; core decisions remain locked. The concrete skill/package shape
> and one-command installation described below shipped in M5. Current execution status
> lives in `CLAUDE.md` and `IMPLEMENTATION_PLAN.md`.
>
> Decisions locked (2026-07-01):
> - **First target game:** Slay the Spire 2.
> - **Local game assumed installed** so we can launch it and close the loop.
> - **First agent runtime:** Claude Code (Codex is a later target).

---

## 1. One-line summary

A **skill** (usable by Claude Code and Codex) that lets ordinary, non-programmer
players create game mods just by describing what they want in natural language.
Goal: **text-to-mod** — the user says what they want, the skill does *all* the
engineering work and hands back a mod that actually loads and runs in-game.

First target: **Slay the Spire 2**.

## 2. Strategy: one game first, then a platform

We deliberately do NOT start with a general-purpose tool. We start with a
**mod studio for one specific game (Slay the Spire 2)**, get the full loop
working end to end, and only then generalize into a universal "make a game mod"
tool.

- **Phase 1 (now):** nail text-to-mod for Slay the Spire 2.
- **Phase 2 (later):** turn the game-specific knowledge into a reusable
  template (see §10 "game pack") so we can add more games — and eventually let
  the community add games — turning a one-game tool into a platform.

## 3. What a "skill" is here

A **skill** is a package that a coding agent (Claude Code or Codex) loads to gain
a specialized capability — instructions + scripts + reference material the agent
follows. The user installs it once, then invokes it by describing what they want.

The concrete shape is now shipped: editable source under `games/sts2/`, a native Claude
Code plugin under `plugins/open-mod/`, and a portable Agent Skills tree under `skills/`.
`publish.sh` renders all three install/development shapes from the same source.

### 3.1 Distribution: one-command install delivered

The shipping experience no longer requires a clone, manual `publish.sh`, or a fixed
working directory:

- **Claude Code:** `/plugin marketplace add WhiteTowerAI/open-mod`, then
  `/plugin install open-mod@open-mod`.
- **Portable Agent Skills:** `npx skills add WhiteTowerAI/open-mod` for Codex, Cursor,
  OpenClaw, and other compatible consumers.

The Claude plugin uses `${CLAUDE_PLUGIN_ROOT}` for cwd-independent tool paths; the portable
shape bundles relative Python tools under the skill. This closes the installation-mechanism
goal established at M2. Remaining distribution work is narrower: registry-directory
**discoverability**, a live install/run in a non-Claude agent, and macOS/Linux live
verification. Windows + Claude Code is the fully proven end-to-end path today.
## 4. The user and the problem

**Who:** a Slay the Spire 2 player who enjoys the game but cannot program at all.

**Why it's painful today:** if such a player just asks a raw AI to "make me a
mod," the AI guesses at the game's rules and conventions — and STS2 has *no
official mod API*, so even skilled help is working from community-reverse-
engineered knowledge. The result almost always fails to install or fails to run.
Making a working mod today requires knowing the game's mod format (`Mod.json`),
C#/Harmony patching, the build tooling, and packaging — none of which a normal
player has.

**What success looks like for them:** they type one sentence and, a short while
later, the thing they described is actually playable in their game — without
writing or understanding a single line of code.

## 5. First target game: Slay the Spire 2 — modding facts

Verified 2026-07-01 (community sources; the scene is young and moving fast, so
re-verify before building):

- **Engine:** a MegaCrit fork of **Godot 4.5.1** (the original STS was Java/LibGDX;
  the sequel is a different stack entirely).
- **Mod language / format:** mods are written in **C#**, identified to the game
  by a **`Mod.json`** manifest, alongside model/data definitions and
  localization files. Code behavior is patched at runtime via **Harmony**.
- **No official mod API.** Nearly all modding knowledge is community-gathered by
  decompiling the game (e.g. the `spire-codex` project). This is exactly the gap
  our **game pack** (§10) fills.
- **Built-in mod loader (good news for us):** the launcher has a
  **"Load with mods"** option, and STS2 shipped with an integrated mod loader
  from day one — so launching the game with our mod for the closed-loop test
  (§6 step 3) is feasible.
- **Steam Workshop: LIVE.** Verified 2026-07-01 — the STS2 Workshop hub
  (`steamcommunity.com/app/2868840/workshop/`) is open and the community is
  already publishing and subscribing to mods (30+ items on the browse page;
  individual items show working Subscribe buttons). So distribution *can* go
  through Workshop subscribe, not just manual file copy. Our core loop still
  builds and tests the mod **locally** ("Load with mods"); publishing to
  Workshop is an optional final step (see §8).
- **BepInEx / dev console:** community uses BepInEx for script injection; the
  dev console (locked in the EA build) has been re-enabled by the community and
  is useful for testing.

> ⚠️ Prior art to be aware of: a **"STS2 Modding Assistant MCP"** already exists
> on Nexus Mods (mod #345). It connects to Claude Code / Cursor / etc. and
> exposes ~151 tools to decompile the game and generate mods. It is an
> MCP + general tool-set aimed at people comfortable driving an AI. Our
> differentiator is the opposite end: a **one-sentence, non-programmer-facing
> text-to-mod flow**, backed by a curated **game pack** and an **auto-repair
> closed loop**. We should study it, not ignore it. (§12)

## 6. What "text-to-mod" means in practice — the user journey

From the user's point of view (example uses a "Gambler's Coin" relic idea — a
Slay the Spire concept, not the Balatro Joker from the original notes):

1. **Install (once, ~1 min).** The player runs one command in their AI assistant
   to install our skill. Like installing an app — ready to use immediately.

2. **Describe the idea (like chatting).** The player types plainly, e.g.:
   > "Make me a relic called 'Gambler's Coin', fairly high rarity. Effect: at
   > the start of each combat there's a 50% chance I gain double energy that
   > turn, and a 50% chance I gain no energy that turn."

3. **The tool works automatically (visible, step by step).** The player just
   waits and watches it:
   - ✅ Understand the idea and translate it into game-recognized settings
     (relic type, rarity, tier, trigger, effect).
   - ✅ Write the relic's actual C# code and `Mod.json` entry.
   - ✅ Wire up the relic art (placeholder image first, so it's at least visible).
   - ✅ Package the mod and put it in the game's correct mods location.
   - ✅ Auto-launch the game ("Load with mods") to test, confirming the relic
     really appears in-game and its effect really triggers.

4. **Player verifies in-game.** The player starts a run, obtains the "Gambler's
   Coin" relic, and the effect actually works. From one sentence to playable,
   with zero code written by the user.

**When something breaks:** the tool reads the game's own error output/logs,
fixes itself, and re-tests. This **error → auto-repair → re-test** loop is the
single biggest difference between us and "a user just poking at a raw AI."

## 7. Scope of engineering tasks the skill owns

The skill is responsible for the entire pipeline (per §6):

- Interpreting the natural-language request into a concrete mod spec.
- Scaffolding the mod in the game's correct format / structure.
- Generating the code, config, and manifest to the game's conventions.
- Preserving unusual mechanic ideas and compiling them through BaseLib-first capability
  composition plus maintainer-grounded Harmony/Publicizer adapters when no public seam
  exists. The user never configures patches, local game references, or decompilation.
- Providing assets via the **art pipeline** (see §7.1): the user approves placeholder
  vs. custom art and the acquisition route; open-mod owns deterministic STS2 processing.
- Packaging the mod and placing it where the game loads mods from.
- Launching the game to validate the mod loads and the behavior triggers.
- Reading errors and auto-repairing, then re-validating — iterating until it works.

### 7.1 Art / sprite pipeline (REQUIRED feature)

Art remains a required product capability, but it is not the gate for the current M6
Character Systems programming phase. Character-system canaries use built-in/fallback
visuals, generated nodes, or generic open-mod-owned scenes while state, hooks, save,
choice, UI-host, and patch behavior are proven. Production character animation/art returns
after those code contracts are live-green.

Whenever a mod needs new sprites (relic icon, card portrait, etc.), the skill must keep
the art decision explicit and the result source-independent:

- **One mod-level choice: placeholder OR custom art.** Placeholder is the silent default
  and keeps the loop immediately testable. Only discuss generation when the user signals
  that visuals matter; do not make a beginner choose every individual file or provider.
- **Current shipped acquisition routes:** (a) an authenticated managed-credit Vofy CLI,
  live-verified on Windows 2026-07-14; (b) a user-configured OpenAI-compatible HTTP backend
  through `gen_sprite.py generate`; or (c) an existing local image through
  `gen_sprite.py import`. We do not bundle inference or credentials.
- **Managed-credit boundary:** the route follows the
  Imagine baseline. The user installs and logs into the CLI; open-mod may submit one
  confirmed non-interactive job and download its source image. It never invokes browser
  login or reads stored auth. A fresh Codex acceptance run generated card plus cut-out
  sprites, rebuilt the `.pck`, and passed in-game visual inspection on Windows. macOS/Linux
  behavior and live provider rejection/insufficient-credit paths remain unverified.
- **Acquisition is not normalization.** HTTP generation, managed CLI, and local files all
  converge on the same deterministic `gen_sprite.py import` contract. Provider output is
  never trusted to already have the exact size, alpha/chroma, duplicate `big/` variant,
  or STS2 path.
- **Correct output regardless of source.** Whether placeholder or generated, the
  asset must land at the right path and exact size the game expects (e.g. card
  portrait 1000x760), so a `.pck` rebuild (Path A / PckPacker) picks it up.
- **Why required:** closes the one concrete feature gap vs. AgentTheSpire (which
  ships an art pipeline). Placeholder-first stays the default for speed; real
  generation is opt-in and source-pluggable so users aren't locked to our choice.

Current implementation resolved (M5.5, card portrait first): the **backend config** is a
provider-agnostic `art-backend.json` (`{base_url, api_key, model}`, OpenAI-images
-compatible — no provider bundled, BYO) read by `tools/gen_sprite.py`; the **prompt
template** per sprite type lives in `sts2-api/reference/art-contract.md` (card portrait
done: subject-centered, no text/border, full-bleed); **regenerate/tweak** is an art
sub-step after AUTHOR and before BUILD — re-run `gen_sprite.py` with an adjusted prompt,
then rebuild the `.pck`. The exact sprite **path + size contract** (a normal card's one
portrait is `1000×760`; 606×852 full art is Ancient-only, out of scope;
relic/power/potion icons are 256×256 loose PNGs, all four types live-verified) is recorded in
`art-contract.md`. `gen_sprite.py` also has an `import` mode for a
user-supplied local image. Placeholder stays the default (a missing sprite falls back to
the template art), so art never blocks the pipeline. The Vofy route produces a
local intermediate and then reuses `import`; it does not replace `art-contract.md` or add
Vofy credentials to `art-backend.json`. See `BASELINE_RESEARCH.md` and
`IMPLEMENTATION_PLAN.md` M5.5 follow-up for its exact boundary and proof gate.

## 8. Out of scope (for now)

- **Other games** — Phase 2. Phase 1 is Slay the Spire 2 only.
- **Codex runtime** — later target; build and validate on Claude Code first.
- **Publishing to Steam Workshop** — Workshop IS live for STS2, but Phase 1
  ends at a mod that works locally. Auto-publishing to Workshop is a later,
  opt-in step (and should always ask first). The user installs/tests locally.
- **Bundling a specific image-gen provider, account, or hosted inference** — the art
  pipeline (§7.1) IS in scope, including optional execution through a user-installed,
  user-authenticated managed-credit CLI. We ship the integration and deterministic asset
  plumbing, not the provider, credentials, credits, or hosted generation. High-quality
  original audio and polished/curated original art beyond what the user's chosen backend
  produces remain later.
- **Full total conversions / replacement acts** remain later ecosystem work. Advanced
  playable characters and large mechanic changes are now in scope when they can be
  expressed as verified capability modules; "BaseLib has no wrapper" is not by itself an
  out-of-scope reason.

## 9. Constraints & assumptions

- **First runtime: Claude Code** (Codex is an eventual target, not Phase 1).
- **The game is installed locally** on the user's machine and can be launched
  with mods — this is required for the auto-test / closed-loop step (§6.3).
- The user is a non-programmer; the experience must be conversational and
  require no manual file editing or tooling knowledge.
- STS2 is in Early Access with **no official mod API**; our knowledge base is
  community-derived and must be re-verified as the game and scene change.
- <!-- TODO: platform — validate on Windows first (current dev environment);
     STS2/Steam is cross-platform, so note macOS/Linux path differences later. -->
- <!-- TODO: a C# toolchain (.NET SDK) is needed to build the mod — does the
     skill assume it's present, or install/guide it? -->

## 10. Our moat: the "game pack"

The sharp question: *why us, not the user just asking an AI themselves?*

Answer: we build a **game pack** — a game-specific manual we feed the AI up front,
containing the game's internal rules, the standard/correct way to write things
(`Mod.json` conventions, Harmony patch patterns), common errors, and working
runnable examples. Because STS2 has no official API, this curated knowledge is
the difference between "gamble on luck" and "reliably works."

For advanced mechanics, the pack also carries semantic capability contracts and
versioned patch adapters: state/lifetime, zones, resources/payment, owned entities,
run choices, hosted UI, save/network ordering, exact Harmony/Publicizer target, conflict
boundary, and Scenario proof. Downfall is the maintainer implementation-depth baseline;
the published pack contains only independently verified distilled modules, never the
gitignored checkout or extracted game assets.

- Building this pack (est. **~1–1.5 weeks** of focused work) is the core moat —
  it's the effort others won't bother to put in.
- The pack is a **replicable template**: to support another eligible game, make
  another pack in the same format. This is the path from a one-game tool to a
  general platform, and it's where the community could contribute packs too.

<!-- TODO: define the concrete structure/format of a game pack so it can be
     authored once and reused as a template. Likely contents: manifest schema,
     code recipes per element type (relic/card/potion), known-good examples,
     error→fix catalog, launch/test procedure. -->

## 11. Success criteria / MVP

MVP: a non-programmer types one sentence describing a single Slay the Spire 2
element (e.g. one relic), and the skill produces a mod that **installs, loads,
and actually works in the game**, with the auto-repair loop handling failures
along the way.

## 12. Resolved risks and open questions

### Resolved foundation risks

- **R1 — CLI build and packaging: RESOLVED.** M0 proved a no-IDE build that emits
  `.dll` + `.pck` + manifest, and M1/M2 proved the same substrate through the skill
  pipeline. PckPacker is the normal path; see `M0_RESULTS.md`, `M1_RESULTS.md`, and
  `M2_RESULTS.md`.
- **R2 — Automated in-game verification: RESOLVED.** Tier 1 reads the real game log;
  Tier 2 is an arg-gated in-process self-test that drives public game commands and
  observes effect markers/state changes. The combat cells and later M6 scenarios are
  recorded in `games/sts2/tests/canary-results.md`; the maintained harness contract is
  `games/sts2/skills/sts2-api/reference/selftest-harness.md`.

### Open product and distribution questions

- When should the best-effort macOS/Linux paths be promoted to a supported claim through
  live runs on those platforms?
- When should the portable package receive a live install/run acceptance test in Codex or
  another non-Claude agent, and which registry directories should list it?
- What should the opt-in Steam Workshop publish flow require before any outward-facing
  upload?
- How far beyond M6 Core should Phase 1 expand before the reusable game-pack template is
  formalized for a second game?
