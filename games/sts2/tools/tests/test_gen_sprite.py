from __future__ import annotations

import base64
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image
from PIL import ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
GEN_SPRITE = TOOLS_DIR / "gen_sprite.py"
sys.path.insert(0, str(TOOLS_DIR))
import gen_sprite  # noqa: E402

_png = io.BytesIO()
Image.new("RGB", (4, 4)).save(_png, "PNG")
PNG_B64 = base64.b64encode(_png.getvalue())


def make_cue_sheet(path: Path, action_name: str) -> None:
    action = gen_sprite.CHARACTER_ART_BUNDLE.cue_action(action_name)
    cell = 100
    image = Image.new(
        "RGBA", (action.columns * cell, action.rows * cell), (255, 0, 255, 255)
    )
    draw = ImageDraw.Draw(image)
    for index in range(action.frame_count):
        row, column = divmod(index, action.columns)
        left = column * cell + 30
        top = row * cell + 10
        draw.rectangle((left, top, left + 39, top + 79), fill=(40, 130, 190, 255))
    image.save(path)


def make_body_sheet(path: Path) -> Image.Image:
    """A 2x2 magenta sheet with three standing bodies and drawn black grid lines."""
    image = Image.new("RGB", (1024, 1024), (255, 0, 255))
    draw = ImageDraw.Draw(image)
    for index in range(3):
        row, column = divmod(index, 2)
        left, top = column * 512, row * 512
        draw.rectangle((left + 120, top + 60, left + 380, top + 450), fill=(40 + 30 * index, 90, 110))
    draw.line((512, 0, 512, 1023), fill=(0, 0, 0), width=5)
    draw.line((0, 512, 1023, 512), fill=(0, 0, 0), width=5)
    image.save(path)
    return image


class GenSpriteTests(unittest.TestCase):
    def test_split_sheet_cells_drops_drawn_grid_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sheet = make_body_sheet(Path(tmp) / "sheet.png")
        cells = gen_sprite.split_sheet_cells(
            sheet, gen_sprite.CHARACTER_ART_BUNDLE.sheet("body_sheet")
        )

        self.assertEqual(["combat_body", "rest_body", "merchant_body"], [name for name, _ in cells])
        for _, cell in cells:
            border = [cell.getpixel((x, y)) for x in range(cell.width) for y in (0, cell.height - 1)]
            border += [cell.getpixel((x, y)) for y in range(cell.height) for x in (0, cell.width - 1)]
            self.assertTrue(all(pixel == (255, 0, 255) for pixel in border))

    def test_import_sheet_places_every_body_cell_on_its_slot_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = root / "sheet.png"
            out = root / "Mod" / "images"
            make_body_sheet(sheet)

            result = subprocess.run(
                [sys.executable, str(GEN_SPRITE), "import-sheet", "--sheet", "body_sheet",
                 "--input", str(sheet), "--out", str(out)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            for name in ("combat", "rest", "merchant"):
                with Image.open(out / "charui" / f"{name}.png") as placed:
                    self.assertEqual((512, 512), placed.size)
                    self.assertEqual(0, placed.getpixel((0, 0))[3])
                    self.assertEqual(255, placed.getchannel("A").getextrema()[1])
            self.assertEqual(str(sheet), result.stdout.strip().splitlines()[-1])

    def test_generate_sheet_spends_one_call_keeps_source_and_routes_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet_image = make_body_sheet(root / "sheet.png")
            portrait = root / "portrait.png"
            Image.new("RGB", (848, 1264), (80, 110, 140)).save(portrait)
            out = root / "Mod" / "images"
            parser = gen_sprite.build_parser()
            base = ["generate-sheet", "--sheet", "body_sheet", "--prompt", "p", "--out", str(out)]
            cfg = {"mode": "command", "command": ["x"]}

            with mock.patch.object(gen_sprite, "load_config", return_value=cfg), \
                    mock.patch.object(gen_sprite, "call_backend", return_value=sheet_image) as backend:
                with self.assertRaises(SystemExit):
                    gen_sprite.cmd_generate_sheet(parser.parse_args(base))
                backend.assert_not_called()
                code = gen_sprite.cmd_generate_sheet(
                    parser.parse_args([*base, "--identity-reference", str(portrait)])
                )

            self.assertEqual(0, code)
            self.assertEqual(1, backend.call_count)
            self.assertEqual((1024, 1024), backend.call_args.args[2])
            self.assertIn(portrait.resolve(), backend.call_args.kwargs["references"])
            self.assertTrue((root / "art-sources" / "generated" / "sheets" / "body_sheet.png").is_file())
            self.assertTrue((out / "charui" / "merchant.png").is_file())


    def test_cutout_fragment_cleanup_keeps_subject_cluster_and_removes_debris(self) -> None:
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 70, 70), fill=(40, 160, 120, 255))
        draw.rectangle((45, 18, 55, 24), fill=(180, 240, 210, 255))
        draw.rectangle((2, 2, 4, 4), fill=(20, 20, 20, 255))
        draw.rectangle((90, 80, 94, 84), fill=(20, 20, 20, 255))
        draw.rectangle((0, 0, 99, 99), outline=(20, 20, 20, 255), width=5)

        cleaned = gen_sprite.remove_cutout_fragments(image)

        self.assertEqual(0, cleaned.getpixel((3, 3))[3])
        self.assertEqual(0, cleaned.getpixel((92, 82))[3])
        self.assertEqual(255, cleaned.getpixel((50, 20))[3])
        self.assertEqual(255, cleaned.getpixel((50, 50))[3])

    def test_shipped_m6_reference_pools_match_supported_profiles(self) -> None:
        root = TOOLS_DIR.parent / "skills" / "sts2api" / "reference" / "art-samples"
        expected = {
            "enchantment": (20, (64, 64)),
            "orb": (5, (100, 100)),
            "monster": (3, (512, 512)),
            "event": (6, (1616, 1616)),
            "rest_site_option": (3, (256, 169)),
            "character_select": (3, (132, 195)),
            "character_icon": (3, (88, 88)),
            "character_combat": (3, (512, 512)),
            "character_rest": (3, (512, 512)),
        }

        for spec, (count, size) in expected.items():
            with self.subTest(spec=spec):
                paths = sorted((root / spec).glob("*.png"))
                self.assertEqual(count, len(paths))
                for path in paths:
                    with Image.open(path) as image:
                        self.assertEqual(size, image.size, path.name)

        self.assertEqual(
            {"axebot.png", "ceremonial_beast.png", "crossbow_ruby_raider.png"},
            {path.name for path in (root / "monster").glob("*.png")},
        )

    def test_character_specs_match_their_current_promotion_state(self) -> None:
        expected = {
            "character_select": ((132, 195), "cover", False, True),
            "character_select_locked": ((132, 195), "cover", False, False),
            "character_icon": ((88, 88), "contain", True, True),
            "character_map_marker": ((49, 64), "contain", True, False),
            "character_background": ((1920, 1200), "cover", False, True),
            "character_combat": ((512, 512), "contain", True, True),
            "character_rest": ((512, 512), "contain", True, True),
            "character_merchant": ((512, 512), "contain", True, True),
            "character_energy": ((256, 256), "contain", True, True),
            "character_energy_large": ((256, 256), "contain", True, True),
            "character_energy_text": ((24, 24), "contain", True, True),
        }
        for spec, (size, fit, chroma, verified) in expected.items():
            with self.subTest(spec=spec):
                info = gen_sprite.SPECS[spec]
                self.assertEqual(size, info["size"])
                self.assertEqual(fit, info["fit"])
                self.assertEqual(chroma, info["chroma"])
                self.assertEqual(verified, info["verified"])

    def test_character_cue_import_stages_until_complete_then_writes_atomic_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            images = project / "CueMod" / "images"
            inputs = root / "inputs"
            inputs.mkdir()

            for index, action in enumerate(
                gen_sprite.CHARACTER_ART_BUNDLE.combat_cues.actions
            ):
                source = inputs / f"{action.name}.png"
                make_cue_sheet(source, action.name)
                result = subprocess.run(
                    [
                        sys.executable, str(GEN_SPRITE), "import",
                        "--spec", action.source_spec,
                        "--slug", action.name,
                        "--input", str(source),
                        "--out", str(images),
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(
                    (project / "art-sources" / "character-cues" / f"{action.name}.png").is_file()
                )
                if index < 3:
                    self.assertIn("bundle incomplete", result.stdout)
                    self.assertFalse((images / "charui" / "cues").exists())

            self.assertIn("normalized complete bundle", result.stdout)
            runtime_frames = sorted((images / "charui" / "cues").rglob("*.png"))
            self.assertEqual(18, len(runtime_frames))
            self.assertTrue(
                (project / "art-review" / "character-cues" / "pipeline-meta.json").is_file()
            )
            self.assertTrue(
                (project / "art-review" / "character-cues" /
                 "character-cues-contact-sheet.png").is_file()
            )

    def test_character_icon_import_writes_exact_transparent_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 30), (40, 160, 120, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_icon", "--slug", "wayfinder_icon",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "charui" / "wayfinder_icon.png"
            outline_path = out / "charui" / "wayfinder_icon_outline.png"
            self.assertTrue(destination.is_file())
            self.assertTrue(outline_path.is_file())
            with Image.open(destination) as image:
                self.assertEqual((88, 88), image.size)
                self.assertEqual("RGBA", image.mode)
                bounds = image.getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 3)
                self.assertGreaterEqual(bounds[1], 3)
                self.assertLessEqual(bounds[2], 85)
                self.assertLessEqual(bounds[3], 85)
            with Image.open(outline_path) as outline:
                self.assertEqual((88, 88), outline.size)
                self.assertEqual("RGBA", outline.mode)
                self.assertEqual(
                    {(255, 255, 255)},
                    {pixel[:3] for pixel in outline.getdata() if pixel[3]},
                )

    def test_character_cutout_removes_edge_connected_soft_magenta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (222, 27, 136, 255))
            ImageDraw.Draw(image).rectangle(
                (35, 15, 64, 84), fill=(30, 80, 150, 255)
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_rest", "--slug", "rest",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "rest.png") as normalized:
                self.assertEqual(0, normalized.getpixel((0, 0))[3])
                self.assertEqual(255, normalized.getpixel((256, 256))[3])
            log = (out / ".gen_sprite.log").read_text(encoding="utf-8")
            self.assertIn("edge-connected soft magenta", log)

    def test_magenta_subject_on_green_background_keeps_its_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
            ImageDraw.Draw(image).ellipse((25, 25, 74, 74), fill=(200, 40, 200, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "relic", "--slug", "orchid",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "relics" / "orchid.png") as normalized:
                self.assertEqual(0, normalized.getpixel((0, 0))[3])
                self.assertEqual((200, 40, 200, 255), normalized.getpixel((128, 128)))
            log = (out / ".gen_sprite.log").read_text(encoding="utf-8")
            self.assertIn("applied green chroma-key", log)

    def test_character_icon_drops_disconnected_debris_before_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (222, 27, 136, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle((35, 15, 64, 84), fill=(30, 80, 150, 255))
            draw.rectangle((0, 0, 4, 4), fill=(20, 40, 90, 255))
            draw.rectangle((95, 95, 99, 99), fill=(20, 40, 90, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_icon", "--slug", "icon",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "icon.png") as normalized:
                bounds = normalized.getchannel("A").getbbox()
                self.assertGreater(bounds[0], 3)
                self.assertLess(bounds[2], 85)
            with Image.open(out / "charui" / "icon_outline.png") as outline:
                self.assertEqual(0, outline.getpixel((0, 0))[3])
                self.assertEqual(0, outline.getpixel((87, 87))[3])
            log = (out / ".gen_sprite.log").read_text(encoding="utf-8")
            self.assertIn("disconnected Character cut-out", log)

    def test_alpha_outline_uses_exact_proportional_white_expansion(self) -> None:
        image = Image.new("RGBA", (88, 88), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((20, 30, 39, 49), fill=(30, 90, 170, 128))

        outline = gen_sprite.derive_alpha_outline(image)

        self.assertEqual((88, 88), outline.size)
        self.assertEqual(3, gen_sprite.outline_expansion_radius(outline.size))
        self.assertEqual(82 / 88, gen_sprite.outline_safe_fill(outline.size))
        self.assertEqual((17, 27, 43, 53), outline.getchannel("A").getbbox())
        self.assertEqual((255, 255, 255, 255), outline.getpixel((17, 27)))
        self.assertEqual((255, 255, 255, 255), outline.getpixel((20, 30)))
        self.assertEqual((255, 255, 255, 0), outline.getpixel((0, 0)))

    def test_alpha_outline_rejects_an_empty_main_icon(self) -> None:
        with self.assertRaisesRegex(SystemExit, "empty final alpha"):
            gen_sprite.derive_alpha_outline(
                Image.new("RGBA", (88, 88), (0, 0, 0, 0))
            )

    def test_relic_import_writes_main_big_and_derived_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (80, 100), (0, 0, 0, 0))
            ImageDraw.Draw(image).ellipse((10, 20, 69, 79), fill=(40, 160, 120, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "relic", "--slug", "first_bearing",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            main_path = out / "relics" / "first_bearing.png"
            big_path = out / "relics" / "big" / "first_bearing.png"
            outline_path = out / "relics" / "first_bearing_outline.png"
            self.assertTrue(main_path.is_file())
            self.assertTrue(big_path.is_file())
            self.assertTrue(outline_path.is_file())
            self.assertEqual(main_path.read_bytes(), big_path.read_bytes())
            self.assertNotEqual(main_path.read_bytes(), outline_path.read_bytes())
            with Image.open(main_path) as main, Image.open(outline_path) as outline:
                self.assertEqual((256, 256), main.size)
                self.assertEqual(main.size, outline.size)
                self.assertEqual(8, gen_sprite.outline_expansion_radius(outline.size))
                bounds = main.convert("RGBA").getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 8)
                self.assertGreaterEqual(bounds[1], 8)
                self.assertLessEqual(bounds[2], 248)
                self.assertLessEqual(bounds[3], 248)
                main_alpha = main.convert("RGBA").getchannel("A")
                outline_alpha = outline.convert("RGBA").getchannel("A")
                self.assertTrue(all(
                    not main_value or outline_value
                    for main_value, outline_value in zip(
                        main_alpha.getdata(), outline_alpha.getdata()
                    )
                ))
                self.assertEqual(
                    {(255, 255, 255)},
                    {pixel[:3] for pixel in outline.convert("RGBA").getdata() if pixel[3]},
                )
                self.assertEqual(0, outline.getpixel((0, 0))[3])

    def run_import(self, spec: str, source: Path, out: Path, *extra: str):
        return subprocess.run(
            [
                sys.executable, str(GEN_SPRITE), "import",
                "--spec", spec, "--slug", "keyed",
                "--input", str(source), "--out", str(out), *extra,
            ],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_cutout_import_keys_by_spec_default_and_honors_no_chroma(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            image = Image.new("RGB", (100, 100), (255, 0, 255))
            ImageDraw.Draw(image).ellipse((20, 20, 79, 79), fill=(40, 160, 120))
            image.save(source)

            keyed = self.run_import("potion", source, root / "default")
            self.assertEqual(0, keyed.returncode, keyed.stderr)
            self.assertNotIn("warning", keyed.stdout)
            with Image.open(root / "default" / "potions" / "keyed.png") as result:
                self.assertEqual(0, result.getpixel((0, 0))[3])

            opaque = self.run_import("potion", source, root / "opaque", "--no-chroma")
            self.assertEqual(0, opaque.returncode, opaque.stderr)
            with Image.open(root / "opaque" / "potions" / "keyed.png") as result:
                self.assertEqual(255, result.getpixel((0, 0))[3])

    def test_cutout_import_neutralizes_key_spill_on_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            image = Image.new("RGB", (100, 100), (255, 0, 255))
            draw = ImageDraw.Draw(image)
            draw.ellipse((18, 18, 81, 81), fill=(150, 30, 150))  # antialiased blend ring
            draw.ellipse((20, 20, 79, 79), fill=(40, 40, 48))
            image.save(source)

            result = self.run_import("relic", source, root / "images")

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(root / "images" / "relics" / "keyed.png") as keyed:
                tinted = [p for p in keyed.convert("RGBA").getdata()
                          if p[3] and min(p[0], p[2]) - p[1] > 40]
            self.assertEqual([], tinted)

    def test_import_crop_uses_only_the_source_pixel_box(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "card.png"
            image = Image.new("RGB", (400, 600), (200, 30, 30))       # frame and text
            ImageDraw.Draw(image).rectangle((100, 100, 299, 299), fill=(30, 60, 200))
            image.save(source)

            result = self.run_import("relic", source, root / "images", "--no-chroma",
                                     "--crop", "100,100,200,200")
            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(root / "images" / "relics" / "keyed.png") as placed:
                colors = {p[:3] for p in placed.convert("RGBA").getdata() if p[3]}
            self.assertTrue(all(b > r for r, _g, b in colors), colors)

            outside = self.run_import("relic", source, root / "other", "--crop", "300,500,200,200")
            self.assertNotEqual(0, outside.returncode)
            self.assertIn("leaves the 400x600 source", outside.stdout + outside.stderr)

    def test_grid_preview_keeps_source_resolution_and_validates_boxes(self) -> None:
        self.assertEqual(50, gen_sprite.grid_step((600, 840)))
        self.assertEqual(100, gen_sprite.grid_step((1200, 1800)))
        self.assertEqual((1, 2, 3, 4), gen_sprite.parse_box("1,2,3,4"))
        with self.assertRaises(gen_sprite.argparse.ArgumentTypeError):
            gen_sprite.parse_box("1,2,0,4")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "card.png"
            Image.new("RGB", (300, 420), (220, 210, 190)).save(source)
            run = lambda *extra: subprocess.run(
                [sys.executable, str(GEN_SPRITE), "grid", "--input", str(source),
                 "--out", str(root / "grid.png"), *extra],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            ok = run("--box", "10,20,100,80")
            self.assertEqual(0, ok.returncode, ok.stderr)
            self.assertIn("source 300x420", ok.stdout)
            with Image.open(root / "grid.png") as grid:
                self.assertEqual((300, 420), grid.size)
            bad = run("--box", "250,400,100,80")
            self.assertNotEqual(0, bad.returncode)

    def test_cutout_import_warns_when_the_subject_was_cut_off(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            image = Image.new("RGB", (100, 100), (255, 0, 255))
            ImageDraw.Draw(image).rectangle((30, 20, 69, 99), fill=(40, 160, 120))  # hem cut at the bottom
            image.save(source)

            result = self.run_import("relic", source, root / "images")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("touches the bottom edge", result.stdout)

    def test_edge_check_ignores_margins_and_stray_pixels(self) -> None:
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        ImageDraw.Draw(image).ellipse((20, 20, 79, 79), fill=(40, 160, 120, 255))
        image.putpixel((50, 99), (40, 160, 120, 255))
        self.assertEqual([], gen_sprite.cutout_edges_touched(image))
        ImageDraw.Draw(image).rectangle((0, 40, 30, 60), fill=(40, 160, 120, 255))
        self.assertEqual(["left"], gen_sprite.cutout_edges_touched(image))

    def test_cutout_import_warns_when_the_background_was_not_keyed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGB", (100, 100), (30, 30, 60))
            ImageDraw.Draw(image).ellipse((20, 20, 79, 79), fill=(40, 160, 120))
            image.save(source)

            result = self.run_import("relic", source, out)

            self.assertEqual(0, result.returncode, result.stderr)
            lines = result.stdout.splitlines()
            self.assertTrue(any(line.startswith("[gen_sprite] warning:") for line in lines))
            self.assertEqual(str(out / "relics" / "keyed.png"), lines[-1])

    def test_backend_request_size_follows_the_spec_orientation(self) -> None:
        self.assertEqual("1536x1024", gen_sprite.request_size_for(gen_sprite.resolve_size("card", None)))
        self.assertEqual("1536x1024", gen_sprite.request_size_for(gen_sprite.resolve_size("event", None)))
        self.assertEqual("1024x1536", gen_sprite.request_size_for(gen_sprite.resolve_size("character_select", None)))
        self.assertEqual("1024x1024", gen_sprite.request_size_for(gen_sprite.resolve_size("relic", None)))

        sent: list[dict] = []

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"data": [{"b64_json": "%s"}]}' % PNG_B64

        def fake_urlopen(request, timeout):
            sent.append(json.loads(request.data))
            return Response()

        cfg = {"base_url": "https://example.test/v1", "api_key": "test", "model": "m"}
        with mock.patch.object(gen_sprite.urllib.request, "urlopen", fake_urlopen):
            gen_sprite.call_backend(cfg, "p", (3440, 1613), lambda _: None)
            gen_sprite.call_backend({**cfg, "request_size": "1024x1024"}, "p", (3440, 1613), lambda _: None)
        self.assertEqual(["1536x1024", "1024x1024"], [body["size"] for body in sent])

    def test_character_background_import_writes_opaque_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (20, 10), (20, 80, 160)).save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_background", "--slug", "wayfinder_bg",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "charui" / "wayfinder_bg.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((1920, 1200), image.size)
                self.assertEqual("RGBA", image.mode)
                self.assertEqual(255, image.getpixel((0, 0))[3])

    def test_character_selection_import_preserves_source_inside_safe_box(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGB", (132, 195), (20, 80, 160))
            ImageDraw.Draw(image).rectangle(
                (0, 0, 131, 194), outline=(240, 220, 40), width=3
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_select", "--slug", "select",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "select.png") as normalized:
                self.assertEqual((132, 195), normalized.size)
                self.assertEqual((255, 255), normalized.getchannel("A").getextrema())
                self.assertNotEqual(
                    normalized.getpixel((0, 0)), normalized.getpixel((6, 9))
                )

    def test_character_combat_import_pins_alpha_box_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (240, 300), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle(
                (40, 0, 199, 299), fill=(80, 160, 120, 255)
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_combat", "--slug", "combat",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "combat.png") as normalized:
                bounds = normalized.getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 26)
                self.assertGreaterEqual(bounds[1], 26)
                self.assertLessEqual(bounds[2], 486)
                self.assertEqual(486, bounds[3])

    def test_reference_pool_selects_spec_subdir_and_randomly_caps_at_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / "enchantment"
            pool.mkdir()
            expected_pool = []
            for index in range(5):
                path = pool / f"style-{index}.png"
                path.touch()
                expected_pool.append(path)
            decoy = root / "card"
            decoy.mkdir()
            (decoy / "wrong-family.png").touch()
            chosen = [expected_pool[4], expected_pool[1], expected_pool[3]]

            with mock.patch.object(gen_sprite.random, "SystemRandom") as factory:
                factory.return_value.sample.return_value = chosen
                references = gen_sprite.resolve_references(
                    str(root), 3, lambda _message: None, spec="enchantment"
                )

            self.assertEqual(chosen, references)
            factory.return_value.sample.assert_called_once_with(expected_pool, 3)

    def test_missing_named_reference_stops_before_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            present = Path(tmp) / "a.png"
            Image.new("RGB", (8, 8)).save(present)
            with self.assertRaises(SystemExit) as raised:
                gen_sprite.resolve_references(
                    f"{present},{Path(tmp) / 'missing.png'}", 3, lambda _: None, spec="card")
            self.assertIn("missing.png", str(raised.exception))

    def test_character_reference_alias_never_falls_back_to_the_root_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / "character_icon"
            pool.mkdir()
            expected = pool / "icon.png"
            expected.touch()
            (root / "wrong-family.png").touch()

            references = gen_sprite.resolve_references(
                str(root), 3, lambda _message: None, spec="character_energy_text"
            )

            self.assertEqual([expected], references)

    def test_character_background_uses_its_own_reference_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background_pool = root / "character_background"
            background_pool.mkdir()
            expected = background_pool / "defect.png"
            expected.touch()
            portrait_pool = root / "character_select"
            portrait_pool.mkdir()
            (portrait_pool / "wrong-small-portrait.png").touch()

            references = gen_sprite.resolve_references(
                str(root), 3, lambda _message: None, spec="character_background"
            )

            self.assertEqual([expected], references)

    def test_character_identity_routing_adds_portrait_only_for_identity_sensitive_specs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = root / "select.png"
            Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)
            messages: list[str] = []

            references = gen_sprite.resolve_references(
                None,
                3,
                messages.append,
                spec="character_combat",
                identity_reference=str(identity),
            )
            self.assertEqual([identity.resolve()], references)

            with self.assertRaisesRegex(SystemExit, "palette-only"):
                gen_sprite.resolve_references(
                    None,
                    3,
                    messages.append,
                    spec="character_icon",
                    identity_reference=str(identity),
                )

    def test_character_energy_import_preserves_shared_source_canvas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (255, 0, 255, 255))
            ImageDraw.Draw(image).rectangle((40, 40, 59, 59), fill=(40, 160, 120, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_energy", "--slug", "orb_layer_1",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "orb_layer_1.png") as normalized:
                bbox = normalized.getchannel("A").getbbox()
                self.assertIsNotNone(bbox)
                self.assertLess(bbox[2] - bbox[0], 100)
                self.assertLess(bbox[3] - bbox[1], 100)

    def test_character_large_and_text_energy_imports_write_distinct_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (80, 80), (40, 160, 120, 255)).save(source)

            for spec, slug, expected_size in (
                ("character_energy_large", "energy_large", (256, 256)),
                ("character_energy_text", "energy_text", (24, 24)),
            ):
                result = subprocess.run(
                    [
                        sys.executable, str(GEN_SPRITE), "import",
                        "--spec", spec, "--slug", slug,
                        "--input", str(source), "--out", str(out),
                    ],
                    capture_output=True, text=True, encoding="utf-8", check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                with Image.open(out / "charui" / f"{slug}.png") as normalized:
                    self.assertEqual(expected_size, normalized.size)

    def test_monster_import_writes_one_exact_static_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 30), (230, 170, 40, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "monster",
                    "--slug",
                    "example_monster",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "monsters" / "example_monster.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((360, 360), image.size)
                self.assertEqual("RGBA", image.mode)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_orb_import_writes_one_exact_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 10), (90, 180, 230, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "orb",
                    "--slug",
                    "shelter_orb",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "orbs" / "shelter_orb.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((100, 100), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_enchantment_import_writes_one_exact_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 10), (220, 180, 40, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "enchantment",
                    "--slug",
                    "guarded",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "enchantments" / "guarded.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((64, 64), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_event_import_writes_one_exact_portrait(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (20, 10), (20, 80, 160)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "event",
                    "--slug",
                    "gilded-signpost",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "events" / "gilded-signpost.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((3440, 1613), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_rest_site_option_import_writes_one_exact_verified_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (40, 20), (90, 50, 30)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "rest_site_option",
                    "--slug",
                    "quiet-forge",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "rest_site_options" / "quiet-forge.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((256, 169), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

            listed = subprocess.run(
                [sys.executable, str(GEN_SPRITE), "list-specs"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, listed.returncode, listed.stderr)
            line = next(
                item for item in listed.stdout.splitlines()
                if item.startswith("rest_site_option")
            )
            self.assertIn("rest_site_options", line)
            self.assertIn("256x169", line)
            self.assertNotIn("*not live-verified", line)

    def test_event_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        event_line = next(
            line for line in result.stdout.splitlines() if line.startswith("event")
        )
        self.assertIn("events", event_line)
        self.assertIn("3440x1613", event_line)
        self.assertNotIn("*not live-verified", event_line)

    def test_enchantment_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        enchantment_line = next(
            line for line in result.stdout.splitlines() if line.startswith("enchantment")
        )
        self.assertIn("enchantments", enchantment_line)
        self.assertIn("64x64", enchantment_line)
        self.assertNotIn("*not live-verified", enchantment_line)

    def test_orb_icon_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        orb_line = next(
            line for line in result.stdout.splitlines() if line.startswith("orb")
        )
        self.assertIn("orbs", orb_line)
        self.assertIn("100x100", orb_line)
        self.assertNotIn("*not live-verified", orb_line)

    def test_monster_static_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        monster_line = next(
            line for line in result.stdout.splitlines() if line.startswith("monster")
        )
        self.assertIn("monsters", monster_line)
        self.assertIn("360x360", monster_line)
        self.assertNotIn("*not live-verified", monster_line)


if __name__ == "__main__":
    unittest.main()
