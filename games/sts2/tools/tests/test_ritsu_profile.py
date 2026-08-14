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
    RuntimeCompileProfile,
    find_manifest,
    local_mods_dir,
    resolve_runtime_asset,
    resolve_runtime_compile_profile,
    validate_host_version,
    validate_project_contract,
    validate_runtime_asset,
)
from scaffold import generate  # noqa: E402


class RitsuProfileTests(unittest.TestCase):
    def test_outer_directory_must_differ_from_mod_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "outer project directory"):
                generate(Path(tmp) / "EmptyRitsu", "EmptyRitsu", "SkillTheSpire")

    def test_scaffold_uses_bundled_sdk_and_pinned_local_assemblies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            compile_hash = hashlib.sha256(b"local-compat").hexdigest()
            compile_profile = RuntimeCompileProfile(
                "0.5.12",
                Path(tmp) / "runtime" / PROFILE.runtime_dll,
                compile_hash,
            )
            generate(
                project,
                "EmptyRitsu",
                "SkillTheSpire",
                compile_profile=compile_profile,
            )
            summary = validate_project_contract(project, "EmptyRitsu")
            self.assertIn(PROFILE.profile_id, summary)
            self.assertIn("local compile runtime 0.5.12", summary)
            manifest = json.loads(
                (project / "mod_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["dependencies"],
                [{"id": "STS2-RitsuLib", "min_version": PROFILE.framework_version}],
            )
            csproj = (project / "EmptyRitsu.csproj").read_text(encoding="utf-8")
            path_props = (project / "Sts2PathDiscovery.props").read_text(encoding="utf-8")
            main = (project / "EmptyRitsuCode" / "MainFile.cs").read_text(encoding="utf-8")
            self.assertNotIn("BaseLib", csproj)
            self.assertNotIn("<PackageReference", csproj)
            self.assertIn('<None Include="mod_manifest.json" />', csproj)
            self.assertIn(
                "$(MSBuildProjectDirectory)\\mod_manifest.json",
                csproj,
            )
            self.assertNotIn("$(MSBuildProjectName).json", csproj)
            self.assertIn(
                "<ModsPath Condition=\"'$(ModsPath)' == ''\">"
                "$(Sts2Dir)/SlayTheSpire2.app/Contents/MacOS/mods/</ModsPath>",
                path_props,
            )
            self.assertIn("<RitsuLibCompileVersion>0.5.12</RitsuLibCompileVersion>", csproj)
            self.assertIn(
                f"<RitsuLibCompileAssemblySha256>{compile_hash}</RitsuLibCompileAssemblySha256>",
                csproj,
            )
            for reference in (
                "sts2",
                "0Harmony",
                "GodotSharp",
                "System.IO.Hashing",
                "STS2-RitsuLib",
            ):
                self.assertIn(f'<Reference Include="{reference}"', csproj)
            sdk = (
                project
                / "skillthespire"
                / "sdk"
                / f"Godot.NET.Sdk.{PROFILE.godot_sdk_version}"
                / "Sdk"
            )
            for name in (
                "Android.props",
                "iOSNativeAOT.props",
                "iOSNativeAOT.targets",
                "Sdk.props",
                "Sdk.targets",
                "SdkPackageVersions.props",
            ):
                self.assertTrue((sdk / name).is_file(), name)
            self.assertIn("public static partial class MainFile", main)
            self.assertIn("static partial void RegisterContent();", main)
            self.assertIn("RitsuLibFramework.CreateLogger(ModId)", main)
            self.assertIn('CompileFrameworkVersion = "0.5.12"', main)

    def test_manifest_name_is_canonical_and_legacy_is_unambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            canonical = project / "mod_manifest.json"
            legacy = project / "ExampleMod.json"

            canonical.write_text("{}\n", encoding="utf-8")
            self.assertEqual(canonical, find_manifest(project, "ExampleMod"))

            canonical.unlink()
            legacy.write_text("{}\n", encoding="utf-8")
            self.assertEqual(legacy, find_manifest(project, "ExampleMod"))

            canonical.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "both canonical and legacy"):
                find_manifest(project, "ExampleMod")

    def test_local_mods_dir_is_adjacent_to_the_platform_executable(self) -> None:
        game = Path("steamapps") / "common" / "Slay the Spire 2"
        self.assertEqual(game / "mods", local_mods_dir(game, "win32"))
        self.assertEqual(game / "mods", local_mods_dir(game, "linux"))
        self.assertEqual(
            game / "SlayTheSpire2.app" / "Contents" / "MacOS" / "mods",
            local_mods_dir(game, "darwin"),
        )

    def test_generated_project_rejects_any_package_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            generate(project, "EmptyRitsu", "SkillTheSpire")
            csproj = project / "EmptyRitsu.csproj"
            text = csproj.read_text(encoding="utf-8").replace(
                "</Project>",
                '<ItemGroup><PackageReference Include="Example" Version="1.0.0" /></ItemGroup></Project>',
            )
            csproj.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "must not declare PackageReference"):
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
            compile_profile = resolve_runtime_compile_profile(root)
            self.assertEqual(PROFILE.framework_version, compile_profile.version)
            self.assertEqual(variant / PROFILE.runtime_dll, compile_profile.assembly_path)
            self.assertEqual(hashlib.sha256(b"dll").hexdigest(), compile_profile.assembly_sha256)

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
                "version": "0.5.12",
                "min_game_version": PROFILE.host_version,
                "dependencies": [],
            }
            manifest_path = root / "mod_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIn("RitsuLib 0.5.12", validate_runtime_asset(root))

            manifest["version"] = "0.5.10"
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

    def test_host_release_version_accepts_macos_bundle_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "Slay the Spire 2"
            resources = game / "SlayTheSpire2.app" / "Contents" / "Resources"
            resources.mkdir(parents=True)
            release = resources / "release_info.json"
            release.write_text(
                json.dumps({"version": "v" + PROFILE.host_version}),
                encoding="utf-8",
            )
            self.assertIn(PROFILE.host_version, validate_host_version(game))


if __name__ == "__main__":
    unittest.main()
