# STS2 verification ownership

This directory owns the current support graph and the evidence rules for generated Mods.
Completed milestone evidence remains under `documents/history/`; it is not a live workflow or a
substitute for current verification.

## Model

Support, implementation, and proof are distinct:

- the pinned RitsuLib/public-fixed route establishes what the product can express;
- recipes/references and generation code establish what open-mod can author;
- Build proves compilation and static artifact contracts; and
- the real STS2 host proves runtime behavior and presentation.

Missing proof remains visible but does not automatically narrow a documented public capability.
Conversely, source, unit tests, or successful Build do not establish game observation.

The maintained workflow is:

```text
request -> DESIGN -> SPEC -> thin capability preflight -> Author + SelfTest
        -> Build -> Tier 1 -> Tier 2 -> optional headed review -> direct report
```

There are no current coherence, deliverable, settlement, repair-routing, surface-envelope, or
cross-file ID ledgers. Do not recreate unit tests that merely validate those retired management
structures or exact prose.

## Source Test Ownership

The source suite under `games/sts2/tools/tests/` keeps coverage that protects real product
behavior and artifacts:

- scaffold, local runtime resolution, Compat/profile identity, manifests, and build inputs;
- localization table/key/token parity and nonempty bilingual values;
- PCK/resource packaging and deterministic art normalization/catalog projection;
- model-hook catalog extraction, capability existence, declaration shape, route ownership, and
  dispatch reachability;
- the thin capability preflight in repository and published payload layouts;
- vanilla target catalogs, exact public/fixed route manifests, generated sources, and focused
  reference-only compilation where maintained;
- launch/log parsing, Tier 1 markers, structured Tier 2 proof filtering, and terminal outcomes;
- current payload contents/layout and source-to-payload parity; and
- modest behavior-level request/SPEC-to-authoring scenarios.

`test_requirement_to_authoring.py` uses a concrete simple Card request. It verifies that its
implementable SPEC selects a real route, passes the actual preflight, and that the selected route
contains the RitsuLib template, registration, damage, upgrade, localization, and SelfTest
ingredients needed to author it. It is intentionally not a Markdown-schema snapshot and does not
pretend the model-driven Author stage is a deterministic compiler.

`test_capability_preflight.py` owns the only pre-Author machine gate. It proves:

- real recipe/reference paths resolve;
- nonexistent paths fail;
- Markdown anchors are not treated as capability identities;
- known reachable hooks pass;
- unknown or unreachable hooks fail;
- declared hook shape matches the pinned catalog;
- route-owned hooks are rejected as raw participation; and
- the cited route actually declares the hook.

`test_payload_tool_layout.py` runs the same checker from the shipped payload directory shape,
where tools move under `modmaker/scripts/`. This guards a real deployment difference rather than
documentation organization.

`test_model_hook_catalog.py` and `test_m82_hook_participation.py` keep the generated pinned catalog
and authorable declaration set aligned. The load-bearing rule is reachability: an override on a
surface outside the dispatcher's listener set can compile and never fire.

`test_m72_native_grammar.py` protects pinned Character starter facts and grounding limits. It does
not claim a generated Character, balance, or gameplay result.

The art, vanilla override, scaffold/build, profile, localization, and verification-tool suites
retain their existing technical ownership. Historical Package-specific proof detail is indexed in
`documents/history/README.md` and must not be copied back into the live unit-test contract.

## Generated-Mod Verification

Use deterministic local assertions for pure calculations, state transitions, payment floors,
capacity, ordering, and reset behavior. Runtime claims require the nearest real host.

### Build

```powershell
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
```

Build owns C# compilation, pinned local references, manifests, resource paths, bilingual static
localization, PCK/package output, and deployment artifacts. Build success is not a load or behavior
result.

### Tier 1

```powershell
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
```

Tier 1 requires the exact `[T2MOD-SELFTEST] <ModName> loaded ok` marker with
`framework=RitsuLib`, actual framework version `>=0.5.11`, exact `host=0.107.1`, exact
`compat=0.107.1`, and no fresh error/exception block. It proves install/load/registration only.

### Tier 2 / SelfTest

```powershell
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured state proof>"
```

Tier 2 requires the generated arg-gated `SelfTest.cs` to drive the real source interaction in the
closest maintained host, wait for the command queue, assert exact post-state/object identities,
emit a matching structured `state proof:`, and finish with `selftest done`. The verifier applies
the requested pattern only to structured proof lines.

A `played`, `fired`, or `used` line can locate a failure but can never establish a pass. A model
mutation outside the host, preview-only value, resource path, Build success, screenshot, or
terminal marker without state proof is also insufficient.

Stateful effects include their declared boundary/reset/persistence cases before the terminal
marker. Collection edits prove unrelated entries survive. Bilingual Mods switch through `eng` and
`zhs`, resolve real consumers, compare exact text/tokens, and restore the original language.

Run only one armed harness Mod at a time because `--t2selftest` arms every loaded harness. Preserve
and restore unrelated user Mods.

### Headed Review

Use headed review only for things structured state cannot prove: real images and layout, mouse and
controller interaction, animation, audio, readability, and subjective experience. Report only
what a human actually observed. A screenshot does not replace behavior assertions, and Tier 2 does
not replace presentation review.

## Host Ownership

| Host | Typical ownership |
|---|---|
| `CombatPlayer` | Cards, Relics, Potions, Powers, Orbs, Enchantments, targeting, computed values, piles, state, resources, and combat cues |
| `CombatEnemy` | Monster/Encounter rosters, HP ranges, moves, intent truth, and combat body behavior |
| `MapNode` / Event | Event pages/options/outcomes, presentation, forced follow-ups, and Ancient dialogue |
| real Rest Site | Card/Relic option absence, gray/payment/outcome/stay/repeat/icon behavior |
| `RunStart` / Character | Foundation fields, starters/pools, static Character consumers, resources, and run/combat reset behavior |
| `ModelDb` and localization host | pinned vanilla identity/catalog, aliases, availability, and exact model composition |
| nearest native visual consumer | actual Card/Relic/Power/Potion/Orb/Event/Encounter/etc. asset provider behavior |

Use one representative real host for a shared lifecycle. Add separate scenarios only for materially
different lifecycle, state, input, or presentation risk.

## Reporting

Finalize reports directly from actual results:

- **Built:** artifact path only when Build passed.
- **Tier 1:** exact marker/profile and fresh-error outcome, or failed/unrun.
- **Tier 2:** real host and concrete post-state assertion, or failed/unreachable/unrun.
- **Headed review:** only concrete observations actually reported by a person.
- **Not included:** explicit DESIGN `Not Now` items or accepted placeholders relevant to the ask.

Historical waivers and skipped checks remain literal exceptions. Do not reinterpret a closed
Package's manual review, Build, or older framework result as a current Tier 1/Tier 2 pass.

## Developer Commands

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills
git diff --check
```

When payload regeneration is explicitly authorized, run both `publish.sh --plugin` and
`publish.sh --portable`, repeat them to establish determinism, and run source/payload parity plus
payload-layout tests. These checks do not install the plugin or run the game.

Completed acceptance evidence is immutable. Future behavior changes still require proportional
current verification; an earlier result is not a blanket regression pass.
