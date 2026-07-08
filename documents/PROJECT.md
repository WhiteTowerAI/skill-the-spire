# Project Brief: Text-to-Mod Skill

> This document describes the intent, scope, and design of the project.
> Its primary audience is an AI coding agent (Claude Code / Codex) that will
> help build and iterate on this project. It is written to convey *what we
> want to build and why*, so the agent can reason about tradeoffs and make
> good engineering decisions.
>
> Status: v1 (decisions locked below). Remaining `TODO`s are for the
> implementation-planning phase, not blockers.
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

<!-- TODO (implementation phase): pin down the concrete on-disk shape
     (SKILL.md + scripts + the game pack) for Claude Code first, then the Codex
     equivalent. Reference model: references/Higgsfield_games/game-studio.md
     (their skill = one markdown file that drives an interview → brief → build
     → deploy pipeline). We build/validate on Claude Code first (decision). -->

### 3.1 Distribution goal: one-command install from a skill registry

**The end-state install experience is a single command**, the way a user adds any
published skill — e.g. `npx skills add open-mod` (or the equivalent for whatever
registry we publish to, such as skills.sh). Assuming their game/toolchain
prerequisites are met, that one command should place the skill where their agent
finds it, with **no repo clone, no manual `publish.sh`, no "open Claude Code in
this specific folder"**. Invoke, describe, done.

This is a **committed target**, not just a nicety — frictionless distribution is
one of our differentiators vs. competitors that make you clone a repo and wire up
tooling ([[competitor-agentthespire]]). Today (M2) install is still the developer
flow (clone → `./publish.sh --agent claude` → open the repo in Claude Code), which
is fine for building/testing but is NOT the shipping experience. Closing that gap —
packaging open-mod so a registry's `add` command deploys it in one step — is
required before we can honestly call the "no setup" claim true. Track as a late-phase
deliverable (around M5, alongside the Codex runtime and opt-in Workshop publish).
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
- Providing assets via the **art pipeline** (see §7.1): per sprite, the user
  chooses placeholder vs. generate; generation backend is user-configured.
- Packaging the mod and placing it where the game loads mods from.
- Launching the game to validate the mod loads and the behavior triggers.
- Reading errors and auto-repairing, then re-validating — iterating until it works.

### 7.1 Art / sprite pipeline (REQUIRED feature)

Whenever a mod needs a new sprite (relic icon, card portrait, etc.), the skill
must let the **user decide per sprite**, not silently pick one:

- **Choice per sprite: placeholder OR generate.** For each needed sprite, offer
  (a) use a **placeholder** for now (the template's default art — keeps the loop
  fast and the mod immediately testable), or (b) **generate a new sprite**. The
  user can mix: placeholder some, generate others.
- **User-chosen generation backend.** If the user picks "generate," the *user*
  decides how the image is produced — their **own image-gen API** (configurable:
  provider + key + model) or a **local model**. We do NOT hardcode or bundle a
  single provider; we provide the plumbing (prompt → backend → correctly-sized,
  correctly-placed sprite) and let the user point it at whatever they want.
- **Correct output regardless of source.** Whether placeholder or generated, the
  asset must land at the right path and exact size the game expects (e.g. card
  portrait 1000x760), so a `.pck` rebuild (Path A / PckPacker) picks it up.
- **Why required:** closes the one concrete feature gap vs. AgentTheSpire (which
  ships an art pipeline). Placeholder-first stays the default for speed; real
  generation is opt-in and BYO-backend so users aren't locked to our choice.

Design resolved (M5.5, card portrait first): the **backend config** is a
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
the template art), so art never blocks the pipeline.

## 8. Out of scope (for now)

- **Other games** — Phase 2. Phase 1 is Slay the Spire 2 only.
- **Codex runtime** — later target; build and validate on Claude Code first.
- **Publishing to Steam Workshop** — Workshop IS live for STS2, but Phase 1
  ends at a mod that works locally. Auto-publishing to Workshop is a later,
  opt-in step (and should always ask first). The user installs/tests locally.
- **Bundling a specific image-gen provider / hosting inference** — the art
  pipeline (§7.1) IS in scope, but generation is **bring-your-own-backend**
  (user configures their own API or local model). We ship the plumbing, not a
  chosen provider or hosted image generation. High-quality original audio, and
  polished/curated original art beyond what the user's chosen backend produces,
  remain later.
- **Complex / total-conversion mods** — start with single-element mods (one
  relic, one card, one potion), not sweeping overhauls.

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

## 12. Open questions

**Two risks gate the whole promise — prototype these FIRST (see
BASELINE_RESEARCH.md for detail):**
- **R1 — Headless/CLI publish.** STS2's mod build generates the `.pck` via Godot,
  and the docs only show doing it from Rider. We need a fully no-IDE
  `dotnet`/MSBuild publish of `.dll`+`.pck` (there's a `GodotPublish` target and
  a `DOTNET_ROOT` hint suggesting it's possible). If this can't be automated,
  the pipeline breaks.
- **R2 — Automated in-game verification.** There's no documented headless test
  mode. We *can* launch without Steam (`steam_appid.txt` = `2868840`), read
  `godot.log`, and spawn content via the dev console — but asserting "the effect
  actually triggered" automatically needs scripting the dev console, an in-mod
  self-test that logs a marker, or log-assertion. This is our headline
  differentiator, so validate it early. **Update: `Gennadiyev/STS2MCP` (421★)
  and `LightEnding/autoSpire` already expose live in-game state to an agent —
  likely reusable for the hard "did the effect fire?" tier instead of building
  a harness from scratch. See COMPETITIVE_LANDSCAPE.md.**

**Other open items:**
- §9: Windows-first is assumed for dev; when do we handle macOS/Linux path
  differences? (mod paths and the game binary differ per OS.)
- §9: .NET SDK 9.0+ and MegaDot (Godot) must be present — does the skill assume
  them, detect them, or guide install?
- §7/§10: Placeholder-first art is the native STS2 workflow (template ships a
  default `card.png`); where/when do "real" assets come from?
- §5: Study the existing **STS2 Modding Assistant MCP** (Nexus #345) and the
  `spire-codex` decompile project — reuse vs. differentiate. (A background agent
  is currently sweeping for other competitors/prior art.)
- §10: Can BaseLib's `Custom*Model` + "copy a similar base card" pattern make
  single-element mods near-templated, leaving the LLM only the effect logic?
