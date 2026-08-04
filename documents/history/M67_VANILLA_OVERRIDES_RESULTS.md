# M6.7 vanilla overrides consolidated results

Date: 2026-08-04

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.5.4`, compat `0.107.1`,
and generated runtime dependencies on `STS2-RitsuLib >= 0.5.4` only.

## Outcome

M6.7 is closed by explicit human-lead decision. M6.7.0 through M6.7.5 implement the
approved singleplayer vanilla-override matrix; M6.7.6 was canceled on 2026-08-03 and
multiplayer vanilla overrides moved to Future Outlook.

On 2026-08-04, the human lead reported that the fresh independent-session in-game test
completed successfully and that the effects passed, then explicitly approved declaring
M6.7 complete. This is a representative milestone acceptance, not an exhaustive proof of
every provider, hook, target, or operation.

## Delivered packages

- M6.7.0: pinned `0.107.1` grounding catalog, localized aliases, semantic manifest,
  fingerprint/baseline/conflict checks, and fail-closed scaffold/build wiring.
- M6.7.1: public existing-Card property, text, play, and owner-hook composition.
- M6.7.2: all 44 public RitsuLib `0.5.4` Card-material and external-asset providers.
- M6.7.3: existing-Ancient option append or checked complete initial-option replacement,
  Mod-owned pages, deterministic effects, and native finish/history.
- M6.7.4: public epoch gates plus checked Card/Relic/Potion pool and availability routes.
- M6.7.5: public non-Card owner hooks, intrinsic data, lifecycle/body replacements,
  Monster move graphs, Encounter rosters, and ordinary Event option/page routes.

The five nonempty Packages remain singleplayer. Operations outside their documented public
or fixed-Adapter routes still fail closed. Vanilla Card base descriptions remain intact
under RitsuLib `0.5.4`; generated effect text composes before or after that body rather than
replacing it.

## Source and payload evidence

The final authoritative-source pass completed before the independent acceptance:

- the complete STS2 regression passed `165/165`;
- Python compilation and all six source/plugin/portable skill-root validations passed;
- plugin and portable payloads were generated twice with `161` effective files each;
- repeated payload generations had zero relative-path or content differences and the
  stable aggregate SHA-256 was
  `E70C6432CFC60E448360CAA214260048961F5FDA1B166B19B6B12BC28420F0C9`;
- the local plugin was reinstalled as `0.6.0+codex.20260803094354`; and
- the installed cache at
  `C:\Users\YY\.codex\plugins\cache\open-mod\open-mod\0.6.0+codex.20260803094354`
  had zero relative-path or file-hash differences from the repository plugin payload.

These checks close the deferred source regression, payload synchronization, repeatability,
dependency-boundary, and installed-plugin delivery gates. They do not count as headed
gameplay, Tier 1, or Tier 2 evidence.

## Independent acceptance Mod

The acceptance ran in the independent workspace
`D:\user_test_openmod\vanilla-reforged-mod` using only the reinstalled plugin payload.
The generated Mod ID was `VanillaReforged`. Its manifest targets STS2 `0.107.1`, depends
only on `STS2-RitsuLib >= 0.5.4`, and declares both DLL and PCK content.

The semantic manifest contains 13 representative operations:

- Ironclad Strike capability variables, title replacement, appended effect text, complete
  `OnPlay` replacement, teal frame, deliberately missing optional banner fallback, and an
  Ironclad-to-Silent pool move;
- Burning Blood combat-start owner-hook composition while retaining the original healing;
- Darv complete initial-option replacement plus fixed Gold cost, Mod-owned page, native
  finish/history, and an initial-portrait override;
- Fuzzy Wurm Crawler fixed initial HP and deterministic complete move graph; and
- the weak Fuzzy Wurm Crawler Encounter's paired runtime/all-possible roster replacement.

This samples M6.7.1 through M6.7.5 without turning every public provider, model family, or
hook into a separate acceptance case.

The retained `.build.log` records a successful build in `00:00:00.87` with zero warnings
and zero errors. The source build output and deployed DLL are byte-identical.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `VanillaReforged.dll` | 32,768 | `E397D258EB05F71524CE6123C98421C54E573D20CC8A425D3ED207E76B760354` |
| `VanillaReforged.pck` | 15,115 | `86F10E4A41C7AF076006224062C54A6274F99B6AD0F7A80DD91B351B3E08CEAD` |
| `VanillaReforged.json` | 393 | `4795842FCF1B26AAAECEA9028CB6B01E7D1C339665149973E8165DFEEDEF5483` |
| `openmod/vanilla-overrides.json` | 15,982 | `D830BB7F4B15FB1632D736905801D8F309E1E353D3B5A225B7750F8CDAFFC4C8` |

## Human-led acceptance

The human lead opened the generated Mod from a new session and reported that the effect
test passed smoothly. That literal report accepts the selected representative Mod as a
whole. No more granular observation is inferred for an individual option state, frame,
fallback, pool cache, save transition, intent, or roster consumer.

## Verification exceptions

- No post-session log inspection or strict Tier 1 exact-load-marker/no-fresh-error check
  was run; Tier 1 is unrun, not passed.
- No Tier 2 harness, structured post-state marker, or `selftest done` was authored or run;
  Tier 2 is unrun, not passed.
- The separate current-localized-catalog headed no-op was intentionally not run. Earlier
  grounding-kernel collector/no-op evidence remains historical evidence only.
- Package-specific representative C# compiles omitted during M6.7.2-M6.7.5 source
  development were not retroactively renamed as passes. The consolidated acceptance Mod
  did compile the selected routes successfully.
- Unselected visual providers, owner hooks, lifecycle families, intrinsic data routes,
  availability modes, ordinary Event routes, save/load and existing-save variants, seeded
  order/RNG, duplicate/cross-Mod cases, and multiplayer behavior remain unrun.
- No screenshot set or agent-driven headed run substitutes for the human lead's report.

## Retained acceptance state

No STS2 or Godot process was running when the final evidence was recorded. The independent
acceptance workspace and deployed `mods/VanillaReforged` copy remain intact because their
deletion was not authorized. They are disposable evidence, not maintained fixtures; any
later retirement is cleanup only and does not reopen or change this closure result.
