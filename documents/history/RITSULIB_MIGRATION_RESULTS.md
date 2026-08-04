# RitsuLib migration results

Closed: 2026-07-24

## Decision

open-mod retired its BaseLib implementation and now generates RitsuLib-only Mods for STS2
stable `0.107.1`. The pinned compile/runtime version is RitsuLib `0.4.62` with the
`0.107.1` compat target.

## Phase Result

| Phase | Result |
|---|---|
| R0-R1 | dependency/API inventory and framework-neutral semantic contract completed |
| R2 | source-owned pinned scaffold, build/profile validation, empty consumer load, and negative compat diagnostics completed |
| R3 | card, relic, potion, power, keyword, enchantment, and orb completed |
| R4 | Monster + Encounter, Event / World Node, Character Foundation, and promoted static Character consumers completed |
| R5 | stateful relic cadence, Secondary Resource/payment, ordered semantic buffer, public combat UI, and final Wayfinder composition completed |
| R6 | generated-Mod-local singleplayer Scry helper completed |
| R7 | canceled by the human lead; no pass is claimed |
| R8 | temporary proof/runtime artifacts removed, active BaseLib path retired, docs reset, and Codex/portable `0.6.0` payloads produced |

All completed technical phases used the stable host and RitsuLib-only runtime dependency,
reached their required hosted state markers plus `selftest done`, and recorded no fresh
target-Mod error. The exact transient proof projects were intentionally deleted after
their contracts and outcomes were promoted.

The R8 maintainer gate passed the Codex plugin validator, all six source/generated skill
validations, all 81 unit tests, Python compilation, dependency/structure checks,
`git diff --check`, and a 269-file publish idempotence comparison.

## Durable Outcome

- Generated projects reference `STS2.RitsuLib.Compat.0.107.1` `0.4.62` only.
- Generated manifests depend on `STS2-RitsuLib >= 0.4.62` only.
- BaseLib and Alchyr templates are absent from the active scaffold/author/build path.
- The art normalizer remains framework-neutral; runtime consumers use RitsuLib asset
  profiles.
- The portable payload and Codex plugin are generated from the same source skills/tools.

BaseLib and Downfall source checkouts remain only as git-ignored offline research under
`baselines/`. Historical M0-M6 records in this directory remain evidence, not current
instructions.

## Residual Boundaries

The migration does not promote vanilla editing, retained-card zones, alternative Energy,
multiplayer UI/Scry, production Character animation/material/audio, native custom-Character
Ancient presentation, arbitrary Event layouts/VFX/chains, or Workshop publishing.

## Acceptance Status

The human lead replaced R7 with an independent clean-workspace Codex user test. On
2026-07-24, the lead reported that the generated Mod worked well in the real game and
accepted the result. This closes the BaseLib-to-RitsuLib migration under the revised plan;
R7 remains canceled rather than passed.

`0.6.0` is not yet a GitHub release. Bug fixes and content-quality improvements remain the
active work before any release decision.
