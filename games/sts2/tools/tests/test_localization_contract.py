from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from localization_contract import (  # noqa: E402
    LocalizationContractError,
    validate_project_localization,
)


class LocalizationContractTests(unittest.TestCase):
    def write_table(
        self, root: Path, language: str, name: str, values: dict[str, str]
    ) -> None:
        directory = root / "Proof" / "localization" / language
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(json.dumps(values), encoding="utf-8")

    def test_project_without_localization_is_language_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                "no localization tables",
                validate_project_localization(Path(tmp), "Proof"),
            )

    def test_bilingual_tables_keys_and_tokens_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(
                root,
                "eng",
                "cards.json",
                {"PROOF_CARD.title": "Strike", "PROOF_CARD.description": "Deal {Damage:diff()} damage."},
            )
            self.write_table(
                root,
                "zhs",
                "cards.json",
                {"PROOF_CARD.title": "打击", "PROOF_CARD.description": "造成 {Damage:diff()} 点伤害。"},
            )
            summary = validate_project_localization(root, "Proof")
            self.assertIn("required=eng,zhs", summary)
            self.assertIn("tables=1", summary)

    def test_missing_required_language_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(root, "eng", "cards.json", {"PROOF_CARD.title": "Strike"})
            with self.assertRaisesRegex(LocalizationContractError, "missing zhs"):
                validate_project_localization(root, "Proof")

    def test_table_and_key_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(root, "eng", "cards.json", {"PROOF_CARD.title": "Strike"})
            self.write_table(root, "zhs", "relics.json", {"PROOF_RELIC.title": "遗物"})
            with self.assertRaisesRegex(LocalizationContractError, "tables differ"):
                validate_project_localization(root, "Proof")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(root, "eng", "cards.json", {"PROOF_CARD.title": "Strike"})
            self.write_table(root, "zhs", "cards.json", {"PROOF_CARD.description": "说明"})
            with self.assertRaisesRegex(LocalizationContractError, "keys differ"):
                validate_project_localization(root, "Proof")

    def test_empty_value_and_token_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(root, "eng", "cards.json", {"PROOF_CARD.title": "Strike"})
            self.write_table(root, "zhs", "cards.json", {"PROOF_CARD.title": " "})
            with self.assertRaisesRegex(LocalizationContractError, "non-empty strings"):
                validate_project_localization(root, "Proof")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_table(
                root,
                "eng",
                "cards.json",
                {"PROOF_CARD.description": "Deal {Damage:diff()} damage."},
            )
            self.write_table(
                root,
                "zhs",
                "cards.json",
                {"PROOF_CARD.description": "造成 {Damage} 点伤害。"},
            )
            with self.assertRaisesRegex(LocalizationContractError, "SmartFormat tokens differ"):
                validate_project_localization(root, "Proof")


if __name__ == "__main__":
    unittest.main()
