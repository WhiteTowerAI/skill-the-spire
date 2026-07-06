# Repair — read the real error, fix one thing, re-verify

Goal: a **bounded** sub-loop shared by `build.md` (5), `verify.md` tier-1 (6), and
the tier-2 check (7). When a stage fails, come here, diagnose from the **real
error** (never a guess), apply **one** fix, re-run **only the failed stage**, and
either converge or stop with an honest report. Auto-repair is bounded, not magical
(~70% converge in the literature) — cap it and hand back a clear failure.

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

- **build (R1):** the diagnostic lines `build.ps1` prints on failure, and the full
  `<ProjectDir>/.build.log` if you need context. Key on the **compiler code +
  symbol** (`CS0246: type 'PlayerCmd' not found`), not the prose.
- **verify tier-1 (load):** `grep_log.ps1`'s verdict plus the `godot.log` lines it
  surfaces. Two distinct failures: **marker NOT FOUND** (did it even load / did we
  inject the marker?) vs **error/exception lines naming the mod** (it loaded but
  threw). The `RUNNING MODDED` flag disambiguates — see errors.md.
- **verify tier-2 (effect):** the observed in-game behavior vs SPEC, plus the
  `fired:` marker (present? values wrong?). "No effect" and "wrong effect" are
  different signatures with different fixes.

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
- tier-2 fix → rebuild, re-launch, re-grant, re-observe.

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

`errors.md` is append-only and is what makes this loop faster next time. But the
published `.claude/skills/` copy is git-ignored and regenerated by `publish.sh` —
**do not edit it at runtime.** Instead:

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
