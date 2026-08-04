# Generated portable payload - do NOT hand-edit

Everything under this top-level `skills/` directory is **generated** by
`publish.sh --portable` from the hand-written source under `games/sts2/skills/`
and `games/sts2/tools/`.

This is the **cross-agent** distribution layout: `skills/<name>/SKILL.md` is the
shape [skills.sh](https://skills.sh) (`npx skills add`) auto-discovers, so
`npx skills add WhiteTowerAI/open-mod` installs the mod maker into Codex, Cursor,
OpenClaw, and other agents that read the standard skills directory.

- `skills/modmaker/`, `skills/sts2-api/` — rendered from `games/sts2/skills/`.
  Tool and skill-internal references are relative.
- `skills/modmaker/scripts/*.py` — the cross-platform Python tools
  (build / launch / grep_log / gen_sprite / acquire_sprite), copied from
  `games/sts2/tools/`. They run on
  Windows/macOS/Linux (only Windows is verified on the dev box).

**Edit the source, then re-run `./publish.sh --portable`.** Changes made directly
here are overwritten on the next publish.

Committed on purpose because skills.sh fetches it from Git. The Codex plugin is a separate
committed tree under `plugins/open-mod/`; regenerate it with `./publish.sh --plugin`.
