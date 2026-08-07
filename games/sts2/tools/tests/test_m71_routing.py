from __future__ import annotations

import re
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
SCENARIOS_PATH = REPO_ROOT / "games" / "sts2" / "tests" / "m71-routing-scenarios.md"


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


class M71RoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.spec = skill_prose.stage("spec")
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")

    def test_route_stage_precedes_adaptive_interview(self) -> None:
        self.assertIn("| `route.md` |", self.skill)
        self.assertIn("Read `route.md` first", self.interview)
        state_index = self.skill.index("0. STATE CHECK")
        route_index = self.skill.index("1. ROUTE (route.md)")
        interview_index = self.skill.index("2. INTERVIEW (interview.md)")
        design_index = self.skill.index("3. DESIGN (design.md)")
        spec_index = self.skill.index("4. SPEC (semantic-contract.md + spec.md)")
        self.assertLess(state_index, route_index)
        self.assertLess(route_index, interview_index)
        self.assertLess(interview_index, design_index)
        self.assertLess(design_index, spec_index)

    def test_fast_route_has_a_hard_question_economy(self) -> None:
        route = normalized(self.route)
        interview = normalized(self.interview)
        self.assertIn("### fast", route)
        self.assertIn("ask no question", route)
        self.assertIn("at most one compact clarification round", route)
        self.assertIn("do not add pillars, a full gdd", route)
        self.assertIn("fast asks no question when complete", interview)
        self.assertNotIn("one round only", interview)

    def test_co_design_requires_material_alternatives_and_preserves_choices(self) -> None:
        route = normalized(self.route)
        for contract in (
            "### co-design",
            "highest-impact open decision first",
            "two or three materially different choices",
            "concrete trade-off",
            "recommend and why",
            "preserve every accepted choice",
        ):
            self.assertIn(contract, route)
        self.assertIn("batch up to three questions", route)

    def test_resume_and_revision_do_not_restart_settled_work(self) -> None:
        route = normalized(self.route)
        spec = normalized(self.spec)
        for artifact in ("design.md", "spec.md", "plan.md", "memory.md"):
            self.assertIn(artifact, route)
        self.assertIn("resume the first unfinished stage immediately", route)
        self.assertIn("do not run another interview", route)
        for delta_field in ("keep", "change", "check", "re-verify"):
            self.assertIn(delta_field, route)
            self.assertIn(delta_field, spec)
        self.assertIn("preserve unrelated decisions", route)
        self.assertIn("reopen only the plan stages invalidated", route)

    def test_conflicts_and_unsupported_routes_stop_before_spec(self) -> None:
        route = normalized(self.route)
        self.assertIn("two conflicting requirements", route)
        self.assertIn("one constrained resolution question", route)
        self.assertIn("state the exact current boundary before spec or scaffold", route)
        self.assertIn("continue only after explicit acceptance", route)
        self.assertIn("never authorizes a downgrade, invented route, or silent omission", route)

    def test_m71_does_not_claim_m74_artifact_contract(self) -> None:
        route = normalized(self.route)
        self.assertIn("m7.1 does not define or generate the full `design.md` schema", route)
        self.assertIn("m7.4 owns those contracts", route)

    def test_scenario_matrix_covers_required_inputs_and_semantic_rubric(self) -> None:
        headings = [
            heading.lower()
            for heading in re.findall(
                r"^## Case \d+ - (.+)$", self.scenarios, re.MULTILINE
            )
        ]
        self.assertEqual(6, len(headings))
        scenario_text = normalized(self.scenarios)
        for required_case in (
            "clear card uses fast",
            "vague risk mechanic uses co-design",
            "contradictory cost pauses once",
            "unsupported request preserves intent",
            "unfinished project resumes directly",
            "existing card receives a bounded revision",
        ):
            self.assertIn(required_case, headings)
        for rubric in (
            "question economy",
            "materially different",
            "decision preservation",
            "boundary honesty",
            "failure signals",
        ):
            self.assertIn(rubric, scenario_text)
        self.assertIn("exact headings and sentences may differ", scenario_text)
        self.assertIn("do not prove runtime behavior", scenario_text)


if __name__ == "__main__":
    unittest.main()
