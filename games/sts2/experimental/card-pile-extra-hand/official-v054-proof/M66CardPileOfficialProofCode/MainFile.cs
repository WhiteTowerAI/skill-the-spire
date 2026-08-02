using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Modding;
using STS2RitsuLib;

namespace M66CardPileOfficialProof;

[ModInitializer(nameof(Initialize))]
public static partial class MainFile
{
    public const string ModId = "M66CardPileOfficialProof";
    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } =
        RitsuLibFramework.CreateLogger(ModId);

    public static void Initialize()
    {
        RegisterContent();
        var frameworkAssembly = typeof(Const).Assembly;
        var compat = frameworkAssembly.GetCustomAttributes<AssemblyMetadataAttribute>()
            .FirstOrDefault(attribute => attribute.Key == "Sts2ApiCompat")?.Value ?? "<missing>";
        Logger.Info($"[T2MOD-SELFTEST] {ModId} loaded ok framework=RitsuLib frameworkVersion={Const.Version} host=0.107.1 compat={compat}");
    }

    static partial void RegisterContent();
}
