# M8.3 Semantic Continuity And Backtracking Result

Date: 2026-08-11

Status: closed by explicit human-lead decision on 2026-08-11. Implementation is complete in
source and both committed payloads. This record does not select M8.5 or authorize M8.6.

## Result

M8.3 closes the workflow gap between finding a difference and attempting a repair. PLAN now
carries one optional `open-mod-repair-routing/v1` active decision. `repair_trace.py` validates
that decision against current DESIGN/SPEC/deliverable/settlement state and blocks Finalize while
repair remains active. A PLAN without the block resumes unchanged.

Every discovered difference is classified before a fix:

- `implementation-equivalent` is technical history owned by `MEMORY.md`;
- `contract-fulfillment` preserves accepted meaning and corrects `SPEC.md` or its output;
- `accepted-semantic-change` stops for a DESIGN-first revision and explicit acceptance; and
- `missing-capability` blocks on the shared recipe/reference without a consumer-local substitute.

Only the first two enter the bounded three-attempt loop. Affected settlements are cleared, the
earliest invalid stage reopens, and an affected operation is inspected through its existing
surface envelope, driver, proof matrix, and cited route across behavior, lifecycle/reset, text,
tips, localization, preview, presentation, and proof. `INV-5` now fires through Verify, Repair,
and Finalize; no `INV-10` was added.

## Work Order

1. **State and ownership:** added the PLAN template block and `repair_trace.py`; current ids,
   owner/status combinations, settlement invalidation, earliest reopening, Finalize blocking,
   and legacy no-block resume are checked. Completed history remains in MEMORY.
2. **Classification at discovery:** Author, Build, Tier 1/Tier 2/headed Verify, Repair, and
   Finalize route through classification before a change. Harness setup remains distinct from
   Mod behavior. Only the two technical routes consume attempts.
3. **Artifact-owned transitions:** technical minimum rerun, SPEC/output fulfillment,
   DESIGN-first accepted revision, and upstream capability block are explicit. State check
   resumes active repair before unchecked PLAN boxes.
4. **Complete-operation impact:** Repair and semantic-contract guidance read each existing
   envelope/driver/proof/route as one operation and preserve unaffected operations and
   `PRESERVE` entries. All ten co-located surfaces already contained a driver and proof matrix;
   none required a batch edit.
5. **Scenarios/checks/synchronization:** all fifteen cases, negative/mutation checks, full
   regression, payload-shaped execution, two-pass payload generation, skill validation,
   compilation, parity, and diff hygiene completed. Both payloads were generated from source.

## Scenario Matrix

`games/sts2/tests/m83-semantic-continuity-scenarios.md` contains all fifteen contracted cases:
technical path correction; harness non-reach; technical-label rejection; Exhaust lifecycle/text;
owner guard neutrality; stale text/tip/localization/preview/presentation; omitted SPEC field;
third-turn versus three-Attacks; replacement/composition and target-count changes; unaccepted art
fallback; cumulative fallback shape; absent authoring/API route; claimed-but-broken shared route;
user playtest feedback; and legacy resume. Each names classification, owner, id treatment,
reopened stages, question rule, and stop/resume condition.

## Checks Run

- M8.3 focused validator/scenario/prose suite: `19/19` passed; with payload-layout coverage:
  `22/22` passed.
- Related M7.4/M7.5/M8.1/M8.2, invariant, semantic-contract, envelope, surface, payload-layout,
  and M8.3 suite: `153/153` passed.
- Full `games/sts2/tools/tests` regression: `384/384` passed.
- Mutation probes passed for owner, classification/status, stale settlement, earliest stage,
  DESIGN-first, and upstream-block enforcement.
- Python compilation passed for source tools, publish scripts, and both payload trees.
- The source, plugin, and portable `modmaker`/`sts2-api` roots all passed skill validation:
  six roots total.
- `test_payload_tool_layout.py` ran `repair_trace.py` from a payload-shaped scratch tree with
  adjacent validators and an active repair.
- Plugin and portable payloads were each generated twice. Both passes produced `188` shared
  effective files per tree (portable-only `GENERATED.md` excluded), zero effective differences,
  and aggregate SHA-256
  `4063F38AD5C3B3A20E146A6CD5829B84C6B90FB1BECCBABB9A4538F2E35600F5`.
- `git diff --check` passed. Scoped status/diff review preserved unrelated `CLAUDE.md`.

## Evidence Boundaries And Exceptions

M8.3 changes workflow instructions and deterministic project-state validation. No generated Mod,
payload installation, game launch, Tier 1, Tier 2, headed review, forward-model run, human
semantic acceptance, commit, push, merge, publication, or release occurred. The tests do not prove
runtime behavior or that every surface is good in-game. The two M8.2 real-host proofs remain
deferred to M8.6. M8.5 process ownership and M8.6 final acceptance remain untouched.

No runtime capability, hook, helper, recipe, route metadata, support row, Tier definition,
multiplayer boundary, BaseLib/Harmony/reflection/Publicizer/IL path, Watcher project, or installed
payload was added or changed. `sts2-api/errors.md` was unchanged because no new runtime signature
was proved.

## Files And Documents

Authoritative implementation changed under `games/sts2/skills/modmaker/` in `SKILL.md`,
`invariants.md`, `route.md`, `design.md`, `spec.md`, `semantic-contract.md`, `author.md`, `build.md`,
`verify.md`, and `repair.md`; added `games/sts2/tools/repair_trace.py`, the M8.3 scenario file, and
its focused tests; and updated M8.1 settlement plus payload-layout tests where their owned
contracts changed. Generated copies changed under `plugins/open-mod/skills/` and `skills/`.

Current documents changed because their status or verification facts changed: `AGENTS.md`,
`README.md`, `documents/IMPLEMENTATION_PLAN.md`, `documents/PROJECT.md`,
`documents/BASELINE_RESEARCH.md`, `documents/history/README.md`, and
`games/sts2/tests/README.md`. At closure, the status-only M8 paragraph in
`games/sts2/tests/content-capability-graph.md` was also synchronized; no capability row changed.

During implementation, `games/sts2/tests/content-capability-graph.md` was reviewed and left
unchanged because M8.3 changed no runtime support fact. The later closure-only status edit above
does not change that evidence boundary.
