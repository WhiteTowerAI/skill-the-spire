"""Shipped validators must resolve their own data in the *payload* layout, not just the repo.

`publish.sh` moves the tools from `games/sts2/tools/` into `skills/modmaker/scripts/`, which
changes every relative path they use to find the pack. A validator that resolves its data only
in the repo passes every local test and then fails on the first installed project -- the
`spec.md` validation sequence stops, and the failure looks like a broken install rather than a
path bug.

That is exactly what happened: `spec_envelope_trace.py` shipped with a payload candidate of
`skills/surfaces`, missing the `modmaker` segment. It resolved in the repo and in nothing else.

These tests build a throwaway payload-shaped tree and run each validator inside it, so the
resolution logic is checked without depending on the committed payloads being fresh.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = TOOLS_DIR.parent / "skills"

PROBE_SPEC = textwrap.dedent(
    """\
    # SPEC - Probe

    - **contract**: sts2-content-semantic/v2
    - **mod id**: probe
    - **author**: tester
    - **content**:
      - name: Probe
      - surface: power
    - **registration**:
      - availability: shared
    - **localization**:
      - fields: title=Probe
    - **effects**:
      - trigger: play
    - **hook participation**: one
      - capability: modify_damage_multiplicative
        shape: value
        player-facing: probe
        subject: the declaring element's owner
        condition: only the declared owner interaction
        value: 2
        dynamic value name: ProbeValue
        outside the condition: preserve the host value unchanged
    - **state**: none
    - **presentation**:
      - assets: none
    - **fallback**:
      - missing asset: checked template
    - **proof**:
      - scenario: CombatPlayer
    """
)

# A run-scope hook is unreachable on a Power. The payload run must reject it for the same
# reason the repo run does -- proving the catalog resolved, not merely that nothing crashed.
UNREACHABLE_SPEC = PROBE_SPEC.replace(
    "capability: modify_damage_multiplicative", "capability: try_modify_rewards"
).replace("shape: value", "shape: collection")


class PayloadLayoutTests(unittest.TestCase):
    """Run the shipped tools from a payload-shaped tree."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        # The layout publish.sh produces: skills/modmaker/{surfaces,scripts}/ + skills/sts2-api/.
        self.scripts = root / "skills" / "modmaker" / "scripts"
        self.scripts.mkdir(parents=True)
        shutil.copytree(
            SKILLS_DIR / "modmaker" / "surfaces", root / "skills" / "modmaker" / "surfaces"
        )
        shutil.copytree(SKILLS_DIR / "sts2-api", root / "skills" / "sts2-api")
        for tool in (
            "spec_envelope_trace.py",
            "design_trace.py",
            "deliverable_trace.py",
            "repair_trace.py",
        ):
            shutil.copy(TOOLS_DIR / tool, self.scripts / tool)
        self.spec_path = root / "SPEC.md"
        self.design_path = root / "DESIGN.md"
        self.plan_path = root / "PLAN.md"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_envelope_trace(self, spec_text: str) -> subprocess.CompletedProcess:
        self.spec_path.write_text(spec_text, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(self.scripts / "spec_envelope_trace.py"),
                "--spec",
                str(self.spec_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_envelope_trace_resolves_surfaces_and_catalog_in_the_payload(self) -> None:
        result = self.run_envelope_trace(PROBE_SPEC)
        self.assertEqual(
            result.returncode,
            0,
            f"shipped validator failed in the payload layout:\n{result.stdout}{result.stderr}",
        )
        self.assertIn("ok contract=sts2-content-semantic/v2", result.stdout)

    def test_payload_run_still_rejects_an_unreachable_hook(self) -> None:
        """Resolution is not enough: the catalog must actually be read and enforced."""
        result = self.run_envelope_trace(UNREACHABLE_SPEC)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot receive it", result.stderr)

    def test_repair_trace_runs_from_the_payload_layout(self) -> None:
        scope = {
            "contract": "open-mod-design/v1",
            "route": "fast",
            "current_slice": [
                {
                    "design_id": "D-001",
                    "disposition": "MUST",
                    "summary": "one exact probe operation",
                    "support": "confirmed",
                    "spec_operations": ["OP-001"],
                    "reason": "payload layout probe",
                }
            ],
            "future_vision": [],
            "blocking_gaps": [],
        }
        deliverable = {
            "contract": "open-mod-deliverable/v1",
            "route": "fast",
            "claim": "One probe operation.",
            "shape": "one probe",
            "required_experiences": [
                {
                    "experience_id": "E-001",
                    "statement": "The probe operation is observable",
                    "design_ids": ["D-001"],
                    "settled_by": "tier-2-structured",
                }
            ],
            "excluded_experiences": [],
        }
        trace = {
            "contract": "open-mod-spec-trace/v1",
            "design_contract": "open-mod-design/v1",
            "operations": [
                {
                    "operation_id": "OP-001",
                    "design_ids": ["D-001"],
                    "semantic_target": "the probe operation",
                    "supported_route": "recipes/card.md",
                }
            ],
        }
        repair = {
            "contract": "open-mod-repair-routing/v1",
            "active_repair": {
                "trigger_stage": "build",
                "observed_difference": "the package path is wrong",
                "classification": "implementation-equivalent",
                "owning_artifact": "MEMORY.md",
                "affected_design_ids": ["D-001"],
                "affected_experience_ids": [],
                "affected_operation_ids": ["OP-001"],
                "invalidated_stages": ["build", "verify-tier-1", "finalize"],
                "reopened_stage": "build",
                "routing_status": "repairing",
            },
        }
        settlement = {"contract": "open-mod-settlement/v1", "settlements": []}
        self.design_path.write_text(
            "\n".join(
                [
                    "<!-- open-mod-deliverable:v1:start -->",
                    "```json",
                    json.dumps(deliverable),
                    "```",
                    "<!-- open-mod-deliverable:v1:end -->",
                    "<!-- open-mod-scope:v1:start -->",
                    "```json",
                    json.dumps(scope),
                    "```",
                    "<!-- open-mod-scope:v1:end -->",
                ]
            ),
            encoding="utf-8",
        )
        self.spec_path.write_text(
            "\n".join(
                [
                    "<!-- open-mod-trace:v1:start -->",
                    "```json",
                    json.dumps(trace),
                    "```",
                    "<!-- open-mod-trace:v1:end -->",
                ]
            ),
            encoding="utf-8",
        )
        self.plan_path.write_text(
            "\n".join(
                [
                    "<!-- open-mod-repair-routing:v1:start -->",
                    "```json",
                    json.dumps(repair),
                    "```",
                    "<!-- open-mod-repair-routing:v1:end -->",
                    "<!-- open-mod-settlement:v1:start -->",
                    "```json",
                    json.dumps(settlement),
                    "```",
                    "<!-- open-mod-settlement:v1:end -->",
                ]
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(self.scripts / "repair_trace.py"),
                "--design",
                str(self.design_path),
                "--spec",
                str(self.spec_path),
                "--plan",
                str(self.plan_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("state=active classification=implementation-equivalent", result.stdout)


if __name__ == "__main__":
    unittest.main()
