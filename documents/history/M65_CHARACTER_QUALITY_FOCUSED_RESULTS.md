# M6.5 Character quality focused results

Dates: 2026-07-27 and 2026-07-28

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, generated runtime
dependency `STS2-RitsuLib >= 0.4.62` only.

This record covers the focused Character content-quality packages promoted before the
fresh natural-language acceptance gate. It does not close M6.5 as a whole.

## Character bundle, footprint, theme, and outlines

The disposable Meridian host work established the structured `CharacterArtBundle`,
role-based reference routing, deterministic review output, and the real-host footprint
contract without changing the existing 132x195 selection or 512x512 combat dimensions.
The normalized combat body used content box `(26,26)-(486,486)`, baseline `486`, public
`VisualNodeStyle` scale `0.80`, and position `(0,-184)`. The hosted screen bounds remained
inside the 1920x1080 viewport and clear of the named UI/enemy regions. The lead accepted
the settled selection and combat comparison.

The same hosted composition proved:

- four exact Character/card-pool colors and one cached deterministic frame material;
- distinct 256x256 large and 24x24 rich-text Energy icons in their real consumers;
- five 256x256 full-energy layers, with one Character layer and four fixed templates;
- deterministic opaque-white 3% alpha-derived top-icon and generated-Relic outlines;
- exact main/outline paths and visible layers in one real `NTopBarPortrait` and `NRelic`;
- static 512x512 RestSite and Shop bodies in `NRestSiteCharacter` and
  `NMerchantCharacter`.

Representative structured markers were:

```text
selection assets expected=portrait132x195/background1920x1200 observed=all
combat assets expected=body/top-icon-normal+outline/same-native-host observed=all
relic assets expected=main+outline256/same-NRelic/big256 observed=all
character theme expected=colors/frame/large-icon/text-icon observed=all
character foundation/static-presentation expected=selected-contract observed=all
selftest done
```

Strict Tier 2 and no-fresh-error checks passed. The lead's headed review accepted the
named color/frame/Energy consumers and top-icon/Relic outline presentation.

## Bounded non-Spine combat cues

`MeridianCueProof` used one private combat-only cue set with the promoted contract:

| cue | frames | frame time | result |
|---|---:|---:|---|
| Idle | 4 | 180 ms | loops |
| Attack | 4 | 90 ms | one shot, then Idle |
| Hit | 4 | 80 ms | one shot, then Idle |
| Dead | 6 | 140 ms | terminal final pose |

All frames shared the combat content box/baseline/style plus stable Bounds, Intent,
Center, Orb, and Talk anchors. Combat 1 proved Idle, Attack, Hit, and normal cleanup;
combat 2 proved that the prior playback node was freed before Dead reached and held its
sixth frame. The exact load/profile marker, strict Tier 2 marker, `selftest done`, and
no-fresh-error check passed:

```text
[T2MOD-SELFTEST] MeridianCueProof loaded ok framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1
[T2MOD-SELFTEST] MeridianCueProof state proof: framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1 character combat cues complete expected=Idle/Attack/Hit/Dead/cleanup observed=all
[T2MOD-SELFTEST] MeridianCueProof selftest done
```

The lead's headed review accepted all four visible actions and stable presentation.

## Missing-frame fallback

The separate fallback run omitted `Hit/03`. The all-or-nothing gate disabled every cue,
mounted the exact static 512x512 `combat.png`, and created no cue playback node. Strict
Tier 2 passed with no fresh target-Mod error:

```text
[T2MOD-SELFTEST] MeridianCueProof state proof: framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1 combat cue fallback expected=one-missing-disables-all/static-combat512/no-playback observed=all
[T2MOD-SELFTEST] MeridianCueProof selftest done
```

The lead watched the headed fallback checkpoint and confirmed that no surviving action
frame flashed.

## Runtime correction and production boundary

The proof found that `CharacterAssetProfile.VisualCues` is not combat-local: RitsuLib may
also consult it for merchant/rest playback, which can replace the checked static world
textures with combat frames. The promoted route therefore leaves that field unset and
passes a private complete cue set directly to `ModAnimStateMachines.StandardCue` from
`SetupCustomCombatAnimationStateMachine`.

Production acquisition uses four identity-referenced action sheets and deterministic
normalization. The processor applies magenta cleanup, connected-component/largest-subject
selection, grid splitting, shared cross-action scale, baseline alignment, edge/body-scale
QC, GIF/contact-sheet review, metadata, and atomic replacement. These processing techniques
are adapted from agent-sprite-forge under MIT. Proof frames are diagnostic and are not
shipped source assets.

The focused source gate passed 102 Python unit tests, relevant Python compilation, and
`git diff --check` before payload generation.

## Payload refresh

On 2026-07-28, both committed payloads were regenerated from `games/sts2/`:

- Codex plugin: `plugins/open-mod/skills/`;
- portable Agent Skills: `skills/`.

Each payload contains 21 `modmaker` files and 123 `sts2-api` files, including ten bundled
Python tools. `character_cues.py` and `reference/character-combat-cues.md` are present in
both outputs. A final second plugin+portable generation produced no size or SHA-256 change
across the 289 files in the two payload roots.

The final non-game gate passed:

- all six source/plugin/portable skill validations;
- Codex plugin manifest validation and repo marketplace structure checks;
- 102 Python unit tests and compilation of 40 source/test/payload Python files;
- no unrendered runtime path placeholders in either payload;
- exact plugin/portable `modmaker` and `sts2-api` tree parity;
- private combat-cue ownership, required cue files, and RitsuLib-only scaffold tests;
- `git diff --check` with no whitespace error.

## Promotion and remaining gate

The focused contracts are promoted in the source interview, semantic SPEC, authoring,
RitsuLib Character recipe/references, self-test guidance, and active capability graph.
Supported runtime output remains limited to private non-Spine Idle/Attack/Hit/Dead cues.
Cast, Spine, trails, animated merchant/rest bodies, production audio/materials,
multiplayer presentation, custom locked selection/map marker, and native custom-Character
Ancient presentation remain unsupported.

No fresh natural-language Character acceptance Mod was generated for this record. The
complete M6.5 acceptance gate, acceptance-project retirement, and any M6.5-complete claim
remain pending. This record does not authorize a release.
