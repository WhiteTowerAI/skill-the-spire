from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from PIL import Image, ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
ART_SAMPLES = TOOLS_DIR.parent / "skills" / "sts2-api" / "reference" / "art-samples"
sys.path.insert(0, str(TOOLS_DIR))
from character_art import (  # noqa: E402
    CHARACTER_ART_BUNDLE,
    CharacterArtBundle,
    CharacterArtValidationError,
)


class CharacterArtBundleTests(unittest.TestCase):
    def test_inventory_has_complete_slot_metadata_and_roles(self) -> None:
        bundle = CHARACTER_ART_BUNDLE

        self.assertEqual(16, len(bundle.slots))
        self.assertEqual(11, len(bundle.specs))
        self.assertEqual(14, sum(slot.required for slot in bundle.slots))
        self.assertEqual(
            {"locked_selection_portrait", "map_marker"},
            {slot.name for slot in bundle.slots if not slot.required},
        )
        self.assertEqual("selection_portrait", bundle.identity_slot)
        self.assertEqual(
            {"character_combat", "character_rest", "character_merchant"},
            {
                slot.spec for slot in bundle.slots
                if slot.reference_role == "identity"
            },
        )
        self.assertEqual(
            {
                "character_background",
                "character_icon",
                "character_energy",
                "character_energy_large",
                "character_energy_text",
            },
            {
                slot.spec for slot in bundle.slots
                if slot.reference_role == "palette"
            },
        )

    def test_sprite_specs_and_reference_families_are_derived_from_bundle(self) -> None:
        specs = CHARACTER_ART_BUNDLE.sprite_specs()

        self.assertEqual((132, 195), specs["character_select"]["size"])
        self.assertEqual("contain", specs["character_select"]["fit"])
        self.assertFalse(specs["character_select"]["chroma"])
        self.assertEqual((256, 256), specs["character_energy"]["size"])
        self.assertTrue(specs["character_energy"]["chroma"])
        self.assertEqual((256, 256), specs["character_energy_large"]["size"])
        self.assertEqual((24, 24), specs["character_energy_text"]["size"])
        self.assertNotEqual(
            CHARACTER_ART_BUNDLE.slot("large_energy_icon").output_path,
            CHARACTER_ART_BUNDLE.slot("compact_energy_icon").output_path,
        )
        self.assertEqual(
            "character_combat",
            CHARACTER_ART_BUNDLE.reference_families()["character_merchant"],
        )
        self.assertEqual(
            "character_background",
            CHARACTER_ART_BUNDLE.reference_families()["character_background"],
        )
        selection = CHARACTER_ART_BUNDLE.visible_footprint("character_select")
        combat = CHARACTER_ART_BUNDLE.visible_footprint("character_combat")
        self.assertEqual((6, 8, 126, 187), selection.content_box)
        self.assertEqual((26, 26, 486, 486), combat.content_box)
        self.assertEqual(486, combat.baseline_y)
        self.assertEqual(0.80, combat.visual_scale)
        self.assertEqual((0.0, -184.0), combat.visual_position)

    def test_combat_cue_contract_owns_actions_budget_geometry_and_identity_routing(self) -> None:
        cues = CHARACTER_ART_BUNDLE.combat_cues

        self.assertIsNotNone(cues)
        self.assertEqual(
            ("character_cue_idle", "character_cue_attack", "character_cue_hit", "character_cue_dead"),
            CHARACTER_ART_BUNDLE.cue_specs,
        )
        self.assertEqual(4, cues.generation_calls)
        self.assertEqual((4, 4, 4, 6), tuple(action.frame_count for action in cues.actions))
        dead = next(action for action in cues.actions if action.name == "dead")
        self.assertEqual((3, 2), (dead.rows, dead.columns))
        self.assertEqual((180, 90, 80, 140), tuple(
            action.frame_duration_ms for action in cues.actions
        ))
        self.assertEqual((512, 512), cues.frame_size)
        self.assertEqual((26, 26, 486, 486), cues.content_box)
        self.assertEqual(486, cues.baseline_y)
        self.assertEqual("combat_body", cues.fallback_slot)
        self.assertEqual((0.0, -184.0), cues.visual_position)
        self.assertEqual(
            "character_combat",
            CHARACTER_ART_BUNDLE.reference_families()["character_cue_attack"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "select.png"
            Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)
            self.assertEqual(
                identity.resolve(),
                CHARACTER_ART_BUNDLE.validate_identity_reference(
                    "character_cue_dead", identity
                ),
            )

    def test_character_background_reference_pool_is_shipped(self) -> None:
        pool = ART_SAMPLES / "character_background"
        references = sorted(pool.glob("*.png"))

        self.assertEqual(
            ["defect.png", "ironclad.png", "silent.png"],
            [path.name for path in references],
        )
        for reference in references:
            with Image.open(reference) as image:
                self.assertEqual((2048, 2048), image.size)

    def test_energy_templates_have_exact_mapping_and_no_generation_budget(self) -> None:
        templates = CHARACTER_ART_BUNDLE.validate_templates()

        self.assertEqual(
            ["layer_2.png", "layer_3.png", "layer_4.png", "layer_5.png"],
            [path.name for path in templates],
        )
        fixed = CHARACTER_ART_BUNDLE.fixed_template_slots
        self.assertEqual(
            ["full_energy_layer_2", "full_energy_layer_3", "full_energy_layer_4", "full_energy_layer_5"],
            [slot.name for slot in fixed],
        )
        self.assertTrue(all(slot.generation_calls == 0 for slot in fixed))
        self.assertEqual(1, CHARACTER_ART_BUNDLE.slot("full_energy_layer_1").generation_calls)
        outline = CHARACTER_ART_BUNDLE.slot("top_panel_icon_outline")
        self.assertEqual("derived", outline.asset_origin)
        self.assertEqual(0, outline.generation_calls)

    def test_install_fixed_templates_copies_source_assets_without_resizing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            installed = CHARACTER_ART_BUNDLE.install_fixed_templates(images)

            self.assertEqual(
                [images / f"charui/orb_layer_{index}.png" for index in range(2, 6)],
                list(installed),
            )
            for slot, destination in zip(CHARACTER_ART_BUNDLE.fixed_template_slots, installed):
                source = CHARACTER_ART_BUNDLE.template_source_path(slot)
                self.assertEqual(source.read_bytes(), destination.read_bytes())
                with Image.open(destination) as image:
                    self.assertEqual((256, 256), image.size)
                    self.assertEqual("RGBA", image.mode)

    def test_identity_routing_requires_only_identity_sensitive_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "select.png"
            Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)

            self.assertEqual(
                identity.resolve(),
                CHARACTER_ART_BUNDLE.validate_identity_reference(
                    "character_combat", identity
                ),
            )
            with self.assertRaisesRegex(CharacterArtValidationError, "palette-only"):
                CHARACTER_ART_BUNDLE.validate_identity_reference(
                    "character_icon", identity
                )
            with self.assertRaisesRegex(CharacterArtValidationError, "requires"):
                CHARACTER_ART_BUNDLE.validate_identity_reference("character_rest", None)

    def test_valid_outputs_require_selection_bootstrap_and_promoted_slots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            for index, slot in enumerate(CHARACTER_ART_BUNDLE.slots):
                if not slot.required:
                    continue
                path = images / slot.output_path
                path.parent.mkdir(parents=True, exist_ok=True)
                if slot.name == "combat_body":
                    image = Image.new("RGBA", slot.size, (0, 0, 0, 0))
                    ImageDraw.Draw(image).rectangle(
                        (80, 26, 431, 485), fill=(30 + index, 60, 90, 255)
                    )
                else:
                    image = Image.new("RGBA", slot.size, (30 + index, 60, 90, 255))
                if slot.alpha == "transparent" and slot.name != "combat_body":
                    image.putpixel((0, 0), (0, 0, 0, 0))
                image.save(path)

            checked = CHARACTER_ART_BUNDLE.validate_outputs(images)

            self.assertEqual(14, len(checked))
            self.assertEqual(
                CHARACTER_ART_BUNDLE.identity_path(images),
                images / "charui/select.png",
            )

    def test_review_writes_contact_sheet_and_energy_composite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            for index, slot in enumerate(CHARACTER_ART_BUNDLE.slots):
                if not slot.required:
                    continue
                path = images / slot.output_path
                path.parent.mkdir(parents=True, exist_ok=True)
                if slot.name == "combat_body":
                    image = Image.new("RGBA", slot.size, (0, 0, 0, 0))
                    ImageDraw.Draw(image).rectangle(
                        (80, 26, 431, 485), fill=(40 + index, 60, 90, 255)
                    )
                else:
                    image = Image.new("RGBA", slot.size, (40 + index, 60, 90, 255))
                if slot.alpha == "transparent" and slot.name != "combat_body":
                    image.putpixel((0, 0), (0, 0, 0, 0))
                image.save(path)

            contact, composite = CHARACTER_ART_BUNDLE.render_review(
                images, root / "review"
            )

            with Image.open(contact) as image:
                self.assertEqual((1200, 1120), image.size)
            with Image.open(composite) as image:
                self.assertEqual((256, 256), image.size)
                self.assertGreater(image.getchannel("A").getextrema()[1], 0)

    def test_combat_footprint_rejects_empty_edge_touching_and_wrong_baseline(self) -> None:
        empty = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        with self.assertRaisesRegex(CharacterArtValidationError, "empty"):
            CHARACTER_ART_BUNDLE.validate_visible_footprint("character_combat", empty)

        touching = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        ImageDraw.Draw(touching).rectangle(
            (80, 0, 431, 485), fill=(80, 110, 140, 255)
        )
        with self.assertRaisesRegex(CharacterArtValidationError, "touches"):
            CHARACTER_ART_BUNDLE.validate_visible_footprint("character_combat", touching)

        wrong_baseline = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        ImageDraw.Draw(wrong_baseline).rectangle(
            (80, 26, 431, 479), fill=(80, 110, 140, 255)
        )
        with self.assertRaisesRegex(CharacterArtValidationError, "baseline"):
            CHARACTER_ART_BUNDLE.validate_visible_footprint(
                "character_combat", wrong_baseline
            )

    def test_contract_rejects_separate_identity_and_path_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            selection = images / "charui/select.png"
            selection.parent.mkdir(parents=True)
            Image.new("RGB", (132, 195), (80, 110, 140)).save(selection)
            with self.assertRaisesRegex(CharacterArtValidationError, "sole Character identity"):
                CHARACTER_ART_BUNDLE.validate_outputs(
                    images, Path(tmp) / "separate-sheet.png"
                )

        first, second, *rest = CHARACTER_ART_BUNDLE.slots
        with self.assertRaisesRegex(CharacterArtValidationError, "share output path"):
            CharacterArtBundle(
                (first, replace(second, output_path=first.output_path), *rest)
            )


if __name__ == "__main__":
    unittest.main()
