# Implementation plan: 0.6.0 stabilization

## Status

The RitsuLib migration and external clean-workspace Codex acceptance are closed at the
supported boundary.

- R0-R6: complete with hosted evidence.
- R7: canceled by the human lead; it did not pass.
- R8: complete. Repository cleanup, active-document reset, Codex plugin conversion,
  payload generation, validation, and idempotence checks passed.
- External acceptance: passed in a fresh user-run Codex workspace with a working in-game
  result.

Version `0.6.0` remains an unreleased development baseline. Migration acceptance does not
mean the product is ready for a GitHub release: remaining bugs and content-quality work
take priority.

## R8 Gate

R8 closed with all of the following true:

1. Active source, recipes, scaffold, project files, and manifests have no selectable
   BaseLib implementation path.
2. Historical BaseLib runtime binaries and migration proof directories are removed;
   offline research checkouts remain clearly non-active.
3. README, AGENTS, project status, tests, and skill entry points agree on the RitsuLib-only
   boundary and external acceptance result.
4. `plugins/open-mod` is a valid Codex plugin at `0.6.0` with a repo-local marketplace.
5. `skills/` is regenerated as the portable payload.
6. Both publish modes are idempotent.
7. Unit tests, Python compilation, skill/plugin validation, dependency audit, and
   `git diff --check` pass.

R8 itself did not require another headed STS2 run because the lead replaced R7 with a
separate fresh-user test. That external Codex test subsequently passed. Existing R0-R6
hosted evidence is not rerun without a real regression.

## Current Runtime Architecture

```text
idea -> interview -> semantic SPEC -> grounded recipe -> pinned scaffold
     -> author -> build/package -> Tier 1 -> hosted Tier 2 -> bounded repair
```

The supported framework profile is fixed at RitsuLib `0.4.62` / STS2 `0.107.1`. The
build wrapper validates project, restore, runtime variant, host version, manifest, and
deployed artifacts before verification.

## Verification Ownership

- `CombatPlayer`: content core, stateful cadence, Scry.
- `CombatEnemy`: Monster + Encounter and move vocabulary.
- `MapNode`: Event behavior/presentation and bounded forced follow-up.
- `RunStart` / Character: Foundation, static presentation, resource/UI, ordered buffer.

Use local assertions for deterministic rules. Use one hosted proof per independent
lifecycle or presentation invariant. Fresh acceptance projects are disposable after their
result is recorded.

## Current Work

Triage and fix bugs found through real user testing, then improve the clarity and quality
of generated content. Do not prepare a GitHub release until the lead explicitly decides
that stabilization is sufficient.

The old plan's first recommended RitsuLib expansion slice was promotion of the Scry helper
into the documented Card pipeline; R6 absorbed and completed that work. It is not a
remaining migration gate. Do not automatically start M7, another expansion slice,
animation, materials, multiplayer presentation, or audio. A later instruction must choose
that scope after stabilization.
