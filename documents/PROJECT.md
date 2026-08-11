# open-mod project

## Product

open-mod is a free, open-source Codex plugin that turns a non-programmer's description into
a working game Mod. Slay the Spire 2 is the first supported game. The strategy is one game
deep, then a reusable platform once multiple independent consumers justify shared
abstractions.

The product combines design collaboration with a grounded implementation pipeline. It asks
only material questions, records intent separately from exact generated operations, authors
against pinned public/fixed routes, builds the Mod, and reports verification literally.

## Release State

`0.6.0` is an unreleased RitsuLib-only development baseline for STS2 stable `0.107.1` and
RitsuLib `0.5.4`. BaseLib has been removed from generated projects. M6.5, M6.6, M6.7, and
M7 are closed; their detailed results and exceptions live under `documents/history/`.

M7.0 was canceled as a standalone evaluation Package. M7.1 through M7.5 are implemented
and synchronized into both committed payloads:

- M7.1 infers fast, co-design, or revision and preserves direct resume;
- M7.2 grounds Character Foundation recommendations in the pinned native starter inventory;
- M7.3 plans mechanics, content sets, formulas, economies, and honest tuning hypotheses;
- M7.4 writes adaptive DESIGN before a validated current-slice SPEC; and
- M7.5 checks selected identity/presentation surfaces and propagates revisions narrowly.

M7.6 closed through a human-led external whole-skill evaluation rather than a new source
Package. The Watcher evaluation built, loaded, and exercised a bounded state subset on
macOS; the human lead reported that it was playable but not very good. That is not a
successful tuning-loop, complete Character, or broad route-acceptance claim. The exact
result is `documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`.

M8 End-to-End Product Integrity is the active milestone. It addresses literal
deliverable scope, complete player-facing operation semantics, maintained exact capability
preflight, semantic backtracking, and cross-platform installed reproducibility with owned-
process cleanup. One final clean installed whole-skill acceptance is scheduled only after
the preceding M8 Packages close. No acceptance run, payload publication, or GitHub release is
currently authorized.

M8.1 Literal Deliverable Contract is closed by explicit human-lead decision on 2026-08-10. Every
`DESIGN.md` now carries one literal deliverable claim — what the user has when this is done,
the `E-###` player experiences required for that claim to be honest, how each will be settled,
and what the claim does not include — and Finalize generates its report from a `PLAN.md`
settlement ledger instead of free prose. `deliverable_trace.py` checks the claim before SPEC and
the ledger at finalize, where no other validator runs. A requirement is not an experience: a
generated operation can pass while the thing the player was promised is false. The result is
`documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md`.

M8.0 Skill Structure Restructuring is closed by explicit human-lead decision on 2026-08-10. The
shipped pack now reads one file per element instead of three per stage, projects its art contract
from code into a catalog, separates diagnostic signatures from preventive constraints, states what
is supported rather than which Package promoted it, and states each cross-stage invariant once.
Both committed payloads are synchronized. Nine of the ten co-located surfaces have never been
piloted; the durable result is `documents/history/M80_SKILL_STRUCTURE_RESULTS.md`. Three of the
thirteen contradictions it found were deferred to M8.2 and are resolved there.

M8.2 Exact Semantic Capability Conformance and Preflight is closed by explicit human-lead
decision on 2026-08-10. A mechanic that changes a value or decision the engine is computing is now
a declaration rather than prose: a capability id, the subject guard that decides direction, the
condition, the value with the name that puts it in rules text, and the neutral result outside the
guard. Preflight resolves each cited route and its anchor, pairs the declared capability against
what that route provides, and rejects a hook the declaring surface cannot receive — which on this
engine is decided by the dispatching iterator, so an override on the wrong surface compiles and
never fires. The SPEC envelope is normalized to `sts2-content-semantic/v2` with a migration path,
which is what made a generated project's SPEC checkable against its surface at all, and closed the
three inherited M8.0 mismatches. `INV-9` states where a claimed-but-broken route blocks. **The two
real-host proofs it owed were deferred to M8.6 and did not run**, so every hook route is
implemented and unobserved in a running game. Four defects were found while spending its own
catalog, three of them in its own earlier steps. The result is
`documents/history/M82_CAPABILITY_CONFORMANCE_RESULTS.md`.

M8.3 Semantic Continuity and Backtracking closed by explicit human-lead decision on 2026-08-11.
It adds one resumable active-repair decision to PLAN, validates four artifact-owned routes with
`repair_trace.py`, and treats each affected operation's behavior/lifecycle/text/tips/localization/
preview/presentation/proof as one impact view. Its `384`-test regression is static/workflow
evidence; no generated Mod or game run occurred.
The result is `documents/history/M83_SEMANTIC_CONTINUITY_RESULTS.md`. M8.4 was removed by the human
lead; M8.5 and M8.6 retain their numbers and are not started.

Generated-Mod localization is bilingual by contract in `sts2-content-semantic/v2`. A Mod with no
localization tables remains language-neutral; once any table exists, English (`eng`) and
Simplified Chinese (`zhs`) are both required with matching table names, keys, and SmartFormat
tokens and with nonempty values. DESIGN and SPEC record the exact text, `INV-10` preserves the
obligation through the workflow, and future Tier 2 checks switch through both languages before
restoring the original language. Translation quality remains a human judgment. This source and
payload implementation was not tested, built, launched, or otherwise verified by human-lead
instruction, so it carries no runtime or game proof.

A pre-M8.5 maintenance debug removes generated-project framework `PackageReference` entries.
Scaffold keeps the RitsuLib `0.5.4` authoring baseline, pins the selected local Compat DLL version
and hash, resolves game/framework assemblies locally, and copies the bundled Godot.NET SDK import
set. Its player manifest remains `STS2-RitsuLib >= 0.5.4` even when the local compiler uses a
newer compatible runtime. Its one focused scaffold contract test passed. No Mod compile,
restore/offline, cross-platform, Tier 1, Tier 2, or game run was performed, and M8.5/M8.6
remain unselected.

## User Experience

```text
plain-language idea
  -> resume or infer fast / co-design / revision
  -> ask only decisions that materially change the Mod
  -> write DESIGN.md for intent, scope, coherence, and revision impact
  -> write SPEC.md for exact supported operations generated now
  -> scaffold, author, build, package, and deploy
  -> run proportional load/behavior verification when required
  -> report passes, failures, and unrun checks literally
```

M8 strengthens this flow. The literal deliverable contract, exact capability preflight, and
semantic-impact backtracking are implemented: DESIGN carries the claim, SPEC is checked against
its surface and cited routes, and active repair returns to MEMORY, SPEC, DESIGN, or a shared route
according to what changed. Durable cross-platform reproduction with no launcher-owned process left
behind remains planned. Existing literal reporting and verification ownership remain in force;
M8 adds no separate evidence-reporting subsystem.

A complete narrow request retains a zero-question path. Ambiguous work receives materially
different player-facing options with trade-offs, not an exhaustive questionnaire. Revision
updates only affected decisions and artifacts instead of restarting the project.

Character/content-set requests lazily load one pinned Foundation reference before creative
deck questions. The skill proposes an exact native-shaped starter deck and explains how it
teaches the intended mechanic. Deliberate implementable departures remain allowed after
their onboarding, compatibility, and balance consequences are explicit.

## Artifact Boundary

DESIGN and SPEC have different jobs:

```text
DESIGN D-### decisions
  -> current MUST / PLACEHOLDER
  -> future DEFER / OUT-OF-SCOPE
  -> blocking gaps
  -> A-### identity anchors and selected expression checks
  -> revision-only Q-### impact queue

current DESIGN decisions only
  -> SPEC OP-### operation allowlist
  -> exact semantic targets and existing supported routes
  -> generated source/resources
```

`design_trace.py` rejects missing/extra operations, one-way links, future leakage,
unresolved gaps, invalid dispositions, invented route forms, absent route files, unresolvable
route anchors, and a capability id no route declares. `coherence_trace.py` rejects invalid
references, unresolved pre-SPEC conflicts, and unbounded revision queues. `deliverable_trace.py`
rejects a malformed claim before SPEC and an outcome that outruns its evidence at finalize.
`spec_envelope_trace.py` rejects a SPEC that drops a shared section, invents a top-level key, or
declares a hook its own surface cannot receive. No validator can prove subjective quality,
balance, enjoyment, or runtime behavior.

## Architecture

1. `games/sts2/skills/modmaker/` owns routing, Interview, DESIGN, SPEC, scaffold, author,
   build, verify, and bounded repair.
2. `games/sts2/skills/sts2-api/` owns lazy design references, exact recipes, pinned API
   facts, error guidance, and current runtime routes.
3. `games/sts2/tools/` owns cross-platform build, launch, log, art, catalog, and artifact
   validators.
4. `games/sts2/tests/` owns the active capability graph, verification ownership, semantic
   scenarios, and deterministic regressions.
5. `plugins/open-mod/` and `skills/` are generated Codex-plugin and portable payloads.

M8 work crosses these ownership boundaries rather than creating a separate runtime
framework, and the delivered Packages followed that split: `modmaker` owns the deliverable claim
and the SPEC-side capability declaration, `sts2-api` owns the maintained exact route and the
pinned hook catalog it projects, tools own the validators, and tests own the capability
conformance cases. M8.3 follows the same division: `modmaker` owns routing, `repair_trace.py` owns
deterministic PLAN validation, and tests own the fifteen cases. Remaining Packages put reproducible
platform/process cleanup in tools and final whole-skill coverage in tests.

Edit source under `games/sts2/`; regenerate both payloads through `publish.sh`. Generated
Mods use the `0.5.4` RitsuLib API baseline, then compile against the exact validated local
RitsuLib Compat DLL selected at scaffold time. The project carries no framework
`PackageReference`: the skill supplies the Godot.NET SDK import files and resolves STS2,
Harmony, GodotSharp, System.IO.Hashing, and RitsuLib from the game/runtime installation.
Runtime discovery prefers the game-local or official Workshop RitsuLib runtime, and an upgrade
after scaffold requires an explicit profile migration. Generated Mods never copy the maintainer
checkout or depend on BaseLib.

## Design Intelligence Boundary

M7 separates four knowledge classes:

- pinned facts from the `0.107.1` catalog/game substrate;
- observed native conventions that support a recommendation but can be deliberately broken;
- creative decisions owned by the user; and
- open hypotheses requiring measurement or human playtest evidence.

Balance uses a human-lead-selected Mod-forward posture: prefer a clearly rewarding,
modestly stronger working value over a no-pick result, while reducing values that erase
choices, setup, costs, ordinary opposition, or create deterministic/self-funding/unbounded
loops. This is a product preference, not a pinned STS2 fact or fixed percentage.

Coherence review is proportional. It checks only selected mechanics, naming, localization,
visuals, Event text, and Character identity against accepted anchors. Placeholder art is a
fallback, not an invented theme. An accepted ironic contrast is recorded as deliberate
tension instead of being normalized automatically.

## Verification Philosophy

Support and verification are separate. Official tutorial Package semantics plus the needed
public API in the pinned profile define support. Missing recipes, validators, builds,
Tier 1/Tier 2 runs, or headed review mean implementation or verification is missing; they
do not narrow a documented public Package automatically.

Use deterministic local assertions for calculations and state rules, then the nearest real
host for changed runtime behavior or presentation. Fresh end-to-end acceptance is reserved
for an explicit milestone gate or human-lead request. Historical evidence is immutable and
does not become a reusable test fixture.

M8 will make that ownership operation-complete: state behavior, lifecycle, rules text,
DynamicVars/keywords, Hover Tips, localization, preview, and real presentation must agree.
Those obligations will use machine-checkable metadata on the existing authoritative route,
not a mechanic-name checklist or second capability catalog. Maintained complex helpers must
prove their selection, ordering, movement, hooks, degenerate states, and input modes; a
claimed route that fails conformance blocks until repaired or narrowed. A claimed platform
run also ends only after the tool confirms that its owned process tree is gone.

M7.1-M7.5 are prompt/design workflow changes. Their deterministic scenarios and validators
prove shipped contracts only. Two focused read-only forward-model prompts exercised M7.5
conflict and revision behavior. The later external Watcher evaluation supplies bounded
build/Tier/human evidence under its own result record; it does not retroactively prove the
full M7 forward-model matrix, all generated operations, headed design quality, visual
quality, or successful playtest tuning.

Current commands and exact verification ownership live in `games/sts2/tests/README.md`.

## Runtime Boundary

The exact supported and unsupported inventory lives in
`games/sts2/tests/content-capability-graph.md`. It includes new content, Character
Foundation and presentation, Custom Card Piles, readability, Events/Ancients, and the five
promoted M6.7 vanilla-override operation families.

Important global limits remain:

- singleplayer-only surfaces are never relabeled as multiplayer support;
- no prompt may invent arbitrary Harmony, reflection, Publicizer, or IL;
- unsupported current intent remains a blocking gap or explicit future item;
- no behavior-bearing arbitrary scene/material/audio generation outside promoted routes;
- no alternative Energy, global acquisition weighting, arbitrary transitions, or
  one-click Workshop publishing; and
- build/static/design evidence never substitutes for real-game behavior or presentation.

## Distribution

The Codex plugin manifest is `plugins/open-mod/.codex-plugin/plugin.json`; the repo-local
marketplace entry is `.agents/plugins/marketplace.json`. `publish.sh --plugin` renders the
committed plugin payload and `publish.sh --portable` renders the top-level Agent Skills
payload. Both contain relative paths so installation does not depend on the user's current
working directory.

The active implementation plan is `documents/IMPLEMENTATION_PLAN.md`. Completed milestone
results, earlier planning snapshots, and retired audits are indexed by
`documents/history/README.md`.
