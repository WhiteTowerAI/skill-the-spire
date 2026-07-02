# M4 Potion Recipe Results

> Companion to IMPLEMENTATION_PLAN.md §6 (M4) and M3_RESULTS.md. Records M4 round 1:
> extending the pipeline from relics to a second element type — **potions** — with a
> new `recipes/potion.md`, spire-codex `grounding.md`, a vanilla potion snapshot, and
> an end-to-end acceptance producing a working potion from one sentence. Run
> 2026-07-02 on the same Windows box as M0–M3 (STS2 v0.107.1 + .NET 9.0.300 +
> BaseLib active).

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

## Next step

Remaining M4 breadth: the **card recipe** (577 vanilla cards, more fields) and a
harder multi-element interview, plus the **art/sprite pipeline** (custom `.tres`
potion atlas / relic png beyond placeholders). Then **M5** — automate tier-2 so the
effect check no longer needs the user's eyes.
