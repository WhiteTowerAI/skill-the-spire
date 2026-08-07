from __future__ import annotations

import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"
TOOLS_DIR = REPO_ROOT / "games" / "sts2" / "tools"
SCENARIOS_PATH = REPO_ROOT / "games" / "sts2" / "tests" / "m75-coherence-scenarios.md"
sys.path.insert(0, str(TOOLS_DIR))
import coherence_trace  # noqa: E402
import design_trace  # noqa: E402


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


class M75CoherenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.design = (MODMAKER_DIR / "design.md").read_text(encoding="utf-8")
        cls.spec = skill_prose.stage("spec")
        cls.author = skill_prose.stage("author")
        cls.api_skill = (STS2_API_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.reference = (STS2_API_DIR / "design" / "coherence-review.md").read_text(
            encoding="utf-8"
        )
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")
        cls.scope = design_trace._extract_json_block(
            cls.design,
            design_trace.DESIGN_START,
            design_trace.DESIGN_END,
            "design instructions",
        )
        cls.coherence = coherence_trace._extract_json_block(
            cls.design,
            coherence_trace.COHERENCE_START,
            coherence_trace.COHERENCE_END,
            "design instructions",
        )
        cls.items, _ = design_trace.validate_design(cls.scope)
        cls.current_ids = {
            design_id
            for design_id, item in cls.items.items()
            if item["disposition"] in design_trace.CURRENT_DISPOSITIONS
        }

    def validate(self, data: dict) -> tuple[int, int, int]:
        return coherence_trace.validate_coherence(
            data,
            known_design_ids=set(self.items),
            current_design_ids=self.current_ids,
        )

    def test_coherence_reference_is_lazy_and_does_not_widen_runtime(self) -> None:
        path = "design/coherence-review.md"
        for routed in (self.skill, self.route, self.api_skill):
            self.assertIn(path, routed)
        reference = normalized(self.reference)
        for contract in (
            "more than one intentional expressive surface",
            "not a runtime route",
            "narrow exact card",
            "placeholder is a delivery state",
            "do not invent a palette",
        ):
            self.assertIn(contract, reference)

    def test_reference_covers_six_surfaces_and_specific_conflicts(self) -> None:
        reference = normalized(self.reference)
        for surface in (
            "**mechanics:**",
            "**naming:**",
            "**localization:**",
            "**visuals:**",
            "**event text:**",
            "**character identity:**",
        ):
            self.assertIn(surface, reference)
        for conflict in (
            "contradicts behavior",
            "drifts terminology",
            "breaks identity",
            "leaks scope",
            "inverts evidence",
        ):
            self.assertIn(conflict, reference)
        self.assertIn("deliberate-tension", reference)
        self.assertIn("semantic parity, not literal sentence parity", reference)

    def test_design_example_has_valid_coherence_contract(self) -> None:
        self.assertEqual((1, 2, 0), self.validate(self.coherence))
        self.assertEqual(
            (1, 2, 0), coherence_trace.validate_file(MODMAKER_DIR / "design.md")
        )
        design = normalized(self.design)
        self.assertIn("open-mod-coherence/v1", design)
        self.assertIn("coherence_trace.py --design", design)
        self.assertIn("`conflicts` must be empty", design)

    def test_file_validator_rejects_route_drift(self) -> None:
        mismatched = self.design.replace('"route": "fast",', '"route": "revision",', 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "DESIGN.md"
            path.write_text(mismatched, encoding="utf-8")
            with self.assertRaisesRegex(
                coherence_trace.CoherenceTraceError, "must match"
            ):
                coherence_trace.validate_file(path)

    def test_validator_rejects_unknown_ids_and_unresolved_conflicts(self) -> None:
        unknown = copy.deepcopy(self.coherence)
        unknown["anchors"][0]["design_ids"] = ["D-999"]
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "unknown design"):
            self.validate(unknown)

        conflict = copy.deepcopy(self.coherence)
        conflict["surface_checks"][1]["status"] = "conflict"
        conflict["conflicts"] = [
            {
                "conflict_id": "C-001",
                "summary": "Name promises healing while SPEC deals damage",
            }
        ]
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "conflicts must be empty"):
            self.validate(conflict)

        missing_record = copy.deepcopy(self.coherence)
        missing_record["surface_checks"][1]["status"] = "conflict"
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "requires a conflicts entry"):
            self.validate(missing_record)

    def test_validator_rejects_invalid_surface_and_unused_anchor(self) -> None:
        invalid = copy.deepcopy(self.coherence)
        invalid["surface_checks"][0]["surface"] = "audio"
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "invalid coherence surface"):
            self.validate(invalid)

        unused = copy.deepcopy(self.coherence)
        unused["anchors"].append(
            {
                "anchor_id": "A-002",
                "design_ids": ["D-001"],
                "statement": "Unused identity promise",
            }
        )
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "not used"):
            self.validate(unused)

    def test_revision_requires_bounded_impact_queue(self) -> None:
        revision = copy.deepcopy(self.coherence)
        revision["route"] = "revision"
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "nonempty impact_queue"):
            self.validate(revision)

        revision["impact_queue"] = [
            {
                "queue_id": "Q-001",
                "source_design_ids": ["D-001"],
                "target": "SPEC",
                "action": "UPDATE",
                "reason": "The accepted display term changed",
            },
            {
                "queue_id": "Q-002",
                "source_design_ids": ["D-003"],
                "target": "character-identity",
                "action": "PRESERVE",
                "reason": "Keep the rejected future route out of current scope",
            },
        ]
        self.assertEqual((1, 2, 2), self.validate(revision))

        invalid = copy.deepcopy(revision)
        invalid["impact_queue"][0]["target"] = "all-files"
        with self.assertRaisesRegex(coherence_trace.CoherenceTraceError, "invalid target"):
            self.validate(invalid)

    def test_revision_workflow_preserves_decisions_and_reopens_only_impacted_work(self) -> None:
        combined = normalized(self.route + self.design + self.author + self.reference)
        for contract in (
            "impact/re-evaluation queue",
            "update design first",
            "preserve stable ids",
            "reopen only",
            "stable runtime/localization identifiers",
            "full acceptance",
        ):
            self.assertIn(contract, combined)

    def test_scenarios_cover_conflicts_tension_and_revision_delta(self) -> None:
        headings = [
            heading.lower()
            for heading in re.findall(r"^## Case \d+ - (.+)$", self.scenarios, re.MULTILINE)
        ]
        self.assertEqual(
            [
                "event localization contradicts its cost and presentation",
                "character contrast requires one explicit creative decision",
                "temper rename and palette revision propagates narrowly",
            ],
            headings,
        )
        scenarios = normalized(self.scenarios)
        for rubric in (
            "decision authority",
            "adaptive depth",
            "player-facing linkage",
            "specific conflict",
            "creative tension",
            "localization meaning",
            "scope honesty",
            "bounded propagation",
        ):
            self.assertIn(rubric, scenarios)
        self.assertIn("失去20点最大生命", self.scenarios)
        self.assertIn("exact headings and sentences may differ", self.scenarios)
        self.assertIn("do not prove runtime behavior", self.scenarios)


if __name__ == "__main__":
    unittest.main()
