#!/usr/bin/env python3
"""Maintainer-only extractor for the pinned vanilla text glossary.

Why this exists. Generated Mods must read like the game: the same English and Simplified
Chinese name for every shared term (Block/格挡, Vulnerable/易伤, Draw Pile/抽牌堆), the same
highlight color for it, and the same Chinese measure word in front of it (给予2层易伤,
获得5点格挡). Agents otherwise invent their own translations and drop the highlight.

Every fact comes from the installed game's own localization: titled keyword, Power, Orb,
Enchantment, Affliction, and static Hover Tip names, plus every colored span vanilla uses in
player-facing rules text, aligned between `eng` and `zhs` by majority vote. Nothing here is
hand-written vocabulary.

Maintainer-only: it reads `SlayTheSpire2.pck`, which a user's runtime does not need. The
committed glossary it writes is the shipped artifact. `publish.sh` excludes this file from
both payloads.

Usage:

    python collect_text_glossary.py extract --sts2-dir <game dir>          # write the glossary
    python collect_text_glossary.py extract --sts2-dir <game dir> --check  # fail if stale
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path


SCHEMA = "skillthespire.sts2.text-glossary/v1"
HOST_VERSION = "0.107.1"
GLOSSARY_RELATIVE_PATH = Path("reference/catalogs/text-glossary-sts2-0.107.1.json")
TOOLS_DIR = Path(__file__).resolve().parent
API_ROOT = TOOLS_DIR.parent / "skills" / "sts2api"
LANGUAGES = ("eng", "zhs")

# Titled vocabulary: every title in these tables is a game term the rules text can name.
TITLED_TABLES = {
    "card_keywords": "keyword",
    "powers": "power",
    "orbs": "orb",
    "enchantments": "enchantment",
    "afflictions": "affliction",
    "static_hover_tips": "hover_tip",
}
# Rules-text fields whose colored spans count as observed vocabulary. Narrative Event pages,
# dialogue, and flavor are excluded: their color is atmosphere, not terminology.
RULES_FIELDS = {
    "cards": (".description",),
    "relics": (".description", ".eventDescription"),
    "potions": (".description",),
    "powers": (".description", ".smartDescription"),
    "enchantments": (".description", ".extraCardText"),
    "afflictions": (".description", ".extraCardText"),
    "orbs": (".smartDescription",),
    "card_keywords": (".description",),
    "static_hover_tips": (".description",),
    "modifiers": (".description",),
    "rest_site_ui": (".description",),
    "events": (".description",),
}
TERM_COLORS = ("gold", "purple", "red")
MIN_OBSERVED = 2
MEASURE_WORDS = ("层", "点", "张", "个", "次", "回合")
# Measure words are reported only for amount-bearing vocabulary; card-count words are grammar.
MEASURED_KINDS = {"power", "orb", "hover_tip"}
SPAN_RE = re.compile(r"\[(gold|purple|red)\]([^\[\]{}]+)\[/\1\]")
NUMBER_THEN_TERM_RE = re.compile(
    r"(?:\{[^{}]*\}|\d+)(?:\[/\w+\])?(" + "|".join(MEASURE_WORDS) + r")\[gold\]([^\[\]{}]+)\[/gold\]"
)
ANY_SPAN_RE = re.compile(r"\[(\w+)\]([^\[\]]+)\[/\1\]")
TAG_RE = re.compile(r"\[/?\w+[^\]]*\]")
BRACE_RE = re.compile(r"\{(?:[^{}]|\{[^{}]*\})*\}")
SKIP_ID_RE = re.compile(r"(MOCK|TEST|DEPRECATED|NETWORK_PROBLEM)")
HOTKEY_SUFFIX_RE = re.compile(r"\s*\{Hotkey:[^{}]*(?:\{\})?[^{}]*\}\s*$")


class GlossaryError(Exception):
    """A bounded extraction failure with an actionable message."""


def read_localization(pck_path: Path) -> dict[str, dict[str, dict[str, str]]]:
    """Return {language: {table: {key: value}}} for the required languages."""
    tables: dict[str, dict[str, dict[str, str]]] = {language: {} for language in LANGUAGES}
    with pck_path.open("rb") as handle:
        header = handle.read(112)
        if header[:4] != b"GDPC":
            raise GlossaryError(f"{pck_path} is not a Godot PCK")
        file_base, directory_offset = struct.unpack_from("<qq", header, 24)
        handle.seek(directory_offset)
        (count,) = struct.unpack("<I", handle.read(4))
        entries = []
        for _ in range(count):
            (length,) = struct.unpack("<I", handle.read(4))
            path = handle.read(length).rstrip(b"\0").decode("utf-8")
            offset, size = struct.unpack("<qq", handle.read(16))
            handle.read(20)
            entries.append((path, offset, size))
        for path, offset, size in entries:
            match = re.fullmatch(r"localization/(eng|zhs)/([a-z_]+)\.json", path)
            if not match:
                continue
            handle.seek(file_base + offset)
            data = json.loads(handle.read(size).decode("utf-8"))
            tables[match.group(1)][match.group(2)] = {
                key: value for key, value in data.items() if isinstance(value, str)
            }
    for language in LANGUAGES:
        if not tables[language]:
            raise GlossaryError(f"{pck_path} has no localization/{language} tables")
    return tables


def _clean_title(text: str) -> str:
    return HOTKEY_SUFFIX_RE.sub("", text).strip()


def _usage(english: str, chinese: str, rules: list[tuple[str, str]]) -> dict[str, int]:
    """Count highlighted versus plain uses of a term in vanilla rules text, per language.

    The ratio tells authoring and the Build style check whether vanilla always highlights a
    term (Block, Vulnerable) or only sometimes does (Attack, Max HP).
    """
    english_re = re.compile(rf"(?<![\w]){re.escape(english)}(?![\w])")
    chinese_re = re.compile(re.escape(chinese))
    counts = {"eng_colored": 0, "eng_plain": 0, "zhs_colored": 0, "zhs_plain": 0}
    for language, pattern, texts in (
        ("eng", english_re, (pair[0] for pair in rules)),
        ("zhs", chinese_re, (pair[1] for pair in rules)),
    ):
        for text in texts:
            text = BRACE_RE.sub(" ", text)
            counts[f"{language}_colored"] += sum(
                1 for span in ANY_SPAN_RE.finditer(text) if span.group(2) == (english if language == "eng" else chinese)
            )
            plain = ANY_SPAN_RE.sub(" ", text)
            counts[f"{language}_plain"] += len(pattern.findall(TAG_RE.sub(" ", plain)))
    return counts


def build_glossary(tables: dict[str, dict[str, dict[str, str]]]) -> dict:
    eng, zhs = tables["eng"], tables["zhs"]
    terms: dict[str, dict] = {}

    for table, kind in TITLED_TABLES.items():
        for key, english in sorted(eng.get(table, {}).items()):
            if not key.endswith(".title") or SKIP_ID_RE.search(key):
                continue
            english, chinese = _clean_title(english), _clean_title(zhs.get(table, {}).get(key, ""))
            if not english or not chinese or "{" in english + chinese:
                continue
            term = terms.setdefault(english, {"eng": english, "zhs": chinese, "kinds": set()})
            term["kinds"].add(kind)

    rules: list[tuple[str, str]] = []
    for table, suffixes in RULES_FIELDS.items():
        for key, english in eng.get(table, {}).items():
            if not key.endswith(suffixes) or SKIP_ID_RE.search(key):
                continue
            if table == "events" and ".options." not in key:
                continue
            rules.append((english, zhs.get(table, {}).get(key, "")))

    observed: Counter[tuple[str, str]] = Counter()
    pairs: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    measures: dict[str, Counter[str]] = defaultdict(Counter)
    for english, chinese in rules:
        for color in TERM_COLORS:
            english_spans = [m.group(2) for m in SPAN_RE.finditer(english) if m.group(1) == color]
            chinese_spans = [m.group(2) for m in SPAN_RE.finditer(chinese) if m.group(1) == color]
            for span in english_spans:
                observed[(span, color)] += 1
            if len(english_spans) == len(chinese_spans):
                for span, translated in zip(english_spans, chinese_spans):
                    pairs[(span, color)][translated] += 1
        for match in NUMBER_THEN_TERM_RE.finditer(chinese):
            measures[match.group(2)][match.group(1)] += 1

    for (english, color), count in observed.items():
        if count < MIN_OBSERVED and english not in terms or not re.search(r"[^\W\d_]", english):
            continue
        votes = pairs.get((english, color))
        term = terms.get(english)
        if term is None:
            if not votes:
                continue
            term = terms[english] = {"eng": english, "zhs": votes.most_common(1)[0][0], "kinds": set()}
        term["kinds"].add("observed")
        term.setdefault("colors", Counter())[color] += count

    rows = []
    for english in sorted(terms, key=str.casefold):
        term = terms[english]
        colors: Counter[str] = term.get("colors", Counter())
        row = {
            "eng": term["eng"],
            "zhs": term["zhs"],
            "color": colors.most_common(1)[0][0] if colors else (
                "purple" if term["kinds"] == {"enchantment"} else "gold"
            ),
            "kinds": sorted(term["kinds"]),
            **_usage(term["eng"], term["zhs"], rules),
        }
        measure = measures.get(term["zhs"]) if term["kinds"] & MEASURED_KINDS else None
        if measure:
            word, votes = measure.most_common(1)[0]
            if votes * 2 > sum(measure.values()):
                row["zhs_measure"] = word
        rows.append(row)
    return {"schema": SCHEMA, "host": HOST_VERSION, "terms": rows}


def render(glossary: dict) -> str:
    return json.dumps(glossary, ensure_ascii=False, indent=1) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract", help="write the committed glossary from the game PCK")
    extract.add_argument("--sts2-dir", required=True, help="installed Slay the Spire 2 directory")
    extract.add_argument("--check", action="store_true", help="fail if the committed copy is stale")
    args = parser.parse_args(argv)

    pck = Path(args.sts2_dir) / "SlayTheSpire2.pck"
    try:
        rendered = render(build_glossary(read_localization(pck)))
    except (OSError, GlossaryError, ValueError) as exc:
        print(f"[glossary] FAILED: {exc}", file=sys.stderr)
        return 2
    target = API_ROOT / GLOSSARY_RELATIVE_PATH
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != rendered:
            print(f"[glossary] STALE: {target}", file=sys.stderr)
            return 1
        print(f"[glossary] up to date: {target.name}")
        return 0
    target.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"[glossary] wrote {len(json.loads(rendered)['terms'])} terms -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
