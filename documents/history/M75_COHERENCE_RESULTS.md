# M7.5 Theme, Narrative, Presentation, and Coherence Results

Date: 2026-08-04

## Result

M7.5 source development is complete after explicit human-lead selection. The authoring
workflow now loads one proportional coherence reference when a request selects multiple
intentional expressive surfaces, explicitly asks for theme/narrative/presentation work, or
revises an identity anchor. A narrow exact Card keeps its fast route and receives only a
compact mechanics/naming check unless a second intentional expression or material conflict
requires the reference.

Every new or revised `DESIGN.md` contains an independent `open-mod-coherence/v1` block:

- one to three stable `A-###` anchors derive from accepted `D-###` decisions;
- selected current mechanics, naming, localization, visuals, Event text, and Character
  identity surfaces state how they express those anchors;
- unresolved contradictions use a temporary `conflict` surface status and a specific
  conflict record, then block SPEC until the user aligns the expression, revises the
  anchor, or explicitly accepts deliberate tension; and
- revision work records an ordered `Q-###` impact queue using `UPDATE`, `REVIEW`,
  `REVERIFY`, and focused `PRESERVE` actions.

`coherence_trace.py` validates the contract, stable design references, current-surface
ownership, allowed surfaces/statuses, resolved pre-SPEC conflicts, route agreement, and
revision queue structure. It deliberately does not judge whether prose, translation, art,
or gameplay is subjectively coherent. Authoring still emits only M7.4's validated current
SPEC operations. Coherence cannot create a runtime route, promote future scope, invent a
placeholder theme, or turn text/art/build evidence into behavior, balance, or enjoyment
evidence.

New fast/co-design work has an empty impact queue. A revision requires at least one affected
target and updates DESIGN before SPEC and downstream expressions. Stable runtime and
localization identifiers are reviewed rather than renamed solely because a display term
changed. An unchanged pre-M7.5 project resumes without forced backfill; its next design
revision derives the coherence block from explicit existing facts.

M7.5 changes authoring guidance, durable design state, and validation only. It does not
expand or alter the runtime capability graph.

## Behavioral Contract

`games/sts2/tests/m75-coherence-scenarios.md` records three semantic cases:

1. an Event's Simplified Chinese text changes `20 HP` loss into Max HP loss while its
   portrait promises a free gift; DESIGN/SPEC remain authoritative and both contradictions
   must be resolved before authoring;
2. a patient Frost Oracle's aggressive title and art direction require one explicit choice
   to align the identity, revise it, or preserve the contrast as deliberate tension; and
3. a visible mechanic rename and palette revision propagate only to affected terminology,
   localization, Event text, art prompts, and proportional checks while preserving rules,
   stable IDs, accepted content, rejected Spine, and deferred voice.

Two focused read-only independent forward-model prompts were run. The revision prompt
preserved the resource rules, stable identifiers, accepted content, Spine exclusion, and
voice deferral while producing a bounded ordered impact queue. The first Character-conflict
prompt exposed a real contract gap: the schema allowed only resolved `aligned` and
`deliberate-tension` statuses even though the workflow had to persist an unresolved conflict
before asking the user. The validator and instructions were repaired to allow a temporary
`conflict` status only with a matching conflict record and still fail before SPEC. A fresh
focused rerun then identified the exact art-versus-defense contradiction, asked one material
choice, preserved the exact mechanics, and stopped before SPEC.

The Event prompt and the complete three-case forward-model matrix were not run. The two
focused outputs are behavioral evidence for those exercised routes only, not human artifact
review or proof of generated runtime behavior.

## Verification

- focused M7.5 coherence contract: `9/9` passed;
- adjacent M7.1 routing through M7.5 coherence contracts: `42/42` passed;
- complete STS2 Python regression: `220/220` passed;
- Python compilation: passed for `games/sts2/tools`;
- the source, plugin, and portable `coherence_trace.py` layouts each validated the shipped
  DESIGN example with `anchors=1`, `surfaces=2`, and `queue=0`;
- `quick_validate.py`: passed for source modmaker/sts2-api, plugin modmaker/sts2-api, and
  portable modmaker/sts2-api;
- plugin and portable payloads: `171` effective files each across the `modmaker` and
  `sts2-api` trees, with zero differences; and
- two forced publish passes produced the same normalized effective-tree SHA-256
  `4465e0e0642031598a089b15b20023ea5cdafddcbc833ae19c4e547d77d8a6df`.

The new source/plugin/portable files are byte-identical per file:

- `coherence_trace.py`:
  `d1f4ef1cb492e641848496c1b11a72937ddc529336c6313b9fd1ecbb8ff2e9b1`; and
- `coherence-review.md`:
  `4f7719cac689fd0c94eca1fa1f37b6d9fb5892497914c64428df61a93f44bc44`.

## Explicit Exceptions

- The Event forward prompt and full three-case independent forward-model matrix were not
  run. The two focused fresh-agent checks are not a human artifact review.
- No generated Mod, build, game launch, runtime load, Tier 1, Tier 2/SelfTest, headed
  review, translation review, visual review, or human playtest was run. M7.5 does not change
  generated runtime behavior or presentation, so no game proof was scheduled.
- Static contract and trace validation prove structure and preserved references, not that a
  theme is compelling, localization is fluent, art is effective, a design is balanced or
  fun, or a human accepts the artifact.
- M7.6 was not started or authorized by this result.
