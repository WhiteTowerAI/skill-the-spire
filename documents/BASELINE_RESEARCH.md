# Baseline Research: Reference Repos for Text-to-Mod (STS2)

> Companion to PROJECT.md. Records what we learned from candidate baselines and
> which we build on. Fetched 2026-07-01 via local proxy.

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
> (COMPETITIVE_LANDSCAPE.md) and is now our **primary** architectural baseline,
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

## Conclusion: our baseline is a COMBINATION

There is no single repo to fork. The right baseline is:

> **godogen's architecture & frame-grounded self-repair loop** (with GodotMaker's
> named `gm-*` stages as the concrete blueprint), retargeted from "generate a
> game" to "generate a mod", **sitting on top of ModTemplate-StS2's mod anatomy +
> BaseLib + dotnet-new scaffolding**, borrowing **Claude-Code-Game-Studios'
> patterns** for organizing skills/agents/hooks only where useful.

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
   **1000x760 PNG** (or 606x852 full-art). Template ships a default `card.png`
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