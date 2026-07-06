# Canary matrix — the self-test regression suite (M4.5 ②)

> **Maintainer-only. NOT shipped** (`publish.sh` renders only
> `games/sts2/skills/{modmaker,sts2-api}`; this `tests/` tree is out of scope). This
> is the skill's own regression suite: **one minimal mod per element type**, each
> scaffolded → authored per its recipe → built → tier-1 load-verified. It exists to
> catch recipe/toolchain regressions **with zero user tests** — the class of bug the
> BloodAndFury run hit (`power.md` shipped an analyzer-invalid loc set because the
> recipe had never actually been built).
>
> **This matrix is the "golden set."** It replaces the ad-hoc hand-built
> `m1-gamblers-coin` as the reference for "what correct current pipeline output looks
> like." (m1 is now just a *substrate proof* — the one artifact the pipeline can't
> reproduce — not a template. See memory `sts2-m45-analyzer-mined` /
> `sts2-m4-cardprep-progress`.)

## The rule this enforces

> **A recipe is PROVISIONAL until it has one green build behind it.**

`power.md` (commit 5536eee) was pure documentation — an unexecuted code path — until
this matrix built it. Card/potion/relic each already had a real acceptance mod
(Firebolt/Firebomb/Gambler's Coin), so their recipes were proven; power and the
combo path were not. Any *new* recipe added later must gain a canary here before it's
considered done.

## The five cells

| Cell | Mod | Element(s) | What it proves in the recipe |
|------|-----|-----------|------------------------------|
| relic | `CanaryRelic` | relic `Bauble` (CANARYRELIC-BAUBLE) | `[Pool(SharedRelicPool)]`, template base class, `AfterSideTurnStart` + turn-1 guard, `PlayerCmd.GainEnergy`, 3-key `relics.json` (title/description/**flavor**) |
| potion | `CanaryPotion` | potion `Fizz` (CANARYPOTION-FIZZ) | the **hand-made `Potions/` + base class** (template scaffolds none), `[Pool(SharedPotionPool)]`, the three abstract props, `OnUse`, `CreatureCmd.Damage`, 2-key `potions.json` |
| card | `CanaryCard` | card `Jolt` (CANARYCARD-JOLT) | `[Pool(ColorlessCardPool)]`, template card base, `OnPlay`, `DamageCmd.Attack(...)` fluent builder, `DamageVar`/`OnUpgrade`, 2-key `cards.json`, **the `ArgumentNullException.ThrowIfNull(cardPlay.Target)` guard** (without it → CS8604) |
| power | `CanaryPower` | power `Smolder` (CANARYPOWER-SMOLDER) | **NO `[Pool]`** (auto-discovered), `Type`+`StackType`, `AfterSideTurnStart` hook, `PowerCmd.Decrement`, and the **3-key `powers.json` incl. `.smartDescription`** — the STS001 case |
| combo | `CanaryCombo` | card `Charge` + custom power `Signal` | the **card → `PowerCmd.Apply<CustomPower>`** dependency path (the BloodAndFury multi-element shape) in one mod: `PowerVar<Signal>`, `DynamicVars["Signal"]`, both loc tables |

## How to run (maintainer, on the STS2 dev box)

Canary projects are **regenerated on demand outside the repo** (like every test mod
since M1 — repo stays clean; trust regenerate over hoarding). The steps per cell:

1. `mkdir canary-<x> && cd canary-<x> && dotnet new alchyrsts2contentmod -n Canary<X> -M OpenMod`
2. Uncomment `BSchneppe.StS2.PckPacker` in the csproj.
3. Author the minimal element per its recipe (see the file list in
   `canary-results.md` for the exact minimal bodies used — copy-paste ready).
4. Add `Logger.Info("[T2MOD-SELFTEST] Canary<X> loaded ok")` at the end of
   `MainFile.Initialize()`.
5. `dotnet build Canary<X>.csproj -c Release` → expect **0 warnings, 0 errors** + a
   `.pck` copied to `mods/Canary<X>/`.
6. Once all five are built: `tools/launch.ps1 -WaitSeconds 35` (one launch loads all
   five), then `tools/grep_log.ps1 -ModName Canary<X>` per cell → expect
   `[PASS] Tier-1 verified`.

## Status

All five **build green (0/0, `.pck` emitted)** and **tier-1 PASS** (load marker +
zero mod-named errors, one launch) — see `canary-results.md` for the run record and
the two recipe fixes this suite surfaced. Tier-2 (effect fired) is out of scope here
— that's M5 (headless behavior test).

## Future

- When M5 automates tier-2, extend each cell to assert its `fired:`/`played:` marker.
- Add a cell for any new element type or recipe before calling that recipe done.
- Consider a single driver script (`run-canaries.ps1`) that regenerates + builds all
  five and greps once; deferred until it earns its keep (the manual steps are cheap
  and the per-cell authoring is the point).
