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

| Cell | Mod | Element(s) | What it proves in the recipe | Tier-2 harness DRIVER + marker |
|------|-----|-----------|------------------------------|--------------------------------|
| relic | `CanaryRelic` | relic `Bauble` (CANARYRELIC-BAUBLE) | `[Pool(SharedRelicPool)]`, template base class, `AfterSideTurnStart` + turn-1 guard, `PlayerCmd.GainEnergy`, 3-key `relics.json` (title/description/**flavor**) | `BeforeCombat`: `RelicCmd.Obtain` → auto-fires at combat start → `Bauble fired: +1 energy` |
| potion | `CanaryPotion` | potion `Fizz` (CANARYPOTION-FIZZ) | the **hand-made `Potions/` + base class** (template scaffolds none), `[Pool(SharedPotionPool)]`, the three abstract props, `OnUse`, `CreatureCmd.Damage`, 2-key `potions.json` | `InCombat`: `TryToProcure` → `EnqueueManualUse(enemy)` → `Fizz used: 10 dmg` |
| card | `CanaryCard` | card `Jolt` (CANARYCARD-JOLT) | `[Pool(ColorlessCardPool)]`, template card base, `OnPlay`, `DamageCmd.Attack(...)` fluent builder, `DamageVar`/`OnUpgrade`, 2-key `cards.json`, **the `ArgumentNullException.ThrowIfNull(cardPlay.Target)` guard** (without it → CS8604) | `InCombat`: `GainEnergy` → spawn to hand → `CardCmd.AutoPlay(_, _, enemy)` → `Jolt played: 6 dmg to target` |
| power | `CanaryPower` | power `Smolder` (CANARYPOWER-SMOLDER) | **NO `[Pool]`** (auto-discovered), `Type`+`StackType`, `AfterSideTurnStart` hook, `PowerCmd.Decrement`, and the **3-key `powers.json` incl. `.smartDescription`** — the STS001 case | a power isn't a top-level element — its marker is asserted via the **combo** cell (a card applies it), matching how powers actually ship |
| combo | `CanaryCombo` | card `Charge` + custom power `Signal` | the **card → `PowerCmd.Apply<CustomPower>`** dependency path (the BloodAndFury multi-element shape) in one mod: `PowerVar<Signal>`, `DynamicVars["Signal"]`, both loc tables | `InCombat` walks SPEC interaction: play `Charge` (`Charge played: applied Signal`) → assert the **dependent** `Signal fired:` marker — the interaction-link proof |

## How to run (maintainer, on the STS2 dev box)

Canary projects are **regenerated on demand outside the repo** (like every test mod
since M1 — repo stays clean; trust regenerate over hoarding). The steps per cell:

1. `mkdir canary-<x> && cd canary-<x> && dotnet new alchyrsts2contentmod -n Canary<X> -M OpenMod`
2. Uncomment `BSchneppe.StS2.PckPacker` in the csproj.
3. Author the minimal element per its recipe (see the file list in
   `canary-results.md` for the exact minimal bodies used — copy-paste ready).
4. Add `Logger.Info("[T2MOD-SELFTEST] Canary<X> loaded ok")` at the end of
   `MainFile.Initialize()`.
5. **(M5) Emit the tier-2 harness** per `reference/selftest-harness.md`: add
   `Canary<X>Code/SelfTest.cs`, fill the DRIVER body from the table above, and append
   `if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();` after the load marker.
   Each element already logs its `fired:`/`played:`/`used:` marker (see the bodies in
   `canary-results.md`), so the harness only has to *trigger* it.
6. `dotnet build Canary<X>.csproj -c Release` → expect **0 warnings, 0 errors** + a
   `.pck` copied to `mods/Canary<X>/`.
7. **Tier-1** (load): `python <open-mod>/games/sts2/tools/launch.py --wait-seconds 35`
   (one launch loads all five), then `python <open-mod>/games/sts2/tools/grep_log.py
   --mod-name Canary<X>` per cell → expect `[PASS] Tier-1 verified`.
8. **Tier-2** (effect fires, per driving cell — each self-drives its own combat):
   `python <open-mod>/games/sts2/tools/launch.py --self-test --mod-name Canary<X>` then
   `python <open-mod>/games/sts2/tools/grep_log.py --mod-name Canary<X> --tier2-pattern
   "fired|used|played|selftest done"` → expect `[PASS] Tier-2 verified`. For
   `CanaryCombo`, confirm both the `Charge played:` and dependent `Signal fired:` markers.

## Status

All five **build green (0/0, `.pck` emitted)** and **tier-1 PASS** (load marker +
zero mod-named errors, one launch) — see `canary-results.md` for the run record and
the two recipe fixes this suite surfaced. **Tier-2 harness (M5): ALL FOUR driving cells
PASS on the dev box (2026-07-06)** — relic/card/potion each drove their effect and combo
proved the interaction chain (card applies power → `EndTurn` → power fires), all with zero
interaction; power is asserted through combo. See `canary-results.md` for the per-cell
markers and the four harness bugs the live run fixed. **Run one cell at a time** —
`--t2selftest` arms every loaded harness mod, so parking all but the cell under test avoids
a main-menu collision.

## Future (M6+)

- New content support requires **two proofs** before it is advertised:
  1. **Type Canary** — registration, clean build/package, and tier-1 load.
  2. **Scenario Canary** — real behavior through the content's host and reusable scenario
     adapter, with an observable state/marker assertion.
- A vertical-slice canary may prove several inseparable types together (for example,
  monster + encounter) instead of creating meaningless isolated cells.
- Consider a single Python driver that regenerates/builds the matrix, runs tier-1 once,
  then parks/arms one self-test mod at a time for tier-2. Defer until M6's second scenario
  shape proves the abstraction earns its maintenance cost.
