# M6.6 Package 3 Relic-owned Rest Site option results

Date: 2026-07-30

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, compat `0.107.1`, and a
generated runtime dependency on `STS2-RitsuLib >= 0.4.62` only.

## Outcome

The first bounded Package 3 slice is pipeline-supported for one option contributed by a
generated-Mod-local Relic in a singleplayer run. The option may use:

- a free or fixed nonnegative Gold cost;
- one deterministic preflightable outcome with no post-payment player choice;
- once-per-Rest-Site or once-per-run repeatability;
- normal leave behavior or one-shot preservation of the other native options; and
- one optional 256x169 opaque custom image with an explicit native Heal-image fallback.

The pipeline distinguishes absence from the native visible-but-disabled state, requires the
same eligibility/payment predicate for rendering and final selection, rejects duplicate
stable option IDs, awaits the complete outcome, and preserves normal Rest Site history and
button ownership. It emits no Harmony, reflection, UI patch, Publicizer, or copied research
Mod implementation.

Card/Modifier owners, variable or non-Gold costs, post-payment choices, rollback-style
arbitrary transactions, repeated successful use in one Rest Site, remote ownership, and
multiplayer remain unsupported.

## Pipeline contract

The modmaker interview and SPEC record owner, localization, eligibility, repeatability,
enabled rule, cost, ordered outcome, stay/leave behavior, optional icon, and the explicit
singleplayer boundary. Authoring routes to the pinned `rest-site-options.md` reference and
RitsuLib's public `ModRestSiteOptionTemplate`, `TryModifyRestSiteOptions`,
`ShouldDisableRemainingRestSiteOptions`, `SavedAttachedState`, and
`RestSiteOptionAssetProfile` surfaces.

The `rest_site_option` art role normalizes one opaque `256x169` image with `cover` into
`images/rest_site_options/<slug>.png`. After the headed result below, that role is marked
live-verified for real custom-button framing and the missing-art native Heal fallback.

## Automated evidence

- the focused semantic/art/acquisition suite passed 65 tests;
- the complete STS2 tools suite passed 122 tests;
- `M66RestSiteProof` built and deployed successfully with host, runtime, dependency,
  manifest, localization, and PCK checks passing;
- both committed payload modes were generated twice after promotion;
- the plugin payload contains 149 files and the portable payload contains 150 files after
  excluding `__pycache__`, with portable-only `GENERATED.md` accounting for the difference;
- all 149 shared relative paths have zero missing files and zero content mismatches;
- the stable aggregate SHA-256 for the shared plugin tree is
  `E9B4AAB14099A638DE45D16CE716F496EAF55422FC4364D4ADB783D55E27B01E`; and
- `git diff --check` reports no whitespace error.

These checks prove the semantic, tooling, build, and delivery contracts. They do not
manufacture the unrun log or strict Tier 2 evidence listed below.

## Focused host

The disposable `M66RestSiteProof` Mod contributed two real Relic-owned options:

| Owner | Option | Cost and outcome | Presentation |
|---|---|---|---|
| `Quiet Forge` | `Reforge` | spend 30 Gold; gain 5 Max HP and the native matching 5 current HP; once per run; keep native options | custom 256x169 image |
| `Fallback Forge` | `Reforge (Fallback)` | same bounded cost/outcome/repeatability | deliberately missing custom path resolved to native Heal image |

The deployed proof artifacts were:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `M66RestSiteProof.dll` | 15,872 | `E818DFAAC20F9C8DA7088176753CC12365EBCED531E24079A03ACAC5AB7D4908` |
| `M66RestSiteProof.json` | 369 | `4BFC4C0F82D0535CD94B8900F6E98253EA83756DEEBFCD5058E81CC41D775122` |
| `M66RestSiteProof.pck` | 5,654 | `07A1CE9A9871624769057FC34A1441E3C666EFAAFC59417A0447B68FEB01D136` |
| `M66RestSiteProof.pdb` | 13,520 | `B6EFAD030405D24C1F6249FB1AAF2533632B19B94D405DE6D84332ED467F9051` |

## Human-led acceptance

The human lead reported that the requested in-game behavior and presentation were normal
and that the complete practical matrix passed. The accepted observations cover:

- no custom option without its owner;
- localized `Reforge` present in the native gray state below its 30-Gold cost and coexisting
  with Heal and Smith;
- enabled selection with the exact 30-Gold payment and +5 current/+5 Max HP outcome;
- removal of the successful custom option while the remaining native options stay usable;
- once-per-run hiding on the next Rest Site;
- normal mouse interaction and controller focus;
- correctly framed custom 256x169 art; and
- `Reforge (Fallback)` visibly resolving to the native Heal image without missing-resource
  or UI problems.

The pinned dev-console `gold` command does not remove Gold: negative inputs are ignored.
The lead used normal Shop spending to establish the insufficient-Gold state. Future manual
instructions must not recommend `gold -N`.

## Verification exceptions

Per explicit human-lead instruction, no post-session `godot.log` or `grep_log.py` check was
performed. Therefore the exact Tier 1 load-marker/no-fresh-error gate was not run and is not
reported as a pass, even though the headed feature was visibly active.

The proof emitted no structured terminal state line and no `selftest done`; strict Tier 2
was not run and is not reported as a pass. Because the console cannot remove Gold, the
literal render-enabled-then-lower-Gold stale-button transition was not independently
reproduced in the headed route. Its final `OnSelect` guard remains enforced by the copied
reference shape and semantic contract tests, but that source evidence is not renamed a
hosted pass.

No screenshots are retained. Localization, gray state, mouse/controller behavior, exact
visible deltas, option rebuilding, repeatability, and image framing are accepted from the
human lead's direct report.

## Remaining boundary

The promotion does not include Card/Modifier owners, variable/non-Gold/post-payment costs,
arbitrary rollback transactions, same-site successful repeat, multiplayer/replay, custom
Rest Site layouts, direct room transitions, or generated patches. Package 2B/2C gameplay
readability is the direct next step in the approved M6.6 order and does not start
automatically.
