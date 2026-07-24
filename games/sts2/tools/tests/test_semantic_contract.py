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

    def test_adapter_records_all_low_risk_surfaces_as_pipeline_supported(self) -> None:
        for surface in ("Card", "Relic", "Potion", "Power", "Keyword", "Enchantment", "Orb"):
            row = next(line for line in self.adapter.splitlines() if f"| {surface} |" in line)
            self.assertIn("pipeline-supported", row)

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

    def test_r4_monster_encounter_uses_ritsulib_registration_and_static_factory(self) -> None:
        recipe = (RECIPES_DIR / "monster.md").read_text(encoding="utf-8")
        author = (MODMAKER_DIR / "author.md").read_text(encoding="utf-8")
        for token in (
            "ModMonsterTemplate",
            "ModEncounterTemplate",
            ".Monster<",
            ".ActEncounter<",
            ".GlobalEncounter<",
            "RoomType => RoomType.Monster",
            "MonsterAssetProfile",
            "TryCreateCreatureVisuals",
            "RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>",
            "MOD>_MONSTER_<TYPE",
            "MOD>_ENCOUNTER_<TYPE",
            "RitsuMonsterProof",
        ):
            self.assertIn(token, recipe)
        for token in (
            "using BaseLib",
            "CustomMonsterModel",
            "CustomEncounterModel",
            "NodeFactory<NCreatureVisuals>",
            "CreateCustomVisuals()",
            "public override string CustomVisualPath",
        ):
            self.assertNotIn(token, recipe)
        for token in (
            "CustomMonsterModel",
            "CustomEncounterModel",
            "NodeFactory<NCreatureVisuals>",
        ):
            self.assertNotIn(token, author)

        monster_row = next(
            line for line in self.adapter.splitlines() if "| Monster |" in line
        )
        encounter_row = next(
            line for line in self.adapter.splitlines() if "| Encounter |" in line
        )
        self.assertIn("pipeline-supported", monster_row)
        self.assertIn("pipeline-supported", encounter_row)

    def test_r4_event_uses_ritsulib_registration_localization_and_assets(self) -> None:
        recipe = (RECIPES_DIR / "event.md").read_text(encoding="utf-8")
        for token in (
            "ModEventTemplate",
            ".SharedEvent<",
            ".ActEvent<",
            "InitialOptionKey",
            "ModOptionKey",
            "events.json",
            "EventAssetProfile",
            "CreateModRelicOption",
        ):
            self.assertIn(token, recipe)
        normalized = " ".join(recipe.split())
        self.assertIn(
            "forcedFollowUp noToken=True wrongAct=True roomForced=True "
            "eventForced=True entered=true seals=1->0 restored=True",
            normalized,
        )
        for token in (
            "using BaseLib",
            "CustomEventModel",
            "CustomInitialPortraitPath",
            "new EventLoc(",
        ):
            self.assertNotIn(token, recipe)

        event_row = next(
            line for line in self.adapter.splitlines() if "| Event |" in line
        )
        self.assertIn("pipeline-supported", event_row)

    def test_r4_character_uses_typed_pools_and_static_asset_profile(self) -> None:
        recipe = (RECIPES_DIR / "character.md").read_text(encoding="utf-8")
        for token in (
            "ModCharacterTemplate",
            "TypeListCardPoolModel",
            "TypeListRelicPoolModel",
            "TypeListPotionPoolModel",
            ".Character<",
            ".AddStartingCard<",
            ".AddStartingRelic<",
            ".Power<",
            "CharacterAssetProfile",
            "CharacterSelectIconPath",
            "EnergyCounterPath",
            "character foundation/static-presentation",
            "HP `72/72`",
            "cards7/relic1/potion1/power1",
        ):
            self.assertIn(token, recipe)
        for token in (
            "using BaseLib",
            "PlaceholderCharacterModel",
            "[Pool(",
            "AddCharacter(",
            "CustomEnergyCounter",
        ):
            self.assertNotIn(token, recipe)

        character_row = next(
            line for line in self.adapter.splitlines() if "| Character |" in line
        )
        self.assertIn("pipeline-supported", character_row)

    def test_r5_stateful_relic_uses_saved_attached_state_and_native_turns(self) -> None:
        stateful = (
            STS2_API_DIR / "reference" / "stateful-mechanics.md"
        ).read_text(encoding="utf-8")
        author = (MODMAKER_DIR / "author.md").read_text(encoding="utf-8")
        relic = (RECIPES_DIR / "relic.md").read_text(encoding="utf-8")
        selftest = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")

        for token in (
            "SavedAttachedState<SpecificRelic, int/bool>",
            "SavedAttachedState<MyRelic, int>",
            "PlayerCombatState.TurnNumber",
            "SavedProperties.From(liveRelic)",
            "RitsuStateProof",
            "strict Tier 2",
            "only the declared RitsuLib runtime dependency",
        ):
            self.assertIn(token, stateful)
        for text in (stateful, author, relic, selftest):
            self.assertNotIn("[SavedProperty]", text)

        state_row = next(
            line for line in self.adapter.splitlines()
            if "| Stateful relic cadence |" in line
        )
        self.assertIn("SavedAttachedState<SpecificRelic, int/bool>", state_row)
        self.assertIn("pipeline-supported", state_row)

    def test_r5_resource_uses_secondary_resource_and_public_ui_attachment(self) -> None:
        resource = (
            STS2_API_DIR / "reference" / "character-resource.md"
        ).read_text(encoding="utf-8")
        author = (MODMAKER_DIR / "author.md").read_text(encoding="utf-8")
        selftest = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")

        for token in (
            "ModSecondaryResourceRegistry",
            "SecondaryResourceDefinition",
            "SecondaryResourcePersistencePolicy.Combat",
            "SecondaryResourceCmd.Get",
            "SecondaryResourceCmd.Gain",
            "SecondaryResourceCmd.Spend",
            "RegisterCombatUi",
            "ModNodeAttachmentRegistry",
            "TryGetAttached",
            "SecondaryResourceUiRuntime.UpdateCombatUi",
            "new Vector2(220, 32)",
            "new Vector2(160, 0)",
            "188x32",
            "RitsuResourceProof",
            "RitsuWayfinderProof",
        ):
            self.assertIn(token, resource)

        for forbidden in (
            "ScopedState<PlayerCombatState",
            "CombatUiKernel.Activated",
            "ResolveCombatUiActivate",
        ):
            self.assertNotIn(forbidden, resource)

        for token in (
            "RegisterCombatUi",
            "SecondaryResourceCmd",
            "220x32 root",
            "`(160,0)` offset",
            "resource UI complete expected=all observed=all",
        ):
            self.assertIn(token, selftest)
        self.assertIn("SecondaryResourceDefinition", author)
        self.assertIn("public `RegisterCombatUi`", author)

        for surface in (
            "Combat resource",
            "Combat UI attachment",
        ):
            row = next(
                line for line in self.adapter.splitlines()
                if f"| {surface} |" in line
            )
            self.assertIn("pipeline-supported", row)

    def test_r5_ordered_buffer_uses_attached_semantics_and_native_lifecycle(self) -> None:
        buffer = (
            STS2_API_DIR / "reference" / "ordered-card-buffer.md"
        ).read_text(encoding="utf-8")
        spec = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")

        for token in (
            "AttachedState<PlayerCombatState, RouteState>",
            "States.GetOrCreate",
            "normal Play -> Discard lifecycle",
            "AddGeneratedCardToCombat",
            "CardGeneratedEntry",
            "N>E>S>W",
            "Block `20`",
            "wayfinder R5 parity complete expected=all observed=all",
        ):
            self.assertIn(token, buffer)
        for forbidden in (
            "ScopedState<PlayerCombatState",
            "skipVisuals: true` lifecycle are supported",
        ):
            self.assertNotIn(forbidden, buffer)
        self.assertIn(
            "Do not call `CardPileCmd.Add(this, customPile, ...)`",
            buffer,
        )

        self.assertIn(
            "**source destination**: normal STS2 result pile, default Discard",
            spec,
        )
        self.assertIn("Retained-card zone UI is unsupported", spec)
        buffer_row = next(
            line for line in self.adapter.splitlines()
            if "| Ordered semantic buffer |" in line
        )
        self.assertIn("AttachedState<PlayerCombatState,TState>", buffer_row)
        self.assertIn("pipeline-supported", buffer_row)

    def test_migration_results_and_capability_graph_record_the_promoted_boundary(self) -> None:
        results = (
            REPO_ROOT / "documents" / "history" /
            "RITSULIB_MIGRATION_RESULTS.md"
        ).read_text(encoding="utf-8")
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" /
            "content-capability-graph.md"
        ).read_text(encoding="utf-8")
        readme = (
            REPO_ROOT / "games" / "sts2" / "tests" / "README.md"
        ).read_text(encoding="utf-8")

        for token in (
            "| R5 | stateful relic cadence, Secondary Resource/payment, ordered semantic buffer",
            "| R6 | generated-Mod-local singleplayer Scry helper completed |",
            "| R7 | canceled by the human lead; no pass is claimed |",
            "Codex/portable `0.6.0` payloads produced",
        ):
            self.assertIn(token, results)

        for token in (
            "RitsuLib-only",
            "SecondaryResourceDefinition",
            "SecondaryResourceCmd",
            "RegisterCombatUi",
            "AttachedState<PlayerCombatState,TState>",
            "retained played-card custom piles",
        ):
            self.assertIn(token, graph + self.adapter)
        self.assertNotIn("resource/buffer/UI migration remains next", readme)
        self.assertNotIn("resource/buffer/UI migration is next", graph)

    def test_r6_scry_helper_is_local_ordered_and_singleplayer_only(self) -> None:
        helper = (
            STS2_API_DIR / "reference" / "scry-helper.md"
        ).read_text(encoding="utf-8")
        author = (MODMAKER_DIR / "author.md").read_text(encoding="utf-8")
        verify = (MODMAKER_DIR / "verify.md").read_text(encoding="utf-8")
        selftest = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")
        results = (
            REPO_ROOT / "documents" / "history" /
            "RITSULIB_MIGRATION_RESULTS.md"
        ).read_text(encoding="utf-8")
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" /
            "content-capability-graph.md"
        ).read_text(encoding="utf-8")

        for token in (
            "OpenModScryResult",
            "NetGameType.Singleplayer",
            "CardSelectCmd.FromSimpleGrid",
            "CardSelectorPrefs.DiscardSelectionPrompt",
            "seen.Where(selected.Contains).ToList()",
            "CardPileCmd.Add(card, discardPile)",
            "History.CardDiscarded(combatState, card)",
            "Hook.AfterCardDiscarded",
            "R6 scry helper complete expected=all observed=all",
            "zero/empty/short/full",
        ):
            self.assertIn(token, helper)

        for forbidden in (
            "using BaseLib",
            "BaseLib.dll",
            "PackageReference Include=\"BaseLib",
            "ScryModifierHook",
            "AfterScryHook",
        ):
            self.assertNotIn(forbidden, helper)

        for text in (author, verify, selftest):
            self.assertIn("scry-helper.md", text)
        self.assertIn("NSimpleCardSelectScreen", verify + selftest)
        self.assertIn("singleplayer", author.lower())
        self.assertIn(
            "| R6 | generated-Mod-local singleplayer Scry helper completed |",
            results,
        )
        self.assertIn("generated-Mod-local top-X selector", graph)


if __name__ == "__main__":
    unittest.main()
