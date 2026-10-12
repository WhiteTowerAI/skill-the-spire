from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from collect_text_glossary import build_glossary  # noqa: E402
from text_style import (  # noqa: E402
    TextStyleError,
    load_vanilla_terms,
    validate_project_text_style,
)


VANILLA_STYLE = {
    "cards.json": (
        {
            "PROOF_CARD_BASH_LIKE.title": "Proof Bash",
            "PROOF_CARD_BASH_LIKE.description": "Deal {Damage:diff()} damage.\n"
            "Apply {VulnerablePower:diff()} [gold]Vulnerable[/gold].",
            "PROOF_CARD_DRAW.title": "Proof Draw",
            "PROOF_CARD_DRAW.description": "Draw {Cards:diff()} {Cards:plural:card|cards}.\n"
            "Gain {Energy:energyIcons()}.",
        },
        {
            "PROOF_CARD_BASH_LIKE.title": "试作痛击",
            "PROOF_CARD_BASH_LIKE.description": "造成{Damage:diff()}点伤害。\n"
            "给予{VulnerablePower:diff()}层[gold]易伤[/gold]。",
            "PROOF_CARD_DRAW.title": "试作抽牌",
            "PROOF_CARD_DRAW.description": "抽{Cards:diff()}张牌。\n获得{Energy:energyIcons()}。",
        },
    ),
    "relics.json": (
        {
            "PROOF_RELIC_ANCHOR_LIKE.title": "Proof Anchor",
            "PROOF_RELIC_ANCHOR_LIKE.description": "At the start of each combat, gain "
            "[blue]{Block}[/blue] [gold]Block[/gold] and heal [green]{Heal}[/green] HP.",
            "PROOF_RELIC_ANCHOR_LIKE.flavor": "It never moved.",
        },
        {
            "PROOF_RELIC_ANCHOR_LIKE.title": "试作船锚",
            "PROOF_RELIC_ANCHOR_LIKE.description": "每场战斗开始时，获得[blue]{Block}[/blue]点"
            "[gold]格挡[/gold]并回复[green]{Heal}[/green]点生命。",
            "PROOF_RELIC_ANCHOR_LIKE.flavor": "它从未移动过。",
        },
    ),
    "powers.json": (
        {
            "PROOF_POWER_RESONANCE.title": "Resonance",
            "PROOF_POWER_RESONANCE.description": "At the start of your turn, gain [gold]Block[/gold].",
            "PROOF_POWER_RESONANCE.smartDescription": "At the start of your turn, gain "
            "[blue]{Amount}[/blue] [gold]Block[/gold].",
        },
        {
            "PROOF_POWER_RESONANCE.title": "共鸣",
            "PROOF_POWER_RESONANCE.description": "在你的回合开始时，获得[gold]格挡[/gold]。",
            "PROOF_POWER_RESONANCE.smartDescription": "在你的回合开始时，获得[blue]{Amount}[/blue]点"
            "[gold]格挡[/gold]。",
        },
    ),
}


class TextStyleTests(unittest.TestCase):
    def write_project(self, root: Path, tables: dict[str, tuple[dict, dict]]) -> None:
        for name, (english, chinese) in tables.items():
            for language, values in (("eng", english), ("zhs", chinese)):
                directory = root / "Proof" / "localization" / language
                directory.mkdir(parents=True, exist_ok=True)
                (directory / name).write_text(json.dumps(values, ensure_ascii=False), encoding="utf-8")

    def check(self, tables: dict[str, tuple[dict, dict]]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            self.write_project(Path(tmp), tables)
            return validate_project_text_style(Path(tmp), "Proof")[1]

    def test_shipped_glossary_carries_vanilla_vocabulary(self) -> None:
        terms = {term.eng: term for term in load_vanilla_terms()}
        self.assertEqual(("格挡", "gold"), (terms["Block"].zhs, terms["Block"].color))
        self.assertEqual("易伤", terms["Vulnerable"].zhs)
        self.assertEqual("抽牌堆", terms["Draw Pile"].zhs)
        # Vanilla usually leaves card types plain, so the check must not demand a highlight.
        self.assertNotIn("Attack", terms)

    def test_vanilla_shaped_project_has_no_warnings(self) -> None:
        self.assertEqual([], self.check(VANILLA_STYLE))

    def test_broken_markup_fails(self) -> None:
        for bad in ("[gold]Block", "[color=red]Block[/color]", "[gold][b]Block[/gold][/b]", "[wave]x[/wave]"):
            tables = {"cards.json": ({"P.description": bad}, {"P.description": "格挡"})}
            with self.subTest(bad=bad), self.assertRaises(TextStyleError):
                self.check(tables)

    def test_tags_inside_grammar_branches_are_not_misread_as_unbalanced(self) -> None:
        text = "Add {Cards:diff()} [gold]{Cards:plural:Shiv[/gold]|Shivs[/gold]}."
        warnings = self.check({"cards.json": ({"P.description": text}, {"P.description": "添加{Cards:diff()}张。"})})
        self.assertFalse(any("unbalanced" in warning for warning in warnings))

    def test_card_style_drift_is_reported(self) -> None:
        warnings = self.check(
            {
                "cards.json": (
                    {"P.description": "Deal [blue]{Damage:diff()}[/blue] damage. Gain 5 Block."},
                    {"P.description": "造成 {Damage:diff()} 点伤害. 获得5点格挡。"},
                )
            }
        )
        joined = "\n".join(warnings)
        self.assertIn("Card `:diff()` already owns", joined)
        self.assertIn("share one line", joined)
        self.assertIn("term 'Block' is not highlighted", joined)
        self.assertIn("term '格挡' is not highlighted", joined)
        self.assertIn("Western punctuation", joined)
        self.assertIn("space inside Chinese text", joined)

    def test_value_surfaces_require_colored_numbers(self) -> None:
        warnings = self.check(
            {
                "potions.json": (
                    {"P.description": "Gain {Block} [gold]Block[/gold]. Draw 2 cards."},
                    {"P.description": "获得[blue]{Block}[/blue]点[gold]格挡[/gold]。抽[blue]2[/blue]张牌。"},
                )
            }
        )
        self.assertTrue(any("eng/potions.json" in w and "{Block} is uncolored" in w for w in warnings))
        self.assertTrue(any("eng/potions.json" in w and "literal 2" in w for w in warnings))
        self.assertFalse(any("zhs/potions.json" in w for w in warnings))

    def test_mod_terms_are_highlighted_elsewhere_but_not_in_their_own_entry(self) -> None:
        tables = dict(VANILLA_STYLE)
        tables["cards.json"] = (
            {"P.title": "Echo", "P.description": "Gain {ProofPower:diff()} Resonance."},
            {"P.title": "回响", "P.description": "获得{ProofPower:diff()}层共鸣。"},
        )
        warnings = self.check(tables)
        self.assertTrue(any("term 'Resonance'" in w for w in warnings))
        self.assertTrue(any("term '共鸣'" in w for w in warnings))
        self.assertFalse(any("PROOF_POWER_RESONANCE" in w for w in warnings))

    def test_power_description_must_not_show_the_canonical_amount(self) -> None:
        warnings = self.check(
            {
                "powers.json": (
                    {"P.title": "Charge", "P.description": "Gain [blue]{Amount}[/blue] [gold]Block[/gold].",
                     "P.smartDescription": "Gain [blue]{Amount}[/blue] [gold]Block[/gold]."},
                    {"P.title": "蓄能", "P.description": "获得[blue]{Amount}[/blue]点[gold]格挡[/gold]。",
                     "P.smartDescription": "获得[blue]{Amount}[/blue]点[gold]格挡[/gold]。"},
                )
            }
        )
        self.assertEqual(2, sum("canonical amount" in w for w in warnings))

    def test_ancient_options_take_event_colors(self) -> None:
        warnings = self.check(
            {
                "ancients.json": (
                    {"A.pages.INITIAL.options.PAY.description": "Lose [red]{HpLoss}[/red] HP. Heal [green]{Heal}[/green] HP."},
                    {"A.pages.INITIAL.options.PAY.description": "失去[red]{HpLoss}[/red]点生命。回复[green]{Heal}[/green]点生命。"},
                )
            }
        )
        self.assertEqual([], warnings)

    def test_titles_stay_plain_and_dialogue_keeps_its_voice(self) -> None:
        warnings = self.check(
            {
                "relics.json": ({"P.title": "[gold]Coin[/gold]"}, {"P.title": "硬币"}),
                "ancients.json": ({"A.talk.ANY.0-0.ancient": "Well..."}, {"A.talk.ANY.0-0.ancient": "嗯...好吧"}),
            }
        )
        self.assertEqual(["eng/relics.json P.title: titles and names stay plain in vanilla"], warnings)


class GlossaryBuildTests(unittest.TestCase):
    def test_aligns_terms_and_measure_words_from_vanilla_text(self) -> None:
        tables = {
            "eng": {
                "powers": {"VULNERABLE_POWER.title": "Vulnerable"},
                "static_hover_tips": {"BLOCK.title": "Block", "DECK.title": "Deck {Hotkey:choose(None):| ({})}"},
                "cards": {
                    "A.description": "Apply {VulnerablePower:diff()} [gold]Vulnerable[/gold].",
                    "B.description": "Apply {VulnerablePower:diff()} [gold]Vulnerable[/gold].",
                    "C.description": "Gain {Block:diff()} [gold]Block[/gold]. Put a card in your [gold]Hand[/gold].",
                    "D.description": "Return a card to your [gold]Hand[/gold].",
                },
            },
            "zhs": {
                "powers": {"VULNERABLE_POWER.title": "易伤"},
                "static_hover_tips": {"BLOCK.title": "格挡", "DECK.title": "牌组{Hotkey:choose(None):|（{}）}"},
                "cards": {
                    "A.description": "给予{VulnerablePower:diff()}层[gold]易伤[/gold]。",
                    "B.description": "给予{VulnerablePower:diff()}层[gold]易伤[/gold]。",
                    "C.description": "获得{Block:diff()}点[gold]格挡[/gold]。将一张牌放入[gold]手牌[/gold]。",
                    "D.description": "将一张牌放回你的[gold]手牌[/gold]。",
                },
            },
        }
        rows = {row["eng"]: row for row in build_glossary(tables)["terms"]}
        self.assertEqual(("易伤", "层", 2), (rows["Vulnerable"]["zhs"], rows["Vulnerable"]["zhs_measure"], rows["Vulnerable"]["eng_colored"]))
        self.assertEqual(("格挡", "点"), (rows["Block"]["zhs"], rows["Block"]["zhs_measure"]))
        self.assertEqual("牌组", rows["Deck"]["zhs"])
        self.assertEqual(("手牌", ["observed"]), (rows["Hand"]["zhs"], rows["Hand"]["kinds"]))
        self.assertNotIn("zhs_measure", rows["Hand"])


if __name__ == "__main__":
    unittest.main()
