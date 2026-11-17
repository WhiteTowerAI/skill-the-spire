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
    check_host,
    find_manifest,
    loader_compat_target,
    local_mods_dir,
    resolve_runtime_asset,
    resolve_runtime_compile_profile,
    validate_host_version,
    validate_project_contract,
    validate_runtime_asset,
)
from scaffold import generate, migrate_profile, repin_runtime  # noqa: E402


def _assembly_bytes(name: str) -> bytes:
    return b"MZ" + name.encode("utf-8")


def runtime_payload(
    version: str = PROFILE.framework_version,
    targets: tuple[str, ...] = (PROFILE.compat_target,),
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


def fixture_compile_profile(root: Path, version: str = "0.6.15") -> RuntimeCompileProfile:
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

    def test_scaffold_keeps_planning_docs_and_refuses_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "planned-outer"
            project.mkdir()
            for name in ("DESIGN.md", "SPEC.md", "PLAN.md", "MEMORY.md"):
                (project / name).write_text(f"# {name}\n", encoding="utf-8")
            generate(project, "EmptyRitsu", "SkillTheSpire")
            self.assertEqual("# SPEC.md\n", (project / "SPEC.md").read_text(encoding="utf-8"))
            self.assertTrue((project / "EmptyRitsu.csproj").is_file())

            other = Path(tmp) / "used-outer"
            other.mkdir()
            (other / "SPEC.md").write_text("spec", encoding="utf-8")
            (other / "notes.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "found notes.txt"):
                generate(other, "EmptyRitsu", "SkillTheSpire")

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
            self.assertIn("local compile runtime 0.6.15", summary)
            manifest = json.loads(
                (project / "mod_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["dependencies"],
                [{"id": "STS2-RitsuLib", "min_version": PROFILE.framework_version}],
            )
            # false made RitsuLib give the Mod's models no network identity.
            self.assertIs(True, manifest["affects_gameplay"])
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
            self.assertIn("<RitsuLibCompileVersion>0.6.15</RitsuLibCompileVersion>", csproj)
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
                f'HintPath="$(RitsuLibRuntimeRoot)\\compat\\{PROFILE.compat_target}'
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
            self.assertIn('CompileFrameworkVersion = "0.6.15"', main)
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
            files = runtime_payload(targets=(PROFILE.compat_target, "0.109.0"))
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", files)
            self.assertIn(PROFILE.compat_target, validate_runtime_asset(root))
            compile_profile = resolve_runtime_compile_profile(root)
            self.assertEqual(PROFILE.framework_version, compile_profile.version)
            self.assertEqual(root, compile_profile.root)
            self.assertEqual(
                [relative for _, relative in PROFILE.assembly_relative_paths()],
                [item.relative_path for item in compile_profile.assemblies],
            )
            runtime_dll = f"compat/{PROFILE.compat_target}/STS2-RitsuLib.Runtime.dll"
            self.assertIn(
                hashlib.sha256(files[runtime_dll]).hexdigest(),
                [item.sha256 for item in compile_profile.assemblies],
            )

            archive = Path(tmp) / "variant-pack.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                for relative, data in files.items():
                    zf.writestr(relative, data)
            self.assertIn(PROFILE.compat_target, validate_runtime_asset(archive))

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
            root = write_runtime(Path(tmp) / "new" / "STS2-RitsuLib", runtime_payload("0.6.15"))
            self.assertIn("RitsuLib 0.6.15", validate_runtime_asset(root))
            old = write_runtime(Path(tmp) / "old" / "STS2-RitsuLib", runtime_payload("0.6.13"))
            with self.assertRaisesRegex(RitsuProfileError, "older than the required minimum"):
                validate_runtime_asset(old)

    def test_runtime_discovery_reuses_official_workshop_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # resolve(): runner temp dirs can be 8.3 short paths, and discovery resolves.
            steamapps = Path(tmp).resolve() / "steamapps"
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
            with self.assertRaisesRegex(RitsuProfileError, "has no .* RitsuLib variant"):
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
            old = fixture_compile_profile(Path(tmp) / "runtime", "0.6.14")
            generate(project, "EmptyRitsu", "SkillTheSpire", compile_profile=old)
            manifest_before = (project / "mod_manifest.json").read_text(encoding="utf-8")
            root = write_runtime(Path(tmp) / "STS2-RitsuLib", runtime_payload("0.6.16"))
            new = resolve_runtime_compile_profile(root)

            self.assertEqual("0.6.16", repin_runtime(project, "EmptyRitsu", new))
            csproj = (project / "EmptyRitsu.csproj").read_text(encoding="utf-8")
            main = (project / "EmptyRitsuCode" / "MainFile.cs").read_text(encoding="utf-8")
            self.assertIn("<RitsuLibCompileVersion>0.6.16</RitsuLibCompileVersion>", csproj)
            self.assertIn(new.assembly_set_sha256, csproj)
            self.assertNotIn(old.assembly_set_sha256, csproj)
            self.assertIn('CompileFrameworkVersion = "0.6.16"', main)
            self.assertEqual(
                manifest_before, (project / "mod_manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn("local compile runtime 0.6.16", validate_project_contract(project))

    def test_migrate_profile_moves_an_older_project_and_keeps_authored_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty-outer"
            generate(project, "EmptyRitsu", "SkillTheSpire")
            csproj = project / "EmptyRitsu.csproj"
            manifest = project / "mod_manifest.json"
            main = project / "EmptyRitsuCode" / "MainFile.cs"
            kit = project / "EmptyRitsuCode" / "SelfTestKit.cs"
            overrides = project / "skillthespire" / "vanilla-overrides.json"
            authored = project / "EmptyRitsuCode" / "Cards" / "Jab.cs"
            authored.parent.mkdir()
            authored.write_text("// authored\n", encoding="utf-8")

            # Rewind every scaffold-owned pin to the previous release's profile.
            old_profile = "ritsulib-0.6.7-sts2-0.107.1"
            for path, pairs in (
                (csproj, ((PROFILE.profile_id, old_profile), (PROFILE.compat_target, "0.107.1"))),
                (main, ((f"host={PROFILE.host_version}", "host=0.107.1"),)),
                (kit, (("// SelfTestKit", "// SelfTestKit 1 old\n// SelfTestKit"),)),
            ):
                text = path.read_text(encoding="utf-8")
                for current, previous in pairs:
                    self.assertIn(current, text)
                    text = text.replace(current, previous)
                path.write_text(text, encoding="utf-8")
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data.update(min_game_version="0.107.1", version="1.2.3", has_pck=True)
            data["dependencies"] = [{"id": PROFILE.runtime_mod_id, "min_version": "0.6.7"}]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            pinned = json.loads(overrides.read_text(encoding="utf-8"))
            catalog_sha256 = pinned["catalog_sha256"]
            pinned.update(profile=old_profile, host_version="0.107.1", catalog_sha256="0" * 64)
            overrides.write_text(json.dumps(pinned), encoding="utf-8")

            with self.assertRaisesRegex(RitsuProfileError, "--migrate-profile"):
                validate_project_contract(project, "EmptyRitsu")
            runtime = fixture_compile_profile(Path(tmp) / "runtime", "0.6.15")
            notes = migrate_profile(project, "EmptyRitsu", runtime)

            self.assertIn(f"{old_profile} -> {PROFILE.profile_id}", notes[0])
            self.assertIn("local compile runtime 0.6.15", validate_project_contract(project))
            csproj_text = csproj.read_text(encoding="utf-8")
            self.assertIn(f"<Sts2ApiCompat>{PROFILE.compat_target}</Sts2ApiCompat>", csproj_text)
            self.assertNotIn("0.107.1", csproj_text)
            migrated = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(PROFILE.host_version, migrated["min_game_version"])
            self.assertEqual(PROFILE.framework_version, migrated["dependencies"][0]["min_version"])
            self.assertEqual(("1.2.3", True), (migrated["version"], migrated["has_pck"]))
            main_text = main.read_text(encoding="utf-8")
            self.assertIn(f"host={PROFILE.host_version} compat=", main_text)
            self.assertIn('CompileFrameworkVersion = "0.6.15"', main_text)
            self.assertNotIn("SelfTestKit 1 old", kit.read_text(encoding="utf-8"))
            repinned = json.loads(overrides.read_text(encoding="utf-8"))
            self.assertEqual(
                (PROFILE.profile_id, PROFILE.host_version, catalog_sha256),
                (repinned["profile"], repinned["host_version"], repinned["catalog_sha256"]),
            )
            self.assertEqual("// authored\n", authored.read_text(encoding="utf-8"))

            with self.assertRaisesRegex(ValueError, "already on"):
                migrate_profile(project, "EmptyRitsu", runtime)

    def test_runtime_whose_loader_would_pick_another_variant_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # A variant for exactly the pinned host outranks the pinned compat target.
            root = write_runtime(
                Path(tmp) / "STS2-RitsuLib",
                runtime_payload(targets=(PROFILE.compat_target, PROFILE.host_version)),
            )
            with self.assertRaisesRegex(RitsuProfileError, "would load its"):
                validate_runtime_asset(root)
            self.assertEqual(
                PROFILE.compat_target,
                loader_compat_target(["0.107.1", PROFILE.compat_target, "0.113.0"], PROFILE.host_version),
            )
            self.assertIsNone(loader_compat_target(["0.113.0"], PROFILE.host_version))

    def test_workshop_runtime_wins_only_with_a_strictly_greater_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # resolve(): runner temp dirs can be 8.3 short paths, and discovery resolves.
            steamapps = Path(tmp).resolve() / "steamapps"
            game = steamapps / "common" / "Slay the Spire 2"
            mods = game / "mods"
            local = mods / PROFILE.runtime_mod_id
            workshop = (
                steamapps / "workshop" / "content" / PROFILE.steam_app_id / PROFILE.workshop_item_id
            )
            for folder, version in ((local, "0.6.14"), (workshop, "0.6.15")):
                folder.mkdir(parents=True)
                (folder / "mod_manifest.json").write_text(
                    json.dumps({"id": PROFILE.runtime_mod_id, "version": version}), encoding="utf-8"
                )
            selected = resolve_runtime_asset(game, mods)
            self.assertEqual(("Steam Workshop", workshop), (selected.source, selected.path))
            self.assertEqual((local,), selected.alternates)

            (workshop / "mod_manifest.json").write_text(
                json.dumps({"id": PROFILE.runtime_mod_id, "version": "0.6.14"}), encoding="utf-8"
            )
            self.assertEqual("mods directory", resolve_runtime_asset(game, mods).source)
            (local / "mod_manifest.json").write_text("not json", encoding="utf-8")
            self.assertEqual("mods directory", resolve_runtime_asset(game, mods).source)

    def test_later_patch_of_the_pinned_line_is_accepted_with_a_warning(self) -> None:
        major, minor, patch = PROFILE.host_version.split(".")
        later = f"{major}.{minor}.{int(patch) + 1}"
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            game.mkdir()
            release = game / "release_info.json"
            release.write_text(json.dumps({"version": "v" + PROFILE.host_version}), encoding="utf-8")
            pinned = check_host(game)
            self.assertTrue(pinned.exact)
            self.assertIsNone(pinned.warning())

            release.write_text(json.dumps({"version": "v" + later}), encoding="utf-8")
            patch_host = check_host(game)
            self.assertFalse(patch_host.exact)
            self.assertEqual(later, patch_host.version)
            self.assertIn("newer patch", patch_host.warning())

            if int(patch) > 0:
                earlier = f"{major}.{minor}.{int(patch) - 1}"
                release.write_text(json.dumps({"version": earlier}), encoding="utf-8")
                with self.assertRaisesRegex(RitsuProfileError, "Update the game"):
                    check_host(game)
            release.write_text(json.dumps({"version": f"{major}.{int(minor) + 2}.0"}), encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "newer than this Skill the Spire release"):
                check_host(game)

    def test_patch_host_runtime_must_still_load_the_pinned_variant(self) -> None:
        major, minor, patch = PROFILE.host_version.split(".")
        later = f"{major}.{minor}.{int(patch) + 1}"
        with tempfile.TemporaryDirectory() as tmp:
            usual = write_runtime(Path(tmp) / "a" / "STS2-RitsuLib", runtime_payload())
            self.assertIn(PROFILE.compat_target, validate_runtime_asset(usual, later))
            # A RitsuLib that ships a variant for the patch itself would load that one instead.
            closer = write_runtime(
                Path(tmp) / "b" / "STS2-RitsuLib",
                runtime_payload(targets=(PROFILE.compat_target, later)),
            )
            with self.assertRaisesRegex(RitsuProfileError, f"would load its {later} variant"):
                validate_runtime_asset(closer, later)

    def test_host_newer_than_the_pin_points_at_the_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            game.mkdir()
            (game / "release_info.json").write_text(json.dumps({"version": "v9.0.0"}), encoding="utf-8")
            with self.assertRaisesRegex(RitsuProfileError, "newer than this Skill the Spire release"):
                validate_host_version(game)

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
            with self.assertRaisesRegex(RitsuProfileError, "required stable .*Update the game"):
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
