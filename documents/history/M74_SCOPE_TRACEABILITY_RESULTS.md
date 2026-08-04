# M7.4 Scope and Design-to-SPEC Traceability Results

Date: 2026-08-04

## Result

M7.4 source development is complete after explicit human-lead selection. Every authoring
route now writes a durable, adaptive `DESIGN.md` between Interview and SPEC:

- a fast request receives a compact intent and scope capsule rather than a full GDD;
- a co-design request records the accepted concept, meaningful decisions, alternatives,
  current deliverable, future vision, and open gaps; and
- a revision preserves stable decisions and IDs while changing only the affected scope.

`DESIGN.md` owns player intent and scope through stable `D-###` items. Each requirement is
classified as current `MUST`, current `PLACEHOLDER`, future `DEFER`, or rejected
`OUT-OF-SCOPE`. An unsupported requirement remains a blocking gap until the user explicitly
accepts a supported current alternative, defers the original intent, or removes it from
scope. The workflow does not silently downgrade that intent or generate a speculative
runtime route.

`SPEC.md` owns only exact current semantic operations. Its `OP-###` entries map back to
current design items and identify an existing shipped `recipes/*.md` or `reference/*.md`
route. `design_trace.py` checks the mapping in both directions, rejects unresolved gaps,
missing or extra operations, future leakage, one-way links, invalid disposition/support
states, invented route forms, and absent route files. Author treats the validated operations
as a generation allowlist. Deferred and out-of-scope items produce no SPEC stub, source,
resource, or implied implementation promise.

Unfinished pre-M7.4 projects that already contain `SPEC.md` are backfilled from settled
intent and accepted operations without restarting Interview or inventing historical
rationale, rejected alternatives, or future vision. M7.4 changes authoring artifacts and
validation only; it does not expand the runtime capability graph.

## Behavioral Contract

`games/sts2/tests/m74-scope-traceability-scenarios.md` records three semantic cases:

1. a Duelist keeps normal Energy and uses supported Momentum as a secondary combat
   resource only after the user explicitly accepts that current slice; replacement Energy
   remains a deferred future intent and never enters SPEC;
2. a Frost Oracle preserves its full future vision while the first deliverable contains
   only the exact Character Foundation, Starter relic, and accepted static presentation
   fallback; and
3. an exact Ember Step Card keeps the fast route, writes a short DESIGN capsule, and maps
   only its exact Card behavior and placeholder-art fallback into SPEC.

A source-contract review checked all three against the shipped Route, Interview, DESIGN,
SPEC, Author, and trace-validator instructions. No independent forward-model output was
produced, so actual model behavior is not inferred from scenario definitions or static
assertions.

## Verification

- focused M7.4 scope/traceability contract: `10/10` passed;
- adjacent M7.1 routing, M7.2 native grammar, M7.3 planning, M7.4 traceability, and semantic
  contracts: combined focused run `49/49` passed;
- complete STS2 Python regression: `211/211` passed;
- Python compilation: passed for `games/sts2/tools/design_trace.py`;
- the source, plugin, and portable `design_trace.py` layouts each resolved their adjacent
  `sts2-api` route files and validated the shipped examples with `design_items=3` and
  `operations=2`;
- `quick_validate.py`: passed for source modmaker/sts2-api, plugin modmaker/sts2-api, and
  portable modmaker/sts2-api;
- plugin and portable payloads: `169` effective files each, zero differences across the
  `modmaker` and `sts2-api` trees; and
- forced publish repeatability: both passes produced effective tree SHA-256
  `8c373202029cd3ac2138e616efca14588dc0cf534b2608ab9370c47e1bb80f07`.

## Explicit Exceptions

- No independent fresh-agent or forward-model execution of the three prompts was run.
- No generated Mod, build, game launch, Tier 1, Tier 2/SelfTest, headed review, human
  artifact review, or playtest was run. M7.4 changes prompt/design workflow and validation
  only; it does not change generated runtime behavior or presentation.
- Static trace validation proves artifact consistency, not that a design is coherent,
  balanced, fun, supported beyond its recorded routes, or accepted by a human.
- M7.5 and later Packages were not started or authorized by this result.
