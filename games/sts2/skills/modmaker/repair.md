# Repair — read the real error, fix one thing, re-verify

> A failing stage is the moment `INV-7` is most tempting to break. The pinned RitsuLib
> profile is still the only active path here.

Goal: classify a discovered difference before changing anything, then either enter the
bounded technical loop, return to the owning artifact, or block on a shared capability.
Diagnose from the **real error** (`INV-2`) and keep the complete player-facing operation
together.

Do not generalize one failed generated route to the whole documented feature Package. If a
pinned API or lifecycle defect is reproducible, record the smallest affected consumer as a
known limitation and preserve the rest of the Package.

## Classify before a fix

Compare observed reality with the accepted `D/E/OP` operation, then write one current
`open-mod-repair-routing/v1` decision in PLAN and run `repair_trace.py`. Use exactly one route:

| Classification | Owner | Action |
|---|---|---|
| `implementation-equivalent` | `MEMORY.md` | No player-facing meaning changes. Apply one technical fix and rerun the earliest invalid stage. |
| `contract-fulfillment` | `SPEC.md` | The accepted operation remains exact and supported. Correct its earliest wrong SPEC/output layer and reverify every affected consumer. |
| `accepted-semantic-change` | `DESIGN.md` | Anything a player notices or understands changes. Stop, show the smallest revision, obtain explicit acceptance, update DESIGN first, then affected SPEC operations. |
| `missing-capability` | `shared recipe/reference` | The exact route is absent, unreachable, unmaintained, or violates its claim. Record the exact project `blocking_gap`, block upstream, and do not create a consumer-local substitute. |

Use the active object below; `affected_*` ids must already exist and trace to each other.
List invalidated stages in pipeline order and make `reopened_stage` the first one. A blocked
missing capability uses an empty stage list and `null` reopened stage.

```json
{
  "trigger_stage": "verify-tier-2",
  "observed_difference": "The Card deals 9 damage but enters Discard instead of Exhaust",
  "classification": "contract-fulfillment",
  "owning_artifact": "SPEC.md",
  "affected_design_ids": ["D-001"],
  "affected_experience_ids": ["E-001"],
  "affected_operation_ids": ["OP-001"],
  "invalidated_stages": ["author", "build", "verify-tier-1", "verify-tier-2", "finalize"],
  "reopened_stage": "author",
  "routing_status": "repairing"
}
```

Allowed statuses are `repairing`/`blocked` for the two technical routes;
`awaiting-user-acceptance`/`revision-accepted`/`blocked` for a semantic change; and
`blocked-upstream` for a missing capability. An implementation-equivalent repair cannot name
an affected experience. Clear every affected settlement before validation.

Uncertainty is player-visible risk: classify it as `accepted-semantic-change`, not as a
technical fix. A harness/setup failure may be implementation-equivalent, but it stays distinct
from a Mod behavior failure. Only `implementation-equivalent` and `contract-fulfillment`
consume the three-attempt budget below.

## Inspect the complete operation

For each affected `OP-###`, read its co-located surface envelope, driver, proof matrix, and
cited route together. Follow a shared value or meaning through every applicable consumer:
behavior, lifecycle/state/reset, rules text and engine-composed text, keyword/DynamicVar/Hover
Tips, shipped localization, preview values, presentation, and proof. A surface may say a
consumer is not applicable; silence is not a reason to skip it. Preserve unaffected operations
and every `PRESERVE` queue entry. A localization repair follows `INV-10`: update both required
languages and preserve table/key/token parity rather than patching only the language that exposed
the failure.

The loop's own rule, on top of the invariants: **if an approach fails twice, change the
hypothesis — don't keep patching the same spot.**

## Hard limits (do not exceed)

- **Max 3 repair attempts per stage.** An attempt = one hypothesis → one change →
  one re-run of the failed stage.
- **Only the two technical routes consume attempts.** A DESIGN-first decision or an upstream
  capability block is routing, not a failed consumer fix.
- **Same signature twice with no change → stop immediately.** If the identical
  error survives a fix (same compiler code + symbol, same log line, same wrong
  behavior), the hypothesis was wrong. Do NOT try a third near-identical tweak —
  step back to a different root cause, and if you don't have one, stop and report.
- **One change per attempt.** Changing three things at once means you can't tell
  which fixed (or broke) it, and it poisons the `errors.md` you write afterward.
- **A repaired stage passes on its own re-verify, or not at all** (`INV-1`). What each
  stage's own re-verify is: build `0/0`; tier-1 marker greppable with no mod-named errors;
  tier-2 effect observed.
- **A workaround for a broken route is not a repair** (`INV-9`). If the fix you are reaching
  for rebuilds a behavior the cited recipe/reference was supposed to provide, stop: that route
  is failing its own contract, and reimplementing it here hides the failure from every later
  Mod while leaving this one carrying an unmaintained copy. It is a scope change that belongs
  in `DESIGN.md` and `SPEC.md`, plus a maintainer note in the project's `MEMORY.md`
  (`INV-8`) — not an attempt.

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
  4. RE-RUN from the earliest invalidated stage
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

Re-run from PLAN's earliest invalidated stage, not the whole pipeline:

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

On convergence: mark the stage done in `PLAN.md`, move the concise completed repair record to
`MEMORY.md`, clear `active_repair`, and continue through only the invalidated downstream stages.
On stop: leave the report above and active failed-stage state; do not advance.

A fix that changes whether a required experience holds must not leave `PLAN.md`'s settlement
ledger describing the run before the fix. Clear the affected `E-###` entries so Finalize
settles them against the rebuilt Mod; a stale `observed` from an earlier attempt is evidence
for a build that no longer exists (`INV-2`).

Before Finalize, `repair_trace.py --finalize` must see `active_repair: null`. A rejected
semantic alternative preserves the original DESIGN and stays blocked or is reclassified as
contract fulfillment; it never licenses the convenient substitute.
