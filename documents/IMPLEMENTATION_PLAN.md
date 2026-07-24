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

Triage and fix bugs found through real user testing while executing the lead-approved
M6.5 Character content-quality milestone below. Do not prepare a GitHub release until the
lead explicitly decides that stabilization is sufficient.

The old plan's first recommended RitsuLib expansion slice was promotion of the Scry helper
into the documented Card pipeline; R6 absorbed and completed that work. It is not a
remaining migration gate. Do not automatically start M7, another expansion slice,
multiplayer presentation, audio, or animation/material work outside the bounded M6.5
packages. M6.5's non-Spine cues, pool frame material, and parameterized trail do not
authorize broader production animation or custom-material work.

## M6.5 - Character Content Quality

M6.5 is the next approved content-quality milestone. It improves the existing RitsuLib-only
Character pipeline; it does not reopen M6 migration work, revive R7, or imply that any item
below is already supported. Promote each surface only after its own real consumer proof.

Execute these work packages in order:

1. **CharacterArtBundle and identity reference chain.** Define one structured bundle for
   every Character art slot, including required/optional status, output path, dimensions,
   alpha policy, fallback, and consumer. Establish one approved canonical identity image
   or character sheet, then pass it as an identity reference to later portrait/body/icon
   generations in addition to type-matched STS2 style references. Preserve the existing
   per-paid-call consent boundary. Add bundle validation and a contact-sheet/composite
   review; do not use a brittle image-similarity score as runtime acceptance. Generate the
   five energy layers as one coordinated sub-bundle with common canvas geometry and a
   composite preview rather than five unrelated images.
   **M6.5.1 passed 2026-07-24.** The source bundle now owns 14 slots across 10 specs, with all 12
   promoted static assets required for custom Character art and locked selection/map marker
   retained as optional unpromoted slots. Selection bootstraps the approved identity;
   later Character acquisitions require it in addition to type-matched style references.
   Contract validation, the contact sheet, shared-canvas Energy composite, generated
   payloads, and the 91-test tool suite passed. MeridianProof built with 0 warnings/errors,
   passed the exact Tier 1 profile marker with no fresh error block, and the lead accepted
   the real selection, combat/top-panel/Energy, RestSite, and Shop consumers. This closes
   work package 1 only; work package 2 is next.
2. **Character-wide card/UI theming.** Add a character card-pool frame material through
   RitsuLib's supported pool material surface. Split the large pool energy icon from the
   small text energy icon, grounding each size and consumer before implementation. Add the
   top-panel outline asset and wire `IconOutlineTexturePath`. Prove the card frame, both
   energy-icon consumers, normal top icon, and outlined top icon independently.
3. **Locked selection, map marker, and parameterized trail.** Finish the existing
   `character_select_locked` and `character_map_marker` routes, then visibly prove the real
   locked-select and run-map hosts before promotion. Add a Character-specific card trail
   first through RitsuLib `CharacterTrailStyle` parameters and existing supported trail
   resources; custom trail scenes, shaders, and materials are not part of this slice.
4. **Non-Spine combat cue sequences.** Add identity-consistent frame assets and RitsuLib
   cue/state-machine wiring for `Idle`, `Attack`, `Cast`, `Hit`, and `Dead`. Verify trigger
   routing, loop/one-shot behavior, timing, return-to-idle behavior, death delay, cleanup,
   and fallback in a real combat. This work package does not authorize a Spine pipeline or
   animated merchant/rest-site production assets.
5. **Fresh acceptance and payload refresh.** After focused contract and hosted proofs pass,
   generate one fresh natural-language Character Mod that exercises the complete M6.5
   composition. Require exact load marker, structured post-state/presentation proof,
   `selftest done`, settled screenshots for every visible host, and no fresh error block.
   Record durable evidence, retire the acceptance Mod, and regenerate both committed
   payloads from `games/sts2/`.

M6.5 is complete only when all five work packages are pipeline-supported on STS2 `0.107.1`
and RitsuLib `0.4.62`. A path existing in a profile, a successful PCK build, or a fallback
image appearing does not close a package. RitsuLib Character presentation patches are
non-critical, so each new route needs an exact-resource assertion plus visible headed
evidence in its real host.

Explicitly outside the current M6.5 scope are Spine authoring, custom transition
materials/shaders, production audio, multiplayer hands/remote UI, native custom-Character
Ancient presentation, animated merchant/rest-site production assets, and release work.
The lead may add other content-quality items later; they are not inferred from this
milestone and do not expand it automatically.
