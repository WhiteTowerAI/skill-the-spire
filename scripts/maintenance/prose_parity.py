#!/usr/bin/env python3
"""Content-conservation check for shipped skill prose.

Restructuring the skill files (splitting by surface, extracting data, moving
diagnostics) must never silently drop a capability boundary, a pinned value, or
an explicit gap. This tool reduces a skill tree to a normalized multiset of
substantive lines so a before/after comparison proves nothing was lost.

Normalization deliberately ignores what restructuring is *allowed* to change:
list markers, indentation, heading depth, and blank lines. It preserves the
words, so a dropped "explicit gap" line is always visible.

Usage:
  # snapshot before a change
  python prose_parity.py snapshot games/sts2/skills --out .tmp/prose-before.json
  # after the change, compare
  python prose_parity.py compare .tmp/prose-before.json games/sts2/skills
  # allow lines that were intentionally removed/reworded
  python prose_parity.py compare .tmp/prose-before.json games/sts2/skills \
      --allow-removed .tmp/allow-removed.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Leading list/quote/heading markers and trailing whitespace carry no meaning
# for content conservation; the words do.
MARKER_RE = re.compile(r"^[\s>]*(?:[-*+]\s+|\d+\.\s+|#{1,6}\s+|\[[ xX]\]\s+)*")
WS_RE = re.compile(r"\s+")


def normalize(line: str) -> str:
    stripped = MARKER_RE.sub("", line).strip()
    stripped = WS_RE.sub(" ", stripped)
    return stripped


def is_substantive(text: str) -> bool:
    """Skip blanks, bare fences, and pure-punctuation table rules."""
    if not text:
        return False
    if text.startswith("```"):
        return False
    if not re.search(r"[A-Za-z0-9]", text):
        return False
    # Markdown table separator rows such as |---|---:|
    if re.fullmatch(r"\|[\s:\-|]+\|?", text):
        return False
    return True


def collect(root: Path) -> Counter[str]:
    lines: Counter[str] = Counter()
    for path in sorted(root.rglob("*.md")):
        for raw in path.read_text(encoding="utf-8").splitlines():
            text = normalize(raw)
            if is_substantive(text):
                lines[text] += 1
    return lines


def digest(counter: Counter[str]) -> str:
    h = hashlib.sha256()
    for text in sorted(counter):
        h.update(f"{counter[text]}\x00{text}\x00".encode("utf-8"))
    return h.hexdigest()


def cmd_snapshot(args: argparse.Namespace) -> int:
    counter = collect(Path(args.root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "root": str(args.root),
        "distinct": len(counter),
        "total": sum(counter.values()),
        "digest": digest(counter),
        "lines": dict(sorted(counter.items())),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[parity] snapshot {out}")
    print(f"[parity] distinct={payload['distinct']} total={payload['total']}")
    print(f"[parity] digest={payload['digest'][:16]}")
    return 0


def load_allow(path: str | None) -> set[str]:
    if not path:
        return set()
    allow: set[str] = set()
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        text = normalize(raw)
        if is_substantive(text):
            allow.add(text)
    return allow


def cmd_compare(args: argparse.Namespace) -> int:
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    old = Counter(before["lines"])
    new = collect(Path(args.root))
    allow = load_allow(args.allow_removed)

    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    unexplained = [line for line in removed if line not in allow]
    explained = [line for line in removed if line in allow]

    print(f"[parity] before distinct={len(old)} after distinct={len(new)}")
    print(f"[parity] removed={len(removed)} (allowed {len(explained)}) added={len(added)}")

    if added and args.show_added:
        print(f"\n[parity] added lines ({len(added)}):")
        for line in added[: args.limit]:
            print(f"  + {line[:160]}")
        if len(added) > args.limit:
            print(f"  ... {len(added) - args.limit} more")

    if unexplained:
        print(f"\n[parity] FAIL: {len(unexplained)} line(s) disappeared with no allowance:")
        for line in unexplained[: args.limit]:
            print(f"  - {line[:160]}")
        if len(unexplained) > args.limit:
            print(f"  ... {len(unexplained) - args.limit} more")
        return 1

    print("\n[parity] PASS: every pre-existing substantive line is still present "
          "(or explicitly allowed).")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    snap = sub.add_parser("snapshot", help="record the current normalized line multiset")
    snap.add_argument("root")
    snap.add_argument("--out", required=True)
    snap.set_defaults(func=cmd_snapshot)

    cmp_ = sub.add_parser("compare", help="verify no substantive line vanished")
    cmp_.add_argument("before")
    cmp_.add_argument("root")
    cmp_.add_argument("--allow-removed", default=None,
                      help="file of lines intentionally removed or reworded")
    cmp_.add_argument("--show-added", action="store_true")
    cmp_.add_argument("--limit", type=int, default=40)
    cmp_.set_defaults(func=cmd_compare)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
