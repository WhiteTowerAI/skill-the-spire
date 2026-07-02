# M2 Skill Skeleton Results

> Companion to IMPLEMENTATION_PLAN.md §5 (M2) and M1_RESULTS.md. Records the
> outcome of M2: building the modmaker skill skeleton and proving it reproduces
> the golden relic from one sentence with no repair. Run 2026-07-02 on the same
> Windows box as M0/M1 (STS2 v0.107.1 + .NET 9.0.300 + BaseLib active).

## Verdict: M2 GATE PASSED — both R2 tiers, zero repair to the generated mod

Driving the modmaker stage files, a single sentence produced a **fresh** relic
that built clean, loaded, and fired its effect in real combat — the first time the
pipeline (not a hand-build) carried an idea end to end.

## Input (the one sentence)

> "a relic that at the start of combat flips a coin — heads doubles your energy,
> tails you lose all your energy"

## Why a fresh name ("LuckyCoin", not "GamblersCoin")

Deliberately used a **new name with the same behavior** to prove the skill
*derives from the recipe* rather than recalling the golden mod, and to avoid
clobbering `mods/GamblersCoin/`. Project at `D:\26summer_intern\m2-luckycoin`,
scaffolded `dotnet new alchyrsts2contentmod -n LuckyCoin -M OpenMod`. Derived id
`LUCKYCOIN-LUCKY_COIN` per the recipe's loc-key rule (class `LuckyCoin` → slug
`LUCKY_COIN`; namespace first segment → prefix `LUCKYCOIN`).

## Pipeline run

- **interview / spec**: sentence was unambiguous → relic, combat-start (turn 1),
  coin-flip double/bust. Defaults: Common, SharedRelicPool, placeholder art.
- **scaffold**: `dotnet new alchyrsts2contentmod`; uncommented PckPacker in the csproj.
- **author**: copied the recipe skeleton, filled only the effect (seeded `Rng`,
  `PlayerCmd.GainEnergy(before)` / `SetEnergy(0m)`), wrote flat prefixed
  `relics.json` keys, injected both self-test markers.
- **build**: `dotnet build -c Release`, **0 warnings / 0 errors**; dll+pck+json
  copied to `mods/LuckyCoin/`.
- **verify tier-1**: log showed the full load chain →
  `[LuckyCoin] [T2MOD-SELFTEST] LuckyCoin loaded ok`, no mod-named errors, RUNNING MODDED.
- **verify tier-2**: user granted via dev console `relic add LUCKYCOIN-LUCKY_COIN`,
  entered combat, saw the relic flash and energy double. Log:
  `[LuckyCoin] [T2MOD-SELFTEST] LuckyCoin fired: HEADS (double) energy 3 -> 6`
  — matched what the user saw. (First HEADS branch observed; M1 only ever saw TAILS.)

## Bugs found — all in the verify tooling, not the generated mod

The mod itself needed **zero repair**. Three defects were in the skill's own tooling/docs:

1. **`grep_log.ps1` — log rotation.** STS2 recreates `godot.log` on every launch,
   so `launch.ps1`'s pre-launch byte offset points past the new (shorter) file and
   the seek skipped the marker → false tier-1 FAIL. **Fix:** if the offset ≥ current
   file length, treat as rotated and read from byte 0.
2. **`build.ps1` — localized output.** The mods-path regex keyed off the localized
   ("中文") dotnet copy line and missed → a false WARNING even though the build and
   copy succeeded. **Fix:** match the PATH (`...\mods\<ModName>`, locale-agnostic)
   plus a `dotnet msbuild -getProperty:ModsPath` fallback.
3. **`author.md` — doc bug.** It claimed the scaffolded `MainFile.cs` already logs
   the `[T2MOD-SELFTEST] loaded ok` marker. The Alchyr template does **not** — the
   marker must be injected into `MainFile.Initialize()`, or tier-1 silently has
   nothing to grep. **Fix:** author.md now instructs injecting the load marker.

Benign: log shows `Could not find relic image path: ...lucky_coin.png` → expected
placeholder fallback (M2 has no custom art; errors.md documents this).

## Next step: M3

Add `repair.md` and grow `errors.md`: feed a few deliberately broken specs and
confirm the loop diagnoses → fixes → re-verifies within the retry cap. The three
tooling bugs above are also candidates to encode as errors.md entries.
