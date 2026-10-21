# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled". Two tiers, and which one you reached
is itself a reported fact.

Any difference found here is classified through `repair.md` before a fix. Write and validate
the active PLAN route first; do not infer that every behavior difference is a consumer-local
bug when the cited shared route may be violating its own contract.

## Bilingual localization proof

Build preflight establishes the static localization half: required directories, table/key
parity, nonempty values, SmartFormat variable parity, valid rich-text markup, and the static
vanilla-style comparison in `.text-style.log`. The exact wording is the authored table itself,
checked against SPEC when you write it. Tier 2 owns the runtime half: on every self-test run the
kit's roll call switches through `eng` and `zhs` with the public `SetLanguage` route, resolves
every Card, Relic, Potion, Power, Character, Monster, and Encounter string through its real
model consumer, rejects missing,
empty, raw-key, and unresolved-placeholder values, and restores the player's language. Strings
of other surfaces (Event pages, Ancient dialogue) are resolved the same way by their own
scenario. One language resolving, static JSON parity, or a catalog lookup is not
bilingual runtime proof. Translation quality, tone, clipping, and layout stay headed review.

## Tier-1 — does it load? (automated, guaranteed)

A Tier 2 launch checks these load facts first: when the Mod did not load, it stops at the
main menu and prints this Tier 1 verdict. After a Build, go straight to Tier 2; launch Tier 1
alone only to diagnose a load failure or before the manual fallback.

```bash
python ${GAME_TOOLS_DIR}/launch.py --mod-name <ModName>
```

One command launches STS2 without Steam, waits for the main menu, closes the game, and
prints the verdict. Do not read or slice the log yourself.

**PASS** = the exact `[T2MOD-SELFTEST] <ModName> loaded ok` record carries the pinned
framework/host/compat profile, and no error/exception block follows it, including global
errors that do not name the Mod. **FAIL** → go to `repair.md`.

Tier 1 has three distinct failure modes, and they are not interchangeable: a **framework
marker** missing or mismatched is a profile/scaffold problem, a **load marker NOT FOUND while
`RUNNING MODDED` = YES** means the Mod loaded but emitted no marker, and a **fresh
error/exception block** means registration or runtime threw. Match the exact signature in
`${STS2API_SKILL_DIR}/errors.md` § Verification and § Registration And Localization for the
cause and fix; do not guess one.

A code/csproj fix only reaches the game through a fresh build, so repair **rebuilds
first**, then reruns the earliest failing check under `repair.md`.

This is the guaranteed check: it proves "installs + loads + registered".

## Tier-2 — does the effect fire? (automated harness, the headline)

**Tier-2 is unattended.** The scaffold-generated kit (`SelfTestKit.cs`) and this Mod's
`SelfTestScenarios.cs` (author.md step 2.5) are compiled in and dormant. Launched with
`--self-test`, the kit runs the roll call, drives itself from the main menu into each hosted
scenario, and fires the effects — **no dev-console typing, no human triggering**. You then grep
its result.

```bash
python ${GAME_TOOLS_DIR}/launch.py --self-test --mod-name <ModName>
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName> --tier2-pattern "kit summary passed=.* scope=all"
```

The kit logs `state proof: kit summary passed=N/N scope=all` only when the roll call, every face
check, and every scenario passed, followed by `selftest done`. `grep_log.py` prints the kit's
coverage and summary lines and every `scenario FAILED:` line with its expected and observed
values. To inspect one SPEC invariant, match its own line instead, for example
`--tier2-pattern "lantern_combat_start_energy: .*observed=4"`. The verifier ignores all ordinary
`played/fired/used` hook logs, even if the regex matches them, and separately requires the exact
load marker and `selftest done`. A Reward run follows `surfaces/reward.md` and proves
claim/refusal, the selected presentation route, and pending-save reconstruction; a custom-pile
run follows `reference/card-piles.md` and proves the consumers selected by SPEC.

While repairing, `--only` reruns just the named scenarios (a trailing `*` matches a prefix):

```bash
python ${GAME_TOOLS_DIR}/launch.py --self-test --only "face.*,lantern_combat_start_energy" --mod-name <ModName>
```

A filtered run logs `scope=partial`, and `grep_log.py` reports `[PASS] Tier-2 partial run`. That
is never the Tier 2 you report (§ Reruns and when to stop).

Derive the verification checklist only from the concrete variants selected in the current
human-readable SPEC. Do not prebuild a nine-family matrix, claim omitted variants, or turn an
authoring contract into runtime proof. Each selected variant remains unobserved until the current
run actually proves it.

> **Isolation is automatic.** `--t2selftest` arms **every** loaded harness Mod, and a stray
> second harness collides on the main menu (`ObjectDisposedException: NMainMenu`).
> `launch.py --self-test` therefore moves every other Mod folder whose DLL contains a
> `t2selftest` gate from `mods/` to `mods-parked-by-skill-the-spire/` for the run and moves
> it back afterwards, even when the run fails. If an earlier run was killed before it could
> restore, the next launch restores first. Never move user Mods by hand.
> The harness abandons any run open in the modded profile before it starts its own. When
> that run used a parked Mod's character, RitsuLib logs `Failed to upload run
> history/metrics: ... ModelNotFoundException`; `grep_log.py` ignores exactly that block
> unless the missing model belongs to the Mod under test.

- `launch.py --self-test` passes `--t2selftest` (or `--t2selftest=<names>` with `--only`),
  which arms the harness — a normal launch never does — then **polls the log** until the harness prints its terminal marker
  (`[T2MOD-SELFTEST] <ModName> selftest done` or `… selftest FAILED`). It waits for the
  harness's logged `selftest budget` plus boot time; `--wait-seconds N` overrides that.
  It exits 0 only for `done`; `FAILED`, a launcher timeout, or the game exiting before a
  terminal marker return 1. The game is closed after the terminal outcome so the grep can
  read the fresh log.
- `grep_log.py --tier2-pattern` applies the regex only to structured `state proof:` lines.
  It passes only if the exact load marker, an asserted state proof, and `selftest done` are
  all present, with no `FAILED` or fresh-run error blocks → `[PASS] Tier-2 verified`, or
  `[PASS] Tier-2 partial run` after `--only`.
  Multiline/global errors after this mod's load marker fail even when the mod name appears
  only in stack context (or not at all).
- For every selected surface and capability, follow the surface page § Proof matrix and the
  selected reference's proof section; derive only the cases SPEC selected. Registration, direct
  method calls, model lookups, serialization, constructed Godot nodes, or a successful Build
  never prove behavior.

### Headed review

Structured state does not prove images, layout, mouse/controller input, animation, audio, or
subjective feel. When SPEC selects one of those, run the headed checks in the owning reference
(for example `advanced-targeting.md`, `card-hand-emphasis.md`, `extra-corner-labels.md`,
`rest-site-options.md`, `art-contract.md`, `character-presentation.md`,
`character-combat-cues.md`, `ancient-dialogue.md`, `event-vfx.md`,
`event-native-presentation.md`, or `forced-followup-event.md`).

Rendered text is also a headed observation. When the user reviews a Card, Relic, Potion,
Power, or Event in game, ask them to compare it with a similar vanilla one: gold terms,
colored numbers, line breaks, the tooltip list, and the Chinese text after switching language
(`reference/vanilla-text-style.md` § Verification). Build's style check is static evidence
only.

Custom art stays unverified until the real headed game visibly shows it, not the fallback, in
every consumer `art-contract.md` lists for that spec. Never infer it from a resource path, a
`.pck` build, or a primary view alone; report behavior Tier 2 separately when a secondary view
cannot be reached.

When the user performs the headed review, build and deploy the focused proof, give them the
exact dev-console commands and the check matrix, and record their reported observations
separately. An unrun Tier 1 or Tier 2 check remains an explicit exception, never a pass.

**Read the harness's terminal marker first — it tells you which failure you have:**

- `selftest done` **and** the matching state proof present → **tier-2 PASS**. The harness
  observed the exact SPEC state, driven end-to-end with zero interaction.
- `selftest done` but the matching state proof is **absent** → the harness reached its
  scenario, but no accepted post-state assertion passed → a **real tier-2 behavior bug** →
  classify in `repair.md` (ordinary trigger markers may still reveal where behavior diverged).
- `selftest FAILED: state proof: <k> of <n> scenarios did not pass: ...` → those scenarios
  ran and an assertion failed or the scenario threw; every other scenario still ran. Each
  `scenario FAILED:` line names the expected and observed values, and its `scenario trail:`
  lines show what the host did. A **real tier-2 behavior bug** in the Mod, or a scenario that
  encoded SPEC wrongly → classify in `repair.md`. Fix every independent failure before the
  next launch.
- `selftest FAILED: timeout: ...` → a scenario ran out of its own budget, or the watchdog found
  it stuck at the named step. For a long scenario, raise its `budgetSeconds` in
  `SelfTestScenarios.cs`; otherwise repair the stalled step. Report it as a timeout, never as a
  navigation failure.
- `[launch] main menu reached without this Mod's load marker` → the Mod did not load; the
  Tier 1 verdict printed next names which load failure it is.
- `[launch] main menu reached but the harness never armed` → `MainFile.cs` lost the
  `SelfTestKit.Arm` line; restore it with `scaffold.py --refresh-selftest-kit`.
- `[launch] TIMEOUT` with no terminal marker → the launcher stopped waiting first. Rerun
  with a larger `--wait-seconds`; it is not evidence about the Mod.
- `selftest FAILED: setup: ...` (or any other stage) → the **harness couldn't reach/drive its
  scenario** (navigation, an unknown `--only` name, a scenario definition error — a setup
  problem, not your effect). Do **not** report a tier-2
  failure of the mod or rewrite the element. Classify any harness navigation/timing repair as
  implementation-equivalent, or fall back to the **manual guide below**; if that is not
  feasible, report **tier-1 only** honestly.

This tells you *which* failure you have. For the cause and fix of each, match the signature in
`${STS2API_SKILL_DIR}/errors.md` § Verification, and § Behavior for a state proof that
reports a wrong observed value.

### Manual fallback (only if the harness could not reach or drive its scenario)

Ask the user to drive it by hand via the dev console:

1. Start a run in STS2 (the mod is loaded — tier-1 confirmed it).
2. Open the **dev console** with **`` ` `` (backtick)** (also `'`, `*`, `^`, `Shift+8`);
   close with `Esc`. Debug commands are auto-enabled because the game is running modded.
3. Grant the element and 4. trigger it: each surface page owns both steps in its
   § Manual fallback — `surfaces/card.md`, `surfaces/relic.md`, `surfaces/potion.md`,
   `surfaces/monster.md`, `surfaces/event.md`, `surfaces/character.md`, `surfaces/act.md`,
    `surfaces/ancient.md`, `surfaces/reward.md`, `surfaces/card-pile.md`, and
    `surfaces/runtime-ui.md`. A Power, keyword, or
   enchantment has no route of its own and is driven through its host Card; an orb is driven
   through its declared channel host.

   Two constraints hold across all of them. A `<PREFIX>-<SLUG>` id is matched differently per
   command — `relic add` is substring `Contains`, while `potion`, `card`, and `event` are exact
   and take no `add`. And a forced follow-up cannot be proved by the `event` shortcut at all:
   direct entry skips the forcing behavior, so if its automated real-Unknown driver cannot run,
   report Tier 1 rather than claiming the hook behavior.
5. Confirm the change matches intent and grep with the tier-2 pattern **without closing the
   game** (closing rotates the log away):

```bash
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

If the console won't open or `add` says "Unable to create", match
`${STS2API_SKILL_DIR}/errors.md` § Verification. The automated PASS still requires a structured harness state proof. A manual
fallback may be reported as **manually observed** only when the user confirms the concrete
state change; otherwise report tier-1 only.

## Reruns and when to stop

Every game launch costs minutes, and a full content-set harness takes four to six, so rerun only
what the change can reach. A Tier 2 PASS already carries every Tier 1 fact: `grep_log.py`
requires the exact load marker, the pinned profile, and no fresh error block for it, and a
Tier 2 launch stops early with the Tier 1 verdict when the Mod does not load. A behavior run
after Build needs only the Tier 2 launch.

| Changed since the last passing run | Rerun |
|---|---|
| Image files only: no code, csproj, resource-path, or localization change | Build, Tier 1, then the headed review that owns the image. The last Tier 2 pass still stands. |
| Localization text only: same keys and variables | Build. Tier 2 can wait for the final run, where its bilingual proof checks the new text. |
| Code, csproj, manifest, resource paths, or `SelfTestScenarios.cs` | Build, then Tier 2. While repairing, `--only` the affected scenarios. |

When the last run or Build shows more than one independent defect, fix each one under
`repair.md`, then share one launch. Do not launch once per fix.

The Tier 2 you report must be an unfiltered run (`scope=all`) on the build you deliver. If code
or localization changed after the last full pass, or the last passes were `--only` runs, run the
full self-test once more before the report; an image-only change does not need it.

Stop launching and report when any of these holds:

- Tier 2 passed on the current build and nothing it asserts has changed since. Never rerun
  only to reconfirm a pass, and never rerun for polish structured state cannot observe: look,
  layout, animation, wording, or feel.
- `repair.md`'s bound is reached: three unsuccessful fixes at the same stage.
- The next step needs the user's eyes, hands, or judgment: headed review, the manual fallback,
  or whether something looks right, plays well, or has the right number. Hand it over with the
  exact build, commands, and checks to make.

## Finalize

Update the plain `PLAN.md` checklist only for stages that actually completed and record the
commands and results in `MEMORY.md`. If a repair is still active or a required check failed,
leave the affected stage unchecked and report the failure; no separate repair-state validator is
needed.

Build the user-facing report directly from observed results:

- **Built:** name the generated Mod and artifact path only when Build passed.
- **Tier 1:** quote the load-marker result and fresh-error result, or say it was not run/failed.
- **Tier 2:** quote the kit summary (`passed=N/N scope=all`), name the scenarios and face-checked
  Cards with their asserted values, and quote the coverage line, including content it never
  exercised; or say it was not run, could not be reached, or failed. Never promote a fired/used
  log to proof.
- **Headed review:** name only observations a human actually reported. Otherwise state that
  visual/UI/controller/animation/subjective review was not run.
- **Not included:** summarize explicit DESIGN `Not Now` items and accepted placeholders when
  relevant to what the user asked for.

Use plain terms: "its effect fired automatically and the post-state matched" for a Tier 2 pass;
"it loads and registers, but its behavior was not observed" for Tier 1 only; "Build passed, but
the game was not launched" when runtime verification did not run. Missing evidence must remain
visible, never silently disappear behind a completion claim.
