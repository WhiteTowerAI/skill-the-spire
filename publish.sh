#!/usr/bin/env bash
# Publish the open-mod STS2 skill source into a runtime-specific layout.
#
# Turns the source under games/sts2/skills/ (which uses ${VAR} placeholders)
# into a ready-to-load skill tree. For Claude Code that is .claude/skills/.
#
# Usage:
#   ./publish.sh --agent claude [--out <target_dir>] [--force]
#   ./publish.sh --agent claude               # defaults --out to this repo root
#
# Mirrors the shape of htdt/godogen's publish.sh, trimmed to one game (STS2)
# and, for now, one runtime (Claude Code). The codex branch is stubbed: the
# variable values are wired but the codex-specific metadata step is deferred to
# M5, so `--agent codex` currently errors out with a clear message.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HELPERS="$REPO_ROOT/scripts/publish"
SRC="$REPO_ROOT/games/sts2/skills"

AGENT=""
OUT=""
FORCE=0

usage() {
    sed -n '1,16p' "$0" >&2
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
        --agent) AGENT="${2:-}"; shift 2 ;;
        --out)   OUT="${2:-}";   shift 2 ;;
        --force) FORCE=1;        shift   ;;
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

case "$AGENT" in
    claude)
        SKILLS_DIR_REL=".claude/skills"
        AGENT_NAME="Claude"
        MODMAKER_COMMAND="/modmaker"
        STS2_API_COMMAND="/sts2-api"
        ;;
    codex)
        echo "error: --agent codex is not wired yet (deferred to M5)." >&2
        echo "The source keeps the \${VAR} placeholders so this is a small add later." >&2
        exit 1
        ;;
    *)
        echo "error: --agent must be 'claude' (codex deferred to M5)" >&2
        usage; exit 1 ;;
esac

# Default target: this repo root (so /modmaker is testable in-place).
if [ -z "$OUT" ]; then
    OUT="$REPO_ROOT"
fi
TARGET="$(cd "$OUT" 2>/dev/null && pwd || (mkdir -p "$OUT" && cd "$OUT" && pwd))"

SKILLS_DIR_ABS="$TARGET/$SKILLS_DIR_REL"
MODMAKER_SKILL_DIR="$SKILLS_DIR_REL/modmaker"
STS2_API_SKILL_DIR="$SKILLS_DIR_REL/sts2-api"
# tools stay with the source (not copied into .claude); reference them there.
GAME_TOOLS_DIR="games/sts2/tools"

# Stage into a temp dir, render placeholders, then sync into place.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/modmaker" "$TMP/sts2-api"
cp -R "$SRC/modmaker/." "$TMP/modmaker/"
cp -R "$SRC/sts2-api/." "$TMP/sts2-api/"

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

echo "Published STS2 skill for $AGENT_NAME -> $SKILLS_DIR_ABS"
echo "  modmaker:  $(find "$SKILLS_DIR_ABS/modmaker" -type f | wc -l) files"
echo "  sts2-api:  $(find "$SKILLS_DIR_ABS/sts2-api" -type f | wc -l) files"
echo "Reload skills in Claude Code, then run $MODMAKER_COMMAND."
