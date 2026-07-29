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
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.author = (MODMAKER_DIR / "author.md").read_text(encoding="utf-8")

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

    def test_computed_card_values_preserve_one_formula_and_native_hooks(self) -> None:
        card = surface_block(self.spec, "Card", "Custom power")
        reference = (
            STS2_API_DIR / "reference" / "card-computed-values.md"
        ).read_text(encoding="utf-8")
        mechanics = (
            STS2_API_DIR / "reference" / "mechanics.md"
        ).read_text(encoding="utf-8")
        recipe = (STS2_API_DIR / "recipes" / "card.md").read_text(
            encoding="utf-8"
        )
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        normalized_card = " ".join(card.split())
        normalized = " ".join(reference.split())
        normalized_interview = " ".join(self.interview.split())

        for field in (
            "calculated values",
            "formula <one deterministic expression>",
            "inputs <complete list>",
            "domain <integer [min,max]>",
            "evaluation <before play | after normal payment and move>",
            "variable tooltips",
        ):
            self.assertIn(field, normalized_card)

        for role in (
            "ModCardVars.ComputedDamage",
            "ModCardVars.ComputedBlock",
            "ModCardVars.ComputedEnergy",
            "ModCardVars.ComputedStars",
            "ModCardVars.ComputedPower<T>",
            "ModCardVars.ComputedPowerAmountGiven<T>",
        ):
            self.assertIn(role, reference)

        for execution_read in (
            "ComputeDynamicValue",
            "ComputeEnergyValue",
            "ComputeStarsValue",
            "ComputePowerValue<T>",
        ):
            self.assertIn(execution_read, reference)

        for rule in (
            "The formula must be pure",
            "Stop authoring when the two phases cannot be reconciled deterministically.",
            "`PreviewValue` is display-only.",
            "`BaseValue` is not the live result of a computed variable.",
            "normal Block hooks once",
            "`PowerCmd.Apply<T>` runs `ModifyPowerAmountGiven` once",
            "Energy 0 is therefore not an empty result",
            "Stars 0 renders no image",
            "WithSharedTooltip",
            "native null-icon Hover Tip",
            "real hand-Card hover consumer",
        ):
            self.assertIn(rule, normalized)

        self.assertIn("{X:starIcons()}", mechanics)
        self.assertNotIn("{X:stars()}", mechanics)
        for routed in (self.author, recipe, api_skill):
            self.assertIn("card-computed-values.md", routed)
        for intake_rule in (
            "one named formula",
            "integer minimum/maximum",
            "before this card spends its energy and leaves your hand",
        ):
            self.assertIn(intake_rule, normalized_interview)

    def test_character_combat_cues_preserve_private_all_or_nothing_contract(self) -> None:
        cues = (
            STS2_API_DIR / "reference" / "character-combat-cues.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(cues.split())
        art = (
            STS2_API_DIR / "reference" / "art-contract.md"
        ).read_text(encoding="utf-8")
        normalized_art = " ".join(art.split())

        for rule in (
            "`Idle` | 2x2 | 4 | 180 ms | loops",
            "`Attack` | 2x2 | 4 | 90 ms | one shot, then returns to `Idle`",
            "`Hit` | 2x2 | 4 | 80 ms | one shot, then returns to `Idle`",
            "`Dead` | 2x3 | 6 | 140 ms | one shot, then holds its final frame",
            "Never assign the generated set to `CharacterAssetProfile.VisualCues`",
            "One missing, unreadable, or wrongly sized expected frame disables the entire set.",
            "The incomplete route must create no cue playback node",
            "There is no `Cast` cue.",
            "character combat cues complete expected=Idle/Attack/Hit/Dead/cleanup observed=all",
            "combat cue fallback expected=one-missing-disables-all/static-combat512/no-playback observed=all",
        ):
            self.assertIn(rule, normalized)

        self.assertIn(
            "Character combat cues | enabled/disabled fixed Idle/Attack/Hit/Dead contract",
            self.contract,
        )
        for rule in (
            "Treat adjacent cells as closely spaced in-between frames, not widely separated key poses.",
            "adjacent silhouettes must substantially overlap",
            "Only the action-specific sentence, grid, and beat list may change",
        ):
            self.assertIn(rule, normalized_art)

        for rule in (
            "Attack and Hit begin near the neutral anchor",
            "Dead distributes its fall across all six frames",
        ):
            self.assertIn(rule, normalized)

        for field in (
            "neutral combat anchor",
            "continuity lock",
            "adjacent cells are small, substantially overlapping in-between pose steps",
        ):
            self.assertIn(field, " ".join(self.spec.split()))

    def test_character_ancient_dialogue_is_semantic_validated_and_native(self) -> None:
        reference = (
            STS2_API_DIR / "reference" / "ancient-dialogue.md"
        ).read_text(encoding="utf-8")
        recipe = (STS2_API_DIR / "recipes" / "character.md").read_text(
            encoding="utf-8"
        )
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        build = (MODMAKER_DIR / "build.md").read_text(encoding="utf-8")
        verify = (MODMAKER_DIR / "verify.md").read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        normalized_spec = " ".join(self.spec.split())

        self.assertIn(
            "Character Ancient dialogue | cataloged natural target",
            self.contract,
        )
        for field in (
            "visit rule: first | visit <one-based N> | repeat from visit <one-based N>",
            "speaker: Character|Ancient",
            "transition prompt",
            "start attackers and end attackers",
            "preserve the global first-visit-ever introduction",
        ):
            self.assertIn(field, normalized_spec)

        for target in (
            "DARV",
            "NEOW",
            "NONUPEIPE",
            "OROBAS",
            "PAEL",
            "TANX",
            "TEZCATARA",
            "VAKUU",
            "THE_ARCHITECT",
        ):
            self.assertIn(f"`{target}`", reference)
        for rule in (
            "The vanilla global first-visit-ever dialogue has higher priority",
            "Dialogue and line indexes begin at zero and are contiguous.",
            "Every non-terminal line has exactly one matching `.next`",
            "It does not allow `ANY` fallback.",
            "Generated Mods only provide `ancients.json`",
            "do not emit Harmony, reflection, IL, Publicizer",
            "line-level Ancient dialogue SFX is unsupported",
            "The localization resource tree requires `has_pck=true`",
            ".DustyTomeCard<<Character>, <AncientCard>>()",
            "fresh missing-resource or UI exception",
        ):
            self.assertIn(rule, normalized)

        for routed in (self.author, recipe, api_skill):
            self.assertIn("reference/ancient-dialogue.md", routed)
        self.assertIn(".DustyTomeCard<<CharacterName>, <AncientCard>>()", recipe)
        self.assertIn("CardRarity.Ancient", recipe)
        self.assertIn("ancients.json", build)
        self.assertIn("production `EnterNextAct()` path", verify)


if __name__ == "__main__":
    unittest.main()
