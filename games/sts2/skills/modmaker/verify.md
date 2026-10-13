# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled". Two tiers, and which one you reached
is itself a reported fact.

Any difference found here is classified through `repair.md` before a fix. Write and validate
the active PLAN route first; do not infer that every behavior difference is a consumer-local
bug when the cited shared route may be violating its own contract.

## Bilingual localization proof

Build preflight establishes the static localization half: required directories, table/key
parity, nonempty values, SmartFormat variable parity, valid rich-text markup, and the static
vanilla-style comparison in `.text-style.log`. Tier 2 owns the runtime half. Before
driving the selected behavior, the generated harness snapshots `LocManager.Instance.Language`,
switches through `eng` and `zhs` with the public `SetLanguage` route, and resolves every
SPEC-required player-facing `LocString` through its real model/UI consumer. Compare against the
exact text recorded for that language, reject raw keys and unresolved placeholders, and restore
the original language in `finally`.

Emit one structured `state proof:` naming both observed language codes only after both passes.
One language resolving, static JSON parity, or a catalog lookup is not bilingual runtime proof.
Use the reusable route in `reference/selftest-harness.md`; do not write the player's language
setting or leave the verification language active after the check.

## Tier-1 — does it load? (automated, guaranteed)

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
first**, then re-runs tier-1 — bounded to 3 attempts.

This is the guaranteed check: it proves "installs + loads + registered".

## Tier-2 — does the effect fire? (automated harness, the headline)

**Tier-2 is unattended.** The mod ships an arg-gated in-process harness
(`SelfTest.cs`, author.md step 2.5). Launched with `--self-test`, it drives itself from the
main menu into the required hosted scenario and fires the effect — **no dev-console typing,
no human triggering**. You then grep its independently asserted state proof.

```bash
python ${GAME_TOOLS_DIR}/launch.py --self-test --mod-name <ModName>
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

The `--tier2-pattern` selects the SPEC invariant from structured
`[T2MOD-SELFTEST] <ModName> state proof:` lines. Every proof also records
`framework=RitsuLib`, the actual loaded version, and exact
`host=0.107.1 compat=0.107.1`. Use concrete
expected/observed vocabulary:
`"card damage.*observed=6"`, `"counter.*6 -> 2"`,
`"cadence cross-combat threshold.*observed=0/4"`,
`"enemy attack.*observed=6"`, `"monster vocabulary complete.*observed=all"`,
`"event gold.*observed=25"`,
`"forcedFollowUp.*restored=True"`, or
`"character foundation/static-presentation.*observed=all"`,
`"resource UI complete.*observed=all"`, or
`"ordered buffer complete.*observed=all"`, or
`"reward complete.*observed=all"`, or
`"custom card piles complete.*observed=all"`, or
`"runtime UI complete.*observed=all"`. A Reward run follows `surfaces/reward.md` and proves
claim/refusal, the selected presentation route, and pending-save reconstruction. A custom-pile run follows
`reference/card-piles.md` and proves the consumers selected by SPEC; API support does
not require a separate run for every documented public consumer. The verifier ignores all
  ordinary `played/fired/used` hook logs, even if the regex matches them, and separately
  requires the exact load marker and `selftest done`.

Derive the verification checklist only from the concrete variants selected in the current
human-readable SPEC. Do not prebuild a nine-family matrix, claim omitted variants, or turn an
authoring contract into runtime proof. Each selected variant remains unobserved until the current
run actually proves it.

> **Isolation before any `--self-test` run:** `--t2selftest` arms **every** loaded harness
> mod, so park all non-target harness mods first (move them out of `mods/`), leaving only the
> one under test. A stray second harness
> collides on the main menu (`ObjectDisposedException: NMainMenu`) and fails the run.

- `launch.py --self-test` passes `--t2selftest` (which arms the harness — a normal launch
  never does), then **polls the log** until the harness prints its terminal marker
  (`[T2MOD-SELFTEST] <ModName> selftest done` or `… selftest FAILED`), bounded by a
  timeout. It exits 0 only for `done`; `FAILED`, timeout, or the game exiting before a
  terminal marker return 1. The game is closed after the terminal outcome so the grep can
  read the fresh log.
- `grep_log.py --tier2-pattern` applies the regex only to structured `state proof:` lines.
  It passes only if the exact load marker, an asserted state proof, and `selftest done` are
  all present, with no `FAILED` or fresh-run error blocks → `[PASS] Tier-2 verified`.
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
- `selftest FAILED: <stage>` or timeout → the **harness couldn't reach/drive its scenario**
  (navigation/timing — a setup problem, not your effect). Do **not** report a tier-2
  failure of the mod or rewrite the element. Classify any harness navigation/timing repair as
  implementation-equivalent, or fall back to the **manual guide below**; if that is not
  feasible, report **tier-1 only** honestly.

This tells you *which* failure you have. For the cause and fix of each, match the signature in
`${STS2API_SKILL_DIR}/errors.md` § Verification, and § Behavior for a state proof that
reports a wrong observed value.

### Manual fallback (only if the harness reported FAILED / timed out)

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

## Finalize

Update the plain `PLAN.md` checklist only for stages that actually completed and record the
commands and results in `MEMORY.md`. If a repair is still active or a required check failed,
leave the affected stage unchecked and report the failure; no separate repair-state validator is
needed.

Build the user-facing report directly from observed results:

- **Built:** name the generated Mod and artifact path only when Build passed.
- **Tier 1:** quote the load-marker result and fresh-error result, or say it was not run/failed.
- **Tier 2:** name the real host scenario and concrete structured state assertion, or say it was
  not run, could not be reached, or failed. Never promote a fired/used log to proof.
- **Headed review:** name only observations a human actually reported. Otherwise state that
  visual/UI/controller/animation/subjective review was not run.
- **Not included:** summarize explicit DESIGN `Not Now` items and accepted placeholders when
  relevant to what the user asked for.

Use plain terms: "its effect fired automatically and the post-state matched" for a Tier 2 pass;
"it loads and registers, but its behavior was not observed" for Tier 1 only; "Build passed, but
the game was not launched" when runtime verification did not run. Missing evidence must remain
visible, never silently disappear behind a completion claim.
