"""Protect the hard model-hook boundary that compilation cannot detect."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import hook_reachability  # noqa: E402


SKILLS_DIR = TOOLS_DIR.parent / "skills"
CATALOG_PATH = (
    SKILLS_DIR
    / "sts2api"
    / "reference"
    / "catalogs"
    / "model-hooks-sts2-0.107.1.json"
)


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


class HookCatalogProjectionTests(unittest.TestCase):
    def test_route_owned_rest_site_hooks_stay_owned_by_their_route(self) -> None:
        owned = [hook for hook in catalog()["hooks"] if hook.get("owned_by_route")]
        self.assertEqual(2, len(owned))
        for hook in owned:
            self.assertIn("rest-site-options.md", hook["owned_by_route"])

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

    def test_global_effect_scope_comes_from_its_source_hook_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "Run.cs").write_text(
                "public sealed class RunRule : HookedSingletonModel\n"
                "{ public RunRule() : base(HookType.Run) { } }\n",
                encoding="utf-8",
            )
            (project / "Combat.cs").write_text(
                "public sealed class CombatRule : HookedSingletonModel\n"
                "{ public CombatRule() : base(HookType.Combat) { } }\n",
                encoding="utf-8",
            )
            self.assertEqual({"global-effect-run"},
                             hook_reachability.global_scopes(project, "RunRule"))
            self.assertEqual({"global-effect-combat"},
                             hook_reachability.global_scopes(project, "CombatRule"))
            self.assertEqual({"global-effect-run", "global-effect-combat"},
                             hook_reachability.global_scopes(project, "UnknownRule"))


if __name__ == "__main__":
    unittest.main()
