# open-mod

**open-mod** is a free, open-source skill that turns one plain-English sentence
into a real, working game mod — no coding required. You describe what you want,
and the skill scaffolds, writes, builds, and verifies a mod that actually loads
and runs in-game.

First supported game: **Slay the Spire 2 (STS2)**.

> **Status: M0-M6 complete at their grounded support boundaries.** open-mod reliably makes **relics, potions, cards, and
> custom powers** (including a card that applies its own power), **custom card
> mechanics** (keywords, card enchantments, and orbs), **enemy encounters** (a custom
> monster plus its encounter), **map events / World Nodes**, and bounded advanced
> **playable characters**. Character support includes a selectable Foundation, valid
> pools/starters, combat resources, ordered semantic card-play buffers, a fixed icon+text
> mechanic UI, and eight checked static art profiles: selection portrait/background,
> top-panel icon, combat/rest/merchant bodies, five-layer full energy, and a compact
> resource icon. It proves both that the
> mod **loads** and that its **effect actually fires** in-game, repairs common build
> errors automatically, and supports placeholder or generated art for card portraits,
> relic/power/potion/enchantment/orb icons, a static monster combat+bestiary body, and
> normal event initial/explicit page portraits. Character scene-backed static art is
> packaged by the bundled build tools, so mod authors do not install Godot or MegaDot.
> Keyword
> card text and hover-tooltip presentation are also live-verified; keywords intentionally
> own no bitmap. When the
> agent runtime exposes a native image tool, open-mod can use it
> without a separate image API key; otherwise the existing BYO/managed/local routes remain
> available and missing art stays on the placeholder. Stateful relic timing now covers
> both counters that continue across combats/save-resume and turn numbers that reset each
> combat. Enemy encounters support
> rich deterministic/conditional move cycles with multi-turn behavior proof. A fresh
> Wayfinder character composed the advanced resource/UI and spatial-route mechanics and
> passed build plus two-combat live verification. The Event slice now includes immediate,
> page, selection, reward, resumable-combat, and terminal-combat outcomes plus one bounded
> code-native portrait-halo VFX profile and native vanilla-style colored/moving description
> text. A bounded solo Quest Card can also force one custom Event from an Unknown MapPoint
> in one specified act, then be completed/removed by that Event. Its headed proof and the
> final general Event suite passed strict Tier 2 with no fresh error. Event static art also
> includes one three-reference generation and real headed render acceptance. All six
> bounded native-presentation follow-ups are complete: rich text and typed tips, native
> exact-lethal warnings, Card/relic acquisition previews, preference-respecting screen
> shake, and curated built-in Event VFX. **Direct next is M7's proactive beginner
> interview.** Animation, materials, multiplayer presentation, and audio are later,
> non-blocking tracks. Vanilla editing and one-click Steam
> Workshop publishing also remain out of scope.
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

You do **not** need to install Godot, MegaDot, or PckPacker manually. The character
template declares the upstream PckPacker package, and open-mod's bundled build wrapper
automatically handles the raw static `.tscn` files that package skips.

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
  Keyword text is also verified on the real hand card and hover tooltip; its tooltip has
  no icon by design, so keyword support does not create an image asset.
  Orb icon art is verified separately in its smart tooltip and trigger flash; the
  persistent combat body still uses an explicit vanilla Spine scene/SFX fallback.
- ✅ **Load verification** — it proves the mod loads in-game, not just "it compiled".
- ✅ **Effect verification (automated)** — the mod carries an in-process self-test
  that drives itself into the required hosted scenario and confirms the effect fires, with no dev-console
  typing. It falls back to a guided manual check and reports load-only if the
  self-test can't reach its scenario.
- ✅ **Automatic error-repair** — a bounded loop diagnoses and fixes common build
  failures, then re-verifies.
- ✅ **Custom art for grounded static surfaces** — card portraits,
  relic/power/potion/enchantment/orb icons, one static monster body, normal event
  initial/page portraits, and eight Character profiles are live-verified. The Character
  set covers selection portrait/background, top-panel icon, static combat/rest/merchant
  bodies, five full-energy layers, and a compact resource icon. Placeholder art remains
  the zero-setup default. Generation prefers a
  callable host-native image tool (Codex `image_gen` when exposed), then supports Vofy,
  your own compatible image backend, or a local image. Every route uses the same
  deterministic STS2 normalizer and falls back safely if unavailable. Reference-capable
  generation randomly selects three real, type-matched STS2 samples for every grounded
  family, including Event's six reviewed and attributed references.
- ✅ **Enemy encounters and rich move cycles** — a plain-English request can produce a
  custom monster plus its encounter, including self custom-Powers, player debuffs,
  Block/Heal, multi-attacks, combined actions, deterministic cycles, and conditional
  branches. Multi-turn verification observes exact move history, hit count, and
  player/monster HP/Block/Power state; a fresh one-sentence run passed build + both live
  tiers with zero repair on 2026-07-15. A checked 360x360 static body now renders in both
  combat and bestiary with an explicit built-in fallback; Spine and move animation are a
  later expansion.
- ✅ **Map events / World Nodes** — a plain-English request can produce a custom event
  with nested page/option text; ordered public Cmd effects; locked choices; blocking card
  selections and custom rewards; and one special combat that either resumes a named Event
  page or proceeds directly to the map. The pipeline enters the real room, drives every
  independent SPEC branch through actual UI, identifies the custom encounter, and observes
  exact state/page/map results. A normal
  event's custom initial and explicit page portraits are live-supported with checked
  fallbacks. Custom phobia art and custom/Ancient scenes remain deferred behind grounded
  engine/BaseLib blockers. The bounded code-native `portrait_halo` VFX is supported with
  Fast Mode behavior and explicit cleanup. Page and option descriptions also support the
  vanilla-observed bounded `b`/color/`jitter`/`sine` vocabulary through the native label;
  titles remain plain and no generated VFX node is involved. Arbitrary VFX remains later. A 2026-07-20
  three-reference generation acceptance
  also normalized, packed, and rendered a new 3440x1613 Event portrait in the real room.
  A bounded delayed follow-up may use one custom unplayable Quest Card to force one custom
  Event from an Unknown MapPoint in one specified act; the target stays out of ordinary
  pools and its completion option consumes the token. One headed run proved both guards,
  real room/Event forcing, visible UI, consumption, and restored normal hooks.
  Direct merchant/rest/treasure room transitions and a second combat from the same Event
  instance remain unsupported, as do arbitrary forced chains, multiplayer semantics, and
  a new save-roundtrip claim for this capability.
- ✅ **Native presentation 1-6** — Card descriptions and standard Card/relic/potion/power
  Hover Tips support bounded per-surface vanilla colors. Enabled Event options support
  typed Hover Tips and normal relic-backed text/metadata; locked tips remain suppressed and
  normal-layout relic images remain deferred. Exact HP/Max HP costs can drive the native
  inclusive-lethal warning glow. Native Card/relic acquisition presentation, the
  preference-respecting `weak_short` screen shake, and the curated built-in `trial_noble`
  Event VFX are also supported with checked cleanup.
- ✅ **Character Foundation** — a plain-English request can produce a selectable minimal
  character with character-scoped card/relic/potion pools, exact starter deck/relic, HP,
  standard 3 energy, and one public/BaseLib starter mechanic. Verification clicks the real
  character button, starts the run, checks the starter ecosystem, and observes the combat
  effect. Its eight static art profiles have real selection, combat, RestSite, and Shop
  render proof. Background/rest/merchant use minimal raw scenes packed without Godot or
  MegaDot; full energy uses BaseLib's native five-layer counter. Locked selection, the map
  marker, and native custom-Character Ancient presentation remain unverified and retain
  explicit fallbacks.
- ✅ **Advanced Character composition** — combat-only resources use explicit payment and
  a fixed 220x32 icon+text counter with text-only fallback; bounded ordered semantic
  buffers produce configured output cards while source cards use STS2's normal result
  piles.
  A fresh Wayfinder acceptance combined both into a spatial route mechanic and passed
  selection, run-start, payment, geometry, history, and two-combat reset proof.
- 🧪 **Character capability kernel (maintainer infrastructure)** — a self-contained,
  version-gated B-risk postfix now has build, load, real UI-host, typed-state, conflict,
  idempotence, and two-combat lifetime proof. It is deliberately not advertised as a
  gameplay mechanic and has not been extracted into `OpenMod.Runtime`.
- ⏭️ **Direct next: M7 proactive beginner interview.** M6 is closed at the exact
  boundaries above; do not reopen its canaries while adding concern-aware questions,
  recommended defaults, and character resource/archetype/run-rhythm guidance.
- ⏳ **Later presentation expansion:** animation, materials, multiplayer presentation,
  and audio each require their own Downfall/BaseLib/game inventory, fallback contract,
  and headed proof. **Not yet:** retained-card
  custom zone UI, unverified advanced character families,
  nonstandard character energy,
  editing existing vanilla content, production-size character card pools, and one-click
  Steam Workshop publishing. Positioned Event speech/thought bubbles are future outlook
  only and have no M6/M7 delivery plan.
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
  failure. To generate custom art, choose it during intake. The skill uses a host-native
  image tool only when it is actually callable; otherwise select a compatible backend,
  Vofy, or a local image. If generation fails, the mod deliberately remains on the
  working placeholder rather than blocking the build.

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
is `plugins/open-mod/.claude-plugin/plugin.json`. Current planning and research live in
`documents/`; completed process evidence is indexed in `documents/history/README.md`.
See `AGENTS.md` before contributing.

## License

See [LICENSE](./LICENSE).


