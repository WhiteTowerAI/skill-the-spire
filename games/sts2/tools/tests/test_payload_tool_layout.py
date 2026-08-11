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
        for tool in ("spec_envelope_trace.py", "design_trace.py"):
            shutil.copy(TOOLS_DIR / tool, self.scripts / tool)
        self.spec_path = root / "SPEC.md"

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


if __name__ == "__main__":
    unittest.main()
