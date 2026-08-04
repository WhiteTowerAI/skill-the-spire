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

## The sixteen cells

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
| monster move vocabulary | `CanaryMonsterVocabulary` | `CanarySentinel` + custom buff `BattleFocus` in one `CanarySentinelEncounter` | `BuffIntent`/custom Power, `SingleAttackIntent` + `DebuffIntent`, `MultiAttackIntent` + `.WithHitCount(2)`, `DefendIntent`, `HealIntent`, explicit `FollowUpState` cycle, exhaustive half-HP `ConditionalBranchState`, and explicit built-in fallback scene | **multi-turn `CombatEnemy`**: two full cycles; assert `NextMove` + `MonsterPerformedMoveEntry`; Power `2 -> 4` and later attack `5 -> 7`; Weak `2`; two-hit totals `8 -> 12`; healthy Block `+5`; wounded HP/Block `+3/+4`; both branch outcomes; final `observed=all` |
| event / World Node | `CanaryEvent` | `GildedSignpost : CustomEventModel` | no `[Pool]`; constructor auto-`AddEvent`; default empty `Acts` means all-act placement; nested in-code `EventLoc` / `EventPageLoc` / `EventOptionLoc`; `Option(FollowTheSign)` slug matches `FOLLOW_THE_SIGN`; `PlayerCmd.GainGold(25m, Owner)` + `SetEventFinished`; verified vanilla portrait placeholder | **`MapNode` scenario**: enter `ModelDb.Event<GildedSignpost>()` via `EnterRoomDebug(RoomType.Event, MapPointType.Unknown, …)`; assert formatted title/option loc; click one real `NEventOptionButton`; independently observe Gold `99 -> 124` (`delta=25`), finished state, and result-page loc |
| stateful cadence | `CadenceCanary` | relic `CadenceBloom` + relic `CombatSundial` | run-persistent `[SavedProperty] int` modulo progress vs combat-owned `PlayerCombatState.TurnNumber`; visible counter updates; no combat-end reset of run progress | **multi-combat `CombatPlayer` scenario**: combat 1 proves progress `1 -> 2` and turn-2 local effect; `SavedProperties.From/Fill` restores `2`; combat 2 turn 1 proves run carry-over threshold `2 -> 0`, Energy `3 -> 4`, plus combat reset `TurnNumber=1` / no second Sundial activation |
| character Foundation | `CanaryCharacter` | selectable `CanaryCharacter` + custom card/relic/potion pools + 10-card starter deck + `TrailMarker` starter relic | `alchyrsts2charmod`; `PlaceholderCharacterModel`; constructor auto-`AddCharacter` with **no manual call**; 14 `CharacterLoc` values + four Architect keys; exact pool/starter ecosystem; standard 3 energy | **`RunStart` + `CombatPlayer` scenario**: locate/click the real custom icon button; registration count=1; run starts HP `72/72`; pools contain expected models; starters `10/5/5/1`; `TrailMarker` changes Energy `3 -> 4` while `MaxEnergy=3`; final `observed=all` |
| capability kernel | `CanaryPatchKernel` | self-contained combat-scoped state + typed hook + UI-host descriptor + one B-risk postfix | version/MVID/signature-gated registry; exact-one target and owned postfix; idempotent repeat; explicit zero-target/failure path; foreign-postfix conflict marker; domain rules outside kernel; no Publicizer/transpiler/`OpenMod.Runtime` | **two-combat `CombatPlayer` scenario**: Tier 1 proves resolved/applied/already-applied markers; combat 1 asserts dispatch/state/listeners `1/1/1` and the real fallback Label; combat 2 asserts distinct generations `1/2` with activations `1/1`; final `patch kernel complete ... observed=all` |
| character resource/UI | `CanaryResourceUi` | combat-owned nonnegative `Charge` resource + gain/spender cards + generic live Label + exact 6c UI adapter | `ScopedState<PlayerCombatState, ...>`; `CanAfford`; all-or-nothing `TrySpend`; payoff only after payment; `NCombatUi.Activate(CombatState)` MVID-gated postfix; no alternative-energy patch or runtime extraction | **two-combat `CombatPlayer`**: amount/counter `0 -> 3 -> 1`; affordable/unaffordable `true/false`; paid Block `+4`; rejected spend leaves amount/Block; combat 2 distinct state/counter `0`; final `resource UI complete ... observed=all` |
| bounded zone/dynamic output | `CanaryZoneDynamic` | hidden BaseLib `CustomPile` + one dynamic source card + compile/output cards | `[CustomEnum] PileType`; capacity before mutation; `CardPileCmd.Add` transitions; ordered source snapshot; per-instance `DynamicVars`; `AddGeneratedCardToCombat` history; no patch/UI/persistence | **two-combat `CombatPlayer`**: order `2>3>5`, capacity `3`, overflow rejected to Discard, hook enter/exit `3/3`, one `CardGeneratedEntry`, configured/actual Block `23`, combat 2 distinct empty pile; final `zone dynamic output complete ... observed=all` |
| advanced character acceptance | `WayfinderAcceptance` | selectable Wayfinder + combat-only Ink/UI + hidden ordered Map + spatially configured MappedRoute | Foundation plus exact 6c UI adapter and both 6d contracts; direction order models movement rather than merged card effects; no `PatchAll`, Publicizer, transpiler, manual registration, or shared runtime | **`RunStart` + two-combat `CombatPlayer`**: HP/pools/starters/Energy; `N>E>S>W`, overflow, one generated history; endpoint/right/left/back/closed/Block `0,0/3/0/0/true/20`; Ink `0->4->0`; paid/rejected output; distinct empty combat 2; final `wayfinder acceptance complete ... observed=all` |

## How to run (maintainer, on the STS2 dev box)

Canary projects are **regenerated on demand outside tracked source** (in an external
work dir or gitignored `.claude/`; repo stays clean; trust regenerate over hoarding).
The steps per cell:

1. `mkdir canary-<x> && cd canary-<x> && dotnet new alchyrsts2contentmod -n Canary<X> -M OpenMod`.
   For the character cell, use `dotnet new alchyrsts2charmod -n CanaryCharacter -M OpenMod`.
2. Uncomment `BSchneppe.StS2.PckPacker` in the csproj.
3. Author the minimal element per its recipe; the capability-kernel and two 6d maintainer
   cells use `reference/{capability-kernel,character-resource,custom-card-zone}.md` (see
   `canary-results.md` for the exact minimal bodies used — copy-paste ready).
4. Add `Logger.Info("[T2MOD-SELFTEST] Canary<X> loaded ok")` at the end of
   `MainFile.Initialize()`.
5. **(M5) Emit the tier-2 harness** per `reference/selftest-harness.md`: add
   `Canary<X>Code/SelfTest.cs`, fill the DRIVER body from the table above, and append
   `if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();` after the load marker.
   Each driver must snapshot and assert the table's concrete observable proof, then emit
   `[T2MOD-SELFTEST] Canary<X> state proof: ...`; element `fired/played/used` logs are
   diagnostic only.
6. `dotnet build Canary<X>.csproj -c Release` → expect **0 warnings, 0 errors** + a
   `.pck` copied to `mods/Canary<X>/`.
7. **Tier-1** (load): `python <open-mod>/games/sts2/tools/launch.py --wait-seconds 35`.
   A single ordinary launch may load every enabled canary, then run
   `python <open-mod>/games/sts2/tools/grep_log.py --mod-name Canary<X>` per cell →
   expect `[PASS] Tier-1 verified`.
8. **Tier-2** (effect fires, per driving cell — each self-drives its own hosted scenario):
   `python <open-mod>/games/sts2/tools/launch.py --self-test --mod-name Canary<X>` then
   `python <open-mod>/games/sts2/tools/grep_log.py --mod-name Canary<X> --tier2-pattern
   "<state-proof pattern>"` → expect `[PASS] Tier-2 verified`. Match concrete state such as
   `"damage.*observed=6"`, `"enemy attack.*observed=6"`, or
   `"event gold.*observed=25"`; rich enemies use
   `"monster vocabulary complete.*observed=all"`; the 6d cells use
   `"resource UI complete.*observed=all"` and
   `"zone dynamic output complete.*observed=all"`. The verifier separately requires the current launch's load
   marker plus `<ModName> selftest done`; terminal and broad trigger/preview lines are never
   accepted as proof. For `CanaryCombo`, require separate state proofs for the card→Power
   application and the dependent Power consequence.

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
not `.Targeting()`). **M6 World Node (2026-07-13): CanaryEvent PASS** — first `MapNode`
scenario seam earned: custom event room entered, nested title/option/result loc resolved,
real option UI clicked, and event+harness independently observed Gold `delta=25`. A fresh
one-sentence `ForgottenCache` acceptance then passed 0/0 + Tier 1 + Tier 2 with zero repair
on 2026-07-14, advancing Event to `pipeline-supported`. See `canary-results.md` for both.
**M6 Monster Move Vocabulary (2026-07-15): CanaryMonsterVocabulary PASS** — eight real
enemy turns proved self custom Power + downstream scaling, player Debuff, Block/Heal,
multi-hit history count, composite actions, an explicit cycle, and both half-HP branch
outcomes. A separate one-sentence `EmberWarden` run passed build 0/0 + Tier 1 + Tier 2 with
zero repair, advancing the richer move scope to `pipeline-supported`.
**M6 Character Foundation (2026-07-15): CanaryCharacter PASS** — the character-template
slice built 0/0, loaded without fresh errors, appeared in character selection, started a
run with exact HP/pools/starters, and proved its starter relic through `RunStart` +
`CombatPlayer`. The new character recipe and compact pipeline routing advance the
Foundation boundary to `pipeline-supported`; advanced Character Program capabilities
remain separate from the Foundation claim.
**M6 Capability Kernel (2026-07-15): CanaryPatchKernel PASS** — the self-contained module
built 0/0 and passed strict Tier 1 + two-combat Tier 2. It version-gated and idempotently
applied one B-risk `NCombatUi.Activate(CombatState)` postfix, dispatched a typed context,
mounted a real generic UI node, and reset semantic state across combat hosts. This advances
the 6c infrastructure boundary to `scenario-verified`; it did not by itself promote a
gameplay family or create `OpenMod.Runtime`.
**M6 6d Representative Advanced Cells (2026-07-16): PASS.** Both canaries were authored
before testing, built to 0/0, and passed a shared ordinary-launch Tier 1. Resource/UI then
passed a two-combat Tier 2 with exact payment/floor/counter/reset proof; Zone/Dynamic
Output passed a two-combat Tier 2 with order/capacity/hooks/history/output/reset proof.
The Resource canary reused only the exact 6c UI seam; the Zone cell stayed BaseLib/public.
Both first advanced to `scenario-verified`; the fresh `WayfinderAcceptance` run then
composed them through the real character path and advanced the bounded Character Program
and M6 Core to `pipeline-supported`.
**M6 6e Fresh Creative Acceptance (2026-07-16): WayfinderAcceptance PASS.** The new
spatial-route mechanic built 0/0 on its first source compile, passed strict Tier 1, and
passed isolated two-combat Tier 2 with exact Foundation, Map geometry, Ink payment/UI, and
reset proofs. Nine parked mods were restored afterward. This closes M6 Core; M7 is next.
See `canary-results.md` for the per-cell markers and harness bugs the live runs
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
  then parks/arms one self-test mod at a time for tier-2. Revisit after `RunStart` adds a
  fourth real scenario shape; do not add it only because three adapters now exist.
