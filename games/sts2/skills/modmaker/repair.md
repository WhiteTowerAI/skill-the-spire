# Repair — read the real error, fix one thing, re-verify

> The pinned RitsuLib scaffold/build profile is the only active path. Never repair a new
> project by restoring BaseLib or an old template workaround.

Goal: a **bounded** sub-loop shared by `build.md` (5), `verify.md` tier-1 (6), and
the tier-2 check (7). When a stage fails, come here, diagnose from the **real
error** (never a guess), apply **one** fix, re-run **only the failed stage**, and
either converge or stop with an honest report. Auto-repair is bounded, not magical
(~70% converge in the literature) — cap it and hand back a clear failure.

Do not generalize one failed generated route to the whole documented feature Package. If a
pinned API or lifecycle defect is reproducible, record the smallest affected consumer as a
known limitation and preserve the rest of the Package.

This is the M3 deliverable. It inherits godogen's debugging discipline (read the
real log, not the exit code; when code and observed reality disagree, trust
reality) and this project's rule: **if an approach fails twice, change the
hypothesis — don't keep patching the same spot.**

## Hard limits (do not exceed)

- **Max 3 repair attempts per stage.** An attempt = one hypothesis → one change →
  one re-run of the failed stage.
- **Same signature twice with no change → stop immediately.** If the identical
  error survives a fix (same compiler code + symbol, same log line, same wrong
  behavior), the hypothesis was wrong. Do NOT try a third near-identical tweak —
  step back to a different root cause, and if you don't have one, stop and report.
- **One change per attempt.** Changing three things at once means you can't tell
  which fixed (or broke) it, and it poisons the `errors.md` you write afterward.
- **Never fake success.** Only report a tier as passed when its *own* re-verify
  passed on observed reality (build 0/0; tier-1 marker greppable with no mod-named
  errors; tier-2 effect observed). A green build is not a load; a load is not an
  effect.

## The loop

```text
stage failed
   |
 1. CAPTURE the real signal (see "Signals per stage")
   |
 2. LOOK IT UP — query sts2-api errors.md for the signature
   |    hit  -> apply the cataloged fix
   |    miss -> form ONE hypothesis from recipe/quirks + grounding (below)
   |
 3. APPLY exactly one change; record it in MEMORY.md
   |    (attempt N: signature -> hypothesis -> change)
   |
 4. RE-RUN only the failed stage
   |    pass -> return to the pipeline; if this was a NEW (miss) fix, note it
   |            in MEMORY.md as an errors.md candidate (see "Growing errors.md")
   |    fail -> attempts < 3 AND signature changed?  yes -> back to 1
   |                                                 no  -> STOP, report
```

## Signals per stage (what "the real error" is)

Read the artifact, not your memory of what you wrote.

- **build:** first distinguish a `RitsuLib profile FAILED`/`RitsuLib restore FAILED`
  contract error from compiler output. Profile failures are fixed in the package,
  manifest, host, or runtime variant selected by `scaffold.md`; never enter a C# repair
  loop for them. For compiler failures, use the diagnostic lines `build.py` prints and the full
  `<ProjectDir>/.build.log` if you need context. Key on the **compiler code +
  symbol** (`CS0246: type 'PlayerCmd' not found`), not the prose.
- **verify tier-1 (load):** `grep_log.py`'s verdict plus the `godot.log` lines it
  surfaces. Two distinct failures: **marker NOT FOUND** (did it even load / did we
  inject the marker?) vs **error/exception lines naming the mod** (it loaded but
  threw). The `RUNNING MODDED` flag disambiguates — see errors.md.
- **verify tier-2 (effect):** the harness's terminal marker plus its structured
  `state proof:` marker; element `fired/used:` lines are diagnostic only. **Three distinct
  signatures — do not conflate them:**
  1. **`selftest FAILED: <stage>` or launch timeout** → the harness never reached/drove
     combat (menu navigation, node path, or timing). This is a **harness/setup** problem,
     **not an effect bug** — do not "fix" the element for it. Causes: a game version bump
     shifted the scene-tree paths in `NavigateToRunAsync` (re-mine them from the decompile
     per `reference/selftest-harness.md`), or a slow load blew the timeout (raise
     `launch.py --wait-seconds`). If it can't be made to reach combat, fall back to the
     manual dev-console check (verify.md) and report **tier-1 only** — never a tier-2 fail.
  2. **`selftest done` but no matching `state proof:`** → the scenario was reached but the
     expected post-state was not established. Use the diagnostic trigger marker to tell
     "source never ran" from "source ran but state stayed wrong", then fix the effect.
  3. **state-proof assertion reports the wrong observed value** (e.g. `expected=9
     observed=6`, energy unchanged) → effect ran but computes wrong → fix numbers/vars.
  Signatures 2 and 3 are effect fixes; signature 1 is not. For a multi-element
  **interaction**, a missing dependent state proof after `selftest done` localizes the
  break to that directed relationship.
  For a **stateful** source, use the first failed boundary to localize lifetime bugs:
  wrong `N-1` progress means the advancing event/owner guard/phase is wrong; same-combat
  threshold passes but second-combat progress resets means `SavedAttachedState` is missing
  or a combat-end hook cleared it; a combat-local effect leaks into combat 2 when code
  duplicated the turn count instead of reading `PlayerCombatState.TurnNumber`; a failed
  save round trip means the selected adapter's property type/holder or run-save bridge is unsupported.
  Fix that boundary, not the effect's numeric Cmd.
  For a **character resource**, a missing amount/reset points to the registered
  `SecondaryResourceDefinition` id or persistence policy; a changed amount with stale UI
  points to `RegisterCombatUi` visibility/update or a missing explicit refresh after
  buffer-only mutation. A failed payment that changed payoff is a caller-order bug: await
  `SecondaryResourceCmd.Spend` and gate the payoff on its bool. Do not add a duplicate
  integer or restore the historical UI postfix.
  For an **ordered semantic buffer**, cross-combat leakage points to a non-combat key or
  process-wide collection; use `AttachedState<PlayerCombatState,TState>`. Wrong overflow
  means capacity was checked after mutation. Stale/overlapping Card views mean source Cards
  were retained or skipped their native lifecycle; restore normal Play -> Discard instead
  of hiding visuals.
  For a **combat Card pile / ExtraHand**, wrong overflow or order means the explicit
  capacity/Top/Bottom preflight was omitted or performed after `CardPileCmd.Add`. A lost
  Card after cancel points to bypassing RitsuLib's manual-play bridge or moving the Card
  again while targeting. Missing/stale holders point to `CardShouldBeVisible`, the wrong
  pile type, backend `AddInternal`/`RemoveInternal`, or `skipVisuals`; restore the exact
  `reference/card-pile-extra-hand.md` route instead of adding UI patches. Native-Hand
  overlap points to the old default `VanillaHand` fan/offset; numbered-key response means
  idle holders were incorrectly registered with `NPlayerHand`. Restore the fixed compact
  layout and ExtraHand-owned holders rather than patching input. A selected Card that looks
  different from the native Hand, or remaining ExtraHand Cards that stop responding after
  one successful Play, points to a framework bridge that bypassed
  `NPlayerHand.StartCardPlay`; use the repaired RitsuLib native lifecycle instead of adding
  generated Card-play or UI patches.
  For **Scry**, a missing overlay usually means Draw was empty, the amount was nonpositive,
  combat was ending, or a test selector was still installed. A completed Card play while
  the overlay is open means `CardSelectCmd.FromSimpleGrid` was not awaited. Wrong retained
  order means the selected set was iterated instead of filtering the stable seen list.
  Missing discard reactions mean history or `Hook.AfterCardDiscarded` was omitted; do not
  replace either with a custom Scry completion hook. A multiplayer call must fail clearly,
  not silently use the local selector.

## Forming a hypothesis on a miss (no errors.md entry yet)

Don't invent an API. In order:

1. Re-read `quirks.md` and the element recipe (`recipes/relic.md`) — most misses
   are a known footgun stated there but not yet in errors.md as a *signature*.
2. If it's an unknown symbol / signature (`CS0246`, `CS0117`, `CS1061`), you
   guessed an API. **Ground it in the pack**: query sts2-api for the real Cmd/type
   (the recipe's "Effect building blocks", `errors.md`, `reference/mechanics.md`).
   If the pack doesn't carry it, stop and report a pack gap — do not try another guess.
3. Only then form the single most-likely fix and apply it.

## Which stage to re-run

Re-run the **failed** stage, not the whole pipeline:

- build fix → `build.md` (rebuild once).
- load/tier-1 fix that touches code or the csproj → **rebuild first** (the fix only
  reaches the game through a fresh `.dll`/`.pck`), then re-run `verify.md` tier-1.
- tier-2 fix → rebuild, then re-run the self-test (`launch.py --self-test --mod-name <M>`)
  and re-grep the structured state proof. (Only fall back to manual re-grant/observe if the harness can't
  reach combat — signature 1 above.)

A code change never reaches the running game without a rebuild — don't re-launch
against a stale build and conclude the fix failed.

## When you stop (exhausted or stuck)

Hand the user a plain-language report — no thrashing, no pretending:

> Couldn't get **<ModName>** past **<stage>** automatically. I tried <N> fix(es):
> 1. <signature> → <what I changed> → <what happened>
> 2. …
> The remaining error is: `<exact signature>`. My best guess at the cause is
> <cause>. You could try <next step>, or share this and I'll dig further.

Leave `PLAN.md` marking the stage as failed (not done) and `MEMORY.md` holding the
attempt log, so a later resume doesn't repeat the same three fixes.

## Growing errors.md (the compounding moat)

`errors.md` is curated source knowledge and is what makes this loop faster next time. The
installed/generated payload is regenerated by `publish.sh`; **do not edit it at runtime.**
Instead:

- **A cataloged fix worked (hit):** nothing to add.
- **A new fix worked (miss → converged):** record the new **signature → cause →
  fix** in the project's `MEMORY.md`, flagged `errors.md candidate`. The skill
  maintainer promotes confirmed, recurring ones into the source
  `sts2-api/errors.md` (same as `quirks.md`'s feedback-loop rule). This keeps the
  moat curated, not polluted by one-off noise.

## Return

On convergence: mark the stage done in `PLAN.md`, note the fix in `MEMORY.md`, and
continue the pipeline from where you were (build → verify → finalize). On stop:
leave the report above and the failed-stage state; do not advance.
