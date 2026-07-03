# Author — write the element, localization, and marker

Goal: fill in ONLY the effect logic on top of the recipe skeleton, add the
localization JSON, and inject the self-test marker. Everything structural
(class skeleton, `[Pool]`, image paths) comes from the recipe — don't reinvent it.

## 0. Read the quirks and the recipe first

- Read `quirks.md` before writing any C#.
- Query the **sts2-api** skill for the recipe matching SPEC's **element**:
  `recipes/relic.md` for a relic, `recipes/potion.md` for a potion, `recipes/card.md`
  for a card. For a **card or power**, also read `reference/mechanics.md` first
  (DynamicVars, SmartFormat descriptions, shared enums). If the effect needs a
  buff/debuff no vanilla power covers, read `recipes/power.md` and author the custom
  power as a dependency. Pull the skeleton, the trigger/usage rules, the effect
  building blocks, and the loc-key derivation rule. Do **not** guess API names — if
  the effect needs a Cmd not in the recipe, follow `grounding.md` (content facts →
  spire-codex / `reference/potions-snapshot.md`; code signatures → the decompiled
  API). Never invent a Cmd name — that's the #1 way the repair loop burns its attempts.

## 1. Write the element class

**Relic** — add `<ModName>Code/Relics/<RelicName>.cs`. Use the recipe skeleton, then:

- Set `Rarity` from SPEC.
- Keep `[Pool(typeof(<Pool>))]` — **omitting it throws at registration** (errors.md).
- Override the hook matching SPEC's trigger (recipe's "Trigger hooks" table). For
  combat-start: `AfterSideTurnStart` + `participants.Contains(Owner.Creature)` +
  `Owner.PlayerCombatState!.TurnNumber <= 1` guards.
- Fill **only** the effect block with the confirmed Cmds/RNG from the recipe. `await`
  every Cmd. Use `Rng`, never `System.Random`. Call `Flash()` when it visibly triggers.

**Potion** — the Alchyr template does **not** scaffold a `Potions/` folder or base
class, so first create `<ModName>Code/Potions/` and the `<ModName>Potion` base class
(recipe "Scaffold difference" section). Then add `<ModName>Code/Potions/<PotionName>.cs`:

- Override the three abstract props: `Rarity`, `Usage` (`CombatOnly`/`AnyTime`),
  `TargetType` (self-buff = `AnyPlayer`, not `Self`; one enemy = `AnyEnemy`).
- Keep `[Pool(typeof(SharedPotionPool))]` — required, same as relics.
- Fill **only** the `OnUse` effect block with confirmed Cmds (`CreatureCmd.Damage/
  GainBlock/Heal`, `PowerCmd.Apply<T>`, `PlayerCmd.*`), using `ValueProp.Unpowered`
  for damage/block. `await` every Cmd; call `AssertValidForTargetedPotion(target)` first.

**Card** — the template **does** scaffold `Cards/` and the `<ModName>Card` base class,
so extend it directly (unlike potions). Add `<ModName>Code/Cards/<CardName>.cs`:

- Pass `cost, CardType, CardRarity, TargetType` to `base(...)`. A card that targets the
  player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions).
- Keep `[Pool(typeof(ColorlessCardPool))]` — required, same as relics/potions.
- Declare scaling numbers in `CanonicalVars` (`DamageVar`/`BlockVar`/`PowerVar<T>`),
  never literals; bump them in `OnUpgrade()`.
- Fill **only** the `OnPlay` effect block with the recipe's confirmed Cmds
  (`DamageCmd.Attack(...).FromCard(this).Targeting(...).Execute(...)`, `CreatureCmd.GainBlock`
  with the `cardPlay` overload, `PowerCmd.Apply<T>`). Null-check `cardPlay.Target` on a
  targeted card. `await` every Cmd. If a custom power is needed, author it first
  (`recipes/power.md`) — no `[Pool]` on the power.

## 2. Inject the self-test markers

**Two markers.** The Alchyr template's `MainFile.cs` does NOT log anything by
default — you must add the **load** marker yourself, or tier-1 verify silently
finds nothing. In `MainFile.Initialize()`, right after `harmony.PatchAll();`:

```csharp
Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");
```

Then, for **effect** proof, log a marker inside the trigger showing what happened
(a relic's combat-start hook, a potion's `OnUse`, or a card's `OnPlay`):

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ElementName> fired/used: <outcome> <metric> {before} -> {after}");
```

verify.md greps the first for tier-1 and the second for tier-2. Keep both while
verification is manual.

## 3. Write localization

Add entries to `<ModName>/localization/eng/<table>.json` — **`relics.json`** for a
relic, **`potions.json`** for a potion, **`cards.json`** for a card, **`powers.json`**
for a custom power. **Keys are FLAT and prefixed** (recipe's loc-key rule + errors.md
"raw-key title"):

```json
{
  "<PREFIX>-<SLUG>.title": "<title from SPEC>",
  "<PREFIX>-<SLUG>.description": "<hover text from SPEC>",
  "<PREFIX>-<SLUG>.flavor": "<relic flavor — relics only>"
}
```

Relics take `.title/.description/.flavor`; potions take `.title/.description` (plus
`.selectionScreenPrompt` only if the effect prompts a choice — no `.flavor`); cards take
`.title/.description` (plus `.selectionScreenPrompt` if it prompts a choice — no
`.flavor`, no separate upgrade key). A **card description uses SmartFormat placeholders**
for scaling numbers — `"Deal {Damage:diff()} damage."` not `"Deal 6 damage."` — so the
upgraded value renders automatically (`reference/mechanics.md` §2). A **power** takes
`.title/.description` with `{Amount}` for the stack count. Use the exact `<PREFIX>-<SLUG>`
you derived in SPEC. Not nested JSON — a flat `Dictionary<string,string>`.

## 4. Art (M4: placeholder)

Leave the default art. A **relic** falls back to `relic.png` if `images/relics/<slug>.png`
is absent. A **potion** uses a `.tres` sprite atlas; leaving the mod potion base's
`CustomPackedImagePath` null falls back to the default potion icon. A **card** renders
with a blank/placeholder portrait when its art file is absent — it still loads and
plays. Custom/generated art is the M4 art pipeline — don't block on it.

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
and any Cmd choices. Mark `author` done in `PLAN.md`. Then go to `build.md`.
