from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from ancient_dialogue import (  # noqa: E402
    AncientDialogueValidationError,
    parse_ancient_dialogue_table,
    resolve_ancient_target,
    validate_project_ancient_dialogue,
)


CHARACTER = "PROOF_CHARACTER_WAYFINDER"


def complete_table() -> dict[str, str]:
    return {
        f"DARV.talk.{CHARACTER}.0-0.char": "I know what I seek.",
        f"DARV.talk.{CHARACTER}.0-0.next": "Listen",
        f"DARV.talk.{CHARACTER}.0-1.ancient": "Then choose carefully.",
        f"DARV.talk.{CHARACTER}.0-visit": "0",
        f"DARV.talk.{CHARACTER}.1-0r.ancient": "Back again?",
        f"DARV.talk.{CHARACTER}.1-0r.next": "Always",
        f"DARV.talk.{CHARACTER}.1-1r.char": "The path changed.",
        f"DARV.talk.{CHARACTER}.1-visit": "1",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-0.char": "The path ends here.",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-0.next": "Face the end",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-1.ancient": "Show me.",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-visit": "0",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-startattack": "None",
        f"THE_ARCHITECT.talk.{CHARACTER}.0-endattack": "Both",
        f"THE_ARCHITECT.talk.{CHARACTER}.1-0r.ancient": "Again.",
        f"THE_ARCHITECT.talk.{CHARACTER}.1-visit": "1",
        f"THE_ARCHITECT.talk.{CHARACTER}.1-startattack": "Player",
        f"THE_ARCHITECT.talk.{CHARACTER}.1-endattack": "Architect",
    }


class AncientDialogueTests(unittest.TestCase):
    def test_catalog_resolves_ids_names_spacing_and_localized_aliases(self) -> None:
        expected = {
            "darv": "DARV",
            "THE_ARCHITECT": "THE_ARCHITECT",
            "the-architect": "THE_ARCHITECT",
            "Tez Catara": "TEZCATARA",
            "\u6d85\u5965": "NEOW",
        }
        for alias, entry in expected.items():
            with self.subTest(alias=alias):
                self.assertEqual(entry, resolve_ancient_target(alias).entry)
        with self.assertRaisesRegex(AncientDialogueValidationError, "unknown Ancient"):
            resolve_ancient_target("made up ancient")

    def test_parser_preserves_lines_visits_repeat_and_architect_attackers(self) -> None:
        groups = parse_ancient_dialogue_table(complete_table(), {CHARACTER})
        self.assertEqual(4, len(groups))

        darv_first, darv_repeat, architect_first, architect_repeat = groups
        self.assertEqual(("Character", "Ancient"), tuple(line.speaker for line in darv_first.lines))
        self.assertEqual("Listen", darv_first.lines[0].next_prompt)
        self.assertIsNone(darv_first.lines[1].next_prompt)
        self.assertEqual(0, darv_first.visit_index)
        self.assertFalse(darv_first.is_repeating)
        self.assertEqual(1, darv_repeat.visit_index)
        self.assertTrue(darv_repeat.is_repeating)
        self.assertEqual(("None", "Both"), (architect_first.start_attackers, architect_first.end_attackers))
        self.assertEqual(("Player", "Architect"), (architect_repeat.start_attackers, architect_repeat.end_attackers))

    def test_existing_foundation_architect_shape_remains_valid(self) -> None:
        table = {
            f"THE_ARCHITECT.talk.{CHARACTER}.0-0r.char": "Still standing.",
            f"THE_ARCHITECT.talk.{CHARACTER}.0-0r.next": "Continue",
            f"THE_ARCHITECT.talk.{CHARACTER}.0-1r.ancient": "For now.",
            f"THE_ARCHITECT.talk.{CHARACTER}.0-attack": "Both",
        }
        group = parse_ancient_dialogue_table(table, {CHARACTER})[0]
        self.assertEqual(0, group.visit_index)
        self.assertTrue(group.is_repeating)
        self.assertEqual("Both", group.end_attackers)

    def test_vanilla_ancient_rich_text_subset_is_validated(self) -> None:
        table = complete_table()
        table[f"DARV.talk.{CHARACTER}.0-0.char"] = (
            "[i][font_size=22]A thought[/font_size][/i] and [sine]a warning[/sine]."
        )
        parse_ancient_dialogue_table(table, {CHARACTER})
        table[f"DARV.talk.{CHARACTER}.0-0.char"] = "[gold]No[/gold]"
        with self.assertRaisesRegex(AncientDialogueValidationError, "unsupported rich-text"):
            parse_ancient_dialogue_table(table, {CHARACTER})

    def test_structural_failures_are_rejected(self) -> None:
        mutations = {
            "unknown target": lambda table: table.__setitem__(
                f"UNKNOWN.talk.{CHARACTER}.0-0.char", table.pop(f"DARV.talk.{CHARACTER}.0-0.char")
            ),
            "dialogue gap": lambda table: table.update(
                {
                    key.replace(f"DARV.talk.{CHARACTER}.1-", f"DARV.talk.{CHARACTER}.2-"): table.pop(key)
                    for key in list(table)
                    if key.startswith(f"DARV.talk.{CHARACTER}.1-")
                }
            ),
            "two speakers": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.0-0.ancient", "No"
            ),
            "mixed repeat": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.1-1.char",
                table.pop(f"DARV.talk.{CHARACTER}.1-1r.char"),
            ),
            "missing next": lambda table: table.pop(f"DARV.talk.{CHARACTER}.0-0.next"),
            "terminal next": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.0-1.next", "Extra"
            ),
            "bad visit": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.0-visit", "-1"
            ),
            "non architect attacker": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.0-startattack", "Player"
            ),
            "bad attacker": lambda table: table.__setitem__(
                f"THE_ARCHITECT.talk.{CHARACTER}.0-endattack", "Everyone"
            ),
            "line sfx": lambda table: table.__setitem__(
                f"DARV.talk.{CHARACTER}.0-0.char.sfx", "event:/not-supported"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                table = complete_table()
                mutate(table)
                with self.assertRaises(AncientDialogueValidationError):
                    parse_ancient_dialogue_table(table, {CHARACTER})

    def test_architect_requires_zero_to_repeat_coverage(self) -> None:
        table = complete_table()
        table[f"THE_ARCHITECT.talk.{CHARACTER}.1-visit"] = "2"
        with self.assertRaisesRegex(AncientDialogueValidationError, "uncovered win indexes"):
            parse_ancient_dialogue_table(table, {CHARACTER})

        table = complete_table()
        table[f"THE_ARCHITECT.talk.{CHARACTER}.1-0.ancient"] = table.pop(
            f"THE_ARCHITECT.talk.{CHARACTER}.1-0r.ancient"
        )
        with self.assertRaisesRegex(AncientDialogueValidationError, "repeating dialogue"):
            parse_ancient_dialogue_table(table, {CHARACTER})

        with self.assertRaisesRegex(AncientDialogueValidationError, "complete production"):
            parse_ancient_dialogue_table(
                complete_table(),
                {CHARACTER, "PROOF_CHARACTER_SECOND"},
            )

    def test_project_validation_requires_character_and_language_key_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for language in ("eng", "zhs"):
                localization = root / "Proof" / "localization" / language
                localization.mkdir(parents=True)
                (localization / "characters.json").write_text(
                    json.dumps({f"{CHARACTER}.title": "Wayfinder"}), encoding="utf-8"
                )
                (localization / "ancients.json").write_text(
                    json.dumps(complete_table()), encoding="utf-8"
                )
            summary = validate_project_ancient_dialogue(root, "Proof")
            self.assertIn("2 language(s)", summary)
            self.assertIn("4 dialogue group(s)", summary)

            zhs = root / "Proof" / "localization" / "zhs" / "ancients.json"
            table = complete_table()
            table.pop(f"DARV.talk.{CHARACTER}.0-0.next")
            zhs.write_text(json.dumps(table), encoding="utf-8")
            with self.assertRaisesRegex(AncientDialogueValidationError, "structural keys differ"):
                validate_project_ancient_dialogue(root, "Proof")

    def test_project_without_ancient_table_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                "no ancients.json",
                validate_project_ancient_dialogue(Path(tmp), "NoDialogue"),
            )

    def test_project_character_requires_ancients_in_each_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for language in ("eng", "zhs"):
                localization = root / "Proof" / "localization" / language
                localization.mkdir(parents=True)
                (localization / "characters.json").write_text(
                    json.dumps({f"{CHARACTER}.title": "Wayfinder"}),
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(
                AncientDialogueValidationError,
                "complete production Architect dialogue",
            ):
                validate_project_ancient_dialogue(root, "Proof")

            eng = root / "Proof" / "localization" / "eng" / "ancients.json"
            eng.write_text(json.dumps(complete_table()), encoding="utf-8")
            with self.assertRaisesRegex(
                AncientDialogueValidationError,
                "ancients.json is required.*zhs",
            ):
                validate_project_ancient_dialogue(root, "Proof")


if __name__ == "__main__":
    unittest.main()
