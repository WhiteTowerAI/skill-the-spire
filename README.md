# open-mod

**open-mod** is a free, open-source skill that turns one plain-English sentence
into a real, working game mod — no coding required. You describe what you want,
and the skill scaffolds, writes, builds, and verifies a mod that actually loads
and runs in-game.

First supported game: **Slay the Spire 2 (STS2)**.

> **Status: M6 Core in progress.** open-mod reliably makes **relics, potions, cards, and
> custom powers** (including a card that applies its own power), **custom card
> mechanics** (keywords, card enchantments, and orbs), **enemy encounters** (a custom
> monster plus its encounter), and **map events / World Nodes**. It proves both that the
> mod **loads** and that its **effect actually fires** in-game, repairs common build
> errors automatically, and supports placeholder or generated art for the four core
> element types. Stateful relic timing now covers both counters that continue across
> combats/save-resume and turn numbers that reset each combat. Enemy encounters support
> rich deterministic/conditional move cycles with multi-turn behavior proof. Minimal
> Character is the direct next step. Editing vanilla content and one-click Steam
> Workshop publishing remain out of scope today.
> See [Current limits](#current-limits).

---

## What you'll need first

open-mod drives the normal STS2 modding toolchain, so you need a machine set up to
build STS2 mods:

1. **Slay the Spire 2**, installed via Steam. Note your install path (for example,
   `<SteamLibrary>\steamapps\common\Slay the Spire 2`).
2. **.NET SDK 9.0 or newer** — check with `dotnet --version`.
3. **BaseLib** — the community modding library open-mod builds on. Subscribe to it
   on the Steam Workshop (search "BaseLib" for STS2), then launch the game once so
   Steam downloads it.
4. **A compatible coding agent** — Claude Code is the fully verified path; the portable
   package also targets Codex, Cursor, OpenClaw, and other Agent Skills consumers.
5. **Python 3**. On Windows, install Python from python.org — the `python3` command
   preinstalled by Windows may be a non-working Store placeholder.

The very first time you make a mod, the skill will also install the STS2 project
template (`dotnet new install Alchyr.Sts2.Templates`) if it isn't already present.

---

## Install (one time)

No clone, no build step, no fixed working directory — install once and `/modmaker`
is available from anywhere.

**Claude Code** (native plugin) — run these two commands:

```
/plugin marketplace add WhiteTowerAI/open-mod
/plugin install open-mod@open-mod
```

The first registers this repository as a plugin marketplace; the second installs
the `open-mod` plugin (the mod-maker skill, the STS2 knowledge pack, and the build
tools). To update later, run `/plugin marketplace update open-mod`.

**Other agents** (Codex, Cursor, OpenClaw, …) — use the cross-agent installer:

```
npx skills add WhiteTowerAI/open-mod
```

This drops the skill into wherever your agent looks for skills. Both paths pull
straight from GitHub.

That's it. `/modmaker` now works in any project.

> **A note on other agents:** the STS2 *knowledge* (recipes, mechanics, error
> fixes) works the same everywhere. The build/verify **tools** are cross-platform
> Python, but the full one-command build → self-test loop is currently proven on
> **Windows + Claude Code**; on other setups you may need to run the build/launch
> steps yourself. See [Current limits](#current-limits).

> **Prefer the dev flow?** Contributors who want to edit the skill in-place can
> still clone the repo and run `./publish.sh --agent claude` (see
> [For contributors](#for-contributors)).

---

## Make a mod

In Claude Code (any project, once the plugin is installed), run the skill and
describe your mod in one sentence:

```
/modmaker
```

Then say what you want, for example:

> a relic that heals you 5 HP at the start of every combat

The skill takes it from there. It will:

1. **Ask you at most one short round of questions** — only if something's genuinely
   unclear (e.g. how rare the relic should be). Plain language, no jargon.
2. **Show you a plan** in plain words and confirm it with you.
3. **Scaffold, write, and build** the mod.
4. **Launch the real game and check its log** to prove the mod loads with no errors.
5. **Run an unattended in-process self-test**: the generated mod drives itself into the
   hosted scenario its content needs, fires the effect, and records the observed marker.
   If navigation cannot reach that scenario, the skill falls back to a guided manual check and reports
   load-only rather than pretending behavior was verified.

The standard verification path requires no dev-console typing or menu clicks. You can
still launch the game afterward to play with the finished mod yourself.

---

## Play it in-game

When the skill finishes, your mod is already installed into the game's `mods/`
folder and has normally passed both automated verification tiers. To play with it:

1. Launch Slay the Spire 2 and start a run.
2. Open the developer console with the **`` ` ``** (backtick) key; close it with
   `Esc`. Debug commands are available because the game is running modded.
3. Grant the element using the exact ID the skill reports:
   - relic: `relic add <ID>`
   - potion: `potion <ID>`
   - card: `card <ID>`
   - enemy encounter: `fight <ENCOUNTER_ID>`
   - event: `event <ID>`
4. Use or trigger it normally. This is for your own play and visual inspection — it
   is not the primary proof path, which the skill already ran automatically.

If the automatic harness could not navigate into its scenario, these same steps become its
honest manual fallback; the skill will tell you exactly what to enter and will only
claim Tier 2 after the effect marker is observed.

> **Where are the files?** The mod lands in
> `…\Slay the Spire 2\mods\<YourModName>\` (the `.dll` + `.pck` + `.json`). The mod's
> source project is created in a folder you choose, outside this repo.

---

## Current limits

open-mod is still young. Today it does the following well, and is honest about the rest:

- ✅ **Relics, potions, cards, and custom powers** — including a card that applies
  its own custom power (the multi-element "combo" case).
- ✅ **Stateful relic timing** — Happy Flower-style counters can continue across combats
  and save/resume; Stone Calendar-style timing resets with each combat's turn number.
- ✅ **Custom card mechanics** — keywords (shared, reusable card rules), card
  enchantments (a persistent modification attached to a card), and orbs (a channeled
  passive/evoke mechanic). Each is proven to actually change combat state, not just load.
- ✅ **Load verification** — it proves the mod loads in-game, not just "it compiled".
- ✅ **Effect verification (automated)** — the mod carries an in-process self-test
  that drives itself into the required hosted scenario and confirms the effect fires, with no dev-console
  typing. It falls back to a guided manual check and reports load-only if the
  self-test can't reach its scenario.
- ✅ **Automatic error-repair** — a bounded loop diagnoses and fixes common build
  failures, then re-verifies.
- ✅ **Custom art for all four types** — card portraits and relic/power/potion icons
  are live-verified. Placeholder art remains the zero-setup default; generation uses
  your own compatible image backend and falls back safely if unavailable.
- ✅ **Enemy encounters and rich move cycles** — a plain-English request can produce a
  custom monster plus its encounter, including self custom-Powers, player debuffs,
  Block/Heal, multi-attacks, combined actions, deterministic cycles, and conditional
  branches. Multi-turn verification observes exact move history, hit count, and
  player/monster HP/Block/Power state; a fresh one-sentence run passed build + both live
  tiers with zero repair on 2026-07-15. Custom monster *art* (an animated scene) remains
  provisional, so custom enemies use an explicit built-in fallback appearance for now.
- ✅ **Map events / World Nodes** — a plain-English request can produce a custom event
  with nested page/option text and a real run-state consequence. The pipeline enters the
  event room, clicks its real option UI, and independently observes the result. Custom
  event art remains provisional, so events use a verified vanilla portrait placeholder.
- ⏭️ **Direct next: Minimal Character** — prove a selectable character can start a run with
  valid starter content and one small supported mechanic combination.
- ⏳ **Not yet:** editing existing vanilla content, production-size playable characters,
  and one-click Steam Workshop publishing.
- ⚠️ **Platform verification:** the complete build → launch → self-test loop is proven
  on Windows + Claude Code. The tools have macOS/Linux and portable-agent paths, but
  those combinations have not yet been live-verified. Registry directory listing is
  also still open; direct GitHub install already works.

If you ask for something outside this, the skill will tell you plainly rather than
half-build it.

## Troubleshooting

- **`/modmaker` doesn't appear** — confirm the plugin installed: run `/plugin` and
  check `open-mod` is listed and enabled. If you installed from a local clone
  instead, make sure you ran `./publish.sh --agent claude` and opened Claude Code
  with the `open-mod` repo as the working directory.
- **`publish.sh` says no working Python** — the Windows Store `python3` is a
  placeholder. Install real Python 3 from python.org and reopen your shell.
- **An element shows placeholder art** — placeholder is the default fast path, not a
  failure. To generate custom art, choose it during intake and provide a compatible
  image backend configuration; if generation fails, the mod deliberately remains on
  the working placeholder rather than blocking the build.

## For contributors

The skill source lives under `games/sts2/` (orchestrator in
`games/sts2/skills/modmaker/`, the STS2 knowledge pack in
`games/sts2/skills/sts2-api/`, cross-platform Python tools in `games/sts2/tools/`).
Source files use `${VAR}` placeholders; `publish.sh` renders them three ways:

- **`./publish.sh --agent claude`** — the dev flow. Renders into `.claude/skills/`
  (git-ignored, regenerate don't commit) with tool paths pointing at
  `games/sts2/tools/`. Testable in-place when Claude Code is opened here.
- **`./publish.sh --plugin`** — the Claude ship flow. Renders the committed plugin
  payload into `plugins/open-mod/{skills,tools}/` with paths pointing at
  `${CLAUDE_PLUGIN_ROOT}`, so the installed plugin works from any cwd.
- **`./publish.sh --portable`** — the cross-agent ship flow. Renders the committed
  top-level `skills/` (the layout `npx skills add` discovers) with tools bundled in
  `skills/modmaker/scripts/` and referenced by **relative** path (no
  `${CLAUDE_PLUGIN_ROOT}` off Claude).

Both ship payloads **are committed** (the marketplaces fetch them from git) — re-run
the relevant publish after any source change and commit the result. Don't hand-edit
the generated trees; see `plugins/open-mod/GENERATED.md` and `skills/GENERATED.md`.

The tools are **Python** (`build.py` / `launch.py` / `grep_log.py`), so they are
designed for Windows/macOS/Linux; invoke with `python` (on Windows the bare `python3`
is often the Store shim). Windows is live-verified; the macOS/Linux path defaults are
best-effort until tested on those systems.

The marketplace manifest is `.claude-plugin/marketplace.json`; the plugin manifest
is `plugins/open-mod/.claude-plugin/plugin.json`. Planning and research docs are in
`documents/`. See `CLAUDE.md` and `AGENTS.md` before contributing.

## License

See [LICENSE](./LICENSE).


