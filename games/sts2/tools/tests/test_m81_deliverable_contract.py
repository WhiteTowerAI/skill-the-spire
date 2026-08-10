"""M8.1 literal deliverable contract: validator behavior and shipped-prose contract.

Two halves. The validator cases pin the decisions that make the ledger worth having —
an outcome may not outrun its evidence type, every required experience must be settled,
and `shape` is free text rather than a closed taxonomy. The prose cases pin that the
shipped pack actually asks for a claim before SPEC and reports from the ledger at the end.

Neither half proves a generated Mod behaves correctly. They prove the workflow cannot
report more than it earned without failing a check.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

import skill_prose


REPO_ROOT = Path(__file__).resolve().parents[4]
MODMAKER_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "modmaker"
TOOLS_DIR = REPO_ROOT / "games" / "sts2" / "tools"
SCENARIOS_PATH = (
    REPO_ROOT / "games" / "sts2" / "tests" / "m81-deliverable-contract-scenarios.md"
)
sys.path.insert(0, str(TOOLS_DIR))
import deliverable_trace  # noqa: E402
import design_trace  # noqa: E402


def normalized(text: str) -> str:
    return " ".join(text.split()).lower()


DELIVERABLE = {
    "contract": "open-mod-deliverable/v1",
    "route": "fast",
    "claim": "One playable Attack card you can add to a run and play in combat for 9 damage.",
    "shape": "one Card",
    "required_experiences": [
        {
            "experience_id": "E-001",
            "statement": "Playing Ember Step deals 9 damage, 12 upgraded",
            "design_ids": ["D-001"],
            "settled_by": "tier-2-structured",
        },
        {
            "experience_id": "E-002",
            "statement": "The card shows the template placeholder portrait",
            "design_ids": ["D-002"],
            "settled_by": "user-decision",
        },
    ],
    "excluded_experiences": ["No custom portrait art in this deliverable"],
}

SETTLEMENT = {
    "contract": "open-mod-settlement/v1",
    "settlements": [
        {
            "experience_id": "E-001",
            "outcome": "observed",
            "evidence_kind": "tier-2-structured",
            "evidence": "state proof: card damage expected=9 observed=9",
        },
        {
            "experience_id": "E-002",
            "outcome": "observed",
            "evidence_kind": "user-decision",
            "evidence": "accepted at the combined confirmation",
        },
    ],
}

CURRENT_IDS = {"D-001", "D-002"}


def experiences(data: dict) -> dict:
    return {entry["experience_id"]: entry for entry in data["required_experiences"]}


class DeliverableClaimTests(unittest.TestCase):
    def test_valid_claim_passes(self) -> None:
        count, excluded = deliverable_trace.validate_deliverable(
            copy.deepcopy(DELIVERABLE), current_design_ids=CURRENT_IDS
        )
        self.assertEqual((count, excluded), (2, 1))

    def test_claim_and_shape_are_required(self) -> None:
        for field in ("claim", "shape"):
            data = copy.deepcopy(DELIVERABLE)
            data[field] = "   "
            with self.assertRaises(deliverable_trace.DeliverableTraceError):
                deliverable_trace.validate_deliverable(
                    data, current_design_ids=CURRENT_IDS
                )

    def test_shape_is_free_text_not_a_taxonomy(self) -> None:
        """The lead's decision: prototype/slice/run-capable are descriptions.

        A validator that accepted only known words would turn an optional description
        into the closed taxonomy M8.1 explicitly refuses to create.
        """
        for shape in (
            "one Card",
            "nine-Card evaluable slice",
            "run-capable Character",
            "a weird little half-finished experiment",
            "两张卡的试验",
        ):
            data = copy.deepcopy(DELIVERABLE)
            data["shape"] = shape
            count, _ = deliverable_trace.validate_deliverable(
                data, current_design_ids=CURRENT_IDS
            )
            self.assertEqual(count, 2, shape)

    def test_experience_must_trace_to_a_current_design_item(self) -> None:
        data = copy.deepcopy(DELIVERABLE)
        data["required_experiences"][0]["design_ids"] = ["D-009"]
        with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
            deliverable_trace.validate_deliverable(data, current_design_ids=CURRENT_IDS)
        self.assertIn("non-current", str(ctx.exception))

    def test_unknown_settled_by_is_rejected(self) -> None:
        data = copy.deepcopy(DELIVERABLE)
        data["required_experiences"][0]["settled_by"] = "looks-fine"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_deliverable(data, current_design_ids=CURRENT_IDS)

    def test_duplicate_and_malformed_experience_ids_are_rejected(self) -> None:
        data = copy.deepcopy(DELIVERABLE)
        data["required_experiences"][1]["experience_id"] = "E-001"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_deliverable(data, current_design_ids=CURRENT_IDS)

        data = copy.deepcopy(DELIVERABLE)
        data["required_experiences"][0]["experience_id"] = "E-1"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_deliverable(data, current_design_ids=CURRENT_IDS)

    def test_required_experiences_cannot_be_empty(self) -> None:
        data = copy.deepcopy(DELIVERABLE)
        data["required_experiences"] = []
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_deliverable(data, current_design_ids=CURRENT_IDS)

    def test_settled_by_covers_exactly_the_four_documented_methods(self) -> None:
        self.assertEqual(
            deliverable_trace.SETTLED_BY,
            {"tier-2-structured", "tier-1-load", "headed-human", "user-decision"},
        )


class SettlementLedgerTests(unittest.TestCase):
    def test_fully_earned_claim_passes(self) -> None:
        settled, observed = deliverable_trace.validate_settlement(
            copy.deepcopy(SETTLEMENT), experiences=experiences(DELIVERABLE)
        )
        self.assertEqual((settled, observed), (2, 2))

    def test_tier2_experience_cannot_be_observed_on_tier1_evidence(self) -> None:
        """The Watcher overclaim, generalized.

        A closing narrative called a mechanic verified while the same record disclosed
        the harness never drove it. Tier-1 passing is not evidence for a tier-2 claim.
        """
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][0]["evidence_kind"] = "tier-1-load"
        with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )
        message = str(ctx.exception)
        self.assertIn("E-001", message)
        self.assertIn("tier-2-structured", message)

    def test_headed_human_experience_cannot_be_observed_by_a_harness(self) -> None:
        claim = copy.deepcopy(DELIVERABLE)
        claim["required_experiences"][1]["settled_by"] = "headed-human"
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][1]["evidence_kind"] = "tier-2-structured"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_settlement(data, experiences=experiences(claim))

    def test_user_decision_is_not_satisfied_by_observation_evidence(self) -> None:
        """Acceptance and observation are different facts (INV-4).

        A `user-decision` experience records that the user accepted a stated difference.
        A harness proof does not establish that they accepted anything.
        """
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][1]["evidence_kind"] = "tier-2-structured"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )

    def test_tier1_experience_accepts_the_stronger_tier2_evidence(self) -> None:
        claim = copy.deepcopy(DELIVERABLE)
        claim["required_experiences"][0]["settled_by"] = "tier-1-load"
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][0]["evidence_kind"] = "tier-2-structured"
        settled, observed = deliverable_trace.validate_settlement(
            data, experiences=experiences(claim)
        )
        self.assertEqual((settled, observed), (2, 2))

    def test_every_required_experience_needs_a_settlement(self) -> None:
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"] = data["settlements"][:1]
        with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )
        self.assertIn("E-002", str(ctx.exception))

    def test_settling_an_unclaimed_experience_is_rejected(self) -> None:
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"].append(
            {
                "experience_id": "E-003",
                "outcome": "observed",
                "evidence_kind": "tier-2-structured",
                "evidence": "state proof for something nobody promised",
            }
        )
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )

    def test_unobserved_and_exception_require_a_note(self) -> None:
        for outcome in ("unobserved", "exception"):
            data = copy.deepcopy(SETTLEMENT)
            data["settlements"][0] = {
                "experience_id": "E-001",
                "outcome": outcome,
                "evidence": "harness reached combat",
            }
            with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
                deliverable_trace.validate_settlement(
                    data, experiences=experiences(DELIVERABLE)
                )
            self.assertIn("note", str(ctx.exception))

    def test_unobserved_with_a_note_is_a_valid_honest_outcome(self) -> None:
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][0] = {
            "experience_id": "E-001",
            "outcome": "unobserved",
            "evidence": "selftest done, no matching state proof line",
            "note": "the structured damage proof for this Card is absent from the log",
        }
        settled, observed = deliverable_trace.validate_settlement(
            data, experiences=experiences(DELIVERABLE)
        )
        self.assertEqual((settled, observed), (2, 1))

    def test_unknown_outcome_is_rejected(self) -> None:
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"][0]["outcome"] = "probably fine"
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )

    def test_duplicate_settlement_for_one_experience_is_rejected(self) -> None:
        data = copy.deepcopy(SETTLEMENT)
        data["settlements"].append(copy.deepcopy(data["settlements"][0]))
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_settlement(
                data, experiences=experiences(DELIVERABLE)
            )


SCOPE_BLOCK = {
    "contract": "open-mod-design/v1",
    "route": "fast",
    "current_slice": [
        {
            "design_id": "D-001",
            "disposition": "MUST",
            "summary": "1-Energy Common Attack dealing 9 damage, 12 upgraded",
            "support": "confirmed",
            "spec_operations": ["OP-001"],
            "reason": "The exact requested Card",
        },
        {
            "design_id": "D-002",
            "disposition": "PLACEHOLDER",
            "summary": "Use the checked template art fallback",
            "support": "placeholder-fallback",
            "spec_operations": ["OP-002"],
            "reason": "Custom art was not requested",
        },
    ],
    "future_vision": [],
    "blocking_gaps": [],
}


def write_design(directory: Path, *, deliverable=None, scope=None) -> Path:
    path = directory / "DESIGN.md"
    parts = [
        "# DESIGN - Ember Step\n",
        deliverable_trace.DELIVERABLE_START,
        "```json",
        json.dumps(deliverable if deliverable is not None else DELIVERABLE, indent=2),
        "```",
        deliverable_trace.DELIVERABLE_END,
        "",
        design_trace.DESIGN_START,
        "```json",
        json.dumps(scope if scope is not None else SCOPE_BLOCK, indent=2),
        "```",
        design_trace.DESIGN_END,
        "",
    ]
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def write_plan(directory: Path, settlement=None) -> Path:
    path = directory / "PLAN.md"
    path.write_text(
        "\n".join(
            [
                "# PLAN - Ember Step\n",
                deliverable_trace.SETTLEMENT_START,
                "```json",
                json.dumps(
                    settlement if settlement is not None else SETTLEMENT, indent=2
                ),
                "```",
                deliverable_trace.SETTLEMENT_END,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class FileRoundTripTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_pre_spec_and_finalize_modes_both_pass(self) -> None:
        design = write_design(self.dir)
        plan = write_plan(self.dir)
        self.assertEqual(deliverable_trace.validate_design_file(design), (2, 1))
        self.assertEqual(deliverable_trace.validate_finalize(design, plan), (2, 2))

    def test_absent_block_is_detectable_for_pre_m81_resume(self) -> None:
        """Why the claim is its own block rather than a scope field.

        An absent block is an unambiguous "predates M8.1" signal, the same way an absent
        coherence block signals pre-M7.5. A missing key inside the scope block could not
        be told apart from an author who forgot it.
        """
        path = self.dir / "OLD.md"
        path.write_text(
            "\n".join(
                [
                    "# DESIGN - legacy",
                    design_trace.DESIGN_START,
                    "```json",
                    json.dumps(SCOPE_BLOCK, indent=2),
                    "```",
                    design_trace.DESIGN_END,
                ]
            ),
            encoding="utf-8",
        )
        text = path.read_text(encoding="utf-8")
        self.assertFalse(deliverable_trace.has_deliverable_block(text))
        self.assertTrue(
            deliverable_trace.has_deliverable_block(
                write_design(self.dir).read_text(encoding="utf-8")
            )
        )

    def test_route_must_match_the_scope_route(self) -> None:
        deliverable = copy.deepcopy(DELIVERABLE)
        deliverable["route"] = "co-design"
        design = write_design(self.dir, deliverable=deliverable)
        with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
            deliverable_trace.validate_design_file(design)
        self.assertIn("route", str(ctx.exception))

    def test_blocking_gaps_stop_the_claim_from_validating(self) -> None:
        scope = copy.deepcopy(SCOPE_BLOCK)
        scope["blocking_gaps"] = ["Momentum cannot replace Energy on the pinned profile"]
        design = write_design(self.dir, scope=scope)
        with self.assertRaises(deliverable_trace.DeliverableTraceError) as ctx:
            deliverable_trace.validate_design_file(design)
        self.assertIn("blocking_gaps", str(ctx.exception))

    def test_deferred_design_item_cannot_carry_a_required_experience(self) -> None:
        scope = copy.deepcopy(SCOPE_BLOCK)
        scope["future_vision"] = [
            {
                "design_id": "D-003",
                "disposition": "DEFER",
                "summary": "Full card pool",
                "support": "not-current",
                "spec_operations": [],
                "reason": "Later",
            }
        ]
        deliverable = copy.deepcopy(DELIVERABLE)
        deliverable["required_experiences"][0]["design_ids"] = ["D-003"]
        design = write_design(self.dir, deliverable=deliverable, scope=scope)
        with self.assertRaises(deliverable_trace.DeliverableTraceError):
            deliverable_trace.validate_design_file(design)

    def test_cli_exit_codes(self) -> None:
        design = write_design(self.dir)
        plan = write_plan(self.dir)
        self.assertEqual(
            deliverable_trace.main(["--design", str(design)]),
            0,
        )
        self.assertEqual(
            deliverable_trace.main(["--design", str(design), "--plan", str(plan)]),
            0,
        )
        broken = copy.deepcopy(SETTLEMENT)
        broken["settlements"][0]["evidence_kind"] = "tier-1-load"
        bad_plan = write_plan(self.dir, broken)
        self.assertEqual(
            deliverable_trace.main(["--design", str(design), "--plan", str(bad_plan)]),
            2,
        )


class ShippedPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (MODMAKER_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.route = (MODMAKER_DIR / "route.md").read_text(encoding="utf-8")
        cls.interview = (MODMAKER_DIR / "interview.md").read_text(encoding="utf-8")
        cls.design = (MODMAKER_DIR / "design.md").read_text(encoding="utf-8")
        cls.repair = (MODMAKER_DIR / "repair.md").read_text(encoding="utf-8")
        cls.spec = skill_prose.stage("spec")
        cls.verify = skill_prose.stage("verify")
        cls.scenarios = SCENARIOS_PATH.read_text(encoding="utf-8")

    def test_design_stage_owns_the_claim_block(self) -> None:
        self.assertIn(deliverable_trace.DELIVERABLE_START, self.design)
        self.assertIn(deliverable_trace.DELIVERABLE_END, self.design)
        block = deliverable_trace._extract_json_block(
            self.design,
            deliverable_trace.DELIVERABLE_START,
            deliverable_trace.DELIVERABLE_END,
            "design.md",
        )
        # The shipped example must itself satisfy the validator, or the pack teaches a
        # shape that fails the moment an author copies it.
        deliverable_trace.validate_deliverable(block, current_design_ids={"D-001", "D-002"})

    def test_design_documents_all_four_settlement_methods(self) -> None:
        for method in sorted(deliverable_trace.SETTLED_BY):
            self.assertIn(method, self.design, method)

    def test_design_states_experience_is_not_requirement_or_operation(self) -> None:
        text = normalized(self.design)
        self.assertIn("an experience is not a requirement and not an operation", text)

    def test_design_keeps_shape_free_text(self) -> None:
        text = normalized(self.design)
        self.assertIn("this is a **description, not a category.**".lower(), text)
        self.assertIn("there is no fixed list", text)

    def test_user_decision_is_marked_as_acceptance_not_observation(self) -> None:
        text = normalized(self.design)
        self.assertIn("is **not** evidence of observation".lower(), text)

    def test_claim_precedes_spec_in_the_pipeline(self) -> None:
        design_index = self.skill.index("3. DESIGN (design.md)")
        spec_index = self.skill.index("4. SPEC (semantic-contract.md + spec.md)")
        self.assertLess(design_index, spec_index)
        self.assertIn("literal deliverable claim", self.skill)

    def test_both_stages_run_the_validator_before_spec(self) -> None:
        for corpus in (self.design, self.spec):
            self.assertIn("deliverable_trace.py --design DESIGN.md", corpus)

    def test_finalize_runs_the_settlement_mode_and_reports_from_the_ledger(self) -> None:
        self.assertIn(
            "deliverable_trace.py --design DESIGN.md --plan PLAN.md", self.verify
        )
        text = normalized(self.verify)
        self.assertIn("settle the deliverable claim first", text)
        self.assertIn("report from the ledger", text)

    def test_finalize_forbids_outrunning_the_evidence(self) -> None:
        text = normalized(self.verify)
        self.assertIn(
            "a `tier-2-structured` experience is not `observed` because tier-1 passed".lower(),
            text,
        )
        self.assertIn("what it may never become is silence", text)

    def test_plan_seeds_an_empty_ledger(self) -> None:
        self.assertIn(deliverable_trace.SETTLEMENT_START, self.spec)
        self.assertIn('"settlements": []', self.spec)
        self.assertIn("seed the ledger empty", normalized(self.spec))

    def test_confirmation_leads_with_the_claim(self) -> None:
        text = normalized(self.spec)
        self.assertIn("lead with the deliverable claim in one sentence", text)

    def test_routing_carries_a_deliverable_signal_without_asking(self) -> None:
        self.assertIn("deliverable signals:", self.route)
        self.assertIn("deliverable signals:", self.interview)
        self.assertIn("is observation, not a new question", self.route)
        self.assertIn("Never ask for the deliverable claim", self.interview)

    def test_repair_clears_stale_settlements_without_owning_backtracking(self) -> None:
        text = normalized(self.repair)
        self.assertIn("must not leave `plan.md`'s settlement", text)
        self.assertIn("is not decided here", text)

    def test_resume_compatibility_is_stated_for_projects_without_a_claim(self) -> None:
        text = normalized(self.design)
        self.assertIn(
            "has no `open-mod-deliverable:v1` block predates the deliverable".lower(), text
        )
        self.assertIn("never as `observed`".lower(), text)

    def test_no_ninth_invariant_was_added(self) -> None:
        """The claim-versus-report rule fires at one stage, so it stays in verify.md.

        `invariants.md` holds only rules that fire at every stage; the repair attempt cap
        and the art-consent boundary already set the precedent for leaving a single-stage
        rule where it fires.
        """
        invariants = skill_prose.read(skill_prose.INVARIANTS_PAGE)
        self.assertNotIn("INV-9", invariants)
        self.assertIn("## INV-8", invariants)

    def test_scenarios_cover_the_three_documented_cases(self) -> None:
        for heading in (
            "## Case 1 - exact Card keeps a one-line claim",
            "## Case 2 - Character content set names its slice and its exclusions",
            "## Case 3 - the harness never drove it, so the report may not claim it",
        ):
            self.assertIn(heading, self.scenarios)

    def test_scenarios_state_the_package_scope_boundary(self) -> None:
        text = normalized(self.scenarios)
        self.assertIn("does not check that", text)
        self.assertIn("does not widen the capability graph", text)


if __name__ == "__main__":
    unittest.main()
