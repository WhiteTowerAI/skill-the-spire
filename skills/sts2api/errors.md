# STS2 Mod error catalog

Match the exact signature, fix one cause, rebuild when code/resources changed, and rerun
only the failed verification stage. Never repair a generated project by adding BaseLib or
switching to an old template.

## Build And Profile

### Generated project is missing a local compile asset

- **Cause:** the bundled Godot SDK files, one local game DLL, or one of the five
  scaffold-pinned RitsuLib modules under `compat/0.107.1/` or `shared/` is missing; the
  project may also have reintroduced a framework `PackageReference`.
- **Fix:** regenerate with `scaffold.py`, restore the checked local host/runtime install,
  and retain `Sts2ApiCompat`, `RitsuLibAutoCopy=false`, local assembly references, and the
  single runtime manifest dependency. Do not add a NuGet framework package as a repair.

### Runtime asset does not contain the `0.107.1` compat variant

- **Cause:** RitsuLib is missing or older than 0.6.0 (variant manifest schema is not 2),
  another host variant was installed, only the root loader DLL was copied, or a module hash
  does not match `ritsulib-variants.manifest`.
- **Fix:** install the complete RitsuLib `>=0.6.7` folder with `compat/0.107.1/`, `shared/`,
  and `assets.zip`, preferably by subscribing to Workshop item `3747602295`. A release zip
  must be installed before it can compile a Mod.

### `local RitsuLib runtime ... differs from this project's pinned compile profile`

- **Cause:** the installed RitsuLib changed after scaffold, usually a Workshop auto-update.
- **Fix:** read the RitsuLib release notes between the two versions, then run
  `scaffold.py --repin-runtime` on the existing project (see `modmaker/scaffold.md`) and rerun
  Build, Tier 1, and Tier 2. Do not edit the pin by hand.

### `this project was scaffolded for the single-DLL RitsuLib runtime before 0.6.0`

- **Cause:** the project predates the RitsuLib 0.6 module split and references one DLL.
- **Fix:** scaffold a new project and move the authored sources, resources, and SPEC across.

### Host version is not `0.107.1`

- **Cause:** Steam updated/downgraded STS2 or the project points at another installation.
- **Fix:** use the supported stable host or stop and re-ground the profile before changing
  package versions.

### No `.pck` is produced

- **Cause:** resources are outside `<project>/<ModName>/`, or bare `dotnet build/publish`
  bypassed skill-the-spire's pack step.
- **Fix:** place resource files under the Mod resource tree and run
  `../modmaker/scripts/build.py`.

### `manifest has_pck must be <true|false>`

- **Cause:** the manifest boolean and the authored Mod resource tree disagree — resources
  exist with `has_pck: false`, or the tree is empty with `has_pck: true`.
- **Fix:** set the boolean to match the resource tree, then rebuild. Do not empty the tree to
  satisfy the flag.

### Deployed Mod contains a loose `.json` other than `mod_manifest.json`

- **Cause:** a build-time sidecar was copied into the deployed Mod. The game parses every
  `.json` under a Mod directory at any depth as a manifest and logs a load error for each one
  without an `id`.
- **Fix:** keep authored JSON inside the `.pck` and build-time inputs in the project
  directory. Any deployed non-manifest `.json` fails the build; delete it from the
  deployed Mod directory and rebuild.

### `[ancient-dialogue]` or an Ancient localization detail in a profile failure

- **Cause:** the generated flat dialogue table is structurally unsafe — wrong semantic
  group/key, non-contiguous line structure, `.next` on a terminal line, bad
  visit/repeat/Architect metadata, a new Mod-owned Ancient missing `.title`/`.epithet`/
  `.pages.INITIAL.description` or half of an option pair, or keys that differ across shipped
  languages.
- **Fix:** fix the reported semantic group/key. Never bypass the preflight and never enable
  the debug missing-Architect fallback to make it pass.

### `localization FAILED` with a language/table/key/token detail

- **Cause:** one of required `eng`/`zhs` is absent, the language trees contain different
  tables or keys, a value is empty, or a translation dropped or renamed a SmartFormat variable
  or a `:diff()`/`energyIcons()`/`starIcons()` value.
- **Fix:** regenerate both language tables from SPEC's bilingual text, preserving exact table
  names, keys, every variable, and every live-value token. Grammar formatters may differ:
  Chinese drops English `{X:plural:...}` branches. Do not copy English prose into `zhs` or
  weaken the validator.

### `[build] RitsuLib profile FAILED` with a `text style` / tag detail

- **Cause:** a localized value uses a tag vanilla never authors (`[color=...]`, `[wave]`), a tag
  parameter, or unbalanced/mis-nested tags. The game would show raw markup.
- **Fix:** use only the surface's vanilla tags from `reference/vanilla-text-style.md`, close
  each tag in reverse order, and keep tags out of titles.

### `[build] text style WARNING`

- **Cause:** a string drifts from vanilla style: an unhighlighted glossary term, an uncolored
  non-Card number, a colored Card `:diff()` number, several Card effects on one line, a Power
  `.description` that shows `{Amount}`, or Western punctuation/spaces in Chinese.
- **Fix:** read `<project>/.text-style.log`, correct each string in both languages per
  `reference/vanilla-text-style.md`, and rebuild. The Build still succeeds; record any
  deliberate exception in `MEMORY.md`.

### `[vanilla-overrides]` with a target/route/page/localization/fingerprint detail

- **Cause:** the override manifest, generated flow, or `events.json` drifted from the pinned
  catalog — unlisted operation, wrong baseline, same-Mod conflict, or a stale Adapter
  fingerprint.
- **Fix:** fix the named semantic operation or generated source. Never relax the catalog and
  never swap in a guessed patch target.

### MSB1008 when passing MSBuild properties

- **Cause:** `/p:Name=Value` was rewritten by the Windows shell/tool boundary.
- **Fix:** use `--property:Name=Value`, or use the normal pinned build wrapper without
  manual properties.

### CS0103 / CS0246 / CS0117 / CS1061 unknown API

- **Cause:** an API name or signature was guessed.
- **Fix:** use the exact recipe/reference signature. If the pack lacks it, report a pack
  gap rather than spending more repair attempts on guesses.

### CS8602 on `Owner.PlayerCombatState`

- **Cause:** the property is nullable outside combat.
- **Fix:** inside a proven combat hook, capture once with
  `var combat = Owner.PlayerCombatState!;`. Outside that boundary, guard null explicitly.

## Registration And Localization

### Model does not appear in ModelDb / registry

- **Cause:** the matching content-pack step is missing, registered twice through competing
  paths, or `.Apply()` was omitted.
- **Fix:** keep one matching `Mod*Template` registration in `RegisterContent()` and one
  final `.Apply()`.

### Visible title/description is blank or a raw key

- **Cause:** authored keys do not match the normalized public registration entry or are in
  the wrong table/resource tree.
- **Fix:** copy the exact public entry from registration diagnostics, use the recipe's
  table/shape, rebuild the PCK, and verify the real consumer.

### Custom art shows the fallback

- **Cause:** the file is missing/mis-sized, outside the packed tree, or the selected asset
  profile points at another path.
- **Fix:** run deterministic `gen_sprite.py import`, verify its destination, rebuild, and
  identify the custom resource in the real consumer. Do not remove the fallback.

## Behavior

### Combat-start Energy disappears

- **Cause:** Energy was granted before STS2's turn-1 reset.
- **Fix:** use the grounded side-turn-start hook, guard the owner/participant, and apply on
  player combat turn 1.

### Relic effect fires for the wrong player or every turn

- **Cause:** the hook omitted participant/owner and phase/turn guards.
- **Fix:** match the concrete owner and the semantic trigger boundary before mutating state.

### Counter goes negative after consume-up-to-N

- **Cause:** the requested amount was subtracted instead of the actual consumed amount.
- **Fix:** compute `consumed = min(current, requested)`, subtract it once, and assert the
  floor locally.

### Run cadence resets after combat or save/resume

- **Cause:** run-owned progress was stored in combat state or an unsaved field.
- **Fix:** use the concrete-Relic saved attached-state contract and its exact
  `SavedProperties.From`/`Fill` round trip.
- **Localize by the first failed boundary**, and fix that boundary rather than the effect's
  numeric Cmd:
  - wrong `N-1` progress → the advancing event, owner guard, or phase is wrong;
  - same-combat threshold passes but second-combat progress resets → `SavedAttachedState` is
    missing, or a combat-end hook cleared it;
  - a combat-local effect leaks into combat 2 → code duplicated the turn count instead of
    reading `PlayerCombatState.TurnNumber`;
  - a failed save round trip → the selected adapter's property type/holder or the run-save
    bridge is unsupported.

### Turn-N effect leaks across combats

- **Cause:** code duplicated a persistent turn counter.
- **Fix:** read native `PlayerCombatState.TurnNumber` for combat-local cadence.

### Resource payment rejects but payoff still fires

- **Cause:** caller did not await `SecondaryResourceCmd.Spend` or ignored its bool result.
- **Fix:** await spend and gate the payoff on success. Never maintain a duplicate amount.

### Resource/buffer UI is stale or overlaps Energy

- **Cause:** the public UI control was not refreshed after buffer-only mutation, or its
  offset/size changed.
- **Fix:** refresh the registered control and retain the 220x32 geometry at offset 160;
  verify disjoint global rects and the text fallback.
- **Localize a character resource by symptom:** a missing amount or reset points at the
  registered `SecondaryResourceDefinition` id or its persistence policy; a changed amount with
  stale UI points at `RegisterCombatUi` visibility/update or a missing explicit refresh after
  buffer-only mutation. Never add a duplicate integer and never add a UI
  postfix patch.

### Ordered buffer has stale Card views or leaks across combat

- **Cause:** source Cards were retained/skipped visually, Card instances were stored, or
  state used a non-combat owner.
- **Fix:** store semantic values in `AttachedState<PlayerCombatState,TState>` and let every
  source Card follow normal Play -> Discard.
- **Localize by symptom:** cross-combat leakage points at a non-combat key or a process-wide
  collection; wrong overflow means capacity was checked after mutation; stale or overlapping
  Card views mean source Cards were retained or skipped their native lifecycle — restore
  normal Play -> Discard instead of hiding visuals.

### Resumed Event starts a second special combat

- **Cause:** one mutable Event instance attempted another special combat.
- **Fix:** redesign the second branch as a noncombat outcome or use a fresh Event instance.

### Custom Orb logs missing channel audio

- **Cause:** a custom/default audio id was inferred without a registered asset.
- **Fix:** retain the verified Frost channel-SFX fallback until the audio track is opened.

### Character Shop cannot generate a valid rarity

- **Cause:** its pool lacks enough eligible non-Basic Attacks/Skills/Powers.
- **Fix:** meet the Character recipe's minimum Shop ecosystem before claiming Shop support.

## Verification

### Load marker missing but `RUNNING MODDED` is true

- **Cause:** initializer did not emit the exact marker, or the log window contains a stale
  run.
- **Fix:** keep the shared initializer marker, launch a fresh run, and use `grep_log.py`.

### Self-test fails before reaching its host

- **Cause:** navigation/timing/scene-tree setup failed.
- **Fix:** repair the harness setup or increase the bounded wait. Do not change gameplay to
  fit a navigation failure. Fall back to an honest Tier 1/manual report if needed.

### `selftest done` appears without the structured state proof

- **Cause:** the scenario completed but the required post-state was not established or the
  proof marker is wrong.
- **Fix:** use diagnostic trigger lines to localize source-vs-dependent behavior, repair the
  failed invariant, rebuild, and rerun Tier 2.

### Dev console will not open, or a debug grant says `Unable to create`

- **Cause:** debug commands exist only while the game is running modded
  (`ModManager.IsRunningModded()`, true whenever at least one gameplay Mod loaded), so a
  missing console means no Mod loaded. `Unable to create` instead means the console is live but
  the requested id did not resolve.
- **Fix:** confirm the Mod actually loaded by grepping the log for `RUNNING MODDED`, and open
  the console with `` ` `` (also `'`, `*`, `^`, `Shift+8`; `Esc` closes). For a failed grant,
  pass a unique substring of the id — `relic add` matches by uppercased `Contains`.
- A manual console observation never substitutes for the structured Tier 2 state proof. Report
  it as manually observed, and only when the user confirms the concrete result.

### Only a known unrelated shutdown/backup error appears

- **Cause:** STS2 emitted an existing non-target cleanup block.
- **Fix:** use the verifier's bounded ignore rule only when the block is byte-for-byte the
  known unrelated signature. Any fresh target-Mod error fails the run.
