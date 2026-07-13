# Canary matrix — run record (M4.5 ②)

> **Historical command note:** this run record preserves the PowerShell commands used on
> 2026-07-06. The tools were later replaced by cross-platform Python; use the current
> commands in `canary.md` when rerunning the matrix.
>
> Companion to `canary.md`. Records the first full run (2026-07-03, STS2 v0.107.1,
> .NET 9.0.300, BaseLib active) and the exact minimal element bodies used, so the
> suite is reproducible. All projects live **outside the repo** at
> `D:\26summer_intern\canary-<x>\` (regenerate-on-demand, not committed).

## Result: ALL FIVE PASS (build 0/0 + tier-1 load-verified)

| Cell | Build | `.pck` | Tier-1 (load marker + no mod errors) |
|------|-------|--------|--------------------------------------|
| CanaryRelic | 0 warn / 0 err | ✓ | PASS |
| CanaryPotion | 0 warn / 0 err | ✓ | PASS |
| CanaryCard | 0 warn / 0 err | ✓ | PASS |
| CanaryPower | 0 warn / 0 err | ✓ | PASS |
| CanaryCombo | 0 warn / 0 err | ✓ | PASS |

One launch loaded all five (`RUNNING MODDED = YES`); each load marker
`[T2MOD-SELFTEST] Canary<X> loaded ok` found, zero errors/exceptions naming any mod.

## Tier-2 (M5 self-test harness) — run record: ALL FOUR DRIVING CELLS PASS (2026-07-06)

Live on the dev box (STS2 v0.107.1, BaseLib v3.3.5, .NET 9.0.300). Each cell regenerated
outside the repo with the fixed harness, built 0/0 with PckPacker, then
`tools/launch.ps1 -SelfTest -ModName Canary<X>` (zero interaction) + `grep_log.ps1
-Tier2Pattern`. **Test ONE mod at a time** — `--t2selftest` arms every loaded harness mod,
so multiple in `mods/` collide on the main menu (`ObjectDisposedException: NMainMenu`); park
all but the cell under test (memory `sts2-m5-selftest-single-mod-constraint`).

| Cell | Harness outcome | Effect marker fired | Verdict |
|------|-----------------|---------------------|---------|
| CanaryCard | selftest done | `Jolt played: 6 dmg to target` | **PASS** |
| CanaryRelic | selftest done | `Bauble fired: +1 energy` | **PASS** |
| CanaryPotion | selftest done | `Fizz used: 10 dmg` | **PASS** |
| CanaryCombo | selftest done | `Charge played: applied Signal` **+** `Signal fired: 3 dmg` | **PASS** (both links) |

The full ForceClick nav (menu → run → combat) drove itself with zero keystrokes on all four.
CanaryCombo (historical project name; now modeled as two elements plus an `applies`
interaction) proves the relationship chain: the card applies the custom power, then
`EndTurn` starts the enemy turn so the power's `AfterSideTurnStart` fires — both markers
observed.

**Bugs the live run surfaced (all fixed in `reference/selftest-harness.md`):** (1)
`SaveManager.SetFtuesEnabled` NREs at Arm() time → best-effort try/catch; (2) `IsInProgress`
races ahead of the run UI node (`NRun.GlobalUi`) → added a wait gate before `EnterRoomDebug`;
(3) harness template emitted 9 nullable warnings → cleaned to 0/0; (4) the interaction
canary showed `PlayerCmd.EndTurn`
returns void (awaiting = CS4008) and is *required* for enemy-turn-start powers.

### Historical (pre-fix) note

The per-cell DRIVER body + asserted marker are specified in `canary.md`'s table; the
minimal element bodies below already emit each `fired/used/played:` marker, so the
harness only has to *trigger* it.

- **relic/potion/card** drive their effect within the harness's turn-1 Play phase.
- **multi-element interaction** (historical project `CanaryCombo`): `Charge` applies
  `Signal` to the **enemy**, and `Signal` fires on `AfterSideTurnStart` — i.e. at the
  **enemy's** turn start. The source is a card, so its normal card DRIVER must
  `PlayerCmd.EndTurn` after playing `Charge` for the dependent `Signal fired:` observation
  to appear (the harness page's card→power example has this `EndTurn` line). Assert
  **both** `Charge played: applied Signal` and `Signal fired:`.
- **power** (`CanaryPower`/`Smolder`) has no standalone tier-2 cell — a power ships applied
  by something else, so its marker is covered by the interaction shape.

Until this section is filled, tier-2 for the matrix is **specified-but-unverified** — do
not claim it passed.

## M6.0 verification-seam regression (2026-07-10)

Re-ran the existing CanaryCard self-test after making terminal/effect proof independent:
`launch.py --self-test --mod-name CanaryCard` returned 0 only after `selftest done`, then
`grep_log.py --tier2-pattern "played"` required all three independent signals — exact
`CanaryCard loaded ok`, `CanaryCard Jolt played: 6 dmg to target`, and
`CanaryCard selftest done` — with no mod-named errors. **PASS live.** Standard-library
synthetic-log tests separately prove that `done` without an effect and `FAILED` after an
effect both fail.

## M6 Mechanic Vocabulary — Keyword (2026-07-10)

`CanaryKeyword` is a Card+custom-Keyword vertical canary generated outside the repo. Its
`Resonant` field uses BaseLib `[CustomEnum]` + `[KeywordProperties(After)]`; `Resonant
Guard` includes that field in `CanonicalKeywords` and implements the named rule in its
Card host. Build: **0 warnings / 0 errors**, `.dll/.pck/.json` copied to the real mods dir.

Live `CombatPlayer` run (other harness canaries parked): exact load marker found, Card
autoplayed, then logged `Resonant fired: present=True block 0 -> 7` and `selftest done`,
with zero mod-named errors. **Type + Scenario PASS.** The first two launches hit known
navigation setup misses (`ConfirmButton not enabled`, then stale-run `no abandon modal`);
these correctly returned nonzero and were not treated as effect failures. A clean retry
passed without changing keyword behavior.

## M6 Mechanic Vocabulary — Card Enchantment (2026-07-10)

`CanaryEnchantment` pairs host Card `Etched Strike` with custom `Guarded :
CustomEnchantmentModel`. Build: **0 warnings / 0 errors**, packaged and copied to the real
mods dir. In the isolated live scenario, the card driver called `CardCmd.Enchant<Guarded>`
and independently observed `Guarded attached: True amount=5`; autoplay then invoked the
enchantment's `OnPlay`, logging `attached=True amount=5 block 0 -> 5`, followed by
`selftest done`, with no mod-named errors. **Type + attachment + altered behavior PASS.**
Custom icon rendering was not checked and remains explicitly provisional.

## M6 Mechanic Vocabulary — Orb (2026-07-10)

`CanaryOrb` pairs host Card `Take Shelter` with `ShelterOrb : CustomOrbModel` using inline
`OrbLoc`. Build: **0 warnings / 0 errors**, packaged and loaded. The isolated live
`CombatPlayer` run used a character with zero orb slots; `OrbCmd.Channel` created capacity
1 and the queue contained the custom orb. Independent observations then proved passive
Block `0 -> 2` and evoke Block `2 -> 7`, followed by `selftest done`, with no mod-named
errors. **Type + channel + passive + evoke PASS.** Two preceding attempts hit the existing
NMainMenu `ObjectDisposedException` setup miss; the verifier returned nonzero and a clean
retry passed without an orb-code change. Custom icon/combat sprite rendering remains
provisional.

## M5.5 art pipeline — sprite verification (2026-07-08)

Live on the dev box (STS2 stable, BaseLib active). Generated real icons via the BYO backend
(Poe / nano-banana-2, chat mode) with `gen_sprite.py`, rebuilt the `.pck`, and eyeballed
each in-game. All render correctly.

| Cell | Spec | Icon(s) written | In-game surfaces checked | Verdict |
|------|------|-----------------|--------------------------|---------|
| CanaryCard   | `card`   | `card_portraits/big/jolt.png` (1000×760) | card portrait | **PASS** (verified 2026-07-08, earlier) |
| CanaryRelic  | `relic`  | `relics/bauble.png` + `relics/big/bauble.png` (256×256) | relic-bar icon **+ detail/inspect popup** | **PASS** |
| CanaryPower  | `power`  | `powers/smolder.png` + `powers/big/smolder.png` (256×256) | combat status icon **+ apply/expire notification popup** | **PASS** |
| CanaryPotion | `potion` | `potions/fizz.png` (256×256) — **ONE file** | potion-bar icon **+ hover tooltip + use** | **PASS** |

**Two findings that changed the pipeline (both fixed + re-verified live):**
1. **relic and power each need TWO icon files, not one.** The bar/status icon
   (`<slug>.png`) and the big popup (`big/<slug>.png`) are separate loose-PNG getters; writing
   only the first leaves the popup on the placeholder. `gen_sprite.py` now writes both
   (`extra_sub_paths`). Confirmed by seeing the relic detail popup and the power
   apply/expire notification both go from placeholder → custom.
2. **a power (or relic) subclass must extend the template base `<ModName>Power` /
   `<ModName>Relic`, not `CustomPowerModel`/`CustomRelicModel` directly.** The template base
   is what overrides the loose-PNG icon getters; a direct BaseLib subclass leaves them null
   and the icon silently falls back to default even with the PNG present. This is exactly
   what the historical minimal `Smolder : CustomPowerModel` body below did — fixed in
   `recipes/power.md` (skeleton + checklist + example now extend `<ModName>Power`).

**relic outline:** `<slug>_outline.png` (the hover/selection white outline) is intentionally
NOT generated — a missing one falls back to the template's generic `relic_outline.png`,
which looks fine in-game (confirmed). power has no outline.

**potion finding — it is NOT a `.tres` atlas (overturned the plan).** The M5.5 ② plan
assumed potion needed a Godot `.tres` sprite-atlas emitter. It does not: BaseLib's
`CustomPotionModel` Harmony-patches `PotionModel.ImagePath` to `CustomPackedImagePath`, whose
docstring says a PNG path is a valid `Texture2D`. Wiring mirrors relic/power — a
`PotionImagePath` helper (`Exists()`+fallback) + the `<ModName>Potion` base overrides the
getter (the template scaffolds neither, so both are hand-added). **Unlike relic/power, potion
writes ONE file** — `PotionModel` exposes a single `Image` texture reused by the bar icon,
hover tooltip, and throw/use VFX; there is no separate `big/` variant (`extra_sub_paths: []`).
Also new: potions are drawn **tilted ~45° right** (STS2's display angle), baked into the
prompt. "Fizz" (a fizzing damage flask) generated → built → all three surfaces show the custom
icon, not placeholder.

## Findings this suite surfaced (its whole point)

1. **`power.md` worked-example `powers.json` was missing `.smartDescription`** — the
   exact STS001 bug the milestone is about, sitting in the recipe's own copy-paste
   example (the prose above it said "three keys", the example showed two). Fixed the
   example to include `.smartDescription`. This is the "recipe written from grounding
   but never built" class — power was the only recipe with no prior green build.
2. **`card.md` skeleton omits the null-guard the prose requires** → a minimal follow
   builds with **CS8604** (possible null on `.Targeting(cardPlay.Target)`). The prose
   and the "Attack" block *do* show `ArgumentNullException.ThrowIfNull(cardPlay.Target)`,
   but the top-level skeleton (lines ~91) does not, so the most literal reading warns.
   The canary adds the guard and builds clean. (Left as a note — the guard is already
   documented; a future card.md tidy could hoist it into the skeleton.)

Both are real recipe-quality wins caught with **zero user involvement** — the
argument for keeping this suite.

## Exact minimal bodies used (copy-paste reproducible)

Each mod = scaffold + PckPacker uncommented + the file(s) below + the
`Logger.Info("[T2MOD-SELFTEST] Canary<X> loaded ok")` line in `MainFile.Initialize()`.
IDs follow the derivation rule (namespace first segment upper + `-` + slugified class).

### relic — `CanaryRelicCode/Relics/Bauble.cs` + `relics.json` (3 keys)
```csharp
[Pool(typeof(SharedRelicPool))]
public sealed class Bauble : CanaryRelicRelic {
    public override RelicRarity Rarity => RelicRarity.Common;
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState) {
        var combat = Owner.PlayerCombatState!;
        if (!participants.Contains(Owner.Creature) || combat.TurnNumber > 1) return;
        Flash();
        await PlayerCmd.GainEnergy(1, Owner);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryRelic Bauble fired: +1 energy");
    }
}
```
`relics.json`: `CANARYRELIC-BAUBLE.{title,description,flavor}`.

### potion — hand-made `Potions/CanaryPotionPotion.cs` (base) + `Potions/Fizz.cs` + `potions.json` (2 keys)
```csharp
public abstract class CanaryPotionPotion : CustomPotionModel { }

[Pool(typeof(SharedPotionPool))]
public sealed class Fizz : CanaryPotionPotion {
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyEnemy;
    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target) {
        AssertValidForTargetedPotion(target);
        await CreatureCmd.Damage(choiceContext, target!, 10m, ValueProp.Unpowered, base.Owner.Creature, null);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryPotion Fizz used: 10 dmg");
    }
}
```
`potions.json`: `CANARYPOTION-FIZZ.{title,description}`.

### card — `Cards/Jolt.cs` + `cards.json` (2 keys)
```csharp
[Pool(typeof(ColorlessCardPool))]
public sealed class Jolt : CanaryCardCard {
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new DamageVar(6m, ValueProp.Move) };
    public Jolt() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }
    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay) {
        System.ArgumentNullException.ThrowIfNull(cardPlay.Target);   // <- without this: CS8604
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCard(this)
            .Targeting(cardPlay.Target).WithHitFx("vfx/vfx_attack_slash").Execute(choiceContext);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] CanaryCard Jolt played: {DynamicVars.Damage.BaseValue} dmg to target");
    }
    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3m);
}
```
`cards.json`: `CANARYCARD-JOLT.{title,description}` (description uses `{Damage}`).

### power — `Powers/Smolder.cs` + `powers.json` (**3 keys incl. smartDescription**)
```csharp
public sealed class Smolder : CustomPowerModel {           // NO [Pool]
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState) {
        if (!participants.Contains(base.Owner)) return;
        Flash();
        int dealt = base.Amount;
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), base.Owner, dealt,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        if (base.Owner.IsAlive) await PowerCmd.Decrement(this);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] CanaryPower Smolder fired: {dealt} dmg to {base.Owner}");
    }
}
```
`powers.json`: `CANARYPOWER-SMOLDER.{title,description,smartDescription}`.

> **Icon note (M5.5):** this minimal body extends `CustomPowerModel` directly, which was
> fine for the tier-2 *effect* test but leaves the custom icon null. For the M5.5 art run
> `Smolder` was changed to extend the template base `CanaryPowerPower` so the loose-PNG icon
> resolves (see the M5.5 section above + `recipes/power.md`).

### interaction fixture (historical project `CanaryCombo`) — `Powers/Signal.cs` + `Cards/Charge.cs` + both loc tables
```csharp
[Pool(typeof(ColorlessCardPool))]
public sealed class Charge : CanaryComboCard {
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new PowerVar<Signal>(3m) };
    public Charge() : base(1, CardType.Skill, CardRarity.Common, TargetType.AnyEnemy) { }
    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay) {
        System.ArgumentNullException.ThrowIfNull(cardPlay.Target);
        await PowerCmd.Apply<Signal>(choiceContext, cardPlay.Target,
            base.DynamicVars["Signal"].BaseValue, base.Owner.Creature, this);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryCombo Charge played: applied Signal");
    }
}
```
`cards.json`: `CANARYCOMBO-CHARGE.{title,description}` (uses `{Signal}`);
`powers.json`: `CANARYCOMBO-SIGNAL.{title,description,smartDescription}`.

## M6 Enemy Encounter — CanaryEncounter (2026-07-10)

`CanaryEncounter` is a Monster + Encounter vertical canary generated outside the repo at
`D:\26summer_intern\canary-encounter\`. It contains one custom monster (`CanaryMite :
CustomMonsterModel`) with a single deterministic PECK move (6 damage, loops) and one
custom encounter (`CanaryMiteEncounter : CustomEncounterModel`) that spawns exactly one
CanaryMite. This is the first **`CombatEnemy`** scenario canary — proving the seam
needed for all enemy-side M6 content.

Build: **0 warnings / 0 errors**, `.dll/.pck/.json` copied to
`D:\Steam\steamapps\common\Slay the Spire 2\mods\CanaryEncounter\`.

Tier-1 (STS2 v0.107.1, BaseLib v3.3.5, .NET 9.0.300):
```
python games/sts2/tools/launch.py --wait-seconds 30
python games/sts2/tools/grep_log.py --mod-name CanaryEncounter
```
→ `[PASS] Tier-1 verified: CanaryEncounter loaded ok.`

Tier-2 — CombatEnemy scenario (other harness mods parked including Overclock):
```
python games/sts2/tools/launch.py --self-test --mod-name CanaryEncounter
python games/sts2/tools/grep_log.py --mod-name CanaryEncounter \
  --tier2-pattern "Peck attacked|encounter started|monster present|action advanced"
```
→ `[PASS] Tier-2 verified: CanaryEncounter loaded AND effect marker fired.`

Four independent CombatEnemy proof signals found in log:
1. `CanaryEncounter encounter started: custom encounter ok` — custom encounter entered
2. `CanaryEncounter monster present: CanaryMite hp=12` — custom monster spawned and identified
3. `CanaryEncounter Peck attacked: player hp [N]` — enemy PECK move executed
4. `CanaryEncounter action advanced: player hp [N] -> [N-6] delta=6` — state delta confirmed

**Bug found and fixed during live run (corrected in `CanaryMite.cs` before tier-2 PASS):**
Monster attacks do NOT use `.Targeting(target)` — that is the card pattern. The correct
vanilla monster pattern (from `SingleAttackMoveMonster`) is `.FromMonster(this).Execute(null)`.
Using `.Targeting(target)` caused the PECK to hang mid-execution; the player's turn never
resumed after `EndTurn`, producing `selftest FAILED: player play phase not resumed after
enemy turn`. Fixed to `.FromMonster(this).Execute(null)` and the second attempt passed.

This finding is now documented in `recipes/monster.md` as a critical warning.

**Art:** no custom scene authored for CanaryMite; game falls back to
`creature_visuals/fallback`. Monster and encounter visual contracts remain **provisional**
and are explicitly excluded from the support claim.

| Signal | Marker |
|--------|--------|
| load | `CanaryEncounter loaded ok` |
| encounter entered | `CanaryEncounter encounter started: custom encounter ok` |
| monster present | `CanaryEncounter monster present: CanaryMite hp=12` |
| enemy action | `CanaryEncounter Peck attacked: player hp [N]` |
| state delta | `CanaryEncounter action advanced: player hp [N] -> [N-6] delta=6` |
| terminal | `CanaryEncounter selftest done` |

### Natural-language pipeline acceptance (2026-07-13)

A user test against the published open-mod **0.5.0** plugin completed the full
plain-language Enemy Encounter pipeline and produced a working mod. This advances the
Monster + Encounter slice from `scenario-verified` to **`pipeline-supported`**; the
reproducible Type + Scenario proof remains the `CanaryEncounter` run above.

The acceptance run also found one template defect before self-test compilation:
`SelfTest.Arm()` called nonexistent `TaskHelper.RunSafely(RunAsync())`. `TaskHelper` is
not supplied by STS2, BaseLib, or the generated project. The source template now uses
standard fire-and-forget `_ = RunAsync();`; `RunAsync()` already catches and logs its own
exceptions. Both committed distribution payloads were regenerated from the corrected
source.
