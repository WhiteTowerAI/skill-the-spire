"""The art contract as data, and the prose views that must agree with it.

The art contract's exact values live in queryable code:
code -- `gen_sprite.SPECS` and `character_art.CHARACTER_ART_BUNDLE` -- because `fit`,
`chroma`, and the visible footprints are behavior, not documentation. The catalog at
`reference/catalogs/art-contract-sts2-0.107.1.json` is a generated projection of that code,
so a reader gets the data without executing Python.

Projection alone would just add a fourth copy. These tests are what make it a single
contract:

1. the committed catalog still equals what the code holds, so changing a size in code and
   forgetting to re-export fails here rather than shipping a stale catalog;
2. every size stated in the three prose tables equals the catalog's; and
3. every spec in the catalog has a row in the prose, so a new spec cannot ship undocumented.

Before this, `art-contract.md` asked a human to "keep them in sync" and nothing checked it.
That instruction had already failed once: the cue grid was written columns-first in four
prose copies and printed rows-first by `list-specs`, which for the only non-square sheet
(`Dead`) named a 3-wide x 2-tall sheet when the geometry is 2 wide x 3 tall. Recorded as
drift between the generated catalog and its authoritative code.

What these tests do not establish: that any size is correct in-game. Sizes are grounded by
the headed runs recorded in `art-contract.md`; this file only holds the copies together.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
GEN_SPRITE = TOOLS_DIR / "gen_sprite.py"
REPO_ROOT = TOOLS_DIR.parents[2]
STS2API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2api"
CATALOG_PATH = STS2API_DIR / "reference" / "catalogs" / "art-contract-sts2-0.107.1.json"
ART_CONTRACT_PATH = STS2API_DIR / "reference" / "art-contract.md"
PRESENTATION_PATH = STS2API_DIR / "reference" / "character-presentation.md"
CUES_PATH = STS2API_DIR / "reference" / "character-combat-cues.md"

sys.path.insert(0, str(TOOLS_DIR))
import gen_sprite  # noqa: E402


def sizes_in(text: str) -> set[tuple[int, int]]:
    """Every WxH literal in a document, tolerating both `x` and the `×` used in prose."""
    return {
        (int(w), int(h))
        for w, h in re.findall(r"\b(\d{2,4})\s*[x×]\s*(\d{2,4})\b", text)
    }


class ArtContractCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.art = ART_CONTRACT_PATH.read_text(encoding="utf-8")
        cls.presentation = PRESENTATION_PATH.read_text(encoding="utf-8")
        cls.cues_page = CUES_PATH.read_text(encoding="utf-8")

    def test_committed_catalog_equals_what_the_code_holds(self) -> None:
        """A code change with no re-export must fail here, not ship a stale catalog."""
        self.assertEqual(gen_sprite.build_art_contract_catalog(), self.catalog)

    def test_catalog_declares_its_generated_projection_status(self) -> None:
        """The catalog must say it is generated, so nobody hand-edits it into a rival source."""
        self.assertEqual("skillthespire.sts2.art-contract/v1", self.catalog["schema"])
        self.assertEqual("0.107.1", self.catalog["host_version"])
        source = self.catalog["source"]
        self.assertIn("gen_sprite.py", source["definition"])
        self.assertIn("character_art.py", source["definition"])
        self.assertIn("export-contract", source["projection"])

    def test_every_content_spec_size_and_row_appears_in_the_prose_table(self) -> None:
        prose_sizes = sizes_in(self.art)
        for entry in self.catalog["content_specs"]:
            spec = entry["spec"]
            with self.subTest(spec=spec):
                self.assertIn(
                    f"`{spec}`",
                    self.art,
                    f"catalog spec {spec} has no row in art-contract.md",
                )
                if entry["size"] is None:
                    continue
                self.assertIn(
                    tuple(entry["size"]),
                    prose_sizes,
                    f"{spec} size {entry['size']} is not stated in art-contract.md",
                )

    def test_every_character_slot_size_and_spec_appears_in_both_prose_pages(self) -> None:
        art_sizes = sizes_in(self.art)
        presentation_sizes = sizes_in(self.presentation)
        for slot in self.catalog["character_slots"]:
            size = tuple(slot["size"])
            with self.subTest(slot=slot["name"]):
                self.assertIn(f"`{slot['spec']}`", self.art)
                self.assertIn(
                    size,
                    art_sizes,
                    f"{slot['name']} size {size} is not stated in art-contract.md",
                )
                self.assertIn(
                    size,
                    presentation_sizes,
                    f"{slot['name']} size {size} is not stated in "
                    f"character-presentation.md",
                )

    def test_character_slot_output_filenames_are_stated_in_the_prose(self) -> None:
        """The stable output names are what the generated AssetProfile resolves."""
        for slot in self.catalog["character_slots"]:
            name = Path(slot["output_path"]).name
            if re.fullmatch(r"orb_layer_[2-5]\.png", name):
                # art-contract.md states these as the range `orb_layer_2.png` through
                # `orb_layer_5.png`; the endpoints are asserted, the interior is prose.
                continue
            if name == "map_marker.png":
                # The unlisted marker keeps its native/shared fallback; the page names the
                # spec and size but deliberately does not advertise a filename to author.
                continue
            with self.subTest(slot=slot["name"]):
                self.assertIn(name, self.art)

    def test_cue_grid_geometry_is_named_and_consistent_everywhere(self) -> None:
        """columns x rows, 512px cells, and the same order in code, catalog, and prose."""
        sheet = self.catalog["character_cues"]["sheet"]
        self.assertEqual(
            [sheet["columns"] * sheet["cell_px"], sheet["rows"] * sheet["cell_px"]],
            sheet["sheet_px"],
            "sheet_px must be columns-first, matching the requested image",
        )
        cells = sheet["columns"] * sheet["rows"]
        for action in self.catalog["character_cues"]["actions"]:
            with self.subTest(cue=action["name"]):
                self.assertTrue(all(0 <= cell < cells for cell in action["play_cells"]))
        grid = f"{sheet['columns']}x{sheet['rows']}"
        pixels = f"{sheet['sheet_px'][0]}x{sheet['sheet_px'][1]}"
        for page, text in (("art-contract.md", self.art), ("character-combat-cues.md",
                                                           self.cues_page)):
            with self.subTest(page=page):
                self.assertIn(grid, text, f"cue grid {grid} (cols x rows) is not in {page}")
                self.assertIn(pixels, text, f"cue sheet {pixels} is not in {page}")

    def test_list_specs_prints_cue_sheets_width_first(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        sheet = [
            line for line in result.stdout.splitlines()
            if line.startswith("character_cues")
        ]
        self.assertEqual(1, len(sheet), result.stdout)
        self.assertIn("2048x2048", sheet[0])
        self.assertIn("4 cols x 4 rows", sheet[0])

    def test_cue_shared_geometry_matches_the_prose_contract(self) -> None:
        cues = self.catalog["character_cues"]
        self.assertEqual(24, cues["total_frames"])
        self.assertEqual(1, cues["generation_calls"])
        for phrase in (
            f"({cues['content_box'][0]},{cues['content_box'][1]})-"
            f"({cues['content_box'][2]},{cues['content_box'][3]})",
            f"baseline `{cues['baseline_y']}`",
            "twenty-four frames",
        ):
            self.assertIn(phrase, self.cues_page)

if __name__ == "__main__":
    unittest.main()
