# CardPile / ExtraHand research archive

This directory preserves the M6.6 Package 4 implementation research and the focused
official-version proof. The historical implementation here remains excluded from generated
payloads. Current Custom Card Piles authoring is supported through the formal
`sts2-api/reference/card-piles.md` route and the `modmaker` workflow.

The focused implementation required a private RitsuLib lifecycle repair for repeated native
manual play. Official RitsuLib `0.5.0` does not provide the required behavior, and open-mod
does not ship generated-Mod or upstream RitsuLib patches.

Official RitsuLib `0.5.4` now contains the missing native-Hand bridge. The unmodified
official runtime passed a focused mouse cancellation, shortcut-isolation, and consecutive-
play recheck on STS2 `0.107.1`; see `official-v054-proof/RESULTS.md`. On 2026-08-02 the
human lead promoted the complete documented Custom Card Piles Package under the repository's
Package-level support rule and moved the formal dependency to `0.5.4`. The focused proof did
not run strict Tier 2; that remains a recorded verification exception rather than a support
restriction.

Commit `436f6cb` preserves the complete implementation snapshot. The durable focused result
is `documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md`; `reference.md` is retained only
as design research, not as the current authoring contract.
