# Implementation plan: M8 end-to-end product integrity

## Status

M8 is the active milestone. M8.0-M8.3 and M8.5 are closed; their implementation detail and
exceptions belong in `documents/history/`. M8.4 was removed by the human lead.

M8.7 Product Boundary Generalization is implemented in authoritative source and both payload
forms. Its result record and explicit human closure remain outstanding, so it is implemented but
open. Do not re-execute, reimplement, or narrow it.

M8.8 Surface Effect Composability Generalization completed its full capability inventory and
ownership-confirmation gate on 2026-08-13 and implemented WP1-WP5. The human lead deferred
Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, WP6 asset/scene/
animation/audio and shared-presentation expansion, and WP7 named typed interoperability. New
interactions whose purpose is to connect included capabilities to any deferred group are deferred
with it. WP8 source/static closeout and authorized plugin/portable payload delivery are complete;
real-host verification retains its separate authorization gate. The human lead accepted the final
result and closed M8.8 on 2026-08-13. The durable record is
`documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`. Existing asset, presentation,
audio, and interoperability routes must be preserved at their current literal boundaries.

M8.6 is the final clean installed whole-skill acceptance. It intentionally follows M8.7 and M8.8
despite its number. M8.8 is closed, but M8.6 remains ineligible while M8.7 is open and has no
executable contract until the human lead selects the exact request and host.

Current order and gate:

1. M8.8: closed by explicit human-lead acceptance on 2026-08-13.
2. M8.7: implemented and open; result record and explicit closure remain.
3. M8.6: waiting for M8.7 closure and explicit selection.

## New-Session Start Protocol

1. Read root `AGENTS.md`, `documents/PROJECT.md`, `documents/BASELINE_RESEARCH.md`, this file,
   `games/sts2/tests/README.md`, and `games/sts2/tests/content-capability-graph.md`.
2. Treat `documents/history/` as immutable evidence, never as current instruction.
3. Check `git status` before editing and preserve unrelated dirty/untracked work.
4. A plan entry is not execution authorization. Do not restart closed M8.8 or start M8.6 while
   M8.7 remains open or before its execution contract is explicitly selected.
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
| M8.8 - surface effect composability | Closed 2026-08-13 | `documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`; newly generalized shapes remain game-unobserved |
| M8.6 - clean installed whole-skill acceptance | Waiting | Eligible only after M8.7 closes and the human lead selects its contract |

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

### Closed Scope And Authorization Boundary

M8.8's complete capability inventory and ownership proposal were reported to the human lead on
2026-08-13. The human lead confirmed the revised scope, authorized implementation and payload
delivery in separate steps, then accepted the final result and closed M8.8 the same day. Closure did
not authorize a generated proof project, installation, game launch, Tier 1/Tier 2, headed review,
commit, push, publication, release, or M8.6.

The required first phase was research and plan confirmation:

1. refresh the official RitsuLib guide navigation, public `v0.5.11` source/API, and
   `STS2.RitsuLib.Compat.0.107.1` metadata;
2. inventory the complete documented and public capability surface using the default-inclusion rule
   in Part 1, not only APIs already represented by open-mod;
3. compare the refreshed facts with this plan, every current open-mod surface, and the current
   capability graph;
4. report changed assumptions, proposed new surfaces, exclusions, and concrete retained boundaries;
   and
5. obtain explicit human-lead confirmation of the resulting implementation scope before editing
   authoritative capability source.

All five steps are complete. The confirmed implementation excludes Progression, post-run Badge,
Settings, Telemetry, Multiplayer, and Update Check as product families. A later explicit human-lead
decision also defers WP6 asset/scene/animation/audio and shared-presentation expansion and WP7 named
typed interoperability in full. M8.8 excludes new recipes, implementation, tests, or compositions
whose purpose is to connect an included family to any deferred group. Preserve independently useful
behavior and all M8.7 capabilities: in particular, this decision does not remove existing asset,
presentation, audio, or interoperability routes, M8.7's availability/epoch routes, or RitsuLib Extra
Badges on Power, Relic, and Intent. All deferred groups remain future interests, not M8.8 closure
work.

M8.7 remains a preservation baseline. M8.8 may reuse and compose its nine generalized families but
must not reimplement, narrow, or relabel them. M8.8 does not start M8.6.

### Goal

Make every documented or public capability exposed by the pinned RitsuLib `0.5.11` profile that can
reasonably serve a generated Mod and remains inside the final confirmed M8.8 product scope usable
through open-mod's normal human-readable SPEC and Author workflow. The final scope is WP1-WP5:
gameplay behavior and composition, lifecycle/state/RNG, the accepted content-model and world
surfaces, Reward/Card Pile, and Runtime UI. It preserves but does not generalize the pre-existing
asset, presentation, audio, and interoperability boundary.

Inclusion is the default. A capability is not excluded merely because it is difficult, lacks an old
recipe or proof Mod, needs a new surface, or requires headed verification. Exclude it only when the
audit establishes that it is framework-internal/maintainer infrastructure with no reasonable
generated-Mod use, requires a forbidden mechanism or unavailable lifecycle value, or falls outside
an explicit product decision accepted by the human lead. Record the smallest concrete reason.

The six initially deferred families plus WP6 and WP7 are the explicit product-decision exceptions
to default inclusion. Their public APIs remain accounted for in the inventory, but M8.8 does not
newly make them open-mod-authorable and does not add integration points for them to otherwise
included surfaces. Existing open-mod authoring routes in those domains remain unchanged.

The resulting workflow remains:

```text
human intent
  -> implementable SPEC behavior and Autotest scenarios
  -> shipped recipe/reference route
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
- author Progression, post-run Badge, Settings, Telemetry, Multiplayer, or Update Check, or add new
  interactions between included families and any of those deferred families;
- generalize assets, scenes, animation, audio, shared presentation, or named typed interoperability,
  or add new interactions whose purpose is to use either deferred WP6/WP7 capability group;
- remove, narrow, or relabel any asset, presentation, audio, or interoperability route that already
  existed before this scope decision or was implemented by WP1-WP5;
- invent registration paths, arbitrary UI/VFX hosts, multiplayer claims, cross-Mod coordination,
  or external runtime dependencies that are not grounded in the pinned public profile;
- generate prompt-derived Harmony, reflection, Publicizer, IL, or private/internal access; or
- treat Build, source tests, a hook-fired log, or previous-version evidence as current gameplay
  proof.

New open-mod surfaces are allowed when a public capability represents a distinct user-requestable
product family or has ownership, lifecycle, routing, or verification needs that would be misleading
inside an existing surface. A new surface must use a grounded public/fixed registration route and
ship its own concise routing, SPEC, recipe/reference, and verification ownership; permission to add
a surface is not permission to invent a runtime API.

Ordinary C#/BCL, public STS2 `0.107.1` and RitsuLib Compat `0.5.11` APIs, Mod-owned helpers and
state, and existing maintained fixed Adapters remain valid implementation tools. A capability or
composition blocks only when it requires a capability absent from the pinned profile, a value
unavailable in a legal lifecycle, a forbidden mechanism, or an explicitly retained product
boundary. Record the smallest concrete boundary.

### Part 1 - Inventory The Complete Mod-Authoring Capability Surface

Use the complete official RitsuLib documentation navigation as the discovery index, then verify
exact symbols and lifecycle behavior against public `v0.5.11` source/API and the pinned
`STS2.RitsuLib.Compat.0.107.1` metadata. Inventory documented features and public APIs even when
open-mod has no current recipe, proof Mod, surface, or historical request for them.

The inventory must cover at least:

- every official RitsuLib tutorial and current guide area;
- public `RitsuLibFramework` entry points, content-pack/registry methods, templates, attributes,
  interfaces, commands, callbacks, lifecycle events, helpers, and compatibility-specific members;
- content behavior, combat hooks and commands, targeting, state, resources, card movement/costs,
  rewards, interactions, UI/presentation, localization, audio, persistence/run data/RNG,
  scenes/assets, and supported interoperability;
- the deferred Progression, post-run Badge, Settings, Telemetry, Multiplayer, and Update Check API
  families, solely to account for their public boundary and prevent accidental partial inclusion;
- public APIs called out by the official docs as present but not yet explained in a dedicated
  article; and
- the current open-mod capability graph, known limitations, fixed Adapters, and M8.7 preservation
  baseline.

Keep this as a concise maintainer research record organized by official documentation/source area.
It may list coverage, proposed owners, and unresolved questions, but it is not a generated-project
contract, permanent API ledger, surface schema, or one-row-per-symbol proof matrix.

Apply a default-inclusion rule. For every documented feature and relevant public API family, record
one plain-language outcome:

- author through an existing open-mod surface;
- author through a shared cross-surface recipe/reference;
- create a new open-mod surface with a grounded public/fixed route;
- retain a concrete temporary or permanent product boundary; or
- exclude framework-internal, maintainer, diagnostic-service, or other infrastructure that has no
  reasonable generated-Mod use, with the exact reason.

The inventory is complete only when every official documentation area and relevant public API area
is accounted for, every exclusion has a concrete reason, proposed new surfaces are visible for
human review, and capabilities absent from older open-mod recipes/proofs are included so the work
is not circular.

### Part 2 - Resolve Ownership Across Existing And New Surfaces

Map the inventory against every current `skills/modmaker/surfaces/*.md` owner: Card, Character,
Enchantment, Event, Keyword, Monster/Encounter, Orb, Potion, Power, and Relic. Review their recipes
and all shared references that already express or constrain behavior, including model-hook
participation, targeting, computed values, state, resources, Rest Site, Event outcomes, vanilla
composition, localization, presentation, and SelfTest guidance.

Prefer an existing surface when it truthfully owns the user's request. Prefer one shared reference
when several surfaces use the same lifecycle or API. Propose a new surface when the capability is
independently requestable and an existing surface would hide or misstate its registration,
lifecycle, presentation, or verification contract. Each proposal must name its user-facing purpose,
public/fixed route, SPEC vocabulary, related owners, hard boundaries, and nearest proof host.

This ownership pass is complete only when every included capability has an existing shared owner or
an explicitly accepted new-surface proposal. The accepted new surfaces are Act, Affliction,
Modifier, Ancient, Reward, Card Pile, Runtime UI, Global Effect, and Rest Site. Do not use a generic
utility page to hide unresolved ownership or route a deferred-family interaction through another
owner.

### Part 3 - Put Durable Knowledge In Recipes And References

Implement the confirmed result in the smallest coherent owner set. Prefer one shared reference for
knowledge used by several surfaces and keep owner-specific lifecycle, parameters, ordering, and
examples in the corresponding recipe/surface page. Do not duplicate the same capability catalog
across surfaces.

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

### Part 4 - Keep Preflight Thin

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

### Part 5 - Prove Requirement-To-Code And Autotest Readiness

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

### Part 6 - Source And Payload Delivery

Before delivery, run the full surviving source suite, focused new behavior/compile cases, both skill
validators, Python `compileall`, retired-workflow residual scans, and `git diff --check`. Confirm
that M8.7 owner knowledge, capability graph rows, and existing asset/presentation/audio/interop
routes remain present.

After explicit payload authorization, regenerate plugin and portable payloads only through
`publish.sh`, then verify:

- a second publish is byte-repeatable;
- shared plugin/portable trees have exact path/hash parity;
- payload tool layout works from the shipped directory shape;
- the payload contains only the thin preflight, not retired or replacement management validators;
  and
- no installed plugin or user Mod was modified in place.

### Close Criteria

M8.8 was eligible for human closure only when:

- the refreshed `0.5.11` guide/source/API/Compat inventory accounts for every documented feature
  and relevant public Mod-authoring API area;
- every included capability has concise shipped ownership through an existing or explicitly added
  surface/shared route, while every exclusion or retained boundary states its concrete reason;
- no Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, or new interaction
  with one of those families has entered M8.8 source, tests, generated payloads, or proof claims;
- no WP6 asset/scene/animation/audio/shared-presentation expansion, WP7 named typed interoperability
  expansion, or new interaction with either group has entered M8.8 source, tests, payloads, or proof
  claims, while all existing routes in those domains remain intact;
- representative requirement-to-authoring, API compatibility, capability reachability, and
  SelfTest-verifier tests pass;
- the sole preflight remains within its three admission criteria;
- existing M8.7 abilities and hard boundaries are preserved;
- active docs and both generated payloads are synchronized and repeatable;
- the result record distinguishes framework-expressible, open-mod-authorable, and game-observed
  facts and lists every unrun Build/Tier/headed path literally; and
- the human lead explicitly accepts `documents/history/M88_SURFACE_EFFECT_COMPOSABILITY_RESULTS.md`
  and closes the Package.

All criteria were satisfied within their literal evidence boundaries, and the human lead accepted
the result record and closed M8.8 on 2026-08-13. Closure did not itself start M8.6.

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

Future interests such as Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update
Check, full asset/scene/animation/audio/shared-presentation generalization, named typed
interoperability generalization, multiplayer vanilla overrides, unsupported presentation hosts, and
process-tree cleanup remain separate work until explicitly selected and grounded. Their new
cross-family integrations are future work as well. Existing capabilities are preserved, but these
interests do not silently widen the current product or acceptance scope.
