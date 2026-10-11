from __future__ import annotations

from collections import Counter
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
STS2API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2api"
GRAMMAR_PATH = STS2API_DIR / "design" / "character-foundation.md"
INVENTORY_PATH = (
    STS2API_DIR
    / "design"
    / "catalogs"
    / "character-foundation-sts2-0.107.1.json"
)
VANILLA_CATALOG_PATH = (
    STS2API_DIR
    / "reference"
    / "vanilla-overrides"
    / "catalogs"
    / "sts2-0.107.1.json"
)
RESEARCH_CHARACTERS_PATH = (
    REPO_ROOT / "baselines" / "spire-codex" / "data" / "characters.json"
)


EXPECTED_DECKS = {
    "IRONCLAD": Counter({"StrikeIronclad": 5, "DefendIronclad": 4, "Bash": 1}),
    "SILENT": Counter(
        {"StrikeSilent": 5, "DefendSilent": 5, "Neutralize": 1, "Survivor": 1}
    ),
    "DEFECT": Counter(
        {"StrikeDefect": 4, "DefendDefect": 4, "Zap": 1, "Dualcast": 1}
    ),
    "NECROBINDER": Counter(
        {
            "StrikeNecrobinder": 4,
            "DefendNecrobinder": 4,
            "Bodyguard": 1,
            "Unleash": 1,
        }
    ),
    "REGENT": Counter(
        {"StrikeRegent": 4, "DefendRegent": 4, "FallingStar": 1, "Venerate": 1}
    ),
}


def expanded_inventory_deck(character: dict[str, object]) -> Counter[str]:
    return Counter(
        {
            str(entry["card_type"]): int(entry["count"])
            for entry in character["starting_deck"]
        }
    )


def dynamic_vars(model: dict[str, object], *, upgrade: bool = False) -> dict[str, int]:
    properties = model["properties"]
    values = properties["upgrade_levels"][0]["dynamic_vars"] if upgrade else properties["dynamic_vars"]
    return {str(value["name"]): int(value["base_value"]) for value in values}


class CharacterFoundationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = GRAMMAR_PATH.read_text(encoding="utf-8")
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        cls.catalog = json.loads(VANILLA_CATALOG_PATH.read_text(encoding="utf-8"))

    def test_checked_character_inventory_matches_pinned_identity(self) -> None:
        self.assertEqual("0.107.1", self.inventory["host_version"])
        self.assertEqual(self.catalog["profile"], self.inventory["framework_profile"])
        self.assertEqual(
            self.catalog["assembly"]["sha256"],
            self.inventory["source"]["assembly_sha256"],
        )
        self.assertEqual(
            self.catalog["assembly"]["mvid"],
            self.inventory["source"]["assembly_mvid"],
        )

        inventory = {character["id"]: character for character in self.inventory["characters"]}
        self.assertEqual(set(EXPECTED_DECKS), set(inventory))
        for character_id, expected_deck in EXPECTED_DECKS.items():
            self.assertEqual(expected_deck, expanded_inventory_deck(inventory[character_id]))

    @unittest.skipUnless(
        RESEARCH_CHARACTERS_PATH.is_file(),
        "maintainer-only spire-codex research data is not checked out",
    )
    def test_checked_character_inventory_matches_research(self) -> None:
        inventory = {character["id"]: character for character in self.inventory["characters"]}
        research_characters = json.loads(RESEARCH_CHARACTERS_PATH.read_text(encoding="utf-8"))
        research = {character["id"]: character for character in research_characters}
        for character_id, expected_deck in EXPECTED_DECKS.items():
            self.assertEqual(expected_deck, Counter(research[character_id]["starting_deck"]))
            self.assertEqual(inventory[character_id]["starting_hp"], research[character_id]["starting_hp"])
            self.assertEqual(inventory[character_id]["starting_gold"], research[character_id]["starting_gold"])
            self.assertEqual(
                inventory[character_id]["starting_relic"],
                research[character_id]["starting_relics"][0],
            )

    def test_prose_starter_table_is_derived_from_the_checked_inventory(self) -> None:
        """The prose starter table must remain a view of the checked inventory."""
        for character in self.inventory["characters"]:
            identifier = str(character["id"])
            rows = [
                line
                for line in self.grammar.splitlines()
                if line.startswith(f"| {identifier.capitalize()} ")
            ]
            with self.subTest(character=identifier):
                self.assertEqual(
                    1, len(rows), f"{identifier} needs exactly one starter-table row"
                )
                row = rows[0]
                for entry in character["starting_deck"]:
                    self.assertIn(
                        f"{entry['count']} `{entry['card_type']}`",
                        row,
                        f"{identifier} row must state the inventory's exact deck entry",
                    )
                total = sum(int(entry["count"]) for entry in character["starting_deck"])
                self.assertIn(
                    f"| {total} |",
                    row,
                    f"{identifier} row total must equal its inventory deck size",
                )
                self.assertIn(
                    f"| {character['starting_hp']} |",
                    row,
                    f"{identifier} row must state the inventory's starting HP",
                )
                self.assertIn(
                    f"`{character['starting_relic']}`",
                    row,
                    f"{identifier} row must name the inventory's Starter relic",
                )

    def test_grammar_states_native_hp_range_and_gold_constant(self) -> None:
        hp_values = [int(c["starting_hp"]) for c in self.inventory["characters"]]
        gold_values = {int(c["starting_gold"]) for c in self.inventory["characters"]}
        self.assertEqual(1, len(gold_values), "this case assumes Gold is a native constant")

        self.assertIn(f"`{min(hp_values)}` to `{max(hp_values)}`", self.grammar)
        self.assertIn(f"{gold_values.pop()} Gold", self.grammar)

    def test_all_character_strike_and_defend_facts_match_the_pinned_catalog(self) -> None:
        models = {model["id"]: model for model in self.catalog["models"]}
        stems = ("IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT")
        for stem in stems:
            strike = models[f"CARD.STRIKE_{stem}"]
            defend = models[f"CARD.DEFEND_{stem}"]

            self.assertEqual("Strike", strike["title_localization"]["localized_titles"]["eng"])
            self.assertEqual("打击", strike["title_localization"]["localized_titles"]["zhs"])
            self.assertEqual("Basic", strike["properties"]["rarity"])
            self.assertEqual(1, strike["properties"]["energy_cost"])
            self.assertEqual(["Strike"], strike["properties"]["tags"])
            self.assertEqual(6, dynamic_vars(strike)["Damage"])
            self.assertEqual(9, dynamic_vars(strike, upgrade=True)["Damage"])

            self.assertEqual("Defend", defend["title_localization"]["localized_titles"]["eng"])
            self.assertEqual("防御", defend["title_localization"]["localized_titles"]["zhs"])
            self.assertEqual("Basic", defend["properties"]["rarity"])
            self.assertEqual(1, defend["properties"]["energy_cost"])
            self.assertEqual(["Defend"], defend["properties"]["tags"])
            self.assertEqual(5, dynamic_vars(defend)["Block"])
            self.assertEqual(8, dynamic_vars(defend, upgrade=True)["Block"])

        for fact in (
            "Strike: 1 Energy, `6 -> 9` damage, `CardTag.Strike`",
            "Defend: 1 Energy, `5 -> 8` Block, `CardTag.Defend`",
            "`Strike` / `Defend` in English and `打击` / `防御`",
        ):
            self.assertIn(fact, self.grammar)


if __name__ == "__main__":
    unittest.main()
