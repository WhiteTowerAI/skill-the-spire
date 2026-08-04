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
RitsuLib `0.5.4`. BaseLib has been removed from generated projects. M6.5, M6.6, and M6.7
are closed; their detailed results and exceptions live under `documents/history/`.

M7 Design Intelligence and User Experience is active. M7.0 was canceled as a standalone
evaluation Package. M7.1 through M7.5 are implemented and synchronized into both committed
payloads:

- M7.1 infers fast, co-design, or revision and preserves direct resume;
- M7.2 grounds Character Foundation recommendations in the pinned native starter inventory;
- M7.3 plans mechanics, content sets, formulas, economies, and honest tuning hypotheses;
- M7.4 writes adaptive DESIGN before a validated current-slice SPEC; and
- M7.5 checks selected identity/presentation surfaces and propagates revisions narrowly.

M7.6 human-owned playtest feedback and tuning has not started. No GitHub release is
currently authorized or planned.

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
unresolved gaps, invalid dispositions, invented route forms, and absent route files.
`coherence_trace.py` rejects invalid references, unresolved pre-SPEC conflicts, and
unbounded revision queues. Neither validator can prove subjective quality, balance,
enjoyment, or runtime behavior.

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

Edit source under `games/sts2/`; regenerate both payloads through `publish.sh`. Generated
Mods use the pinned compile package and discover a validated game-local or official
Workshop RitsuLib runtime. They never copy the maintainer checkout or depend on BaseLib.

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

M7.1-M7.5 are prompt/design workflow changes. Their deterministic scenarios and validators
prove shipped contracts only. Two focused read-only forward-model prompts exercised M7.5
conflict and revision behavior; no full M7 forward-model matrix, generated Mod, Tier 1,
Tier 2, headed design review, or human playtest is inferred.

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
