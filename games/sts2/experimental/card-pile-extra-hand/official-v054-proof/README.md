# Official RitsuLib 0.5.4 Package 4 proof

This is a repository-only focused proof for STS2 `0.107.1` and the unmodified official
`STS2.RitsuLib.Compat.0.107.1` `0.5.4` package/runtime. It does not patch RitsuLib or STS2.
The human lead accepted its focused headed result on 2026-08-02 and promoted the complete
documented Custom Card Piles Package under the repository's Package-level support rule.
This proof remains focused evidence rather than a claim that every Package consumer ran.

The proof registers one combat-only Archive through `CardPileOwned`, moves exact Card
instances through awaited `CardPileCmd.Add`, and enables the public ExtraHand manual-play
route. `Review Setup` creates five native-Hand probes and three Archive Cards, then asserts
capacity, overflow rejection, holder ownership, and idle separation from the native Hand.

Build and runtime validation must reject any proof directory that contains
`STS2-RitsuLib.dll`, `BaseLib.dll`, Harmony patches, UnsafeAccessor declarations,
reflection-based lifecycle access, Publicizer, or private RitsuLib source.

The headed matrix remains the one in `../reference.md`. The direct setup route is:

```text
fight CULTISTS_NORMAL
card M66_CARD_PILE_OFFICIAL_PROOF_CARD_REVIEW_SETUP
```

Play `Review Setup`, then exercise the upper Stored Guard, Stored Strike, and Stored Sweep.
The effect-body diagnostic logs `pileOnEffect=Play`, which is the expected result after the
native play action has moved the Card out of its temporary Hand bridge. The official source
audit owns the separate claim that targeting begins through `NPlayerHand.StartCardPlay`.
A clean build or setup log does not replace mouse/controller, cancellation,
consecutive-play, cleanup, layout, Tier 1, or strict Tier 2 evidence.

The latest focused result is recorded in `RESULTS.md`.
