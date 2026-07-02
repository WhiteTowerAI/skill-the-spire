# M3 Repair Loop Results

> Companion to IMPLEMENTATION_PLAN.md §5 (M3) and M2_RESULTS.md. Records the
> outcome of M3: adding the bounded automated repair loop (`repair.md`), wiring it
> into the pipeline, growing `errors.md`, and proving the loop diagnoses → fixes →
> re-verifies deliberately-broken specs within the retry cap. Run 2026-07-02 on the
> same Windows box as M0/M1/M2 (STS2 v0.107.1 + .NET 9.0.300 + BaseLib active).

## Verdict: M3 GATE PASSED — both broken specs repaired within the cap

Two deliberately-broken relic specs were each diagnosed → fixed → re-verified in
**1 repair attempt**, driving the real `build.ps1` / `launch.ps1` / `grep_log.ps1`
tools and the new `repair.md` loop. One covers a build-time failure (fully
automated), the other the headline "green build ≠ loads" load-time failure.

## What was built

- **`repair.md`** — a bounded sub-loop shared by `build.md` (5) and `verify.md`
  tier-1/tier-2 (6). Inherits godogen's debugging discipline (read the real error,
  not the exit code; when code and observed reality disagree, trust reality) and
  this project's hard limits:
  - **Max 3 attempts per stage**; **same signature surviving a fix → stop
    immediately** (don't patch the same spot a third time — change the hypothesis).
  - **One change per attempt** (so the fix that worked is unambiguous, and the
    `errors.md` entry it seeds is clean).
  - **Never fake success**: a tier is "passed" only when its own re-verify passes on
    observed reality (build 0/0; tier-1 marker greppable AND no mod-named errors;
    tier-2 effect observed).
  - Per-stage "real signal" definitions, a "don't guess an API — ground it" rule for
    unknown-symbol misses, a rebuild-before-relaunch rule, and the honest
    stop-and-report template on exhaustion.
- **Pipeline wiring** — `SKILL.md` scope updated to "M3 relic + bounded repair",
  stage table + pipeline diagram add repair as step 8; `build.md` / `verify.md`
  failure branches now hand off to `repair.md` instead of "stop, don't loop".
- **`errors.md` grown** — two new entries: guessed-API compile errors
  (CS0103/CS0246/CS0117/CS1061 → don't guess again, ground against the recipe /
  decompiled dll) and tier-1 "RUNNING MODDED = YES but marker missing → marker not
  injected into MainFile / not rebuilt" (a generalization of the M2 author.md doc
  bug, kept distinct from the log-rotation false-FAIL entry).

## Acceptance run (project: `D:\26summer_intern\m3-repair-test`, outside this repo)

Scaffolded `dotnet new alchyrsts2contentmod -n M3PoolTest -M OpenMod`; relic class
`DoublerCoin` (combat-start double energy), id `M3POOLTEST-DOUBLER_COIN`. Two
defects were injected one at a time. Full attempt log lives in that project's
`MEMORY.md`.

### Test A — build stage: fabricated energy API (fully automated)
- **Defect:** `await EnergyCmd.Add(before, Owner)` — a guessed API.
- **Signal:** `build.ps1` FAILED, `CS0103: 名称 "EnergyCmd" 不存在`.
- **Repair (1 attempt):** errors.md hit (guessed-API family) → the "don't guess
  again, ground it" rule → real API from `recipes/relic.md` is
  `PlayerCmd.GainEnergy(decimal, Player)`. One change, rebuild → **0/0, PASS**.

### Test B — tier-1 load stage: missing `[Pool]` (the headline case)
- **Defect:** removed `[Pool(typeof(SharedRelicPool))]` from the relic.
- **Build:** still **clean (0/0)** — the compiler can't see it. Bad `.dll` copied to
  `mods/`. This is exactly the "a green build does not mean it loads" failure that
  tier-1 exists to catch.
- **Signal:** launch + `grep_log.ps1` → FAIL. `RUNNING MODDED = YES` and error line
  `System.Exception: Model ...DoublerCoin must be marked with a PoolAttribute`.
- **Repair (1 attempt):** errors.md direct hit → re-add `[Pool]`. Rebuild (so the
  fix reaches the game) → relaunch → re-grep → **PASS** (marker found, no errors).

## Findings from running it (not predicted in advance)

1. **The error-line check is load-bearing.** In Test B the load marker was still
   FOUND even though registration threw — the marker is logged in
   `MainFile.Initialize()` (which ran), while the relic registration throws
   separately via BaseLib reflection. Marker-alone would have **false-PASSed**; the
   "marker AND no mod-named errors" double condition is what caught the failure.
   Confirms `grep_log.ps1`'s two-part verdict is necessary, not belt-and-suspenders.
2. **errors.md grew from the run.** A bare fabricated name resolves to **CS0103**,
   not the CS0246/CS0117/CS1061 the entry originally listed. CS0103 was added to the
   guessed-API signature list and the skill re-published — a live instance of the
   "errors.md is a compounding moat, seeded by real failures" design.
3. **The rebuild-before-relaunch rule mattered.** A tier-1 code fix that skips the
   rebuild re-verifies a stale `.dll` and looks like the fix failed. `repair.md`
   states this explicitly; Test B exercised it.

## Notes / deferred

- Both tests converged on the **first** attempt, so the 3-attempt cap and the
  same-signature-stop were exercised by design/wording but not by a real
  non-converging run. A future harder spec (e.g. a subtly wrong Cmd sequence) would
  stress the multi-attempt path and the honest give-up report.
- `repair.md` and the stage files reference the tools as `pwsh`; on this box the
  tools run under Windows PowerShell (`powershell.exe`). The scripts are
  shell-agnostic PowerShell — no change needed, but worth noting for the one-command
  install work (M5) where the launcher must pick the right PowerShell.
- Test project kept at `D:\26summer_intern\m3-repair-test` (outside the repo, like
  m1/m2), so it is a reference, not part of the published skill.

## Next step: M4

Breadth within STS2 (card/potion recipes, harder interview) + the art/sprite
pipeline. The repair loop now backstops those new element types as they land.
