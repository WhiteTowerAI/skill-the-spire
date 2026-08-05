# M7.6 whole-skill evaluation and M7 closure

## Decision

The human lead closed M7 Design Intelligence and User Experience on 2026-08-05.
M7.1 through M7.5 remain the implemented source Packages recorded in their individual
result files. M7.6 closed through a human-led external whole-skill evaluation rather than
through a new source-workflow Package.

This is a milestone-close decision, not a claim that the evaluated Mod was polished, that
every generated route passed, or that a playtest-tuning implementation was added to the
shipped skill. The human-lead-selected cross-stage lessons from the evaluation now define
planned M8 End-to-End Product Integrity work.

## Evaluation Artifact

On 2026-08-04 the human lead used the installed open-mod workflow through Claude Code on
macOS to create a Watcher Character/content-set project targeting STS2 `0.107.1` and the
RitsuLib `0.5.4` compile profile. A workspace-supplied copy is retained under
`usertest_M76/watcher-port/` for inspection. It contains:

- the exported main conversation and capability-audit records;
- `DESIGN.md`, `SPEC.md`, `PLAN.md`, and project `MEMORY.md`;
- the generated C# Character, Card, Power, Relic, helper, and SelfTest source;
- English and Simplified Chinese localization; and
- the project and runtime manifests.

The copy is evaluation input, not authoritative generator source and not a shipped plugin
or portable payload. The durable facts needed for milestone status are recorded here so
the active plan does not depend on that workspace directory remaining present.

## Literal Result

The exported project record reports:

- a successful macOS compile and deployment with zero warnings and zero errors;
- Tier 1 PASS for the Watcher load marker, matching host/compat marker, modded mode, and no
  fresh Watcher error block; and
- a completed in-process Tier 2 harness with `selftest done` and 24 `StateProof` calls in
  source, although project `PLAN.md` summarizes the count as 20.

The human lead subsequently played the Mod and supplied the controlling experience result:

> The Mod is playable, but the result is not very good.

That observation is human-owned playtest evidence. It does not become a balance pass,
presentation pass, or complete Character acceptance.

The human lead later supplied five concrete whole-skill observations from the same run:

- the skill-launched game process was not closed automatically; a macOS-specific cause was
  suspected but not established;
- generated Card Exhaust behavior was not represented in the Card description;
- the generated Scry behavior was not semantically accurate;
- expected Hover Tips were absent; and
- Wrath did not implement the requested incoming-damage multiplier, so its replacement
  cost did not deliver the literal core behavior.

These are human-reported evaluation facts, not current-repository reproductions. They are
recorded as examples of generic process-lifecycle, complete player-facing semantics, and
capability-conformance failures rather than as a Watcher-specific repair list.

## Evidence Limits

The Tier 2 harness proves a bounded subset of concrete state behavior. It drives Character
selection/run start, starter identity, maximum Energy, Pure Water/Miracle, Eruption into
Wrath, Watcher-Card damage multiplication, the Wrath end-turn trigger, same-stance no-op,
Calm exit Energy, Mantra threshold entry into Divinity, and explicit Miracle movement to
Exhaust.

The exported conversation explicitly says the harness did not drive Scry, composed Draw,
Rushdown, or Devotion. Draw-pile exhaustion/reshuffle behavior also remained unobserved.
One unconditional final assertion says `stance/mantra/scry observed=all`; it is not Scry
evidence. The final narrative later calls the Scry foundation verified despite its own
unrun disclosure. Those overclaims are evaluation findings, not accepted proof.

The result also retains these literal boundaries:

- all Character, Card, Relic, Power, and Energy presentation used placeholders;
- the reward pool was a nine-Card vertical slice, not a complete run-scale content set;
- several identity-bearing behaviors used acknowledged fallbacks or composed routes;
- the human observation was not followed by a recorded DESIGN/SPEC delta and same-
  hypothesis replay;
- no current-repository Windows or macOS replay was run for this documentation closeout;
- the local macOS session repaired path/deployment assumptions during the consumer run;
  those local changes are not treated as synchronized repository fixes; and
- no repository source, generated payload, GitHub release, or Workshop publication is
  accepted by this result.

## Whole-Skill Findings

The evaluation exposed cross-stage product-integrity problems rather than one Watcher bug
list:

1. The workflow did not keep a literal distinction between a mechanic prototype, an
   evaluable vertical slice, and a run-capable Character/content set.
2. Identity-critical capability hypotheses reached current DESIGN/SPEC with no blocking
   gap, leaving maintainer-level API discovery to the consumer author/verify session.
3. Player-visible repairs moved forward locally instead of backtracking to DESIGN, scope,
   and trace validation.
4. Individually accepted fallbacks accumulated against the same identity anchors without
   a combined player-experience review.
5. Minimum registration/merchant counts and one-node-per-role coverage did not establish
   an evaluable content ecosystem or adequate presentation.
6. Implementation, generated SelfTest, and final reporting were too correlated; evidence
   coverage and narrative claims could disagree.
7. macOS success depended on consumer-session path/deployment repair rather than an
   immutable, repository-verified installed workflow.
8. Superseded hypotheses and generic findings remained mixed into project state instead
   of becoming one current fact and a bounded upstream-learning queue.
9. Launch ownership ended at process creation rather than verified cleanup of the spawned
   process tree.
10. Runtime behavior, lifecycle, Card text, keyword/hover discoverability, and localization
    were not treated as one inseparable player-facing operation contract.
11. Complex mechanics could be re-created approximately inside the consumer project, or
    replaced with a different effect, without maintained semantic-conformance proof or a
    capability-promotion decision.

These findings remain the complete evaluation record. The active implementation plan owns
which findings become M8 Packages; the others remain historical observations. None changes
the current RitsuLib runtime capability graph by itself.

## M7 Closure Boundary

M7 is complete by explicit human-lead decision. Its durable outcome is:

- M7.1-M7.5: implemented source workflow with the exact evidence and exceptions in their
  individual result files;
- M7.6: closed by the external human-led whole-skill evaluation recorded here, with no new
  source Package claimed; and
- no additional M7 implementation, forward-model matrix, generated-Mod acceptance, or
  playtest revision loop is pending.

M8 is planned but has not started. Do not repair the Watcher project as a substitute for
M8, edit installed payloads in place, or begin M8.1 without later human-lead instruction.
