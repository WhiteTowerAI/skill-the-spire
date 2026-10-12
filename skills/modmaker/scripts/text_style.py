#!/usr/bin/env python3
"""Check generated localization against the pinned vanilla STS2 text style.

The localization contract (`localization_contract.py`) proves that both languages carry the
same keys and SmartFormat tokens. This module proves the text will render like the game:

- errors (Build fails): a rich-text tag the host does not render as vanilla does, a tag
  parameter, or unbalanced/mis-nested tags. Each one shows raw markup to the player.
- warnings (Build passes, the author fixes or records why): a vanilla term that is not
  highlighted, a number that is not colored where vanilla colors it, a Card number wrapped
  in a color its `:diff()` formatter already owns, several Card effects on one line, or
  Western punctuation/spacing inside Simplified Chinese text.

The vocabulary comes from `reference/catalogs/text-glossary-sts2-0.107.1.json`, extracted
from the game's own localization, plus the Mod's own Power, keyword, Orb, Enchantment, and
Affliction titles. The house style itself lives in `reference/vanilla-text-style.md`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


GLOSSARY_NAME = "text-glossary-sts2-0.107.1.json"
REQUIRED_LANGUAGES = ("eng", "zhs")

# Every authored tag observed in the pinned vanilla localization. Anything else is an error.
VANILLA_TAGS = frozenset(
    {
        "aqua", "b", "blue", "font_size", "gold", "green", "i", "jitter", "orange",
        "pink", "purple", "rainbow", "red", "shake", "sine", "thinky_dots",
    }
)
# Only `font_size` (Ancient dialogue) and `rainbow` (Event pages) carry parameters in vanilla.
PARAMETER_TAGS = frozenset({"font_size", "rainbow"})
# Godot's literal-bracket escapes: standalone, never closed.
ESCAPE_TAGS = frozenset({"lb", "rb"})
COLOR_TAGS = frozenset({"aqua", "blue", "gold", "green", "orange", "pink", "purple", "red"})
VALUE_COLORS = frozenset({"blue", "green", "red", "gold", "purple"})

# Tags vanilla authors per table. A tag outside its table's set is a warning, not an error.
TABLE_TAGS = {
    "afflictions": {"blue", "gold"},
    # New Ancients keep option text in ancients.json, so it also takes the Event option colors.
    "ancients": {
        "aqua", "b", "blue", "font_size", "gold", "green", "i", "jitter", "orange", "purple",
        "red", "sine", "thinky_dots",
    },
    "card_keywords": {"gold"},
    "cards": {"blue", "gold", "purple"},
    "characters": {"blue", "gold", "green", "jitter", "orange", "pink", "purple", "red", "sine"},
    "enchantments": {"blue", "gold"},
    "encounters": {"gold", "purple", "sine"},
    "events": {"aqua", "b", "blue", "gold", "green", "jitter", "orange", "purple", "rainbow", "red", "sine"},
    "intents": {"blue", "font_size", "gold"},
    "modifiers": {"blue", "gold", "red"},
    "monsters": {"gold", "jitter", "orange", "red", "sine"},
    "orbs": {"blue", "gold"},
    "potions": {"blue", "gold", "green"},
    "powers": {"blue", "gold"},
    "relics": {"blue", "gold", "green", "purple", "red", "shake"},
    "rest_site_ui": {"blue", "gold", "green", "red"},
    "static_hover_tips": {"blue", "gold", "green", "red"},
}
DEFAULT_TABLE_TAGS = {"blue", "gold", "green", "purple", "red"}

# Field kinds by table and key suffix. `card` text keeps numbers on `:diff()`; `value` text
# colors its numbers; `plain` text carries no markup in vanilla.
CARD_FIELDS = {"cards": (".description", ".extraDescription")}
VALUE_FIELDS = {
    "relics": (".description", ".eventDescription"),
    "potions": (".description",),
    "powers": (".smartDescription", ".remoteDescription"),
    "enchantments": (".description",),
    "afflictions": (".description",),
    "modifiers": (".description",),
    "orbs": (".smartDescription",),
    "events": ("options.*.description",),
    "ancients": ("options.*.description",),
}
# Placeholders that render a name or an icon rather than a number.
NAME_PLACEHOLDERS = frozenset(
    {"Card", "Character", "Enchantment", "Encounter", "Event", "Name", "Potion", "Relic",
     "character", "encounter", "event"}
)
# Dialogue keeps the speaker's voice (ellipses, stammers); punctuation checks skip it.
DIALOGUE_TABLES = frozenset({"ancients"})
DIALOGUE_KEY_RE = re.compile(
    r"\.(talk|banter|dialogue|speakLine\d*|goldMonologue|eventDeathPrevention|aromaPrinciple)\b"
)
TERM_FIELDS = {
    **{table: suffixes for table, suffixes in CARD_FIELDS.items()},
    **VALUE_FIELDS,
    "powers": (".description", ".smartDescription", ".remoteDescription"),
    "card_keywords": (".description",),
    "static_hover_tips": (".description",),
    "rest_site_ui": (".description",),
}
PLAIN_FIELDS = (".title", ".name")

TAG_RE = re.compile(r"\[(/?)([a-z_]+)((?:=| )[^\]]*)?\]")
BRACE_RE = re.compile(r"\{(?:[^{}]|\{[^{}]*\})*\}")
NUMERIC_FORMATTERS = {"", "diff", "abs", "percentMore", "percentLess", "inverseDiff"}
CJK = "㐀-鿿＀-￯　-〿"
ZHS_WESTERN_PUNCT_RE = re.compile(rf"(?<=[{CJK}])[,.;:!?](?!\d)|[,.;:!?](?=[{CJK}])|(?<=[{CJK}])\.$")
ZHS_SPACE_RE = re.compile(rf"(?<=[{CJK}\]}}])[ \t]+(?=[{CJK}\[{{\d])|(?<=[{CJK}])[ \t]+(?=[\]}}\d])")
CARD_SAME_LINE_RE = re.compile(r"[.!?](?:\[/[a-z]+\])?[ \t]+(?=[A-Z\[{])")
ZHS_CARD_SAME_LINE_RE = re.compile(r"。(?:\[/[a-z]+\])?(?=[^\n\]}\0])")
BARE_LITERAL_RE = re.compile(r"(?<![\w{.%])\d+(?:%|\.\d+)?(?![\w}])")


class TextStyleError(ValueError):
    """Generated localization contains markup the host cannot render as authored."""


@dataclass(frozen=True)
class Term:
    eng: str
    zhs: str
    color: str
    languages: frozenset[str] = frozenset(REQUIRED_LANGUAGES)


# A vanilla term is enforced in a language only when vanilla highlights it consistently there:
# Block is always gold, while Attack and Max HP are usually plain.
MIN_COLORED_USES = 3
MIN_HIGHLIGHT_RATE = 0.8


def api_root() -> Path:
    """Resolve sts2api in the repository or in the published payload layout."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "skills" / "sts2api", here.parents[1] / "sts2api"):
        if (candidate / "reference").is_dir():
            return candidate
    raise TextStyleError("cannot locate the shipped sts2api root")


def load_vanilla_terms() -> list[Term]:
    path = api_root() / "reference" / "catalogs" / GLOSSARY_NAME
    if not path.is_file():
        raise TextStyleError(f"cannot locate the shipped {GLOSSARY_NAME}")
    terms: list[Term] = []
    for row in json.loads(path.read_text(encoding="utf-8"))["terms"]:
        languages = {
            language
            for language in REQUIRED_LANGUAGES
            if row[f"{language}_colored"] >= MIN_COLORED_USES
            and row[f"{language}_colored"]
            >= MIN_HIGHLIGHT_RATE * (row[f"{language}_colored"] + row[f"{language}_plain"])
        }
        if languages:
            terms.append(Term(row["eng"], row["zhs"], row["color"], frozenset(languages)))
    return terms


def _field_matches(key: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        if pattern.startswith("options."):
            if re.search(r"\.options\.[^.]+\.description$", key):
                return True
        elif key.endswith(pattern):
            return True
    return False


def _strip_braces(text: str) -> str:
    """Replace SmartFormat regions with same-length filler so offsets stay comparable."""
    return BRACE_RE.sub(lambda m: "\0" * len(m.group(0)), text)


def check_markup(text: str) -> list[str]:
    """Return errors for tags the host would render as raw or unintended markup."""
    errors: list[str] = []
    for match in TAG_RE.finditer(text):
        name, parameter = match.group(2), match.group(3)
        if name in ESCAPE_TAGS:
            continue
        if name not in VANILLA_TAGS:
            errors.append(f"unsupported tag [{match.group(1)}{name}]")
        elif parameter and name not in PARAMETER_TAGS:
            errors.append(f"tag parameter in [{name}{parameter}] (use a named color tag)")
    if any(TAG_RE.search(region) for region in BRACE_RE.findall(text)):
        return errors  # tags inside plural/conditional branches balance per branch, as vanilla does
    outside = _strip_braces(text)
    stack: list[str] = []
    for match in TAG_RE.finditer(outside):
        closing, name = match.group(1), match.group(2)
        if name in ESCAPE_TAGS:
            continue
        if not closing:
            stack.append(name)
        elif not stack or stack[-1] != name:
            errors.append(f"unbalanced or mis-nested [/{name}]")
            return errors
        else:
            stack.pop()
    if stack:
        errors.append(f"unclosed [{stack[-1]}]")
    return errors


def _colored_mask(text: str, colors: frozenset[str]) -> list[bool]:
    """True for every character inside one of `colors`."""
    mask = [False] * len(text)
    stack: list[tuple[str, int]] = []
    for match in TAG_RE.finditer(text):
        closing, name = match.group(1), match.group(2)
        if not closing:
            stack.append((name, match.end()))
            continue
        for index in range(len(stack) - 1, -1, -1):
            if stack[index][0] == name:
                opened, start = stack.pop(index)
                if opened in colors:
                    for position in range(start, match.start()):
                        mask[position] = True
                break
    return mask


def _uncolored_term_hits(text: str, term: str, language: str) -> bool:
    mask = _colored_mask(text, COLOR_TAGS)
    braces = _strip_braces(text)
    if language == "eng":
        pattern = re.compile(rf"(?<![\w\[/]){re.escape(term)}(?![\w\]])")
    else:
        pattern = re.compile(re.escape(term))
    for match in pattern.finditer(braces):
        if not any(mask[match.start():match.end()]):
            return True
    return False


def _placeholder_warnings(text: str, card: bool) -> list[str]:
    warnings: list[str] = []
    mask = _colored_mask(text, VALUE_COLORS)
    for match in BRACE_RE.finditer(text):
        body = match.group(0)[1:-1]
        name, _, formatter = body.partition(":")
        formatter = formatter.split("(", 1)[0]
        if not re.fullmatch(r"\w+", name) or formatter not in NUMERIC_FORMATTERS:
            continue
        if name in NAME_PLACEHOLDERS or name.endswith(("Icon", "Icons")):
            continue
        colored = any(mask[match.start():match.end()])
        if card and formatter == "diff" and colored:
            warnings.append(f"{{{body}}} is colored; Card `:diff()` already owns green/red")
        elif not card and not colored:
            warnings.append(f"{{{body}}} is uncolored; vanilla wraps displayed numbers in [blue]")
    if not card:
        braces = _strip_braces(text)
        tagless = TAG_RE.sub(lambda m: " " * len(m.group(0)), braces)
        for match in BARE_LITERAL_RE.finditer(tagless):
            if not any(mask[match.start():match.end()]):
                warnings.append(f"literal {match.group(0)} is uncolored; vanilla wraps it in [blue]")
                break
    return warnings


def check_value(
    table: str,
    key: str,
    text: str,
    language: str,
    terms: list[Term],
    own_titles: dict[str, set[str]],
) -> list[str]:
    """Return style warnings for one localized value."""
    warnings: list[str] = []
    used = {match.group(2) for match in TAG_RE.finditer(text)}
    allowed = TABLE_TAGS.get(table, DEFAULT_TABLE_TAGS)
    for name in sorted(used - allowed):
        if name in VANILLA_TAGS:
            warnings.append(f"[{name}] is not used in vanilla {table} text")
    if key.endswith(PLAIN_FIELDS) and used:
        warnings.append("titles and names stay plain in vanilla")

    if table == "powers" and key.endswith(".description") and "{Amount" in text:
        warnings.append(
            "Power .description shows the canonical amount (usually 0) in Card/Relic tooltips; "
            "state the general rule and keep {Amount} in .smartDescription"
        )

    is_card = _field_matches(key, CARD_FIELDS.get(table, ()))
    is_value = _field_matches(key, VALUE_FIELDS.get(table, ()))
    if is_card or is_value:
        warnings.extend(_placeholder_warnings(text, card=is_card))
    if is_card:
        same_line = CARD_SAME_LINE_RE if language == "eng" else ZHS_CARD_SAME_LINE_RE
        if same_line.search(_strip_braces(text)):
            warnings.append("several Card sentences share one line; vanilla starts each with \\n")

    if _field_matches(key, TERM_FIELDS.get(table, ())):
        stem = key.rsplit(".", 1)[0]
        for term in terms:
            word = term.eng if language == "eng" else term.zhs
            if language not in term.languages or not word or word in own_titles.get(stem, ()):
                continue
            if _uncolored_term_hits(text, word, language):
                warnings.append(f"term {word!r} is not highlighted; vanilla uses [{term.color}]")

    if language == "zhs" and table not in DIALOGUE_TABLES and not DIALOGUE_KEY_RE.search(key):
        braces = _strip_braces(text).replace("...", "…")
        if ZHS_WESTERN_PUNCT_RE.search(braces):
            warnings.append("Western punctuation in Chinese text; vanilla uses ，。：；！？")
        if ZHS_SPACE_RE.search(TAG_RE.sub("", braces).replace("\0", "0")):
            warnings.append("space inside Chinese text; vanilla writes 获得[blue]5[/blue]点 without spaces")
    return warnings


def _mod_terms(tables: dict[tuple[str, str], dict[str, str]]) -> tuple[list[Term], dict[str, set[str]]]:
    """The Mod's own titled vocabulary, plus each entry's own title (never self-highlighted)."""
    terms: list[Term] = []
    own: dict[str, set[str]] = {}
    for table in ("powers", "card_keywords", "orbs", "enchantments", "afflictions"):
        english = tables.get(("eng", table), {})
        chinese = tables.get(("zhs", table), {})
        for key, title in english.items():
            if not key.endswith(".title"):
                continue
            stem = key[: -len(".title")]
            translated = chinese.get(key, "")
            own.setdefault(stem, set()).update({title, translated})
            terms.append(Term(title, translated, "purple" if table == "enchantments" else "gold"))
    for (_, table), values in tables.items():
        for key, title in values.items():
            if key.endswith(".title"):
                own.setdefault(key[: -len(".title")], set()).add(title)
    return terms, own


def validate_project_text_style(project_dir: Path, mod_name: str) -> tuple[str, list[str]]:
    """Fail on broken markup; return (summary, warnings) for vanilla-style drift."""
    root = project_dir / mod_name / "localization"
    tables: dict[tuple[str, str], dict[str, str]] = {}
    for language in REQUIRED_LANGUAGES:
        for path in sorted((root / language).glob("*.json")) if (root / language).is_dir() else []:
            data = json.loads(path.read_text(encoding="utf-8"))
            tables[(language, path.stem)] = {k: v for k, v in data.items() if isinstance(v, str)}
    if not tables:
        return "no localization tables", []

    mod_terms, own_titles = _mod_terms(tables)
    terms = sorted(load_vanilla_terms() + mod_terms, key=lambda term: -len(term.eng))
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    for (language, table), values in sorted(tables.items()):
        for key, text in sorted(values.items()):
            checked += 1
            label = f"{language}/{table}.json {key}"
            errors.extend(f"{label}: {problem}" for problem in check_markup(text))
            warnings.extend(
                f"{label}: {problem}"
                for problem in check_value(table, key, text, language, terms, own_titles)
            )
    if errors:
        raise TextStyleError("; ".join(errors))
    return f"values={checked} warnings={len(warnings)}", warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check generated localization against vanilla style")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--mod-name", required=True)
    args = parser.parse_args(argv)
    # Warnings quote Chinese text; a legacy console code page must not crash the report.
    sys.stdout.reconfigure(errors="backslashreplace")
    try:
        summary, warnings = validate_project_text_style(Path(args.project_dir), args.mod_name)
    except (OSError, ValueError) as exc:
        print(f"text style FAILED: {exc}", file=sys.stderr)
        return 2
    for warning in warnings:
        print(f"text style WARNING: {warning}")
    print(f"text style OK: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
