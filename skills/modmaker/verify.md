# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled". Two tiers. Always report
which tier you reached; never claim the effect is verified when only load was.

## Tier-1 — does it load? (automated, guaranteed)

Launch STS2 without Steam, wait, then grep the log for the load marker and fresh-run
error blocks.

```bash
python scripts/launch.py
python scripts/grep_log.py --mod-name <ModName>
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
python scripts/launch.py --self-test --mod-name <ModName>
python scripts/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
```

The `--tier2-pattern` selects the SPEC invariant from structured
`[T2MOD-SELFTEST] <ModName> state proof:` lines. Use concrete expected/observed vocabulary:
`"card damage.*observed=6"`, `"counter.*6 -> 2"`,
`"cadence cross-combat threshold.*observed=0/4"`,
`"enemy attack.*observed=6"`, `"monster vocabulary complete.*observed=all"`,
`"event gold.*observed=25"`,
`"forcedFollowUp.*restored=True"`, or
`"character foundation complete.*observed=all"`,
`"resource UI complete.*observed=all"`, or
`"ordered buffer complete.*observed=all"`. A maintainer capability-kernel canary
uses `"patch kernel complete.*observed=all"` only after its patch, typed state, hosted UI,
and lifetime assertions. The verifier ignores all
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
- For a multi-move enemy, one HP delta is likewise insufficient. Before the terminal proof,
  the harness must execute every SPEC move/branch outcome and assert its move history,
  concrete creature/Power state, downstream buff consequence, and multi-hit result count.
- For a Character Foundation, the final proof is valid only after the harness has asserted
  one constructor-registered model, the real selection button, runtime identity/HP, three
  pool types and member models, exact starter deck/relic multisets, designed MaxEnergy,
  and one hosted public/BaseLib mechanic delta through `CombatPlayer`. If Shop is selected,
  the unlocked pool must also fill its two Attack, two Skill, and one Power colored slots.
- For a character resource, require gain, affordable and unaffordable checks, one exact
  successful payoff, one rejected spend with no mutation/negative state, live counter
  values, and a distinct zero state/counter in combat 2.
- For an ordered semantic buffer/dynamic output, require exact source/compile-card result
  piles, visible order, capacity and overflow behavior, one generated-history entry, exact
  configured output/effect, and a distinct empty state/UI in combat 2.
- For an Event, require one real UI path per independent SPEC outcome family. Blocking
  card/reward overlays must finish before their post-state assertion. A special combat must
  identify the custom encounter and prove exactly one authored completion path: named
  `Resume` page or direct map. Use a fresh Event instance if SPEC independently exercises
  both forms; never start two combats from one mutable Event. The final structured marker
  lists identical expected/observed outcome families.

### Custom-art headed acceptance

Tier 2 proves behavior, not custom art. When `SPEC.md` selected `generate`, keep the art
claim separate until the real headed game visibly excludes the fallback in every independent
consumer named by `reference/art-contract.md`. Record a screenshot or an equivalent node
assertion plus visual inspection. In particular:

- relic: bar icon and clicked detail popup;
- power: status icon and big apply/expire notification;
- enchantment: card tab and hover tooltip;
- orb icon: smart tooltip and trigger flash (the Frost combat body remains fallback);
- monster: static body in combat with unobscured intent/floor alignment, then the same
  custom body in bestiary with title/move list and no crop;
- event: the normal initial portrait behind the real option UI, then every selected
  later-page portrait after its real option transition; missing optional page art must
  visibly retain the current portrait. When `portrait_halo` is selected, also capture every
  configured page after its UI fade, observe motion (or static Instant-mode behavior), and
  prove the prior named root is freed across page/portrait/combat/finish transitions. A
  near-black room-transition frame is not evidence.
- forced follow-up Event: one settled target Event room reached through the real Unknown
  MapPoint path. The title/description/completion option must be visibly usable; direct
  `event <ID>` entry skips the forcing behavior and is not acceptance evidence.
- native Event presentation: capture the settled `trial_noble` page, the real Card
  acquisition preview with the acquired relic visible in the top bar, and the settled
  result page. Assert preference-aware shake movement/return and preview/VFX cleanup in the
  same `MapNode` run; a model delta without the native consumers is insufficient.
- character static presentation: the real character-select button/background, top-panel
  icon, and static combat body must visibly use the normalized custom resources. The
  compact icon must resolve at 24x24 inside the fixed 220x32 icon+text control. Enter real
  RestSite and Shop hosts for selected static bodies; merchant also asserts the exact
  versioned prefix `targets/owned prefix/postfix=1/1/0` and no Spine error. Full energy
  asserts five 256x256 custom layers, native 128x128 root, and live number label. Locked
  selection and map marker require their own visible-host evidence. Do not infer any
  consumer from a path or successful build. Read `reference/character-presentation.md`.
- Ancient presentation: enter the real Ancient/Architect flow and capture the native name
  banner plus one character/Architect dialogue exchange. Assert the character localization,
  speech-bubble color, and attack VFX selection; normal Event rich text is not a substitute.

If a secondary view cannot be reached, report behavior Tier 2 separately and label the art
unverified; do not infer it from a resource path, `.pck` build, or primary view.

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
   - **character:** select the custom character on the real character screen and click
     Confirm; there is no console shortcut that proves character-select presence.
4. Trigger it: **relic** → enter a combat; **potion** → use it (pick a target if targeted);
   **card** → play it (target an enemy for an attack; `energy 3` first for headroom);
   **enemy encounter** → end enough turns to traverse the declared cycle; confirm every
   move's visible intent and exact HP/Block/Power change, and drive each conditional outcome;
   **event** → choose the specified options and confirm each exact Cmd/selection/reward
    consequence. For special combat, confirm the requested custom encounter and then the
    named return page or direct map. For `portrait_halo`, visually inspect configured pages
    and confirm no stale overlay survives a page switch or combat entry. For vanilla Event
    text effects, inspect the named colored/moving phrase on each authored page and confirm
    the prior page's text is gone after the transition.
    For native acquisition presentation, confirm the real Card preview and relic top-bar
    animation, and for `trial_noble` confirm its exact initial-page placement and absence on
    the result page. A `weak_short` shake must terminate and must honor a disabled setting.
    A forced follow-up cannot be proved by the `event` console shortcut; if its automated
    real-Unknown driver cannot run, report Tier 1 rather than claiming the hook behavior.
   **character** → confirm HP, starter deck/relic, and standard 3 energy after run start;
   enter combat and observe the named starter mechanic's exact state delta.
5. Confirm the change matches intent and grep with the tier-2 pattern **without closing the
   game** (closing rotates the log away):

```bash
python scripts/grep_log.py --mod-name <ModName> --tier2-pattern "<state-proof-pattern>"
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
