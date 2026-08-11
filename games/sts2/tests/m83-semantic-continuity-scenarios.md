# M8.3 semantic continuity and backtracking scenarios

These cases define routing behavior when Author, Build, Verify, headed observation, Repair,
or Finalize finds a difference. They are workflow contracts, not runtime proof. Every active
repair preserves unrelated operations and settlements.

## Case 1 - technical path correction

- **Classification:** `implementation-equivalent`.
- **Owner:** `MEMORY.md`; preserve the affected `D/OP` ids and name no affected `E` id.
- **Reopen:** the earliest changed scaffold/author/build stage, then only its downstream checks.
- **Ask:** no user question because player-facing meaning is frozen and unchanged.
- **Stop/resume:** stop if the fix changes meaning; otherwise resume after the corrected stage passes.

A grounded namespace, manifest, or package-path correction may make the same operation build or
load. Any source/output change rebuilds before Verify.

## Case 2 - harness did not reach the scenario

- **Classification:** `implementation-equivalent`, or no repair when Finalize records an exception.
- **Owner:** `MEMORY.md`; preserve all semantic ids.
- **Reopen:** `verify-tier-2` for navigation/timing only.
- **Ask:** no design question; manual observation remains human-owned.
- **Stop/resume:** never rewrite the Mod; resume when the harness reaches the scenario, or report Tier 1 plus exception.

`selftest FAILED` or timeout is harness/setup evidence, not a failed Mod behavior.

## Case 3 - a technical fix changes visible meaning

- **Classification:** `accepted-semantic-change`, not `implementation-equivalent`.
- **Owner:** `DESIGN.md`; preserve ids until the accepted delta says which change.
- **Reopen:** `design` first, then affected SPEC/output/check stages.
- **Ask:** one explicit question naming the changed text meaning, fallback, or proof expectation.
- **Stop/resume:** stop before the fix; resume only after DESIGN-first acceptance.

## Case 4 - Exhaust lifecycle or text is incomplete

- **Classification:** `contract-fulfillment`.
- **Owner:** `SPEC.md`; preserve the accepted Exhaust `D/E/OP` meaning.
- **Reopen:** `spec` only when a required field is absent, otherwise `author`; then build and affected Verify.
- **Ask:** none; the user already chose Exhaust.
- **Stop/resume:** stop if the exact route is broken; otherwise resume after damage, result pile, and engine-composed text all pass.

A Card that deals correct damage but enters Discard, or omits Exhaust meaning, has not fulfilled
the complete operation.

## Case 5 - owner guard lacks a neutral result

- **Classification:** `contract-fulfillment`.
- **Owner:** `SPEC.md`; preserve the multiplier `D/E/OP` ids.
- **Reopen:** `author`, then build and both modified/neutral proofs.
- **Ask:** none while the declared subject and neutral result remain unchanged.
- **Stop/resume:** resume only when owner and unrelated-target cases both pass.

This is a source-contract scenario, not M8.6's deferred real-host proof.

## Case 6 - one shared value is stale on another consumer

- **Classification:** `contract-fulfillment`.
- **Owner:** `SPEC.md`; preserve ids and the one owning value.
- **Reopen:** the earliest output containing the stale rules text, DynamicVar/Hover Tip,
  localization, preview, or presentation, then its proof.
- **Ask:** none; this is not cosmetic equivalence.
- **Stop/resume:** resume after every applicable consumer reads the same value.

## Case 7 - SPEC omitted an accepted field

- **Classification:** `contract-fulfillment`.
- **Owner:** `SPEC.md`; preserve DESIGN and its `D/E` ids, updating the affected `OP` trace only as needed.
- **Reopen:** `spec`, all four pre-scaffold validators, Author, Build, and affected Verify.
- **Ask:** no repeated question for the same accepted result.
- **Stop/resume:** stop on validator failure; resume after the corrected operation validates.

## Case 8 - third turn becomes after three Attacks

- **Classification:** `accepted-semantic-change`.
- **Owner:** `DESIGN.md`; update affected `D/E/OP` meaning only after acceptance.
- **Reopen:** `design` first.
- **Ask:** explicitly compare turn timing with attack-count timing.
- **Stop/resume:** stop before the easier implementation; resume only on acceptance.

## Case 9 - replacement becomes composition or multi-target becomes single-target

- **Classification:** `accepted-semantic-change`.
- **Owner:** `DESIGN.md`; preserve the original ids while blocked, then update the accepted delta.
- **Reopen:** `design` first.
- **Ask:** accept the exact visible difference, defer it, or remove it.
- **Stop/resume:** never patch forward; resume only from an explicitly selected supported result.

## Case 10 - unaccepted placeholder art fallback

- **Classification:** `accepted-semantic-change`.
- **Owner:** `DESIGN.md`; after acceptance add the `PLACEHOLDER`, exclusion, and affected `E` settled by `user-decision`.
- **Reopen:** `design`, then affected SPEC/presentation/finalize work.
- **Ask:** one fallback decision unless the checked fallback was already accepted.
- **Stop/resume:** stop before substitution; resume from recorded acceptance.

## Case 11 - cumulative fallbacks change the deliverable

- **Classification:** `accepted-semantic-change`.
- **Owner:** `DESIGN.md`; update the combined claim, exclusions, affected experiences, anchors, and queue.
- **Reopen:** `design` first.
- **Ask:** one bounded confirmation of the combined result, not isolated local approvals.
- **Stop/resume:** resume only when the literal deliverable shape remains honest.

## Case 12 - no maintained route

- **Classification:** `missing-capability`.
- **Owner:** `shared recipe/reference`; preserve consumer `D/E/OP` intent as blocked.
- **Reopen:** no consumer stage while upstream is missing.
- **Ask:** no approximation question; a genuinely different result uses Case 9.
- **Stop/resume:** stop without consuming an attempt; resume only after the route is promoted or the user accepts a DESIGN change.

Distinguish an absent public API from a documented public Package whose maintained authoring is
missing.

## Case 13 - a claimed shared route fails reality

- **Classification:** `missing-capability` under `INV-9`.
- **Owner:** `shared recipe/reference`; preserve the consumer ids and record the smallest failing contract.
- **Reopen:** no consumer stage; repair or narrow the shared route first.
- **Ask:** none unless the user later selects a different supported result.
- **Stop/resume:** block without a private copy; resume after upstream conformance is restored.

## Case 14 - user playtest feedback changes balance or feel

- **Classification:** `accepted-semantic-change` once an exact delta is proposed.
- **Owner:** `DESIGN.md`; preserve the report as user evidence and affected ids until acceptance.
- **Reopen:** existing revision route, `design` first, then only affected stages.
- **Ask:** only the bounded semantic decision; do not diagnose or tune automatically.
- **Stop/resume:** resume after acceptance and validation, not merely after receiving feedback.

## Case 15 - legacy project resumes without backfill

- **Classification:** none until a new difference starts a repair; then use one of the four routes.
- **Owner:** existing DESIGN/SPEC/PLAN/MEMORY compatibility state.
- **Reopen:** the existing first unfinished stage unless a new active repair names another route.
- **Ask:** no migration question for an unchanged pre-M7.5, pre-M8.1, or v1-SPEC project.
- **Stop/resume:** resume unchanged; create only the active PLAN block for a new repair, and migrate current contracts only when existing revision rules require it.

## Evidence boundary

These cases prove deterministic routing and artifact-state checks only. They do not prove a
generated Mod, runtime behavior, human acceptance, design quality, or complete in-game surface
coverage.
