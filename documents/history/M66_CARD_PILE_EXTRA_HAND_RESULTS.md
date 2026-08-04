# M6.6 Package 4 combat CardPile / ExtraHand results

Date: 2026-07-31

Acceptance environment: Windows, STS2 stable `0.107.1`, compile package
`STS2.RitsuLib.Compat.0.107.1` `0.4.62`, and a locally repaired matching RitsuLib runtime.
The delivery baseline is RitsuLib `0.4.67`, which carries the same accepted lifecycle
repair without changing the generated Package 4 API contract.

## Outcome

The first bounded Package 4 recipe is pipeline-supported for one generated-Mod-local,
singleplayer, combat-only visible Card pile. It provides:

- one compact horizontal ExtraHand above the native Hand;
- finite capacity with non-destructive overflow;
- explicit Top/Bottom entry and non-play exit;
- distinct instances of the same Card model;
- optional native manual play with normal payment, hooks, targeting, and result piles;
- restoration of the exact Card and source index after targeting or queued-action cancel;
- native-Hand-only numbered shortcuts; and
- complete Card/UI/subscription cleanup at combat end.

Run persistence, multiplayer or remote-player UI, vanilla-pile replacement, arbitrary
layout callbacks, and interception of an already played Card into a retained custom zone
remain outside this generated recipe.

## Pipeline contract

The modmaker interview and SPEC record one stable local pile name, localization, explicit
entry and non-play exit triggers, Top/Bottom position, capacity/overflow, repeated-model
policy, manual-play choice, normal successful result pile, compact above-Hand layout, and
the singleplayer combat boundary. Authoring registers the pile through RitsuLib's public
`CardPileOwned` route and moves exact Card instances only through awaited `CardPileCmd.Add`.
Generated gameplay does not call backend `AddInternal`/`RemoveInternal`, retain a parallel
Card collection, synthesize numbered input, or emit Harmony, reflection, Publicizer, or IL.

## Runtime repair

The first headed review exposed four linked RitsuLib lifecycle/presentation defects:

- the ExtraHand bridge created an independent `NCardPlay`, so selected presentation and
  the native Hand's current-play/awaiting-holder state diverged;
- a completed play could leave stale active coordinator state;
- ExtraHand holders inherited native numbered labels until a hover refresh; and
- mouse targeting used the ExtraHand card's above-play-zone starting Y position, causing
  lower-screen targets to be interpreted as cancellation.

The repair temporarily moves the exact Card into the backend Hand, reparents its existing
holder, enters `NPlayerHand.StartCardPlay`, clears stale active state, explicitly clears
the holder index label, and normalizes only above-zone mouse drag starts to the native play
zone. The obsolete prepare patch was removed. Successful Cards still follow their own
normal result-pile lifecycle, while cancellation restores the source pile/index.

## Automated evidence

- the repaired RitsuLib `0.107.1` compatibility source compiled offline with zero warnings
  and zero errors when unrelated Viewer/manifest-generation environment tasks were disabled;
- `M66CardPileProof` built and deployed with zero compile errors; its only warnings were
  cached NuGet audit metadata (`NU1900`) attempting to reach the unavailable NuGet service;
- the setup diagnostic recorded five native-Hand holders, three ExtraHand holders, zero
  ExtraHand Cards in native Hand while idle, non-destructive overflow, and exact order
  `Stored Guard > Stored Strike > Stored Sweep`;
- the current log contains seven successful manual plays with
  `beganFromExtraHand=True`, including one-card and different-position targeted cases; and
- the complete STS2 tools suite passed `125/125` tests;
- plugin and portable payloads each contain 152 effective files after excluding
  `__pycache__` and portable-only `GENERATED.md`, with zero missing files and zero content
  mismatches; and
- the stable aggregate SHA-256 for the shared generated payload is
  `305A2D0CD3F4D56440EF929A67F75D18882E21061E8FEC79FC0406FEA9EA93A6`.

The final focused proof artifacts were:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `M66CardPileProof.dll` | 28,160 | `9DAC7B5D15DB38F8612F936C6ADA99636BD77AF6450E4C72563892E1DBBFCFB5` |
| `M66CardPileProof.json` | 363 | `3BF648DF15F9BF55E0418FB18B0CB5E19F9D5E3BB29A2A8438EE717CF33F5C9E` |
| `M66CardPileProof.pck` | 1,945 | `A0A5AE3F388CCF8A1F04007B928C43E49327B9006987B4EA7DCFF5723DAA0A62` |
| `M66CardPileProof.pdb` | 16,188 | `1BBA7A957D0F62B69BD6C6583B060D9BFEC432DC09B08A55DD34A3656EC07FD3` |

## Human-led acceptance

The human lead reported that the complete focused headed matrix passed after the final
mouse-targeting repair. The accepted observations cover:

- empty, one, full, and rejected-overflow states;
- deterministic Top/Bottom insertion, non-play movement, exact order, and distinct
  same-model instances;
- native hover/tooltips, playable and unplayable glow, mouse interaction, controller focus,
  and normal return between ExtraHand and native Hand;
- no numbered labels on ExtraHand Cards and numbered shortcuts selecting only native-Hand
  Cards from initial render onward;
- no-target, single-target, and multi-target manual play;
- insufficient payment, target cancellation, and queued-action cancellation without lost
  Cards, double payment, or duplicate hooks;
- successful play into the Card's normal result pile;
- immediate consecutive plays, targeted Cards from every ExtraHand position, and a targeted
  Card remaining as the only ExtraHand Card; and
- stable 16:9/16:10 placement plus complete combat-end cleanup and an empty second combat.

No screenshots are retained. These interaction, presentation, and layout claims are owned
by the human lead's direct report; the log corroborates the setup state and successful
ExtraHand play entries but does not replace that report.

## Tier 1

The current-run log contains the exact load marker and matching framework/host profile:

```text
[INFO] [M66CardPileProof] [T2MOD-SELFTEST] M66CardPileProof loaded ok framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1
```

However, the final `grep_log.py` read occurred after game shutdown and found Godot
renderer/resource leak blocks after the marker. Therefore the literal no-fresh-error Tier 1
gate did not pass. The log contains no Package 4 exception, but that narrower fact is not
renamed a strict Tier 1 pass.

## Strict Tier 2 exception

Per explicit human-lead decision, strict Tier 2 is not run for this Package 4 closure. The
proof emitted no structured terminal state line and no `selftest done`; strict Tier 2 is an
intentional verification exception and is not reported as a pass. The focused headed
acceptance substitutes only for the interaction and presentation matrix above.

## Proof retirement

After recording the human-led result, log/Tier exceptions, artifact hashes, source tests,
and generated-payload parity, the game process was confirmed absent. The disposable
`C:\Users\YY\AppData\Local\Temp\open-mod-m66-card-pile-proof` project and deployed
`mods/M66CardPileProof` directory were deleted. They are retired proof artifacts, not
maintained product sources or future regression hosts.

## Remaining boundary

The promotion does not add run-persistent or hidden piles, multiplayer/remote-player UI,
vanilla-pile replacement, arbitrary layout callbacks, or a redirect that retains an already
played source Card. Other documented public Card Piles Package consumers remain supported
under the Package-level rule when their public APIs exist; missing open-mod recipes remain
authoring gaps rather than invented lifecycle claims.
