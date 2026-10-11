#!/usr/bin/env bash
# Publish the Skill the Spire STS2 skill source into the committed skills/ payload.
#
# Turns the source under games/sts2/skills/ (which uses ${VAR} placeholders)
# into a ready-to-load Agent Skills tree.
#
# Usage:
#   ./publish.sh [--force]                    # render the committed top-level skills/
#   ./publish.sh --agent codex [--out <dir>]  # render a local Codex dev copy
#
# Two shapes:
#   (default)      : the SHIP flow. Renders into the repo's top-level skills/ (COMMITTED).
#                    This one tree serves every distribution: `npx skills add` discovers it,
#                    and it is the plugin root for Codex and Claude Code, which get their
#                    manifests copied from scripts/publish/ into skills/.codex-plugin/ and
#                    skills/.claude-plugin/. Only skills/ lands in a user's plugin cache.
#                    The repo-root marketplaces point at ./skills. Tools are bundled inside
#                    skills/modmaker/scripts/ and referenced by RELATIVE path (the Agent Skills
#                    spec convention). The bundled tools are Python (.py), so they run on
#                    Windows/macOS/Linux.
#   --agent codex  : the DEV flow. Renders into <out>/.agents/skills/ (git-ignored).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HELPERS="$REPO_ROOT/scripts/publish"
SRC="$REPO_ROOT/games/sts2/skills"

AGENT=""
OUT=""
FORCE=0

usage() {
    sed -n '1,21p' "$0" >&2
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
    "")
        SKILLS_DIR_REL="skills"
        ;;
    codex)
        SKILLS_DIR_REL=".agents/skills"
        ;;
    *)
        echo "error: --agent accepts only codex; omit it to render the committed skills/." >&2
        usage; exit 1 ;;
esac

TOOLS_DIR_REL="$SKILLS_DIR_REL/modmaker/scripts"
MODMAKER_SKILL_DIR="."
STS2API_SKILL_DIR="../sts2api"
GAME_TOOLS_DIR="../modmaker/scripts"

# Default target: this repo root.
if [ -z "$OUT" ]; then
    OUT="$REPO_ROOT"
fi
TARGET="$(cd "$OUT" 2>/dev/null && pwd || (mkdir -p "$OUT" && cd "$OUT" && pwd))"

SKILLS_DIR_ABS="$TARGET/$SKILLS_DIR_REL"

if [ "$FORCE" -eq 1 ] && [ -d "$SKILLS_DIR_ABS" ]; then
    echo "Force: cleaning $SKILLS_DIR_ABS"
    rm -rf "${SKILLS_DIR_ABS:?}"
fi

# Stage into a temp dir, render placeholders, then sync into place.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/modmaker" "$TMP/sts2api"
cp -R "$SRC/modmaker/." "$TMP/modmaker/"
cp -R "$SRC/sts2api/." "$TMP/sts2api/"

$PYTHON "$HELPERS/render_dir.py" "$TMP" \
    "MODMAKER_SKILL_DIR=$MODMAKER_SKILL_DIR" \
    "STS2API_SKILL_DIR=$STS2API_SKILL_DIR" \
    "GAME_TOOLS_DIR=$GAME_TOOLS_DIR"

mkdir -p "$SKILLS_DIR_ABS/modmaker" "$SKILLS_DIR_ABS/sts2api"
# rsync if available (clean deletes), else cp -R.
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$TMP/modmaker/" "$SKILLS_DIR_ABS/modmaker/"
    rsync -a --delete "$TMP/sts2api/" "$SKILLS_DIR_ABS/sts2api/"
else
    rm -rf "${SKILLS_DIR_ABS:?}/modmaker" "${SKILLS_DIR_ABS:?}/sts2api"
    mkdir -p "$SKILLS_DIR_ABS/modmaker" "$SKILLS_DIR_ABS/sts2api"
    cp -R "$TMP/modmaker/." "$SKILLS_DIR_ABS/modmaker/"
    cp -R "$TMP/sts2api/." "$SKILLS_DIR_ABS/sts2api/"
fi

# Bundle the cross-platform Python tools inside the modmaker skill for every mode.
TOOLS_DIR_ABS="$TARGET/$TOOLS_DIR_REL"
rm -rf "${TOOLS_DIR_ABS:?}"
mkdir -p "$TOOLS_DIR_ABS"
for t in "$REPO_ROOT"/games/sts2/tools/*.py; do
    # Catalog collection is a repository-maintainer workflow: one needs a C# project/template,
    # the other reads the gitignored decompile under baselines/. Neither can run in a user's
    # runtime, and generated Mods need only the checked catalogs plus their validators.
    case "$(basename "$t")" in
        collect_vanilla_catalog.py|collect_model_hooks.py) continue ;;
    esac
    cp "$t" "$TOOLS_DIR_ABS/"
done

echo "Published STS2 skills -> $SKILLS_DIR_ABS"
echo "  modmaker:  $(count_files "$SKILLS_DIR_ABS/modmaker") files"
echo "  sts2api:  $(count_files "$SKILLS_DIR_ABS/sts2api") files"
echo "  tools:     $(count_files "$TOOLS_DIR_ABS") files (in modmaker/scripts/)"
if [ -z "$AGENT" ]; then
    # skills/ is also the plugin root for both agents, so their manifests live inside it.
    mkdir -p "$SKILLS_DIR_ABS/.codex-plugin" "$SKILLS_DIR_ABS/.claude-plugin"
    cp "$HELPERS/codex-plugin.json" "$SKILLS_DIR_ABS/.codex-plugin/plugin.json"
    cp "$HELPERS/claude-plugin.json" "$SKILLS_DIR_ABS/.claude-plugin/plugin.json"
    cp "$HELPERS/generated.md" "$SKILLS_DIR_ABS/GENERATED.md"
    echo "Committed skills payload ready. Install with any of:"
    echo "  codex plugin marketplace add $REPO_ROOT && codex plugin add skill-the-spire@skill-the-spire"
    echo "  claude plugin marketplace add $REPO_ROOT && claude plugin install skill-the-spire@skill-the-spire"
    echo "  npx skills add WhiteTowerAI/skill-the-spire"
else
    echo "Start a new Codex thread, then invoke \$modmaker."
fi
