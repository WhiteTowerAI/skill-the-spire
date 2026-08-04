# Competitive & Reference Landscape (STS2 Text-to-Mod)

> Companion to PROJECT.md / BASELINE_RESEARCH.md. From a background research
> sweep, 2026-07-01. Excludes the four already-covered projects (GodotMaker,
> Claude-Code-Game-Studios, ModTemplate-StS2, STS2 Modding Assistant MCP #345).
> Several items here change our technical picture — see "Impact" at the end.

## 1. Direct competitors — AI/text-to-mod (any game)
- **cgxjdzz/AgentTheSpire** (formerly "SpireForge") —
  https://github.com/cgxjdzz/AgentTheSpire — **⚠️⚠️ CLOSEST DIRECT COMPETITOR:
  same game (STS2), same stack (.NET 9 / Godot Mono 4.5.1 / PCK), same NL→mod
  promise, and shipped first.** A standalone **local web app** (Python FastAPI +
  React/TS + C#/Godot mod template), launches at localhost:7860. NOT a Claude
  Code skill, NOT an MCP ("does not use MCP"). 3-stage pipeline: code gen (Claude
  Code CLI *or* API keys — Anthropic/Moonshot/DeepSeek/Qwen/Zhipu) → **art gen**
  (FLUX.2/FAL/即梦/通义万相 + bg removal) → `dotnet publish` → PCK → deploy to
  mods folder. Already has a **compile-error auto-repair loop** and optional
  **game-DLL decompilation** for grounding. MIT, 51★/10 forks, but **very new /
  barely maintained** (~4 commits, all ~2026-03-21).
  **How we differ:** (1) **distribution/friction** — we are a Claude Code *skill*
  (near-zero install) vs. their clone-repo + Python/Node/.NET/Godot + edit-JSON-
  keys + web-UI toolchain; (2) **grounding** — our curated `sts2-api` game pack +
  BaseLib recipes vs. their ad-hoc decompilation; (3) **true non-programmer, one-
  sentence UX** vs. their AI-tinkerer bar; (4) we make **tier-2 behavior
  verification** the headline. **Two gaps we must own:** they HAVE an art pipeline
  and we don't yet; and our "no setup" claim must be genuinely true. MIT = their
  mod_template/PCK flow, auto-repair design, decompiler, and multi-provider art
  pipeline are all borrow/study references.
- **lebek/modmixer** — https://github.com/lebek/modmixer (modmixer.com) —
  Desktop app: decompiles/indexes a game, gives an AI LLM (Claude/Codex/Kimi/
  Deepseek) tools to build AND test mods, "without writing code." TypeScript.
  Non-programmers via AI assistant. Active (2026-06-28), 12★.
  **⚠️ Closest game-AGNOSTIC analog to our loop.** Differentiator vs us: it's a
  general desktop app, not a non-programmer one-sentence *skill* + STS2-specific
  game pack. (Deep-dive: COMPETITOR_MODMIXER.md.)
- **Minecraft no-code AI SaaS cluster** — modlyai.com, player.games,
  orcaclient.com, enderdevelopment.com, creativemode.net, codexe.eu,
  stacknests.com, Modder AI, Blink — "describe a mod → working Minecraft mod,
  no coding." Closed SaaS, non-programmers, commercial/active.
  **Reference-only** (proves mass demand; Minecraft-only, not agent skills).
- **jamesvovos/ai-game-asset-creator** — NLP→assets (quests/dialogue/textures),
  Python/LangChain, 19★, **abandoned 2023**. Reference-only.
- **Prastiwar/ForgeModGenerator** — GUI Minecraft-Forge generator, **no AI**,
  C#/WPF, 4★, **abandoned 2022**. Sounds relevant, isn't.

## 2. AI modding tools for specific communities
- **SpookyPirate/spookys-automod-toolkit** — https://github.com/SpookyPirate/spookys-automod-toolkit —
  Tools to help LLMs create/edit Skyrim mods. C#, programmer-leaning, 15★,
  active (2026-05). **Reference — genuine parallel effort.**
- **liminalwarmth/stardew-valley-ai-modkit** — template + rules file for
  building Stardew mods with Claude Code. C#, 3★, early (2025-12).
  **Reference — same template+rules pattern we'd use.**
- **galgtonold/ai_combinator** — NL→Factorio circuit logic, Lua, 7★, active.
  Reference (narrow).
- Non-competitors flagged: lorenz-liu/stardew-gpt (in-game chat, not a
  generator), mvircs1/RimAI (empty), Nexus StardewAI Assistant (in-game NPC).

## 3. MCP servers for engines / modding
- **CoplayDev/unity-mcp** — LLM manipulates Unity Editor live. C#, **11,201★**.
  Reference — gold-standard engine-bridge MCP design (wrong engine for us).
- **Coding-Solo/godot-mcp** — https://github.com/Coding-Solo/godot-mcp —
  launch editor, run projects, **capture debug output**. JS, **4,479★**, active.
  **Reusable reference — launch+run+capture-errors maps to our auto-repair.**
  (Drives the Godot *editor*, not the STS2 mod loader.)
- Smaller: bradypp/godot-mcp (86★), LeeSinLiang/godot-mcp (8★), etc.

## 4. Claude Code / Codex skills & frameworks for game dev
- **htdt/godogen** — https://github.com/htdt/godogen — Autonomous game dev for
  Godot/Bevy/Babylon with Claude Code & Codex: plan→code→assets→**run engine→
  check screenshots→self-repair**. Python; Godot output is C#/.NET. **4,191★**,
  active. **⭐ Most important structural reference — nearly our exact loop, and
  10x more traction than GodotMaker.** Steal: **"frame-grounded self-repair"**
  (judge from observed output, not "it compiled"), engine-docs-lookup skill,
  stop-hooks, Claude-vs-Codex publish-time rendering.
- **Simone-Tarantino/godot-superpowers** — 33 skills + 15 subagents, lint/verify
  hooks, MCP, orchestrator/verifier subagents. 1★ (unproven) but rich structural
  reference for a Godot Claude-Code skill suite.
- HermeticOrmus/claude-code-game-development (41★, docs/patterns), 
  prskid1000/Agent-GameBuilder-Skill (0★) — reference-only/negligible.

## 5. STS2-specific ecosystem
- **Alchyr/BaseLib-StS2** — https://github.com/Alchyr/BaseLib-StS2 — the
  community core lib we target. C#, **384★**, active. NuGet
  `Alchyr.Sts2.BaseLib`. Wiki https://alchyr.github.io/BaseLib-Wiki/.
  **Reusable dependency + essential doc input.**
- **Gennadiyev/STS2MCP** — https://github.com/Gennadiyev/STS2MCP — a mod that
  **exposes live in-game state** + an MCP server for agentic runs. C#, **421★**,
  active. **⭐ Most reusable for our R2 — this is the live-state observation we
  thought didn't exist. Potentially drop-in for behavior verification.**
- **ptrlrd/spire-codex** — https://github.com/ptrlrd/spire-codex — decompiles
  STS2 into a queryable API (spire-codex.com) + spire-codex-mod. TS, **221★**,
  active. **Reusable grounding data — critical since STS2 has no official API.**
- **LightEnding/autoSpire** — MCP mod to drive STS2 autonomously. C#, 1★, newer
  alternative to STS2MCP. Reference.
- **GlitchedReme/SlayTheSpire2ModdingTutorials** — 176★, active. Grounding/
  training content for the game pack.
- **khevtol/STS2-reference-index** — index of STS2+BaseLib classes/methods/
  assets. 0★, nascent. Reference data.
- **Official wiki** (slaythespire.wiki.gg) + **MegaCrit Neowsletter #23** —
  confirm Godot 4.5.1 fork, C#/Mod.json/Harmony, integrated loader, Workshop in
  Update 2, and **no official modding API** (community-gathered).
- Context mods (reference): erasels/Minty-Spire-2 (102★),
  **erasels/StS2-Quick-Restart (166★ — useful for fast test-iteration)**,
  Rain156/sts2-RMP-Mods (141★), emptylower/STS2-Game-Lobby (81★).

## 6. Academic / blog prior art
- **RepairAgent** (arxiv 2403.17134) — autonomous LLM program-repair loop;
  directly relevant to read-errors→auto-repair.
- **"Practical Limits of Autonomous Test Repair"** (arxiv 2605.01471) —
  multi-agent LLM test-repair, ~70% convergence. **Realism check: auto-repair
  is not a silver bullet.**
- **Personality-Driven Automated Game Testing with LLMs** (arxiv 2604.07752);
  **Cerebras "Never Loop Without Verifiers"** — loops must observe real output.
  Backs our R2 design rationale (self-test markers / observed state, not "it
  built").

## Biggest threats
- **cgxjdzz/AgentTheSpire** — the ONLY direct STS2 text-to-mod competitor found:
  same game, same stack, working auto-repair loop AND art pipeline, shipped first.
  Threat tempered by being an early, barely-maintained heavyweight app (not a
  frictionless skill) — but it proves the concept and beats us to market.
- **lebek/modmixer** — same decompile→index→LLM-tools→build+test-no-code
  concept, game-agnostic; small now, could add STS2 trivially.
- **htdt/godogen** (4,191★) — the autonomous generate→run→observe→self-repair
  loop for Godot+C# is already built and popular; a pivot to mod output = our
  architecture with a head start. (Also our primary architecture baseline —
  BASELINE_RESEARCH.md.)
- **STS2MCP author / STS2 community** — whoever first pairs live-state MCP with
  generation owns the STS2 niche.

## Most reusable
- **Gennadiyev/STS2MCP** (421★) + **ptrlrd/spire-codex** (221★) — live game-state
  observation + decompiled API/data; together they cover our test-loop and the
  grounding STS2 lacks officially.
- **Alchyr/BaseLib-StS2** (384★) + BaseLib-Wiki + ModTemplate — library/manifest
  conventions our generated code must follow.
- **htdt/godogen** + **Coding-Solo/godot-mcp** (4,479★) — loop architecture,
  frame-grounded self-repair, Godot launch/run/capture-debug patterns.

---

## Impact on our plan (what actually changes)
1. **R2 is less risky than assessed.** `STS2MCP` and `autoSpire` already expose
   live in-game state to an agent — the piece R1_R2_FEASIBILITY.md called the
   "open frontier." Revisit R2 Tier-2: possibly **reuse STS2MCP** for behavior
   verification instead of building a harness mod. (Still validate: does it let
   us drive to a deterministic combat and read our element's effect?)
2. **Primary architecture reference → `htdt/godogen`** (with GodotMaker
   secondary). Same loop, same engine family, 10x traction, and its
   "frame-grounded self-repair" is the principle behind our R2.
3. **Grounding source for the game pack → `spire-codex`** (queryable decompiled
   API) + the tutorials/reference-index repos, not raw decompilation from
   scratch.
4. **We are NOT first, but the niche is open.** No one yet combines
   (non-programmer one-sentence UX) + (STS2 game pack) + (auto-repair verified
   loop). modmixer is the closest and is game-agnostic/programmer-ish; the STS2
   MCPs are agent-driver tools, not one-sentence generators. That intersection
   is our wedge — and it's defensible only if the game pack + verified loop are
   genuinely good.
5. **Sober note (from the test-repair paper): ~70% auto-repair convergence.**
   Don't over-promise the self-repair loop; design for graceful "couldn't fix,
   here's what's wrong" outcomes.
