from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"


def surface_block(text: str, heading: str, next_heading: str) -> str:
    match = re.search(
        rf"\*\*{re.escape(heading)}\*\*.*?(?=\*\*{re.escape(next_heading)}\*\*)",
        text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing {heading} SPEC block")
    return match.group(0)


class SemanticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = (MODMAKER_DIR / "semantic-contract.md").read_text(
            encoding="utf-8"
        )
        cls.spec = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")

    def test_contract_has_all_shared_semantic_sections(self) -> None:
        for field in (
            "content",
            "registration",
            "localization",
            "effects",
            "state",
            "presentation",
            "fallback",
            "proof",
        ):
            self.assertIn(f"**{field}**", self.contract)
        self.assertIn("sts2-content-semantic/v1", self.contract)

    def test_simple_card_and_relic_spec_are_framework_neutral(self) -> None:
        relic = surface_block(self.spec, "Relic:", "Potion")
        card = surface_block(self.spec, "Card", "Custom power")
        forbidden = (
            "BaseLib",
            "RitsuLib",
            "[Pool",
            "CustomRelicModel",
            "CustomCardModel",
            "Id.Entry",
            "csproj",
            "manifest id",
        )
        for block in (relic, card):
            for token in forbidden:
                self.assertNotIn(token, block)
            self.assertIn("logical id", block)
            self.assertIn("adapter output", block)
            for section in (
                "content",
                "registration",
                "localization",
                "effects",
                "state",
                "presentation",
                "fallback",
                "proof",
            ):
                self.assertIn(f"**{section}**", block)

    def test_diagnostic_envelope_records_pinned_compatibility(self) -> None:
        for token in (
            "framework=RitsuLib",
            "frameworkVersion=0.4.62",
            "host=0.107.1",
            "compat=0.107.1",
        ):
            self.assertIn(token, self.contract)

    def test_stateful_mechanics_preserve_lifetime_reset_and_save_semantics(self) -> None:
        stateful = (
            STS2_API_DIR / "reference" / "stateful-mechanics.md"
        ).read_text(encoding="utf-8")

        for field in (
            "event",
            "threshold/phase",
            "lifetime",
            "reset",
            "persistence",
            "owner",
            "UI meaning",
            "proof",
        ):
            self.assertIn(f"**{field}**", stateful)
        for rule in (
            "Every N events across combats",
            "never clear at combat end; normal run save restores it",
            "On turn N / every N turns this combat",
            "native combat state starts at turn 1",
            '"Every 3 turns" and "on turn 3" are not synonyms.',
            "Always scope side/card events to the owner.",
        ):
            self.assertIn(rule, stateful)

    def test_character_resource_preserves_payment_lifetime_and_ui_semantics(self) -> None:
        resource = (
            STS2_API_DIR / "reference" / "character-resource.md"
        ).read_text(encoding="utf-8")

        for rule in (
            "`combat`; a new combat starts at the registered default",
            "integer, minimum `0`; no implicit debt",
            "all-or-nothing; rejection leaves amount and payoff unchanged",
            "not a replacement for native Energy",
            "fixed 220x32 icon+text control at offset `(160,0)`; checked text-only fallback",
            "resource and native energy global rects do not intersect",
            "combat 2 has a distinct `PlayerCombatState`, amount `0`, and reset UI",
        ):
            self.assertIn(rule, resource)

    def test_ordered_buffer_preserves_values_order_and_normal_card_lifecycle(self) -> None:
        buffer = (
            STS2_API_DIR / "reference" / "ordered-card-buffer.md"
        ).read_text(encoding="utf-8")

        for rule in (
            "immutable semantic value such as direction, suit, or contribution",
            "normal STS2 result, default `Discard`; never intercept into a custom pile",
            "finite positive integer and non-destructive overflow behavior",
            "one real mutable card added",
            "every source Card reaches its normal result pile",
            "overflow leaves order/resource/UI unchanged while its source still resolves normally",
            "combat 2 has a distinct attached state, empty route, reset resource, and reset UI",
        ):
            self.assertIn(rule, buffer)

    def test_scry_preserves_local_singleplayer_selection_semantics(self) -> None:
        helper = (
            STS2_API_DIR / "reference" / "scry-helper.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(helper.split())

        for rule in (
            "singleplayer only; multiplayer and replay callers fail clearly",
            "returns an empty structured result without opening a selector or mutating piles/history",
            "inspect at most the top `amount` cards in current Draw order",
            "move selected cards to Discard in their original seen order",
            "exactly once for each selected card",
            "leave unselected cards in Draw in their original relative order",
            "There is no global Scry modifier or completion hook.",
            "zero/empty/short/full matrix",
        ):
            self.assertIn(rule, normalized)


if __name__ == "__main__":
    unittest.main()
