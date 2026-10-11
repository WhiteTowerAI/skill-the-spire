from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import capability_preflight as preflight  # noqa: E402


def spec(*lines: str) -> str:
    return "# SPEC\n\n## Implementation\n\n" + "\n".join(lines) + "\n\n## Autotest\n"


class CapabilityPreflightTests(unittest.TestCase):
    def test_real_recipe_and_reference_routes_pass(self) -> None:
        self.assertEqual(
            (2, 0, False),
            preflight.validate_spec_text(
                spec(
                    "- Support: `recipes/card.md`",
                    "- Support: reference/card-computed-values.md",
                )
            ),
        )

    def test_missing_route_fails(self) -> None:
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(spec("- Support: recipes/not-real.md"))
        self.assertIn("does not exist", str(caught.exception))

    def test_mod_local_route_line_is_ignored_beside_maintained_routes(self) -> None:
        self.assertEqual(
            (1, 0, False),
            preflight.validate_spec_text(
                spec(
                    "- Support: recipes/card.md",
                    "- Mod-local: example operation - ExampleOwner.ExampleMember",
                )
            ),
        )

    def test_markdown_anchor_is_not_a_preflight_contract(self) -> None:
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(spec("- Support: recipes/card.md#some-heading"))
        self.assertIn("not a Markdown anchor", str(caught.exception))

    def test_declarations_do_not_depend_on_a_markdown_heading(self) -> None:
        self.assertEqual(
            (1, 0, False),
            preflight.validate_spec_text("# Work order\n\n- Support: recipes/card.md\n"),
        )

    def test_reachable_hook_passes(self) -> None:
        text = spec(
            "- Hook: modify_damage_multiplicative | surface: power | shape: value | "
            "route: reference/model-hook-participation.md"
        )
        self.assertEqual((0, 1, False), preflight.validate_spec_text(text))

    def test_unknown_hook_fails(self) -> None:
        text = spec(
            "- Hook: modify_nonexistent_thing | surface: power | shape: value | "
            "route: reference/model-hook-participation.md"
        )
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(text)
        self.assertIn("not in", str(caught.exception))

    def test_unreachable_hook_fails(self) -> None:
        catalog = json.loads(preflight.hook_catalog_path().read_text(encoding="utf-8"))
        hook = next(
            entry
            for entry in catalog["hooks"]
            if "power" not in entry["authorable_surfaces"]
            and not entry.get("owned_by_route")
            and not entry.get("enchantment_redirect")
        )
        shape = preflight.SHAPES[hook["declaration_shape"]]
        text = spec(
            f"- Hook: {hook['semantic_id']} | surface: power | shape: {shape} | "
            "route: reference/model-hook-participation.md"
        )
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(text)
        self.assertIn("cannot reach", str(caught.exception))

    def test_wrong_hook_shape_fails(self) -> None:
        text = spec(
            "- Hook: modify_damage_multiplicative | surface: power | shape: collection | "
            "route: reference/model-hook-participation.md"
        )
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(text)
        self.assertIn("catalog requires 'value'", str(caught.exception))

    def test_route_owned_hook_fails(self) -> None:
        catalog = json.loads(preflight.hook_catalog_path().read_text(encoding="utf-8"))
        hook = next(entry for entry in catalog["hooks"] if entry.get("owned_by_route"))
        shape = preflight.SHAPES[hook["declaration_shape"]]
        text = spec(
            f"- Hook: {hook['semantic_id']} | surface: {hook['authorable_surfaces'][0]} | "
            f"shape: {shape} | route: reference/model-hook-participation.md"
        )
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(text)
        self.assertIn("owned by", str(caught.exception))

    def test_hook_route_must_declare_the_capability(self) -> None:
        text = spec(
            "- Hook: modify_damage_multiplicative | surface: power | shape: value | "
            "route: recipes/power.md"
        )
        with self.assertRaises(preflight.CapabilityPreflightError) as caught:
            preflight.validate_spec_text(text)
        self.assertIn("does not declare", str(caught.exception))

    def test_legacy_spec_is_skipped_without_rewrite(self) -> None:
        self.assertEqual((0, 0, True), preflight.validate_spec_text("# Old SPEC\n\n- card: x\n"))

    def test_cli_runs_against_payload_layout_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "SPEC.md"
            path.write_text(spec("- Support: recipes/card.md"), encoding="utf-8")
            self.assertEqual(0, preflight.main(["--spec", str(path)]))


if __name__ == "__main__":
    unittest.main()
