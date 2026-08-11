"""Route pointers must resolve, and a claimed capability must be one the route declares.

M8.2 preflight. `design_trace.py` used to split a `supported_route` on `#` and check only the
file half, so an operation could cite `reference/art-contract.md#placeholder` -- an anchor that
has never existed in that file -- and pass. That exact pointer shipped as the canonical example
in `spec.md`, so every generated project copied it. A pointer that does not resolve is worse
than no pointer: it reads as grounding while landing nowhere.

The capability half is the other direction. A route file existing does not mean it documents
the semantics the operation needs; Watcher's Wrath cited a real recipe that simply had no
multiplier line. `capability_ids` lets an operation name what it consumes and the route page
declare what it provides, so the pairing is checkable rather than assumed.

Both checks are additive: an operation with no fragment and no `capability_ids` validates
exactly as it did before, which is what keeps a pre-M8.2 project resuming unchanged.

What these tests do not establish: that a route's documented capability is *correct*, or that
generated code honors it. That is step 5's conformance rule and a real-host proof.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import design_trace  # noqa: E402


DESIGN = {
    "contract": "open-mod-design/v1",
    "route": "fast",
    "current_slice": [
        {
            "design_id": "D-001",
            "disposition": "MUST",
            "summary": "one Attack card",
            "support": "confirmed",
            "spec_operations": ["OP-001"],
            "reason": "the user asked for it",
        }
    ],
    "future_vision": [],
    "blocking_gaps": [],
}

SPEC = {
    "contract": "open-mod-spec-trace/v1",
    "design_contract": "open-mod-design/v1",
    "operations": [
        {
            "operation_id": "OP-001",
            "design_ids": ["D-001"],
            "semantic_target": "Card Ember Step: registration and exact play effect",
            "supported_route": "recipes/card.md",
        }
    ],
}


def write_pair(directory: Path, design: dict, spec: dict) -> tuple[Path, Path]:
    design_path = directory / "DESIGN.md"
    spec_path = directory / "SPEC.md"
    design_path.write_text(
        "# DESIGN\n\n"
        f"{design_trace.DESIGN_START}\n```json\n{json.dumps(design)}\n```\n"
        f"{design_trace.DESIGN_END}\n",
        encoding="utf-8",
    )
    spec_path.write_text(
        "# SPEC\n\n"
        f"{design_trace.SPEC_START}\n```json\n{json.dumps(spec)}\n```\n"
        f"{design_trace.SPEC_END}\n",
        encoding="utf-8",
    )
    return design_path, spec_path


class HeadingSlugTests(unittest.TestCase):
    def test_slugs_follow_github_style(self) -> None:
        text = "# Top level\n## Path root\n### The contract — the ONE card portrait\n"
        slugs = design_trace.heading_slugs(text)
        self.assertIn("top-level", slugs)
        self.assertIn("path-root", slugs)
        self.assertIn("the-contract--the-one-card-portrait", slugs)

    def test_shipped_example_anchor_resolves(self) -> None:
        """The example in `spec.md` is what every project copies, so it must resolve."""
        spec_page = (
            TOOLS_DIR.parent / "skills" / "modmaker" / "spec.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn(
            "art-contract.md#placeholder",
            spec_page,
            "the dangling anchor returned to the shipped example",
        )


class DeclaredCapabilityTests(unittest.TestCase):
    def test_parses_comma_and_space_separated_ids(self) -> None:
        self.assertEqual(
            {"modify_damage_multiplicative", "modify_damage_additive"},
            design_trace.declared_capabilities(
                "<!-- openmod-capabilities: modify_damage_multiplicative, "
                "modify_damage_additive -->"
            ),
        )

    def test_absent_declaration_is_an_empty_set(self) -> None:
        self.assertEqual(set(), design_trace.declared_capabilities("# just a page\n"))


class RouteValidationTests(unittest.TestCase):
    def validate(self, spec: dict) -> None:
        with tempfile.TemporaryDirectory() as raw:
            design_path, spec_path = write_pair(Path(raw), DESIGN, spec)
            design_trace.validate_files(design_path, spec_path)

    def test_route_without_a_fragment_passes(self) -> None:
        self.validate(SPEC)

    def test_resolving_anchor_passes(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["supported_route"] = "reference/art-contract.md#path-root"
        self.validate(spec)

    def test_invented_anchor_fails(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["supported_route"] = (
            "reference/art-contract.md#invented-anchor"
        )
        with self.assertRaises(design_trace.DesignTraceError) as caught:
            self.validate(spec)
        self.assertIn("anchor does not exist", str(caught.exception))
        self.assertIn("invented-anchor", str(caught.exception))

    def test_missing_route_file_still_fails(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["supported_route"] = "recipes/not-a-real-route.md"
        with self.assertRaises(design_trace.DesignTraceError):
            self.validate(spec)


class CapabilityPairingTests(unittest.TestCase):
    """An operation may claim only a capability its route page declares."""

    def validate(self, spec: dict) -> None:
        with tempfile.TemporaryDirectory() as raw:
            design_path, spec_path = write_pair(Path(raw), DESIGN, spec)
            design_trace.validate_files(design_path, spec_path)

    def test_operation_without_capability_ids_passes(self) -> None:
        """Additive: a pre-M8.2 operation is unchanged by this check."""
        self.validate(SPEC)

    def test_undeclared_capability_fails(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["capability_ids"] = ["not_a_declared_capability"]
        with self.assertRaises(design_trace.DesignTraceError) as caught:
            self.validate(spec)
        message = str(caught.exception)
        self.assertIn("not_a_declared_capability", message)
        self.assertIn("does not declare", message)

    def test_empty_capability_list_is_rejected_rather_than_ignored(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["capability_ids"] = []
        with self.assertRaises(design_trace.DesignTraceError) as caught:
            self.validate(spec)
        self.assertIn("empty capability_ids", str(caught.exception))

    def test_malformed_capability_id_is_rejected(self) -> None:
        spec = copy.deepcopy(SPEC)
        spec["operations"][0]["capability_ids"] = ["ModifyDamageMultiplicative"]
        with self.assertRaises(design_trace.DesignTraceError) as caught:
            self.validate(spec)
        self.assertIn("invalid capability id", str(caught.exception))

    def test_declared_capability_on_a_real_route_passes(self) -> None:
        """Uses whichever shipped route declares capabilities, so the pair is end-to-end."""
        route_root = TOOLS_DIR.parent / "skills" / "sts2-api"
        for page in sorted(route_root.rglob("*.md")):
            declared = design_trace.declared_capabilities(
                page.read_text(encoding="utf-8")
            )
            if not declared:
                continue
            spec = copy.deepcopy(SPEC)
            spec["operations"][0]["supported_route"] = page.relative_to(
                route_root
            ).as_posix()
            spec["operations"][0]["capability_ids"] = [sorted(declared)[0]]
            self.validate(spec)
            return
        self.skipTest("no shipped route declares capabilities yet")


if __name__ == "__main__":
    unittest.main()
