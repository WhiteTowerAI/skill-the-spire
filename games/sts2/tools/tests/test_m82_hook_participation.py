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
    / "sts2-api"
    / "reference"
    / "catalogs"
    / "model-hooks-sts2-0.107.1.json"
)
ROUTE_PAGE = SKILLS_DIR / "sts2-api" / "reference" / "model-hook-participation.md"
SURFACES_DIR = SKILLS_DIR / "modmaker" / "surfaces"
RECIPES_DIR = SKILLS_DIR / "sts2-api" / "recipes"
AUTHORABLE_SURFACES = ("card", "enchantment", "monster", "orb", "potion", "power", "relic")
NON_AUTHORABLE_SURFACES = ("character", "event", "keyword")


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

    def test_authorable_surfaces_document_hook_participation(self) -> None:
        for slug in AUTHORABLE_SURFACES:
            with self.subTest(surface=slug):
                text = (SURFACES_DIR / f"{slug}.md").read_text(encoding="utf-8")
                self.assertIn("hook participation", text.lower())
                recipe = (RECIPES_DIR / f"{slug}.md").read_text(encoding="utf-8")
                self.assertIn("model-hook-participation.md", recipe)

    def test_non_authorable_surfaces_do_not_offer_hook_participation(self) -> None:
        for slug in NON_AUTHORABLE_SURFACES:
            with self.subTest(surface=slug):
                text = (SURFACES_DIR / f"{slug}.md").read_text(encoding="utf-8")
                self.assertNotIn("hook participation:", text.lower())

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

    def test_route_requires_modified_and_neutral_proof(self) -> None:
        text = ROUTE_PAGE.read_text(encoding="utf-8")
        self.assertIn("the modified value", text)
        self.assertIn("neutral case outside the guard", text)
        self.assertIn("unrelated entry", text)
        self.assertIn("hook must be driven by the engine", text)


if __name__ == "__main__":
    unittest.main()
