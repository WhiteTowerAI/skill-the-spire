"""Protect the hard model-hook boundary that compilation cannot detect."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import capability_preflight as preflight  # noqa: E402


SKILLS_DIR = TOOLS_DIR.parent / "skills"
CATALOG_PATH = (
    SKILLS_DIR
    / "sts2api"
    / "reference"
    / "catalogs"
    / "model-hooks-sts2-0.107.1.json"
)
ROUTE_PAGE = SKILLS_DIR / "sts2api" / "reference" / "model-hook-participation.md"
AUTHORABLE_SURFACES = (
    "affliction",
    "card",
    "enchantment",
    "global-effect-run",
    "global-effect-combat",
    "modifier",
    "monster",
    "orb",
    "potion",
    "power",
    "relic",
)


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def expected_capability_ids() -> set[str]:
    ids: set[str] = set()
    for hook in catalog()["hooks"]:
        if hook.get("owned_by_route"):
            continue
        ids.add(hook["semantic_id"])
        if hook.get("enchantment_redirect"):
            ids.add(snake(hook["enchantment_redirect"]))
    return ids


def hook_spec(capability: str, surface: str, shape: str) -> str:
    return (
        "# SPEC - Hook Probe\n\n"
        "## Implementation\n\n"
        f"- Hook: {capability} | surface: {surface} | shape: {shape} | "
        "route: reference/model-hook-participation.md\n\n"
        "## Autotest\n\n"
        "- Drive the real host path and assert the modified and neutral cases.\n"
    )


class HookCatalogProjectionTests(unittest.TestCase):
    def test_route_declarations_equal_catalog_authorable_set(self) -> None:
        declared = preflight.declared_capabilities(ROUTE_PAGE.read_text(encoding="utf-8"))
        expected = expected_capability_ids()
        self.assertEqual(
            expected,
            declared,
            f"route-only={sorted(declared - expected)} catalog-only={sorted(expected - declared)}",
        )

    def test_route_owned_rest_site_hooks_are_not_raw_capabilities(self) -> None:
        declared = preflight.declared_capabilities(ROUTE_PAGE.read_text(encoding="utf-8"))
        owned = [hook for hook in catalog()["hooks"] if hook.get("owned_by_route")]
        self.assertEqual(2, len(owned))
        for hook in owned:
            self.assertNotIn(hook["semantic_id"], declared)
            self.assertIn("rest-site-options.md", hook["owned_by_route"])

    def test_every_catalog_shape_has_a_reachable_preflight_case(self) -> None:
        seen: set[str] = set()
        for hook in catalog()["hooks"]:
            if hook.get("owned_by_route"):
                continue
            shape = preflight.SHAPES[hook["declaration_shape"]]
            preflight.validate_spec_text(
                hook_spec(hook["semantic_id"], hook["authorable_surfaces"][0], shape)
            )
            seen.add(shape)
        self.assertEqual({"value", "out-replacement", "collection"}, seen)

    def test_new_model_and_global_effect_surfaces_have_exact_reachability(self) -> None:
        hooks = {hook["semantic_id"]: hook for hook in catalog()["hooks"]}

        combat_only = hooks["should_draw"]
        self.assertIn("affliction", combat_only["authorable_surfaces"])
        self.assertIn("modifier", combat_only["authorable_surfaces"])
        self.assertIn("global-effect-combat", combat_only["authorable_surfaces"])
        self.assertNotIn("global-effect-run", combat_only["authorable_surfaces"])

        run_only = hooks["modify_merchant_price"]
        self.assertIn("modifier", run_only["authorable_surfaces"])
        self.assertIn("global-effect-run", run_only["authorable_surfaces"])
        self.assertNotIn("affliction", run_only["authorable_surfaces"])
        self.assertNotIn("global-effect-combat", run_only["authorable_surfaces"])

        run_with_combat = hooks["modify_damage_multiplicative"]
        self.assertIn("affliction", run_with_combat["authorable_surfaces"])
        self.assertIn("global-effect-run", run_with_combat["authorable_surfaces"])
        self.assertIn("global-effect-combat", run_with_combat["authorable_surfaces"])

    def test_preflight_rejects_wrong_global_effect_stream(self) -> None:
        with self.assertRaises(preflight.CapabilityPreflightError):
            preflight.validate_spec_text(
                hook_spec("should_draw", "global-effect-run", "value")
            )
        with self.assertRaises(preflight.CapabilityPreflightError):
            preflight.validate_spec_text(
                hook_spec("modify_merchant_price", "global-effect-combat", "value")
            )

    def test_each_surface_rejects_one_cataloged_unreachable_hook(self) -> None:
        hooks = [hook for hook in catalog()["hooks"] if not hook.get("owned_by_route")]
        for surface in AUTHORABLE_SURFACES:
            unreachable = next(
                (hook for hook in hooks if surface not in hook["authorable_surfaces"]),
                None,
            )
            if unreachable is None:
                continue
            shape = preflight.SHAPES[unreachable["declaration_shape"]]
            with self.subTest(surface=surface, capability=unreachable["semantic_id"]):
                with self.assertRaises(preflight.CapabilityPreflightError):
                    preflight.validate_spec_text(
                        hook_spec(unreachable["semantic_id"], surface, shape)
                    )


if __name__ == "__main__":
    unittest.main()
