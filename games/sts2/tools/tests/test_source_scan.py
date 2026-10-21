from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import source_scan  # noqa: E402
from vanilla_overrides import load_catalog  # noqa: E402

# The two reviewed Adapter shapes the shipped override references teach.
ANCIENT_ADAPTER = """
using HarmonyLib;
using STS2RitsuLib.Patching.Models;

internal sealed class AncientInitialOptionsReplacementPatch : IPatchMethod
{
    public static string PatchId => "skillthespire_ancient_initial_options";
    public static ModPatchTarget[] GetTargets() =>
        [new(typeof(AncientEventModel), "GenerateInitialOptionsWrapper", Type.EmptyTypes)];

    [HarmonyBefore("com.ritsukage.sts2-RitsuLib.framework-core")]
    public static void Postfix(AncientEventModel __instance) { }
}
"""
AVAILABILITY_ADAPTER = """
internal sealed class VanillaRelicEpochGatePatch : IPatchMethod
{
    public static ModPatchTarget[] GetTargets() =>
    [
        new(typeof(RelicPoolModel), nameof(RelicPoolModel.GetUnlockedRelics),
            [typeof(UnlockState)]),
        new(typeof(SharedRelicPool), nameof(SharedRelicPool.GetUnlockedRelics),
            [typeof(UnlockState)]),
    ];
}
"""
LOAD_MARKER = """
var frameworkAssembly = typeof(STS2RitsuLib.RitsuLibFramework).Assembly;
var version = frameworkAssembly.GetName().Version?.ToString(3);
var compat = frameworkAssembly.GetCustomAttributes<AssemblyMetadataAttribute>();
"""


class SourceScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()

    def project(self, files: dict[str, str], csproj: str = "<Project />") -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "project"
        code = root / "ProofCode"
        code.mkdir(parents=True)
        (root / "Proof.csproj").write_text(csproj, encoding="utf-8")
        for name, text in files.items():
            (code / name).write_text(text, encoding="utf-8")
        return root

    def scan(self, root: Path) -> list[str]:
        return source_scan.scan(root, "Proof", catalog=self.catalog)

    def test_reviewed_adapters_and_load_marker_pass(self) -> None:
        root = self.project({
            "Ancient.cs": ANCIENT_ADAPTER,
            "Availability.cs": AVAILABILITY_ADAPTER,
            "MainFile.cs": LOAD_MARKER,
        })
        self.assertEqual([], self.scan(root))

    def test_forbidden_routes_fail_with_file_and_line(self) -> None:
        cases = {
            "[Pool(typeof(SharedRelicPool))]\npublic sealed class Coin {}": "[Pool",
            "var h = new Harmony(\"id\");": "raw Harmony",
            "[HarmonyPatch(typeof(Player))]\nclass P {}": "Harmony patch attribute",
            "var f = AccessTools.Field(typeof(Player), \"_gold\");": "Harmony reflection",
            "var m = typeof(Player).GetMethod(\"Lose\", BindingFlags.NonPublic);": "member reflection",
            "var m = player.GetType().GetField(\"_gold\");": "member reflection",
            "static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> c) => c;":
                "IL generation",
        }
        for code, reason in cases.items():
            with self.subTest(reason=reason):
                findings = self.scan(self.project({"Bad.cs": "\n" + code}))
                self.assertTrue(findings, code)
                self.assertTrue(all(f.startswith("ProofCode/Bad.cs:") for f in findings), findings)
                self.assertTrue(any(reason in f for f in findings), findings)

    def test_unreviewed_patch_target_fails(self) -> None:
        patch = (
            "class P : IPatchMethod { public static ModPatchTarget[] GetTargets() =>\n"
            "    [new(typeof(Player), nameof(Player.LoseGold))]; }"
        )
        findings = self.scan(self.project({"Patch.cs": patch}))
        self.assertEqual(1, len(findings), findings)
        self.assertIn("Player.LoseGold is not a reviewed Adapter", findings[0])

    def test_getter_target_resolves_to_its_accessor_method(self) -> None:
        reviewed = ("get_Rarity" in {m for _, m in source_scan.reviewed_adapter_methods(self.catalog)})
        self.assertTrue(reviewed)
        target = source_scan.patch_targets(
            "[new(typeof(RelicModel), nameof(RelicModel.Rarity), MethodType.Getter)]"
        )
        self.assertEqual([("RelicModel", "get_Rarity", 1)], target)

    def test_unreadable_patch_targets_fail(self) -> None:
        patch = "class P : IPatchMethod { static ModPatchTarget[] GetTargets() => Build(); }"
        findings = self.scan(self.project({"Patch.cs": patch}))
        self.assertTrue(any("targets are unreadable" in f for f in findings), findings)

    def test_comments_kit_and_build_output_are_ignored(self) -> None:
        root = self.project({
            "Card.cs": "// never add [Pool(...)] or new Harmony(...)\n/* BindingFlags */ class C {}",
            "SelfTestKit.cs": "var t = typeof(Player).GetMethod(\"X\");",
        })
        (root / "obj").mkdir()
        (root / "obj" / "Generated.cs").write_text("[Pool(typeof(X))] class G {}", encoding="utf-8")
        self.assertEqual([], self.scan(root))

    def test_publicizer_in_csproj_fails(self) -> None:
        root = self.project({}, csproj='<Project><PackageReference Include="Krafs.Publicizer" /></Project>')
        self.assertEqual(["Proof.csproj: a Publicizer: private members are off limits"], self.scan(root))

    def test_validate_reports_findings(self) -> None:
        root = self.project({"Bad.cs": "[Pool(typeof(X))] class B {}"})
        with self.assertRaisesRegex(source_scan.SourceScanError, r"ProofCode/Bad.cs:1: `\[Pool"):
            source_scan.validate_project_sources(root, "Proof", catalog=self.catalog)


if __name__ == "__main__":
    unittest.main()
