# Implementation plan: M7 design intelligence and user experience

## Status

Version `0.6.0` is the unreleased RitsuLib-only development baseline for STS2 stable
`0.107.1` and RitsuLib `0.5.4`. The BaseLib migration and M6.5-M6.7 implementation tracks
are closed. Their plans, focused results, acceptance evidence, waivers, and unrun checks are
historical records under `documents/history/`; they are not active work in this plan.

M7 improves how the skill understands, discusses, scopes, records, and revises a Mod design
without expanding the runtime capability graph. M7.0 was canceled as a standalone
evaluation Package. M7.1 through M7.5 are implemented in source and synchronized into the
plugin and portable payloads. M7.6 has not started and is the only remaining planned M7
Package.

The current literal results are:

- `documents/history/M71_ADAPTIVE_ROUTING_RESULTS.md`;
- `documents/history/M72_NATIVE_DESIGN_GRAMMAR_RESULTS.md`;
- `documents/history/M73_MECHANIC_CONTENT_BALANCE_RESULTS.md`;
- `documents/history/M74_SCOPE_TRACEABILITY_RESULTS.md`; and
- `documents/history/M75_COHERENCE_RESULTS.md`.

Do not prepare or claim a GitHub release, reopen a closed M6 proof, or start M7.6 without
later human-lead instruction.

## Dependency Boundary

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.5.4`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.5.4`.
- The compile package remains exactly `0.5.4`; a newer runtime is accepted only with the
  exact `0.107.1` compat variant, marker, and manifest hash.
- Generated Mods must not reference, package, or depend on BaseLib or use historical
  Alchyr templates.
- Runtime support remains the exact graph in
  `games/sts2/tests/content-capability-graph.md`. Design confidence never promotes an
  unsupported runtime operation.

## Implemented Flow

```text
idea
  -> state check / direct unfinished-project resume
  -> inferred fast / co-design / revision route
  -> lazy relevant native grammar, planning, and coherence references
  -> adaptive interview for material unresolved decisions only
  -> durable DESIGN.md with current/future scope and coherence
  -> validated current-slice SPEC.md operation allowlist
  -> grounded scaffold / author / build / verify / bounded repair
  -> human-owned playtest feedback and revision (planned M7.6)
```

The official RitsuLib tutorials establish product semantics and documented Package
membership. The pinned RitsuLib source/compat profile supplies exact versioned API facts.
`games/sts2/` is authoritative; `plugins/open-mod/` and `skills/` are generated payloads.

Artifact ownership is strict:

- `DESIGN.md` owns player intent, accepted decisions, rationale, current/future scope,
  tuning hypotheses, identity anchors, and revision impact;
- `SPEC.md` owns only exact supported operations generated now;
- `PLAN.md` owns pipeline stage status;
- `MEMORY.md` owns resolved technical identities and build/repair facts, not creative intent.

Unresolved unsupported intent remains a blocking DESIGN gap. Unresolved cross-surface
conflicts also stop before SPEC. Deferred and out-of-scope items produce no SPEC stub,
source, resource, or implied implementation promise.

## Package Status

| Package | Status | Product result and retained evidence boundary |
| --- | --- | --- |
| M7.0 - behavioral evaluation baseline | Canceled | No standalone corpus or evaluator. The smallest behavioral cases travel with the Package that changes the behavior. |
| M7.1 - adaptive Interview and routing | Implemented | Fast/co-design/revision inference, direct resume, material-question filtering, constrained contradiction/unsupported handling, and decision-preserving deltas. Six semantic scenarios and deterministic contracts passed; independent forward-model and runtime checks remain unrun. |
| M7.2 - STS2-native design grammar | Implemented | Lazy Character Foundation grounding, checked five-Character starter inventory, exact native-shaped proposal, fact/convention/decision separation, and deliberate-departure consequences. Three scenarios and exact fact/contracts passed; independent forward-model and runtime checks remain unrun. |
| M7.3 - mechanic, content-set, and balance planning | Implemented | Lazy mechanic/content-set/balance references, compact planning capsule, directed interactions, formulas/economies, open hypotheses, and a Mod-forward working-value bias bounded by meaningful choices and real costs. Three scenarios and deterministic contracts passed; no human balance/playtest evidence exists. |
| M7.4 - scope and design-to-SPEC translation | Implemented | Adaptive `open-mod-design/v1` DESIGN, stable `D-###`/`OP-###` IDs, four scope dispositions, blocking gaps, and bidirectional supported-route validation. Three scenarios and deterministic trace contracts passed; independent forward-model and runtime checks remain unrun. |
| M7.5 - theme, narrative, presentation, and coherence | Implemented | Lazy proportional `A-###` anchors, six selected expression surfaces, fail-closed conflicts, deliberate tension, and revision-only `Q-###` impact queues. Three scenarios and deterministic validator contracts passed. Two focused read-only independent prompts covered conflict and revision; the Event prompt, full matrix, and human artifact review remain unrun. |
| M7.6 - playtest and tuning loop | Not started | Planned human-executable hypothesis-led playtest, observation capture, design-versus-implementation triage, bounded tuning delta, and targeted backtracking. It requires explicit selection before work starts. |

## M7.6 Planned Contract

M7.6 must keep observation human-owned. It may structure a playtest plan, record what the
human actually observed, distinguish design problems from implementation defects, and
produce a bounded DESIGN/SPEC delta. It must never fabricate playtest evidence, treat an
LLM judge as the sole pass/fail authority, or reopen unaffected decisions.

One focused human-led tuning exercise is sufficient if M7.6 is selected. Any generated
behavior change receives the nearest proportional host and literal Tier 1/Tier 2 status.
Prompt-only or future-vision wording changes do not require a game run.

## Verification Policy

M7 prompt and authoring tests evaluate semantics rather than preferred prose. They cover:

- question economy and preservation of settled user decisions;
- meaningful alternatives and concrete player-facing trade-offs;
- exact pinned facts versus observed conventions and creative decisions;
- supported current slice versus future vision and blocking gaps;
- DESIGN-to-SPEC traceability and fail-closed route resolution;
- cross-surface coherence, deliberate tension, and bounded propagation; and
- refusal to invent runtime, balance, presentation, or playtest evidence.

Documentation and prompt-only work uses contract, scenario, payload, and structural skill
checks. A change to generated runtime behavior or presentation uses the nearest maintained
real host. Fresh natural-language acceptance is reserved for an explicitly scheduled
full-pipeline gate or direct human-lead request.

Tier 1 still requires the exact load marker and no fresh error block. Tier 2 still requires
a structured post-state proof plus `selftest done`. Build success, static trace validation,
forward-model prose, and screenshots do not substitute for those checks.

## Closed Milestones

The active plan does not duplicate closed implementation matrices:

- migration: `documents/history/RITSULIB_MIGRATION_RESULTS.md`;
- through-M6 planning snapshot: `documents/history/IMPLEMENTATION_PLAN_THROUGH_M6.md`;
- M6.5 focused and fresh acceptance results: `documents/history/M65_*`;
- M6.6 Package results: `documents/history/M66_*` and the retained official RitsuLib
  `0.5.4` Card Piles proof;
- M6.7 consolidated result: `documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`; and
- post-acceptance generation repair:
  `documents/history/M67_POST_ACCEPTANCE_GENERATION_QUALITY_REPAIR.md`.

M6.7 ended at M6.7.5. M6.7.6 was canceled, the milestone batching exception is closed,
and the separate current-catalog headed no-op plus every unselected route remain literally
unrun. Do not recreate the acceptance Mod, expand the closed provider/hook matrix, or infer
individual-route acceptance from the representative Mod accepted as a whole.

## Future Outlook

Multiplayer vanilla overrides remain a separate future track. Promotion requires identical
peer manifests and real-host evidence for deterministic state/RNG, choices, save/load,
remote presentation, synchronization, timeout/disconnect cleanup, and host authority.
Singleplayer evidence must never be relabeled as multiplayer support.

Optional Mod settings and additional native-design grammar slices remain unscheduled. Add
them only for a selected product need with bounded source research and behavioral cases;
do not add configuration or a full design process to every simple Mod.
