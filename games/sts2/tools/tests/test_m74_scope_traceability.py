from __future__ import annotations

import copy
import re
import sys
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
TOOLS_DIR = REPO_ROOT / "games" / "sts2" / "tools"
SCENARIOS_PATH = REPO_ROOT / "games" / "sts2" / "tests" / "m74-scope-traceability-scenarios.md"
sys.path.insert(0, str(TOOLS_DIR))
import design_trace  # noqa: E402


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


class M74ScopeTraceabilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.design = (MODMAKER_DIR / "design.md").read_text(encoding="utf-8")
        cls.contract = (MODMAKER_DIR / "semantic-contract.md").read_text(encoding="utf-8")
        cls.spec = skill_prose.stage("spec")
        cls.author = skill_prose.stage("author")
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")
        cls.design_example = design_trace._extract_json_block(
            cls.design,
            design_trace.DESIGN_START,
            design_trace.DESIGN_END,
            "design instructions",
        )
        cls.spec_example = design_trace._extract_json_block(
            cls.spec,
            design_trace.SPEC_START,
            design_trace.SPEC_END,
            "spec instructions",
        )

    def test_design_stage_sits_between_interview_and_spec(self) -> None:
        self.assertIn("| `design.md` |", self.skill)
        state_index = self.skill.index("0. STATE CHECK")
        route_index = self.skill.index("1. ROUTE (route.md)")
        interview_index = self.skill.index("2. INTERVIEW (interview.md)")
        design_index = self.skill.index("3. DESIGN (design.md)")
        spec_index = self.skill.index("4. SPEC (semantic-contract.md + spec.md)")
        self.assertLess(state_index, route_index)
        self.assertLess(route_index, interview_index)
        self.assertLess(interview_index, design_index)
        self.assertLess(design_index, spec_index)
        self.assertIn("- [x] design", self.spec)

    def test_artifact_ownership_and_adaptive_depth_are_explicit(self) -> None:
        design = normalized(self.design)
        for artifact, ownership in (
            ("`design.md`", "player intent"),
            ("`spec.md`", "exact framework-neutral operations"),
            ("`plan.md`", "stage status only"),
            ("`memory.md`", "resolved technical identities"),
        ):
            self.assertIn(artifact, design)
            self.assertIn(ownership, design)
        self.assertIn("**fast:**", design)
        self.assertIn("**co-design:**", design)
        self.assertIn("**revision:**", design)
        self.assertIn("no empty full-design ceremony", design)
        self.assertIn("one combined design/current-slice/spec confirmation", design)

    def test_scope_schema_defines_four_dispositions_and_fail_closed_gap(self) -> None:
        design = normalized(self.design)
        for disposition in ("**must:**", "**placeholder:**", "**defer:**", "**out-of-scope:**"):
            self.assertIn(disposition, design)
        # Explicit acceptance of a visible difference is INV-5, stated once in
        # `invariants.md` and named by the stages that must obtain it.
        scope_corpus = normalized(
            self.design + self.route + skill_prose.read(skill_prose.INVARIANTS_PAGE)
        )
        for contract in (
            "blocking_gaps",
            "do not freeze design, write spec, scaffold",
            "continue only after the user",
            "request to avoid questions does not permit a silent downgrade",
        ):
            self.assertIn(contract, scope_corpus)

    def test_instruction_examples_form_one_valid_bidirectional_trace(self) -> None:
        self.assertEqual(
            (3, 2),
            design_trace.validate_pair(self.design_example, self.spec_example),
        )
        spec = normalized(self.spec)
        self.assertIn("generation allowlist", spec)
        self.assertIn("one stable `op-###`", spec)
        self.assertIn("shipped semantic recipe/reference", spec)
        self.assertIn("emit only operations listed", normalized(self.author))

    def test_trace_rejects_missing_or_extra_spec_operations(self) -> None:
        missing = copy.deepcopy(self.spec_example)
        missing["operations"].pop()
        with self.assertRaisesRegex(design_trace.DesignTraceError, "operation mismatch"):
            design_trace.validate_pair(self.design_example, missing)

        extra = copy.deepcopy(self.spec_example)
        extra["operations"].append(
            {
                "operation_id": "OP-999",
                "design_ids": ["D-001"],
                "semantic_target": "Untraced convenience behavior",
                "supported_route": "recipes/card.md",
            }
        )
        with self.assertRaisesRegex(design_trace.DesignTraceError, "operation mismatch"):
            design_trace.validate_pair(self.design_example, extra)

    def test_trace_rejects_future_leak_and_one_way_links(self) -> None:
        future_leak = copy.deepcopy(self.spec_example)
        future_leak["operations"][0]["design_ids"] = ["D-003"]
        with self.assertRaisesRegex(design_trace.DesignTraceError, "non-current"):
            design_trace.validate_pair(self.design_example, future_leak)

        one_way = copy.deepcopy(self.spec_example)
        one_way["operations"][0]["design_ids"] = ["D-002"]
        with self.assertRaisesRegex(design_trace.DesignTraceError, "not listed"):
            design_trace.validate_pair(self.design_example, one_way)

    def test_trace_rejects_blocking_gap_and_invalid_disposition_support(self) -> None:
        blocked = copy.deepcopy(self.design_example)
        blocked["blocking_gaps"] = ["Alternative Energy has no supported route"]
        with self.assertRaisesRegex(design_trace.DesignTraceError, "blocking_gaps"):
            design_trace.validate_pair(blocked, self.spec_example)

        invalid_placeholder = copy.deepcopy(self.design_example)
        invalid_placeholder["current_slice"][1]["support"] = "confirmed"
        with self.assertRaisesRegex(design_trace.DesignTraceError, "placeholder-fallback"):
            design_trace.validate_pair(invalid_placeholder, self.spec_example)

        future_operation = copy.deepcopy(self.design_example)
        future_operation["future_vision"][0]["spec_operations"] = ["OP-003"]
        with self.assertRaisesRegex(design_trace.DesignTraceError, "cannot map"):
            design_trace.validate_pair(future_operation, self.spec_example)

    def test_trace_rejects_invented_supported_route(self) -> None:
        invented = copy.deepcopy(self.spec_example)
        invented["operations"][0]["supported_route"] = "future/alternative-energy.md"
        with self.assertRaisesRegex(design_trace.DesignTraceError, "invalid supported route"):
            design_trace.validate_pair(self.design_example, invented)

        missing = copy.deepcopy(self.spec_example)
        missing["operations"][0]["supported_route"] = "recipes/not-a-real-route.md"
        design_text = (MODMAKER_DIR / "design.md").read_text(encoding="utf-8")
        spec_text = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8").replace(
            '"supported_route": "recipes/card.md"',
            '"supported_route": "recipes/not-a-real-route.md"',
            1,
        )
        self.assertIn(missing["operations"][0]["supported_route"], spec_text)
        with self.assertRaisesRegex(design_trace.DesignTraceError, "does not exist"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                design_path = temp / "DESIGN.md"
                spec_path = temp / "SPEC.md"
                design_path.write_text(design_text, encoding="utf-8")
                spec_path.write_text(spec_text, encoding="utf-8")
                design_trace.validate_files(design_path, spec_path)

    def test_pre_m74_resume_backfills_without_inventing_history(self) -> None:
        combined = normalized(self.route + self.design)
        for contract in (
            "spec.md` but no `design.md",
            "do not restart or re-interview",
            "record no invented rationale, rejected alternative, or future vision",
            "this migration records existing truth; it is not a design revision",
        ):
            self.assertIn(contract, combined)

    def test_scenario_matrix_covers_scope_future_and_fast_path(self) -> None:
        headings = [
            heading.lower()
            for heading in re.findall(
                r"^## Case \d+ - (.+)$", self.scenarios, re.MULTILINE
            )
        ]
        self.assertEqual(
            [
                "supported resource and unsupported energy replacement fail closed",
                "larger frost-oracle vision is separated from the first playable slice",
                "exact card keeps a compact design capsule",
            ],
            headings,
        )
        scenarios = normalized(self.scenarios)
        for rubric in (
            "artifact ownership",
            "explicit scope",
            "boundary honesty",
            "bidirectional trace",
            "no future leakage",
            "decision preservation",
            "question economy",
            "scope honesty",
        ):
            self.assertIn(rubric, scenarios)
        self.assertIn("exact headings and sentences may differ", scenarios)
        self.assertIn("do not prove runtime behavior", scenarios)


if __name__ == "__main__":
    unittest.main()
