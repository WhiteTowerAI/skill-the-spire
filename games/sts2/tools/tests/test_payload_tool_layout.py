"""The shipped capability preflight must resolve routes and catalogs in payload layout."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
SOURCE_SKILLS = TOOLS_DIR.parent / "skills"


class PayloadLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "skills"
        self.scripts = self.root / "modmaker" / "scripts"
        self.api = self.root / "sts2api"
        (self.api / "reference" / "catalogs").mkdir(parents=True)
        (self.api / "recipes").mkdir(parents=True)
        self.scripts.mkdir(parents=True)

        shutil.copy(TOOLS_DIR / "capability_preflight.py", self.scripts)
        shutil.copy(
            SOURCE_SKILLS
            / "sts2api"
            / "reference"
            / "catalogs"
            / "model-hooks-sts2-0.107.1.json",
            self.api / "reference" / "catalogs",
        )
        shutil.copy(
            SOURCE_SKILLS / "sts2api" / "reference" / "model-hook-participation.md",
            self.api / "reference",
        )
        shutil.copy(SOURCE_SKILLS / "sts2api" / "recipes" / "card.md", self.api / "recipes")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_preflight(self, text: str) -> subprocess.CompletedProcess[str]:
        spec = Path(self.temp.name) / "SPEC.md"
        spec.write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(self.scripts / "capability_preflight.py"), "--spec", str(spec)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_support_route_resolves_in_payload(self) -> None:
        result = self.run_preflight(
            "# SPEC\n\n## Implementation\n\n- Support: recipes/card.md\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("support_routes=1", result.stdout)

    def test_hook_catalog_and_declaration_resolve_in_payload(self) -> None:
        result = self.run_preflight(
            "# SPEC\n\n## Implementation\n\n"
            "- Hook: modify_damage_multiplicative | surface: power | shape: value | "
            "route: reference/model-hook-participation.md\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("hooks=1", result.stdout)

    def test_payload_run_rejects_unreachable_hook(self) -> None:
        raw = json.loads(
            (
                self.api
                / "reference"
                / "catalogs"
                / "model-hooks-sts2-0.107.1.json"
            ).read_text(encoding="utf-8")
        )
        hook = next(
            entry
            for entry in raw["hooks"]
            if "power" not in entry["authorable_surfaces"]
            and not entry.get("owned_by_route")
            and not entry.get("enchantment_redirect")
        )
        shapes = {
            "scalar-return": "value",
            "out-replacement": "out-replacement",
            "collection-edit": "collection",
        }
        result = self.run_preflight(
            "# SPEC\n\n## Implementation\n\n"
            f"- Hook: {hook['semantic_id']} | surface: power | "
            f"shape: {shapes[hook['declaration_shape']]} | "
            "route: reference/model-hook-participation.md\n"
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot reach", result.stderr)


if __name__ == "__main__":
    unittest.main()
