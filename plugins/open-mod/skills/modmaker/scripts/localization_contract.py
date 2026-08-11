#!/usr/bin/env python3
"""Validate bilingual localization resources for a generated STS2 Mod."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_LANGUAGES = ("eng", "zhs")
SMART_FORMAT_RE = re.compile(r"\{[^{}\r\n]+\}")


class LocalizationContractError(ValueError):
    """A generated localization tree violates the bilingual contract."""


def _load_table(path: Path) -> dict[str, str]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LocalizationContractError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LocalizationContractError(f"{path}: localization root must be an object")

    table: dict[str, str] = {}
    invalid_keys: list[str] = []
    invalid_values: list[str] = []
    for key, text in value.items():
        if not isinstance(key, str) or not key.strip():
            invalid_keys.append(repr(key))
            continue
        if not isinstance(text, str) or not text.strip():
            invalid_values.append(key)
            continue
        table[key] = text
    if invalid_keys:
        raise LocalizationContractError(
            f"{path}: localization keys must be non-empty strings: "
            + ", ".join(invalid_keys)
        )
    if invalid_values:
        raise LocalizationContractError(
            f"{path}: localization values must be non-empty strings: "
            + ", ".join(sorted(invalid_values))
        )
    return table


def _language_tables(localization_root: Path) -> dict[str, dict[str, Path]]:
    languages: dict[str, dict[str, Path]] = {}
    if not localization_root.is_dir():
        return languages
    for directory in sorted(path for path in localization_root.iterdir() if path.is_dir()):
        tables = {
            path.name: path
            for path in sorted(directory.glob("*.json"))
            if path.is_file()
        }
        if tables:
            languages[directory.name] = tables
    return languages


def _smart_format_tokens(value: str) -> Counter[str]:
    return Counter(SMART_FORMAT_RE.findall(value))


def validate_project_localization(project_dir: Path, mod_name: str) -> str:
    """Require eng/zhs parity whenever the generated Mod ships localization."""
    localization_root = project_dir / mod_name / "localization"
    languages = _language_tables(localization_root)
    if not languages:
        return "no localization tables"

    missing_languages = [
        language for language in REQUIRED_LANGUAGES if language not in languages
    ]
    if missing_languages:
        raise LocalizationContractError(
            "generated localization requires English and Simplified Chinese; missing "
            + ", ".join(missing_languages)
        )

    reference_language = REQUIRED_LANGUAGES[0]
    reference_tables = set(languages[reference_language])
    loaded: dict[tuple[str, str], dict[str, str]] = {}
    total_keys = 0
    for language, tables in languages.items():
        table_names = set(tables)
        if table_names != reference_tables:
            missing = sorted(reference_tables - table_names)
            extra = sorted(table_names - reference_tables)
            raise LocalizationContractError(
                f"localization tables differ between {reference_language} and {language}; "
                f"missing={missing} extra={extra}"
            )
        for table_name, path in tables.items():
            loaded[(language, table_name)] = _load_table(path)

    for table_name in sorted(reference_tables):
        reference = loaded[(reference_language, table_name)]
        reference_keys = set(reference)
        total_keys += len(reference_keys)
        for language in languages:
            if language == reference_language:
                continue
            translated = loaded[(language, table_name)]
            translated_keys = set(translated)
            if translated_keys != reference_keys:
                missing = sorted(reference_keys - translated_keys)
                extra = sorted(translated_keys - reference_keys)
                raise LocalizationContractError(
                    f"{language}/{table_name}: keys differ from {reference_language}; "
                    f"missing={missing} extra={extra}"
                )
            token_mismatches = sorted(
                key
                for key in reference_keys
                if _smart_format_tokens(translated[key])
                != _smart_format_tokens(reference[key])
            )
            if token_mismatches:
                raise LocalizationContractError(
                    f"{language}/{table_name}: SmartFormat tokens differ from "
                    f"{reference_language}: {', '.join(token_mismatches)}"
                )

    return (
        f"languages={len(languages)} tables={len(reference_tables)} "
        f"keys={total_keys} required={','.join(REQUIRED_LANGUAGES)}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated English and Simplified Chinese localization"
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--mod-name", required=True)
    args = parser.parse_args(argv)
    try:
        summary = validate_project_localization(Path(args.project_dir), args.mod_name)
    except (OSError, LocalizationContractError) as exc:
        print(f"localization FAILED: {exc}", file=sys.stderr)
        return 2
    print(f"localization OK: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
