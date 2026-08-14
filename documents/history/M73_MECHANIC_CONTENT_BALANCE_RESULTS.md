# M7.3 Mechanic, Content-Set, and Balance Planning Results

Date: 2026-08-04

## Result

M7.3 source development is complete after explicit human-lead selection. The routed
authoring workflow now loads three independent planning references only when applicable:

- `design/mechanic-planning.md` for player fantasy, meaningful competing actions, the
  trigger-to-payoff/reset loop, risk/reward, STS2 singleplayer pressure, exact edge rules,
  tuning knobs, and dominant-strategy review;
- `design/content-set-planning.md` for Foundation/access/payoff/consistency/defense/
  scaling/bridge/release roles, real content nodes, directed interaction coverage, and
  archetype dominance risks; and
- `design/balance-planning.md` for evidence classes, formulas, sources/sinks, timing and
  opportunity cost, low/working/high sensitivity, independent knobs, and open human
  playtest hypotheses.

An exact narrow Card retains the M7.1 fast path and does not receive all three reviews
merely because it contains a number. Character/content-set planning composes with M7.2
Character Foundation; it does not replace the pinned starter proposal.

The human lead selected a deliberate Mod-forward numeric posture. In the absence of a
contrary user direction, the working value should be clearly rewarding and modestly
stronger than the closest checked native comparison in its intended state. There is no
fixed percentage. A weak option with no plausible pick/use case fails the design, while a
value is above the playability ceiling when it erases meaningful choices, setup, or costs;
trivializes ordinary opposition; or creates a deterministic, self-funding, or unbounded
loop. Without measurements or human playtest evidence, the result remains a generous
working hypothesis rather than a balance or enjoyment claim.

Interview carries a compact M7.3 planning capsule. SPEC receives only accepted, supported,
exact current rules, values, formulas, content nodes, and directed interactions. A material
open hypothesis stops SPEC; rationale, alternatives, sensitivity discussion, dominance
review, future vision, and playtest evidence do not become generated facts. M7.4 still owns
the durable `DESIGN.md`, current/future slice, and design-to-SPEC traceability. M7.3 does not
expand the runtime capability graph.

## Behavioral Contract

`games/sts2/tests/m73-design-planning-scenarios.md` records three semantic cases:

1. an ambiguous Heat mechanic receives one high-impact structural decision, materially
   different player-action alternatives, a compact loop/edge/tuning capsule, and an honest
   dominance review;
2. a glassblower Character/content set begins from the M7.2 Foundation, then builds real
   role coverage and a directed interaction graph without mistaking a large card list for
   a coherent or balanced ecosystem; and
3. an Ink economy computes `ceil(3 / expected Skill triggers per turn)` and 4 damage per
   Ink, applies the Mod-forward posture, audits source/sink/reset/cap/opportunity-cost and
   self-funding risks, and refuses to declare 12 damage balanced without evidence.

A source-contract review checked all three against the shipped route, Interview, SPEC, and
planning references. No independent forward-model output was produced, so actual model
behavior is not inferred from the scenario definitions or static assertions.

## Verification

- focused M7.3 planning contract: `8/8` passed;
- adjacent M7.1 routing, M7.2 native grammar, and semantic contracts: combined focused run
  `39/39` passed including M7.3;
- complete STS2 Python regression: `201/201` passed;
- Python compilation: passed for `games/sts2/tools`;
- `quick_validate.py`: passed for source modmaker/sts2-api, plugin modmaker/sts2-api, and
  portable modmaker/sts2-api;
- plugin and portable payloads: `167` effective files each, zero differences across the
  `modmaker` and `sts2-api` trees;
- forced publish repeatability: both passes produced effective tree SHA-256
  `0e98c2d87757262d18df8566c768e2fce5374f7f772fac8ea9d786227265f68b`;
- new reference source/plugin/portable SHA-256 values are identical per file:
  - mechanic planning:
    `9861ae2d7bc77e0215c2af080a976b3278bf7b14671685783a2447800919e9f4`;
  - content-set planning:
    `1e5f7b7f91a4221a8f1fb0aa336d9fd2474b67a096242ab4c998cf290554fa2f`;
  - balance planning:
    `6f28eb32d4b37ca1cc14745a82844491a1b86018199f3461009af2945fd6c80b`.

## Explicit Exceptions

- No independent fresh-agent or forward-model execution of the three prompts was run.
- No generated Mod, build, game launch, Tier 1, Tier 2/SelfTest, headed review, or human
  playtest was run. M7.3 changes prompt/design workflow only and does not change generated
  runtime behavior or presentation.
- No numeric recommendation, content set, or mechanic is claimed balanced, fun, or proven
  by static calculations or contract tests.
- M7.4 and later Packages were not started or authorized by this result.
