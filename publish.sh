#!/usr/bin/env bash
# Publish the open-mod STS2 skill source into a runtime-specific layout.
#
# Turns the source under games/sts2/skills/ (which uses ${VAR} placeholders)
# into a ready-to-load Codex or portable Agent Skills tree.
#
# Usage:
#   ./publish.sh --agent codex [--out <target_dir>] [--force]
#   ./publish.sh --agent codex                # defaults --out to this repo root
#   ./publish.sh --plugin [--force]           # render the committed Codex plugin payload
#   ./publish.sh --portable [--force]         # render the committed cross-agent payload (skills.sh)
#
# Three shapes:
#   --agent codex  : the DEV flow. Renders into <out>/.agents/skills/ (git-ignored).
#   --plugin       : the Codex SHIP flow. Renders into plugins/open-mod/skills/
#                    (COMMITTED), including tools in the modmaker skill's scripts/ folder.
#   --portable     : the CROSS-AGENT ship flow. Renders into the repo's top-level skills/
#                    (COMMITTED) — the layout skills.sh (`npx skills add`) auto-discovers and
#                    installs into Codex / Cursor / OpenClaw / etc. Tools are bundled inside
#                    skills/modmaker/scripts/ and referenced by RELATIVE path (the AgentSkills
#                    spec convention).
#                    The bundled tools are Python (.py), so they run on Windows/macOS/Linux.
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

count_files() {
    "$PYTHON" -c 'import pathlib, sys; print(sum(path.is_file() for path in pathlib.Path(sys.argv[1]).rglob("*")))' "$1"
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

# The source description names the runtime, while all installed paths stay relative to
# the current skill so Codex can relocate/cache the plugin safely.
AGENT_NAME="Codex"

if [ "$PLUGIN" -eq 1 ]; then
    SKILLS_DIR_REL="plugins/open-mod/skills"
elif [ "$PORTABLE" -eq 1 ]; then
    SKILLS_DIR_REL="skills"
else
    case "$AGENT" in
        codex)
            SKILLS_DIR_REL=".agents/skills"
            ;;
        *)
            echo "error: pass --plugin (Codex ship), --portable (cross-agent ship), or --agent codex (dev)." >&2
            usage; exit 1 ;;
    esac
fi

TOOLS_DIR_REL="$SKILLS_DIR_REL/modmaker/scripts"
MODMAKER_SKILL_DIR="."
STS2_API_SKILL_DIR="../sts2-api"
GAME_TOOLS_DIR="../modmaker/scripts"

# Default target: this repo root.
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

$PYTHON "$HELPERS/render_dir.py" "$TMP" \
    "AGENT_NAME=$AGENT_NAME" \
    "MODMAKER_SKILL_DIR=$MODMAKER_SKILL_DIR" \
    "STS2_API_SKILL_DIR=$STS2_API_SKILL_DIR" \
    "GAME_TOOLS_DIR=$GAME_TOOLS_DIR"

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

# Bundle the cross-platform Python tools inside the modmaker skill for every mode.
TOOLS_DIR_ABS="$TARGET/$TOOLS_DIR_REL"
rm -rf "${TOOLS_DIR_ABS:?}"
mkdir -p "$TOOLS_DIR_ABS"
for t in "$REPO_ROOT"/games/sts2/tools/*.py; do
    cp "$t" "$TOOLS_DIR_ABS/"
done

echo "Published STS2 skill for $AGENT_NAME -> $SKILLS_DIR_ABS"
echo "  modmaker:  $(count_files "$SKILLS_DIR_ABS/modmaker") files"
echo "  sts2-api:  $(count_files "$SKILLS_DIR_ABS/sts2-api") files"
if [ "$PLUGIN" -eq 1 ]; then
    echo "  tools:     $(count_files "$TOOLS_DIR_ABS") files (in skills/modmaker/scripts/)"
    echo "Committed Codex plugin payload ready. Test locally with:"
    echo "  codex plugin marketplace add $REPO_ROOT"
    echo "  codex plugin add open-mod@open-mod"
elif [ "$PORTABLE" -eq 1 ]; then
    echo "  tools:     $(count_files "$TOOLS_DIR_ABS") files (in skills/modmaker/scripts/)"
    echo "Committed cross-agent payload ready. Install into any agent with:"
    echo "  npx skills add WhiteTowerAI/open-mod"
else
    echo "Start a new Codex thread, then invoke \$modmaker."
fi
