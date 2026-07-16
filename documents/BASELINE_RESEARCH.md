# Baseline Research: Reference Repos for Text-to-Mod (STS2)

> Companion to PROJECT.md. Records what we learned from candidate baselines and
> which we build on. Initial baselines fetched 2026-07-01; Imagine/Vofy art-source
> follow-up researched 2026-07-14; Downfall advanced-character research added
> 2026-07-15.

## Why this project (framing, from the user)

Text-to-game is now fairly mature and has commercial products. Modding shares
most of its engineering with game-making, but far fewer people build *mod*
tooling — so there's an open niche. STS2 is an especially good first target:
it's built on **Godot** (same engine + language as our strongest architectural
baseline, godogen — Godot 4 / C#), ships a **built-in mod loader**, has a **live Steam Workshop**, and mods are
**single-element granularity** (one relic/card/potion), which is more tractable
than generating a whole game.

## The references

> Note: `htdt/godogen` was surfaced by the later competitive sweep
> (`history/COMPETITIVE_LANDSCAPE.md`) and is now our **primary** architectural baseline,
> ahead of GodotMaker — same engine family and closed loop, ~10× the traction,
> and a permissive MIT license. GodotMaker remains a strong corroborating
> reference (the two are near-identical in shape, so they validate each other).

### 1. htdt/godogen — PRIMARY ARCHITECTURE + CLOSED-LOOP baseline ⭐⭐
- `Autonomous game dev for Godot / Bevy / Babylon with Claude Code & Codex:
  plan → code → assets → run engine → check screenshots → self-repair`
- **4.2k★**, 371 forks, active (34 commits, recent changelog), **MIT license**.
  72.5% Python (Godot output is C#/.NET 9).
- **Why it's our primary architectural baseline:**
  - **Same engine + language as STS2 (Godot 4, C#/.NET 9).** Transfers directly.
  - **~10× GodotMaker's traction and a permissive MIT license** (vs GodotMaker's
    restrictive BUSL 1.1) — safer to learn from and adapt.
  - **The exact loop we want, proven and popular:** describe → plan → write code →
    generate assets → **run the engine → capture screenshots → self-repair visible
    defects → playable output.** The agent iterates on **observed output, not
    "it compiled"** — this "frame-grounded self-repair" is the principle behind
    our R2 (for us the observed reality is the game log + live state, not frames).
  - **Multi-runtime by *publish-time rendering*, not runtime adapters:** a
    `publish.sh` renders agent-specific layouts — Claude Code → `.claude/skills/`,
    Codex → `.agents/skills/`. Directly informs our "Claude Code first, Codex
    later" plan (build once, render per runtime).
  - **Concrete patterns to steal:**
    - **Frame-grounded self-repair** — judge from observed output, iterate on
      visible defects, never trust a green build.
    - **Engine-docs lookup skill** (local reference access) — the model for our
      swappable `sts2-api` game pack.
    - **Lazy-loaded stage files / file-based state** enabling resume — the basis
      for our SPEC.md/PLAN.md/MEMORY.md resume design.
    - **Stop hooks** (optional push with final proof) — a completion-gate pattern.
- **Caveat:** like GodotMaker it *generates whole games*; we *add a mod to an
  existing game*. Pipeline shape transfers; "what gets built" differs.

### 1b. RandallLiuXin/GodotMaker — corroborating architecture reference ⭐
- `Autonomous text-to-game pipeline for Godot, powered by Claude Code, Codex, Opencode`
- Python, 407★, actively updated, source-available (**BUSL 1.1** — restrictive).
- **Why still useful (secondary):** near-identical closed loop to godogen, so it
  independently validates the shape. Some pieces are spelled out more concretely
  than godogen's docs and are worth borrowing:
  - **A named skill pipeline we can mirror 1:1:** `skills/core/gm-*` =
    `gm-gdd` → `gm-scaffold` → `gm-build` → `gm-verify` → `gm-evaluate` →
    `gm-fixgap`/`gm-rescue` → `gm-finalize`/`gm-accept`. Each = `SKILL.md` +
    `references/`. (Our stage mapping below is expressed against these names.)
  - Ships `godot-api/csharp.md` — confirms C#-on-Godot knowledge transfers.
  - `agent-runtimes/{claude-code,codex,opencode}/` + a `capability-contract.md`.
  - `gm-verify` runs `godot --headless --quit` + gdUnit4, emits a structured JSON
    report; stage state in `.godotmaker/stage.jsonl` for resume; each skill
    declares strict read/write permissions; visual QA is a first-class gate.
  - Its README pre-writes our "why not a closed commercial platform" argument.

### 2. Alchyr/ModTemplate-StS2 — ENGINEERING SUBSTRATE (game-pack raw material) ⭐
- `Slay the Spire 2 mod project template`, C#, 243★, has a wiki, updated 2026-06-29.
- **This is the ground truth for what an STS2 mod actually is.** Three templates:
  empty mod / **Content mod** (add content) / **Character mod** (full character)
  — maps onto our "start at single-element" plan.
- Verified mod anatomy:
  - `XxxMod.json` manifest — fields: `id, name, author, version,
    min_game_version, has_pck, has_dll, dependencies[{id:"BaseLib", min_version}],
    affects_gameplay`. So a mod = a Godot **`.pck`** (resources) + a **`.dll`**
    (compiled C#).
  - `XxxModCode/` C# source split by type: `Cards/ Relics/ Potions/ Powers/`
    plus `Character/` (pools) and `Extensions/`, entry `MainFile.cs`.
  - Relics inherit `BaseLib.Abstracts.CustomRelicModel`, tagged `[Pool(...)]`;
    image paths resolved by convention. IDE has a right-click "Custom Relic
    template" generator.
  - `localization/eng/*.json` (cards/relics/powers/potions/keywords) — text.
  - `images/{relics,powers,card_portraits}/...` incl. `big/` variants.
  - `project.godot` + `export_presets.cfg` — confirms it's a real Godot project
    exported via Godot's own tooling.
  - Depends on **BaseLib** (community base library ≈ the old BaseMod).
  - Ships as a **.NET template** (`.template.config/template.json`, `dotnet new`)
    — so scaffolding is already solved; our skill can invoke it rather than
    hand-roll the tree.
- **The wiki** (Setup, etc.) is prime game-pack source material.

### 3. Donchitos/Claude-Code-Game-Studios — ORG-PATTERN reference only
- `Turn Claude Code into a full game dev studio`, Shell, 22.5k★.
- 49 agents / 73 skills / hooks / rules / doc templates, studio hierarchy
  (directors/leads/specialists).
- **Only produces docs + code scripts; does NOT touch the engine, running the
  game, or visual/closed-loop verification** (matches the bibliography's note).
- Useful as a reference for how to *organize* skills/agents/hooks/rules at scale,
  and its human-in-the-loop story workflow. NOT a technical baseline for the
  closed loop.
- **NEW USE (2026-07-09): the reference baseline for M7's interview mode.** The user
  tried CCGS and found its interview UX good, so M7's proactive interview is modeled on
  its `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` — the Question→Options→Decision→Draft→
  Approval loop, the Explain→Capture two-step (full reasoning in chat, then an
  `AskUserQuestion` selectable UI), the good-vs-bad question rubric, always-recommend-but-
  defer, scope-based depth routing (`/quick-design` vs `/design-system` — their answer to
  "proactive but not exhausting"), and incremental section writing. Take the interaction
  *shape*, not the multi-agent gate/director machinery (out of scope for our one-shot,
  non-programmer, single-mod tool). See `IMPLEMENTATION_PLAN.md` M7.

### 4. cgxjdzz/AgentTheSpire — CLOSEST DIRECT COMPETITOR, also a borrow reference ⭐
- STS2 text-to-mod generator (formerly "SpireForge"). Standalone local web app
  (Python FastAPI + React/TS + C#/Godot template), MIT, 51★, very new/thinly
  maintained (~4 commits ~2026-03-21). Full competitive analysis:
  `history/COMPETITIVE_LANDSCAPE.md` §1 (it is our closest rival — same game, same stack,
  shipped first).
- **Why it's also a reference (MIT-licensed, so borrowable):**
  - **It has an art-generation pipeline and we don't yet** — the one concrete
    feature gap. Study its multi-provider image-gen approach (FLUX.2 / FAL / 即梦
    / 通义万相 + background removal) as prior art for our required, BYO-backend
    art pipeline (PROJECT.md §7.1).
  - Its **compile-error auto-repair loop**, **mod_template → `dotnet publish` →
    PCK → deploy** flow, and optional **game-DLL decompilation for grounding** are
    all working references for our build/verify/repair stages and `grounding.md`.
- **How we differ (don't just copy):** it's a heavyweight app for AI-tinkerers;
  we are a low-friction Claude Code *skill* for true non-programmers, with a
  curated game pack (vs. ad-hoc decompilation) and tier-2 behavior verification.

### 5. WhiteTowerAI/imagine-skill — MANAGED-CREDIT ART ACQUISITION reference

Researched from gitignored `baselines/imagine-skill/` at commit
`1163a799ebffc19ba4d2aeb45ed945bdaa3dd514` (2026-05-19), repository package
version 0.1.2, MIT. The user described the service as Coi; the checked-in repository
identifies the actual execution service as **Vofy** and the executable as `vofy`, so
those are the names used here.

**What it is — and is not:**

- `imagine-skill` is an agent-instruction layer over the separately installed
  `vofy-cli@0.1.7`; it is not an image SDK and contains no inference transport itself.
- The user installs the CLI and performs `vofy login` once. Login opens a browser and
  stores a refresh-capable local session; an agent must never initiate it.
- After setup, the agent uses non-interactive CLI commands. `vofy status` checks auth,
  plan, and credits; `vofy image create ... --yes` creates a task; synchronous mode waits
  for completion; `--download-to <path>` saves the result locally.
- Async recovery exists through `vofy tasks --plain` and
  `vofy task <id_or_prefix> --download-to <path>`, but a normal open-mod sprite should use
  the synchronous path so the art stage remains one resumable pipeline step.

**Relevant image contract:**

- `vofy image create` supports text-to-image, repeatable `--image <path|url>` inputs for
  image-to-image/reference work, `--n`, aspect ratio, resolution, model selection, and a
  local download target.
- Model capabilities are not uniform. In the researched snapshot, for example,
  `seedream-4.5` accepts up to 14 image inputs and supports 4:3/1:1; GPT Image 1.5 accepts
  references and optional transparent backgrounds but not 4:3; Gemini Flash accepts
  references and 4:3. These are examples, not defaults to hardcode.
- `vofy models <model>` is the runtime source of truth for modes, input count, ratios,
  resolution, provider route, and current credit price. Generated model docs can drift.
- STS2 card portraits are 1000x760, not a standard generation ratio. Request 4:3 where
  supported, then let open-mod crop/fit to exactly 1000x760. Cut-out icons request 1:1 and
  retain the existing magenta-background contract; provider transparency is an optional
  optimization, not a new asset contract.

**Integration decision: use the CLI boundary, not skill-to-skill delegation.** Agent skill
composition and installation order differ across Claude Code, Codex, Cursor, and other
runtimes. open-mod therefore should not invoke `/imagine`, import Imagine's prompt skills,
or make `imagine-skill` a runtime dependency. It may optionally invoke the documented
`vofy` executable when present. Imagine remains a maintainer baseline for safe command
construction and capability lookup.

The art pipeline should keep acquisition separate from deterministic asset processing:

```text
open-mod art prompt + STS2 references
    |
    +-- current: BYO HTTP backend (`gen_sprite.py generate`)
    +-- current: authenticated managed-credit CLI (`vofy image create`)
    +-- current: user/local file
    |
downloaded/generated source image
    |
`gen_sprite.py import` -> crop/fit/chroma -> exact STS2 path(s) -> PckPacker
```

The managed-CLI implementation does not add provider HTTP code to `gen_sprite.py`. It:

1. detect `vofy` and run `vofy status`; if unavailable/unauthenticated, instruct the user
   to install/login themselves and offer BYO HTTP, local import, or placeholder;
2. run `vofy models <chosen-model>` before using model-specific flags;
3. show the final prompt, model, output count, and credit-spending action for confirmation;
4. generate synchronously with `--yes --n 1 --download-to <unique-empty-temp-dir>`, adding
   repeatable `--image` references only when the chosen model supports them;
5. discover the single new image from that isolated directory rather than parse human
   stdout (the researched CLI documents no stable JSON-output flag and does not guarantee
   a result filename);
6. pass that file to the already-live `gen_sprite.py import` path, then build and verify
   the normal STS2 asset contract.

**Security and UX boundaries:** open-mod never reads/copies Vofy credentials, writes them
to SPEC/MEMORY/logs, silently installs the CLI, launches login, chooses a paid route without
confirmation, or silently falls through to another paid backend. Missing auth, insufficient
credits, CLI failure, timeout, zero/multiple downloaded images, and unsupported references
must all fall back honestly without blocking the mod. Placeholder remains the default.

**Implementation and proof status (2026-07-14):** stdlib-only `tools/acquire_sprite.py`
implements this boundary and is bundled into both plugin payloads. Eleven Windows tests use
an isolated fake Vofy executable (including an npm-style `.cmd` shim) to cover missing
CLI/auth/model, the paid-approval gate, invalid local references, prompt normalization,
task failure/timeout, zero/multiple output, and successful card plus relic import contracts.
The full tools suite passes (19 tests). The wrapper suppresses status/create output, never
invokes login, submits one task, and calls the sibling `gen_sprite.py import`; it does not
duplicate pixel normalization.

The fresh Codex acceptance mod `HonedEdge` closes the Windows happy-path proof gate. It used
Vofy `gpt-image-2` with type-matched STS2 references to acquire three card portraits plus one
power and one relic cut-out, imported them to the exact one/two-file contracts, rebuilt the
`.pck`, and passed in-game visual inspection. The first multiline Honed Edge prompt produced
a rejected draft because the CLI path acted on only its opening line; the draft stayed
outside runtime resources. Subsequent single-line prompts produced the five accepted runtime
sprites. The wrapper now folds all whitespace to one line before invoking Vofy and has a
Windows `.cmd` regression proving later sentences survive. macOS/Linux behavior and live
provider rejection for unsupported flags or insufficient credits remain unverified.

### 6. lamali292/Downfall - ADVANCED CHARACTER CAPABILITY baseline

Researched from the gitignored `baselines/downfall/` checkout at commit
`ee2f8018635110569f2f5125aef6a45754b62280` (2026-07-15 repository HEAD), mod version
`0.0.30`, MIT. Its manifest targets the same live-verified substrate as open-mod: STS2
`0.107.1`, BaseLib `3.3.5`, and .NET 9. The local checkout is maintainer research input;
it is not shipped, read at runtime, or made a generated-mod dependency.

**What it is:** a large combined STS2 mod with ten character source modules and a shared
runtime kernel. The current combined project compiles Automaton, Awakened, Champ, Guardian,
Hermit, Hexaghost, Slime Boss, and Snecko. Collector and Gremlins remain substantial
source/assets in the repository but are commented out of the current `Downfall.csproj`
compile, so their code is grounding/design evidence rather than current-release behavior
proof. Across the repository there are 4,526 tracked files, including roughly 1,804 C#
files. This is production-size evidence for how character mechanics compose, not a minimal
template to copy.

**Why it changes the character plan:** BaseLib is a strong substrate, not the intended
feature ceiling. Downfall demonstrates mechanisms that are larger than one `Custom*Model`:

- custom combat zones and generated cards (Automaton);
- threshold transformations and rotating private pools (Awakened);
- owner-bound finite-state machines with charges and entry/exit actions (Champ);
- timed zones, persistent card attachments, rest-site options, and custom rewards
  (Guardian);
- hand-position semantics requiring a pre-play Harmony snapshot (Hermit);
- ordered circular state machines with polymorphic nodes (Hexaghost);
- owned minion rosters, command protocols, and death compatibility patches (Slime Boss);
- saved run-setup choices and cross-character card-pool composition (Snecko);
- persistent collection/currency/payment/reward systems (Collector, source-only);
- a multi-body party with active/bench rotation and per-member HP persistence (Gremlins,
  source-only).

These named mechanics reduce to reusable capability families: scoped state, state
machines, card zones, dynamic content, resources/payment, owned entities, run setup,
hosted choices, semantic hooks, UI adapters, save/network contracts, and versioned patch
bridges. The detailed source map and risk analysis live in
`history/downfall-character-capability-audit.md`.

**The upstream lesson:** Downfall already separates a shared kernel from thin character
modules. `DownfallHook` owns typed dispatch/aggregation; registries expose card execution,
combat UI, top-bar, and custom-pile hosts; `ModPatcher` applies selected Harmony patches and
reports zero-target/failure results. open-mod should generalize this further: generated
character code describes semantic states/transitions/resources, maintained capability
modules provide reusable implementation, and an optional automatically installed
`OpenMod.Runtime` eventually owns only cross-mod Harmony/Publicizer seams. Do not create a
shared runtime until two real advanced canaries prove the boundary; otherwise keep the
selected module self-contained in the generated mod.

**Registration correction:** Downfall never calls `AddCharacter` directly. In BaseLib
3.3.5, `CustomCharacterModel`'s constructor auto-registers through
`CustomContentDictionary.AddCharacter(this)`. Our capability graph must describe the
constructor behavior so generated code does not make an explicit duplicate call.

**What not to inherit:** Downfall's contributor build requires a local game path, a
Godot/MegaDot path, and GDRE-extracted assets linked into the project; it also carries a
large Publicizer/Harmony surface, including fragile transpilers. Players installing its
prebuilt DLL/PCK do not need those tools. open-mod's product opportunity is to absorb the
author-side complexity into path discovery, generated project configuration, curated
capability modules, packaging, patch diagnostics, and live self-tests. It must not require
users to install an editor or decompile/extract the game.

**Current scope decision:** programming expressiveness was the M6 Character Systems
priority, and those code contracts are now proven. The direct follow-up is an M6 art pass:
ground the real asset/scene contracts and extend open-mod's source-independent pipeline for
the new mechanics, enemies, events, characters, and character UI before M7. MIT code may be
adapted with notice, but Downfall art, ported content, and extracted game assets are not
assumed reusable.

## Conclusion: our baseline is a COMBINATION

There is no single repo to fork. The right baseline is:

> **godogen's architecture & frame-grounded self-repair loop** (with GodotMaker's
> named `gm-*` stages as the concrete blueprint), retargeted from "generate a
> game" to "generate a mod", **sitting on top of ModTemplate-StS2's mod anatomy +
> BaseLib + dotnet-new scaffolding**, borrowing **Claude-Code-Game-Studios'
> patterns** for organizing skills/agents/hooks only where useful.

For advanced characters, add **Downfall's demonstrated mechanic families and shared-kernel
pattern** as the implementation-depth baseline. This remains a combination, not a fork:
open-mod owns a smaller capability-oriented layout, versioned patch seams, natural-language
composition, and stronger Type + Scenario verification than the reference repository.

Imagine/Vofy does not change that core combination. It is a reusable **edge acquisition
pattern** for optional art: delegate account/task/download concerns to a user-owned CLI,
then return immediately to open-mod's source-independent asset contract.

Mapping the closed-loop stages (GodotMaker's `gm-*` names; godogen has the same
shape) onto our text-to-mod flow:

| Closed-loop stage | Our text-to-mod equivalent |
|---|---|
| `gm-gdd` (idea → design contract) | interview → **mod spec** (relic: rarity, tier, trigger, effect) |
| `gm-scaffold` | `dotnet new` from ModTemplate-StS2 (+ BaseLib dep) |
| `gm-build` (workers write code+tests) | write the C# element + `Mod.json` + localization + placeholder art |
| `gm-verify` (`godot --headless`, tests) | build the `.dll`, produce the `.pck` (PckPacker), static checks |
| `gm-evaluate` (launch, E2E, screenshots) | launch STS2 **"Load with mods"**, confirm element loads (log marker) + effect triggers |
| `gm-fixgap`/`gm-rescue` | read game logs → **auto-repair** → re-test (our headline differentiator) |
| `gm-finalize` | package the mod; optional (opt-in) Workshop publish |

Key adaptation: godogen/GodotMaker verify on **screenshots** (frame-grounded);
STS2 has no documented headless test mode, so our observed reality is the
**game log + live state**, not frames — same principle, different sensor.

## Open questions this raises (feed into PROJECT.md §12)
- How far can we push a **headless / scripted** STS2 test vs. needing the real
  client for the evaluate step? (GodotMaker leans on headless + screenshots.)
- Can we reuse BaseLib's abstractions enough that most "single-element" mods are
  near-templated, leaving the LLM to fill only the effect logic?
- Does the ModTemplate `dotnet new` flow assume Rider/IDE, or is it fully CLI
  (`dotnet`)? Our skill needs the CLI path.
- Study the existing **STS2 Modding Assistant MCP** (Nexus #345) alongside these
  — where it overlaps GodotMaker's role and where our non-programmer + game-pack
  + auto-repair angle differs.

## Sources
- https://github.com/htdt/godogen (primary architecture baseline)
- https://github.com/RandallLiuXin/GodotMaker
- https://github.com/Alchyr/ModTemplate-StS2 (+ /wiki)
- https://github.com/Donchitos/Claude-Code-Game-Studios
- https://github.com/cgxjdzz/AgentTheSpire (closest competitor + art-pipeline reference)
- https://github.com/WhiteTowerAI/imagine-skill (managed-credit CLI art-source reference)
- https://github.com/lamali292/Downfall (advanced character capability reference)

---

# Deep dive: ModTemplate-StS2 wiki (the STS2 modding ground truth)

Fetched 2026-07-01 from the repo wiki. These are the concrete engineering facts
our skill + game pack must encode. Grouped by the stage of our pipeline they
affect. **⚠️ = a technical risk we must validate.**

## Toolchain / environment (feeds `gm-scaffold` equivalent)
- **Engine binary:** MegaCrit's custom Godot, "**MegaDot**"
  (megadot.megacrit.com); fallback = matching Godot .NET version. Needed to
  generate the `.pck`.
- **.NET SDK 9.0+** required. C# + OOP knowledge assumed (for humans — for us,
  the game pack replaces that).
- **Scaffolding IS pure-CLI:** `dotnet new install Alchyr.Sts2.Templates`
  then `dotnet new`. Three templates: Character / Content / Empty. Rule:
  project name no spaces, `.sln`, "Put solution and project in same directory".
- **BaseLib** = the community base library (github.com/Alchyr/BaseLib-StS2),
  its own wiki at alchyr.github.io/BaseLib-Wiki (Features list is the index).
  Best obtained by **subscribing on Steam Workshop** (id `3737335127`) →
  lands at `Steam/steamapps/workshop/content/2868840/3737335127/BaseLib`.
- **StS2ModAnalyzers** (Roslyn analyzers, github.com/Alchyr/StS2ModAnalyzers):
  reports missing localization and can generate placeholder localization. The
  authoritative list of localizable types is in its `LocalizationAnalyzer.cs`.
- **Publicizer** is used by the template so mods can access non-public members
  (shows up as `[OriginalAttributes(...)]` in decompiled code).

## Build vs Publish (feeds `gm-build`/`gm-verify` equivalent)
- **`Build`** (fast): compiles only the `.dll` (code) and copies it to the mods
  folder. Enough when only code changed.
- **`Publish`** (slow): compiles `.dll` **+ generates the `.pck` via Godot** +
  copies `.dll`/`.pck`/`.json` to the mods folder. **Required for any non-code
  change (localization, images, scenes) to show up.**
- Path to the game/Godot is configured in **`Directory.Build.props`**.
- ⚠️ **CLI-publish is not clearly documented.** The wiki demonstrates Publish via
  Rider's right-click button. But it references an underlying `GodotPublish`
  MSBuild target and a `DOTNET_ROOT=~/.dotnet` workaround — strong hint a pure
  `dotnet`/MSBuild CLI publish exists. **We must verify a fully headless,
  no-IDE `.dll`+`.pck` publish, or our automation breaks.**

## Where mods live (feeds packaging / install)
- Local dev mods: `mods/` in the StS2 install dir (Win/Linux) or
  `SlayTheSpire2.app/Contents/MacOS` (Mac). Template auto-copies here on
  build/publish.
- Workshop mods: `Steam/steamapps/workshop/content/2868840/<workshopId>/`.
- A mod = up to 3 files, best in a folder named after it:
  `ModName.json` (manifest) + `ModName.dll` (code) + `ModName.pck` (assets/text).
- **Manifest fields** (confirmed): `id` (immutable, drives file loading),
  `name`, `author`, `description`, `version`, `has_pck`, `has_dll`,
  `min_game_version` (new as of 0.105), `dependencies:[{id,min_version}]`,
  `affects_gameplay` (set false for cosmetic-only or multiplayer desyncs).

## Content model (feeds the "understand request → code" core)
- Everything is a **`Model`** (`CardModel`, `RelicModel`, `PowerModel`, ...) that
  hooks lifecycle actions (`OnPlay`, etc.). Behaviour = a series of **commands**
  (`DamageCmd.Attack`, `PowerCmd.Apply<StrengthPower>`). **Prefer commands over
  manipulating data directly.**
- BaseLib provides `Custom*Model` base classes; you inherit and override
  properties. With Character/Content templates you inherit the mod-named
  abstract (`FoobarModCard`) which auto-assigns the pool.
- **The canonical authoring loop:** "think of similar base-game content →
  decompile it → adapt its commands." This is exactly what the **game pack must
  pre-digest** so the LLM doesn't have to decompile live every time.

## Anatomy of adding ONE card (our MVP target, end to end)
1. Create Card class inheriting `<Mod>Card`; fill template fields: cost (int),
   then type/rarity/target via dropdowns.
2. Pool: `[Pool(...)]` attribute (auto with character template).
3. Localization: `localization/eng/cards.json`; analyzer flags missing entries
   and generates placeholders (Alt+Enter "Generate localization").
4. Art: `<Mod>/images/card_portraits/big/<class_name_lower>.png`,
   **1000x760 PNG** — the one portrait the game loads for a normal card (606x852
   full-art is Ancient-rarity only, out of scope). Template ships a default `card.png`
   placeholder — so **placeholder-first art is already the native workflow.**
5. Effect logic: copy the command sequence from a similar decompiled base card.
6. Build/Publish → appears in Settings → Mod Settings → test via dev console.

## Closed-loop testing — the make-or-break for our differentiator
Good news (all confirmed):
- **Dev console** opens with `` ` `` / `~` / `*` / `'` / `Shift+8`; `help` lists
  commands; can **spawn content instantly** to test (`help card`, etc.).
- **Logs are readable and parseable** — `godot.log` at
  `%appdata%/SlayTheSpire2/logs` (Win). BaseLib adds `showlog`, `open logs`, and
  a "**Open log window on startup**" option. **This is our auto-repair input.**
- **Can launch WITHOUT Steam:** create `steam_appid.txt` containing `2868840`
  in the game dir, then run `SlayTheSpire2.exe` directly — **critical for
  scripted/automated launch.**
- **Rich launch-arg surface:** `-nomods` (vanilla), `-fastmp host_standard` /
  `-fastmp join` / `-clientId` (multiplayer). Wiki even ships .bat/.sh scripts
  that launch multiple instances programmatically.
- Own logging via `MainFile.Logger.Info(...)` — we can have generated mods emit
  assertions/markers we then grep from `godot.log`.

⚠️ **The hard part:** there is **no documented headless / unattended test entry
point.** GodotMaker leans on `godot --headless` + gdUnit4 + screenshots; STS2
testing as documented means launching the full client, getting into a run, and
spawning via the dev console (key-driven). Driving "confirm the effect actually
triggers" automatically likely requires either scripting the dev console, an
in-mod self-test that logs a marker on load/trigger, or log-assertion — none of
which is off-the-shelf. **This is our #1 technical risk to prototype early.**

## Decompilation (feeds game-pack authoring, not runtime)
- Game code is in **`sts2.dll`** under `data_sts2_windows_x86_64/` (varies by
  platform). Decompile with Rider (Ctrl+Click to navigate), or external tools
  ILSpy / dnSpy / dotPeek. Search by Type/Method/Member; "Analyze"/"Find Usages"
  to trace how a power/card is used.
- Decompiled code has oddities (publicizer attributes, verbose getters,
  compiler-generated types, constants inlined). The game pack should capture
  cleaned, canonical patterns — not raw decompiler output.

## STS2 ecosystem components discovered (reusable, not competitors)
- **BaseLib-StS2** + **BaseLib-Wiki** — the base library our mods depend on.
- **StS2ModAnalyzers** — localization/analysis, reusable in our build step.
- **megacrit/sts2-mod-uploader** — MegaCrit's **official CLI mod uploader** for
  Workshop → our opt-in publish step can wrap this instead of hand-rolling.
- **ptrlrd/spire-codex** — decompile/API project (from earlier research).

## Net effect on our plan
- `gm-scaffold` → `dotnet new` (solved, CLI). Low risk.
- The content-authoring core is tractable *because* of BaseLib `Custom*Model` +
  the "copy a similar base card" pattern — the game pack's main job is to
  pre-digest those patterns and BaseLib's Features so the LLM writes correct
  command sequences without live decompiling.
- Placeholder-art-first is native. Low risk.
- **Two things gate the whole promise and must be prototyped first:**
  1. **Headless/CLI publish** of `.dll`+`.pck` (no Rider).
  2. **Automated in-game verification** (launch via `steam_appid.txt`, then
     assert via logs / dev-console scripting / in-mod self-test markers).

# MegaCrit design language (research 2026-07-09 — feeds M7's proactive interview)

Gathered to answer: *what does "designing like MegaCrit" actually mean*, so M7's
interview can guide a mod author instead of just transcribing one sentence into one
element. Nine principles distilled from developer interviews + deckbuilder design
analysis. These are the raw material for the planned pack page
`reference/design-principles.md` (see `IMPLEMENTATION_PLAN.md`, M7).

1. **Risk vs reward is the spine.** Anthony Giovannetti (co-designer): *"The core design
   of Slay the Spire is risk versus reward."* Every card / relic / choice should be a
   meaningful trade-off. An effect with no opportunity cost is boring.
2. **Cards are tactical; relics/mechanics are strategic.** The game's beating heart is the
   *"synergistic relationship between a player's deck and their collection of relics"* —
   cards give in-combat options, relics/character mechanics set the long-term route the
   whole run builds toward. The strategic frame is the "整体 (overall thing)", not any
   single power.
3. **The unit of design is the ARCHETYPE, not the card.** A character's pool is 2-3
   distinct "machines". Giovannetti: *"If I change one card and it's part of a particular
   strategy, that's going to have other ramifications on the cards in that strategy."*
   Cards don't exist in isolation.
4. **Each card plays a ROLE in its machine:** *enabler* (produces a resource:
   energy/Strength/poison/draw/Souls), *payoff* (converts the resource into a win
   condition), *engine/glue* (draw, deck-thinning, tutor — keeps it running), *standalone*
   (flexible support any archetype uses). STS2 example: Necrobinder's Souls loop —
   "Gain X Souls" Block skills (enabler) ↔ "Consume all Souls" attacks (payoff).
5. **Scale, don't flat-line.** A run pivots from front-loaded power into an *exponential
   scaling engine* before front-loading stops working (Ironclad: early aggression →
   Strength/Exhaust/Block engine). Bad design just makes *"the math bigger"* — good design
   asks "how does this reach act 3?"
6. **Character identity = a shared resource/keyword vocabulary + a play-feel**, spread
   across the whole pool — Silent = poison/discard/Sly, Defect = orbs/Focus,
   Necrobinder = Souls. Identity is the *language the pool speaks*, not one signature power.
7. **A "commit moment" rewards betting on a build.** A build-defining rare or a key relic
   is a signpost that makes the player go all-in on an archetype. A card you *want to build
   around* is build-defining.
8. **Constraints tame degenerate combos** — not just number nerfs. When Dual Wield went
   infinite, they restricted it to copy *Skill* cards only. Rarity / cost / scope / target
   are design levers.
9. **Data finds problems; intuition shapes fixes.** Pick rate too low = *"basically not a
   card in our game"*; but changes are judged on *fun*, not pure math. (Single-player, so
   decks needn't be balanced against each other — they can be tuned for entertainment.)

**The "联动性 (interplay)" ladder these imply** (M7 scope): L1 technical dependency
(A triggers B — already shipped via the interaction harness, historical project
`CanaryCombo`), L2 resource loop (enabler↔payoff,
principle 4), L3 archetype identity (principles 3+6, needs M6's content types), L4 run
rhythm & risk-reward advisor (principles 1+5+7+8, the highest rung). See `IMPLEMENTATION_PLAN.md`
§5 M7 for how each rung maps to interview/spec work.

**Sources (2026-07-09):**
- Anthony Giovannetti interview — Justin Gary, *Crafting Slay the Spire* (2024):
  https://justingarydesign.substack.com/p/anthony-giovannetti-crafting-slay
- *How Slay the Spire's devs use data to balance their roguelike deck-builder* — Game
  Developer (2018):
  https://www.gamedeveloper.com/design/how-i-slay-the-spire-i-s-devs-use-data-to-balance-their-roguelike-deck-builder
- *Slay the Spire designer discusses new characters and card game inspirations* — PC Gamer
  (2018): https://www.pcgamer.com/slay-the-spire-designer-discusses-new-characters-and-card-game-inspirations/
- *What Makes a Deckbuilder Replayable?* — GlyphShuffle:
  https://glyphshuffle.com/blog/what-makes-a-deckbuilder-replayable
- STS2 character archetype summaries (Ironclad/Silent/Necrobinder pools) — community guides
  surveyed via search 2026-07-09.
