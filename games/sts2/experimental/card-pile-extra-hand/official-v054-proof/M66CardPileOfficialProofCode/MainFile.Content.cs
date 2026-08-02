using Godot;
using MegaCrit.Sts2.Core.Models.CardPools;
using M66CardPileOfficialProof.Cards;
using STS2RitsuLib;
using STS2RitsuLib.CardPiles;

namespace M66CardPileOfficialProof;

public static partial class MainFile
{
    static partial void RegisterContent()
    {
        RitsuLibFramework.CreateContentPack(ModId)
            .Card<ColorlessCardPool, StoredStrike>()
            .Card<ColorlessCardPool, StoredSweep>()
            .Card<ColorlessCardPool, StoredGuard>()
            .Card<ColorlessCardPool, ReviewSetup>()
            .CardPileOwned(ArchivePile.LocalStem, new ModCardPileSpec
            {
                Scope = ModCardPileScope.CombatOnly,
                Style = ModCardPileUiStyle.ExtraHand,
                Anchor = new ModCardPileAnchor(
                    ModCardPileAnchorKind.ExtraHandAbove,
                    new Vector2(0f, -420f)),
                CardShouldBeVisible = true,
                ExtraHand = new ModCardPileExtraHandSpec
                {
                    Direction = ModExtraHandLayoutDirection.Horizontal,
                    Spacing = 180f,
                    CardScale = Vector2.One * 0.55f,
                    HoverScale = Vector2.One * 0.75f,
                    ShowPlayableGlow = true,
                    AllowCardPlay = true,
                    OnCardVisualCreated = ReviewDiagnostics.Attach,
                },
            })
            .Apply();
    }
}
