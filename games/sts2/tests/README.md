# STS2 verification ownership

This directory owns the current support graph and generated-Mod verification rules.

## Model

Support, implementation, and observation are distinct:

- the pinned RitsuLib/public-fixed route establishes what the product can express;
- recipes, references, and generation code establish what Skill the Spire can author;
- Build proves compilation and static artifact contracts; and
- the real STS2 host proves runtime behavior and presentation.

Missing runtime observation does not automatically narrow a documented public capability.
Conversely, source, unit tests, or successful Build do not establish gameplay behavior.

```text
request -> DESIGN -> SPEC -> thin capability preflight -> Author + SelfTest
        -> Build -> Tier 1 -> Tier 2 -> headed review when needed -> direct report
```

## Source Test Ownership

The suite under `games/sts2/tools/tests/` protects product behavior and artifacts:

- scaffold, local runtime resolution, profile identity, manifests, and build inputs;
- localization table/key/token parity and nonempty bilingual values;
- resource packaging and deterministic art normalization/catalog projection;
- model-hook catalog extraction, declaration shape, route ownership, and dispatch reachability;
- capability preflight in repository and published payload layouts;
- vanilla target catalogs, fixed route manifests, generated sources, and focused compatibility;
- launch/log parsing, Tier 1 markers, structured Tier 2 filtering, and terminal outcomes;
- payload contents/layout and source-to-payload projection; and
- modest request/SPEC-to-authoring scenarios.

Do not add tests that only freeze prose, headings, development chronology, management schemas, or
historical evidence. A test must protect a supported authoring route, generated artifact, static
boundary, or real verification mechanism.

## Generated-Mod Verification

### Build

```powershell
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
```

Build owns C# compilation, pinned local references, manifests, resource paths, bilingual static
localization, PCK/package output, and deployment artifacts. Build success is not load or behavior.

### Tier 1

```powershell
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
```

Tier 1 requires the exact `[T2MOD-SELFTEST] <ModName> loaded ok` marker with
`framework=RitsuLib`, actual framework version `>=0.5.11`, exact `host=0.107.1`, exact
`compat=0.107.1`, and no fresh error/exception block.

### Tier 2 / SelfTest

```powershell
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured state>"
```

Tier 2 requires the arg-gated `SelfTest.cs` to drive the real interaction in the closest
maintained host, wait for the command queue, assert exact post-state/object identity, emit a
matching structured `state proof:`, and finish with `selftest done`.

A `played`, `fired`, or `used` line can locate a failure but cannot establish a pass. A model
mutation outside the host, preview-only value, resource path, Build success, screenshot, or
terminal marker without structured state is also insufficient.

Run only one armed harness Mod at a time because `--t2selftest` arms every loaded harness.
Preserve and restore unrelated user Mods.

### Headed Review

Use headed review only for things structured state cannot establish: images and layout,
mouse/controller interaction, animation, audio, readability, and subjective experience. Report
only what a person actually observed.

## Host Ownership

| Host | Typical ownership |
|---|---|
| `CombatPlayer` | Cards, Relics, Potions, Powers, Orbs, Enchantments, targeting, values, piles, state, resources, and combat cues |
| `CombatEnemy` | Monster/Encounter rosters, HP ranges, moves, intents, and combat bodies |
| `MapNode` / Event | Event pages/options/outcomes, presentation, forced follow-ups, and Ancient dialogue |
| real Rest Site | option absence, disable/payment/outcome/stay/repeat/icon behavior |
| `RunStart` / Character | Foundation fields, starters/pools, static consumers, resources, and reset behavior |
| `ModelDb` and localization host | pinned vanilla identity, aliases, availability, and composition |
| nearest native visual consumer | actual asset-provider behavior for the selected content family |

Use one representative host for a shared lifecycle. Add cases only for materially different
lifecycle, state, input, or presentation risk.

## Reporting

- **Built:** artifact path only when Build passed.
- **Tier 1:** exact marker/profile and fresh-error outcome, or failed/unrun.
- **Tier 2:** real host and concrete structured state assertion, or failed/unreachable/unrun.
- **Headed review:** only concrete observations actually reported by a person.
- **Not included:** relevant accepted `Not Now` items or placeholders.

## Developer Commands

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
python -m compileall -q games/sts2/tools scripts/publish
git diff --check
```

When payload regeneration is authorized, run both publisher modes twice and verify deterministic
trees, publisher-aware parity, and payload tool layout. Those checks do not install the plugin or
run the game.
