from __future__ import annotations

from collections import Counter
import json
import re
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
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
SCENARIOS_PATH = REPO_ROOT / "games" / "sts2" / "tests" / "character-foundation-scenarios.md"


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


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


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
        cls.research_characters = json.loads(
            RESEARCH_CHARACTERS_PATH.read_text(encoding="utf-8")
        )
        cls.api_skill = (STS2API_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.modmaker_skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.spec = skill_prose.stage("spec")
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")

    def test_checked_character_inventory_matches_pinned_identity_and_research(self) -> None:
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
        research = {character["id"]: character for character in self.research_characters}
        self.assertEqual(set(EXPECTED_DECKS), set(inventory))
        for character_id, expected_deck in EXPECTED_DECKS.items():
            self.assertEqual(expected_deck, expanded_inventory_deck(inventory[character_id]))
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

    def test_grammar_states_native_hp_range_gold_constant_and_relic_effect_limit(self) -> None:
        """Expose the native HP range and avoid inventing missing relic behavior."""
        hp_values = [int(c["starting_hp"]) for c in self.inventory["characters"]]
        gold_values = {int(c["starting_gold"]) for c in self.inventory["characters"]}
        self.assertEqual(1, len(gold_values), "this case assumes Gold is a native constant")

        self.assertIn(f"`{min(hp_values)}` to `{max(hp_values)}`", self.grammar)
        self.assertIn(f"{gold_values.pop()} Gold", self.grammar)

        grammar = normalized(self.grammar)
        self.assertIn("not** recorded in the pinned catalog", grammar)
        self.assertIn("does from memory", grammar)

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

    def test_grammar_separates_fact_convention_and_creative_decision(self) -> None:
        grammar = normalized(self.grammar)
        for category in ("pinned fact", "observed convention", "creative decision"):
            self.assertIn(category, grammar)
        self.assertIn("not a universal ten-card rule", grammar)
        self.assertIn("not a universal `4/4/2` rule", grammar)
        self.assertIn("research, not independent authority", grammar)

    def test_character_grammar_is_lazy_and_precedes_creative_questions(self) -> None:
        path = "design/character-foundation.md"
        for routed in (self.api_skill, self.modmaker_skill, self.route, self.interview):
            self.assertIn(path, routed)
        route = normalized(self.route)
        api_skill = normalized(self.api_skill)
        self.assertIn("character/foundation", route)
        self.assertIn("load only the design references", route)
        self.assertIn("load it only for that character surface", api_skill)

    def test_interview_proposes_an_exact_deck_before_requesting_details(self) -> None:
        grammar = normalized(self.grammar)
        interview = normalized(self.interview)
        for contract in (
            "every card name, count, base effect, upgrade, total deck size",
            "do not ask the user to name ten cards",
            "present the exact proposal at confirmation without adding a deck question",
        ):
            self.assertIn(contract, grammar)
        for contract in (
            "recommend the exact card names, counts, base effects, upgrades, and total",
            "never ask the user to name ten cards from a blank form",
            "not a universal `4/4/2` or ten-card rule",
        ):
            self.assertIn(contract, interview)

    def test_departures_are_preserved_with_three_consequences(self) -> None:
        grammar = normalized(self.grammar)
        for consequence in ("onboarding", "compatibility", "balance"):
            self.assertIn(f"**{consequence}:**", grammar)
        self.assertIn("do not reject an implementable departure", grammar)
        self.assertIn("preserve the departure literally", grammar)
        self.assertIn("cardtag.strike", grammar)
        self.assertIn("cardtag.defend", grammar)

    def test_character_spec_records_basis_rationale_and_departure(self) -> None:
        spec = normalized(self.spec)
        for field in (
            "native design basis",
            "pinned facts used",
            "observed convention",
            "creative decision",
            "starter deck rationale",
            "deliberate native departure",
        ):
            self.assertIn(field, spec)
        self.assertIn("does not define `design.md`", normalized(self.grammar))

    def test_scenario_matrix_covers_required_inputs_and_semantic_rubric(self) -> None:
        headings = [
            heading.lower()
            for heading in re.findall(
                r"^## Case \d+ - (.+)$", self.scenarios, re.MULTILINE
            )
        ]
        self.assertEqual(
            [
                "character with unspecified starter deck",
                "character and content-set request starts from foundation",
                "deliberate implementable departure is preserved",
            ],
            headings,
        )
        scenarios = normalized(self.scenarios)
        for rubric in (
            "lazy grounding",
            "evidence labels",
            "actionable default",
            "question economy",
            "native analogy",
            "departure handling",
            "scope honesty",
        ):
            self.assertIn(rubric, scenarios)
        self.assertIn("separate content-set and balance planning", scenarios)
        self.assertIn("do not establish runtime behavior", scenarios)
        self.assertIn("exact headings and sentences may differ", scenarios)


if __name__ == "__main__":
    unittest.main()
