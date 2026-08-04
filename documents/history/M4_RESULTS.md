# M4 Recipe Results (potion + card)

> **Historical run record.** M4's manual tier-2 observations and its then-proposed
> `--headless`/`TestMode` follow-up are preserved below as history. M5 later shipped a
> headed, zero-keystroke in-process harness using public Cmds; all four driving cells pass.
> Current commands and status are in `games/sts2/tests/canary.md` and `canary-results.md`.

> Companion to IMPLEMENTATION_PLAN.md §6 (M4) and M3_RESULTS.md. Records M4's
> element-breadth work: **round 1 — potions** (`recipes/potion.md` + spire-codex
> `grounding.md` + a vanilla potion snapshot, 2026-07-02) and **round 2 — cards**
> (`recipes/card.md` + `reference/mechanics.md` + `recipes/power.md`, 2026-07-03).
> Both extend the pipeline to a new element type and pass an end-to-end acceptance
> producing a working element from one sentence. Same Windows box as M0–M3
> (STS2 v0.107.1 + .NET 9.0.300 + BaseLib active).
>
> **Round 2 (card) is the newer result — see the "M4 round 2: card" section at the
> bottom.** Round 1 (potion) is recorded first, unchanged.

## Verdict: M4 ROUND 1 PASSED — potion recipe produces a loading, firing potion

A single-target damage potion ("Firebomb": deal 20 damage to one enemy) was
scaffolded, authored per `recipes/potion.md`, built clean, and **tier-1 verified**
(loads + registers, zero mod-named errors). Tier-2 (effect fires in combat) was
**user-confirmed by observation** — see the honest caveat below on marker evidence.
Every API used was grounded against the decompile before writing; **zero repair
attempts were needed** (like the M2 relic acceptance).

## What was built (skill source, on `Henry's_cc`)

- **`recipes/potion.md`** — the copy-adaptable potion pattern. Confirmed against the
  decompile, not guessed: trigger is `protected override async Task OnUse(
  PlayerChoiceContext, Creature?)` (potions are actively used — there is **no**
  combat-lifecycle hook like a relic's); three required abstract props
  `Rarity`/`Usage`/`TargetType`; `[Pool(typeof(SharedPotionPool))]` required; loc
  table `potions` with flat prefixed keys; effect Cmds use the literal
  `decimal`+`ValueProp.Unpowered` overloads. Worked examples: BlockPotion (self-buff,
  `AnyPlayer`) + FirePotion (single-target damage, `AnyEnemy`).
- **`grounding.md`** — the spire-codex (content source) vs local decompile (C#
  signatures) split, and API-usage rules (browser UA or 403; save-to-file + python;
  60 req/min; PolyForm noncommercial + attribution).
- **`reference/potions-snapshot.md`** — a curated 63-potion vanilla snapshot
  (name/pool/effect) + enum values, for offline fallback. © Mega Crit + spire-codex
  attribution. (The "both" decision: point at the live API AND keep a small snapshot
  — not a full data dump, for license + staleness + size reasons.)
- **Pipeline wired for two element types** — `interview.md`, `spec.md`, `author.md`,
  `scaffold.md`, `modmaker/SKILL.md`, `sts2-api/SKILL.md` now branch on element type
  = relic OR potion.

## Acceptance run (project: `D:\26summer_intern\m4-potion-test`, outside this repo)

Scaffolded `dotnet new alchyrsts2contentmod -n EmberFlask -M OpenMod`; PckPacker
uncommented. Because the Alchyr content template scaffolds `Cards/`/`Powers/`/
`Relics/` but **not** `Potions/`, the recipe's "scaffold difference" step was
exercised for real: hand-created `EmberFlaskCode/Potions/` + an `EmberFlaskPotion`
base class (mirrors the generated relic base), then the concrete potion.

Potion class `Firebomb` (Common, `CombatOnly`, `AnyEnemy`), id
`EMBERFLASK-FIREBOMB`, effect
`await CreatureCmd.Damage(choiceContext, target, 20m, ValueProp.Unpowered, base.Owner.Creature, null)`.

- **Build:** clean. `.dll` + `.json` + **`.pck` (63 KB)** all copied to
  `mods/EmberFlask/`. PckPacker emitted the `.pck` with no MegaDot needed.
- **Tier-1:** `RUNNING MODDED = YES`, load marker
  `[T2MOD-SELFTEST] EmberFlask loaded` FOUND, **zero** errors/exceptions naming the
  mod → PASS.
- **Tier-2:** user started a run, granted the potion via the dev console
  (`potion EMBERFLASK-FIREBOMB`), used it on an enemy in combat, and **observed the
  20 damage land**. Effect confirmed by observation.

## Findings from running it (not predicted in advance)

1. **A potion with no custom art loads cleanly — the flagged risk did not
   materialize.** Potion art is a `.tres` sprite atlas (not a loose `.png` like
   relics); the pre-run worry was that PckPacker or load-time registration might
   error on a potion with no atlas. It did not: `CustomPotionModel.CustomPackedImagePath`
   is `virtual` returning `null` (confirmed in the BaseLib decompile), so a null path
   falls back to the default potion icon and registration is clean. Custom potion art
   remains an M4+ art-pipeline concern, but it is **not** a blocker for functional
   potions.
2. **The dev console potion command is `potion <id>`, NOT `potion add <id>`, and it
   matches the id EXACTLY (uppercased), not by substring.** This differs from
   `relic [add|remove] <id>` (add default, substring `Contains` match). Confirmed by
   reading `PotionConsoleCmd.cs` + `RelicConsoleCmd.cs` in the decompile — the recipe
   and `verify.md` had guessed `potion add`; both were corrected. A run must be in
   progress. (Recorded so the next element type's console-grant step is checked, not
   assumed.)
3. **`CreatureCmd.Damage` has many overloads; the 6-arg
   `(PlayerChoiceContext, Creature, decimal, ValueProp, Creature?, CardModel?)` one is
   the right literal-amount single-target form** (returns
   `Task<IEnumerable<DamageResult>>`, awaited and discarded). Grounded against
   `CreatureCmd.cs` before authoring — the recipe's signature was exact.

## Notes / deferred

- **Tier-2 marker evidence was not captured this run (honest caveat).** The
  automated `[T2MOD-SELFTEST] Firebomb used:` marker is emitted in `OnUse`, but the
  user ran tier-2 from a **separate Steam launch** after the scripted tier-1 launch,
  and STS2 overwrites `godot.log` on every launch (archiving the prior one). That
  run's log had already rotated out by the time it was grepped, so the effect is
  **user-observed but the log marker was not captured**. Per the project's
  "observed reality only" rule, tier-2 is recorded as confirmed-by-observation, not
  log-verified. This is the inherent weakness of manual tier-2 and the direct
  motivation for **M5 headless behavior testing** (drive `fight`/`potion`/`block`
  console commands under `--headless` + `TestMode`, which skips VFX/waits, and assert
  HP programmatically — the decompile shows all the entry points exist).
- Zero repair attempts (grounded APIs compiled and loaded first try), so M4 did not
  exercise `repair.md` — consistent with M2. The loop remains a backstop.
- Test project kept at `D:\26summer_intern\m4-potion-test` (outside the repo, like
  m1/m2/m3), so it is a reference, not part of the published skill.
- `PlayerCmd.Draw`'s exact signature is still a recipe guess (marked "confirm");
  irrelevant to the damage potion, but ground it before the card recipe.

## Next step (from round 1)

Remaining M4 breadth: the **card recipe** (577 vanilla cards, more fields) and a
harder multi-element interview, plus the **art/sprite pipeline** (custom `.tres`
potion atlas / relic png beyond placeholders). Then **M5** — automate tier-2 so the
effect check no longer needs the user's eyes.

---

# M4 round 2: card recipe (2026-07-03)

## Verdict: M4 ROUND 2 PASSED — card recipe produces a loading, firing card, both tiers LOG-VERIFIED

A single-target attack card ("Firebolt": deal 8 damage, upgrade +3 → 11) was
scaffolded, authored per `recipes/card.md`, built clean, **tier-1 verified** (loads +
registers, zero mod-named errors), and **tier-2 LOG-VERIFIED** — the effect marker was
grepped from the live log while the game was still open, closing round 1's tier-2
capture gap. Every API was grounded against the decompile before writing; **zero
repair attempts** (like M2/M4-round-1).

## What was built (skill source, on `Henry's_cc`, committed `fe06b5c`)

- **`recipes/card.md`** — the copy-adaptable card pattern for **new cards**, four
  worked shapes (attack / block / power / combine). Grounded, not guessed: effect in
  `protected override async Task OnPlay(PlayerChoiceContext, CardPlay)`; ctor
  `base(cost, CardType, CardRarity, TargetType)`; `[Pool(typeof(ColorlessCardPool))]`
  required (cards ARE pooled, unlike powers); numbers in `CanonicalVars`
  (`DamageVar`/`BlockVar`/`PowerVar<T>`) read via `DynamicVars.Damage`/`.Block`/
  `["PowerName"]`; attack uses the `DamageCmd.Attack(...).FromCard(this).Targeting(...)
  .WithHitFx(...).Execute(ctx)` fluent builder; block uses the `cardPlay` overload of
  `CreatureCmd.GainBlock`; loc table `cards`, **no separate upgrade key** (SmartFormat
  `{Damage:diff()}` renders the upgraded value).
- **Foundations (committed earlier, `5536eee`)**: `reference/mechanics.md`
  (DynamicVars, SmartFormat, shared enums) + `recipes/power.md` (custom buff/debuff,
  usually a card dependency).
- **Pipeline wired for card + power** — `interview.md`, `spec.md`, `scaffold.md`,
  `author.md`, `verify.md`, `modmaker/SKILL.md`, `sts2-api/SKILL.md` now branch on
  element type = relic / potion / card (+ power as a dependency).
- **Scope decision:** *editing* existing vanilla cards is deferred (BaseLib exposes no
  wrapper API — it needs raw Harmony patching; the scaffolding `harmony.PatchAll()` is
  already present). `card.md` covers making NEW cards, with a one-line future-work note.

## Acceptance run (project: `D:\26summer_intern\m4-card-test`, outside this repo)

Scaffolded `dotnet new alchyrsts2contentmod -n Firebolt -M OpenMod`; PckPacker
uncommented. Unlike potions, the Alchyr template **does** scaffold `Cards/` + a
`FireboltCard` base class — so no hand-created base was needed (recipe says so).

Card class `Firebolt` (Common, `Attack`, `AnyEnemy`), id `FIREBOLT-FIREBOLT`, effect
`await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCard(this).Targeting(cardPlay.Target).WithHitFx("vfx/vfx_attack_slash").Execute(choiceContext)`.

- **Build:** clean. `.dll` + `.json` + **`.pck` (63 KB)** copied to `mods/Firebolt/`.
- **Tier-1:** `RUNNING MODDED = YES`, load marker `[T2MOD-SELFTEST] Firebolt loaded ok`
  FOUND, **zero** errors naming the mod → PASS.
- **Tier-2 (LOG-VERIFIED):** dev console `card FIREBOLT-FIREBOLT` spawned it into hand,
  played on an enemy, 8 damage landed, and — game kept OPEN — the marker
  `[T2MOD-SELFTEST] Firebolt played: 8 dmg to target` was grepped from the current
  `godot.log`. Not just observed: **log-verified.**

## Findings from running it (not predicted in advance)

1. **The card console command is `card <id> [pile]` — spawns into HAND by default, no
   `add`/`remove` subcommand, EXACT (uppercased) match.** A third distinct console
   grammar: relic = `relic add <id>` (substring), potion = `potion <id>` (exact, no
   subcmd), card = `card <id>` (exact, no subcmd, → hand). Grounded in `CardConsoleCmd.cs`.
2. **`grep_log.ps1` had a file-lock bug that tier-2 triggered.** It used
   `File.ReadAllText` (exclusive open), which throws `IOException` when the game is
   still running — exactly the tier-2 case where you must NOT close the game (or the
   log rotates). Fixed to open with `FileShare.ReadWrite` and gained a `-Tier2Pattern`
   arg so one call verifies both tiers with the game open. `verify.md` updated to use it.
   This is the concrete fix for round 1's honest tier-2 caveat.

## Cleanup (2026-07-03)

Test mods are repo-external and NOT git-tracked. Decision: keep **m1-gamblers-coin**
(the hand-built relic golden, a CardModel-independent reference CLAUDE.md points at,
not reproducible by the pipeline); delete the pipeline-*product* test mods
(m3-repair-test, m4-potion-test, m4-card-test) and their installed copies in the game
`mods/` folder — their knowledge is captured in the recipes + results + memory, and
trusting "regenerate on demand" over hoarding old outputs is itself the pipeline's
value proposition. Game `mods/` now holds only `GamblersCoin`.

## Next step

M4 breadth for cards + potions is done. Remaining: the **art/sprite pipeline** (custom
card portraits / potion `.tres` atlas / relic png beyond placeholders), and **M5** —
automate tier-2 headless (drive `fight`/`card`/`potion` console commands under
`--headless` + `TestMode`, assert HP programmatically) so the effect check no longer
needs the user's eyes, plus the Codex adapter + one-command install.
