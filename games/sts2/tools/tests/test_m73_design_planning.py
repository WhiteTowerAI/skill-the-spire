from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"
DESIGN_DIR = STS2_API_DIR / "design"
SCENARIOS_PATH = REPO_ROOT / "games" / "sts2" / "tests" / "m73-design-planning-scenarios.md"


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


class M73DesignPlanningContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modmaker_skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.spec = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")
        cls.mechanic = (DESIGN_DIR / "mechanic-planning.md").read_text(encoding="utf-8")
        cls.content_set = (DESIGN_DIR / "content-set-planning.md").read_text(encoding="utf-8")
        cls.balance = (DESIGN_DIR / "balance-planning.md").read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")

    def test_three_design_references_exist_and_are_lazily_routed(self) -> None:
        paths = (
            "design/mechanic-planning.md",
            "design/content-set-planning.md",
            "design/balance-planning.md",
        )
        for path in paths:
            for routed in (self.modmaker_skill, self.api_skill, self.route):
                self.assertIn(path, routed)

        route = normalized(self.route)
        self.assertIn("load the smallest applicable set", route)
        self.assertIn("exact narrow card stays on the fast path", route)
        self.assertIn("merely because the card contains a cost or effect number", route)

    def test_mechanic_planning_covers_decision_loop_and_dominance(self) -> None:
        mechanic = normalized(self.mechanic)
        for contract in (
            "player fantasy",
            "core decision",
            "risk and reward",
            "counterplay or pressure",
            "rules and edge cases",
            "tuning knobs",
            "unfavorable, ordinary, and favorable state",
            "ignore this mechanic",
            "self-funding, deterministic, or unbounded",
        ):
            self.assertIn(contract, mechanic)
        self.assertIn("two or three structures", mechanic)
        self.assertIn("number-only variants are not different mechanics", mechanic)

    def test_content_set_planning_uses_roles_and_directed_relationships(self) -> None:
        content_set = normalized(self.content_set)
        for role in (
            "foundation",
            "access/enabler",
            "payoff",
            "consistency",
            "defense/safety",
            "scaling",
            "bridge/off-ramp",
            "release valve",
        ):
            self.assertIn(role, content_set)
        for contract in (
            "directed interaction graph",
            "isolated nodes",
            "circular prerequisites",
            "source -> dependent edges",
            "not mandatory one-card slots",
        ):
            self.assertIn(contract, content_set)

    def test_balance_planning_uses_evidence_math_and_mod_forward_ceiling(self) -> None:
        balance = normalized(self.balance)
        for evidence in (
            "user-provided measurements",
            "exact pinned `0.107.1` values",
            "transparent calculation",
            "open creative hypothesis",
        ):
            self.assertIn(evidence, balance)
        for contract in (
            "mod-forward power bias",
            "modestly stronger",
            "not a fixed percentage",
            "weak floor",
            "playability ceiling",
            "time to first payoff = ceil",
            "conversion efficiency",
            "low, working, and high scenarios",
            "do not claim balanced from a formula alone",
        ):
            self.assertIn(contract, balance)

    def test_interview_carries_compact_capsule_without_claiming_evidence(self) -> None:
        interview = normalized(self.interview)
        for field in (
            "planning references:",
            "player fantasy:",
            "core decision:",
            "loop:",
            "risk/reward:",
            "counterplay/pressure:",
            "content roles:",
            "interaction graph:",
            "formula/economy:",
            "tuning knobs:",
            "dominant-strategy check:",
            "open hypotheses:",
        ):
            self.assertIn(field, interview)
        self.assertIn("highest-impact open design decision first", interview)
        self.assertIn("never invent a fixed power percentage", interview)
        self.assertIn("never call static reasoning, compilation", interview)

    def test_spec_lowers_only_accepted_exact_supported_behavior(self) -> None:
        spec = normalized(self.spec)
        for contract in (
            "user-accepted, supported, exact current behavior",
            "directed source-to-dependent relationships into `interactions`",
            "keep unsupported operations in `gaps`",
            "pause before freezing spec",
            "playtest-only balance hypothesis",
            "never write `balanced`, `fun`, or fabricated playtest evidence",
        ):
            self.assertIn(contract, spec)
        self.assertIn("design role:", spec)
        self.assertIn("m7.4 owns the durable `design.md`", spec)

    def test_every_reference_preserves_m74_and_runtime_boundaries(self) -> None:
        for reference in (self.mechanic, self.content_set, self.balance):
            text = normalized(reference)
            self.assertIn("m7.4", text)
            self.assertIn("spec.md", text)
        self.assertIn("not a runtime route", normalized(self.mechanic))
        self.assertIn("do not fabricate", normalized(self.content_set))
        self.assertIn("m7.6 owns", normalized(self.balance))

    def test_scenario_matrix_covers_required_cases_and_rubric(self) -> None:
        headings = [
            heading.lower()
            for heading in re.findall(
                r"^## Case \d+ - (.+)$", self.scenarios, re.MULTILINE
            )
        ]
        self.assertEqual(
            [
                "ambiguous heat mechanic gets one structural decision",
                "glassblower character receives a connected content set",
                "ink economy uses a generous working hypothesis",
            ],
            headings,
        )
        scenarios = normalized(self.scenarios)
        for rubric in (
            "lazy planning",
            "question economy",
            "decision preservation",
            "meaningful alternatives",
            "sts2-native pressure",
            "interaction coverage",
            "evidence honesty",
            "mod-forward power",
            "scope honesty",
        ):
            self.assertIn(rubric, scenarios)
        self.assertIn("ceil(3 / expected skill triggers per turn)", scenarios)
        self.assertIn("4 damage per ink", scenarios)
        self.assertIn("do not prove runtime behavior", scenarios)
        self.assertIn("exact headings and sentences may differ", scenarios)


if __name__ == "__main__":
    unittest.main()
