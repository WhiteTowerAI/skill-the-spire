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
  the effect needs a Cmd not in the recipe, follow `grounding.md` — at runtime that
  means the rest of the pack (`reference/mechanics.md`, `build-constraints.md`,
  snapshots, `errors.md`), and if it's genuinely not there, report a pack gap. Never
  invent a Cmd name — that's the #1 way the repair loop burns its attempts.

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

verify.md greps the first for tier-1 and the second for tier-2. **Both markers stay in
every mod** — the load marker proves it loads, the effect marker is what the tier-2
harness (next step) makes fire automatically.

## 2.5 Emit the tier-2 self-test harness

This is what makes tier-2 automatic — the effect fires and is grepped with **no human at
the keyboard, no dev-console typing**. Query the **sts2-api** skill for
`reference/selftest-harness.md` and follow it. In short:

1. Emit `<ModName>Code/SelfTest.cs` — the fixed scaffold from that page (menu→combat
   navigation is identical for every mod; do not hand-edit it), in the **same namespace
   as `MainFile.cs`** (`<ModName>.<ModName>Code`) so it reaches `MainFile.Logger`.
2. Fill **exactly one** DRIVER body per SPEC's element: **relic** → `BeforeCombat`
   (grant it, its `AfterSideTurnStart` fires on its own); **card** → `InCombat`
   (`GainEnergy` → spawn into hand → `CardCmd.AutoPlay`); **potion** → `InCombat`
   (`TryToProcure` → `EnqueueManualUse`); **combo** → `InCombat`, walking SPEC's
   interaction block source-first (drive the source element; the dependent logs its own
   marker). The page has the exact body for each.
3. Add the **gated arm line** to `MainFile.Initialize()`, right after the load marker:

```csharp
if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();   // verification-only; dormant for end users
```
`using MegaCrit.Sts2.Core.Helpers;` for `CommandLineHelper`. The arg gate means a normal
user launch never arms it — no menu driving, fully inert. It ships dormant inside the mod.

**Grounding rule still holds:** the harness uses only the confirmed public Cmds in
`selftest-harness.md` (`CardCmd.AutoPlay`, `PowerCmd.Apply`, `RelicCmd.Obtain`, potion
`EnqueueManualUse`, …). Do **not** invent an API or try `NDevConsole…ProcessCommand(string)`
— that path is unreachable (private field); the page explains why.

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

## 4. Art (per SPEC's art plan — placeholder or generate)

Read `SPEC.md`'s `**art**` line — it holds the **one mod-level** art choice made at
interview time (placeholder or generate). Do NOT re-ask here. Two branches follow. If
generate, apply it to every card portrait in the mod using each card's own SPEC subject.

### Placeholder (the default — do nothing)

Leaving the art file absent makes the scaffolded base class fall back to the template
default, and the mod loads fine on it: a **relic** falls back to `relic.png` if
`images/relics/<slug>.png` is absent; a **potion** falls back to `potion.png` when
`images/potions/<slug>.png` is absent (the base's `PotionImagePath` `Exists()` check); a
**card** renders on the default portrait when `images/card_portraits/big/<slug>.png` is
absent. This is the fast path — nothing to build, no backend, no dev box. Skip to §5.

### Generate (custom sprite via `tools/gen_sprite.py`)

Supported sprite specs (see `sts2-api` → `reference/art-contract.md` for the full
contract):
- **`--spec card`** — the one portrait a normal card loads, **1000×760 landscape**, full-
  bleed (chroma OFF), written to `card_portraits/big/<slug>.png`. **Live-verified in-game.**
  The 606×852 "full art" size is **Ancient-rarity only and out of scope — we never make it**.
- **`--spec relic` / `--spec power`** — a **256×256** cut-out icon, `fit: contain`, magenta
  chroma-key ON (so the prompt must ask for a solid flat `#FF00FF` background — see the
  contract). **Live-verified in-game.** Each writes **two files** (the tool does both
  automatically): `relics/<slug>.png` + `relics/big/<slug>.png` for a relic (bar icon +
  detail popup), `powers/<slug>.png` + `powers/big/<slug>.png` for a power (status icon +
  the big apply/expire notification). A **relic** also has an optional `<slug>_outline.png`
  hover outline — we don't generate it; a missing one harmlessly falls back to the
  template's default outline (looks fine). **power** has no outline.
  **Prereq:** the relic/power subclass must extend the template base (`<ModName>Relic` /
  `<ModName>Power`), NOT `CustomRelicModel`/`CustomPowerModel` directly — the template base
  is what wires the loose-PNG icon paths, so a direct subclass shows the default icon even
  with the PNG present (see `recipes/power.md`).
- **`--spec potion`** — a **256×256** cut-out icon, `fit: contain`, magenta chroma-key ON
  (prompt asks for a solid flat `#FF00FF` background), a loose PNG like relic/power — **not**
  a `.tres` atlas. **Live-verified in-game.** Writes **ONE file**, `potions/<slug>.png` (the
  bar icon, hover tooltip, and use VFX all reuse that single texture — no `big/`). Art
  direction: draw the bottle **tilted ~45° leaning right** (STS2's potion display angle; see
  `art-contract.md`). **Prereq:** the potion subclass must extend the template base
  (`<ModName>Potion`), which the template does NOT scaffold — add it + a `PotionImagePath`
  helper per `recipes/potion.md`; a direct `CustomPotionModel` subclass shows the default icon.

1. **Build the prompt (three segments — see `art-contract.md`).** ① the fixed STS2 style
   descriptor (verbatim, incl. the "reference images = STYLE ONLY, don't reuse their
   objects" guard), ② the visual subject you *translate* from the card's **name**
   (flavor secondary) — NOT its damage/keyword numbers; mechanics have no picture, and
   painting them ("two blood drops" for "lose 2 HP") looks literal and awkward. Write ②
   as **two-to-four sentences describing one dramatic, centered, frozen-mid-motion
   subject with a warm rim light** (e.g. "Firebolt" → *a blazing arrow of living fire
   streaking diagonally mid-flight, trailing embers, orange-to-yellow rim light on its
   edge*), not a keyword list. ③ the fixed structural/negative constraints. You write
   it — don't make the user do it. Only ② differs per element; ①③ are shared guardrails.
   **For a `relic`/`power` icon** the same name→subject translation applies, but since it's
   a cut-out (chroma ON), ③ must also ask for a **solid flat `#FF00FF` magenta background,
   no gradient** so the tool can key it out cleanly (the contract's cut-out rule).
1a. **Confirm before spending.** Generating calls the user's paid API, so show the
   assembled prompt + the subject you derived and get a one-line yes before the first
   generate. If unhappy with the result, adjust ② and re-run (the regenerate loop) —
   don't silently keep spending.
2. **Locate the mod's images dir**: `<work dir>/<ModName>/images` (the resource subdir
   the template made; `<slug>` = lowercased prefix-stripped id, same as the loc keys).
3. **Run the tool** (`${GAME_TOOLS_DIR}` resolves per install — same as `build.py`).
   Use the `--spec` matching SPEC's element (`card` / `relic` / `power`):
   ```
   python ${GAME_TOOLS_DIR}/gen_sprite.py generate \
     --spec <card|relic|power> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --config <path to art-backend.json> \
     --reference ${STS2_API_SKILL_DIR}/reference/art-samples
   ```
   `--reference` passes the shipped STS2 style samples (Layer 2 few-shot) — keep it on, and
   point it at the **root** `art-samples` dir (as shown): the tool auto-picks the `card/`,
   `relic/`, or `power/` subdir matching `--spec`, so a relic never gets card refs. Backends
   that accept reference images (gpt-image-1 edits, Gemini/nano-banana, ComfyUI) imitate the
   game style far better, and plain text-to-image backends just ignore it.
   The tool POSTs to the user's backend, then chroma-keys (per spec — OFF for a full-bleed
   `card`, ON for a cut-out `relic`/`power` icon) / fits / resizes to the exact contract
   size and writes `<slug>.png` at the spec's sub-path. Each spec makes exactly one file
   (a relic's optional `_outline.png` is not generated — see above).
   Local file instead of a backend? Use `gen_sprite.py import --input <file> …`.
4. **No backend / failure → fall back to placeholder, don't block.** If the user chose
   generate but has no `art-backend.json`, or the tool exits non-zero (it prints a clear
   reason and writes `.gen_sprite.log`), record that in `MEMORY.md`, tell the user the
   mod will use placeholder art, and continue. Art never blocks the pipeline.
5. **Regenerate/tweak** is just re-running step 3 with an adjusted prompt (or a different
   `--input`), then rebuilding. The `.pck` rebuild in `build.md` picks up whatever PNG is
   at the path — placeholder if none, the custom one if present.

Whether placeholder or generated, the `.pck` build (`build.md`) is what makes the art
reach the game — a code-only `dotnet build` won't (same rule as localization).

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
any Cmd choices, which DRIVER body the harness uses, and the **art outcome**
(placeholder, or generated `<slug>.png`/`big/<slug>.png` — and if generate was chosen
but fell back to placeholder, why). Mark `author` and `art` done in `PLAN.md`. Then go
to `build.md`.
