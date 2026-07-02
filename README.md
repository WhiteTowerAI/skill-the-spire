# open-mod

**open-mod** is a free, open-source skill that turns one plain-English sentence
into a real, working game mod — no coding required. You describe what you want,
and the skill scaffolds, writes, builds, and verifies a mod that actually loads
and runs in-game.

First supported game: **Slay the Spire 2 (STS2)**.

> **Status: M2 (early).** Right now open-mod reliably makes **relics** (passive or
> triggered items the player owns). Cards, potions, custom art, and one-click
> Steam Workshop publishing are on the roadmap. See [Current limits](#current-limits).

---

## What you'll need first

open-mod drives the normal STS2 modding toolchain, so you need a machine set up to
build STS2 mods:

1. **Slay the Spire 2**, installed via Steam. Note your install path (e.g.
   `D:\Steam\steamapps\common\Slay the Spire 2`).
2. **.NET SDK 9.0 or newer** — check with `dotnet --version`.
3. **BaseLib** — the community modding library open-mod builds on. Subscribe to it
   on the Steam Workshop (search "BaseLib" for STS2), then launch the game once so
   Steam downloads it.
4. **Claude Code** — this skill runs inside Claude Code.
5. **Python 3** and **Git Bash** (the install step uses a short bash script). On
   Windows, install Python from python.org — note the "python3" that ships with
   Windows by default is a non-working placeholder.

The very first time you make a mod, the skill will also install the STS2 project
template (`dotnet new install Alchyr.Sts2.Templates`) if it isn't already present.

---

## Install (one time)

1. **Get the code.** Clone this repository:

   ```bash
   git clone https://github.com/WhiteTowerAI/open-mod.git
   cd open-mod
   ```

2. **Publish the skill** so Claude Code can see it. From the repo root, in Git Bash:

   ```bash
   ./publish.sh --agent claude
   ```

   This renders the skill into `.claude/skills/` inside the repo. You should see:

   ```
   Published STS2 skill for Claude -> .../.claude/skills
     modmaker:  8 files
     sts2-api:  3 files
   ```

3. **Open this repo in Claude Code.** Start Claude Code with the `open-mod` folder
   as the working directory. The skill is project-scoped, so `/modmaker` becomes
   available whenever Claude Code is opened here.

That's it. You don't need to re-run `publish.sh` unless you pull new changes.

---

## Make a mod

In Claude Code (opened in this repo), run the skill and describe your mod in one
sentence:

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
4. **Launch the game and check the log** to confirm the mod loads with no errors.
5. **Walk you through a quick in-game check** that the effect actually fires
   (see below).

You'll be asked to do a couple of hands-on things (launch the game, click through a
menu) — that's expected. Just follow the prompts.

---

## Play it in-game

When the skill finishes, your mod is already installed into the game's `mods/`
folder. To try it:

1. **Launch Slay the Spire 2** and start a run.
2. Open the **developer console** with the **`` ` ``** (backtick) key — it's enabled
   automatically because the game is running modded. Close it with `Esc`.
3. **Give yourself the relic** by name, e.g.:

   ```
   relic add <YOUR-RELIC-ID>
   ```

   The skill tells you the exact id after it builds (something like
   `MYRELIC-MY_RELIC`). A unique part of the name works too.
4. **Trigger it.** For a "start of combat" relic, just enter a fight and watch it
   fire.

If it loaded and fired, you're done — you made a working mod from one sentence.

> **Where are the files?** The mod lands in
> `…\Slay the Spire 2\mods\<YourModName>\` (the `.dll` + `.pck` + `.json`). The mod's
> source project is created in a folder you choose, outside this repo.

---

## Current limits

open-mod is early. Today it does the following well, and is honest about the rest:

- ✅ **Relics** — passive/triggered items (start of combat, start of turn, etc.).
- ✅ **Load verification** — it proves the mod loads in-game, not just "it compiled".
- 🚧 **Effect verification is guided, not automated** — the skill walks you through
  the dev-console check; it doesn't yet drive the game itself.
- ⏳ **Not yet:** cards, potions, custom/generated art (relics use a placeholder
  icon for now), automatic error-repair, and one-click Steam Workshop publishing.

If you ask for something outside this, the skill will tell you plainly rather than
half-build it.

## Troubleshooting

- **`/modmaker` doesn't appear** — make sure you ran `./publish.sh --agent claude`
  and opened Claude Code with the `open-mod` repo as the working directory.
- **`publish.sh` says no working Python** — the Windows Store `python3` is a
  placeholder. Install real Python 3 from python.org and reopen your shell.
- **The relic shows a plain coin/placeholder icon** — expected for now; custom art
  is on the roadmap.

## For contributors

The skill source lives under `games/sts2/` (orchestrator in
`games/sts2/skills/modmaker/`, the STS2 knowledge pack in
`games/sts2/skills/sts2-api/`, helper scripts in `games/sts2/tools/`). `publish.sh`
renders it into `.claude/skills/` (git-ignored — regenerate, don't commit).
Planning and research docs are in `documents/`. See `CLAUDE.md` and `AGENTS.md`
before contributing.

## License

See [LICENSE](./LICENSE).


