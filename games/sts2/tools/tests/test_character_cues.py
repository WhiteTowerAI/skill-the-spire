from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageChops, ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from character_cues import (  # noqa: E402
    ACTION_CONTRACT,
    BASELINE_Y,
    SHEET_COLUMNS,
    SHEET_ROWS,
    CharacterCueError,
    process_sheet,
)


MAGENTA = (255, 0, 255, 255)
CELL = 100
BODY = (40, 130, 190, 255)


def blank_sheet(background=MAGENTA) -> Image.Image:
    return Image.new("RGBA", (SHEET_COLUMNS * CELL, SHEET_ROWS * CELL), background)


def draw_body(draw: ImageDraw.ImageDraw, index: int, size=(40, 80), bottom_offset=-10,
              left=None) -> tuple[int, int]:
    row, column = divmod(index, SHEET_COLUMNS)
    x, y = column * CELL, row * CELL
    width, height = size
    left = x + (CELL - width) // 2 if left is None else left
    bottom = y + CELL + bottom_offset
    draw.rectangle((left, bottom - height + 1, left + width - 1, bottom), fill=BODY)
    return x, y


def cell_owner() -> dict[int, str]:
    """Each played cell belongs to the first cue that plays it, as the processor groups it."""
    owner: dict[int, str] = {}
    for action, contract in ACTION_CONTRACT.items():
        for cell in contract["play_cells"]:
            owner.setdefault(cell, action)
    return owner


def make_sheet(path: Path, sizes: dict[str, tuple[int, int]] | None = None,
               touch_edge: bool = False) -> Path:
    image = blank_sheet()
    draw = ImageDraw.Draw(image)
    owner = cell_owner()
    for index in range(SHEET_COLUMNS * SHEET_ROWS):
        left = 0 if touch_edge and index == 0 else None
        size = (sizes or {}).get(owner.get(index, ""), (40, 80))
        x, y = draw_body(draw, index, size, left=left)
        # A dark speck in the cell corner: debris, not part of the frame.
        draw.rectangle((x + 4, y + 4, x + 5, y + 5), fill=(30, 30, 30, 255))
    image.save(path)
    return path


def frames(root: Path, action: str) -> list[Image.Image]:
    return [Image.open(path).convert("RGBA")
            for path in sorted((root / "images" / "charui" / "cues" / action).glob("*.png"))]


class CharacterCueProcessorTests(unittest.TestCase):
    def test_processes_one_sheet_into_breathing_idle_and_key_pose_cues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            review = root / "review"
            metadata = process_sheet(make_sheet(root / "sheet.png"), root / "images", review)

            self.assertEqual("skill-the-spire-character-cues/v3", metadata["contract"])
            self.assertEqual(1, metadata["generation_calls"])
            self.assertEqual("combat_body", metadata["fallback_slot"])
            self.assertEqual({"scale": 0.8, "position": [0.0, -184.0]}, metadata["visual_style"])
            self.assertEqual([-160.0, -368.0], metadata["anchors"]["bounds_position"])
            self.assertTrue(metadata["actions"]["idle"]["loop"])
            self.assertTrue(metadata["actions"]["dead"]["terminal"])
            for action, contract in ACTION_CONTRACT.items():
                images = frames(root, action)
                self.assertEqual(contract["frame_count"], len(images))
                for frame in images:
                    self.assertEqual((512, 512), frame.size)
                    bounds = frame.getchannel("A").getbbox()
                    self.assertEqual(BASELINE_Y, bounds[3])
                    self.assertGreaterEqual(bounds[0], 26)
                    self.assertGreaterEqual(bounds[1], 26)
                    self.assertLessEqual(bounds[2], 486)
                self.assertTrue((review / action / "animation.gif").is_file())

            # Idle is one painted frame breathing: only the top moves, by a few pixels.
            tops = [frame.getchannel("A").getbbox()[1] for frame in frames(root, "idle")]
            self.assertEqual(tops[1], tops[3])
            self.assertLess(tops[2], tops[1])
            self.assertLess(tops[1], tops[0])
            self.assertLessEqual(tops[0] - tops[2], 6)
            self.assertEqual(1, len(metadata["actions"]["idle"]["poses"]))

            # Shared and repeated cells are the very same image, so a cue switch or a hold
            # never redraws the body.
            def same(a, b):
                return ImageChops.difference(a, b).getbbox() is None
            idle, attack, hit = (frames(root, name) for name in ("idle", "attack", "hit"))
            plays = {name: ACTION_CONTRACT[name]["play_cells"] for name in ("attack", "hit")}
            self.assertTrue(same(idle[0], attack[0]))
            self.assertTrue(same(idle[0], hit[0]))
            for name, images in (("attack", attack), ("hit", hit)):
                for i, j in ((i, j) for i in range(len(images)) for j in range(i + 1, len(images))):
                    if plays[name][i] == plays[name][j]:
                        self.assertTrue(same(images[i], images[j]), (name, i, j))
            shared = set(plays["attack"][1:]) & set(plays["hit"][1:])
            for cell in shared:
                self.assertTrue(same(attack[plays["attack"].index(cell)],
                                     hit[plays["hit"].index(cell)]))

            self.assertTrue((review / "raw-sheet-clean.png").is_file())
            self.assertTrue((review / "character-cues-contact-sheet.png").is_file())
            saved = json.loads((review / "pipeline-meta.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["global_scale"], saved["global_scale"])
            self.assertTrue(all(
                pose["component_count"] == 2
                for action in saved["actions"].values()
                for pose in action["poses"]
            ))

    def test_rejects_a_frame_cut_by_the_sheet_edge_before_writing_anything(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = make_sheet(root / "sheet.png", touch_edge=True)

            with self.assertRaisesRegex(CharacterCueError, "touches"):
                process_sheet(sheet, root / "images", root / "review")

            self.assertFalse((root / "images" / "charui" / "cues").exists())
            self.assertFalse((root / "review").exists())

    def test_rejects_attack_body_scale_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = make_sheet(root / "sheet.png", sizes={"attack": (20, 50)})

            with self.assertRaisesRegex(CharacterCueError, "attack median body height"):
                process_sheet(sheet, root / "images", root / "review")

    def test_resamples_backend_rounded_sheet_and_rejects_wrong_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = make_sheet(root / "sheet.png")
            with Image.open(sheet) as image:
                # Right shape, not whole cells, as a backend's own rounding returns it.
                image.resize((402, 402), Image.Resampling.NEAREST).save(sheet)
            metadata = process_sheet(sheet, root / "images", root / "review")
            self.assertEqual(ACTION_CONTRACT["attack"]["frame_count"],
                             len(metadata["actions"]["attack"]["frame_order"]))

            with Image.open(sheet) as image:
                image.resize((401, 703), Image.Resampling.NEAREST).save(sheet)
            with self.assertRaisesRegex(CharacterCueError, "not divisible"):
                process_sheet(sheet, root / "images2", root / "review2")

    def test_erases_grid_lines_despills_rims_and_keeps_detached_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = blank_sheet((255, 85, 252, 255))  # a real backend background, not #FF00FF
            draw = ImageDraw.Draw(image)
            for index in range(SHEET_COLUMNS * SHEET_ROWS):
                x, y = draw_body(draw, index)
                # Background noise past the old global threshold, joined to the grid lines.
                draw.line((x, y + 6, x + CELL - 1, y + 6), fill=(255, 130, 250, 255))
                draw.rectangle((x + 30, y + 11, x + 69, y + 12), fill=(120, 40, 120, 255))
                draw.rectangle((x + 74, y + 40, x + 81, y + 52), fill=(230, 170, 60, 255))
            for line in range(0, image.width + 1, CELL):
                draw.line((line, 0, line, image.height), fill=(10, 10, 10, 255), width=3)
                # The line's antialiased fringe: dark key blends that once bridged rows.
                for offset in (-2, 2):
                    draw.line((line + offset, 0, line + offset, image.height),
                              fill=(104, 0, 104, 255))
            for line in range(0, image.height + 1, CELL):
                draw.line((0, line, image.width, line), fill=(10, 10, 10, 255), width=3)
                for offset in (-2, 2):
                    draw.line((0, line + offset, image.width, line + offset),
                              fill=(104, 0, 104, 255))
            image.save(root / "sheet.png")

            process_sheet(root / "sheet.png", root / "images", root / "review")

            for action in ACTION_CONTRACT:
                for frame in frames(root, action):
                    bounds = frame.getchannel("A").getbbox()
                    self.assertLess(bounds[2] - bounds[0], 512 - 52)  # not a whole cell
                    pixels = [p for p in frame.getdata() if p[3]]
                    self.assertTrue(any(p[0] > 200 and p[2] < 120 for p in pixels))  # item kept
                    self.assertFalse(any(min(p[0], p[2]) - p[1] > 40 for p in pixels))

    def test_keeps_feet_that_cross_the_cell_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = blank_sheet()
            draw = ImageDraw.Draw(image)
            for index in range(SHEET_COLUMNS * SHEET_ROWS):
                row = index // SHEET_COLUMNS
                # Bodies end 6 px into the next row's cell, as real 2K sheets do; the last
                # row stays inside the sheet.
                offset = 5 if row < SHEET_ROWS - 1 else -6
                x, y = draw_body(draw, index, bottom_offset=offset)
                bottom = y + CELL + offset
                draw.rectangle((x + 30, bottom - 3, x + 69, bottom), fill=(200, 60, 30, 255))
            image.save(root / "sheet.png")

            process_sheet(root / "sheet.png", root / "images", root / "review")

            for action in ACTION_CONTRACT:
                for frame in frames(root, action):
                    bottom_row = [frame.getpixel((x, BASELINE_Y - 1)) for x in range(512)]
                    # The red "sole" painted on the last 4 px survives in every frame.
                    self.assertTrue(any(p[3] and p[0] > 150 and p[2] < 90 for p in bottom_row))

    def test_keeps_see_through_glass_painted_as_darkened_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = blank_sheet()
            draw = ImageDraw.Draw(image)
            for index in range(SHEET_COLUMNS * SHEET_ROWS):
                x, y = draw_body(draw, index)
                # Glass on the body's open side, touching the background, painted as the
                # key seen through it: a real 1K sheet's (133, 30, 99).
                draw.rectangle((x + 70, y + 40, x + 79, y + 60), fill=(133, 30, 99, 255))
            image.save(root / "sheet.png")

            process_sheet(root / "sheet.png", root / "images", root / "review")

            for frame in frames(root, "attack"):
                bounds = frame.getchannel("A").getbbox()
                body_only = frames(root, "attack")[0].getchannel("A").getbbox()
                self.assertEqual(body_only, bounds)
                pixels = [p for p in frame.getdata() if p[3] == 255]
                glass = [p for p in pixels if p[0] > 50 and p[2] < 60 and p[1] < 40]
                self.assertTrue(glass, "the glass was punched out")
                self.assertFalse(any(min(p[0], p[2]) - p[1] > 40 for p in pixels))


if __name__ == "__main__":
    unittest.main()
