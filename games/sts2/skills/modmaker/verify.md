# Verify — prove it loads (tier-1), then that the effect fires (tier-2)

Goal: verify on **observed reality**, not "it compiled". Two tiers. Always report
which tier you reached; never claim the effect is verified when only load was.

## Tier-1 — does it load? (automated, guaranteed)

Launch STS2 without Steam, wait, then grep the log for the load marker and any
mod-named errors.

```powershell
$offset = pwsh ${GAME_TOOLS_DIR}/launch.ps1
pwsh ${GAME_TOOLS_DIR}/grep_log.ps1 -ModName <ModName> -SinceOffset $offset
```

- `launch.ps1` ensures `steam_appid.txt` (=2868840) exists, snapshots the log
  size, launches `SlayTheSpire2.exe`, waits ~25s, closes it, and prints the byte
  offset so the grep reads only this run.
- `grep_log.ps1` passes if it finds `[T2MOD-SELFTEST] <ModName> loaded ok` **and**
  no error/exception lines naming the mod. It also reports the `RUNNING MODDED` flag.

**PASS** = marker found, no mod-named errors. **FAIL** → consult sts2-api
`errors.md` (registration/load section) — e.g. missing `[Pool]` throws at
registration; a raw-key title means the loc keys don't match `Id.Entry`. Fix, rebuild, re-verify once.

This is the guaranteed check: it proves "installs + loads + registered".

## Tier-2 — does the effect fire? (best-effort, the headline)

**M2: user-guided via the dev console** (automation is M5). Tell the user, plainly:

1. Start a run in STS2 (with the mod loaded — the tier-1 launch confirmed it loads).
2. Open the **dev console** with the **`` ` `` (backtick)** key (also `'`, `*`, `^`,
   or `Shift+8`); close with `Esc`. Debug commands are auto-enabled because the game
   is running modded.
3. Grant the relic: `relic add <PREFIX>-<SLUG>` (e.g. `relic add GAMBLERSCOIN-GAMBLERS_COIN`;
   a unique substring like `GAMBLERS` also works — matching is `Contains`, uppercased).
4. Trigger the effect (for a combat-start relic: enter a combat).
5. Confirm the observed change matches intent (e.g. energy 3 → 0), and re-grep the
   log for the `fired:` marker:

```powershell
pwsh ${GAME_TOOLS_DIR}/grep_log.ps1 -ModName <ModName> -SinceOffset 0
```

If the console won't open or `relic add` says "Unable to create relic", see
errors.md "Verification harness". Report the tier-2 result as **observed** only if
the marker fired and the user saw the change; otherwise report tier-1 only.

## Finalize

Update `PLAN.md` (check the verify boxes for the tiers actually reached). Then
summarize for the user in plain language:

> Built **<Title>** (Common relic). It **loads in-game** (verified) and its effect
> **<fired / is written but not yet observed>**. Artifacts are in
> `mods/<ModName>/`. <If tier-2 not observed: how they can check it themselves.>

Be honest about the tier. A loaded-but-effect-unobserved mod is tier-1, not tier-2.
