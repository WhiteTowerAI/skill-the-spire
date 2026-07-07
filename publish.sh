#!/usr/bin/env bash
# Publish the open-mod STS2 skill source into a runtime-specific layout.
#
# Turns the source under games/sts2/skills/ (which uses ${VAR} placeholders)
# into a ready-to-load skill tree. For Claude Code that is .claude/skills/.
#
# Usage:
#   ./publish.sh --agent claude [--out <target_dir>] [--force]
#   ./publish.sh --agent claude               # defaults --out to this repo root
#   ./publish.sh --plugin [--force]           # render the committed Claude plugin payload
#   ./publish.sh --portable [--force]         # render the committed cross-agent payload (skills.sh)
#
# Three shapes:
#   --agent claude : the DEV flow. Renders skills into <out>/.claude/skills/ (git-ignored)
#                    with tool paths pointing at games/sts2/tools/ — testable in-place when
#                    Claude Code is opened with this repo as cwd.
#   --plugin       : the Claude SHIP flow. Renders into plugins/open-mod/{skills,tools}/
#                    (COMMITTED) with tool/skill paths pointing at ${CLAUDE_PLUGIN_ROOT}/...
#                    so the mod maker works from any cwd once installed via the plugin
#                    marketplace (/plugin marketplace add WhiteTowerAI/open-mod).
#                    ${CLAUDE_PLUGIN_ROOT} is left un-rendered on purpose — Claude Code
#                    substitutes it at load time.
#   --portable     : the CROSS-AGENT ship flow. Renders into the repo's top-level skills/
#                    (COMMITTED) — the layout skills.sh (`npx skills add`) auto-discovers and
#                    installs into Codex / Cursor / OpenClaw / etc. Tools are bundled inside
#                    skills/modmaker/scripts/ and referenced by RELATIVE path (the AgentSkills
#                    spec convention — no ${CLAUDE_PLUGIN_ROOT} variable exists off Claude).
#                    The three tools are Python (.py), so they run on Windows/macOS/Linux.
#
# Mirrors the shape of htdt/godogen's publish.sh, trimmed to one game (STS2)
# and, for now, one runtime (Claude Code). The codex branch is stubbed: the
# variable values are wired but the codex-specific metadata step is deferred to
# a later milestone, so `--agent codex` currently errors out with a clear message.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HELPERS="$REPO_ROOT/scripts/publish"
SRC="$REPO_ROOT/games/sts2/skills"

AGENT=""
OUT=""
FORCE=0
PLUGIN=0
PORTABLE=0

usage() {
    sed -n '1,32p' "$0" >&2
}

# Pick a working Python 3. On Windows the bare `python3` on PATH is often the
# Microsoft Store shim, which exits non-zero without running — so probe each
# candidate by actually invoking it, not just `command -v`.
find_python() {
    local cand
    for cand in python3 python py; do
        if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; assert sys.version_info[0]==3' >/dev/null 2>&1; then
            echo "$cand"; return 0
        fi
    done
    return 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        --agent)    AGENT="${2:-}"; shift 2 ;;
        --out)      OUT="${2:-}";   shift 2 ;;
        --force)    FORCE=1;        shift   ;;
        --plugin)   PLUGIN=1;       shift   ;;
        --portable) PORTABLE=1;     shift   ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "error: unknown option $1" >&2; usage; exit 1 ;;
        *)
            if [ -n "$OUT" ]; then
                echo "error: target specified more than once" >&2
                exit 1
            fi
            OUT="$1"; shift ;;
    esac
done

PYTHON="$(find_python)" || {
    echo "error: no working Python 3 found (tried python3, python, py)." >&2
    echo "Install Python 3, or ensure it's on PATH (note: the Windows Store 'python3' shim does not count)." >&2
    exit 1
}

MODE_COUNT=$((PLUGIN + PORTABLE))
[ -n "$AGENT" ] && MODE_COUNT=$((MODE_COUNT + 1))
if [ "$MODE_COUNT" -gt 1 ]; then
    echo "error: use exactly one of --agent, --plugin, --portable." >&2
    usage; exit 1
fi

# Common command/name values (Claude Code runtime). The command names are stored
# WITHOUT a leading slash (see the render_dir.py call note); the source templates
# supply the "/" literally.
AGENT_NAME="Claude"
MODMAKER_COMMAND="modmaker"
STS2_API_COMMAND="sts2-api"

if [ "$PLUGIN" -eq 1 ]; then
    # SHIP flow: render the committed plugin payload. Tool/skill paths point at
    # ${CLAUDE_PLUGIN_ROOT}, which Claude Code resolves to the plugin's install
    # dir at load time — so we pass it through render_dir.py UN-substituted by
    # simply never giving it as a key. Single-quote to stop bash from expanding it.
    PLUGIN_ROOT_VAR='${CLAUDE_PLUGIN_ROOT}'
    SKILLS_DIR_REL="plugins/open-mod/skills"
    TOOLS_DIR_REL="plugins/open-mod/tools"
    MODMAKER_SKILL_DIR="$PLUGIN_ROOT_VAR/skills/modmaker"
    STS2_API_SKILL_DIR="$PLUGIN_ROOT_VAR/skills/sts2-api"
    GAME_TOOLS_DIR="$PLUGIN_ROOT_VAR/tools"
elif [ "$PORTABLE" -eq 1 ]; then
    # CROSS-AGENT ship flow: committed top-level skills/ that skills.sh discovers.
    # No ${CLAUDE_PLUGIN_ROOT} off Claude, so tools live inside the modmaker skill
    # (skills/modmaker/scripts/) and are referenced by RELATIVE path. Skill-internal
    # file refs are also relative (each skill dir is the agent's read root).
    SKILLS_DIR_REL="skills"
    TOOLS_DIR_REL="skills/modmaker/scripts"
    MODMAKER_SKILL_DIR="."
    STS2_API_SKILL_DIR="."
    GAME_TOOLS_DIR="scripts"
else
    case "$AGENT" in
        claude)
            SKILLS_DIR_REL=".claude/skills"
            ;;
        codex)
            echo "error: --agent codex is not wired yet (deferred to a later milestone)." >&2
            echo "The source keeps the \${VAR} placeholders so this is a small add later." >&2
            exit 1
            ;;
        *)
            echo "error: pass --plugin (Claude ship), --portable (cross-agent ship), or --agent claude (dev)." >&2
            usage; exit 1 ;;
    esac
    MODMAKER_SKILL_DIR="$SKILLS_DIR_REL/modmaker"
    STS2_API_SKILL_DIR="$SKILLS_DIR_REL/sts2-api"
    # DEV flow: tools stay with the source (not copied); reference them there.
    GAME_TOOLS_DIR="games/sts2/tools"
fi

# Default target: this repo root (so /modmaker is testable in-place; plugin
# payload lands under plugins/open-mod/ here for commit).
if [ -z "$OUT" ]; then
    OUT="$REPO_ROOT"
fi
TARGET="$(cd "$OUT" 2>/dev/null && pwd || (mkdir -p "$OUT" && cd "$OUT" && pwd))"

SKILLS_DIR_ABS="$TARGET/$SKILLS_DIR_REL"

# Stage into a temp dir, render placeholders, then sync into place.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/modmaker" "$TMP/sts2-api"
cp -R "$SRC/modmaker/." "$TMP/modmaker/"
cp -R "$SRC/sts2-api/." "$TMP/sts2-api/"

# NOTE on the command values: MODMAKER_COMMAND/STS2_API_COMMAND are the leaf slash-
# command names WITHOUT a leading slash ("modmaker", not "/modmaker"). The source
# templates write the slash literally ("/${MODMAKER_COMMAND}"). This dodges Git Bash's
# MSYS path conversion, which rewrites a bare "/modmaker" argv entry into a Windows
# path ("D:/Git/modmaker") before python sees it — while leaving real path args
# (like $HELPERS) correctly converted.
$PYTHON "$HELPERS/render_dir.py" "$TMP" \
    "AGENT_NAME=$AGENT_NAME" \
    "MODMAKER_COMMAND=$MODMAKER_COMMAND" \
    "STS2_API_COMMAND=$STS2_API_COMMAND" \
    "MODMAKER_SKILL_DIR=$MODMAKER_SKILL_DIR" \
    "STS2_API_SKILL_DIR=$STS2_API_SKILL_DIR" \
    "GAME_TOOLS_DIR=$GAME_TOOLS_DIR"

# Make the pack a fork-context lookup skill (keeps it out of main context).
if [ -f "$TMP/sts2-api/SKILL.md" ]; then
    $PYTHON "$HELPERS/inject_claude_lookup_frontmatter.py" "$TMP/sts2-api/SKILL.md"
fi

if [ "$FORCE" -eq 1 ] && [ -d "$SKILLS_DIR_ABS" ]; then
    echo "Force: cleaning $SKILLS_DIR_ABS"
    rm -rf "${SKILLS_DIR_ABS:?}/modmaker" "${SKILLS_DIR_ABS:?}/sts2-api"
fi

mkdir -p "$SKILLS_DIR_ABS/modmaker" "$SKILLS_DIR_ABS/sts2-api"
# rsync if available (clean deletes), else cp -R.
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$TMP/modmaker/" "$SKILLS_DIR_ABS/modmaker/"
    rsync -a --delete "$TMP/sts2-api/" "$SKILLS_DIR_ABS/sts2-api/"
else
    rm -rf "${SKILLS_DIR_ABS:?}/modmaker" "${SKILLS_DIR_ABS:?}/sts2-api"
    mkdir -p "$SKILLS_DIR_ABS/modmaker" "$SKILLS_DIR_ABS/sts2-api"
    cp -R "$TMP/modmaker/." "$SKILLS_DIR_ABS/modmaker/"
    cp -R "$TMP/sts2-api/." "$SKILLS_DIR_ABS/sts2-api/"
fi

# Ship flows (plugin + portable) bundle the cross-platform Python tools next to the
# skills so the rendered tool paths resolve after install. Only the .py tools are
# shipped (the legacy .ps1 stay as source in games/sts2/tools/, not distributed).
if [ "$PLUGIN" -eq 1 ] || [ "$PORTABLE" -eq 1 ]; then
    TOOLS_DIR_ABS="$TARGET/$TOOLS_DIR_REL"
    # Clean any stale tools (e.g. legacy .ps1 from an earlier publish) then ship .py.
    rm -rf "${TOOLS_DIR_ABS:?}"
    mkdir -p "$TOOLS_DIR_ABS"
    for t in "$REPO_ROOT"/games/sts2/tools/*.py; do
        cp "$t" "$TOOLS_DIR_ABS/"
    done
fi

echo "Published STS2 skill for $AGENT_NAME -> $SKILLS_DIR_ABS"
echo "  modmaker:  $(find "$SKILLS_DIR_ABS/modmaker" -type f | wc -l) files"
echo "  sts2-api:  $(find "$SKILLS_DIR_ABS/sts2-api" -type f | wc -l) files"
if [ "$PLUGIN" -eq 1 ]; then
    echo "  tools:     $(find "$TOOLS_DIR_ABS" -type f | wc -l) files"
    echo "Committed plugin payload ready. Test locally with:"
    echo "  /plugin marketplace add $REPO_ROOT"
    echo "  /plugin install open-mod@open-mod"
elif [ "$PORTABLE" -eq 1 ]; then
    echo "  tools:     $(find "$TOOLS_DIR_ABS" -type f | wc -l) files (in skills/modmaker/scripts/)"
    echo "Committed cross-agent payload ready. Install into any agent with:"
    echo "  npx skills add WhiteTowerAI/open-mod"
else
    echo "Reload skills in Claude Code, then run /$MODMAKER_COMMAND."
fi
