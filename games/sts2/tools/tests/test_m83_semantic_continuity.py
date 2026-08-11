"""M8.3 semantic repair routing, scenarios, and shipped workflow integration."""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
SURFACES_DIR = MODMAKER_DIR / "surfaces"
TOOLS_DIR = REPO_ROOT / "games" / "sts2" / "tools"
SCENARIOS_PATH = (
    REPO_ROOT / "games" / "sts2" / "tests" / "m83-semantic-continuity-scenarios.md"
)
sys.path.insert(0, str(TOOLS_DIR))
import deliverable_trace  # noqa: E402
import design_trace  # noqa: E402
import repair_trace  # noqa: E402


SCOPE = {
    "contract": "open-mod-design/v1",
    "route": "fast",
    "current_slice": [
        {
            "design_id": "D-001",
            "disposition": "MUST",
            "summary": "Ember Step deals 9 damage and Exhausts",
            "support": "confirmed",
            "spec_operations": ["OP-001"],
            "reason": "accepted Card behavior",
        },
        {
            "design_id": "D-002",
            "disposition": "PLACEHOLDER",
            "summary": "Use checked placeholder art",
            "support": "placeholder-fallback",
            "spec_operations": ["OP-002"],
            "reason": "accepted fallback",
        },
    ],
    "future_vision": [],
    "blocking_gaps": [],
}

DELIVERABLE = {
    "contract": "open-mod-deliverable/v1",
    "route": "fast",
    "claim": "One playable Attack card that deals 9 damage and Exhausts.",
    "shape": "one Card",
    "required_experiences": [
        {
            "experience_id": "E-001",
            "statement": "Playing Ember Step deals 9 damage and moves it to Exhaust",
            "design_ids": ["D-001"],
            "settled_by": "tier-2-structured",
        },
        {
            "experience_id": "E-002",
            "statement": "The Card uses the accepted placeholder portrait",
            "design_ids": ["D-002"],
            "settled_by": "user-decision",
        },
    ],
    "excluded_experiences": ["No custom portrait art"],
}

SPEC_TRACE = {
    "contract": "open-mod-spec-trace/v1",
    "design_contract": "open-mod-design/v1",
    "operations": [
        {
            "operation_id": "OP-001",
            "design_ids": ["D-001"],
            "semantic_target": "Ember Step damage, Exhaust lifecycle, and text",
            "supported_route": "recipes/card.md",
        },
        {
            "operation_id": "OP-002",
            "design_ids": ["D-002"],
            "semantic_target": "Checked placeholder portrait",
            "supported_route": "reference/art-contract.md#path-root",
        },
    ],
}

CURRENT = {entry["design_id"]: entry for entry in SCOPE["current_slice"]}
OPERATIONS = {entry["operation_id"]: entry for entry in SPEC_TRACE["operations"]}
EXPERIENCES = {
    entry["experience_id"]: entry for entry in DELIVERABLE["required_experiences"]
}


def fulfillment() -> dict:
    return {
        "trigger_stage": "verify-tier-2",
        "observed_difference": "Damage is correct but the Card enters Discard",
        "classification": "contract-fulfillment",
        "owning_artifact": "SPEC.md",
        "affected_design_ids": ["D-001"],
        "affected_experience_ids": ["E-001"],
        "affected_operation_ids": ["OP-001"],
        "invalidated_stages": [
            "author",
            "build",
            "verify-tier-1",
            "verify-tier-2",
            "finalize",
        ],
        "reopened_stage": "author",
        "routing_status": "repairing",
    }


def implementation_equivalent() -> dict:
    active = fulfillment()
    active.update(
        classification="implementation-equivalent",
        owning_artifact="MEMORY.md",
        affected_experience_ids=[],
        invalidated_stages=["build", "verify-tier-1", "verify-tier-2", "finalize"],
        reopened_stage="build",
    )
    return active


def semantic_change() -> dict:
    active = fulfillment()
    active.update(
        classification="accepted-semantic-change",
        owning_artifact="DESIGN.md",
        invalidated_stages=[
            "design",
            "spec",
            "author",
            "build",
            "verify-tier-1",
            "verify-tier-2",
            "finalize",
        ],
        reopened_stage="design",
        routing_status="awaiting-user-acceptance",
    )
    return active


def missing_capability() -> dict:
    active = fulfillment()
    active.update(
        classification="missing-capability",
        owning_artifact="shared recipe/reference",
        invalidated_stages=[],
        reopened_stage=None,
        routing_status="blocked-upstream",
    )
    return active


def validate(active: dict, *, settled: set[str] | None = None) -> str:
    return repair_trace.validate_active_repair(
        active,
        current_design=CURRENT,
        operations=OPERATIONS,
        experiences=EXPERIENCES,
        settled_ids=settled or set(),
    )


def write_design(root: Path, *, scope: dict | None = None) -> Path:
    path = root / "DESIGN.md"
    path.write_text(
        "\n".join(
            [
                "# DESIGN - Ember Step",
                deliverable_trace.DELIVERABLE_START,
                "```json",
                json.dumps(DELIVERABLE, indent=2),
                "```",
                deliverable_trace.DELIVERABLE_END,
                design_trace.DESIGN_START,
                "```json",
                json.dumps(scope if scope is not None else SCOPE, indent=2),
                "```",
                design_trace.DESIGN_END,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_spec(root: Path) -> Path:
    path = root / "SPEC.md"
    path.write_text(
        "\n".join(
            [
                "# SPEC - Ember Step",
                design_trace.SPEC_START,
                "```json",
                json.dumps(SPEC_TRACE, indent=2),
                "```",
                design_trace.SPEC_END,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_plan(
    root: Path,
    *,
    active: dict | None,
    settlements: list[dict] | None = None,
) -> Path:
    path = root / "PLAN.md"
    repair = {"contract": repair_trace.REPAIR_CONTRACT, "active_repair": active}
    settlement = {
        "contract": deliverable_trace.SETTLEMENT_CONTRACT,
        "settlements": settlements or [],
    }
    path.write_text(
        "\n".join(
            [
                "# PLAN - Ember Step",
                repair_trace.REPAIR_START,
                "```json",
                json.dumps(repair, indent=2),
                "```",
                repair_trace.REPAIR_END,
                deliverable_trace.SETTLEMENT_START,
                "```json",
                json.dumps(settlement, indent=2),
                "```",
                deliverable_trace.SETTLEMENT_END,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class RoutingValidationTests(unittest.TestCase):
    def test_all_four_classifications_pass_in_their_valid_state(self) -> None:
        for active in (
            implementation_equivalent(),
            fulfillment(),
            semantic_change(),
            missing_capability(),
        ):
            with self.subTest(classification=active["classification"]):
                self.assertEqual(validate(active), active["classification"])

    def test_classification_owner_and_status_are_closed_combinations(self) -> None:
        active = fulfillment()
        active["owning_artifact"] = "DESIGN.md"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "owned by SPEC.md"):
            validate(active)

        active = fulfillment()
        active["routing_status"] = "awaiting-user-acceptance"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "cannot use"):
            validate(active)

        active = fulfillment()
        active["classification"] = "looks-close-enough"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "classification"):
            validate(active)

    def test_affected_ids_must_exist_and_trace_to_each_other(self) -> None:
        active = fulfillment()
        active["affected_design_ids"] = ["D-999"]
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "not current"):
            validate(active)

        active = fulfillment()
        active["affected_operation_ids"] = ["OP-002"]
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "does not trace"):
            validate(active)

        active = fulfillment()
        active["affected_experience_ids"] = ["E-002"]
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "does not trace"):
            validate(active)

    def test_affected_settlement_must_be_cleared(self) -> None:
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "must be cleared"):
            validate(fulfillment(), settled={"E-001"})

    def test_reopened_stage_is_the_earliest_in_pipeline_order(self) -> None:
        active = fulfillment()
        active["reopened_stage"] = "build"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "earliest"):
            validate(active)

        active = fulfillment()
        active["invalidated_stages"] = ["build", "author", "finalize"]
        active["reopened_stage"] = "build"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "pipeline order"):
            validate(active)

        active = fulfillment()
        active["invalidated_stages"] = ["author", "build", "verify-tier-2"]
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "fresh settlement"):
            validate(active)

    def test_route_specific_reopening_rules_reject_silent_substitution(self) -> None:
        active = implementation_equivalent()
        active["affected_experience_ids"] = ["E-001"]
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "player experiences"):
            validate(active)

        active = semantic_change()
        active["invalidated_stages"] = ["author", "build", "finalize"]
        active["reopened_stage"] = "author"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "DESIGN first"):
            validate(active)

        active = missing_capability()
        active["invalidated_stages"] = ["author", "build"]
        active["reopened_stage"] = "author"
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "blocks upstream"):
            validate(active)


class FileAndResumeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.design = write_design(self.root)
        self.spec = write_spec(self.root)

    def test_active_round_trip_and_finalize_block(self) -> None:
        plan = write_plan(self.root, active=fulfillment())
        self.assertEqual(
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            ),
            ("active", "contract-fulfillment"),
        )
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "Finalize is blocked"):
            repair_trace.validate_files(
                plan,
                design_path=self.design,
                spec_path=self.spec,
                require_clear=True,
            )

    def test_clear_new_plan_can_finalize(self) -> None:
        plan = write_plan(self.root, active=None)
        self.assertEqual(
            repair_trace.validate_files(plan, require_clear=True), ("clear", None)
        )

    def test_legacy_plan_without_block_resumes_unchanged(self) -> None:
        plan = self.root / "LEGACY_PLAN.md"
        plan.write_text("# PLAN - legacy\n- [ ] build\n", encoding="utf-8")
        self.assertEqual(
            repair_trace.validate_files(plan, require_clear=True), ("legacy", None)
        )

    def test_file_validation_rejects_a_stale_affected_settlement(self) -> None:
        plan = write_plan(
            self.root,
            active=fulfillment(),
            settlements=[
                {
                    "experience_id": "E-001",
                    "outcome": "observed",
                    "evidence_kind": "tier-2-structured",
                    "evidence": "proof from the stale build",
                }
            ],
        )
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "must be cleared"):
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            )

    def test_active_cli_requires_design_and_spec(self) -> None:
        plan = write_plan(self.root, active=fulfillment())
        self.assertEqual(repair_trace.main(["--plan", str(plan)]), 2)

    def test_missing_capability_requires_the_project_blocking_gap(self) -> None:
        plan = write_plan(self.root, active=missing_capability())
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "blocking_gaps"):
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            )

        scope = copy.deepcopy(SCOPE)
        scope["blocking_gaps"] = [
            "OP-001 shared route violates its claimed Exhaust lifecycle"
        ]
        write_design(self.root, scope=scope)
        self.assertEqual(
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            ),
            ("active", "missing-capability"),
        )

    def test_semantic_change_may_wait_on_a_gap_but_acceptance_may_not(self) -> None:
        scope = copy.deepcopy(SCOPE)
        scope["blocking_gaps"] = ["User has not accepted the changed result"]
        write_design(self.root, scope=scope)
        plan = write_plan(self.root, active=semantic_change())
        self.assertEqual(
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            ),
            ("active", "accepted-semantic-change"),
        )

        accepted = semantic_change()
        accepted["routing_status"] = "revision-accepted"
        plan = write_plan(self.root, active=accepted)
        with self.assertRaisesRegex(repair_trace.RepairTraceError, "cannot retain"):
            repair_trace.validate_files(
                plan, design_path=self.design, spec_path=self.spec
            )


class MutationAdequacyTests(unittest.TestCase):
    """Each negative fixture becomes accepted only when its owning guard is neutered."""

    @staticmethod
    def mutant(condition: str) -> types.SimpleNamespace:
        source_path = TOOLS_DIR / "repair_trace.py"
        source = source_path.read_text(encoding="utf-8")
        replacement = "if False:"
        if source.count(condition) != 1:
            raise AssertionError(f"mutation target drifted: {condition}")
        namespace = {
            "__name__": "repair_trace_mutant",
            "__file__": str(source_path),
        }
        exec(compile(source.replace(condition, replacement), str(source_path), "exec"), namespace)
        return types.SimpleNamespace(**namespace)

    def assert_mutation_is_load_bearing(
        self,
        active: dict,
        condition: str,
        *,
        settled: set[str] | None = None,
    ) -> None:
        with self.assertRaises(repair_trace.RepairTraceError):
            validate(active, settled=settled)
        mutant = self.mutant(condition)
        result = mutant.validate_active_repair(
            active,
            current_design=CURRENT,
            operations=OPERATIONS,
            experiences=EXPERIENCES,
            settled_ids=settled or set(),
        )
        self.assertEqual(result, active["classification"])

    def test_owner_status_settlement_and_routing_guards_are_load_bearing(self) -> None:
        active = fulfillment()
        active["owning_artifact"] = "DESIGN.md"
        self.assert_mutation_is_load_bearing(
            active, "if owner != CLASS_OWNERS[classification]:"
        )

        active = fulfillment()
        active["routing_status"] = "awaiting-user-acceptance"
        self.assert_mutation_is_load_bearing(
            active, "if status not in CLASS_STATUSES[classification]:"
        )

        self.assert_mutation_is_load_bearing(
            fulfillment(), "if stale:", settled={"E-001"}
        )

        active = fulfillment()
        active["reopened_stage"] = "build"
        self.assert_mutation_is_load_bearing(
            active, "if reopened != invalidated[0]:"
        )

        active = fulfillment()
        active["invalidated_stages"] = ["author", "build", "verify-tier-2"]
        self.assert_mutation_is_load_bearing(
            active,
            'if (\n        experience_ids\n        and classification != "missing-capability"\n        and "finalize" not in invalidated\n    ):',
        )

        active = semantic_change()
        active["invalidated_stages"] = ["author", "build", "finalize"]
        active["reopened_stage"] = "author"
        self.assert_mutation_is_load_bearing(
            active,
            'if classification == "accepted-semantic-change" and reopened != "design":',
        )

        active = missing_capability()
        active["invalidated_stages"] = ["author", "build"]
        active["reopened_stage"] = "author"
        self.assert_mutation_is_load_bearing(
            active, "if invalidated or reopened is not None:"
        )


class ShippedContractTests(unittest.TestCase):
    def test_all_fifteen_scenarios_name_the_required_routing_fields(self) -> None:
        text = SCENARIOS_PATH.read_text(encoding="utf-8")
        matches = list(re.finditer(r"^## Case ([0-9]+) - .+$", text, re.MULTILINE))
        self.assertEqual([int(match.group(1)) for match in matches], list(range(1, 16)))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section = text[match.start() : end]
            for label in ("Classification", "Owner", "Reopen", "Ask", "Stop/resume"):
                with self.subTest(case=index + 1, label=label):
                    self.assertIn(f"**{label}:**", section)

    def test_complete_operation_view_exists_on_all_ten_surfaces(self) -> None:
        expected = {
            "card.md",
            "character.md",
            "enchantment.md",
            "event.md",
            "keyword.md",
            "monster.md",
            "orb.md",
            "potion.md",
            "power.md",
            "relic.md",
        }
        actual = {path.name for path in SURFACES_DIR.glob("*.md")}
        self.assertEqual(actual, expected)
        for path in SURFACES_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(surface=path.name):
                self.assertIn("## proof matrix", text)
                self.assertIn("driver", text)

    def test_discovery_points_classify_before_fix_and_finalize_blocks(self) -> None:
        for name in ("author.md", "build.md", "verify.md", "repair.md"):
            text = (MODMAKER_DIR / name).read_text(encoding="utf-8").lower()
            with self.subTest(file=name):
                self.assertIn("classif", text)
                self.assertIn("repair_trace.py", text)
        verify = (MODMAKER_DIR / "verify.md").read_text(encoding="utf-8")
        self.assertIn("repair_trace.py --design DESIGN.md --spec SPEC.md --plan PLAN.md --finalize", verify)

    def test_plan_template_and_state_check_resume_active_repair(self) -> None:
        spec = (MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")
        skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8").lower()
        self.assertIn(repair_trace.REPAIR_START, spec)
        self.assertIn('"active_repair": null', spec)
        self.assertIn("active `open-mod-repair-routing/v1`", skill)
        self.assertIn("active `open-mod-repair-routing/v1`", route)

    def test_inv5_fires_through_finalize_and_inv10_is_separate(self) -> None:
        text = (MODMAKER_DIR / "invariants.md").read_text(encoding="utf-8")
        inv5 = text.split("## INV-5", 1)[1].split("## INV-6", 1)[0].lower()
        for stage in ("author", "verify", "repair", "finalize"):
            self.assertIn(stage, inv5)
        self.assertNotIn("localization", inv5)
        self.assertIn("## INV-10 — Player-facing localization is bilingual", text)


if __name__ == "__main__":
    unittest.main()
