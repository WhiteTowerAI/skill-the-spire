# RitsuLib migration matrix

Status: R0 inventory frozen on 2026-07-22. This is the comparison matrix for the
project-wide migration from the historical BaseLib implementation to the pinned
RitsuLib target. Historical BaseLib evidence is regression input only.

## Environment pin

| Item | Frozen value | Evidence / implication |
|---|---|---|
| Git branch | `Henry's_cc` | Required working branch |
| STS2 host | stable `0.107.1` | `release_info.json` and branch both report `v0.107.1` |
| .NET SDK | `9.0.300` | Current verified toolchain |
| Python | `3.13.5` | Current local toolchain |
| Historical runtime | BaseLib `3.3.8` currently installed | Must be absent from the final dependency proof |
| RitsuLib source | clean tag `v0.4.62`, commit `e92b786...` | Research checkout under `baselines/STS2-RitsuLib` |
| Required compile asset | `STS2.RitsuLib.Compat.0.107.1.0.4.62.nupkg` | Do not select the default beta-facing package |
| Required runtime asset | `STS2.RitsuLib.Compat.0.107.1.0.4.62.github.zip` or pinned variant | Must expose the `0.107.1` DLL |
| Variant pack | SHA256 `3924ce9b60654e70cfed7f1a23b384f036e7f46deae3ea463a767dfe65d38040` | Contains `lib/0.107.1/STS2-RitsuLib.dll` and compat marker |
| Runtime manifest | RitsuLib `0.4.62`, `min_game_version: 0.107.1`, no dependencies | Generated mods depend on RitsuLib only |

At the R0 freeze, RitsuLib was not installed in the local NuGet cache or game Mods
directory and no headed proof existed. Gate R2 below records the later pinned install and
first headed proof without changing the frozen R0 facts.

## Migration matrix

| Surface / entry | Historical dependency to replace | RitsuLib public replacement | Open-mod-owned adapter | Nearest validation | Residual risk / phase |
|---|---|---|---|---|---|
| Semantic SPEC | Pool attributes, framework base names, hook names, framework-derived ids leaked into SPEC | Same framework-neutral envelope selects the pinned adapter | `semantic-contract.md`; adapter selection/diagnostic record | Contract test with simple Card + Relic | R1 gate; implementation not yet proven |
| Scaffold / project | Alchyr templates and historical package/MSBuild assumptions | Compat package `STS2.RitsuLib.Compat.0.107.1` | `scaffold.py` emits one pinned, open-mod-owned project | Empty mod load | **R2 complete**; content bases remain R3-R5 |
| Manifest / runtime dependency | BaseLib dependency and installed-version inference | RitsuLib manifest id/version with `min_game_version: 0.107.1` | One dependency/manifest generator and variant validator | Empty mod load with BaseLib absent | **R2 complete**; repeat negative audit at R7 |
| Build / packaging | Template PckPacker assumptions and historical DLL/PCK copy rules | Pinned compat DLL plus separately installed RitsuLib runtime | `ritsu_profile.py`; resource-only `pack_pck.py` route | Build tests + empty mod load | **R2 complete**; no framework DLL in consumer output |
| Diagnostics | Exact load/Tier-2 markers omit framework identity | Pinned framework/compat metadata | Shared build/load/Tier-2 diagnostic envelope | Verification-tool tests + empty mod load | **R2 complete**; each migrated suite must emit it |
| Card | Historical custom base + pool attribute registration | `ModCardTemplate`, content-pack Card registration | Translate availability, cost/type/target, scaling, upgrade, loc and fallback | `CombatPlayer` | **R3 Card complete**; `RITSU_CARD_PROOF_CARD_JOLT`, title `Jolt`, exact 6 damage, empty asset fallback |
| Relic | Historical custom base + pool attribute registration | `ModRelicTemplate`, content-pack Relic registration | Translate availability, rarity, trigger/state, loc and icon fallback | `CombatPlayer` | **R3 Relic complete**; `RITSU_CARD_PROOF_RELIC_BAUBLE`, title `Bauble`, turn-1 Energy `3 -> 4` |
| Potion | Historical custom base/pool and hand-authored image path | `ModPotionTemplate`, content-pack Potion registration | Usage/target/effect and one checked icon profile | `CombatPlayer` | **R3 complete**; `EmberDraft` exact damage `4`, localization resolved |
| Power | Historical custom model auto-registration and saved-property patterns | `ModPowerTemplate`, content-pack Power registration | Stack-domain enforcement, loc/SmartFormat and icon profile | `CombatPlayer` | **R3 complete**; `ChargePower` Counter `2 -> 3`, localization resolved |
| Keyword | Historical custom enum/registration and tooltip composition | RitsuLib keyword registry/manifest route | Keep behavior separate from text-only display | `CombatPlayer` | **R3 complete**; native membership and `Resonant` localization resolved |
| Enchantment | Historical custom model and attachment path | `ModEnchantmentTemplate`, enchantment registration | Host compatibility, persistent change, checked 64x64 icon | `CombatPlayer` | **R3 complete**; `Guarded` amount `5`, Block `7 -> 12` |
| Orb | Historical custom model and explicit Frost fallbacks | `ModOrbTemplate`, orb registration | Preserve separate passive/evoke behavior and icon/body/SFX fallbacks | `CombatPlayer` | **R3 complete**; capacity `1`, Block `0 -> 2 -> 7`, removed |
| Monster | Historical custom model/visual factory | `ModMonsterTemplate`, monster registration | Deterministic move vocabulary and checked static-body fallback | `CombatEnemy` | R4; bounds/intent/bestiary consumers must render |
| Encounter | Historical constructor registration and act validity | `ModEncounterTemplate`, act/global encounter registration | Pair with monster as one semantic slice | `CombatEnemy` | R4; spawn/group/act rules pending |
| Event core | Historical custom Event registration and nested loc behavior | `ModEventTemplate`, shared/act event registration | Page/option/outcome translator with one-combat-per-instance guard | `MapNode` / `CanaryEvent` | R4; exact layout/loc/room integration pending |
| Event presentation | Historical portrait hooks, normal option helpers, native consumers | `EventAssetProfile` and public game presentation APIs | Checked portrait fallback; bounded VFX/rich text/tips/lethal/acquisition/shake adapters only | `CanaryPresentation`, `CanaryNativePresentation` | R4; no custom layout/Ancient/arbitrary VFX promotion |
| Forced Event | Historical public hook implementation | Public game hooks through the selected registration path | One Quest Card, one target Event, one act, one completion option | `CanaryForcedEvent` | R4; solo only, no new save/multiplayer claim |
| Stateful mechanics | Historical saved properties and model hooks | `RunSavedDataStore` or public model/lifecycle APIs | Explicit owner/lifetime/reset/save mapping | Stateful `CombatPlayer` cadence | R5; save round-trip and second combat required |
| Character Foundation | Historical character template, constructor registration, pool attributes | `ModCharacterTemplate<...>`, character/starter registrations | Exactly-once registration, pools, starters, loc and Foundation fallback | `RunStart` + `CombatPlayer` | R4; selection/run flow must be re-grounded |
| Character static presentation | Historical template getters/factories and merchant prefix | `CharacterAssetProfile` plus public runtime factories where sufficient | Raw scene wrappers and exact versioned merchant adapter only if still needed | Wayfinder + `RestSite` + `Shop` | R4; each consumer needs visible proof; Ancient remains blocked |
| Combat resource | Historical combat state/payment/UI and one B-risk UI seam | Secondary-resource registry and commands | Preserve nonnegative all-or-nothing payment and fixed icon+text/text-only fallback | Wayfinder `CombatPlayer` two-combat suite | R5; do not replace native Energy |
| Ordered semantic buffer | Historical combat-scoped values/UI | Public game state/history plus normal Play -> Discard | Open-mod semantic state/output helper only | Wayfinder `CombatPlayer` two-combat suite | R5; retained-card CustomPile remains unsupported |
| Scry | Historical convenience API | No public RitsuLib equivalent in `0.4.62` | Future helper using native selection/pile commands | Focused visible selector suite | R6; zero/short/full, order, history, await, multiplayer restriction |
| Art pipeline | Historical framework paths/factories embedded in authoring | Per-surface RitsuLib asset profiles | `gen_sprite.py import` remains framework-neutral; adapter owns paths/fallbacks | Unit tests + each real visual consumer | R3-R5; build/path success is not visual proof |
| Self-test / repair | Historical generated model assumptions | Public game commands plus selected adapter | Same hosted scenarios and structured diagnostics | Existing tool tests then nearest live suite | R3-R7; framework marker never replaces state proof |
| Unsupported boundary | Temptation to equate framework breadth with support | No automatic promotion | Preserve explicit gaps centrally | Dependency/support audit | R7; vanilla editing, alt energy, zones, motion/materials/multiplayer/audio remain out |

## Source inventory classification

Active BaseLib/Alchyr references were found in approximately 39 source files, mainly
under `games/sts2/skills/modmaker/`, `games/sts2/skills/sts2-api/recipes/`, active
references, `games/sts2/tools/gen_sprite.py`, and the capability graph.

| Classification | Scope | Treatment |
|---|---|---|
| `replace` | scaffold, dependency/manifest/build logic, active runtime recipes | Replace with the single RitsuLib adapter path during R2-R5 |
| `rewrite` | semantic SPEC/author/verify/repair guidance, active references, capability graph, diagnostics wording | Move semantic intent out of framework code and route lazily |
| `research-only` | `documents/BASELINE_RESEARCH.md`, RitsuLib and Downfall checkouts | Keep for source/API comparison; never package |
| `historical` | `documents/history/**`, M0-M6 BaseLib evidence | Preserve unchanged as regression evidence |

Generated `plugins/open-mod/` and `skills/` payloads still mirror the source and must be
regenerated after source changes; they are never hand-edited.

## Gate R2 record - 2026-07-22

- Added one source-owned scaffold generator and one central profile validator under
  `games/sts2/tools/`; no Alchyr template or BaseLib fallback remains in the active
  scaffold/build path.
- The generated project pins `STS2.RitsuLib.Compat.0.107.1` `0.4.62`, disables
  `RitsuLibAutoCopy`, leaves `RitsuLibDeployDir` empty, and emits a manifest whose only
  dependency is `STS2-RitsuLib >= 0.4.62` with `min_game_version: 0.107.1`.
- The GitHub release NuGet container SHA256 is
  `7b3af1d38c5304a88401ff0abbca94c7d7f528b82536369f4d80cb361dcde297`; the signed public
  NuGet container differs, but both contain DLL SHA256
  `f3704cbab9280902bd1b1ae3c6e8ca311cd410ffb5a3446522c61102e4b5f8d0`, matching the
  installed variant-pack `lib/0.107.1` DLL.
- `D:/26summer_intern/r2-ritsu-empty` generated and built `RitsuEmpty` with zero warnings
  and zero errors. Its deployed directory contains only its DLL, manifest, and PDB.
- The final clean headed run loaded exactly `RitsuEmpty` and `STS2-RitsuLib`; BaseLib,
  Downfall, and the BaseLib-dependent user Mod were temporarily parked and restored to
  their exact original locations afterward. RitsuLib selected variant `0.107.1`, the load
  marker reported `frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1`, and Tier 1 passed
  with no fresh error block.
- Residual risk for R3: the variant loader logs a warning that direct assembly association
  was unavailable and uses its reflection bridge. The empty initializer works; content
  auto-registration still requires the first Card/Relic hosted proof.

## Gate R3 progress - Card and Relic slice - 2026-07-22

- The open-mod scaffold now exposes one optional partial `RegisterContent()` hook and one
  shared RitsuLib logger. Card and Relic authoring use that single content-pack boundary;
  neither model carries a pool attribute or a second registration path.
- The public-entry rule is re-grounded as normalized `MOD_CATEGORY_TYPENAME`, not the
  historical namespace prefix. Runtime registered `RITSU_CARD_PROOF_CARD_JOLT` and
  `RITSU_CARD_PROOF_RELIC_BAUBLE`; the packed `cards`/`relics` tables resolved `Jolt` and
  `Bauble` in the real models.
- The combined `RitsuCardProof` project built with zero warnings/errors and deployed only
  its DLL, manifest, PDB, and resource PCK. Its manifest depends only on
  `STS2-RitsuLib >= 0.4.62`.
- BaseLib, Downfall, the BaseLib-dependent user Mod, and the empty R2 Mod were parked for
  the final run. Exactly `RitsuCardProof` and `STS2-RitsuLib` loaded; the runtime selected
  compat `0.107.1`.
- Strict `CombatPlayer` Tier 2 passed independently for Card (`hp 28 -> 22`, damage `6`)
  and Relic (`energy=4` after `AfterSideTurnStart`, with trigger diagnostic `3 -> 4`).
  Both reached `selftest done`; no fresh error block was present.
- Gate R3 remains open for Potion, Power, Keyword, Enchantment, and Orb. The Card/Relic
  proof project is migration evidence, not a shipped runtime dependency.

## Gate R3 close - 2026-07-22

- The `RitsuCardProof` project now contains the complete low-risk R3 slice: Card, Relic,
  Potion, Power, Keyword, Enchantment, and Orb all register through one RitsuLib content
  pack and use no historical pool attributes or model bases.
- The final build completed with zero warnings and zero errors. Its manifest contains only
  `STS2-RitsuLib >= 0.4.62` and `min_game_version: 0.107.1`; the consumer output contains
  no framework DLL or PCK.
- One armed headed `CombatPlayer` harness loaded exactly `RitsuCardProof` and
  `STS2-RitsuLib` against the stable `0.107.1` host. Strict Tier 2 reached `selftest done`
  for all seven surfaces with no fresh error block. The structured markers were:
  `Card damage=6`, `Relic energy=3 -> 4`, `Potion damage=4`, `Power amount=2 -> 3`,
  `Keyword membership=true behaviorDamage=6`, `Enchantment amount=5 block=7 -> 12`, and
  `Orb channelCount=1 capacity=1 passiveBlock=0 -> 2 evokeBlock=2 -> 7 remaining=0`.
- R3 residual risk is limited to the documented presentation boundary: the Orb icon is not
  a custom combat body, and the migrated low-risk recipes do not promote animation,
  materials, multiplayer, audio, vanilla editing, or alternative Energy. R4 starts with
  monster/encounter, Event, and Character Foundation parity.

## Session handoff - 2026-07-22

- Stop point: immediately before R4 implementation. A read-only source/API entry search was
  performed, but no Monster, Encounter, Event, or Character migration source was changed.
- Verification close: 73 Python tests passed; compileall, source/proof/generated dependency
  audits, plugin/portable publication, and `git diff --check` passed after the final headed
  R3 run.
- Operational cleanup: all four temporarily parked user Mods were restored to their exact
  original locations. The disposable R3 project is not a runtime dependency or canonical
  hosted suite.
- Resume order: Monster + Encounter / `CombatEnemy`, Event / `MapNode`, then Character
  Foundation and static presentation. Do not begin M7.
