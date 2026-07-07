# Generated cross-agent payload — do NOT hand-edit

Everything under this top-level `skills/` directory is **generated** by
`publish.sh --portable` from the hand-written source under `games/sts2/skills/`
and `games/sts2/tools/`.

This is the **cross-agent** distribution layout: `skills/<name>/SKILL.md` is the
shape [skills.sh](https://skills.sh) (`npx skills add`) auto-discovers, so
`npx skills add WhiteTowerAI/open-mod` installs the mod maker into Codex, Cursor,
OpenClaw, and other agents that read the standard skills directory.

- `skills/modmaker/`, `skills/sts2-api/` — rendered from `games/sts2/skills/`.
  Tool and skill-internal references are **relative** (`scripts/build.py`,
  `./recipes/…`), because off Claude there is no `${CLAUDE_PLUGIN_ROOT}` variable.
- `skills/modmaker/scripts/*.py` — the three cross-platform Python tools
  (build / launch / grep_log), copied from `games/sts2/tools/`. They run on
  Windows/macOS/Linux (only Windows is verified on the dev box).

**Edit the source, then re-run `./publish.sh --portable`.** Changes made directly
here are overwritten on the next publish.

Committed on purpose (skills.sh fetches it from git). The Claude-native plugin
payload is a separate committed tree under `plugins/open-mod/` (paths use
`${CLAUDE_PLUGIN_ROOT}` instead of relative `scripts/`); regenerate it with
`./publish.sh --plugin`.
