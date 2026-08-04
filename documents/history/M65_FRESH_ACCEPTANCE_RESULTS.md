# M6.5 fresh Character acceptance results

## Outcome

On 2026-07-29, the human lead reported that the headed Prismwright acceptance completed
successfully and directed the one-off acceptance project to be retired. The lead explicitly
waived the remaining Tier 2/self-test harness rather than spending more time on it.

This closes M6.5 by an explicit lead acceptance decision. It is not a claim that every row
of the original automated gate ran: the exceptions below remain part of the result. This
decision does not start M7, another expansion track, or a GitHub release.

## Acceptance Mod

Prismwright was a fresh natural-language Character Mod generated against STS2 `0.107.1`,
RitsuLib `0.4.62`, and compat `0.107.1`. It exercised the promoted M6.5 composition:

- selection/background, top-panel main/outline, combat/rest/merchant bodies;
- five full-energy layers plus distinct large and text Energy icons;
- the structured card/UI theme and generated Relic main/outline pair;
- private non-Spine `Idle`/`Attack`/`Hit`/`Dead` combat cues.

The cue processor atomically produced 18 runtime frames: Idle 4, Attack 4, Hit 4, and Dead
6. The final Character bundle review retained Hit recoil as the highest-priority headed
check; the lead subsequently reported the headed acceptance completed successfully.

## Automated Evidence

The acceptance repairs and regenerated plugin/portable payloads passed 105 source unit
tests, source/plugin/portable Python compilation, key bundled-tool hash parity, and
`git diff --check`. The final Mod build completed with zero warnings and zero errors.

The deployed artifacts before retirement were:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `Prismwright.dll` | 32,256 | `6C5D923AD3B8B4914D6E3C862B05D7D8A1BCAF10F8DE04FA40B5110868D07672` |
| `Prismwright.pck` | 4,636,705 | `7983E684B004C063D9361E62ECE6E21102BA0AEB1B2837BB03BDDA933D070A79` |
| `Prismwright.json` | 404 | `AD57B890387794E0698950BF2BC19A45278C1DB8AB58416E2A89F6C0251CD5C0` |
| `Prismwright.pdb` | 17,680 | `DFAD856082D659D32A42DE715EF4ED06093BCFBF58DB9C34188C91D1B4E2F0BF` |

The headed run log contained the exact load marker and matching profile:

```text
[T2MOD-SELFTEST] Prismwright loaded ok framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1
```

It also recorded all ten deferred Character/content registrations before registration
froze.

## Accepted Exceptions

- No structured Tier 2 post-state marker or `selftest done` harness was authored or run.
- Strict `grep_log.py` returned failure because the game emitted RID, shader, ObjectDB,
  and resource-leak messages during engine shutdown after the successful load and headed
  session. No Prismwright-local exception was present in the inspected block, but this is
  not recorded as a strict no-fresh-error pass.
- No settled screenshot set is retained in the repository; headed presentation acceptance
  is the human lead's reported result.

## Retirement

After this evidence was captured, the disposable `m65-acceptance-project` workspace and
the deployed `mods/Prismwright` copy were removed. Maintained source, generated plugin and
portable payloads, focused host evidence, and this result remain; the acceptance project
must not be restored as a permanent fixture.
