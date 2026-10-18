from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from PIL import Image, ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
STS2_DIR = TOOLS_DIR.parent
ART_SAMPLES = STS2_DIR / "skills" / "sts2api" / "reference" / "art-samples"
CHARACTER_RECIPE = STS2_DIR / "skills" / "sts2api" / "recipes" / "character.md"
sys.path.insert(0, str(TOOLS_DIR))
import character_art  # noqa: E402
from character_art import (  # noqa: E402
    CHARACTER_ART_BUNDLE,
    CharacterArtBundle,
    CharacterArtSheet,
    CharacterArtTier,
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
        self.assertEqual("cover", specs["character_select"]["fit"])
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
        self.assertIsNone(CHARACTER_ART_BUNDLE.visible_footprint("character_select"))
        self.assertEqual("cover", CHARACTER_ART_BUNDLE.slot("selection_portrait").fit)
        combat = CHARACTER_ART_BUNDLE.visible_footprint("character_combat")
        self.assertEqual((26, 26, 486, 486), combat.content_box)
        self.assertEqual(486, combat.baseline_y)
        self.assertEqual(0.80, combat.visual_scale)
        self.assertEqual((0.0, -184.0), combat.visual_position)

    def test_combat_cue_contract_owns_actions_budget_geometry_and_identity_routing(self) -> None:
        cues = CHARACTER_ART_BUNDLE.combat_cues

        self.assertIsNotNone(cues)
        self.assertEqual(("character_cues",), CHARACTER_ART_BUNDLE.cue_specs)
        self.assertEqual(1, cues.generation_calls)
        self.assertEqual((2048, 2048), cues.sheet_size)
        self.assertEqual(0, cues.anchor_cell)
        plays = {action.name: action.play_cells for action in cues.actions}
        self.assertEqual((0,), plays["idle"])
        self.assertEqual(cues.anchor_cell, plays["attack"][0])
        self.assertEqual(cues.anchor_cell, plays["hit"][0])
        # Hit recovers through Attack's recovery cell; holds are repeated cells.
        self.assertEqual(plays["attack"][-1], plays["hit"][-1])
        self.assertEqual((4, 9, 6, 5), tuple(action.frame_count for action in cues.actions))
        self.assertEqual(["idle"], [action.name for action in cues.actions if action.breathing])
        self.assertEqual(0.0, cues.breath[0])
        self.assertEqual((250, 60, 70, 170), tuple(
            action.frame_duration_ms for action in cues.actions
        ))
        self.assertEqual(5, cues.attack_strike_frame)
        self.assertEqual((512, 512), cues.frame_size)
        self.assertEqual((26, 26, 486, 486), cues.content_box)
        self.assertEqual(486, cues.baseline_y)
        self.assertEqual("combat_body", cues.fallback_slot)
        self.assertEqual((0.0, -184.0), cues.visual_position)
        self.assertEqual(
            "character_combat",
            CHARACTER_ART_BUNDLE.reference_families()["character_cues"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            anchor = Path(tmp) / "combat.png"
            Image.new("RGBA", (512, 512), (80, 110, 140, 255)).save(anchor)
            self.assertEqual(
                anchor.resolve(),
                CHARACTER_ART_BUNDLE.validate_identity_reference("character_cues", anchor),
            )
            with self.assertRaises(CharacterArtValidationError):
                CHARACTER_ART_BUNDLE.validate_identity_reference("character_cues", None)

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
        layer_1 = CHARACTER_ART_BUNDLE.slot("full_energy_layer_1")
        self.assertEqual(("derived", 0), (layer_1.asset_origin, layer_1.generation_calls))
        outline = CHARACTER_ART_BUNDLE.slot("top_panel_icon_outline")
        self.assertEqual("derived", outline.asset_origin)
        self.assertEqual(0, outline.generation_calls)

    def test_placeholder_energy_fallback_is_explicitly_ironclad(self) -> None:
        counter_fallback = "base-game Ironclad profile: ironclad_energy_counter.tscn"
        for index in range(1, 6):
            self.assertEqual(
                counter_fallback,
                CHARACTER_ART_BUNDLE.slot(f"full_energy_layer_{index}").fallback,
            )
        self.assertIn(
            "energy_ironclad.tres",
            CHARACTER_ART_BUNDLE.slot("large_energy_icon").fallback,
        )
        self.assertIn(
            "ironclad_energy_icon.png",
            CHARACTER_ART_BUNDLE.slot("compact_energy_icon").fallback,
        )

        recipe = CHARACTER_RECIPE.read_text(encoding="utf-8")
        for required in (
            'public override string? PlaceholderCharacterId => "ironclad";',
            '"res://images/atlases/ui_atlas.sprites/card/energy_ironclad.tres";',
            ": PlaceholderLargeEnergyIconPath;",
            "res://images/packed/sprite_fonts/ironclad_energy_icon.png",
            'EnergyColorName => "<stable custom energy prefix>";',
        ):
            self.assertIn(required, recipe)
        self.assertNotIn('EnergyColorName => "<color>";', recipe)
        self.assertNotIn('EnergyColorName => "red"', recipe)
        self.assertNotIn('EnergyIconHelper.GetPath("red")', recipe)
        # RitsuLib's patched GetPath reads every pool's BigEnergyIconPath to build its cache;
        # calling it from that getter recursed into a stack overflow at run start.
        self.assertNotIn(": EnergyIconHelper.GetPath(", recipe)

    def test_energy_counter_is_rendered_from_theme_colors_on_template_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            written = CHARACTER_ART_BUNDLE.render_energy_counter(images, "B83A2E", "#3A0F0A")

            self.assertEqual(
                [images / f"charui/orb_layer_{index}.png" for index in range(1, 6)],
                list(written),
            )
            with Image.open(written[0]) as disc:
                self.assertEqual(255, disc.getpixel((128, 128))[3])
                self.assertEqual(0, disc.getpixel((0, 0))[3])
            for slot, destination in zip(CHARACTER_ART_BUNDLE.fixed_template_slots, written[1:]):
                with Image.open(CHARACTER_ART_BUNDLE.template_source_path(slot)) as source, \
                        Image.open(destination) as rendered:
                    self.assertEqual((256, 256), rendered.size)
                    self.assertEqual("RGBA", rendered.mode)
                    self.assertEqual(
                        list(source.convert("RGBA").getchannel("A").getdata()),
                        list(rendered.getchannel("A").getdata()),
                    )
            with Image.open(written[3]) as ring:
                opaque = [pixel for pixel in ring.getdata() if pixel[3] > 200]
                red = sum(pixel[0] for pixel in opaque)
                blue = sum(pixel[2] for pixel in opaque)
                self.assertGreater(red, blue * 2)
            with self.assertRaisesRegex(CharacterArtValidationError, "RRGGBB"):
                CHARACTER_ART_BUNDLE.render_energy_counter(images, "red", "3A0F0A")

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

    def test_art_tiers_set_the_spend_and_skip_unpromoted_slots(self) -> None:
        self.assertEqual(
            {"minimal": 2, "standard": 4, "full": 5},
            {
                tier.name: CHARACTER_ART_BUNDLE.tier_generation_calls(tier.name)
                for tier in CHARACTER_ART_BUNDLE.tiers
            },
        )
        for tier in CHARACTER_ART_BUNDLE.tiers:
            names = {slot.name for slot in CHARACTER_ART_BUNDLE.tier_slots(tier.name)}
            self.assertNotIn("locked_selection_portrait", names)
            self.assertNotIn("map_marker", names)
        standard = {slot.name for slot in CHARACTER_ART_BUNDLE.tier_slots("standard")}
        self.assertIn("top_panel_icon_outline", standard)
        self.assertIn("full_energy_layer_5", standard)
        minimal = {slot.name for slot in CHARACTER_ART_BUNDLE.tier_slots("minimal")}
        self.assertEqual(
            {"selection_portrait", "combat_body", "rest_body", "merchant_body"}, minimal
        )
        with self.assertRaisesRegex(CharacterArtValidationError, "only required generated"):
            replace(
                CHARACTER_ART_BUNDLE,
                tiers=(CharacterArtTier("extra", ("selection_portrait", "map_marker")),),
            )
        with self.assertRaisesRegex(CharacterArtValidationError, "unknown Character art tier"):
            CHARACTER_ART_BUNDLE.tier("deluxe")

    def test_sheets_group_one_reference_role_and_tiers_take_whole_sheets(self) -> None:
        body = CHARACTER_ART_BUNDLE.sheet("body_sheet")
        self.assertEqual((1024, 1024), body.source_size)
        self.assertEqual(("combat_body", "rest_body", "merchant_body"), body.slots)
        self.assertIs(body, CHARACTER_ART_BUNDLE.sheet_for_slot("rest_body"))
        self.assertIsNone(CHARACTER_ART_BUNDLE.sheet_for_slot("selection_background"))

        invalid = {
            "mixes reference roles": CharacterArtSheet(
                "mixed", 2, 1, ("combat_body", "top_panel_icon"),
            ),
            "non-identity": CharacterArtSheet(
                "portrait", 2, 1, ("selection_portrait", "combat_body"),
            ),
            "fill its grid": CharacterArtSheet("short", 2, 2, ("combat_body", "rest_body")),
        }
        for message, sheet in invalid.items():
            with self.subTest(message), self.assertRaisesRegex(CharacterArtValidationError, message):
                replace(CHARACTER_ART_BUNDLE, sheets=(sheet,), tiers=())
        with self.assertRaisesRegex(CharacterArtValidationError, "lists part of sheet"):
            replace(
                CHARACTER_ART_BUNDLE,
                tiers=(CharacterArtTier("partial", ("selection_portrait", "combat_body")),),
            )

    def test_minimal_tier_review_requires_only_portrait_and_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            portrait = images / "charui/select.png"
            portrait.parent.mkdir(parents=True)
            Image.new("RGB", (132, 195), (80, 110, 140)).save(portrait)
            body = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            ImageDraw.Draw(body).rectangle((80, 26, 431, 485), fill=(40, 60, 90, 255))
            for name in ("combat", "rest", "merchant"):
                body.save(images / f"charui/{name}.png")

            with self.assertRaisesRegex(CharacterArtValidationError, "missing required"):
                CHARACTER_ART_BUNDLE.validate_outputs(images)
            checked = CHARACTER_ART_BUNDLE.validate_outputs(images, tier="minimal")
            contact, composite = CHARACTER_ART_BUNDLE.render_review(
                images, root / "review", tier="minimal"
            )

            self.assertEqual(4, len(checked))
            self.assertTrue(contact.is_file())
            self.assertIsNone(composite)

    # Center colors measured from the vanilla large card Energy icons (STS2 0.107.1 ui_atlas)
    # with their shipped card-pool EnergyOutlineColor.
    VANILLA_COST_ICONS = {
        "colorless": ((0xD5, 0xD5, 0xD5), (0x5C, 0x54, 0x40)),
        "defect": ((0x70, 0xB6, 0xEC), (0x1D, 0x56, 0x73)),
        "ironclad": ((0xF5, 0x7E, 0x19), (0x80, 0x20, 0x20)),
        "necrobinder": ((0xFC, 0x98, 0xC8), (0x80, 0x33, 0x67)),
        "quest": ((0x66, 0x39, 0x25), (0x43, 0x1E, 0x14)),
        "regent": ((0xF8, 0xC2, 0x2A), (0x80, 0x3D, 0x0E)),
        "silent": ((0x2E, 0xBD, 0x5E), (0x1A, 0x66, 0x25)),
    }

    def test_number_contrast_rule_accepts_every_vanilla_cost_icon(self) -> None:
        for name, (center, outline) in self.VANILLA_COST_ICONS.items():
            with self.subTest(name=name):
                self.assertEqual([], character_art.number_outline_problems(outline, center))

    def test_derived_outline_reads_on_any_center_and_keeps_hue(self) -> None:
        import colorsys

        for name, (center, _outline) in self.VANILLA_COST_ICONS.items():
            derived = character_art.derive_number_outline(center)
            with self.subTest(name=name):
                self.assertEqual([], character_art.number_outline_problems(
                    derived, center, character_art.DERIVE_MARGIN))
                if name != "colorless":
                    hue = colorsys.rgb_to_hls(*(v / 255 for v in center))[0]
                    got = colorsys.rgb_to_hls(*(v / 255 for v in derived))[0]
                    self.assertLess(min(abs(hue - got), 1 - abs(hue - got)), 0.05)
        gray = character_art.derive_number_outline((0xD5, 0xD5, 0xD5))
        self.assertEqual(len(set(gray)), 1, gray)
        for value in range(0, 256, 15):
            for center in ((value, value, value), (value, 255 - value, 128), (255, value, 0)):
                derived = character_art.derive_number_outline(center)
                self.assertEqual([], character_art.number_outline_problems(derived, center),
                                 (center, derived))

    def test_pale_outline_on_pale_icon_is_rejected(self) -> None:
        problems = character_art.number_outline_problems((0xE0, 0xC0, 0xF0), (0xEB, 0xBE, 0xFA))
        self.assertEqual(2, len(problems))

    def test_cli_derives_checks_and_rejects_number_outlines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            (images / "charui").mkdir(parents=True)
            icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            draw.regular_polygon((128, 128, 110), 8, fill=(150, 40, 200, 255))
            draw.ellipse((70, 70, 186, 186), fill=(235, 190, 250, 255))
            icon.save(images / "charui/energy_large.png")
            base = [
                sys.executable, str(Path(__file__).resolve().parents[1] / "character_art.py"),
                "--images-root", str(images), "--out-dir", str(root / "review"), "--present-only",
            ]
            derived = subprocess.run(base + ["--energy-colors", "6a2c8a,auto"],
                                     capture_output=True, text=True, check=False)
            self.assertEqual(0, derived.returncode, derived.stderr)
            self.assertIn("derived EnergyOutlineColor #", derived.stdout)
            self.assertIn("card cost: EnergyOutlineColor #", derived.stdout)
            self.assertIn("use EnergyLabelOutlineColor #", derived.stdout)

            rejected = subprocess.run(base + ["--number-outlines", "E0C0F0,"],
                                      capture_output=True, text=True, check=False)
            self.assertEqual(2, rejected.returncode)
            self.assertIn("EnergyOutlineColor #E0C0F0 is hard to read", rejected.stderr)

    def test_present_only_review_requires_only_the_groups_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            (images / "charui").mkdir(parents=True)
            body = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            ImageDraw.Draw(body).rectangle((80, 26, 431, 485), fill=(40, 60, 90, 255))
            body.save(images / "charui/combat.png")
            CHARACTER_ART_BUNDLE.render_energy_counter(images, "3a6ea5", "1d3a5c")

            checked = CHARACTER_ART_BUNDLE.validate_outputs(images, present_only=True)
            contact, composite = CHARACTER_ART_BUNDLE.render_review(
                images, root / "review", present_only=True
            )

            self.assertEqual(6, len(checked))
            self.assertTrue(contact.is_file())
            self.assertIsNotNone(composite)

    def test_present_only_still_requires_the_rest_of_a_started_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            (images / "charui").mkdir(parents=True)
            with self.assertRaisesRegex(CharacterArtValidationError, "no Character art output"):
                CHARACTER_ART_BUNDLE.validate_outputs(images, present_only=True)
            Image.new("RGBA", (88, 88), (0, 0, 0, 0)).save(images / "charui/icon.png")
            with self.assertRaisesRegex(CharacterArtValidationError,
                                        "missing required top_panel_icon_outline"):
                CHARACTER_ART_BUNDLE.validate_outputs(images, present_only=True)
            with self.assertRaisesRegex(CharacterArtValidationError, "not both"):
                CHARACTER_ART_BUNDLE.validate_outputs(images, tier="minimal", present_only=True)

    def test_cli_energy_render_then_present_only_review_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            (images / "charui").mkdir(parents=True)
            command = [
                sys.executable, str(Path(__file__).resolve().parents[1] / "character_art.py"),
                "--images-root", str(images), "--out-dir", str(root / "review"),
                "--energy-colors", "3a6ea5,1d3a5c",
            ]
            strict = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(2, strict.returncode)
            self.assertIn("Energy layers were written, but the review failed", strict.stderr)

            partial = subprocess.run(command + ["--present-only"], capture_output=True,
                                     text=True, check=False)
            self.assertEqual(0, partial.returncode, partial.stderr)
            self.assertIn("energy composite:", partial.stdout)
            self.assertNotIn("not in this review", partial.stdout)

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
