# Generated Codex plugin payload - do NOT hand-edit

Everything under this plugin directory **except** `.codex-plugin/plugin.json`
and this note is **generated** by `publish.sh --plugin` from the hand-written
source under `games/sts2/skills/` and `games/sts2/tools/`.

- `skills/modmaker/`, `skills/sts2-api/` are rendered from `games/sts2/skills/`.
- `skills/modmaker/scripts/*.py` contains the cross-platform build, launch,
  verification, and art tools copied from `games/sts2/tools/`.
- All internal references are relative to the owning skill, so Codex may install/cache
  the plugin independently of the user's current workspace.

**Edit the source, then re-run `./publish.sh --plugin`.** Changes made directly
here are overwritten on the next publish.

This payload is committed because the Codex marketplace consumes it from the repository.
