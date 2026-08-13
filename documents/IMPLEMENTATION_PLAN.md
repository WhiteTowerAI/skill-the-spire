# Implementation plan: M8 end-to-end product integrity

## Status

M8 is the active milestone. M8.0-M8.3 and M8.5 are closed; their implementation detail and
exceptions belong in `documents/history/`. M8.4 was removed by the human lead.

M8.7 Product Boundary Generalization is implemented in authoritative source and both payload
forms. Its result record and explicit human closure remain outstanding, so it is implemented but
open. Do not re-execute, reimplement, or narrow it.

M8.8 Surface Effect Composability Generalization is paused by explicit human-lead direction. Its
former trace/schema-oriented draft predates both RitsuLib `0.5.11` and the simplified workflow and
is retired. The refactored future plan below replaces that draft, but is not execution
authorization. Future resumption must first refresh the official guide and current public
source/API/Compat audit, then obtain explicit human confirmation before implementation.

M8.6 is the final clean installed whole-skill acceptance. It intentionally follows M8.7 and M8.8
despite its number. It is ineligible while either Package remains open and has no executable
contract until the human lead selects the exact request and host.

Current order and gate:

1. M8.7: implemented and open; result record and explicit closure remain.
2. M8.8: paused; current-profile research/contract refresh and confirmation required.
3. M8.6: waiting for both closures and explicit selection.

## New-Session Start Protocol

1. Read root `AGENTS.md`, `documents/PROJECT.md`, `documents/BASELINE_RESEARCH.md`, this file,
   `games/sts2/tests/README.md`, and `games/sts2/tests/content-capability-graph.md`.
2. Treat `documents/history/` as immutable evidence, never as current instruction.
3. Check `git status` before editing and preserve unrelated dirty/untracked work.
4. A plan entry is not execution authorization. Do not start M8.8 from its retired draft. Do not
   start M8.6 while M8.7 or M8.8 remains open.
5. Work in authoritative source under `games/sts2/`. Never hand-edit `plugins/open-mod/` or
   top-level `skills/`; regenerate them through `publish.sh` only when explicitly authorized.
6. Do not install a payload, launch the game, run Tier 1/Tier 2, create a fresh acceptance Mod,
   commit, push, publish, or release merely because a plan mentions those actions.
7. Close a Package only after its named result exists, active documents that own changed facts are
   synchronized, and the human lead explicitly accepts closure.

## Current Product Contract

The active Mod-generation workflow is:

```text
plain-language request
  -> adaptive interview when needed
  -> concise DESIGN.md
  -> implementable SPEC.md
  -> capability_preflight.py
  -> scaffold
  -> author + SelfTest
  -> build
  -> Tier 1
  -> Tier 2 / SelfTest
  -> headed human review when needed
  -> direct report from actual results
```

`DESIGN.md` records intent, accepted decisions, current scope, and explicit `Not Now` items.
`SPEC.md` is the sole implementation work order and includes concrete content/behavior/text,
selected support routes, and exact autotest scenarios. Existing projects may retain old metadata;
the current workflow ignores it and does not force migration.

Author runs a single thin capability check. It validates route existence and the pinned facts
needed to prevent unsupported or silently unreachable raw model-hook implementations. It does not
validate Markdown, ordinary fields, C# signatures, manifests, resources, localization, runtime
behavior, presentation, evidence, or project status.

Generated Mods target STS2 `0.107.1` and the RitsuLib Compat `0.5.11` authoring/API baseline.
Scaffold pins the exact validated local Compat DLL it compiles against, while runtime manifests
require `STS2-RitsuLib >= 0.5.11`. Generated projects have no framework `PackageReference` and no
BaseLib dependency.

Capability statements keep three facts distinct:

- `framework-expressible`: the pinned public/fixed API can express the operation;
- `open-mod-authorable`: shipped recipe/reference guidance covers its implementation and proof;
- `game-observed`: the exact shape ran successfully in its real host.

Static source, tests, Build, or payload synchronization do not imply game observation.

## Package Summary

| Package | State | Durable record or next requirement |
|---|---|---|
| M8.0 - skill structure restructuring | Closed 2026-08-10 | `documents/history/M80_SKILL_STRUCTURE_RESULTS.md` |
| M8.1 - literal deliverable contract | Closed 2026-08-10 | `documents/history/M81_DELIVERABLE_CONTRACT_RESULTS.md` |
| M8.2 - exact semantic capability conformance | Closed 2026-08-10 | `documents/history/M82_CAPABILITY_CONFORMANCE_RESULTS.md`; its two real-host hook proofs remain assigned to M8.6 |
| M8.3 - semantic continuity and backtracking | Closed 2026-08-11 | `documents/history/M83_SEMANTIC_CONTINUITY_RESULTS.md` |
| M8.4 | Removed 2026-08-05 | Do not reuse the number or recreate the Package |
| M8.5 - cross-platform installed workflow | Closed 2026-08-12 with exceptions | `documents/history/M85_CROSS_PLATFORM_WORKFLOW_RESULTS.md`; macOS installed reproduction and launcher-owned process-tree cleanup remain unresolved |
| M8.7 - product boundary generalization | Implemented; open | `documents/history/M87_PRODUCT_BOUNDARY_GENERALIZATION_RESULTS.md` and explicit closure remain required |
| M8.8 - surface effect composability | Paused; refactored future plan recorded | Refresh current `0.5.11` evidence, confirm the plan, then implement recipe/reference authoring and proportional proof without new trace/schema machinery |
| M8.6 - clean installed whole-skill acceptance | Waiting | Eligible only after M8.7/M8.8 close and the human lead selects its contract |

## M8.7 Preservation Gate

M8.7 generalized nine product families: secondary resources; Monster move graphs, Encounter
composition, and HP ranges; Character starting fields; Card- or Relic-owned Rest Site options;
multiple computed Card values; reusable bounded state; bounded forced Event mappings; new-Card
Star costs; and bounded Event acquisition/shake profiles.

Preserve their authoring guidance, lowering routes, hard boundaries, and proof matrices. Removing
the old surface JSON contracts and management validators does not remove these capabilities. Newly
generalized variants remain game-unobserved unless their exact real-host scenario has run.

No M8.7-specific compile, Tier 1, Tier 2, headed, install, game, or save/load proof is inferred from
source implementation or payload presence.

## M8.8 - Surface Effect Composability Generalization

### State And Authorization Gate

M8.8 remains paused and unimplemented. This section is its architecture-adjusted future plan, not
an executable contract. Do not begin its audit, source edits, generated proof project, payload
regeneration, install, game launch, or result record until the human lead explicitly selects M8.8.

When selected, the first turn is research and plan confirmation only:

1. refresh the official RitsuLib guide navigation, public `v0.5.11` source/API, and
   `STS2.RitsuLib.Compat.0.107.1` metadata;
2. compare the refreshed facts with this plan and the current capability graph;
3. report any changed assumptions, newly found surfaces, or boundaries; and
4. obtain explicit human-lead confirmation of the updated implementation scope before editing
   authoritative source.

M8.7 remains a preservation baseline. M8.8 may reuse and compose its nine generalized families but
must not reimplement, narrow, or relabel them. M8.8 does not start M8.6.

### Goal

Make every player-visible effect capability exposed by the pinned RitsuLib `0.5.11` profile for
Card, Potion, Relic, Power, Orb, Enchantment, Monster, and Event usable through open-mod's normal
human-readable SPEC and Author workflow, including new combinations not represented by an older
recipe or proof Mod.

The resulting workflow remains:

```text
human intent
  -> implementable SPEC behavior and Autotest scenarios
  -> existing recipe/reference route
  -> thin capability preflight only where silent unsupported code is otherwise possible
  -> Author + SelfTest
  -> Build
  -> real-host Tier 1/Tier 2 when selected
  -> direct report
```

Support does not depend on a capability having appeared in an earlier open-mod artifact. The
current pinned public API and lifecycle decide whether it is framework-expressible; complete
shipped authoring knowledge decides whether it is open-mod-authorable; only an actual real-host run
makes a particular shape game-observed.

### Non-Goals And Hard Boundaries

M8.8 must not:

- create a new large schema, capability ledger, trace graph, ID family, surface JSON envelope, or
  per-Mod evidence table;
- restore any deleted workflow validator or add a new validator for Markdown wording, headings,
  ordinary fields, recipe prose, stage state, or proof accounting;
- turn `capability_preflight.py` into a general SPEC validator;
- require one proof Mod or one test for every individual API symbol;
- create new content surfaces, registration paths, arbitrary UI/VFX hosts, multiplayer claims,
  cross-Mod coordination, or external runtime dependencies;
- generate prompt-derived Harmony, reflection, Publicizer, IL, or private/internal access; or
- treat Build, source tests, a hook-fired log, or previous-version evidence as current gameplay
  proof.

Ordinary C#/BCL, public STS2 `0.107.1` and RitsuLib Compat `0.5.11` APIs, Mod-owned helpers and
state, and existing maintained fixed Adapters remain valid implementation tools. A composition
blocks only when it requires a capability absent from the pinned profile, a value unavailable in a
legal lifecycle, a forbidden mechanism, or a separately unsupported product surface. Record the
smallest concrete boundary.

### Part 1 - Refresh The Current Effect Surface

Use the official guide as the discovery index, then verify exact symbols and lifecycle behavior
against public `v0.5.11` source/API and pinned Compat metadata. Cover all eight selected owner
surfaces rather than searching only for effect names already present in open-mod.

Review the existing owners that can already express or constrain an effect:

- the eight relevant `skills/modmaker/surfaces/*.md` pages;
- their `sts2-api/recipes/*.md` and referenced capability pages;
- model-hook participation, targeting, computed values, state, resources, Rest Site, Event,
  Monster, vanilla composition, localization, and SelfTest guidance;
- the pinned model-hook and vanilla catalogs; and
- the current capability graph and known limitations.

Keep the audit as a concise maintainer research record organized by official guide/source area and
its eventual recipe/reference owner. It may list coverage and unresolved questions, but it is not
a generated-project contract, schema, or permanent per-effect proof ledger. For every discovered
area, decide one of four plain-language outcomes:

- current-profile player-visible effect needing an authoring owner;
- lifecycle/query/target/state context needed by an effect owner;
- non-effect registration, asset, diagnostic, or tooling API; or
- retained product boundary with the concrete reason.

The refresh is complete only when every guide area and relevant public API area is accounted for,
every player-visible effect has an existing or proposed concise owner, and at least one capability
absent from older open-mod recipes/proofs is included so the work is not circular.

### Part 2 - Put Durable Knowledge In Recipes And References

Implement the refreshed result in the smallest existing owner set. Prefer one shared reference for
knowledge used by several surfaces and keep owner-specific lifecycle, parameters, ordering, and
examples in the corresponding recipe/surface page. Do not duplicate eight effect catalogs.

For each materially distinct capability family, the authoring guidance must let Author determine:

- the real public command/callback/data route and valid owner surfaces;
- trigger timing, target/source identity, async ordering, returned result, and neutral behavior;
- required values, conditions, Mod-owned state/helpers, and composition order;
- rules text, DynamicVars/Hover Tips, bilingual localization, preview, and presentation consumers
  when player-visible;
- failure/cleanup/reset behavior and retained hard boundaries; and
- the concrete SelfTest host, driver, expected post-state, neutral/edge cases, and structured proof
  pattern.

SPEC continues to name behavior in game terms and cite the selected support route. Do not make a
user or generated project copy API inventories, C# signatures, or audit tables into SPEC.

New combinations of supported effects may use ordinary code composition even when no old example
matches the combination. Author must preserve each component's lifecycle, ordering, player-facing
semantics, and independent SelfTest assertions instead of lowering the combination to the nearest
old sample.

### Part 3 - Keep Preflight Thin

Review each newly identified hard boundary against all three preflight admission criteria:

1. the fact is mechanically exact;
2. C# compilation and existing Build checks cannot detect it; and
3. violating it would produce unsupported, unreachable, or silently ineffective code.

Only a rule satisfying all three may extend `capability_preflight.py`. Expected candidates are
route existence, hook/callback capability existence, owner/surface dispatch reachability,
route-owned callback rejection, and exact declaration shape where the wrong shape can silently
miss dispatch.

Keep ordinary fields, API parameter/type errors, manifests, resources, localization files,
runtime state/lifecycle, visuals, input behavior, and evidence status out of preflight. Recipes
guide those facts; compiler/Build, Tier 2, and headed review prove them.

Every added preflight rule requires positive, negative, payload-layout, and neutered-check evidence
showing the rejection would disappear if the rule were removed. If no new rule clears the three
criteria, do not change the checker.

### Part 4 - Prove Requirement-To-Code And Autotest Readiness

Developer tests must emphasize behavior and artifacts rather than document formatting:

- add a small set of representative natural-language requirement/SPEC scenarios spanning
  materially different effect lifecycles and compositions;
- prove each SPEC selects real shipped routes and exposes sufficient Author ingredients for code,
  localization/player-facing semantics, and SelfTest;
- use focused reference-only C# compile fixtures where exact public API compatibility is the risk;
- retain hook/callback reachability and catalog/profile checks;
- test SelfTest and log-verifier behavior for exact structured post-state, neutral/edge cases,
  command-queue completion, terminal outcomes, and rejection of fired/used-only evidence; and
- preserve all existing scaffold, Build, localization, art, packaging, vanilla, and payload tests.

Do not add one prose snapshot per capability. Group tests by materially different lifecycle,
dispatch, ordering, state, or presentation risk. A recipe paragraph existing is not proof; a test
must protect authorability, compilation, generated artifacts, or runtime-verification machinery.

If the human lead separately authorizes real-host proof during M8.8, use the smallest
representative generated Mod(s) needed to exercise genuinely new lifecycle classes. Run Build,
Tier 1, and structured Tier 2 in real STS2 and record only the exact shapes observed. Do not claim
unselected capabilities or infer a family-wide gameplay result. Without that separate
authorization, label every new shape game-unobserved and leave M8.6's final installed acceptance
untouched.

### Part 5 - Source And Payload Delivery

Before delivery, run the full surviving source suite, focused new behavior/compile cases, both skill
validators, Python `compileall`, retired-workflow residual scans, and `git diff --check`. Confirm
that M8.7 owner knowledge and capability graph rows remain present.

After explicit payload authorization, regenerate plugin and portable payloads only through
`publish.sh`, then verify:

- a second publish is byte-repeatable;
- shared plugin/portable trees have exact path/hash parity;
- payload tool layout works from the shipped directory shape;
- the payload contains only the thin preflight, not retired or replacement management validators;
  and
- no installed plugin or user Mod was modified in place.

### Close Criteria

M8.8 may be proposed for human closure only when:

- the refreshed `0.5.11` guide/source/API/Compat audit accounts for the complete selected effect
  surface;
- every current-profile player-visible effect has concise shipped recipe/reference ownership or a
  concrete retained product boundary;
- representative requirement-to-authoring, API compatibility, capability reachability, and
  SelfTest-verifier tests pass;
- the sole preflight remains within its three admission criteria;
- existing M8.7 abilities and hard boundaries are preserved;
- active docs and both generated payloads are synchronized and repeatable;
- the result record distinguishes framework-expressible, open-mod-authorable, and game-observed
  facts and lists every unrun Build/Tier/headed path literally; and
- the human lead explicitly accepts `documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`
  and closes the Package.

M8.8 closure does not itself start M8.6.

## M8.6 Waiting Gate

M8.6 is the only planned fresh natural-language full-pipeline acceptance. It remains unstarted.
When eventually selected, its execution contract must name the request, clean installed source,
host platform, success criteria, cleanup ownership, and literal evidence boundaries.

It also owns the two real-host proofs deferred from M8.2:

- one custom content element declaring an incoming-damage multiplier, including the guarded value,
  neutral case, and matching rules-text number; and
- one collection edit that proves both its intended entry and preservation of unrelated entries.

Human review owns design quality, comprehension, enjoyment, tuning, visual presentation,
controller behavior, and animation. Tier 1 and Tier 2 retain their exact technical meanings.

## Verification Policy

For source maintenance, use tests proportional to the changed surface. Preserve scaffold/build,
profile, manifest, localization, art, catalog, packaging, payload layout, capability reachability,
vanilla route, and launch/log/autotest reliability coverage. Prefer a small behavior-level scenario
over tests that only freeze prose or Markdown structure.

Source delivery requires:

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

When payload regeneration is authorized, run both publish modes and verify repeatability,
source/payload parity, and payload tool layout. Payload checks are not install, game, Tier 1,
Tier 2, macOS, or gameplay proof.

For generated Mods:

- Build proves compilation and static packaging/profile contracts.
- Tier 1 proves the exact load marker and no fresh error block.
- Tier 2 proves a structured post-state assertion in a real STS2 host plus `selftest done`.
- `played`/`fired`/`used` logs are diagnostics only.
- Headed review proves only the concrete visual/UI/controller/animation observations a human
  actually reports.
- Final reporting states every run, failure, exception, fallback, and unrun check directly.

## Closed Work And Future Outlook

Closed Package details stay in `documents/history/` and must not return as per-Mod workflow
ceremony. The active plan carries only current status, prerequisites, and the next authorized work
boundary.

Future interests such as multiplayer vanilla overrides, unsupported presentation hosts, broader
effect composability, and process-tree cleanup remain separate work until explicitly selected and
grounded. They do not silently widen the current product or acceptance scope.
