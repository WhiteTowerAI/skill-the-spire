# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled" (`INV-2`). Two tiers, and which one
you reached is itself a reported fact (`INV-1`).

Any difference found here is classified through `repair.md` before a fix. Write and validate
the active PLAN route first; do not infer that every behavior difference is a consumer-local
bug when the cited shared route may be violating its own contract (`INV-9`).

## Bilingual localization proof

Build preflight establishes the static half of `INV-10`: required directories, table/key
parity, nonempty values, and SmartFormat token parity. Tier 2 owns the runtime half. Before
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

Launch STS2 without Steam, wait, then grep the log for the framework profile, exact load
marker, and fresh-run error blocks. The pinned scaffold and verifier enforce this before any
RitsuLib runtime claim.

```bash
python ${GAME_TOOLS_DIR}/launch.py
python ${GAME_TOOLS_DIR}/grep_log.py --mod-name <ModName>
```

- `launch.py` ensures `steam_appid.txt` (=2868840) exists, launches the game,
  waits ~25s, and closes it.
- `grep_log.py` reads the **current** `godot.log` in full. The verifier passes
  only if the exact `[T2MOD-SELFTEST] <ModName> loaded ok` record also contains
  `framework=RitsuLib`, an actual `frameworkVersion>=0.5.11`, and exact
  `host=0.107.1 compat=0.107.1`, with no
  error/exception block after that
  boundary. It includes multiline stack context and global errors whose header does not
  name the mod. It also reports the `RUNNING MODDED` flag. Two exact, stack-qualified
  base-game cleanup blocks are reported but ignored: abandon deleting a nonexistent
  `current_run.save.backup`, and native Sentry close during launcher termination. Similar
  headers without those cleanup stacks still fail.
- Read the whole current log. Never slice it by a pre-launch byte offset: STS2 archives the
  previous log and starts a fresh `godot.log` each launch, so a stale offset points into the
  wrong file and makes a working Mod look like it failed to load.

**PASS** = marker found, no fresh-run error blocks. **FAIL** → go to `repair.md`.

Tier 1 has three distinct failure modes, and they are not interchangeable: a **framework
marker** missing or mismatched is a profile/scaffold problem, a **load marker NOT FOUND while
`RUNNING MODDED` = YES** means the Mod loaded but emitted no marker, and a **fresh
error/exception block** means registration or runtime threw. Match the exact signature in
`${STS2_API_SKILL_DIR}/errors.md` § Verification and § Registration And Localization for the
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
`"custom card piles complete.*observed=all"`. A custom-pile run follows
`reference/card-piles.md` and proves the consumers selected by SPEC; Package support does
not require a separate run for every documented public consumer. The verifier ignores all
  ordinary `played/fired/used` hook logs, even if the regex matches them, and separately
  requires the exact load marker and `selftest done`.

For a v3 SPEC, derive the ordinary verification checklist only from the families and concrete
variants present in its `open-mod-surface-data/v1` block. Do not prebuild a nine-family matrix,
claim omitted variants, or turn M8.7 structural validation into runtime proof. Each selected
variant keeps its own evidence status until the current run actually observes it.

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
  run-save state also asserts a real save/fill round trip. Use the multi-combat
  variant in `reference/selftest-harness.md`.
- For a multi-move enemy, one HP delta is likewise insufficient. See `surfaces/monster.md`
  § Proof matrix.
- For a Character Foundation, see `surfaces/character.md` § Proof matrix. Its opening
  paragraph is the gate the final proof must clear before it is valid.
- For selected secondary resources, see `reference/character-resource.md` and derive only the
  declared resource/use/UI/lifecycle cases. For an ordered semantic buffer/dynamic output,
  see `surfaces/character.md` § Proof matrix.
- For advanced Card/Potion targeting, follow `reference/advanced-targeting.md`: require
  the source-aware single Card, single Potion, and player-aware multi Card as distinct real
  consumers. Assert zero/one/multiple candidates, exact affected creature IDs and deltas,
  queued invalidation, unchanged rejected payment/Potion state, and normal Card result
  pile. `potion + many` remains a known lifecycle limitation.
- For a Card- or Relic-owned Rest Site option, follow `reference/rest-site-options.md` and
  the matching owner surface. Card ownership remains game-unobserved until that exact route runs.
- For an Event, see `surfaces/event.md` § Proof matrix.

### Advanced-target headed acceptance

The structured state proof does not establish selection UI. In the same focused
`CombatPlayer` fixture, the reviewer uses the dev console to grant each proof Card/Potion,
then checks the exact matrix from `reference/advanced-targeting.md`: mouse and controller
can select only legal single targets, cancel returns normally, zero legal targets cannot
commit the action, multi-target reticles appear only on the resolved creatures, and no
reticle remains after resolution. This is a manually observed result (`INV-1`).

### Gameplay-readability headed acceptance

For Card hand emphasis, see `surfaces/card.md` § Gameplay-readability headed acceptance.

For Relic/Power extra labels, read `reference/extra-corner-labels.md`. Obtain the real hosts
and drive Power zero/one plus Relic zero/one/bounded-multiple, plain/rich text, state
refresh, removal, host cleanup, and combat-transition cleanup. Inspect crowded Relic and
Power rows at common aspect ratios; the native main counter, icon, tooltip, and neighboring
labels must remain unobstructed.

When the human lead reserves this review, do not launch the game or take screenshots.
Build/deploy the focused proof and provide exact console commands plus the matrix above.
Record the lead's reported observations separately (`INV-1`); any unrun Tier 1 or structured
Tier 2 gate remains an explicit exception.

### Rest Site option headed acceptance

Do not launch this check automatically when the human lead has reserved headed review.
Build and deploy the focused proof, then provide the exact dev-console route from
`reference/rest-site-options.md`. The reviewer checks native localization, custom and
fallback icon framing, gray state, mouse click, controller focus loop, native-option
coexistence, failed-payment retention, successful list rebuild, and the declared second
visit. Record the reported matrix separately from Tier 1 and strict Tier 2 (`INV-1`); an unrun
structured harness remains an exception, never a pass.

On the pinned host, `gold -N` is not a removal command: negative values are ignored. Use
normal Shop spending before entering the Rest Site to establish the visible low-Gold state.
A literal render-then-lower-Gold stale-button check needs a narrow proof driver that calls a
public Gold command; if the human-led route omits it, record that omission explicitly.

### Custom-art headed acceptance

Tier 2 proves behavior, not custom art. When `SPEC.md` selected `generate`, keep the art
claim separate until the real headed game visibly excludes the fallback in every independent
consumer named by `reference/art-contract.md`. Record a screenshot or an equivalent node
assertion plus visual inspection. In particular:

- relic: exact 256x256 main/derived-outline pair in one real `NRelic`, plus the clicked
  detail popup using the explicit big path;
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
- rest-site option: one real `NRestSiteButton` must show the packed 256x169 custom image
  without crop/distortion, and a missing-art build must show the resolved native Heal icon
  without missing-resource or UI errors. The dimensions and fallback consumer are verified;
  each generated image still needs its own framing review.
- character static presentation: the real character-select button/background, top-panel
  icon, and static combat body must visibly use the normalized custom resources. Assert the
  exact 132x195 portrait, 1920x1200 background, normal and outlined 88x88 top-panel
  textures under one `NTopBarPortrait`, and 512x512 non-Spine
  combat body in their real hosts. Full energy asserts one native counter with five 256x256
  custom layers and its live number label. For the Character theme, automatically assert all
  four exact color values, frame shader target/brightness, distinct existing icon paths,
  the 256x256 large icon in a real hand card's `NCard.%EnergyIcon`, and the 24x24 path in a
  real `EnergyIconsFormatter` card-description result. Enter real RestSite and Shop hosts and assert their
  512x512 static bodies; the RitsuLib route requires no merchant prefix. Capture one settled
  screenshot for selection, combat/top-panel/energy, RestSite, and Shop. Locked selection
  and map marker require their own visible-host evidence. Do not infer any consumer from a
  path or successful build. Read `reference/character-presentation.md`.
- character combat cues: in real combat, observe Idle loop, Attack and damage-triggered Hit
  one-shots returning to Idle, Dead reaching and holding frame 6, stable body/UI anchors,
  and playback cleanup between combats. The harness asserts every 512x512 frame and shared
  geometry. Separately omit one frame and require the static 512x512 combat body with no
  playback node or surviving-frame flash. Read `reference/character-combat-cues.md`.
- Character Ancient dialogue: first parse every selected catalog target through the actual
  RitsuLib localization route and assert group count, line order/speaker, visit/repeat,
  prompts, and Architect attackers. Enter one ordinary target through `ancient <ID>` and
  enter Architect only through the final-act production `EnterNextAct()` path. In the
  ordinary scene confirm the native name banner/background, Character and Ancient
  icon/bubble direction/color, readable text/prompts, mouse/controller progression, and
  restoration of the untouched native options after the last line. In Architect confirm
  Character speech color, configured start/end attackers, every selected
  `GetArchitectAttackVfx()` path, Proceed, and clean run completion. A fresh profile's
  global first-visit-ever line correctly wins before Character dialogue. Normal Event rich
  text, `event THE_ARCHITECT`, debug fallback, or a successful build is not a substitute.

If a secondary view cannot be reached, report behavior Tier 2 separately and label the art
unverified; do not infer it from a resource path, `.pck` build, or primary view.

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
`${STS2_API_SKILL_DIR}/errors.md` § Verification, and § Behavior for a state proof that
reports a wrong observed value.

### Manual fallback (only if the harness reported FAILED / timed out)

Ask the user to drive it by hand via the dev console:

1. Start a run in STS2 (the mod is loaded — tier-1 confirmed it).
2. Open the **dev console** with **`` ` `` (backtick)** (also `'`, `*`, `^`, `Shift+8`);
   close with `Esc`. Debug commands are auto-enabled because the game is running modded.
3. Grant the element and 4. trigger it: each surface page owns both steps in its
   § Manual fallback — `surfaces/card.md`, `surfaces/relic.md`, `surfaces/potion.md`,
   `surfaces/monster.md`, `surfaces/event.md`, `surfaces/character.md`. A Power, keyword, or
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
`${STS2_API_SKILL_DIR}/errors.md` § Verification. The automated PASS still requires a structured harness state proof. A manual
fallback may be reported as **manually observed** only when the user confirms the concrete
state change; otherwise report tier-1 only.

## Finalize

Update `PLAN.md` (check the verify boxes for the tiers actually reached) and record the
checks that actually ran in `MEMORY.md`.

Before settling or reporting, require repair state to be clear:

```bash
python ${GAME_TOOLS_DIR}/repair_trace.py --design DESIGN.md --spec SPEC.md --plan PLAN.md --finalize
```

An active repair blocks Finalize. Classify a difference discovered while settling just like
one found during Verify; clear affected `E-###` settlements and reopen only its recorded stages.

### Settle the deliverable claim first

Before writing anything for the user, settle every required experience in `DESIGN.md`'s
`open-mod-deliverable:v1` block. Fill `PLAN.md`'s settlement ledger with one entry per
`E-###`, then generate the summary **from that ledger**. Writing the summary first and the
ledger afterward defeats the check: the ledger exists so the report cannot say more than the
run earned.

Each entry records one outcome:

| Outcome | Means |
|---|---|
| `observed` | The evidence this experience's `settled_by` requires actually exists |
| `unobserved` | The check that would settle it ran and did not establish it |
| `exception` | The check did not run, was waived, or is reserved for a human |

`evidence` quotes or names the concrete thing that settled it — the structured state-proof
line, the load marker, the human's reported observation, the user's acceptance. `observed`
also records `evidence_kind`, and it must be evidence that experience's `settled_by` can
actually accept: a `tier-2-structured` experience is not `observed` because tier-1 passed,
and a `headed-human` experience no human looked at is an `exception`. `unobserved` and
`exception` both require a `note` saying what is missing. Then run:

```bash
python ${GAME_TOOLS_DIR}/deliverable_trace.py --design DESIGN.md --plan PLAN.md
```

This is the one validator that runs here rather than before SPEC, because it is the only
check that compares what was promised against what happened. It fails on a required
experience with no settlement and on an outcome that outruns its evidence type.

An `unobserved` or `exception` outcome is not a failure to hide — it is the honest state of a
run whose harness could not reach its scenario, or whose art nobody has looked at yet. What
it may never become is silence.

### Report from the ledger

> Built **<Title>** (Common relic). <Claim restated in one sentence.>
>
> What was proved: <each `observed` experience in plain words>.
> Not proved: <each `unobserved`/`exception` experience, with what is missing>.
> Not included: <the excluded experiences that a reader of the claim would ask about>.
>
> Artifacts are in `mods/<ModName>/`.

Say which tier each claim rests on in the user's own terms — "its effect fired automatically
in its self-test scenario" for a structured proof, "it loads and registers, but the effect
hasn't been observed yet" for tier-1 only, "you accepted template art for this build" for a
`user-decision`. This is `INV-1` in the form the user reads.

Two failures this replaces, both from the same real run: a closing summary that called a
mechanic verified while the same record disclosed the harness never drove it, and a
deliverable whose accumulated placeholders were never read back as one thing. If every
required experience is `observed`, say so plainly and stop — a fully earned claim needs no
hedging.
