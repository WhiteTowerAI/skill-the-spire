from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import hook_reachability  # noqa: E402
import scaffold  # noqa: E402
from ritsu_profile import local_mods_dir, resolve_runtime_asset, resolve_runtime_compile_profile  # noqa: E402

# A run-only hook on a Power (never fires), a combat hook on a Relic (fires), and a general
# Block hook on an Enchantment (must use its Enchant* replacement instead).
PROBE_SOURCE = """using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace HookProbe;

public sealed class RunOnlyPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override decimal ModifyCardRewardUpgradeOdds(Player player, CardModel card, decimal odds) =>
        odds + 1m;
}

internal sealed class CombatRelic : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Common;
    public override decimal ModifyBlockAdditive(Creature target, decimal block, ValueProp props,
        CardModel? cardSource, CardPlay? cardPlay) => block + 1m;
}

public sealed class BlockEnchantment : ModEnchantmentTemplate
{
    public override decimal ModifyBlockAdditive(Creature target, decimal block, ValueProp props,
        CardModel? cardSource, CardPlay? cardPlay) => block + 1m;
}
"""


def local_host() -> tuple[Path, Path] | None:
    configured = os.environ.get("OPEN_MOD_STS2_DIR")
    candidates = [Path(configured)] if configured else []
    candidates += [
        Path("D:/Steam/steamapps/common/Slay the Spire 2"),
        Path("C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2"),
        Path.home() / ".local/share/Steam/steamapps/common/Slay the Spire 2",
    ]
    for host in candidates:
        data = host / "data_sts2_windows_x86_64"
        if (data / "sts2.dll").is_file():
            return host, data
    return None


class HookReachabilityTests(unittest.TestCase):
    def test_catalog_hooks_name_their_surfaces(self) -> None:
        hooks = hook_reachability.load_hooks()
        self.assertEqual(68, len(hooks))
        self.assertNotIn("power", hooks["ModifyCardRewardUpgradeOdds"]["authorable_surfaces"])
        self.assertIn("relic", hooks["TryModifyRestSiteOptions"]["authorable_surfaces"])

    def test_compiled_overrides_are_checked_against_their_surface(self) -> None:
        dotnet = shutil.which("dotnet")
        found = local_host()
        if not dotnet or found is None:
            self.skipTest("dotnet or the STS2 host is unavailable; set OPEN_MOD_STS2_DIR")
        host, data_dir = found
        try:
            runtime = resolve_runtime_asset(host, local_mods_dir(host))
            compile_profile = resolve_runtime_compile_profile(runtime.path)
        except ValueError as exc:
            self.skipTest(f"checked local RitsuLib runtime is unavailable: {exc}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "hook-probe-project"
            scaffold.generate(project, "HookProbe", "SkillTheSpire", compile_profile=compile_profile)
            (project / "HookProbeCode" / "Probe.cs").write_text(PROBE_SOURCE, encoding="utf-8")
            mods_path = root / "mods"
            result = subprocess.run(
                [dotnet, "build", str(project / "HookProbe.csproj"), "-c", "Release", "--nologo",
                 f"-p:Sts2Dir={host}", f"-p:Sts2DataDir={data_dir}",
                 f"-p:ModsPath={mods_path.as_posix()}/",
                 f"-p:RitsuLibRuntimeRoot={compile_profile.root.resolve().as_posix()}",
                 "-p:RestoreIgnoreFailedSources=true"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
                env={**os.environ, "NUGET_PACKAGES": str(Path.home() / ".nuget" / "packages")},
            )
            self.assertEqual(0, result.returncode, (result.stdout or "") + (result.stderr or ""))

            findings = hook_reachability.unreachable_overrides(
                mods_path / "HookProbe" / "HookProbe.dll", project_dir=project
            )

        self.assertEqual(2, len(findings), findings)
        self.assertTrue(any(f.startswith("RunOnlyPower.ModifyCardRewardUpgradeOdds: ")
                            and "to a power" in f for f in findings), findings)
        self.assertTrue(any(f.startswith("BlockEnchantment.ModifyBlockAdditive: ")
                            and "EnchantBlockAdditive" in f for f in findings), findings)
        self.assertFalse(any(f.startswith("CombatRelic.") for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
