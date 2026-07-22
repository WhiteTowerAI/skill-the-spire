# STS2 verification

This directory contains the **current** verification model and support graph. Completed
run transcripts and retired canary/audit documents live in `documents/history/`.

## Keep it lean

Do not require one canary project per capability.

1. Use lightweight contract checks for deterministic formulas and state rules.
2. Reuse the closest hosted live suite.
3. Keep a separate project when it is genuinely clearer or isolates a distinct host risk.
4. Treat fresh acceptance mods as disposable after evidence capture unless they become the
   canonical suite.

## Hosted suites

| Host | Current canonical coverage |
|---|---|
| `CombatPlayer` | basic content matrix, interaction, keyword card-text/no-icon tooltip, enchantment tab/tooltip icon, orb tooltip/flash icon plus fallback scene and behavior, cadence |
| `CombatEnemy` | encounter/move vocabulary plus static monster body in combat and bestiary |
| `MapNode` | Event Cmd/page/selection/reward outcomes, resumable and terminal special combat, normal initial/page portraits, bounded portrait-halo VFX, bounded native rich text, enabled typed option tips, normal relic-backed text/metadata, exact-lethal HP/Max HP warnings, native Card/relic acquisition presentation, `weak_short` screen shake, curated `trial_noble` VFX, bounded Quest Card -> forced Event follow-up, and cleanup/fallback presentation |
| `RunStart` / Character | Wayfinder selection/background, pools/starters, resource/UI, semantic route buffer, dynamic output, static combat/rest/merchant bodies, and five-layer full energy; locked/map and Ancient/Architect remain unverified |

RitsuLib migration checkpoint (2026-07-22): the `CombatPlayer` R3 proof rebuilt the Card,
Relic, Potion, Power, Keyword, Enchantment, and Orb functional contracts with only
RitsuLib `0.4.62` on stable STS2 `0.107.1`. Every surface reached strict Tier 2 plus
`selftest done` with no fresh error. Monster/Encounter, Event, and Character rows still use
their M0-M6 regression evidence until R4 reruns each host; do not describe those rows as
RitsuLib proof yet.

Wayfinder supersedes the isolated Foundation/resource/kernel composition path for current
character regression. The retired real-card `CustomPile` canary remains historical evidence
only; it does not represent player-facing support.

The 2026-07-21 Wayfinder tooling follow-up proved that generated Character authors need no
Godot/MegaDot install. `build.py` invoked the bundled raw-scene packer, then one headed run
rendered the exact 1920x1200 selection background, 512x512 rest and merchant bodies, and
five 256x256 energy layers in the native 128x128 counter. Static merchant also proved the
version-gated `NMerchantCharacter._Ready()` prefix and inherited fallback contract. The
full two-combat suite, RestSite, Shop, `selftest done`, and no-fresh-error checks all passed.

`CanaryEvent` was a disposable hosted acceptance mod. Its work directory and installed copy
were retired after the 2026-07-20 outcome/VFX/rich-text evidence was recorded. The `MapNode`
row above is the durable host contract, not a requirement to keep an armed mod installed;
recreate or extend an Event acceptance project only when the next candidate is ready.

`CanaryPresentation` was a disposable `CombatPlayer` + `MapNode` acceptance mod. Its 2026-07-20
headed run promoted native-presentation items 1-3: Card/standard-tip rich text, enabled typed
Event option tips with locked-tip suppression and normal relic-backed text/metadata, and
inclusive exact-lethal HP/Max HP warning glow. It was retired after the structured proofs,
`selftest done`, screenshots, and no-fresh-error checks were recorded.

`CanaryNativePresentation` was the disposable `MapNode` acceptance mod for items 4-6. Its
final 35-second headed run proved native Card/relic acquisition with exact `+1/+1` deltas,
the preference-respecting `weak_short` shake moving and returning at preference index 2,
the exact built-in `trial_noble` scene/host/position/inherited process mode, and complete
preview/VFX cleanup. Three settled screenshots, `selftest done`, and strict no-fresh-error
Tier 2 closed the remaining native-presentation pass on 2026-07-21.

`CanaryForcedEvent` was a disposable `MapNode` acceptance mod for the bounded solo
follow-up contract. Its one successful 37.5-second headed run proved no-token/wrong-act
pass-through, Unknown room forcing, target Event forcing/entry, a real visible option,
Quest token `1 -> 0`, restored hook outputs, `selftest done`, and no fresh error. Two prior
setup-only timeouts did not enter the Event and were resolved by reusing the established
map/room startup gate. The source and installed copy were retired after evidence capture;
the screenshot remains durable evidence.

## Proof rule

```text
setup -> enter real host -> drive real source -> observe post-state -> terminal
```

- Tier 1: exact load marker plus no fresh error block.
- Tier 2: structured state proof plus `selftest done`.
- A trigger/preview log or terminal marker alone never proves behavior.
- Custom presentation requires a player-visible invariant; model state alone is
  insufficient.
- Text-only presentation still requires headed evidence of every real consumer; it does
  not justify inventing a bitmap contract.

The direct M6 art follow-up reuses these same hosts. An art claim additionally requires the
exact packed resource/scene to render in the headed game, with a screenshot or equivalent
visual assertion that distinguishes it from the fallback. Build success and resource-path
logs alone do not prove art. Extend a hosted suite when practical; there is still no
one-project-per-art-type rule.

For Event screenshots, wait until option/page fades and combat room transitions settle.
Visible node existence is not enough; a blank page or near-black transition frame is not
acceptance evidence.
For rich text, wait for both description opacity and `VisibleRatio` to settle; assert the
required host effect types rather than an exact `CustomEffects` array length because the
real Event scene contributes one additional entry beyond `MegaRichTextLabel`'s own table.

Run only one armed harness mod at a time because `--t2selftest` arms every loaded harness.

## Commands

```bash
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> \
  --tier2-pattern "<structured state proof>"
```

Current capability claims are in `content-capability-graph.md`. Historical exact markers,
failures, and repair chronology are indexed by `documents/history/README.md`.
