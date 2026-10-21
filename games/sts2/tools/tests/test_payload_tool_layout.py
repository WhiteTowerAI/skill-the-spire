"""Build's shipped helpers must find their catalogs in the published payload layout."""
from __future__ import annotations

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
        catalogs = self.root / "sts2api" / "reference" / "catalogs"
        catalogs.mkdir(parents=True)
        self.scripts.mkdir(parents=True)
        for tool in ("hook_reachability.py", "api.py"):
            shutil.copy(TOOLS_DIR / tool, self.scripts)
        shutil.copy(
            SOURCE_SKILLS / "sts2api" / "reference" / "catalogs" / "model-hooks-sts2-0.107.1.json",
            catalogs,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_hook_reachability_resolves_its_catalog_in_payload(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c",
             "import hook_reachability as h; print(len(h.load_hooks()), h.hook_catalog_path())"],
            cwd=self.scripts,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        count, path = result.stdout.split(maxsplit=1)
        self.assertEqual("68", count)
        self.assertTrue(Path(path.strip()).is_relative_to(self.root))


if __name__ == "__main__":
    unittest.main()
