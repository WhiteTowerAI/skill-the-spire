# STS2 Mod error catalog

Match the exact signature, fix one cause, rebuild when code/resources changed, and rerun
only the failed verification stage. Never repair a generated project by adding BaseLib or
switching to an old template.

## Build And Profile

### Required compile asset is `STS2.RitsuLib.Compat.0.107.1 0.5.4`

- **Cause:** the project selected a floating/default RitsuLib package, another compat
  target, or an additional framework package.
- **Fix:** regenerate with `scaffold.py` or restore the exact pinned `PackageReference`,
  `Sts2ApiCompat`, `RitsuLibAutoCopy=false`, and single runtime manifest dependency.

### Runtime asset does not contain the `0.107.1` compat DLL/marker

- **Cause:** RitsuLib is missing, another host variant was installed, or its variant
  manifest/hash does not match.
- **Fix:** install RitsuLib `0.5.4` with `lib/0.107.1/STS2-RitsuLib.dll`; do not use
  `--skip-runtime-check` for Tier 1.

### Host version is not `0.107.1`

- **Cause:** Steam updated/downgraded STS2 or the project points at another installation.
- **Fix:** use the supported stable host or stop and re-ground the profile before changing
  package versions.

### No `.pck` is produced

- **Cause:** resources are outside `<project>/<ModName>/`, or bare `dotnet build/publish`
  bypassed open-mod's pack step.
- **Fix:** place resource files under the Mod resource tree and run
  `${GAME_TOOLS_DIR}/build.py`.

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

### Ordered buffer has stale Card views or leaks across combat

- **Cause:** source Cards were retained/skipped visually, Card instances were stored, or
  state used a non-combat owner.
- **Fix:** store semantic values in `AttachedState<PlayerCombatState,TState>` and let every
  source Card follow normal Play -> Discard.

### Scry overlay is missing, unawaited, or has wrong order/history

- **Cause:** an empty/no-op boundary was reached; selector command was not awaited; code
  iterated the selected set instead of the stable seen list; or discard history/hooks were
  omitted.
- **Fix:** follow `reference/scry-helper.md` exactly. Await selection and pile commands,
  filter the stable seen list, record normal history/hooks once, and reject multiplayer.

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

### Only a known unrelated shutdown/backup error appears

- **Cause:** STS2 emitted an existing non-target cleanup block.
- **Fix:** use the verifier's bounded ignore rule only when the block is byte-for-byte the
  known unrelated signature. Any fresh target-Mod error fails the run.
