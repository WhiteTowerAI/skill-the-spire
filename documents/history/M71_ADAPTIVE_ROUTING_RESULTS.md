# M7.1 Adaptive Interview and Routing Results

Date: 2026-08-04

## Result

M7.1 source development is complete after explicit human-lead selection. The `modmaker`
workflow now reads project state first, resumes an unchanged unfinished project directly,
and otherwise infers one of three authoring routes:

- **fast:** zero questions for a complete narrow request and at most one compact
  clarification round when one material decision is missing;
- **co-design:** the highest-impact open decision receives two or three materially
  different player-facing choices, concrete trade-offs, and a reasoned recommendation; and
- **revision:** existing artifacts are preserved through a bounded keep/change/check/
  re-verify delta instead of restarting the Interview.

The shared material-question filter rejects questions answered by the prompt, project
artifacts, pinned references, capability graph, or safe defaults. Contradictory and
unsupported requirements stop before SPEC/scaffold and require an explicit user decision;
requests to skip questions never authorize a silent downgrade.

M7.1 reads an existing `DESIGN.md` as creative state but does not define or generate its
full schema, current/future split, or design-to-SPEC traceability. Those remain M7.4 work.
STS2-native design grammar remains M7.2, and playtest-led tuning remains M7.6.

## Behavioral Contract

`games/sts2/tests/m71-routing-scenarios.md` records six semantic cases:

1. a complete Card takes fast and asks zero questions;
2. a vague health-risk Card takes co-design and receives materially different trade-offs;
3. contradictory Card costs pause for one constrained resolution;
4. an unsupported multiplayer/retained-zone/audio request preserves intent and stops;
5. an unchanged unfinished project resumes at its first incomplete stage; and
6. an existing Card value change uses a bounded revision and proportional re-verification.

A source-contract review checked all six against the shipped instructions. No independent
forward-model output was produced, so actual model behavior is not inferred from the
scenario definitions or static assertions.

## Verification

- focused M7.1 routing contract: `7/7` passed;
- existing semantic contract regression: `16/16` passed;
- complete STS2 Python regression: `185/185` passed;
- Python compilation: passed for `games/sts2/tools`;
- `quick_validate.py`: passed for source modmaker/sts2-api, plugin modmaker/sts2-api, and
  portable modmaker/sts2-api;
- plugin and portable payloads: `162` effective files each, zero parity differences;
- forced publish repeatability: both passes produced tree SHA-256
  `b42b21f7ec902f2091c0f5cf2c38cecf5ff2b6fab487a577a8fc02daea1bee64`;
- new `route.md`: identical source/plugin/portable SHA-256
  `2bdeaeb45828de2e396f48241f28d6f8a8646a9a5facf284e1945c5cf00cb09d`.

## Explicit Exceptions

- No independent fresh-agent or forward-model execution of the six prompts was run.
- No generated Mod, build, game launch, Tier 1, Tier 2/SelfTest, headed review, or playtest
  was run. M7.1 changes prompt workflow only and does not change generated runtime behavior
  or presentation.
- M7.2 and later Packages were not started or authorized by this result.
