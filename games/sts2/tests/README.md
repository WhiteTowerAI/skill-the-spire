# STS2 verification ownership

Completed migration evidence is archived in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. Current claims are defined by
`AGENTS.md`, `content-capability-graph.md`, and focused tests under
`games/sts2/tools/tests/`.
The focused M6.6 computed-Card result is archived in
`documents/history/M66_COMPUTED_VALUES_RESULTS.md`.
The failed initial native Ancient-dialogue proof, repair, and successful recheck are recorded in
`documents/history/M66_ANCIENT_DIALOGUE_RESULTS.md`.
The bounded advanced-targeting proof and its manual-verification exception are recorded in
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`.
The historical private-repair Package 4 result is retained in
`documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md`. The official RitsuLib `0.5.4`
promotion proof and current literal exceptions are recorded under
`games/sts2/experimental/card-pile-extra-hand/official-v054-proof/`; the formal route is
`sts2-api/reference/card-piles.md`.
The M6.7.0 catalog, localized-title aliases, no-op manifest, fail-closed checks, and
repeatable real-host collector development result are recorded in
`documents/history/M67_GROUNDING_KERNEL_RESULTS.md`. The complete M6.7 delivery and
representative acceptance are recorded in
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`; the separate current-catalog headed
no-op remains intentionally unrun. The later fail-closed Card-description and generated-file
namespace repair is recorded separately in
`documents/history/M67_POST_ACCEPTANCE_GENERATION_QUALITY_REPAIR.md`; it does not alter or
rerun the milestone acceptance.

## Model

Support is not a test result. Official product semantics plus the pinned public RitsuLib
profile establish support for a documented Package and its public consumers. Tests and
real-host runs report what actually worked; missing proof stays visible but does not make a
public Package unsupported.

1. Use local assertions for deterministic calculations, state transitions, payment floors,
   capacity, ordering, and reset rules.
2. Reuse the closest real host for lifecycle behavior and presentation.
3. For an ordinary feature or bug fix, stop after the changed behavior is proved in that
   real host; do not add a complete demo-Mod run to every change.
4. Use a fresh natural-language acceptance Mod only when the active implementation plan
   schedules a full user-pipeline gate or the human lead requests one, then retire it after
   recording the outcome.

M6.7 used batched verification by human-lead decision and closed on 2026-08-04. The final
source regression, payload parity/repeatability, local-plugin refresh, independent build,
and representative human-led in-game acceptance completed. M6.7.6 was canceled and moved
to Future Outlook. Tier 1, Tier 2/SelfTest, the current-catalog headed no-op, and every
unselected check remain unrun, not passed; do not rerun the closed milestone gate.

## M7 authoring-quality verification and closure

The human lead canceled M7.0 as a standalone evaluation Package on 2026-08-04. Behavioral
cases travel with M7.1 routing, M7.2 native grammar, M7.3 design planning, M7.4 scope/
traceability, and M7.5 coherence. M7.1 is implemented with
`m71-routing-scenarios.md` and
`tools/tests/test_m71_routing.py`: fast, co-design, revision, direct resume,
material-question filtering, contradictions, unsupported requests, and decision-preserving
deltas are deterministic shipped-instruction contracts. Independent forward-model runs are
unrun. These tests are separate from runtime support and Tier 1/Tier 2; they cannot prove
that a generated Mod loads, behaves correctly, looks correct, or is enjoyable.
The complete source/payload result and explicit exceptions are recorded in
`documents/history/M71_ADAPTIVE_ROUTING_RESULTS.md`.

M7.2 is implemented with `m72-native-grammar-scenarios.md` and
`tools/tests/test_m72_native_grammar.py`. Its structured inventory is tied to the exact
`0.107.1` assembly identity and records all five native starter decks. Exact catalog tests
cover every Character-specific Strike/Defend type, English/Simplified-Chinese title,
Basic rarity, Energy cost, tag, base value, and upgrade value. Contract tests cover lazy
Character-only loading, exact native-shaped proposals before deck questions, explicit
fact/convention/creative labels, deliberate-departure consequences, and Character SPEC
preservation. Independent forward-model runs, generated Mods, runtime loading, Tier 1,
Tier 2, headed review, and balance/playtest evidence are unrun. The complete source/payload
result is recorded in `documents/history/M72_NATIVE_DESIGN_GRAMMAR_RESULTS.md`.

M7.3 is implemented with `m73-design-planning-scenarios.md` and
`tools/tests/test_m73_design_planning.py`. Its three lazy references cover mechanic loops
and dominance, content roles and directed interactions, and formula/economy sensitivity.
Contract tests cover selective loading, the exact-Card fast path, the compact planning
capsule, accepted supported SPEC lowering, explicit hypotheses, and the human lead's
Mod-forward power bias with a choice-preserving ceiling. Independent forward-model runs,
generated Mods, runtime loading, Tier 1, Tier 2, headed review, and human balance/playtest
evidence are unrun. The complete source/payload result is recorded in
`documents/history/M73_MECHANIC_CONTENT_BALANCE_RESULTS.md`.

M7.4 is implemented with `m74-scope-traceability-scenarios.md`,
`tools/tests/test_m74_scope_traceability.py`, and `tools/design_trace.py`. Every route writes
adaptive DESIGN before SPEC. The validator checks stable scope/operation IDs,
MUST/PLACEHOLDER versus DEFER/OUT-OF-SCOPE placement, empty blocking gaps, bidirectional
current-design/SPEC links, supported route syntax, and actual shipped route files. Its
behavioral matrix covers supported-plus-unsupported intent, a larger future vision, and an
exact-Card compactness review. Independent forward-model runs, generated Mods, runtime
loading, Tier 1, Tier 2, headed review, and human artifact review are unrun. The complete
source/payload result is recorded in
`documents/history/M74_SCOPE_TRACEABILITY_RESULTS.md`.

M7.5 is implemented with `m75-coherence-scenarios.md`,
`tools/tests/test_m75_coherence.py`, and `tools/coherence_trace.py`. New/revised DESIGN
records accepted identity anchors, selected mechanics/name/localization/visual/Event/
Character surface checks, resolved conflicts, deliberate tensions, and a revision-only
impact queue. The validator checks stable references, current-surface ownership, allowed
targets/actions, empty pre-SPEC conflicts, and a nonempty affected queue for revisions. Its
behavioral matrix covers an Event localization/visual contradiction, a Character identity
conflict, and a terminology/palette revision that preserves accepted and rejected scope.
Two focused read-only independent forward-model prompts covered the Character conflict and
bounded revision. The initial conflict run exposed the missing temporary `conflict` state;
after repair, its rerun correctly blocked SPEC pending a user decision. The Event prompt
and complete matrix, generated Mods, runtime loading, Tier 1, Tier 2, headed review,
translation/visual review, and human artifact review remain unrun. The complete source/
payload result is recorded in `documents/history/M75_COHERENCE_RESULTS.md`.

M7.6 closed through a human-led external whole-skill evaluation rather than a shipped
source Package. The copied Watcher project records a macOS build, Tier 1, a bounded
SelfTest, and the human observation that the Mod was playable but not very good. The
harness did not drive Scry, composed Draw, Rushdown, Devotion, or draw-pile exhaustion;
one unconditional aggregate assertion and the final narrative overclaimed Scry coverage.
No post-observation DESIGN/SPEC delta and same-hypothesis replay occurred. The exact result
and exceptions are in
`documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`. By explicit human-lead decision,
that evaluation closes M7 without claiming a M7.6 source implementation, successful tuning
loop, polished Character, or complete runtime matrix.

Evaluate three layers:

1. **Deterministic contract:** required artifact sections, stable semantic fields, exact
   pinned facts, supported-route resolution, explicit gaps, and payload parity.
2. **Behavioral rubric:** question economy, materially distinct alternatives, concrete
   trade-offs, preservation of user decisions, STS2-native recommendations, coherent
   content roles and expressions, bounded change propagation, and honest unknowns.
3. **Human review:** whether the design proposal expresses the intended player experience
   and whether a real playtest observation warrants a design change. An LLM judge may assist
   comparison but is never the sole pass/fail authority.

Do not assert exact prose merely because one response was preferred. Assert exact names or
values only when they are pinned game facts or product contracts, such as the native
Character-specific Basic Strike/Defend identities, localized display names, tags, and
values used by the shipped Character grammar.

Pre-M7 maintenance replaced the retired proof identity, exact values, and log markers in
generic Character verification/reference text with current-`SPEC.md` assertions. A static
regression scans source plus both generated payloads so retired proof identities remain only
in history or repository-only evidence. This is a shipped-guidance regression check, not a
rewrite of historical proof.

When an M7 Package changes generated runtime behavior or presentation, use the same nearest
real-host rule as any other implementation change. Prompt-only work needs no game launch.
Real-player observations remain human-owned and may not be fabricated or replaced by
simulated personas.

## M8 whole-skill verification plan

M8 is planned and has not started. M8.1 is next selectable; later Packages wait on the
prerequisites and exact execution contracts in `documents/IMPLEMENTATION_PLAN.md`. The
Watcher evaluation is baseline failure evidence, not the final acceptance project. Package
cases must verify the decision each Package adds:

1. a literal completion claim cannot silently grow beyond the accepted current slice;
   complete single-element Mods keep their real product shape, while identity-critical or
   non-default player experiences map through existing DESIGN/SPEC operations;
2. identity-critical operations resolve to exact current routes before generation, while
   supported-but-unimplemented and unsupported remain distinct literal facts; reusable
   complex mechanics use maintained implementations with conformance cases for selection,
   ordering, movement, hooks, degenerate states, and input modes instead of local
   approximations; a claimed route that fails conformance blocks until its maintained
   implementation is repaired or its limitation is narrowed;
3. repair routing distinguishes implementation-equivalent, contract-fulfillment, accepted
   semantic-change, and missing-capability outcomes, returning only to the artifact that
   owns the changed fact;
4. claimed Windows/macOS installed workflows reproduce without mutating installed skills,
   track the process tree they create, and finish with no owned game child running; and
5. after M8.1-M8.3 and M8.5 close, one human-lead-selected M8.6 clean installed acceptance
   exercises the complete contract without reusing or repairing Watcher.

M8.6 is the only planned fresh natural-language full-pipeline gate and is not authorized to
run yet. Human play owns any claim about decision quality, comprehension, enjoyment, or
tuning; Tier 1/Tier 2 retain their existing literal meanings. M8.4 and its proposed separate
evidence-reporting subsystem were removed; existing verification ownership remains active.

The Watcher Exhaust-text, Scry, Hover Tip, Wrath, and leaked-process observations are audit
inputs for those generic contracts. They do not become five special-case assertions and do
not change a support row without current pinned maintainer grounding.

Host ownership:

| Host | Owns |
|---|---|
| `CombatPlayer` | content core, computed Card values, custom Card Piles/ExtraHand, hand emphasis, Relic/Power extra labels, advanced targeting, stateful relics, Scry, Character combat cues, and M6.7.1 existing-Card property/text/play/owner-hook behavior |
| `CombatEnemy` | Monster + Encounter, move vocabulary, combat/bestiary body |
| `MapNode` / Character | Event outcomes/presentation, bounded forced follow-up, native Ancient/Architect dialogue |
| real Rest Site / `MapNode` | Relic-owned option absence/gray/payment/stay/repeat/icon matrix |
| `RunStart` / Character | Foundation, static art/theme, combat cues, resource/UI, ordered buffer |
| `ModelDb`/localization after preload + offline PE metadata | M6.7 version catalog identity, stable title keys and 14-language display aliases, runtime semantic snapshot, adapter signatures/fingerprints, and no-op manifest grounding |
| nearest native visual consumers | M6.7.2 Card/CardPool, Relic/Power/Potion/Orb, Act, Event/Ancient, Encounter, Affliction/Enchantment/Modifier public visual providers; selected Card and Darv providers were included in the representative Mod accepted as a whole, while other providers remain unrun |
| native Ancient room | M6.7.3 initial-option append/replacement, visible/locked/cost/tip/relic presentation, ordered outcomes, selectors/rewards, page graph, native finish/choice history, and M6.7.2 visual composition; selected Darv replacement/page/portrait was included in the representative Mod accepted as a whole, while other routes remain unrun |
| `ModelDb` pools / unlock consumers | M6.7.4 public epoch gates plus Card/Relic/Potion pool add and fixed membership/epoch Adapters; one Card pool move was included in the representative Mod accepted as a whole, while cache timing, fresh-acquisition order/RNG, duplicates, and save variants remain unrun |
| combat/run owner streams, concrete non-Card lifecycle hosts, `CombatEnemy`, and ordinary Event room | M6.7.5 all public Relic/Potion/Power/Orb/Enchantment/Affliction/Monster owner hooks, intrinsic data, complete lifecycle/body replacements, Monster move graphs, paired Encounter rosters, and Event options/pages; selected Relic/Monster/Encounter routes were included in the representative Mod accepted as a whole, while unselected families remain unrun |

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof and `selftest done`. Trigger logs, terminal markers, and
model-only state are diagnostics, not behavior proof.

The M6.7.0 collector's strict Tier 2 proves that its checked snapshot was written with the
expected model count and assembly/file hashes. It is not gameplay-behavior or presentation
proof for a vanilla edit. M6.7.1 through M6.7.5 are the five promoted operation Packages.
M6.7.1 focused tests and compile-only check pass. M6.7.2 focused manifest/resource tests
pass, while its earlier Package-specific C# compile was not run. M6.7.3 focused manifest/
localization/catalog/documentation-route tests, M6.7.4 focused manifest/catalog/
documentation-route tests, and M6.7.5 focused 40-test checks/Python syntax pass. The final
regression passed `165/165`; payloads synchronized repeatably; and the independent
installed-plugin Mod built with zero warnings/errors. The human lead reported that the
representative Mod's effect test passed; no individual Card, Relic, Darv, Monster, or
Encounter observation is inferred. This does not prove the unselected providers, hooks,
availability modes, ordinary Event paths, or save variants.

Use one representative real host for a shared Package lifecycle. Add separate cases only
for materially different behavior or presentation risks; do not create one support gate per
consumer merely to justify the Package name. State Tier 1, Tier 2, headed checks, waivers,
and skipped checks literally.

The M6.6 Package 2A proof is an explicit exception: the human lead accepted its complete
manual behavior/presentation matrix after Tier 1, while the structured Tier 2 harness was
not run. Preserve that wording; do not report the omitted harness as passed.

Package 5 has the same explicit boundary. Its first headed Darv/Architect run failed, then
the repaired proof passed the human lead's visible native-flow recheck and the current log
showed the mounted PCK, both routes, clean progression, and no fresh error block. The log
did not contain the structured state proof or `selftest done`; strict Tier 2 remains an
exception rather than a pass.

Package 1 also uses that explicit boundary. The human lead accepted its complete zero-,
single-, and multi-candidate mouse/controller matrix, while current-run logs corroborated
the exact successful consumers and no fresh error block. No automated `selftest done`
harness ran, and queued-target invalidation was not exercised; strict Tier 2 remains an
exception rather than a pass.

The bounded Package 3 Relic-owned Rest Site option slice is implemented after the
human lead accepted its focused native absence/gray/enabled/payment/outcome/stay/repeat/
controller/custom-icon/fallback matrix. Per lead instruction, no log read followed the
headed run, and no structured `selftest done` harness ran; the exact Tier 1 log gate and
strict Tier 2 remain explicit exceptions. The pinned dev-console `gold` command ignores
negative values, so future manual routes must use normal Shop spending for a low-Gold state
or a narrow proof driver for a render-time stale-payment check.

Package 2B/2C authoring is implemented. Its human-led hand/Relic/Power matrix and strict
Tier 1 passed after narrowing Power authoring to one top-left label; strict Tier 2 was not
run and remains an explicit exception.

Package 4 Custom Card Piles is formally supported on official RitsuLib `0.5.4`. The human
lead accepted the unmodified-runtime focused ExtraHand cancellation, shortcut-isolation,
and consecutive-play result and promoted the complete documented Package. The current run
had a host save-backup cleanup error and no structured `selftest done`, so strict Tier 1 did
not pass and strict Tier 2 was waived rather than relabeled as passed. Future generated Mods
verify the scopes, styles, screens, movement, persistence, callbacks, and interactions they
actually select; unrun consumers do not narrow Package support.

Run one armed harness at a time. Preserve and restore unrelated user Mods. Do not reopen a
completed host proof unless a later source change exposes a real regression.

## Commands

```powershell
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured state proof>"
```

Completed acceptance evidence is historical. Future bug fixes still require verification
proportional to the changed behavior; an earlier acceptance result is not a blanket
substitute for regression testing.
