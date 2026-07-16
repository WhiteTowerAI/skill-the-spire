# Competitor Deep-Dive: modmixer

> Founder-facing competitive brief. From a background deep-dive, 2026-07-01.
> Repo state through commit ~2026-06-28, release v0.9.2. Facts tagged VERIFIED
> (seen in repo/site/HN) vs INFERENCE. Companion to COMPETITIVE_LANDSCAPE.md.

## TL;DR
Free, open-source (MIT) **Windows desktop app** that wraps a coding agent so
non-programmers build **RimWorld** (mature) and **Minecraft NeoForge** (beta)
mods by chatting. **Bring-your-own-AI**, no hosted inference, **no revenue
model**. Genuinely strong where it's hard: **local decompile+index of real game
source**, a **two-tier curated+accumulating knowledge base**, and a **real
auto-test/auto-repair loop** via an in-game diagnostics bridge. Traction is tiny
(**12★, ~solo author, 4-person Discord, ~zero HN pickup**). Crucially, by the
author's own admission the loop **"can't play the game to test the mod"** — it
verifies *compiles+loads*, not *behaves correctly*. That gap + true
non-programmer UX is exactly our wedge.

## Product & positioning (VERIFIED)
- **Form:** Electron+React+TS desktop app, Windows-first. Not CLI/web/MCP.
- **Flow:** install → onboarding (pick game → connect AI provider → detect game
  install/DLCs, provision toolchains, build source index) → "+ New Mod" → agent
  asks idea → clarifies → **presents plan for approval** → builds (tool calls
  stream) → "ready to test?" → launches game + bridge mod → user play-tests →
  reports in chat → fixes → one-click publish (Workshop/Modrinth).
- **Target user:** marketed to non-programmers, but author (HN) admits it needs a
  "driver" who does creativity, game design, value-tuning, and **play-testing**.
  Honest target = motivated hobbyist/player-designer, not zero-effort layperson.
- **Business model:** free + MIT, BYO-AI, no pricing page (404), no subscription.
  Recommends OpenRouter + **Kimi K2.6** (cheap, non-frontier). Looks like a
  passion/mindshare play, not (yet) a business.
- **Games:** RimWorld (default, full), Minecraft/NeoForge (beta, half features
  off). Factorio/Stardew/Project Zomboid "coming soon" (not shipped).
- **New-game model = plugin/pack (like ours):** descriptor (data: identity,
  capability flags, lore taxonomy) + main-process adapter (scaffold/build/test/
  index/publish) + one registry line. Their pack ≈ {descriptor + adapter +
  decompile/index pipeline + shipped lore/ + cookbook/ + a bridge mod}.
  **Their pack is code-plus-knowledge; ours is knowledge-first for one game.**
- **Traction:** 12★/0 forks; contributors = lebek (332 commits) + "claude" (2);
  created 2026-04-29, ~daily commits, 28 releases to v0.9.2 in ~2 months; HN post
  1 point/0 comments. Only real credibility = a homepage leaderboard of actual
  shipped Workshop mods (top ones by the author & a few power users).

## Architecture (VERIFIED)
- **Not a homegrown agent.** Built on the **Pi agent harness**
  (`@mariozechner/pi-*`, badlogic/pi-mono) — multi-provider LLM API + tool-calling
  runtime, with local patches. **modmixer = Pi agent + per-game tool layer +
  knowledge base + Electron GUI.** Direct analogue to building on Claude Code/Codex.
- **Stack:** Electron 41/React 19/TS/Vite/Tailwind; better-sqlite3 (index),
  @vscode/ripgrep (search), isomorphic-git (snapshots/rollback), fast-xml-parser
  + smol-toml, steamworks.js (publish), Sentry+PostHog (telemetry).
- **Decompile+index (crown jewel):** RimWorld → vendored **ILSpy** decompiles
  `Assembly-CSharp*.dll` + owned DLC DLLs → tree-sitter-csharp symbol index + XML
  defs in SQLite. Minecraft → **ModDevGradle** generates Mojang-mapped+Parchment
  sources locally + indexes data-driven JSON. LLM tools: `search_defs`,
  `search_source`, `read_csharp_symbol`, `decompile_dll`, `inspect_mod`, etc.
  **Goal (author, HN): feed the model real symbols so it doesn't guess, cheaply.**
- **Knowledge pack, two tiers:**
  1. `cookbook/` — human-curated, repo-shipped, read-only (e.g. Harmony patterns,
     Combat Extended compat).
  2. `lore/` — agent-consulted AND **agent-writable**, topic-locked per game,
     tiered repo(read-only) vs user(accumulates). **RimWorld lore syncs via a
     shared Supabase backend — a crowd-sourced flywheel.**
- **Build+test loop:** `build_mod` → `dotnet build` (RimWorld) / `./gradlew build`
  (MC). `run_test_cycle` **launches the real game** + a **"Modmixer Bridge" mod**
  (C#/Harmony) that streams load/runtime errors over **localhost TCP as NDJSON,
  bucketed by stack-signature**; agent is auto-prompted to fix + relaunch. Errors
  attributed per-mod, isolated savedata so user's real modlist is untouched.
- **Invocation:** it **wraps** the Pi agent in-process; it is NOT an MCP server
  and does not expose itself to other agents. modmixer is the host/harness.

## The Minecraft correction (the founder asked)
- "Minecraft mod" ≠ one format. Four worlds: (1) **Forge/Fabric/NeoForge Java
  mods** — community modloaders, NOT Mojang-official; (2) **data/resource packs**
  — Mojang's official no-code JSON; (3) **Bedrock add-ons** — official JSON+JS;
  (4) no general official Java code-mod API.
- **The belief "MC mods are Mojang's official way" is INCORRECT.** modmixer
  generates **community NeoForge Java mods** (MC 1.21.1 / NeoForge 21.1.234 /
  Java 21, a Gradle project, publish to Modrinth). It targets exactly ONE MC
  version on purpose (one JDK, one vendored MDK, one index pipeline).
- **Irony:** a no-code-for-non-programmers product picked the **most code-heavy**
  MC path (real Java+Gradle+JDK+registry-timing gotchas) over the genuinely
  no-code official data-pack/add-on formats — because it has the biggest audience
  and their decompile→index→write-code→compile→test architecture maps onto a code
  ecosystem, not a constrained-JSON one.
- **RimWorld:** standard layout — `About.xml` + `Defs/*.xml` + `Patches/` +
  `Textures/` + optional C# assembly (`dotnet build`) + Harmony. Matches reality.

## Strengths to consider adopting
1. **Local decompile+index of the real game** so the agent reasons over real
   symbols, cheaply. For us: index STS2's real card/relic/monster classes +
   BaseLib surface. (We planned this via sts2-api + spire-codex — they prove it.)
2. **In-game diagnostics bridge over localhost** — clean plumbing for our R2
   (a small companion mod that phones home beats scraping godot.log alone).
3. **Two-tier knowledge base + community sync flywheel** — validates our
   `recipes/`(=cookbook) + `errors.md`(=accumulating lore) design; the Supabase
   community-lore sync is a mechanic worth planning toward.
4. **Engineered for cheap models + an A/B "does the model obey" harness** — cost
   discipline worth copying if our economics matter.
5. **Clean plugin/pack architecture** with a "no game branches in core" guardrail.
6. **Full lifecycle polish:** load-order autosort, dep pull-in, rollback via git
   snapshots, one-click publish, mod manager.

## Weaknesses = our openings
1. **Verification is "it loads," not "it works."** Author: *"it can't play the
   game to test the mod."* Their lore: *"a green build does NOT mean the mod
   loads."* The loop fixes crashes, not wrong behavior. **THIS is the biggest
   opening for our R2 Tier-2 behavioral verification — they punt exactly where
   we aim to win.**
2. **"Non-programmer" is aspirational.** Tool-call noise in the UI (README:
   "ok if these messages look confusing"), user must be QA/designer/tuner, and
   MC drops them into Java/Gradle/JDK.
3. **Broad-and-shallow; MC is thin.** Depth lives in RimWorld; every new game
   restarts the lore/cookbook/bridge investment near-zero.
4. **Tiny bus-factor/traction; no revenue model.** Could stall or pivot.
5. **Windows-only Electron install** — friction vs. a skill riding an agent the
   user already runs (Claude Code/Codex).

## Strategic contrast (deep-on-STS2 vs broad)
- **Our edge is real where it counts.** Their per-game cost is large (decompile
  pipeline + bridge mod + curated lore + adapter + publish, *per game*). Going one
  game deep lets us build a genuinely curated STS2 pack AND invest in
  **behavioral verification** — the thing they explicitly hand back to the user.
  "The new card actually deals X / the relic actually triggers" is a category
  difference, not an increment.
- **Respect what broad buys them:** plugin architecture, a cross-game community
  flywheel, and an easier story ("mod *any* game"). If STS2's modder/player base
  is small, **TAM is our risk, not our tech.**
- **Moats we must match:** local source indexing (don't guess STS2 APIs) + a
  runtime error bridge (grounded fixes). **Gap to attack:** verified behavioral
  correctness + literally-true one-sentence-to-tested-mod UX.
- **Net: they validate the approach (decompile+index+agent+bridge+curated
  knowledge) AND the pack model, but NOT deep verification or frictionless
  non-programmer UX. That whitespace is ours to take.**

## Impact on our plan (actionable)
1. **Adopt the diagnostics-bridge pattern for R2.** Our verify.md was going to
   grep `godot.log`; modmixer shows a **companion "bridge" mod streaming errors
   over localhost** is cleaner and attributes errors per-mod. Consider a small
   STS2 bridge mod (BaseLib + Harmony) — or check if **STS2MCP already provides
   this channel** (it exposes live state), which fits our "reuse at the edges"
   decision. Fold into the M0 R2 tier-2 investigation.
2. **Make behavioral verification the headline, not a footnote.** modmixer's
   loudest admitted gap. Our R2 Tier-2 (does the effect fire?) is the
   differentiator; resource it, and never ship a "verified" claim that only
   means "loaded" (which is all they do).
3. **Plan the `lore`/`errors.md` accumulation + eventual community sync now.**
   They've proven the flywheel; design `errors.md` from day one to be
   append-only and later shareable.
4. **Index real STS2 source (don't just hand-write the pack).** Combine our
   curated `recipes/` with a spire-codex-backed searchable index so the agent
   grounds on real symbols like they do.
5. **Lean into the UX gap.** A true one-sentence flow with plain-language
   progress (hide tool-call noise) on an agent the user already runs is a
   concrete, marketable advantage over a separate Electron app full of tool logs.

## Access gaps
Fully read: repo (src tree, adapters, index/decompile, lore/cookbook, monitor
bridge, system prompt, onboarding), GitHub API, site + RimWorld docs, Pi
framework identity, HN post. Not available: HN thread has no comments; nexusmods/
some Steam pages block curl; no static model list (built from Pi catalog at
runtime); did not run the .exe (UX claims rest on README/docs, consistent w/ code).

Sources: modmixer.com · github.com/lebek/modmixer · HN item 48121901 ·
modmixer.com/docs/rimworld · github.com/badlogic/pi-mono
