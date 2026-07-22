from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"
RECIPES_DIR = STS2_API_DIR / "recipes"


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
        cls.contract = (MODMAKER_DIR / "semantic-contract.md").read_text(encoding="utf-8")
        cls.spec = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")
        cls.adapter = (
            STS2_API_DIR / "reference" / "ritsulib-adapter.md"
        ).read_text(encoding="utf-8")

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

    def test_same_contract_selects_pinned_ritsulib_card_and_relic_routes(self) -> None:
        self.assertIn("ritsulib-0.4.62-sts2-0.107.1", self.adapter)
        self.assertIn("ModCardTemplate", self.adapter)
        self.assertIn("ModRelicTemplate", self.adapter)
        self.assertIn("CardAssetProfile", self.adapter)
        self.assertIn("RelicAssetProfile", self.adapter)
        self.assertIn("lib/0.107.1/STS2-RitsuLib.dll", self.adapter)
        for token in (
            "ModPotionTemplate",
            "ModPowerTemplate",
            "CardKeywordOwnedByLocNamespace",
            "ModEnchantmentTemplate",
            "ModOrbTemplate",
            "PotionAssetProfile",
            "PowerAssetProfile",
            "EnchantmentAssetProfile",
            "OrbAssetProfile",
        ):
            self.assertIn(token, self.adapter)

    def test_card_and_relic_adapter_uses_content_pack_without_historical_pool_attributes(self) -> None:
        card_start = self.adapter.index("### Card")
        relic_start = self.adapter.index("### Relic")
        card = self.adapter[card_start:relic_start]
        relic = self.adapter[relic_start:self.adapter.index("## Cross-cutting routes")]
        for block in (card, relic):
            self.assertIn("CreateContentPack", block)
            self.assertNotIn("[Pool", block)
            self.assertNotIn("BaseLib", block)
        self.assertIn("MOD_CATEGORY_TYPENAME", self.adapter)

    def test_r3_adapter_records_all_low_risk_surfaces_as_complete(self) -> None:
        for surface in ("Card", "Relic", "Potion", "Power", "Keyword", "Enchantment", "Orb"):
            row = next(line for line in self.adapter.splitlines() if f"| {surface} |" in line)
            self.assertIn("R3 complete", row)

    def test_diagnostic_envelope_records_framework_host_and_compat(self) -> None:
        for token in (
            "framework=RitsuLib",
            "frameworkVersion=0.4.62",
            "host=0.107.1",
            "compat=0.107.1",
        ):
            self.assertIn(token, self.contract)

    def test_r3_low_risk_recipes_use_only_the_ritsu_adapter_contract(self) -> None:
        required = {
            "potion.md": (
                "ModPotionTemplate",
                ".Potion<SharedPotionPool",
                "PotionAssetProfile",
                "MOD_POTION_TYPENAME",
                "localization/eng/potions.json",
                "placeholder",
                "selftest done",
            ),
            "power.md": (
                "ModPowerTemplate",
                ".Power<",
                "PowerAssetProfile",
                ".smartDescription",
                "Counter",
                "placeholder",
            ),
            "keyword.md": (
                "CardKeywordOwnedByLocNamespace",
                "CardKeyword",
                "CanonicalKeywords",
                "card_keywords.json",
                "null icon",
            ),
            "enchantment.md": (
                "ModEnchantmentTemplate",
                ".Enchantment<",
                "EnchantmentAssetProfile",
                "CardCmd.Enchant",
                "64x64",
                "placeholder",
            ),
            "orb.md": (
                "ModOrbTemplate",
                ".Orb<",
                "OrbAssetProfile",
                "ChannelSfx",
                "frost_orb",
                "Evoke",
            ),
        }
        historical_tokens = (
            "using BaseLib",
            "CustomPotionModel",
            "CustomPowerModel",
            "CustomEnchantmentModel",
            "CustomOrbModel",
            "[Pool(",
        )
        for filename, tokens in required.items():
            with self.subTest(recipe=filename):
                text = (RECIPES_DIR / filename).read_text(encoding="utf-8")
                for token in tokens:
                    self.assertIn(token, text)
                for token in historical_tokens:
                    self.assertNotIn(token, text)

    def test_r3_asset_normalizer_matches_ritsu_card_profile_path(self) -> None:
        tool = (REPO_ROOT / "games" / "sts2" / "tools" / "gen_sprite.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"card":', tool)
        self.assertIn('"sub_path": "card_portraits"', tool)
        self.assertNotIn('"sub_path": "card_portraits/big"', tool)
        art_contract = (STS2_API_DIR / "reference" / "art-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("CardAssetProfile.PortraitPath", art_contract)
        self.assertIn("card_portraits/<slug>.png", art_contract)


if __name__ == "__main__":
    unittest.main()
