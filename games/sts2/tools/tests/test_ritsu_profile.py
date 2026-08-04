from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
from ritsu_profile import (  # noqa: E402
    PROFILE,
    RitsuProfileError,
    resolve_runtime_asset,
    validate_host_version,
    validate_project_contract,
    validate_runtime_asset,
)
from scaffold import generate  # noqa: E402


class RitsuProfileTests(unittest.TestCase):
    def test_outer_directory_must_differ_from_mod_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "outer project directory"):
                generate(Path(tmp) / "EmptyRitsu", "EmptyRitsu", "OpenMod")

    def test_generated_empty_project_is_pinned_and_base_lib_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            generate(project, "EmptyRitsu", "OpenMod")
            summary = validate_project_contract(project, "EmptyRitsu")
            self.assertIn(PROFILE.profile_id, summary)
            manifest = json.loads((project / "EmptyRitsu.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["dependencies"], [{"id": "STS2-RitsuLib", "min_version": "0.5.4"}])
            csproj = (project / "EmptyRitsu.csproj").read_text(encoding="utf-8")
            main = (project / "EmptyRitsuCode" / "MainFile.cs").read_text(encoding="utf-8")
            self.assertNotIn("BaseLib", csproj)
            self.assertIn("public static partial class MainFile", main)
            self.assertIn("static partial void RegisterContent();", main)
            self.assertIn("RitsuLibFramework.CreateLogger(ModId)", main)

    def test_default_beta_package_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            generate(project, "EmptyRitsu", "OpenMod")
            csproj = project / "EmptyRitsu.csproj"
            text = csproj.read_text(encoding="utf-8").replace(
                PROFILE.package_id, "STS2.RitsuLib"
            )
            csproj.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "default beta-facing"):
                validate_project_contract(project, "EmptyRitsu")

    def test_runtime_variant_directory_and_zip_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "STS2-RitsuLib"
            variant = root / "lib" / PROFILE.host_version
            variant.mkdir(parents=True)
            (root / PROFILE.runtime_dll).write_bytes(b"loader")
            (root / "mod_manifest.json").write_text(json.dumps({
                "id": PROFILE.runtime_mod_id,
                "version": PROFILE.framework_version,
                "min_game_version": PROFILE.host_version,
                "dependencies": [],
            }), encoding="utf-8")
            (variant / PROFILE.runtime_dll).write_bytes(b"dll")
            (variant / "compat-target.txt").write_text(PROFILE.host_version + "\n", encoding="utf-8")
            (root / "ritsulib-variants.manifest").write_text(json.dumps({
                "schema": 1,
                "variants": [{
                    "compatTarget": PROFILE.host_version,
                    "directory": f"lib/{PROFILE.host_version}",
                    "assembly": PROFILE.runtime_dll,
                    "sha256": hashlib.sha256(b"dll").hexdigest(),
                }],
            }), encoding="utf-8")
            self.assertIn(PROFILE.host_version, validate_runtime_asset(root))

            archive = Path(tmp) / "variant-pack.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr(PROFILE.runtime_dll, b"loader")
                zf.writestr("mod_manifest.json", json.dumps({
                    "id": PROFILE.runtime_mod_id,
                    "version": PROFILE.framework_version,
                    "min_game_version": PROFILE.host_version,
                    "dependencies": [],
                }))
                zf.writestr(f"lib/{PROFILE.host_version}/{PROFILE.runtime_dll}", b"dll")
                zf.writestr(f"lib/{PROFILE.host_version}/compat-target.txt", PROFILE.host_version + "\n")
                zf.writestr(
                    "ritsulib-variants.manifest",
                    json.dumps({
                        "schema": 1,
                        "variants": [{
                            "compatTarget": PROFILE.host_version,
                            "directory": f"lib/{PROFILE.host_version}",
                            "assembly": PROFILE.runtime_dll,
                            "sha256": hashlib.sha256(b"dll").hexdigest(),
                        }],
                    }),
                )
            self.assertIn(PROFILE.host_version, validate_runtime_asset(archive))

    def test_newer_runtime_version_is_accepted_but_older_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "STS2-RitsuLib"
            variant = root / "lib" / PROFILE.host_version
            variant.mkdir(parents=True)
            (root / PROFILE.runtime_dll).write_bytes(b"loader")
            (variant / PROFILE.runtime_dll).write_bytes(b"dll")
            (variant / "compat-target.txt").write_text(
                PROFILE.host_version + "\n", encoding="utf-8"
            )
            (root / "ritsulib-variants.manifest").write_text(json.dumps({
                "schema": 1,
                "variants": [{
                    "compatTarget": PROFILE.host_version,
                    "directory": f"lib/{PROFILE.host_version}",
                    "assembly": PROFILE.runtime_dll,
                    "sha256": hashlib.sha256(b"dll").hexdigest(),
                }],
            }), encoding="utf-8")

            manifest = {
                "id": PROFILE.runtime_mod_id,
                "version": "0.5.9",
                "min_game_version": PROFILE.host_version,
                "dependencies": [],
            }
            manifest_path = root / "mod_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIn("RitsuLib 0.5.9", validate_runtime_asset(root))

            manifest["version"] = "0.5.3"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "older than the required minimum"):
                validate_runtime_asset(root)

    def test_runtime_discovery_reuses_official_workshop_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            steamapps = Path(tmp) / "steamapps"
            game = steamapps / "common" / "Slay the Spire 2"
            mods = game / "mods"
            workshop = (
                steamapps
                / "workshop"
                / "content"
                / PROFILE.steam_app_id
                / PROFILE.workshop_item_id
            )
            game.mkdir(parents=True)
            workshop.mkdir(parents=True)

            selected = resolve_runtime_asset(game, mods)
            self.assertEqual("Steam Workshop", selected.source)
            self.assertEqual(workshop, selected.path)
            self.assertEqual((), selected.alternates)

            local = mods / PROFILE.runtime_mod_id
            local.mkdir(parents=True)
            selected = resolve_runtime_asset(game, mods)
            self.assertEqual("mods directory", selected.source)
            self.assertEqual(local, selected.path)
            self.assertEqual((workshop,), selected.alternates)

    def test_runtime_discovery_reports_both_searched_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "steamapps" / "common" / "Slay the Spire 2"
            game.mkdir(parents=True)
            with self.assertRaisesRegex(
                RitsuProfileError,
                f"official Steam Workshop item {PROFILE.workshop_item_id}",
            ):
                resolve_runtime_asset(game, game / "mods")

    def test_wrong_runtime_variant_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "STS2-RitsuLib"
            variant = root / "lib" / "0.109.0"
            variant.mkdir(parents=True)
            (root / PROFILE.runtime_dll).write_bytes(b"loader")
            (root / "mod_manifest.json").write_text(json.dumps({
                "id": PROFILE.runtime_mod_id,
                "version": PROFILE.framework_version,
                "min_game_version": PROFILE.host_version,
                "dependencies": [],
            }), encoding="utf-8")
            (variant / PROFILE.runtime_dll).write_bytes(b"dll")
            (variant / "compat-target.txt").write_text("0.109.0\n", encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "no matching"):
                validate_runtime_asset(root)

    def test_host_release_version_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            release = game / "data_sts2_windows_x86_64" / "game"
            release.mkdir(parents=True)
            (release / "release_info.json").write_text(
                json.dumps({"version": "v" + PROFILE.host_version}), encoding="utf-8"
            )
            self.assertIn(PROFILE.host_version, validate_host_version(game))
            (release / "release_info.json").write_text(json.dumps({"version": "0.108.0"}), encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "stable 0.107.1"):
                validate_host_version(game)


if __name__ == "__main__":
    unittest.main()
