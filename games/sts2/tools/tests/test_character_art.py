from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from PIL import Image


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from character_art import (  # noqa: E402
    CHARACTER_ART_BUNDLE,
    CharacterArtBundle,
    CharacterArtValidationError,
)


class CharacterArtBundleTests(unittest.TestCase):
    def test_current_inventory_has_complete_runtime_metadata(self) -> None:
        bundle = CHARACTER_ART_BUNDLE

        self.assertEqual(14, len(bundle.slots))
        self.assertEqual(10, len(bundle.specs))
        self.assertEqual(12, sum(slot.required for slot in bundle.slots))
        self.assertEqual(
            {"locked_selection_portrait", "map_marker"},
            {slot.name for slot in bundle.slots if not slot.required},
        )
        for slot in bundle.slots:
            with self.subTest(slot=slot.name):
                self.assertTrue(slot.output_path.startswith("charui/"))
                self.assertTrue(slot.fallback)
                self.assertTrue(slot.consumer)

        energy = [slot for slot in bundle.slots if slot.spec == "character_energy"]
        self.assertEqual(
            [f"charui/orb_layer_{index}.png" for index in range(1, 6)],
            [slot.output_path for slot in energy],
        )
        self.assertEqual({(256, 256)}, {slot.size for slot in energy})

    def test_sprite_tools_receive_the_existing_character_contract(self) -> None:
        specs = CHARACTER_ART_BUNDLE.sprite_specs()

        self.assertEqual((132, 195), specs["character_select"]["size"])
        self.assertEqual("cover", specs["character_select"]["fit"])
        self.assertFalse(specs["character_select"]["chroma"])
        self.assertEqual((49, 64), specs["character_map_marker"]["size"])
        self.assertFalse(specs["character_map_marker"]["verified"])
        self.assertTrue(specs["character_energy"]["chroma"])
        self.assertEqual(
            "character_combat",
            CHARACTER_ART_BUNDLE.reference_families()["character_merchant"],
        )

    def test_valid_bundle_requires_identity_and_all_promoted_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            identity = root / "identity.png"
            Image.new("RGB", (640, 640), (80, 110, 140)).save(identity)

            expected: list[Path] = []
            for slot in CHARACTER_ART_BUNDLE.slots:
                if not slot.required:
                    continue
                path = images / slot.output_path
                path.parent.mkdir(parents=True, exist_ok=True)
                if slot.alpha == "opaque":
                    image = Image.new("RGBA", slot.size, (30, 60, 90, 255))
                else:
                    image = Image.new("RGBA", slot.size, (30, 60, 90, 255))
                    image.putpixel((0, 0), (0, 0, 0, 0))
                image.save(path)
                expected.append(path)

            checked = CHARACTER_ART_BUNDLE.validate_outputs(images, identity)

            self.assertEqual(tuple(expected), checked)
            self.assertFalse((images / "charui/select_locked.png").exists())
            self.assertFalse((images / "charui/map_marker.png").exists())

    def test_review_writes_contact_sheet_and_energy_composite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            identity = root / "identity.png"
            Image.new("RGB", (640, 640), (80, 110, 140)).save(identity)
            for index, slot in enumerate(CHARACTER_ART_BUNDLE.slots):
                if not slot.required:
                    continue
                path = images / slot.output_path
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new("RGBA", slot.size, (40 + index, 60, 90, 255))
                if slot.alpha == "transparent":
                    image.putpixel((0, 0), (0, 0, 0, 0))
                image.save(path)

            contact, composite = CHARACTER_ART_BUNDLE.render_review(
                images, identity, root / "review"
            )

            with Image.open(contact) as image:
                self.assertEqual((1200, 1120), image.size)
            with Image.open(composite) as image:
                self.assertEqual((256, 256), image.size)
                self.assertEqual("RGBA", image.mode)
                self.assertGreater(image.getchannel("A").getextrema()[1], 0)

    def test_validation_reports_identity_missing_output_size_and_alpha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            bad_icon = images / "charui/icon.png"
            bad_icon.parent.mkdir(parents=True)
            Image.new("RGBA", (10, 10), (20, 40, 60, 255)).save(bad_icon)

            with self.assertRaises(CharacterArtValidationError) as raised:
                CHARACTER_ART_BUNDLE.validate_outputs(images)

            message = str(raised.exception)
            self.assertIn("canonical identity reference is required", message)
            self.assertIn("missing required selection_portrait", message)
            self.assertIn("top_panel_icon has size (10, 10)", message)
            self.assertIn("top_panel_icon has no transparent pixels", message)

    def test_contract_rejects_output_collisions_and_inconsistent_energy_geometry(self) -> None:
        first, second, *rest = CHARACTER_ART_BUNDLE.slots
        with self.assertRaisesRegex(CharacterArtValidationError, "share output path"):
            CharacterArtBundle((first, replace(second, output_path=first.output_path), *rest))

        slots = list(CHARACTER_ART_BUNDLE.slots)
        layer_index = next(
            index for index, slot in enumerate(slots)
            if slot.name == "full_energy_layer_2"
        )
        slots[layer_index] = replace(slots[layer_index], size=(128, 128))
        with self.assertRaisesRegex(CharacterArtValidationError, "inconsistent slot metadata"):
            CharacterArtBundle(tuple(slots))


if __name__ == "__main__":
    unittest.main()
