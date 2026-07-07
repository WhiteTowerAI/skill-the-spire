# Generated plugin payload — do NOT hand-edit

Everything under this plugin directory **except** `.claude-plugin/plugin.json`
and this note is **generated** by `publish.sh --plugin` from the hand-written
source under `games/sts2/skills/` and `games/sts2/tools/`.

- `skills/modmaker/`, `skills/sts2-api/` — rendered from `games/sts2/skills/`
  (the `${VAR}` placeholders are resolved at publish time; the one exception is
  `${CLAUDE_PLUGIN_ROOT}`, which is left intact for Claude Code to substitute at
  load time with this plugin's install directory).
- `tools/*.ps1` — copied verbatim from `games/sts2/tools/`.

**Edit the source, then re-run `./publish.sh --plugin`.** Changes made directly
here are overwritten on the next publish.

This payload is committed to the repo on purpose (unlike `.claude/skills/`,
which is git-ignored): the plugin marketplace fetches it straight from the
repository, so it must be present in git.
