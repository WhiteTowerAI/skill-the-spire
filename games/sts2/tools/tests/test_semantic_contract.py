from __future__ import annotations

import re
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"


def surface_block(text: str, heading: str, next_heading: str) -> str:
    """The SPEC envelope for one surface, wherever it now lives.

    A surface whose envelope/driver/proof are co-located owns a `surfaces/<slug>.md`
    page; that page IS the block. Otherwise fall back to slicing the shared stage
    page between two headings.
    """
    slug = heading.rstrip(":").strip().lower().replace(" ", "-")
    if slug in skill_prose.surface_names():
        # Only the envelope is framework-neutral; the same page's author section
        # legitimately names framework types. Slice the envelope section alone.
        page = skill_prose.surface(slug)
        envelope = re.search(r"## SPEC envelope\n(.*?)(?=\n## )", page, re.DOTALL)
        if not envelope:
            raise AssertionError(f"surfaces/{slug}.md has no '## SPEC envelope' section")
        return envelope.group(1)
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
        cls.spec = skill_prose.stage("spec")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.author = skill_prose.stage("author")

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
        self.assertIn("sts2-content-semantic/v3", self.contract)
        # v1 is retained in the migration note; the canonical declaration is v3.
        self.assertIn("sts2-content-semantic/v1", self.contract)

    def test_localization_contract_requires_english_and_chinese(self) -> None:
        self.assertIn("languages: [eng, zhs]", self.contract)
        self.assertIn(
            "exact English and Simplified Chinese text",
            " ".join(self.contract.split()),
        )
        self.assertIn("localization/eng/", self.author)
        self.assertIn("localization/zhs/", self.author)
        for slug in ("card", "relic", "potion", "power", "orb", "monster", "event", "character"):
            with self.subTest(surface=slug):
                self.assertIn("languages: [eng, zhs]", skill_prose.surface(slug))

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
            "ritsulib-0.5.11-sts2-0.107.1",
            "frameworkVersion=<actual-loaded-version>",
            "host=0.107.1",
            "compat=0.107.1",
        ):
            self.assertIn(token, self.contract)

    def test_support_policy_uses_simple_package_rule(self) -> None:
        guidance = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        baseline = (REPO_ROOT / "documents" / "BASELINE_RESEARCH.md").read_text(
            encoding="utf-8"
        )
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" /
            "content-capability-graph.md"
        ).read_text(encoding="utf-8")
        grounding = (STS2_API_DIR / "grounding.md").read_text(encoding="utf-8")
        adapter = (
            STS2_API_DIR / "reference" / "ritsulib-adapter.md"
        ).read_text(encoding="utf-8")
        normalized_guidance = " ".join(guidance.split())
        normalized_baseline = " ".join(baseline.split())

        for rule in (
            "all documented public consumers in that Package are supported",
            "Record a confirmed API or lifecycle problem as the smallest known limitation",
            "Do not add readiness levels or evidence badges",
        ):
            self.assertIn(rule, normalized_guidance)
        for baseline_fact in (
            "public-beta",
            "5a9110b3c1b1c428f9f349e51cd4a155266b92e3",
        ):
            self.assertIn(baseline_fact, normalized_baseline)

        self.assertIn("Official RitsuLib Product-Semantics Baseline", baseline)

        self.assertIn("Card Hand Glow", graph)
        self.assertIn("Power, Relic, and Intent", graph)
        self.assertIn("## Supported With Known Limitations", graph)
        self.assertIn("## Unsupported", graph)
        self.assertIn("pinned official RitsuLib tutorial distillations", grounding)
        self.assertIn("| Card Hand Glow |", adapter)
        self.assertIn("| Extra Badges |", adapter)

        for field in (
            "hand emphasis: none | one or more ordered rules",
            "extra badges: none | one to three",
            "extra badges: none | one",
        ):
            self.assertIn(field, self.spec)
        for removed_field in (
            "capability status:",
            "pipeline readiness:",
            "evidence badges:",
        ):
            self.assertNotIn(removed_field, self.spec)
        self.assertIn("Card highlighted in hand", self.interview)
        self.assertIn("second player-readable number", self.interview)
        self.assertNotIn("authoring recipe is not shipped yet", self.author)

    def test_retired_character_proof_identity_is_not_shipped(self) -> None:
        shipped_roots = (
            REPO_ROOT / "games" / "sts2" / "skills",
            REPO_ROOT / "plugins" / "open-mod" / "skills",
            REPO_ROOT / "skills",
        )
        violations: list[str] = []
        for root in shipped_roots:
            for path in root.rglob("*.md"):
                text = path.read_text(encoding="utf-8").lower()
                for retired_identity in ("wayfinder", "pathfinder"):
                    if retired_identity in text:
                        violations.append(
                            f"{path.relative_to(REPO_ROOT)}: {retired_identity}"
                        )
        self.assertEqual([], violations)

    def test_card_piles_package_is_supported_and_authorable(self) -> None:
        formal_reference = STS2_API_DIR / "reference" / "card-piles.md"
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" /
            "content-capability-graph.md"
        ).read_text(encoding="utf-8")
        reference = formal_reference.read_text(encoding="utf-8")
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        adapter = (
            STS2_API_DIR / "reference" / "ritsulib-adapter.md"
        ).read_text(encoding="utf-8")
        harness = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")

        self.assertTrue(formal_reference.is_file())
        for routed in (self.author, api_skill, adapter, harness):
            self.assertIn("reference/card-piles.md", routed)

        normalized = " ".join(reference.split())
        for contract in (
            "CombatOnly",
            "RunPersistent",
            "Headless",
            "TopBarDeck",
            "BottomLeft",
            "BottomRight",
            "ExtraHand",
            "AtPosition",
            "AtCenter",
            "AtPivot",
            "ModCardPileViewSpec.DeckLike",
            "CardPileCmd.Add",
            "CardPilePosition.Top",
            "CardPilePosition.Bottom",
            "LayoutResolver",
            "OnCardVisualCreated",
            "OnCardArrived",
            "NPlayerHand.StartCardPlay",
        ):
            self.assertIn(contract, normalized)

        for field in (
            "scope: combat | run",
            "style: headless | top bar deck | bottom left | bottom right | extra hand",
            "open behavior: default pile screen | public custom screen",
            "view: vanilla | deck-like | explicit capabilities",
            "movement:",
        ):
            self.assertIn(field, " ".join(self.spec.split()))
        self.assertIn("Custom Card Piles Package", self.interview)
        self.assertIn("custom Card Piles", graph)
        self.assertNotIn("custom CardPile/ExtraHand generation", graph)

    def test_gameplay_readability_routes_are_bounded_and_authorable(self) -> None:
        hand = (
            STS2_API_DIR / "reference" / "card-hand-emphasis.md"
        ).read_text(encoding="utf-8")
        badges = (
            STS2_API_DIR / "reference" / "extra-corner-labels.md"
        ).read_text(encoding="utf-8")
        card_recipe = (STS2_API_DIR / "recipes" / "card.md").read_text(
            encoding="utf-8"
        )
        power_recipe = (STS2_API_DIR / "recipes" / "power.md").read_text(
            encoding="utf-8"
        )
        relic_recipe = (STS2_API_DIR / "recipes" / "relic.md").read_text(
            encoding="utf-8"
        )
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        harness = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")
        normalized_hand = " ".join(hand.split())
        normalized_badges = " ".join(badges.split())

        for routed in (self.author, card_recipe, api_skill, harness):
            self.assertIn("reference/card-hand-emphasis.md", routed)
        for routed in (self.author, power_recipe, relic_recipe, api_skill, harness):
            self.assertIn("reference/extra-corner-labels.md", routed)

        for contract in (
            "one or more ordered rules",
            "highest active priority wins",
            "ties favor the later listed rule",
            "VisibleWhenUnplayable",
            "RefreshEveryFrame: false",
        ):
            self.assertIn(contract, normalized_hand)
        self.assertIn("hand emphasis: none | one or more ordered rules", self.spec)

        for contract in (
            "Relics may generate at most three labels",
            "Powers may generate at most one supplemental label",
            "TopLeft",
            "TopRight",
            "BottomLeft",
            "Relic: at most 4 visible characters",
            "Power: at most 6 visible characters",
            "[color=blue|gold|green|purple|red]",
            "InvokeDisplayAmountChanged()",
            "PowerExtraIconAmountLabelsInvalidated",
            "RelicExtraIconAmountLabelsInvalidated",
        ):
            self.assertIn(contract, normalized_badges)
        self.assertIn(
            "Powers use at most one top-left label", " ".join(self.spec.split())
        )
        self.assertIn("Return zero to one", " ".join(power_recipe.split()))
        self.assertIn("Return zero to three", " ".join(relic_recipe.split()))
        self.assertNotIn("zero/one/bounded-multiple provider output", power_recipe)
        self.assertNotIn("corner: top-left | top-right | bottom-left | custom", self.spec)
        # The product boundary is that Intent stays a supported public consumer while no
        # authoring recipe exists, so this recipe must not be adapted to it. M8.0 change 4
        # removed the milestone scheduling wording that used to carry that rule; the rule
        # itself is what this pins.
        self.assertIn("no Intent authoring recipe exists", normalized_badges)
        self.assertIn("Do not adapt this Relic/Power recipe to Intent", normalized_badges)

    def test_stateful_mechanics_preserve_lifetime_reset_and_save_semantics(self) -> None:
        stateful = (
            STS2_API_DIR / "reference" / "stateful-mechanics.md"
        ).read_text(encoding="utf-8")

        for field in (
            "owner",
            "schema",
            "transition",
            "consumer/output",
            "event phase",
            "lifetime",
            "reset",
            "persistence",
            "visibility",
        ):
            self.assertIn(f"**{field}**", stateful)
        for rule in (
            "Every N events across combats",
            "never clear at combat end; normal run save restores it",
            "On turn N / every N turns this combat",
            "native combat state starts at turn 1",
            '"Every 3 turns" and "on turn 3" are not synonyms.',
            "side/Card events to the declared listener and state owner.",
        ):
            self.assertIn(rule, stateful)

    def test_character_resource_preserves_payment_lifetime_and_ui_semantics(self) -> None:
        resource = (
            STS2_API_DIR / "reference" / "character-resource.md"
        ).read_text(encoding="utf-8")

        for rule in (
            "`combat` snapshot or `run` save persistence, selected per resource",
            "bounded nonnegative integer; no implicit debt",
            "rejection is nondestructive",
            "not a replacement for native Energy or Stars",
            "CustomMinimumSize = new Vector2(220, 32)",
            "does not overlap the 128x128 native Character",
            "distinct combat-2 reset",
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

    def test_advanced_targeting_preserves_selection_resolution_and_payment(self) -> None:
        reference = (
            STS2_API_DIR / "reference" / "advanced-targeting.md"
        ).read_text(encoding="utf-8")
        card_recipe = (STS2_API_DIR / "recipes" / "card.md").read_text(
            encoding="utf-8"
        )
        potion_recipe = (STS2_API_DIR / "recipes" / "potion.md").read_text(
            encoding="utf-8"
        )
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        adapter = (
            STS2_API_DIR / "reference" / "ritsulib-adapter.md"
        ).read_text(encoding="utf-8")
        harness = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")
        verify = (MODMAKER_DIR / "verify.md").read_text(encoding="utf-8")
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" / "content-capability-graph.md"
        ).read_text(encoding="utf-8")
        normalized_reference = " ".join(reference.split())
        normalized_spec = " ".join(self.spec.split())
        normalized_interview = " ".join(self.interview.split())
        normalized_graph = " ".join(graph.split())

        self.assertIn(
            "Advanced creature targeting | consumer, one/many mode, stable Mod-local target id",
            self.contract,
        )
        for field in (
            "consumer: card | potion",
            "mode: one | many",
            "target id: <stable Mod-local stem>",
            "candidate conditions",
            "acting-player conditions",
            "source conditions",
        ):
            self.assertIn(field, normalized_spec)
            self.assertIn(field, normalized_interview)

        for api in (
            "RegisterSingleTargetType",
            "RegisterSingleTargetTypeWithContext",
            "RegisterMultiTargetType",
            "CustomTargetContext",
            "CardModelTargetingExtensions.GetTargets",
            "PotionModelTargetingExtensions.GetTargets",
        ):
            self.assertIn(api, reference)

        for rule in (
            "RegisterTargetTypes();",
            "before the content pack",
            "There is no source-aware multi-target registration.",
            "mouse and controller",
            "revalidated before Energy or Stars are spent",
            "revalidated before the Potion is removed",
            "executes once with a null selected target",
            "protected override bool IsPlayable",
            "normal result pile",
            "potion + many",
            "stop authoring",
        ):
            self.assertIn(rule, normalized_reference)

        for routed in (
            self.author,
            card_recipe,
            potion_recipe,
            api_skill,
            adapter,
            harness,
            verify,
        ):
            self.assertIn("advanced-targeting.md", routed)

        self.assertIn(
            "custom multi-target Potions have a pinned lifecycle limitation",
            normalized_graph,
        )
        self.assertIn("stops at Card one/many and Potion one", normalized_graph)

    def test_card_or_relic_owned_rest_site_option_preserves_native_payment_lifecycle(self) -> None:
        reference = (
            STS2_API_DIR / "reference" / "rest-site-options.md"
        ).read_text(encoding="utf-8")
        recipe = (STS2_API_DIR / "recipes" / "relic.md").read_text(
            encoding="utf-8"
        )
        api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        adapter = (
            STS2_API_DIR / "reference" / "ritsulib-adapter.md"
        ).read_text(encoding="utf-8")
        harness = (
            STS2_API_DIR / "reference" / "selftest-harness.md"
        ).read_text(encoding="utf-8")
        verify = (MODMAKER_DIR / "verify.md").read_text(encoding="utf-8")
        modmaker = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        graph = (
            REPO_ROOT / "games" / "sts2" / "tests" /
            "content-capability-graph.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        normalized_spec = " ".join(self.spec.split())
        normalized_interview = " ".join(self.interview.split())

        self.assertIn("Card- or Relic-owned Rest Site option", self.contract)
        for field in (
            "owner: card",
            "owner: relic",
            "eligibility:",
            "repeatability: once per Rest Site | once per run",
            "enabled rule: always | can pay fixed Gold cost",
            "cost: free | <nonnegative integer> Gold",
            "after success: leave | keep remaining options available",
            "multiplayer: singleplayer only",
        ):
            self.assertIn(field, normalized_spec)

        for intake_rule in (
            "distinguish when it is absent from when it is visible but gray",
            "once per Rest Site",
            "fixed Gold price",
            "same-site repeat",
        ):
            self.assertIn(intake_rule, normalized_interview)

        for api in (
            "ModRestSiteOptionTemplate",
            "TryModifyRestSiteOptions",
            "RestSiteOptionAssetProfile",
            "SavedAttachedState<<OwnerName>, bool>",
            "ShouldDisableRemainingRestSiteOptions",
            "NetGameType.Singleplayer",
            "GoldLossType.Spent",
            "CreatureCmd.GainMaxHp",
        ):
            self.assertIn(api, reference)

        for rule in (
            "NRestSiteButton.Create` snapshots",
            "`OnSelect() == false` keeps the option",
            "A successful option can never remain available in that same visit",
            "`ShouldOffer(player)`",
            "`CanPay(player)`",
            "returns `false` only immediately after this option's success",
            "res://images/ui/rest_site/option_heal.png",
            "Modifier owners",
            "arbitrary transactional outcomes",
            "dev-console `gold` command ignores negative values",
            "Tier 2 requires a structured post-state proof plus `selftest done`",
        ):
            self.assertIn(rule, normalized)

        for routed in (
            self.author,
            recipe,
            api_skill,
            adapter,
            harness,
            verify,
            modmaker,
        ):
            self.assertIn("rest-site-options.md", routed)

        self.assertIn("Card/Relic-owned Rest Site option", graph)
        self.assertIn("checked custom/Heal-fallback icon", graph)
        self.assertIn("M66_REST_SITE_OPTIONS_RESULTS.md", graph)

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
