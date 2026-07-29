# M6.6 native Ancient dialogue focused results

Date: 2026-07-29

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, generated runtime
dependency `STS2-RitsuLib >= 0.4.62` only.

## Outcome

M6.6 Package 5 custom-Character dialogue in native Ancient scenes is pipeline-supported.
In the first headed proof, both Darv and The Architect stopped after their first visible
line. Static parser results did not prove that the localization PCK was mounted or that the
native scenes could initialize and complete.

The repair keeps every vanilla Ancient/Architect model, scene, background, layout, option,
reward, and progression route. Generated Mods still contribute only their own
Character-scoped localization groups through RitsuLib's registered population patch.
After the repair, the human lead observed Mod-local dialogue text and normal flow through
the rebuilt Darv and production Architect paths. The current-run log confirmed the mounted
PCK, pinned framework/host profile, both native routes, clean progression, and no fresh
error block. No structured post-state marker or `selftest done` appeared, so strict Tier 2
is an explicit verification exception rather than a pass. This promotion does not close
M6.6, start Package 1 or M6.7, or authorize a release.

## Product implementation

The generated-Mod pipeline now includes:

- semantic intake and SPEC fields for natural-language target, first/explicit/repeating
  visit rules, ordered Character/Ancient speakers and text, transition prompts, and
  Architect start/end attackers;
- a pinned STS2 `0.107.1` catalog for `DARV`, `NEOW`, `OROBAS`, `PAEL`, `TEZCATARA`,
  `NONUPEIPE`, `TANX`, `VAKUU`, and `THE_ARCHITECT`;
- flat `ancients.json` lowering through RitsuLib `0.4.62` without generated Harmony,
  reflection, IL, Publicizer, or a second injection patch;
- build preflight for Character IDs, contiguous group/line indexes, exactly one speaker,
  consistent repeat mode, exact `.next` placement, visit/attacker metadata, no line SFX,
  bounded balanced rich text, language-key parity, and complete Architect win coverage;
- compatibility with the legacy four-key repeating Architect group already emitted by
  Character Foundation; and
- a resource-manifest gate requiring `has_pck=true` exactly when generated localization,
  image, or scene resources exist;
- conditional registration of one Mod-local `CardRarity.Ancient` candidate when Darv
  dialogue is selected, preserving Darv's unchanged Dusty Tome option; and
- a focused-proof prerequisite requiring valid native Event-option text assets before
  headed review.

Every generated Character localization language must now include a complete production
Architect group in `ancients.json`. A global first-visit-ever Ancient introduction retains
native priority over the Character's first visit. `THE_ARCHITECT` remains a finale
`EventModel`; it is not entered through the normal `ancient` console command.

## Automated evidence

After repair, the automated source and delivery gate passed:

- the focused validator reports 18 dialogue groups across all nine targets;
- 22 focused build/Ancient-dialogue/semantic-contract tests and all 118 tools tests pass;
- 43 source/plugin/portable Python files compile;
- all six source/plugin/portable skill roots pass `quick_validate.py`;
- the plugin manifest, repo marketplace entry, and rendered runtime paths validate;
- two plugin/portable publishes each contain 147 shared files with zero path or content
  mismatch and the same aggregate SHA-256,
  `A8A47461E407A442465ED2D7FB2D73AE3D557E906D495AC062F26F1DCE560C59`;
- `git diff --check` reports no whitespace error; and
- the formal Release build reports `has_pck=true`, 18 groups, nine targets, the pinned
  `0.107.1` host, RitsuLib `0.4.62`, and zero build warning/error lines.

The earlier green source gate did not exercise PCK mounting, native Event-control asset
resolution, or Darv's Dusty Tome candidate and therefore was insufficient evidence for
promotion. The repaired automated gate is paired with the successful headed recheck below;
it does not manufacture the absent structured Tier 2 result.

## Focused host

The disposable `M66AncientProof` project used a playable RitsuLib Character named
`Wayfarer`, two Basic starter Cards, one starter Relic, typed Card/Relic/Potion pools, all
nine catalog targets, 18 dialogue groups, and 36 lines. A public RunStart parser sweep used
the real RitsuLib parser and checked native localization population, exact visit selection,
and Architect attacker metadata. A proof-only `ActEnteredEvent` driver deferred a real
`RunManager.Instance.EnterNextAct()` call to enter the production Architect finale.

The first proof manifest declared `has_pck=false` even though a PCK was packed and deployed.
RitsuLib therefore could not mount the authored `ancients.json`. The proof also used the
nonexistent `green` Energy asset prefix, which caused native Event-control resource errors,
and registered no Ancient Card for Darv's random Dusty Tome option. The repaired proof uses
`has_pck=true`, the native `silent` proof-only Energy assets, and a registered Mod-local
Ancient Block Card. The product build now rejects resource-manifest mismatch before MSBuild.

The repaired deployed artifacts are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `M66AncientProof.dll` | 19,968 | `19D687FB818F5A814AFA4724436AE03CF6050E1A3825E53682B3CB95CD7D57B0` |
| `M66AncientProof.json` | 365 | `E651CC78394260D9CD792C945E5E026A1DDE1DA7E1E6ADA4A5B5A4D7AD014A73` |
| `M66AncientProof.pck` | 8,488 | `C0DB0250B5ABFBA247A82B9D23A22627D501A8FD678301E4D6C1F9AF3C326B07` |
| `M66AncientProof.pdb` | 14,376 | `CEA2FA74C9EBB5131E3E0F340BB0CA8CD5956A7F08ECC8C40AED70DA50D1B579` |

After the headed result and current-run log evidence were recorded, the disposable
`D:\26summer_intern\m66-ancient-proof` project and deployed
`mods/M66AncientProof` directory were deleted. They are retired proof artifacts, not
maintained product sources or future regression hosts.

## Headed acceptance

The initial headed acceptance failed. The human lead observed that Wayfarer stopped after
the first visible line in both Darv and The Architect. The runtime log then exposed the
three proof defects recorded above. No native option restoration, Architect attack VFX, or
clean run completion is claimed from that run.

In the repaired recheck, the human lead reported that the visible dialogue was clearly the
Mod's authored text and that the flow was normal. The wording differed from the previously
listed first-visit examples because native visit/win state selected a repeating group; the
log later recorded Wayfarer's Darv count reaching three and four. This is expected
first/visit/repeat routing, not fallback or stale localization.

The still-running game's current `godot.log` provided the following corroboration:

- `M66AncientProof.pck` loaded before the exact RitsuLib `0.4.62`/host `0.107.1` marker;
- two `ancient darv` entries completed far enough to restore normal outcomes, including a
  native Card choice after the first entry;
- `act 3` entered the production `THE_ARCHITECT_EVENT_ENCOUNTER`, followed by the normal
  all-players-ready transition and run-progress updates; and
- `grep_log.py --mod-name M66AncientProof` found no fresh error block after Mod load.

The log does not encode the exact rendered line text or input device. The rendered text and
normal-flow claim is owned by the human lead's headed observation; no separate
input-device-specific trace was recorded. The log also contains neither the structured
Package 5 state proof nor `selftest done`; strict Tier 2 remains an explicit exception,
not a pass.

## Remaining boundary

Custom Ancient models, scenes, backgrounds, layouts, options/rewards, line audio, arbitrary
Ancient VFX, global dialogue replacement, multiplayer presentation, and debug missing-
Architect fallback remain unsupported. Historical proof does not replace proportional
regression testing after future source changes.
