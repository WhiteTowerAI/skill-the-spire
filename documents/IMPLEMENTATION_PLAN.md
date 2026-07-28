# Implementation plan: 0.6.0 stabilization

## Status

Version `0.6.0` is an unreleased RitsuLib-only development baseline. The
BaseLib-to-RitsuLib migration and external clean-workspace Codex acceptance are closed;
the durable migration record is
`documents/history/RITSULIB_MIGRATION_RESULTS.md`.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
pipeline-supported. Their evidence is recorded in
`documents/history/M65_CHARACTER_QUALITY_FOCUSED_RESULTS.md`. The fresh Prismwright
acceptance and its explicit lead-approved verification exceptions are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`; M6.5 is closed.

Do not prepare or claim a GitHub release or start another expansion slice without a later
explicit instruction from the human lead.

## Dependency Boundary

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.4.62`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.4.62`.
- Generated Mods must not reference, package, or depend on BaseLib or use historical
  Alchyr templates. Offline BaseLib/Downfall checkouts remain research-only.

## Current Runtime Architecture

```text
idea -> interview -> semantic SPEC -> grounded recipe -> pinned scaffold
     -> author -> build/package -> Tier 1 -> hosted Tier 2 -> bounded repair
```

The build wrapper validates project, restore, runtime variant, host version, manifest,
and deployed artifacts before verification.

## Verification Ownership

- `CombatPlayer`: content core, stateful cadence, Scry, and Character combat cues.
- `CombatEnemy`: Monster + Encounter and move vocabulary.
- `MapNode`: Event behavior/presentation and bounded forced follow-up.
- `RunStart` / Character: Foundation, static presentation, resource/UI, and ordered
  buffer.

Use local assertions for deterministic rules. Use one hosted proof per independent
lifecycle or presentation invariant. Fresh acceptance projects are disposable after
their result is recorded.

## Current Work

Continue triaging bugs found through real user testing. No M6.5 gate remains scheduled.
On 2026-07-29, the human lead reported the headed Prismwright acceptance successful,
explicitly waived the remaining Tier 2/self-test harness, and directed retirement. The
load marker and runtime profile matched; the strict log parser separately reported only
engine-shutdown resource-leak messages after the headed session. M6.5 is closed by that
lead decision rather than by claiming those omitted checks passed.

Do not reopen Prismwright, start M7 or another expansion slice, or prepare a GitHub release
without a later explicit instruction from the human lead.

## Current Boundaries

M6.5 has no separate Character-sheet generation, locked-selection route, custom map
marker, Character trail, or `Cast` cue. Characters keep the checked game-native shared
map-marker fallback. Full-energy acquisition uses one Character-specific layer plus four
fixed templates. Combat cues remain the private, combat-only, all-or-nothing
`Idle`/`Attack`/`Hit`/`Dead` set; they do not promote Spine, animated merchant/rest-site
bodies, production audio/materials, or multiplayer presentation.

Locked-selection presentation, Character-specific card trails, additional combat cue
states, native custom-Character Ancient presentation, retained-card zones, alternative
Energy, vanilla editing, arbitrary Event layouts/chains, and one-click Workshop publishing
remain unsupported. None is a scheduled follow-up package.
