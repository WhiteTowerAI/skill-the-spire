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
> reproduce — not a template. See `canary-results.md` for the historical acceptance
> runs and recipe fixes, and `content-capability-graph.md` for the current support/evidence
> ledger.)

## The rule this enforces

> **A recipe is PROVISIONAL until it has one green build behind it.**

`power.md` (commit 5536eee) was pure documentation — an unexecuted code path — until
this matrix built it. Card/potion/relic each already had a real acceptance mod
(Firebolt/Firebomb/Gambler's Coin), so their recipes were proven; power and the
card→power interaction path were not. Any *new* recipe added later must gain a canary
here before it is considered done.

## The nine cells

| Cell | Mod | Element(s) | What it proves in the recipe | Tier-2 harness DRIVER + marker |
|------|-----|-----------|------------------------------|--------------------------------|
| relic | `CanaryRelic` | relic `Bauble` (CANARYRELIC-BAUBLE) | `[Pool(SharedRelicPool)]`, template base class, `AfterSideTurnStart` + turn-1 guard, `PlayerCmd.GainEnergy`, 3-key `relics.json` (title/description/**flavor**) | `BeforeCombat`: `RelicCmd.Obtain` → auto-fires at combat start → `Bauble fired: +1 energy` |
| potion | `CanaryPotion` | potion `Fizz` (CANARYPOTION-FIZZ) | the **hand-made `Potions/` + base class** (template scaffolds none), `[Pool(SharedPotionPool)]`, the three abstract props, `OnUse`, `CreatureCmd.Damage`, 2-key `potions.json` | `InCombat`: `TryToProcure` → `EnqueueManualUse(enemy)` → `Fizz used: 10 dmg` |
| card | `CanaryCard` | card `Jolt` (CANARYCARD-JOLT) | `[Pool(ColorlessCardPool)]`, template card base, `OnPlay`, `DamageCmd.Attack(...)` fluent builder, `DamageVar`/`OnUpgrade`, 2-key `cards.json`, **the `ArgumentNullException.ThrowIfNull(cardPlay.Target)` guard** (without it → CS8604) | `InCombat`: `GainEnergy` → spawn to hand → `CardCmd.AutoPlay(_, _, enemy)` → `Jolt played: 6 dmg to target` |
| power | `CanaryPower` | power `Smolder` (CANARYPOWER-SMOLDER) | **NO `[Pool]`** (auto-discovered), `Type`+`StackType`, `AfterSideTurnStart` hook, `PowerCmd.Decrement`, and the **3-key `powers.json` incl. `.smartDescription`** — the STS001 case | a power isn't a top-level driver — its marker is asserted through the interaction cell (a card applies it), matching how powers actually ship |
| keyword interaction | `CanaryKeyword` | card `Resonant Guard` + custom keyword `Resonant` | `[CustomEnum]`, `[KeywordProperties(After)]`, `card_keywords.json`, `CanonicalKeywords`, and the display-vs-behavior boundary | `CombatPlayer` autoplays the host Card → assert custom keyword membership `present=True` **and** the named Block rule changes state `0 -> 7` |
| card-enchantment interaction | `CanaryEnchantment` | card `Etched Strike` + custom enchantment `Guarded` | `CustomEnchantmentModel`, `enchantments` loc, `CardCmd.Enchant`, attached Amount, and host `OnPlay` modification | `CombatPlayer` asserts `attached=True amount=5`, autoplays the host, then observes `Guarded fired: ... block 0 -> 5` |
| card-orb interaction | `CanaryOrb` | card `Take Shelter` + custom orb `Shelter` | `CustomOrbModel`, inline `OrbLoc`, zero-slot Channel behavior, queue ownership, passive + evoke | `CombatPlayer` autoplays host Card → queue `present=True capacity=1` → passive Block `0 -> 2` → evoke Block `2 -> 7` |
| interaction | `CanaryCombo` *(historical project name)* | card `Charge` + custom power `Signal` | the **card → `PowerCmd.Apply<CustomPower>`** dependency path (the BloodAndFury multi-element shape) in one mod: two real element nodes, an `applies` interaction, `PowerVar<Signal>`, `DynamicVars["Signal"]`, and both loc tables | `CombatPlayer` drives the real source type (`card`): play `Charge` (`Charge played: applied Signal`) → assert the dependent `Signal fired:` observation — the interaction-edge proof |
| enemy encounter | `CanaryEncounter` | `CanaryMite : CustomMonsterModel` + `CanaryMiteEncounter : CustomEncounterModel` | `CustomMonsterModel` (no `[Pool]`, auto `RegisterType`), `GenerateMoveStateMachine` + `MoveState("PECK", …, SingleAttackIntent(6))` + `.FollowUpState = peck`, `CustomEncounterModel(RoomType.Monster)` (auto `AddEncounter`), `IsValidForAct`, `AllPossibleMonsters` / `GenerateMonsters`, `monsters.json` + `encounters.json` loc; **bug fix**: monster attacks use `.FromMonster(this).Execute(null)` NOT `.Targeting(target)` | **`CombatEnemy` scenario**: enter via `ModelDb.Encounter<CanaryMiteEncounter>().ToMutable()` + `EnterRoomDebug`; assert `Enemies.FirstOrDefault(e => e.Monster is CanaryMite)` found; wait Play phase; `EndTurn` (void); wait Play phase again; assert player `hp [before] -> [after] delta=6` |

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
7. **Tier-1** (load): `python <open-mod>/games/sts2/tools/launch.py --wait-seconds 35`.
   A single ordinary launch may load every enabled canary, then run
   `python <open-mod>/games/sts2/tools/grep_log.py --mod-name Canary<X>` per cell →
   expect `[PASS] Tier-1 verified`.
8. **Tier-2** (effect fires, per driving cell — each self-drives its own combat):
   `python <open-mod>/games/sts2/tools/launch.py --self-test --mod-name Canary<X>` then
   `python <open-mod>/games/sts2/tools/grep_log.py --mod-name Canary<X> --tier2-pattern
   "fired|used|played"` → expect `[PASS] Tier-2 verified`. The verifier separately requires
   `<ModName> selftest done`; a terminal line is never accepted as the effect proof. For
   `CanaryCombo`, confirm both the `Charge played:` and dependent `Signal fired:` markers.

## Status

The original five-cell M4.5 baseline **built green (0/0, `.pck` emitted)** and passed
Tier 1 in one ordinary launch. Its four Tier-2 driving cells later passed on the dev box
(2026-07-06): relic/card/potion each drove its effect and the historical `CanaryCombo`
project proved an interaction chain (card applies power → `EndTurn` → power fires), all
with zero interaction; power is asserted through that relationship.
**M6 Mechanic Vocabulary (2026-07-10): keyword/enchantment/orb PASS** — three CombatPlayer
cells live-verified. **M6 Enemy Encounter (2026-07-10): CanaryEncounter PASS** — first
`CombatEnemy` scenario seam earned: custom encounter started, CanaryMite present, PECK move
executed, player HP delta observed; key correction logged (monster `.FromMonster().Execute(null)`
not `.Targeting()`). See `canary-results.md` §M6 Enemy Encounter for the run record.
See `canary-results.md` for the per-cell markers and the four harness bugs the live run
fixed. **Run one cell at a time** —
`--t2selftest` arms every loaded harness mod, so parking all but the cell under test avoids
a main-menu collision. **This includes Overclock** — park it along with all Canary* mods
before any harness run.

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
