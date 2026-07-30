# M6.6 Package 2B/2C gameplay readability results

Date: 2026-07-30

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, compat `0.107.1`, and a
generated runtime dependency on `STS2-RitsuLib >= 0.4.62` only.

## Outcome

Package 2B Card hand readability and Package 2C Relic/Power corner-label authoring are
implemented and accepted through a focused human-led real-host review.

Generated Cards may declare ordered fixed-color hand-emphasis rules with explicit priority,
later-rule tie resolution, and visibility while unplayable. Generated Relics may expose up
to three supplemental labels in distinct `TopLeft`, `TopRight`, and `BottomLeft` corners.
Generated Powers may expose one supplemental `TopLeft` label while preserving the native
main amount.

The narrower Power boundary is deliberate. The pinned RitsuLib Power presets are not
clipped to one compact icon: left presets use a 100-pixel-wide band and `TopRight` extends
left from x=-56. The first crowded 16:9 host review found that multiple Power labels could
overflow into an adjacent Power. Open-mod therefore does not combine Power presets or
generate an unproved custom rectangle. The documented dual-number Power use case remains
available as the native amount plus one supplemental value.

Intent remains a supported public consumer in RitsuLib's Extra Badges Package, but its
authoring recipe was removed from active M6.6 work by human-lead decision. This result does
not add Intent authoring.

## Pipeline contract

The pipeline records hand-emphasis meaning, condition, fixed color, integer priority, and
unplayable visibility. It lowers one simple gold/red rule through the native channel or all
competing/custom-color rules through one typed `CardHandOutline<TCard>` ruleset. It never
mixes both resolvers on one Card.

Relic/Power badge intake records auxiliary meaning, bounded formatter, plain or one bounded
color span, refresh event, and removal condition. It preserves the native main amount,
rejects bottom-right and arbitrary-rectangle authoring, and uses exactly one normal host
display or independent invalidation path per mutation. Relic text is bounded to four
visible characters; Power text is bounded to six.

## Automated evidence

- the focused semantic-contract suite passed 14 tests;
- the complete STS2 tools suite passed 124 tests;
- source Python files compiled successfully;
- all six source/plugin/portable skill roots passed `quick_validate.py`;
- regenerated plugin and portable payloads contained 151 shared files after excluding
  `__pycache__` and portable-only `GENERATED.md`, with zero path or SHA-256 mismatch;
- `M66ReadabilityProof` built with zero warnings and zero errors after host, compat,
  dependency, resource-manifest, localization/PCK, and runtime-profile checks passed; and
- `git diff --check` reported no whitespace error.

These checks prove the semantic, build, and delivery contracts. They do not replace the
headed presentation observations or manufacture a strict Tier 2 result.

## Focused host

The disposable `M66ReadabilityProof` Mod registered:

- one `Signal Card` with gold, purple, and red competing hand rules;
- `Raise Signal`, `Clear Signal`, and `Spend Energy` setup Cards;
- one `Readability Relic` with zero/one/three-label states plus four filler Relics; and
- one `Readability Meter` Power plus four filler Powers for crowded-row checks.

The final deployed proof artifacts were:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `M66ReadabilityProof.dll` | 20,480 | `FEE0059FA3886778EF5A7910BDF5BCD4D4FF3A87DFD70867FF208428B6796885` |
| `M66ReadabilityProof.json` | 388 | `A723D38A78EB54D52DF6E6FA6B2931A046A08936701D47741E044593AB191DE1` |
| `M66ReadabilityProof.pck` | 3,618 | `F09EAB08D43444C816640B0627897B46B6BC4D98FDBA144BF3E45C5E2319E4C0` |
| `M66ReadabilityProof.pdb` | 13,876 | `8954A84BCBF3FB0B6537FE0136ECD60EDC279A64B023EB1286A12A08E04ED67C` |

## Human-led acceptance

The initial human-led matrix passed every requested item except the crowded 16:9 Power row.
That first pass established:

- Card activation/deactivation and gold/purple/red priority changes;
- expected playable/unplayable visibility, hover/drag behavior, and hand cleanup;
- Relic zero/one/multiple labels, plain/rich text, refresh, removal, and native-counter
  preservation;
- Power state refresh/removal and native-counter preservation outside the failing crowded
  multi-label layout; and
- a normal crowded Relic row at 16:9.

After Power authoring was narrowed and the proof rebuilt, the human lead reported the
focused recheck passed at both 16:9 and 16:10. The accepted final Power observations cover:

- exactly one top-left supplemental label through plain `+1`, gold rich-text `+2`, and
  plain `+3` states;
- no intrusion into either adjacent filler Power in the crowded row;
- readable native bottom-right amount, icon, and tooltip; and
- complete label removal with the host Power and no visible cleanup residue.

No screenshots are retained. Color, layout, interaction, tooltip, overlap, and cleanup
claims are owned by the human lead's direct headed report.

## Tier 1

The current-run log contained the exact marker:

```text
[INFO] [M66ReadabilityProof] [T2MOD-SELFTEST] M66ReadabilityProof loaded ok framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1
```

The framework profile matched and `grep_log.py` found no fresh error after the Mod load.
Strict Tier 1 passed.

## Verification exception

The proof had no armed automated hosted harness. It emitted no structured post-state proof
and no `selftest done`, so strict Tier 2 was not run and is not reported as a pass. The
human-led headed result substitutes only for the focused interaction and presentation
matrix described above.

## Proof retirement

After recording the human-led result, strict Tier 1 log evidence, artifact hashes, delivery
checks, and strict Tier 2 exception, the game process was confirmed absent. The disposable
`C:\Users\YY\AppData\Local\Temp\OpenModM66ReadabilityProofWork` project and deployed
`mods/M66ReadabilityProof` directory were then deleted. They are retired proof artifacts,
not maintained product sources or future regression hosts.

## Remaining boundary

Generated hand emphasis remains fixed-color and refreshes through normal combat-state
changes. Generated Power badges remain limited to one top-left label; arbitrary rectangles,
bottom-right labels, multiple generated Power labels, and Intent badge authoring are not in
the active pipeline. Package 4 combat-only singleplayer CardPile/ExtraHand is the direct
next M6.6 development step but does not start without human-lead selection.
