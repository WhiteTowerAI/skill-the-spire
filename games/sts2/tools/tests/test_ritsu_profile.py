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
    RuntimeAssembly,
    RuntimeCompileProfile,
    find_manifest,
    local_mods_dir,
    resolve_runtime_asset,
    resolve_runtime_compile_profile,
    validate_host_version,
    validate_project_contract,
    validate_runtime_asset,
)
from scaffold import generate, repin_runtime  # noqa: E402


def _assembly_bytes(name: str) -> bytes:
    return b"MZ" + name.encode("utf-8")


def runtime_payload(
    version: str = PROFILE.framework_version,
    targets: tuple[str, ...] = (PROFILE.host_version,),
) -> dict[str, bytes]:
    """Return a RitsuLib 0.6-style schema-2 runtime layout keyed by relative POSIX path."""
    files: dict[str, bytes] = {
        PROFILE.runtime_dll: b"MZloader",
        "mod_manifest.json": json.dumps({
            "id": PROFILE.runtime_mod_id,
            "version": version,
            "min_game_version": PROFILE.host_version,
            "has_dll": True,
            "dependencies": [],
        }).encode("utf-8"),
    }
    for name in PROFILE.shared_assemblies:
        files[f"shared/{name}.dll"] = _assembly_bytes(name)
    variants = []
    for target in targets:
        # Real 0.6.x bundles write the marker with a UTF-8 BOM.
        files[f"compat/{target}/compat-target.txt"] = ("\ufeff" + target + "\n").encode("utf-8")
        for name in PROFILE.compat_assemblies:
            files[f"compat/{target}/{name}.dll"] = _assembly_bytes(f"{target}/{name}")
        variants.append({
            "compatTarget": target,
            "files": [
                {
                    "assembly": name,
                    "sha256": hashlib.sha256(files[f"compat/{target}/{name}.dll"]).hexdigest(),
                }
                for name in PROFILE.compat_assemblies
            ],
        })
    files[PROFILE.variant_manifest] = json.dumps({
        "schema": 2,
        "shared": [
            {"assembly": name, "sha256": hashlib.sha256(files[f"shared/{name}.dll"]).hexdigest()}
            for name in PROFILE.shared_assemblies
        ],
        "variants": variants,
    }).encode("utf-8")
    return files


def write_runtime(root: Path, files: dict[str, bytes]) -> Path:
    for relative, data in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


def fixture_compile_profile(root: Path, version: str = "0.6.8") -> RuntimeCompileProfile:
    return RuntimeCompileProfile(
        version,
        root,
        tuple(
            RuntimeAssembly(name, relative, hashlib.sha256(relative.encode()).hexdigest())
            for name, relative in PROFILE.assembly_relative_paths()
        ),
    )


class RitsuProfileTests(unittest.TestCase):
    def test_outer_directory_must_differ_from_mod_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "outer project directory"):
                generate(Path(tmp) / "EmptyRitsu", "EmptyRitsu", "SkillTheSpire")

    def test_scaffold_uses_bundled_sdk_and_pinned_local_assemblies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            compile_profile = fixture_compile_profile(Path(tmp) / "runtime")
            compile_hash = compile_profile.assembly_set_sha256
            generate(
                project,
                "EmptyRitsu",
                "SkillTheSpire",
                compile_profile=compile_profile,
            )
            summary = validate_project_contract(project, "EmptyRitsu")
            self.assertIn(PROFILE.profile_id, summary)
            self.assertIn("local compile runtime 0.6.8", summary)
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
            self.assertIn("<RitsuLibCompileVersion>0.6.8</RitsuLibCompileVersion>", csproj)
            self.assertIn(
                "<RitsuLibCompileAssemblySetSha256>"
                f"{compile_hash}</RitsuLibCompileAssemblySetSha256>",
                csproj,
            )
            for reference in (
                "sts2",
                "0Harmony",
                "GodotSharp",
                "System.IO.Hashing",
                *PROFILE.compat_assemblies,
                *PROFILE.shared_assemblies,
            ):
                self.assertIn(f'<Reference Include="{reference}"', csproj)
            self.assertIn(
                f'HintPath="$(RitsuLibRuntimeRoot)\\compat\\{PROFILE.host_version}'
                '\\STS2-RitsuLib.Runtime.dll"',
                csproj,
            )
            self.assertIn(
                'HintPath="$(RitsuLibRuntimeRoot)\\shared\\STS2-RitsuLib.Shared.dll"', csproj
            )
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
            self.assertIn('CompileFrameworkVersion = "0.6.8"', main)
            # The loaded version and compat come from the per-host Runtime module, not from
            # the compile-time Const.Version constant.
            self.assertIn("typeof(RitsuLibFramework).Assembly", main)
            self.assertNotIn("Const.Version", main)

    def test_manifest_must_use_the_canonical_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest = project / "mod_manifest.json"
            old_name = project / "ExampleMod.json"

            with self.assertRaisesRegex(RitsuProfileError, "missing manifest"):
                find_manifest(project, "ExampleMod")

            old_name.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "rename it to mod_manifest.json"):
                find_manifest(project, "ExampleMod")

            old_name.unlink()
            manifest.write_text("{}\n", encoding="utf-8")
            self.assertEqual(manifest, find_manifest(project, "ExampleMod"))

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

    def test_runtime_directory_and_zip_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = runtime_payload(targets=(PROFILE.host_version, "0.109.0"))
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", files)
            self.assertIn(PROFILE.host_version, validate_runtime_asset(root))
            compile_profile = resolve_runtime_compile_profile(root)
            self.assertEqual(PROFILE.framework_version, compile_profile.version)
            self.assertEqual(root, compile_profile.root)
            self.assertEqual(
                [relative for _, relative in PROFILE.assembly_relative_paths()],
                [item.relative_path for item in compile_profile.assemblies],
            )
            runtime_dll = f"compat/{PROFILE.host_version}/STS2-RitsuLib.Runtime.dll"
            self.assertIn(
                hashlib.sha256(files[runtime_dll]).hexdigest(),
                [item.sha256 for item in compile_profile.assemblies],
            )

            archive = Path(tmp) / "variant-pack.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                for relative, data in files.items():
                    zf.writestr(relative, data)
            self.assertIn(PROFILE.host_version, validate_runtime_asset(archive))

    def test_assembly_set_digest_tracks_every_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = runtime_payload()
            first = resolve_runtime_compile_profile(write_runtime(Path(tmp) / "a", files))
            changed = dict(files)
            changed["shared/STS2-RitsuLib.Settings.dll"] = b"MZchanged"
            manifest = json.loads(changed[PROFILE.variant_manifest])
            for entry in manifest["shared"]:
                if entry["assembly"] == "STS2-RitsuLib.Settings":
                    entry["sha256"] = hashlib.sha256(b"MZchanged").hexdigest()
            changed[PROFILE.variant_manifest] = json.dumps(manifest).encode("utf-8")
            second = resolve_runtime_compile_profile(write_runtime(Path(tmp) / "b", changed))
            self.assertNotEqual(first.assembly_set_sha256, second.assembly_set_sha256)

    def test_module_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = runtime_payload()
            files["shared/STS2-RitsuLib.Ui.dll"] = b"MZtampered"
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", files)
            with self.assertRaisesRegex(RitsuProfileError, "does not match"):
                resolve_runtime_compile_profile(root)

    def test_pre_0_6_single_dll_layout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = runtime_payload()
            manifest = json.loads(files[PROFILE.variant_manifest])
            manifest["schema"] = 1
            files[PROFILE.variant_manifest] = json.dumps(manifest).encode("utf-8")
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", files)
            with self.assertRaisesRegex(RitsuProfileError, "schema 2"):
                validate_runtime_asset(root)

    def test_newer_runtime_version_is_accepted_but_older_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_runtime(Path(tmp) / "new" / "STS2-RitsuLib", runtime_payload("0.6.8"))
            self.assertIn("RitsuLib 0.6.8", validate_runtime_asset(root))
            old = write_runtime(Path(tmp) / "old" / "STS2-RitsuLib", runtime_payload("0.6.6"))
            with self.assertRaisesRegex(RitsuProfileError, "older than the required minimum"):
                validate_runtime_asset(old)

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
            root = write_runtime(
                Path(tmp) / "STS2-RitsuLib", runtime_payload(targets=("0.109.0",))
            )
            with self.assertRaisesRegex(RitsuProfileError, "no matching"):
                validate_runtime_asset(root)

    def test_pre_0_6_project_pin_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            generate(project, "EmptyRitsu", "SkillTheSpire")
            csproj = project / "EmptyRitsu.csproj"
            csproj.write_text(
                csproj.read_text(encoding="utf-8").replace(
                    "RitsuLibCompileAssemblySetSha256", "RitsuLibCompileAssemblySha256"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RitsuProfileError, "before 0.6.0"):
                validate_project_contract(project, "EmptyRitsu")

    def test_repin_updates_only_the_compile_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            old = fixture_compile_profile(Path(tmp) / "runtime", "0.6.7")
            generate(project, "EmptyRitsu", "SkillTheSpire", compile_profile=old)
            manifest_before = (project / "mod_manifest.json").read_text(encoding="utf-8")
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", runtime_payload("0.6.9"))
            new = resolve_runtime_compile_profile(root)

            self.assertEqual("0.6.9", repin_runtime(project, "EmptyRitsu", new))
            csproj = (project / "EmptyRitsu.csproj").read_text(encoding="utf-8")
            main = (project / "EmptyRitsuCode" / "MainFile.cs").read_text(encoding="utf-8")
            self.assertIn("<RitsuLibCompileVersion>0.6.9</RitsuLibCompileVersion>", csproj)
            self.assertIn(new.assembly_set_sha256, csproj)
            self.assertNotIn(old.assembly_set_sha256, csproj)
            self.assertIn('CompileFrameworkVersion = "0.6.9"', main)
            self.assertEqual(
                manifest_before, (project / "mod_manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn("local compile runtime 0.6.9", validate_project_contract(project))

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
