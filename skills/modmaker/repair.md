# Repair — read the real error, fix one thing, re-verify

> A failing stage is the moment `INV-7` is most tempting to break. The pinned RitsuLib
> profile is still the only active path here.

Goal: a **bounded** sub-loop shared by `build.md` (5), `verify.md` tier-1 (6), and
the tier-2 check (7). When a stage fails, come here, diagnose from the **real
error** (`INV-2`), apply **one** fix, re-run **only the failed stage**, and
either converge or stop with an honest report. Auto-repair is bounded, not magical
(~70% converge in the literature) — cap it and hand back a clear failure.

Do not generalize one failed generated route to the whole documented feature Package. If a
pinned API or lifecycle defect is reproducible, record the smallest affected consumer as a
known limitation and preserve the rest of the Package.

The loop's own rule, on top of the invariants: **if an approach fails twice, change the
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
- **A repaired stage passes on its own re-verify, or not at all** (`INV-1`). What each
  stage's own re-verify is: build `0/0`; tier-1 marker greppable with no mod-named errors;
  tier-2 effect observed.

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
  Once you know which signature you have, `errors.md` § Behavior localizes it per mechanic —
  stateful cadence, character resource, ordered buffer, and Scry each list which boundary
  their symptom points at. Fix that boundary, not the effect's numeric Cmd.

## Forming a hypothesis on a miss (no errors.md entry yet)

`INV-3` decides where the fix may come from. The order to look:

1. Re-read `quirks.md` and the element recipe (`recipes/relic.md`) — most misses
   are a known footgun stated there but not yet in errors.md as a *signature*.
2. An unknown symbol (`CS0246`, `CS0117`, `CS1061`) is the signature of a guessed API.
   Ground it: query sts2-api for the real Cmd/type (the recipe's "Effect building blocks",
   `errors.md`, `reference/mechanics.md`).
3. Only then form the single most-likely fix and apply it.

## Which stage to re-run

Re-run the **failed** stage, not the whole pipeline:

- build fix → `build.md` (rebuild once).
- load/tier-1 fix that touches code or the csproj → **rebuild first** (the fix only
  reaches the game through a fresh `.dll`/`.pck`), then re-run `verify.md` tier-1.
- tier-2 fix → rebuild, then re-run the self-test (`launch.py --self-test --mod-name <M>`)
  and re-grep the structured state proof. (Only fall back to manual re-grant/observe if the harness can't
  reach combat — signature 1 above.)

Every branch above rebuilds first for the reason `INV-2` gives: a re-launch against a stale
build tests the old code and blames the new fix.

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

`errors.md` is curated source knowledge and is what makes this loop faster next time. `INV-8`
is why a fix you just proved does not go straight into it:

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
