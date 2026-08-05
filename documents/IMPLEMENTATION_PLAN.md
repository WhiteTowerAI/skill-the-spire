# Implementation plan: M8 end-to-end product integrity

## Status

Version `0.6.0` remains the unreleased RitsuLib-only development baseline for STS2 stable
`0.107.1` and RitsuLib `0.5.4`. The BaseLib migration and M6.5-M6.7 implementation tracks
are closed.

M7 Design Intelligence and User Experience is also closed by explicit human-lead decision
on 2026-08-05. M7.1 through M7.5 are implemented in source and synchronized into the
plugin and portable payloads. M7.6 closed through the external human-led Watcher
whole-skill evaluation recorded in
`documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`; no M7.6 source Package or
successful tuning result is inferred.

M8 End-to-End Product Integrity is the active planned milestone. It turns the Watcher
evaluation's cross-stage findings into changes across modmaker routing, capability
grounding, artifact traceability, repair, content-set scope, cross-platform tooling, and
final installed acceptance. No M8 Package has started. M8.1 is the next selectable Package.
M8.4 Independent Verification and Evidence-Derived Reporting was removed by the human lead
on 2026-08-05; M8.5 and M8.6 retain their numbers. Planning this milestone does not itself
authorize M8.1 implementation, a new acceptance Mod, payload publication, or a GitHub
release.

## New-Session Start Protocol

A new coding session must not re-plan M8 from scratch. After reading `AGENTS.md` and the
active documents, it must use this sequence:

1. Read the Package Status table below and the complete execution contract for the first
   Package marked **Next selectable** or **In progress**.
2. If the human lead says only "start M8" or "continue M8", select or resume that Package.
   Do not ask the human to choose among later Packages and do not begin the final acceptance.
3. Read the listed authoritative source files before editing. Inspect current dirty changes
   and preserve unrelated work, especially `usertest_M76/`.
4. Implement only that Package's work order. A later Package may be read for interface
   compatibility but may not be implemented early.
5. Run only the Package's listed proportional checks unless the human lead narrows or
   reserves verification. Never turn an intermediate Package into a fresh whole-skill Mod.
6. Write the named history result and update this status table. Review `AGENTS.md`,
   `README.md`, `documents/PROJECT.md`, `documents/BASELINE_RESEARCH.md`,
   `documents/history/README.md`, `games/sts2/tests/README.md`, and
   `games/sts2/tests/content-capability-graph.md`; edit only the files whose owned facts
   changed, and list checked-but-unchanged current documents in the result record.
7. Source changes under `games/sts2/` require regenerated and validated plugin and portable
   payloads. Do not hand-edit payloads, commit, merge, publish, or start the next Package
   without the corresponding instruction.

If the named Package's prerequisite is not closed, stop and report that exact dependency.
If current source contradicts an execution contract, preserve the product invariant, record
the smallest plan correction in this file, and explain it rather than silently improvising.

## Product Problem

The current workflow can produce a Mod for which every local stage has a plausible pass
while the final player-facing result has drifted from the original intent:

```text
locally implementable + locally verified + separately accepted fallbacks
    != end-to-end faithful + evidence-bound + reproducible
```

M8 must preserve one literal product contract from request through observed result. It
must distinguish what is being delivered, resolve exact authoring routes before generation,
backtrack on semantic change, keep runtime behavior and every required player-facing rule
surface together, and reproduce the installed workflow without self-modification or leaked
child processes.

This cannot be implemented as a growing prompt checklist of named mechanics. Existing
DESIGN decisions, SPEC operations, and maintained recipe/reference routes must carry the
smallest machine-checkable semantic facts needed to bind behavior, lifecycle, rules-text
tokens, keyword/DynamicVar and Hover Tip obligations, localization, preview, and
presentation consumers. Do not create a parallel contract or capability truth source when
an existing artifact can own the fact. Behavior and localized explanatory surfaces may be
authored separately, but their shared values, keywords, and invariants must agree.

M8 improves the whole skill. It does not widen the RitsuLib runtime capability graph merely
because the Watcher experiment wanted an unavailable or ungrounded behavior. M8.2 may
promote a reusable generic capability family only after maintainer-owned pinned research,
an exact public/fixed route, semantic-conformance tests, documentation, and payload
validation. If that route cannot be grounded, the literal request remains blocked rather
than receiving an approximate substitute.

## Dependency And Support Boundary

The dependency and Supported Boundary in `AGENTS.md` apply unchanged. The active runtime
inventory remains `games/sts2/tests/content-capability-graph.md`; M8 records implementation
and verification gaps without silently changing Package support. Missing exact routes block
generation, and no M8 work authorizes BaseLib or prompt-derived Harmony, reflection,
Publicizer, or IL.

## Target Flow

```text
plain-language request
  -> literal completion claim and required player experiences
  -> exact semantic capability and presentation preflight
  -> adaptive DESIGN and current/future scope
  -> validated SPEC operation allowlist
  -> scaffold / author / build
  -> repair classification
       -> equivalent technical repair continues locally
       -> player-visible semantic change backtracks to DESIGN/scope/SPEC
  -> existing proportional operation-linked verification
  -> human observation when an experience claim is in scope
  -> literal final report
```

Existing artifact ownership remains:

- `DESIGN.md` owns player intent, accepted decisions, rationale, current/future scope,
  tuning hypotheses, identity anchors, and revision impact;
- `SPEC.md` owns only exact supported operations generated now;
- `PLAN.md` owns literal pipeline stage and backtracking status; and
- project `MEMORY.md` owns resolved technical identities and build/repair facts.

## Package Plan

There is no standalone M8.0 evaluator. The Watcher record is the baseline evidence, and
the smallest behavioral cases travel with the Package that changes a decision. It is not
the final M8 acceptance project.

| Package | Status | Prerequisite | Plain-language result |
| --- | --- | --- | --- |
| M8.1 - literal deliverable contract | **Next selectable** | M7 closed | Before making anything, state the exact completion claim and the player experiences required now; prototype/slice/run-capable labels are optional descriptions, not a closed taxonomy. |
| M8.2 - exact semantic capability conformance and preflight | Waiting | M8.1 closed | Complex mechanics come from one maintained exact implementation; unsupported or broken routes block instead of becoming an approximation. |
| M8.3 - semantic continuity and backtracking | Waiting | M8.2 closed | If implementation or repair changes what the player gets, return to the owning design/spec decision instead of patching forward. |
| M8.5 - cross-platform reproducible installed workflow | Waiting; may be selected independently after M8.1 | M8.1 closed | The committed installed skill works reproducibly on Windows and macOS and cleans up only the process tree it started. Default order remains M8.2 then M8.3 unless the human lead explicitly selects M8.5 earlier. |
| M8.6 - clean installed whole-skill acceptance | Waiting | M8.1-M8.3 and M8.5 closed, plus human-selected request/host | Run one fresh broad request from an untouched installed payload and let the result prove the whole workflow. |

## Package Execution Contracts

### M8.1 - Literal Deliverable Contract

**Authoritative source scope:**

- `games/sts2/skills/modmaker/SKILL.md`, `route.md`, `interview.md`, `design.md`,
  `semantic-contract.md`, and `spec.md`;
- `games/sts2/tools/design_trace.py`;
- new behavioral cases in `games/sts2/tests/m81-deliverable-contract-scenarios.md`; and
- new focused contracts in
  `games/sts2/tools/tests/test_m81_deliverable_contract.py`.

**Work order:**

1. Extend the existing `open-mod-design/v1` scope block rather than adding a second DESIGN
   contract. Record one concise `completion_claim` in the user's terms and a bounded list of
   `required_player_experiences` tied to current `D-###` decisions.
2. Treat `mechanic proof`, `playable slice`, and `run-capable content set` as useful examples,
   not an enum. A complete single Card, Relic, Event, visual override, revision, or other
   supported product may keep its literal shape without being relabeled as a prototype.
3. Record only identity-critical or explicitly non-default player-facing requirements in
   DESIGN. M8.2 capability routes supply their normal lifecycle/text/tip/preview/
   presentation obligations; do not make every fast request enumerate not-applicable
   surfaces or ask the user to classify internal metadata.
4. Update routing and Interview so an exact narrow request retains the zero-question fast
   path. Ask only when two plausible completion claims would produce materially different
   current scope; the number of questions remains governed by the existing material-question
   filter rather than a new hard limit.
5. Carry the completion claim and current required experiences through the existing
   `open-mod-spec-trace/v1` operations. `design_trace.py` must fail before scaffold when a
   current required experience has no owning operation, a SPEC operation has no current
   design owner, or the reported completion claim exceeds the accepted current slice.
6. Keep future vision in DESIGN only. A placeholder, deferred item, or technical fallback
   cannot satisfy a required literal invariant unless the user explicitly approved that
   player-visible result.
7. Add semantic scenarios for a complete single-element Mod, an ambiguous "working
   Character", a requested run-capable set whose current contents are only a vertical
   slice, and a focused revision that must preserve the existing completion claim.

**Result record:** `documents/history/M81_LITERAL_DELIVERABLE_RESULTS.md`.

### M8.2 - Exact Semantic Capability Conformance And Preflight

**Prerequisite:** M8.1 is closed and its completion claim/required experiences are available
to preflight.

**Authoritative source scope:**

- `games/sts2/skills/modmaker/semantic-contract.md`, `spec.md`, and `author.md`;
- `games/sts2/skills/sts2-api/SKILL.md`, `grounding.md`, relevant recipes/references, and
  especially `reference/scry-helper.md`, `reference/mechanics.md`,
  `reference/content-text-effects.md`, and `recipes/card.md`;
- new validator `games/sts2/tools/semantic_capabilities.py`;
- new scenarios `games/sts2/tests/m82-semantic-capability-scenarios.md`; and
- new tests `games/sts2/tools/tests/test_m82_semantic_capabilities.py`.

**Work order:**

1. First implement the common kernel for the four M8.2 audit families: add one small marked
   capability-contract block to each existing authoritative recipe/reference route selected
   by those families. The block records version, exact invariant, owner/consumer boundary,
   lifecycle, shared semantic facts, required player-facing surfaces, and the smallest
   known limitation. Other existing routes remain unchanged until a later selected need;
   do not create a manually maintained central catalog beside the routes and capability graph.
2. Make `semantic_capabilities.py` follow an audited operation's existing `supported_route`,
   read that route's marked contract, and reject an unknown/unimplemented route,
   incompatible owner/lifecycle, or missing required surface before authoring.
3. Then audit four reusable families against official product semantics, pinned RitsuLib `0.5.4`
   source, the `0.107.1` game substrate/catalog, and current generated recipes: Card
   lifecycle/behavior metadata and its explanatory text; deck inspection, selection, and
   movement mechanics such as Scry; mechanic Hover Tips; and incoming/outgoing numeric
   modifiers such as damage multipliers.
4. For each family, keep Package support and current generator implementation separate. A
   family closes with either a maintained exact route or the smallest explicit blocking
   limitation; it does not need speculative expansion beyond the observed generic gap.
5. Change authoring so normal consumer Mods select the maintained route rather than receive
   newly improvised mechanic code. Share structured facts such as values, keywords,
   direction, lifecycle, and selection/movement semantics between behavior and explanatory
   surfaces. Author localized text separately, then validate that it covers those facts.
6. If an existing generated route fails the audit, block that route until the shared source
   is repaired or the capability graph records the narrow limitation. If a needed generic
   route is absent, use maintainer-owned pinned research and the normal promotion process;
   never research or patch it ad hoc in a consumer project.
7. Add conformance cases for exact state transition, selection and cancellation, ordering,
   destination/history/hooks, degenerate states, mouse/controller input where applicable,
   plus matching rules text, keyword/DynamicVar, Hover Tip, localization, and preview.
8. Any repair that changes generated runtime behavior or presentation receives the nearest
   maintained real-host proof. Static/catalog proof alone must be reported as such.

**Result record:** `documents/history/M82_SEMANTIC_CAPABILITY_RESULTS.md`.

### M8.3 - Semantic Continuity And Backtracking

**Prerequisite:** M8.2 is closed, so current operations have stable maintained route
contracts and surface obligations.

**Authoritative source scope:**

- `games/sts2/skills/modmaker/SKILL.md`, `route.md`, `design.md`, `spec.md`, `repair.md`,
  and `semantic-contract.md`;
- `games/sts2/tools/design_trace.py` and `coherence_trace.py` where their existing ownership
  applies;
- new scenarios `games/sts2/tests/m83-semantic-continuity-scenarios.md`; and
- new tests `games/sts2/tools/tests/test_m83_semantic_continuity.py`.

**Work order:**

1. Route every discovery or repair through four outcomes with explicit artifact ownership:
   implementation-equivalent repair updates source/MEMORY and reruns affected checks;
   contract-fulfillment repair keeps DESIGN but corrects affected SPEC/source/localization
   and reruns its surface checks; accepted product-semantic change updates DESIGN before
   SPEC; missing capability routes back to M8.2 and blocks.
2. A product-semantic change reopens only affected `D-###` decisions, records
   keep/change/check/re-verify impact, then regenerates affected `OP-###` operations and
   reruns both traces before authoring resumes. A contract-fulfillment repair never changes
   the accepted completion claim merely to make current output pass.
3. A missing maintained capability routes back to M8.2's maintainer queue and blocks the
   consumer project. It must not become an accepted local fallback merely because it builds.
4. Make `PLAN.md` record the current stage, `backtrack_to`, affected design/operation IDs,
   reason, and checks invalidated by the change. Resume at the earliest invalidated stage,
   not at the last command that failed.
5. Preserve unrelated settled decisions, rejected alternatives, future scope, and evidence.
   Superseded hypotheses leave the current path and remain only in bounded history.
6. Cover an equivalent compile repair, missing Card text, missing Hover Tip, a mechanic
   substitution, and a revision affecting one of several identity anchors.

**Result record:** `documents/history/M83_SEMANTIC_CONTINUITY_RESULTS.md`.

### M8.5 - Cross-Platform Reproducible Installed Workflow

**Prerequisite:** M8.1 is closed. M8.5 is operationally independent of M8.2-M8.3 and may be
selected early by explicit human-lead instruction; otherwise follow the default Package
order and begin it after M8.3.

**Authoritative source scope:**

- `games/sts2/tools/launch.py`, `launch.ps1`, `build.py`, `grep_log.py`, and
  `ritsu_profile.py` as required by discovered platform drift;
- `games/sts2/skills/modmaker/build.md`, `verify.md`, and `repair.md`;
- `games/sts2/tools/tests/test_verification_tools.py` plus new
  `games/sts2/tools/tests/test_m85_platform_workflow.py`; and
- installed plugin/portable payload validation scripts already owned by `publish.sh` and
  `scripts/publish/`.

**Work order:**

1. Make `launch.py` the canonical cross-platform process owner. `launch.ps1` must delegate
   to it or have explicit parity coverage; it cannot retain a divergent cleanup contract.
2. Refuse to adopt or terminate a game process that existed before the launch. Record the
   created root identity and owned descendants. On macOS, first research and prove a route
   that preserves normal bundle/Steam/Godot launch semantics while retaining the actual game
   PID or process-group ownership. The current short-lived `open` helper is not sufficient;
   direct bundle-executable launch is only one candidate until verified.
3. Put cleanup in an unconditional finalization path for success, failure, timeout, and
   interruption. Prefer graceful termination, then use a bounded forced cleanup only for
   the recorded owned tree. Verify that no owned descendant remains before reporting done.
4. Make discovery, deployment, log location, compat identity, and argument passing explicit
   for Windows and macOS. Consumer-session path edits or installed-cache source edits must
   not count as success.
5. Record the installed source/payload identity before a consumer build and verify it did
   not change. Confirm generated output comes from the committed synchronized payload.
6. Add mocked process-tree tests for pre-existing processes, normal exit, timeout, child
   survival, interruption, and scoped forced cleanup. Add PID-reuse protection only if the
   selected ownership strategy can actually encounter it. Then obtain literal repository-
   owned installed-workflow evidence on both Windows and macOS.

**Result record:** `documents/history/M85_CROSS_PLATFORM_WORKFLOW_RESULTS.md`.

### M8.6 - Clean Installed Whole-Skill Acceptance

**Prerequisites:** M8.1-M8.3 and M8.5 are closed; both committed payloads are synchronized;
the human lead explicitly selects the broad request and host; and no older acceptance
project is reused.

**Authoritative scope:** the clean installed plugin or portable payload, a fresh external
workspace, the generated DESIGN/SPEC/PLAN/MEMORY artifacts, and repository-owned tools.
M8.6 does not start by editing source.

**Work order:**

1. Record installed payload version/hash, target host, clean workspace, requested product
   shape, and the human-selected experience question before generation.
2. Run the ordinary installed skill from request through deliverable contract, capability
   preflight, DESIGN/SPEC confirmation, author/build, proportional verification, and final
   literal report. Do not patch the installed skill or copied payload.
3. Require every selected mechanic's behavior, lifecycle, rules text, keyword/Hover Tip,
   localization, preview, and presentation obligations to have literal evidence or remain
   visibly failed/unrun.
4. Use normal human play for comprehension, decision quality, enjoyment, or tuning claims.
   Record the human's exact observation separately from technical Tier evidence.
5. If the run exposes a product-integrity defect, stop the acceptance, route it back to the
   owning M8 Package, repair source there, republish, and restart with a fresh workspace.
   Do not repair the acceptance Mod into a pass.
6. Finish by proving launcher-owned process cleanup. Report each technical check from its
   actual tool/log result and each experience observation from the human who supplied it;
   failed and unrun checks remain explicit rather than being absorbed into an aggregate pass.

**Result record:** `documents/history/M86_CLEAN_WHOLE_SKILL_ACCEPTANCE_RESULTS.md`.

Each Package requires the smallest semantic cases that prove its own decisions. M8.6 is the
only planned fresh full-pipeline gate. Do not recreate or repair Watcher as that gate, and
do not start it before M8.1-M8.3 and M8.5 are closed and the human lead selects the request
and host.

## Verification Policy

The literal Tier definitions and host ownership in `AGENTS.md` and
`games/sts2/tests/README.md` remain authoritative. M8 contract tests own completion-claim
traceability, route conformance, surface parity, and backtracking; changed runtime or
presentation still uses the nearest real host; platform claims require evidence from the
claimed host; and human observation alone owns experience claims. M8.6 is the only fresh
natural-language acceptance gate and is not authorized to run yet.

## Closed Milestones

Closed migration through M7 results are indexed by `documents/history/README.md`; they are
evidence, not active instruction. Historical records retain the status and exceptions true
at their own close.

## Future Outlook

Multiplayer vanilla overrides, optional Mod settings, and unrelated runtime operation
families remain outside M8 unless a separately selected product need promotes them. M8.2
may promote the reusable generic capability gaps selected by this plan, but only through
the normal grounded support process; it does not authorize arbitrary runtime expansion.
