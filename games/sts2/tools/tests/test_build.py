from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import build  # noqa: E402


class BuildTests(unittest.TestCase):
    def test_resource_pack_is_only_selected_when_assets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "Canary"
            mods = root / "mods" / "Canary"
            assets.mkdir()
            mods.mkdir(parents=True)

            with mock.patch.object(build, "pack_assets") as pack, mock.patch("builtins.print"):
                self.assertFalse(build.pack_project_assets(root, "Canary", mods))
                pack.assert_not_called()

                (assets / "localization.json").write_text("{}\n", encoding="utf-8")
                self.assertTrue(build.pack_project_assets(root, "Canary", mods))
                pack.assert_called_once_with(
                    assets, "Canary", mods / "Canary.pck"
                )


if __name__ == "__main__":
    unittest.main()
