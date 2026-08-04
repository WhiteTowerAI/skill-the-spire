# M6.6 Package 2A computed Card values results

Date: 2026-07-29

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, compat `0.107.1`, and a
generated runtime dependency on `STS2-RitsuLib >= 0.4.62` only.

## Outcome

Package 2A computed Card previews, icon variables, typed Power amounts, and variable
tooltips are pipeline-supported. This promotion is limited to Card values expressible as
one pure bounded formula with explicit live inputs, integer domain, upgrade behavior, and
evaluation point. Package 2B hand emphasis and Package 2C corner labels remain unsupported.

The pipeline now records calculated semantics during interview/SPEC, routes authoring to a
pinned RitsuLib recipe/reference, and requires execution through the matching
`Compute*Value` helper rather than `BaseValue` or display-only `PreviewValue`.

## Focused Host Proof

The disposable `ComputedValuesProof` Mod exercised four real hand Cards:

- Damage equal to current Block, plus 2 when upgraded, with Strength and target-specific
  Vulnerable applied exactly once;
- Block equal to four times current Stars, plus 4 when upgraded, with Dexterity and Frail
  applied exactly once;
- Energy and Star gains equal to current Block and capped at 4, including Energy zero as
  `0` plus one icon, repeated Energy icons for 1-3, numeric Energy fallback at 4, and one
  Star icon per positive count;
- raw Poison 2 versus Snecko Skull amount-given preview/application 3.

The human lead manually accepted zero, changed, maximum, base, and upgrade displays; exact
Damage, Block, Energy, Stars, and Poison outcomes; no stale icons, clipping, or overlap;
and the localized `Measured Charge` null-icon tooltip on a spawned hand-Card clone. The
lead subsequently repeated the no-Block upgraded-Damage case and the ordinary Block case
and reported exact outcomes of 12 and 9 respectively. At the lead's direction, no further
log read was performed after that final manual confirmation.

Tier 1 found the exact load marker, matching framework/host profile, and no fresh error
after the proof Mod loaded:

```text
[T2MOD-SELFTEST] ComputedValuesProof loaded ok framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1
```

Earlier diagnostic lines agreed with the accepted icon, ordinary Damage, upgraded Block,
and Poison cases. They remain diagnostics rather than substitutes for the lead's manual
behavior and presentation review.

## Automated Source Evidence

Before promotion, the focused semantic-contract suite passed 9 tests, the complete source
tools suite passed 106 tests, and `git diff --check` reported no whitespace error. The
proof Mod built and deployed with no warning or error and contained no BaseLib, Publicizer,
or generated Harmony dependency.

## Payload Refresh

Both committed payloads were generated twice from `games/sts2/` through explicit Git Bash
`publish.sh --plugin` and `publish.sh --portable` runs. Each result contained 21 modmaker
files, including 10 bundled Python tools, and 124 sts2-api files. Excluding the intentional
portable-only `GENERATED.md`, the plugin and portable trees had 145 shared files, zero path
or content mismatches, and the same aggregate SHA-256:

```text
C53E563590CBA9DC291197755B843DDFFA2C6AF18489C3465E29D06966AB6D33
```

The second publish did not change that digest. All six source/plugin/portable skill roots
passed `quick_validate.py`; the plugin manifest and repo marketplace contract passed; no
runtime path placeholders remained; the RitsuLib profile suite passed 6 tests; the full
tools suite still passed 106 tests after publication; and 39 source/payload Python files
compiled in memory.

## Accepted Exceptions

- The disposable proof did not include a structured post-state harness and did not emit
  `selftest done`; strict Tier 2 was not run and is not claimed as passed.
- No screenshots are retained. Headed text, icons, reflow, tooltip, and state changes are
  accepted from the human lead's direct in-game report.
- The proof project lives outside the repository and is not a maintained fixture or
  shipped payload input.

## Promotion Boundary

Generated Cards may use computed Damage/Block, Energy/Star icon counts, raw and
amount-given typed Power values, and declared localized variable tooltips under the shared
formula contract. Static values keep their existing typed DynamicVar routes. Arbitrary
per-frame formulas, unbounded icon counts, display-only duplicate calculations, custom
formatters, Package 2B/2C presentation, and unrelated M6.6 surfaces remain unsupported.
