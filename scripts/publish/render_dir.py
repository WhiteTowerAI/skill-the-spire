"""Replace ${KEY} tokens in every text file under a directory tree.

Vendored from htdt/godogen (scripts/publish/render_dir.py, MIT) unchanged —
it is a generic token replacer with no godogen-specific logic. Used by
publish.sh to turn the skill source (with ${MODMAKER_SKILL_DIR} etc.) into a
runtime-specific layout under .claude/skills/.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: render_dir.py <root> KEY=VALUE...", file=sys.stderr)
        return 2

    root = Path(argv[1])
    replacements: dict[str, str] = {}
    for pair in argv[2:]:
        key, value = pair.split("=", 1)
        replacements[f"${{{key}}}"] = value

    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for token, value in replacements.items():
            text = text.replace(token, value)
        if text != original:
            path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
