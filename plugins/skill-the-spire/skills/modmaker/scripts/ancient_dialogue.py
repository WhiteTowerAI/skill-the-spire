#!/usr/bin/env python3
"""Validate generated custom-Character dialogue for vanilla STS2 Ancients."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from localization_contract import REQUIRED_LANGUAGES


class AncientDialogueValidationError(ValueError):
    """A generated Ancient localization table violates the pinned contract."""


@dataclass(frozen=True)
class AncientTarget:
    entry: str
    name: str
    aliases: tuple[str, ...]
    availability: str
    console_entry: bool


VANILLA_ANCIENTS = (
    AncientTarget("DARV", "Darv", ("the hoarder", "\u8fbe\u5f17"), "shared", True),
    AncientTarget("NEOW", "Neow", ("\u6d85\u5965",), "act 1", True),
    AncientTarget("OROBAS", "Orobas", ("\u6b27\u6d1b\u5df4\u65af",), "act 2", True),
    AncientTarget("PAEL", "Pael", ("\u4f69\u5c14",), "act 2", True),
    AncientTarget(
        "TEZCATARA",
        "Tezcatara",
        ("\u7279\u5179\u5361\u5854\u62c9",),
        "act 2",
        True,
    ),
    AncientTarget(
        "NONUPEIPE",
        "Nonupeipe",
        ("\u8bfa\u5974\u4f69\u666e",),
        "act 3",
        True,
    ),
    AncientTarget("TANX", "Tanx", ("\u5766\u514b\u65af",), "act 3", True),
    AncientTarget("VAKUU", "Vakuu", ("\u74e6\u5e93",), "act 3", True),
    AncientTarget(
        "THE_ARCHITECT",
        "The Architect",
        ("architect", "\u5efa\u7b51\u5e08"),
        "finale",
        False,
    ),
)

TARGET_BY_ENTRY = {target.entry: target for target in VANILLA_ANCIENTS}
CHARACTER_ENTRY_RE = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*_CHARACTER_[A-Z0-9_]+$")
LINE_KEY_RE = re.compile(
    r"^(?P<dialogue>\d+)-(?P<line>\d+)(?P<repeat>r)?\."
    r"(?P<kind>ancient|char|next)$"
)
METADATA_KEY_RE = re.compile(
    r"^(?P<dialogue>\d+)-(?P<kind>visit|attack|startattack|endattack)$"
)
MARKUP_RE = re.compile(r"\[([^\]]+)\]")
ALLOWED_OPEN_TAGS = {
    "aqua": "aqua",
    "b": "b",
    "font_size=22": "font_size",
    "i": "i",
    "jitter": "jitter",
    "orange": "orange",
    "red": "red",
    "sine": "sine",
    "thinky_dots": "thinky_dots",
}
ATTACKERS = {"none": "None", "player": "Player", "architect": "Architect", "both": "Both"}


@dataclass(frozen=True)
class DialogueLine:
    speaker: str
    text: str
    next_prompt: str | None


@dataclass(frozen=True)
class DialogueGroup:
    ancient_entry: str
    character_entry: str
    dialogue_index: int
    visit_index: int
    is_repeating: bool
    start_attackers: str
    end_attackers: str
    lines: tuple[DialogueLine, ...]


@dataclass
class _GroupInput:
    line_texts: dict[int, list[tuple[str, bool, str, str]]]
    prompts: dict[int, list[tuple[bool, str, str]]]
    metadata: dict[str, tuple[str, str]]

    @classmethod
    def create(cls) -> "_GroupInput":
        return cls({}, {}, {})


def _normalize_alias(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def resolve_ancient_target(name: str) -> AncientTarget:
    needle = _normalize_alias(name)
    if not needle:
        raise AncientDialogueValidationError("Ancient target name is empty")
    matches = []
    for target in VANILLA_ANCIENTS:
        names = (target.entry, target.name, *target.aliases)
        if needle in {_normalize_alias(candidate) for candidate in names}:
            matches.append(target)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        entries = ", ".join(target.entry for target in matches)
        raise AncientDialogueValidationError(
            f"Ancient target {name!r} is ambiguous: {entries}"
        )
    supported = ", ".join(target.name for target in VANILLA_ANCIENTS)
    raise AncientDialogueValidationError(
        f"unknown Ancient target {name!r}; supported targets: {supported}"
    )


def _validate_rich_text(value: str, key: str) -> None:
    stack: list[str] = []
    for match in MARKUP_RE.finditer(value):
        token = match.group(1)
        if token.startswith("/"):
            closing = token[1:]
            if not stack or stack[-1] != closing:
                raise AncientDialogueValidationError(
                    f"{key}: rich-text tags must be balanced and reverse-nested"
                )
            stack.pop()
            continue
        closing = ALLOWED_OPEN_TAGS.get(token)
        if closing is None:
            allowed = ", ".join(f"[{tag}]" for tag in sorted(ALLOWED_OPEN_TAGS))
            raise AncientDialogueValidationError(
                f"{key}: unsupported rich-text tag [{token}]; allowed: {allowed}"
            )
        stack.append(closing)
    if stack:
        raise AncientDialogueValidationError(f"{key}: unclosed rich-text tag [{stack[-1]}]")


def _nonempty_string(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AncientDialogueValidationError(f"{key}: value must be a non-empty string")
    return value


def _parse_attacker(value: str, key: str) -> str:
    parsed = ATTACKERS.get(value.casefold())
    if parsed is None:
        raise AncientDialogueValidationError(
            f"{key}: attacker must be one of None, Player, Architect, Both"
        )
    return parsed


def _default_visit(dialogue_index: int, previous_visit: int) -> int:
    if dialogue_index == 0:
        return 0
    if dialogue_index == 1:
        return 1
    if dialogue_index == 2:
        return 4
    return previous_visit + 3


def _parse_group(
    ancient_entry: str,
    character_entry: str,
    dialogue_index: int,
    source: _GroupInput,
    previous_visit: int,
) -> DialogueGroup:
    prefix = f"{ancient_entry}.talk.{character_entry}.{dialogue_index}"
    line_indexes = sorted(source.line_texts)
    if line_indexes != list(range(len(line_indexes))) or not line_indexes:
        raise AncientDialogueValidationError(
            f"{prefix}: line indexes must begin at 0 and be contiguous"
        )

    repeat_modes: set[bool] = set()
    lines: list[DialogueLine] = []
    last_line = line_indexes[-1]
    for line_index in line_indexes:
        candidates = source.line_texts[line_index]
        if len(candidates) != 1:
            raise AncientDialogueValidationError(
                f"{prefix}-{line_index}: exactly one .ancient or .char speaker key is required"
            )
        speaker, repeating, text, text_key = candidates[0]
        repeat_modes.add(repeating)
        _validate_rich_text(text, text_key)

        prompts = source.prompts.get(line_index, [])
        if line_index < last_line:
            if len(prompts) != 1:
                raise AncientDialogueValidationError(
                    f"{prefix}-{line_index}: every non-terminal line requires exactly one .next"
                )
            prompt_repeating, prompt, prompt_key = prompts[0]
            repeat_modes.add(prompt_repeating)
            if MARKUP_RE.search(prompt):
                raise AncientDialogueValidationError(
                    f"{prompt_key}: transition prompts must be plain text"
                )
            next_prompt = prompt
        else:
            if prompts:
                raise AncientDialogueValidationError(
                    f"{prefix}-{line_index}: terminal line must not have a .next key"
                )
            next_prompt = None
        lines.append(DialogueLine(speaker, text, next_prompt))

    orphan_prompts = sorted(set(source.prompts) - set(line_indexes))
    if orphan_prompts:
        raise AncientDialogueValidationError(
            f"{prefix}: orphan .next line indexes: {orphan_prompts}"
        )
    if len(repeat_modes) != 1:
        raise AncientDialogueValidationError(
            f"{prefix}: every line and .next key must use one consistent repeat mode"
        )

    metadata = source.metadata
    if "visit" in metadata:
        visit_key, visit_text = metadata["visit"]
        try:
            visit_index = int(visit_text)
        except ValueError as exc:
            raise AncientDialogueValidationError(
                f"{visit_key}: visit index must be a non-negative integer"
            ) from exc
        if visit_index < 0 or str(visit_index) != visit_text.strip():
            raise AncientDialogueValidationError(
                f"{visit_key}: visit index must be a non-negative integer"
            )
    elif ancient_entry == "THE_ARCHITECT":
        visit_index = dialogue_index
    else:
        visit_index = _default_visit(dialogue_index, previous_visit)

    attacker_keys = {"attack", "startattack", "endattack"} & metadata.keys()
    if attacker_keys and ancient_entry != "THE_ARCHITECT":
        raise AncientDialogueValidationError(
            f"{prefix}: attacker metadata is supported only for THE_ARCHITECT"
        )
    start_attackers = "None"
    end_attackers = "Architect" if ancient_entry == "THE_ARCHITECT" else "None"
    if "attack" in metadata and "endattack" in metadata:
        raise AncientDialogueValidationError(
            f"{prefix}: legacy -attack and -endattack must not both be present"
        )
    if "attack" in metadata:
        key, value = metadata["attack"]
        end_attackers = _parse_attacker(value, key)
    if "startattack" in metadata:
        key, value = metadata["startattack"]
        start_attackers = _parse_attacker(value, key)
    if "endattack" in metadata:
        key, value = metadata["endattack"]
        end_attackers = _parse_attacker(value, key)

    return DialogueGroup(
        ancient_entry=ancient_entry,
        character_entry=character_entry,
        dialogue_index=dialogue_index,
        visit_index=visit_index,
        is_repeating=repeat_modes.pop(),
        start_attackers=start_attackers,
        end_attackers=end_attackers,
        lines=tuple(lines),
    )


def parse_ancient_dialogue_table(
    table: dict[str, object],
    character_entries: Iterable[str] | None = None,
) -> tuple[DialogueGroup, ...]:
    allowed_characters = set(character_entries) if character_entries is not None else None
    grouped: dict[tuple[str, str, int], _GroupInput] = {}

    for key, raw_value in table.items():
        value = _nonempty_string(raw_value, key)
        if ".sfx" in key:
            raise AncientDialogueValidationError(
                f"{key}: line-level Ancient dialogue SFX is unsupported"
            )
        if ".talk." not in key:
            raise AncientDialogueValidationError(f"{key}: unsupported ancients.json key")
        ancient_entry, remainder = key.split(".talk.", 1)
        target = TARGET_BY_ENTRY.get(ancient_entry)
        if target is None:
            raise AncientDialogueValidationError(
                f"{key}: target is not in the pinned STS2 0.107.1 Ancient catalog"
            )
        try:
            character_entry, suffix = remainder.split(".", 1)
        except ValueError as exc:
            raise AncientDialogueValidationError(f"{key}: malformed dialogue key") from exc
        if not CHARACTER_ENTRY_RE.fullmatch(character_entry):
            raise AncientDialogueValidationError(
                f"{key}: Character entry must use normalized MOD_CHARACTER_TYPE form"
            )
        if allowed_characters is not None and character_entry not in allowed_characters:
            raise AncientDialogueValidationError(
                f"{key}: Character entry has no matching .title in characters.json"
            )

        line_match = LINE_KEY_RE.fullmatch(suffix)
        metadata_match = METADATA_KEY_RE.fullmatch(suffix)
        if line_match:
            dialogue_index = int(line_match.group("dialogue"))
            line_index = int(line_match.group("line"))
            repeating = line_match.group("repeat") == "r"
            kind = line_match.group("kind")
            group = grouped.setdefault(
                (target.entry, character_entry, dialogue_index), _GroupInput.create()
            )
            if kind == "next":
                group.prompts.setdefault(line_index, []).append((repeating, value, key))
            else:
                group.line_texts.setdefault(line_index, []).append(
                    ("Ancient" if kind == "ancient" else "Character", repeating, value, key)
                )
            continue
        if metadata_match:
            dialogue_index = int(metadata_match.group("dialogue"))
            kind = metadata_match.group("kind")
            group = grouped.setdefault(
                (target.entry, character_entry, dialogue_index), _GroupInput.create()
            )
            if kind in group.metadata:
                raise AncientDialogueValidationError(f"{key}: duplicate metadata")
            group.metadata[kind] = (key, value)
            continue
        raise AncientDialogueValidationError(f"{key}: malformed or unsupported dialogue key")

    pair_indexes: dict[tuple[str, str], list[int]] = {}
    for ancient_entry, character_entry, dialogue_index in grouped:
        pair_indexes.setdefault((ancient_entry, character_entry), []).append(dialogue_index)
    for pair, indexes in pair_indexes.items():
        ordered = sorted(indexes)
        if ordered != list(range(len(ordered))):
            raise AncientDialogueValidationError(
                f"{pair[0]}.talk.{pair[1]}: dialogue indexes must begin at 0 and be contiguous"
            )

    parsed: list[DialogueGroup] = []
    for ancient_entry, character_entry in sorted(pair_indexes):
        previous_visit = 0
        for dialogue_index in sorted(pair_indexes[(ancient_entry, character_entry)]):
            group = _parse_group(
                ancient_entry,
                character_entry,
                dialogue_index,
                grouped[(ancient_entry, character_entry, dialogue_index)],
                previous_visit,
            )
            parsed.append(group)
            previous_visit = group.visit_index

    _validate_architect_coverage(parsed, allowed_characters)
    return tuple(parsed)


def _validate_architect_coverage(
    groups: Iterable[DialogueGroup],
    required_characters: Iterable[str] | None = None,
) -> None:
    by_character: dict[str, list[DialogueGroup]] = {}
    referenced_characters = set(required_characters or ())
    for group in groups:
        referenced_characters.add(group.character_entry)
        if group.ancient_entry == "THE_ARCHITECT":
            by_character.setdefault(group.character_entry, []).append(group)

    for character_entry in sorted(referenced_characters):
        architect_groups = by_character.get(character_entry, [])
        if not architect_groups:
            raise AncientDialogueValidationError(
                f"THE_ARCHITECT.talk.{character_entry}: complete production dialogue is required"
            )
        repeating = [group.visit_index for group in architect_groups if group.is_repeating]
        if not repeating:
            raise AncientDialogueValidationError(
                f"THE_ARCHITECT.talk.{character_entry}: a repeating dialogue is required for later wins"
            )
        repeat_start = min(repeating)
        covered = {group.visit_index for group in architect_groups}
        missing = [visit for visit in range(repeat_start) if visit not in covered]
        if missing:
            raise AncientDialogueValidationError(
                f"THE_ARCHITECT.talk.{character_entry}: uncovered win indexes before repeat: {missing}"
            )


def _load_json_object(path: Path) -> dict[str, object]:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise AncientDialogueValidationError(f"{path}: duplicate JSON key {key}")
            result[key] = value
        return result

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AncientDialogueValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise AncientDialogueValidationError(f"{path}: localization root must be an object")
    return parsed


def _character_entries(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    table = _load_json_object(path)
    entries = {key.removesuffix(".title") for key in table if key.endswith(".title")}
    return {entry for entry in entries if CHARACTER_ENTRY_RE.fullmatch(entry)}


def validate_project_ancient_dialogue(project_dir: Path, mod_name: str) -> str:
    localization_dir = project_dir / mod_name / "localization"
    tables = sorted(localization_dir.glob("*/ancients.json"))
    character_languages = {
        path.parent.name: _character_entries(path)
        for path in sorted(localization_dir.glob("*/characters.json"))
    }
    character_languages = {
        language: entries
        for language, entries in character_languages.items()
        if entries
    }
    if not tables:
        if character_languages:
            languages = ", ".join(sorted(character_languages))
            raise AncientDialogueValidationError(
                "complete production Architect dialogue is required for Character "
                f"localization language(s): {languages}"
            )
        return "no ancients.json"

    table_languages = {path.parent.name for path in tables}
    missing_languages = sorted(set(character_languages) - table_languages)
    if missing_languages:
        raise AncientDialogueValidationError(
            "ancients.json is required for Character localization language(s): "
            + ", ".join(missing_languages)
        )
    missing_character_languages = sorted(table_languages - set(character_languages))
    if missing_character_languages:
        raise AncientDialogueValidationError(
            "characters.json with the custom Character entry is required for Ancient "
            "dialogue language(s): " + ", ".join(missing_character_languages)
        )
    missing_required_languages = sorted(set(REQUIRED_LANGUAGES) - table_languages)
    if missing_required_languages:
        raise AncientDialogueValidationError(
            "custom-Character Ancient dialogue requires English and Simplified Chinese; "
            "missing " + ", ".join(missing_required_languages)
        )

    reference_keys: set[str] | None = None
    reference_language = ""
    all_groups: list[DialogueGroup] = []
    targets: set[str] = set()
    characters: set[str] = set()
    for path in tables:
        table = _load_json_object(path)
        keys = set(table)
        if reference_keys is None:
            reference_keys = keys
            reference_language = path.parent.name
        elif keys != reference_keys:
            missing = sorted(reference_keys - keys)
            extra = sorted(keys - reference_keys)
            raise AncientDialogueValidationError(
                f"{path}: structural keys differ from {reference_language}; "
                f"missing={missing} extra={extra}"
            )
        character_entries = _character_entries(path.with_name("characters.json"))
        groups = parse_ancient_dialogue_table(table, character_entries)
        all_groups.extend(groups)
        targets.update(group.ancient_entry for group in groups)
        characters.update(group.character_entry for group in groups)

    per_language = len(all_groups) // len(tables)
    return (
        f"{len(tables)} language(s), {per_language} dialogue group(s), "
        f"{len(targets)} target(s), {len(characters)} Character(s)"
    )


def _list_targets() -> None:
    for target in VANILLA_ANCIENTS:
        route = "ancient console" if target.console_entry else "finale host"
        print(f"{target.entry:14} {target.name:16} {target.availability:7} {route}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate custom-Character localization for vanilla STS2 Ancients"
    )
    parser.add_argument("--list-targets", action="store_true")
    parser.add_argument("--project-dir")
    parser.add_argument("--mod-name")
    args = parser.parse_args(argv)

    if args.list_targets:
        if args.project_dir or args.mod_name:
            parser.error("--list-targets cannot be combined with project validation")
        _list_targets()
        return 0
    if not args.project_dir or not args.mod_name:
        parser.error("project validation requires --project-dir and --mod-name")
    try:
        summary = validate_project_ancient_dialogue(Path(args.project_dir), args.mod_name)
    except AncientDialogueValidationError as exc:
        print(f"[ancient-dialogue] FAILED: {exc}", file=sys.stderr)
        return 2
    print(f"[ancient-dialogue] OK: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
