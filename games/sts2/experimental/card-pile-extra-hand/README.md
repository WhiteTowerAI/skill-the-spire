# CardPile / ExtraHand repository experiment

This directory preserves the M6.6 Package 4 implementation research. It is excluded from
the formal `modmaker` and `sts2-api` skills, the support graph, and generated plugin and
portable payloads.

The focused implementation required a private RitsuLib lifecycle repair for repeated native
manual play. Official RitsuLib `0.5.0` does not provide the required behavior, and open-mod
does not ship generated-Mod or upstream RitsuLib patches. Package 4 is therefore unsupported.

Commit `436f6cb` preserves the complete implementation snapshot. The durable focused result
is `documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md`; `reference.md` is retained only
as design research.
