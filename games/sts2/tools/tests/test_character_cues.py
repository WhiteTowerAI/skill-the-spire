from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from character_cues import (  # noqa: E402
    ACTION_CONTRACT,
    BASELINE_Y,
    CharacterCueError,
    process_bundle,
)


MAGENTA = (255, 0, 255, 255)


def make_sheet(
    path: Path,
    action: str,
    subject_size: tuple[int, int] = (40, 80),
    touch_edge: bool = False,
) -> None:
    contract = ACTION_CONTRACT[action]
    rows, cols = contract["rows"], contract["cols"]
    cell = 100
    image = Image.new("RGBA", (cols * cell, rows * cell), MAGENTA)
    draw = ImageDraw.Draw(image)
    width, height = subject_size
    for index in range(rows * cols):
        row, column = divmod(index, cols)
        left = column * cell + (0 if touch_edge and index == 0 else (cell - width) // 2)
        top = row * cell + (cell - height) // 2
        draw.rectangle((left, top, left + width - 1, top + height - 1), fill=(40, 130, 190, 255))
        draw.rectangle((column * cell + 4, row * cell + 4, column * cell + 5, row * cell + 5),
                       fill=(30, 30, 30, 255))
    image.save(path)


class CharacterCueProcessorTests(unittest.TestCase):
    def _sources(self, root: Path, **sizes: tuple[int, int]) -> dict[str, Path]:
        sources = {}
        for action in ACTION_CONTRACT:
            path = root / f"{action}.png"
            make_sheet(path, action, subject_size=sizes.get(action, (40, 80)))
            sources[action] = path
        return sources

    def test_processes_complete_bundle_with_shared_scale_baseline_and_qc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            review = root / "review"
            metadata = process_bundle(self._sources(root), images, review)

            self.assertEqual("skill-the-spire-character-cues/v1", metadata["contract"])
            self.assertEqual(18, sum(
                len(action["frames"]) for action in metadata["actions"].values()
            ))
            self.assertEqual([0, 1, 2, 3], metadata["actions"]["attack"]["frame_order"])
            self.assertTrue(metadata["actions"]["idle"]["loop"])
            self.assertTrue(metadata["actions"]["dead"]["terminal"])
            self.assertEqual(4, metadata["generation_calls"])
            self.assertEqual("combat_body", metadata["fallback_slot"])
            self.assertEqual(
                {"scale": 0.8, "position": [0.0, -184.0]},
                metadata["visual_style"],
            )
            self.assertEqual([-160.0, -368.0], metadata["anchors"]["bounds_position"])
            self.assertEqual([0.0, -420.0], metadata["anchors"]["talk_position"])
            self.assertEqual(
                "character_cue_dead", metadata["actions"]["dead"]["source_spec"]
            )

            for action, contract in ACTION_CONTRACT.items():
                frame_paths = sorted((images / "charui" / "cues" / action).glob("*.png"))
                self.assertEqual(contract["rows"] * contract["cols"], len(frame_paths))
                for frame_path in frame_paths:
                    with Image.open(frame_path) as frame:
                        self.assertEqual((512, 512), frame.size)
                        bounds = frame.getchannel("A").getbbox()
                        self.assertEqual(BASELINE_Y, bounds[3])
                        self.assertGreaterEqual(bounds[0], 26)
                        self.assertGreaterEqual(bounds[1], 26)
                        self.assertLessEqual(bounds[2], 486)

            for action in ACTION_CONTRACT:
                self.assertTrue((review / action / "raw-sheet-clean.png").is_file())
                self.assertTrue((review / action / "animation.gif").is_file())
            self.assertTrue((review / "character-cues-contact-sheet.png").is_file())
            saved = json.loads((review / "pipeline-meta.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["global_scale"], saved["global_scale"])
            self.assertTrue(all(
                frame["component_count"] == 2
                for action in saved["actions"].values()
                for frame in action["frames"]
            ))

    def test_rejects_edge_touch_before_writing_any_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = self._sources(root)
            make_sheet(sources["attack"], "attack", touch_edge=True)

            with self.assertRaisesRegex(CharacterCueError, "touches"):
                process_bundle(sources, root / "images", root / "review")

            self.assertFalse((root / "images" / "charui" / "cues").exists())
            self.assertFalse((root / "review").exists())

    def test_rejects_attack_body_scale_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = self._sources(root, attack=(20, 50))

            with self.assertRaisesRegex(CharacterCueError, "attack median body height"):
                process_bundle(sources, root / "images", root / "review")

    def test_requires_all_four_action_sheets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = self._sources(root)
            del sources["dead"]

            with self.assertRaisesRegex(CharacterCueError, "missing action sheet"):
                process_bundle(sources, root / "images", root / "review")


if __name__ == "__main__":
    unittest.main()
