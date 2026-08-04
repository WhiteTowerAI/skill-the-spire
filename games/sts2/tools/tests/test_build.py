from __future__ import annotations

import sys
import tempfile
import unittest
import json
from pathlib import Path
from unittest import mock


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import build  # noqa: E402


class BuildTests(unittest.TestCase):
    def test_shared_user_nuget_cache_requires_complete_pinned_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            packages = home / ".nuget" / "packages"
            package = packages / build.PROFILE.package_id.lower() / build.PROFILE.framework_version

            selected, source = build.select_nuget_packages_dir(
                None, environ={}, home=home
            )
            self.assertIsNone(selected)
            self.assertEqual("dotnet default", source)

            (package / "lib" / "net9.0").mkdir(parents=True)
            (package / "buildTransitive").mkdir()
            (package / "lib" / "net9.0" / build.PROFILE.runtime_dll).write_bytes(b"dll")
            (package / "buildTransitive" / f"{build.PROFILE.package_id}.targets").write_text(
                "<Project />\n", encoding="utf-8"
            )
            (package / (
                f"{build.PROFILE.package_id.lower()}."
                f"{build.PROFILE.framework_version}.nupkg"
            )).write_bytes(b"package")

            selected, source = build.select_nuget_packages_dir(
                None, environ={}, home=home
            )
            self.assertEqual(packages, selected)
            self.assertEqual("shared user cache", source)

    def test_explicit_nuget_cache_precedes_environment_and_user_cache(self) -> None:
        selected, source = build.select_nuget_packages_dir(
            "explicit-cache",
            environ={"NUGET_PACKAGES": "environment-cache"},
            home=Path("user-home"),
        )
        self.assertEqual(Path("explicit-cache"), selected)
        self.assertEqual("explicit", source)

    def test_msbuild_property_uses_selected_dotnet_environment(self) -> None:
        completed = mock.Mock(returncode=0, stdout="value\n")
        with mock.patch.object(build.subprocess, "run", return_value=completed) as run:
            env = {"NUGET_PACKAGES": "shared-cache"}
            self.assertEqual(
                "value",
                build.get_msbuild_property(Path("Proof.csproj"), "ModsPath", env),
            )
            self.assertEqual(env, run.call_args.kwargs["env"])

    def test_resource_manifest_must_match_authored_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "Canary.json"
            manifest.write_text(json.dumps({"has_pck": False}), encoding="utf-8")

            self.assertEqual(
                "has_pck=false",
                build.validate_resource_manifest(root, "Canary"),
            )

            assets = root / "Canary"
            assets.mkdir()
            (assets / "localization.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(build.RitsuProfileError, "has_pck must be true"):
                build.validate_resource_manifest(root, "Canary")

            manifest.write_text(json.dumps({"has_pck": True}), encoding="utf-8")
            self.assertEqual(
                "has_pck=true",
                build.validate_resource_manifest(root, "Canary"),
            )

            (assets / "localization.json").unlink()
            with self.assertRaisesRegex(build.RitsuProfileError, "has_pck must be false"):
                build.validate_resource_manifest(root, "Canary")

    def test_resource_pack_is_only_selected_when_assets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "Canary"
            mods = root / "mods" / "Canary"
            assets.mkdir()
            mods.mkdir(parents=True)

            with mock.patch.object(build, "pack_assets") as pack, mock.patch("builtins.print"):
                self.assertFalse(build.pack_project_assets(root, "Canary", mods))
                pack.assert_not_called()

                (assets / "localization.json").write_text("{}\n", encoding="utf-8")
                self.assertTrue(build.pack_project_assets(root, "Canary", mods))
                pack.assert_called_once_with(
                    assets, "Canary", mods / "Canary.pck"
                )

    def test_main_stops_before_msbuild_when_ancient_dialogue_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Proof.csproj").write_text("<Project />", encoding="utf-8")
            localization = root / "Proof" / "localization" / "eng"
            localization.mkdir(parents=True)
            (localization / "characters.json").write_text(
                json.dumps({"PROOF_CHARACTER_WAYFINDER.title": "Wayfinder"}),
                encoding="utf-8",
            )
            (localization / "ancients.json").write_text(
                json.dumps(
                    {
                        "THE_ARCHITECT.talk.PROOF_CHARACTER_WAYFINDER.0-0r.char": "Ready",
                        "THE_ARCHITECT.talk.PROOF_CHARACTER_WAYFINDER.0-0r.next": "Continue",
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch.object(build, "validate_project_contract", return_value="ok"),
                mock.patch.object(build, "validate_resource_manifest", return_value="has_pck=true"),
                mock.patch.object(build.subprocess, "run") as run,
                mock.patch("builtins.print"),
            ):
                self.assertEqual(
                    2,
                    build.main(
                        [
                            "--project-dir",
                            str(root),
                            "--mod-name",
                            "Proof",
                            "--skip-runtime-check",
                        ]
                    ),
                )
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
