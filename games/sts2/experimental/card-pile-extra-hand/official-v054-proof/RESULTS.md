# Official RitsuLib 0.5.4 focused result

Date: 2026-08-02

Status: focused mouse-path result accepted; complete documented Package promoted by the
human lead under the Package-level support rule. Strict Tier 2 was waived, not run.

## Inputs

- STS2 stable `0.107.1`.
- Official RitsuLib tag `v0.5.4`, commit `8b971a79`.
- Official `STS2.RitsuLib.Compat.0.107.1` package version `0.5.4`.
- Official runtime manifest version `0.5.4`, minimum game version `0.107.1`, compat marker
  `0.107.1`.
- Proof runtime dependency: `STS2-RitsuLib >= 0.5.4`.
- No consumer Harmony patch, `UnsafeAccessor`, `PrivateAccess`, Publicizer, IL generation,
  lifecycle reflection, bundled RitsuLib DLL, or private RitsuLib source.

The official `0.5.4` source temporarily moves the exact Card into the native Hand,
reparents its holder into `NPlayerHand.CardHolderContainer`, and calls the native
`NPlayerHand.StartCardPlay` path. This replaces the independent `NCardPlay` construction
used by official `0.5.0`.

## Automated evidence

- Offline restore and build completed with zero warnings and zero errors.
- The proof DLL and PCK loaded in the real STS2 host.
- The exact load marker reported RitsuLib `0.5.4`, host `0.107.1`, and compat `0.107.1`.
- Setup asserted five native-Hand holders, three separate ExtraHand holders, capacity three,
  rejected overflow, and zero Archive Cards mounted in the idle native Hand.
- All three Archive Cards entered their effect bodies through the normal Play pile.
- After correcting the diagnostic field name, the proof rebuilt with zero warnings and
  zero errors.

The reviewed run logged `pileDuringPlay=Play`. That field name was misleading: the callback
runs in the Card effect body, after normal play has already advanced the Card from its
temporary Hand bridge into the Play pile. The proof source now names the field
`pileOnEffect=Play`; this label-only rebuild was not run in game again.

## Human-headed evidence

The human lead reported all requested focused cases normal:

- five lower native-Hand Cards and three upper Archive Cards were presented separately;
- numbered shortcuts selected only the five lower native-Hand Cards;
- canceling Stored Strike target selection restored it normally;
- after one Archive Card resolved, the remaining Archive Cards stayed interactive;
- Stored Guard, Stored Strike, and Stored Sweep could be played consecutively by mouse.

## Literal exceptions

- At the time of this run, the repository log verifier was still pinned to RitsuLib `0.5.0`,
  so its framework-profile check reported a version mismatch rather than a pass. The formal
  profile was subsequently updated to `0.5.4` as part of promotion.
- The current run logged a host save-cleanup error while abandoning the run:
  `Error deleting path modded/profile1/saves/current_run.save.backup: Failed`.
  Therefore exact Tier 1 did not pass even though no Package 4 error was logged.
- No structured `selftest done` marker was produced, so strict Tier 2 did not run.
- Controller focus, insufficient Energy, queued-action cancellation, non-play exits,
  second-combat cleanup, and the full 16:9/16:10 non-overlap matrix were not run in this
  focused recheck.

## Conclusion

Official RitsuLib `0.5.4` fixes the historical repeated native manual-play failure for the
focused mouse path without an open-mod consumer patch. On 2026-08-02 the human lead accepted
this focused result, waived strict Tier 2, and promoted the complete documented Custom Card
Piles Package under the repository's Package-level rule. That support claim comes from the
official Package semantics plus the public `0.5.4` API surface; it does not claim that this
focused proof exercised every documented consumer.
