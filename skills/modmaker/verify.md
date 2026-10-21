# Verify — prove the effect in the real game

Verify on observed reality, not "it compiled". Which check you actually reached is itself a
reported fact. Classify every difference through `repair.md` before fixing it, and never assume a
behavior difference is local when the cited shared route may be breaking its own contract.

## Tier 2: does the effect fire? (unattended, the headline)

The scaffold's kit (`SelfTestKit.cs`) and this Mod's `SelfTestScenarios.cs` are compiled in and
dormant. Launched with `--self-test`, the kit runs the roll call, drives itself from the main menu
into each hosted scenario, fires the effects, and asserts post-state, with no console typing or
human triggering:

```bash
python ../modmaker/scripts/launch.py --self-test --mod-name <ModName>
python ../modmaker/scripts/grep_log.py --mod-name <ModName> --tier2-pattern "kit summary passed=.* scope=all"
```

After a Build, go straight to Tier 2: the launch checks the Tier 1 load facts first and stops at
the main menu with the Tier 1 verdict when the Mod did not load. The launcher parks every other
harness Mod for the run and restores it afterwards (a second armed harness collides on the main
menu); never move user Mods by hand. It waits for the harness's logged budget plus boot time
(`--wait-seconds N` overrides), exits 0 only for `selftest done`, and closes the game so the grep
reads the fresh log.

The kit logs `state proof: kit summary passed=N/N scope=all` only when the roll call, every face
check, and every scenario passed, followed by `selftest done`. `grep_log.py` applies the pattern
only to structured `state proof:` lines, ignores every `played/fired/used` log, requires the exact
load marker and `selftest done`, and fails on any `FAILED` or fresh error block after the load
marker, even one that does not name the Mod. To inspect one SPEC invariant, match its own line
(`--tier2-pattern "lantern_combat_start_energy: .*observed=4"`).

While repairing, `--only` reruns just the named scenarios (a trailing `*` matches a prefix); the
run logs `scope=partial` and is never the Tier 2 you report:

```bash
python ../modmaker/scripts/launch.py --self-test --only "face.*,lantern_combat_start_energy" --mod-name <ModName>
```

Derive the checklist only from the variants the current SPEC selects, following each element
recipe's § Proof matrix and each selected reference's proof section. Registration, direct method
calls, model lookups, serialization, constructed Godot nodes, or a successful Build never prove
behavior.

**Bilingual text.** Build proves the static half (directories, table/key parity, nonempty values,
variable parity, markup, vanilla-style warnings). On every run the roll call switches through
`eng` and `zhs` with the public `SetLanguage` route, resolves every content model's strings
through its real consumer, rejects missing, empty, raw-key, and unresolved-placeholder values, and
restores the player's language; Event pages and Ancient dialogue are resolved by their own
scenarios. Translation quality, tone, clipping, and layout stay headed review.

### Read the outcome

| Launcher or harness result | Meaning and next step |
|---|---|
| `selftest done` with the matching state proof | **Tier 2 PASS**: the exact SPEC state was observed end to end. |
| `selftest done`, state proof absent | The scenario ran but no post-state assertion passed: a real behavior bug; classify in `repair.md`. |
| `selftest FAILED: state proof: <k> of <n> scenarios did not pass` | Those scenarios ran and an assertion failed or threw; the others still ran. Each `scenario FAILED:` line names expected and observed values, and `scenario trail:` lines show what the host did. Fix every independent failure before the next launch; a scenario that encoded SPEC wrongly is fixed per `repair.md`. |
| `selftest FAILED: timeout: ...` | A scenario ran out of its budget or stalled at the named step. Raise a long scenario's `budgetSeconds`, otherwise repair the stalled step; report it as a timeout. |
| `selftest FAILED: setup: ...` (or another stage) | The harness could not reach or drive the scenario (navigation, an unknown `--only` name, a scenario definition error). Not a Mod failure: repair the harness use, or fall back to the manual guide; otherwise report Tier 1 only. |
| `[launch] main menu reached without this Mod's load marker` | The Mod did not load; the Tier 1 verdict printed next names the load failure. |
| `[launch] main menu reached but the harness never armed` | `MainFile.cs` lost the `SelfTestKit.Arm` line; restore it with `scaffold.py --refresh-selftest-kit`. |
| `[launch] TIMEOUT` with no terminal marker | The launcher stopped waiting first; rerun with a larger `--wait-seconds`. It is not evidence about the Mod. |

Match each signature's cause and fix in `../sts2api/errors.md` § Verification, and
§ Behavior for a wrong observed value. A code or csproj fix reaches the game only through a fresh
Build.

## Tier 1: does it load? (diagnosis)

```bash
python ../modmaker/scripts/launch.py --mod-name <ModName>
```

It launches STS2 without Steam, waits for the main menu, closes the game, and prints the verdict;
never read or slice the log yourself. **PASS** is the exact `[T2MOD-SELFTEST] <ModName> loaded ok`
record carrying the pinned framework/host/compat profile with no error block after it. Its three
failures are distinct: a missing or mismatched **framework marker** is a profile/scaffold problem;
a **load marker NOT FOUND while `RUNNING MODDED` = YES** means the Mod loaded but emitted no marker;
a **fresh error/exception block** means registration or runtime threw. Match the signature in
`errors.md` § Verification and § Registration And Localization; never guess.

## Headed review

Structured state does not prove images, layout, mouse/controller input, animation, audio, or
feel. When SPEC selects one of those, run the headed checks in its owning reference (for example
`advanced-targeting.md`, `card-hand-emphasis.md`, `extra-corner-labels.md`, `rest-site-options.md`,
`art-contract.md`, `character-presentation.md`, `character-combat-cues.md`, `ancient-dialogue.md`,
`event-vfx.md`, `event-native-presentation.md`, or `forced-followup-event.md`).

Rendered text is also a headed observation: when the user reviews a Card, Relic, Potion, Power, or
Event, ask them to compare it with a similar vanilla one (gold terms, colored numbers, line breaks,
the tooltip list, and the Chinese text after switching language). Custom art stays unverified until
the real game visibly shows it, not the fallback, in every consumer its art page lists; never
infer it from a resource path or a `.pck` build. Give the user the exact build, dev-console
commands, and check matrix, and record their observations separately.

### Manual fallback (only when the harness could not reach or drive its scenario)

1. Start a run in STS2 (the Mod is loaded, as Tier 1 confirmed).
2. Open the **dev console** with **`` ` `` (backtick)** (also `'`, `*`, `^`, `Shift+8`); close with
   `Esc`. Debug commands are enabled because the game runs modded.
3. Grant and trigger the element as its recipe's § Manual fallback says. A Power, Keyword, or
   Enchantment is driven through its host Card, an Orb through its channel host. `relic add`
   matches a substring; `potion`, `card`, and `event` match exactly and take no `add`. A forced
   follow-up cannot be proved through the `event` shortcut, which skips the forcing behavior.
4. Confirm the change matches intent and grep **without closing the game** (closing rotates the
   log away):

```bash
python ../modmaker/scripts/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

If the console will not open or `add` says "Unable to create", match `errors.md` § Verification.
A manual run may be reported as **manually observed** only when the user confirms the concrete
state change; otherwise report Tier 1 only.

## Reruns and when to stop

Every launch costs minutes, and a full content-set harness takes four to six, so rerun only what a
change can reach:

| Changed since the last passing run | Rerun |
|---|---|
| Image files only: no code, csproj, resource-path, or localization change | Build, Tier 1, then the headed review that owns the image. The last Tier 2 pass still stands. |
| Localization text only: same keys and variables | Build. Tier 2 can wait for the final run, whose bilingual proof checks the new text. |
| Code, csproj, manifest, resource paths, or `SelfTestScenarios.cs` | Build, then Tier 2. While repairing, `--only` the affected scenarios. |

When a run or Build shows several independent defects, fix each under `repair.md`, then share one
launch. The Tier 2 you report is an unfiltered run (`scope=all`) on the build you deliver: if code
or localization changed after the last full pass, or the last passes were `--only` runs, run the
full self-test once more (an image-only change does not need it).

Stop launching and report when:

- Tier 2 passed on the current build and nothing it asserts has changed since. Never rerun only to
  reconfirm a pass or for polish structured state cannot observe (look, layout, animation,
  wording, feel);
- `repair.md`'s bound is reached: three unsuccessful fixes at the same stage; or
- the next step needs the user's eyes, hands, or judgment: headed review, the manual fallback, or
  whether something looks right, plays well, or has the right number. Hand it over with the exact
  build, commands, and checks.

## Finalize

Update `PLAN.md` only for stages that actually completed and record commands and results in
`MEMORY.md`. Leave a stage unchecked when its repair is active or its check failed, and report the
failure. Build the user-facing report directly from observed results:

- **Built:** the Mod and artifact path, only when Build passed.
- **Tier 2:** the kit summary (`passed=N/N scope=all`), the scenarios and face-checked Cards with
  their asserted values, and the coverage line including content it never exercised; or that it
  was not run, could not be reached, or failed. Never promote a fired/used log to proof.
- **Tier 1:** the load-marker and fresh-error result when Tier 2 did not run.
- **Headed review:** only observations a human actually reported; otherwise say
  visual/UI/controller/animation/subjective review was not run.
- **Not included:** relevant DESIGN `Not Now` items and accepted placeholders.

Use plain terms: "its effect fired automatically and the post-state matched" for a Tier 2 pass;
"it loads and registers, but its behavior was not observed" for Tier 1 only; "Build passed, but
the game was not launched" when no runtime check ran. Missing evidence stays visible and never
disappears behind a completion claim.
