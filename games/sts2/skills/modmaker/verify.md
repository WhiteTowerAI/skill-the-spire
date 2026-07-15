# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled". Two tiers. Always report
which tier you reached; never claim the effect is verified when only load was.

## Tier-1 — does it load? (automated, guaranteed)

Launch STS2 without Steam, wait, then grep the log for the load marker and fresh-run
error blocks.

```bash
python ${GAME_TOOLS_DIR}/launch.py
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName>
```

- `launch.py` ensures `steam_appid.txt` (=2868840) exists, launches the game,
  waits ~25s, and closes it.
- `grep_log.py` reads the **current** `godot.log` in full and passes if it finds
  `[T2MOD-SELFTEST] <ModName> loaded ok` **and** no error/exception block after that
  boundary. It includes multiline stack context and global errors whose header does not
  name the mod. It also reports the `RUNNING MODDED` flag. Two exact, stack-qualified
  base-game cleanup blocks are reported but ignored: abandon deleting a nonexistent
  `current_run.save.backup`, and native Sentry close during launcher termination. Similar
  headers without those cleanup stacks still fail.
- **Why no byte offset:** STS2 archives the previous log (to
  `godot<timestamp>.log`) and starts a fresh `godot.log` on every launch, so the
  current file already holds exactly this run. Do NOT try to slice the log by a
  pre-launch byte offset — a stale offset from the old file points into the wrong
  place in the new file and makes a working mod look like it failed to load. This
  was a real bug; read the whole current log instead.

**PASS** = marker found, no fresh-run error blocks. **FAIL** → go to `repair.md`. It
distinguishes the two tier-1 failure modes and fixes accordingly:

- **marker NOT FOUND but `RUNNING MODDED` = YES** → the mod loaded but logged no
  marker: it wasn't injected into `MainFile.Initialize()` (author.md step 2), or
  the code change never rebuilt. (Distinct from the log-rotation false-FAIL, which
  errors.md already retired.)
- **fresh error/exception block** → registration/load/runtime threw — e.g.
  missing `[Pool]` throws; a raw-key title means the loc keys don't match `Id.Entry`.

A code/csproj fix only reaches the game through a fresh build, so repair **rebuilds
first**, then re-runs tier-1 — bounded to 3 attempts.

This is the guaranteed check: it proves "installs + loads + registered".

## Tier-2 — does the effect fire? (automated harness, the headline)

**Tier-2 is now unattended** (M5). The mod ships an arg-gated in-process harness
(`SelfTest.cs`, author.md step 2.5). Launched with `--self-test`, it drives itself from the
main menu into the required hosted scenario and fires the effect — **no dev-console typing,
no human triggering**. You then grep its independently asserted state proof.

```bash
python ${GAME_TOOLS_DIR}/launch.py --self-test --mod-name <ModName>
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

The `--tier2-pattern` selects the SPEC invariant from structured
`[T2MOD-SELFTEST] <ModName> state proof:` lines. Use concrete expected/observed vocabulary:
`"card damage.*observed=6"`, `"counter.*6 -> 2"`,
`"cadence cross-combat threshold.*observed=0/4"`,
`"enemy attack.*observed=6"`, or `"event gold.*observed=25"`. The verifier ignores all
ordinary `played/fired/used` hook logs, even if the regex matches them, and separately
requires the exact load marker and `selftest done`.

> **Isolation before any `--self-test` run:** `--t2selftest` arms **every** loaded harness
> mod, so park all non-target harness mods first (move them out of `mods/`), leaving only the
> one under test. This includes **Overclock** and every `Canary*` — a stray second harness
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
- For a stateful effect, one matching proof line is not the whole scenario contract. The
  harness must assert `N-1`, threshold, and reset/carry-over before it emits `selftest done`;
  a run `[SavedProperty]` also asserts `SavedProperties.From`/`Fill`. Use the multi-combat
  variant in `reference/selftest-harness.md`.

**Read the harness's terminal marker first — it tells you which failure you have:**

- `selftest done` **and** the matching state proof present → **tier-2 PASS**. The harness
  observed the exact SPEC state, driven end-to-end with zero interaction.
- `selftest done` but the matching state proof is **absent** → the harness reached its
  scenario, but no accepted post-state assertion passed → a **real tier-2 behavior bug** →
  `repair.md` (ordinary trigger markers may still reveal where behavior diverged).
- `selftest FAILED: <stage>` or timeout → the **harness couldn't reach/drive its scenario**
  (navigation/timing — a setup problem, not your effect). Do **not** report a tier-2
  failure of the mod. Fall back to the **manual guide below**, and if that's not feasible,
  report **tier-1 only** honestly.

### Manual fallback (only if the harness reported FAILED / timed out)

Ask the user to drive it by hand via the dev console — the pre-M5 path:

1. Start a run in STS2 (the mod is loaded — tier-1 confirmed it).
2. Open the **dev console** with **`` ` `` (backtick)** (also `'`, `*`, `^`, `Shift+8`);
   close with `Esc`. Debug commands are auto-enabled because the game is running modded.
3. Grant the element by its `<PREFIX>-<SLUG>` id:
   - **relic:** `relic add <PREFIX>-<SLUG>` (`add` is default; matching is substring `Contains`).
   - **potion:** `potion <PREFIX>-<SLUG>` (**no `add`**, **exact** match; run in progress).
   - **card:** `card <PREFIX>-<SLUG>` spawns into **hand** (**no `add`**, **exact** match;
     run in progress, hand not full).
   - **enemy encounter:** `fight <PREFIX>-<ENCOUNTER_SLUG>` enters the custom encounter
     (run in progress). Confirm the custom monster spawned before ending the turn.
   - **event:** `event <PREFIX>-<SLUG>` enters the custom event (**exact** match; run in
     progress). Confirm the localized option appears before choosing it.
4. Trigger it: **relic** → enter a combat; **potion** → use it (pick a target if targeted);
   **card** → play it (target an enemy for an attack; `energy 3` first for headroom);
   **enemy encounter** → end your turn and confirm the enemy takes its move (HP/state changes);
   **event** → choose the specified option and confirm its run-state consequence.
5. Confirm the change matches intent and grep with the tier-2 pattern **without closing the
   game** (closing rotates the log away):

```bash
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

If the console won't open or `add` says "Unable to create", see errors.md "Verification
harness". The automated PASS still requires a structured harness state proof. A manual
fallback may be reported as **manually observed** only when the user confirms the concrete
state change; otherwise report tier-1 only.

## Finalize

Update `PLAN.md` (check the verify boxes for the tiers actually reached). Then
summarize for the user in plain language:

> Built **<Title>** (Common relic). It **loads in-game** (verified) and its effect
> **<fired automatically in its self-test scenario / is written but not yet observed —
> the harness couldn't reach its scenario>**. Artifacts are in `mods/<ModName>/`.
> <If tier-2 not observed: the harness marker it stopped on, and the manual check.>

Be honest about the tier. A loaded-but-effect-unobserved mod is tier-1, not tier-2 —
and a `selftest FAILED` is a harness miss, not proof the effect is broken.
