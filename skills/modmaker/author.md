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
  power as a dependency. If SPEC declares custom keywords, also read
  `recipes/keyword.md`: emit the generated enum field and `card_keywords.json`, attach
  it to each host Card, and implement the named rule separately from its tooltip. If SPEC
  declares a card enchantment, read `recipes/enchantment.md`, author
  `CustomEnchantmentModel`, and attach it through `CardCmd.Enchant<T>`; never substitute
  the unrelated run-level `CustomModifierModel`. If SPEC declares a custom orb, read
  `recipes/orb.md`, author `CustomOrbModel`, and make the real host channel it via
  `OrbCmd.Channel<T>`; preserve separate passive and evoke observations. For an **enemy
  encounter** (`element: enemy encounter`), read `recipes/monster.md` and author BOTH the
  `CustomMonsterModel` and the `CustomEncounterModel(RoomType.Monster)` it spawns as one
  slice — the monster's move body attacks with `.FromMonster(this).Execute(null)` (**never**
  `.Targeting()`), and the diagnostic trigger marker goes on the enemy's move; do not model the pair as
  two `elements` + an interaction. For an **event / World Node** (`element: event`),
  read `recipes/event.md`: author one `CustomEventModel`, nested `EventLoc` pages/options,
  a public-Cmd consequence, and a `SetEventFinished` result page; no `[Pool]` or manual
  `AddEvent`. Pull the skeleton, the trigger/usage rules, the effect
  building blocks, and the loc-key derivation rule. Do **not** guess API names — if
  the effect needs a Cmd not in the recipe, follow `grounding.md` — at runtime that
  means the rest of the pack (`reference/mechanics.md`, `build-constraints.md`,
  snapshots, `errors.md`), and if it's genuinely not there, report a pack gap. Never
  invent a Cmd name — that's the #1 way the repair loop burns its attempts.
- If SPEC has a non-`none` **state** block, also read
  `reference/stateful-mechanics.md` before writing the hook. Implement its event,
  threshold/phase, lifetime, reset, persistence, UI meaning, and proof as one contract;
  never infer lifetime from the C# field that happens to be easiest.

## 1. Write the element class

**Relic** — add `<ModName>Code/Relics/<RelicName>.cs`. Use the recipe skeleton, then:

- Set `Rarity` from SPEC.
- Keep `[Pool(typeof(<Pool>))]` — **omitting it throws at registration** (errors.md).
- Override the hook matching SPEC's trigger (recipe's "Trigger hooks" table). For
  combat-start: `AfterSideTurnStart` + `participants.Contains(Owner.Creature)` +
  `Owner.PlayerCombatState!.TurnNumber <= 1` guards.
- Fill **only** the effect block with the confirmed Cmds/RNG from the recipe. `await`
  every Cmd. Use `Rng`, never `System.Random`. Call `Flash()` when it visibly triggers.
- For stateful relics, follow `reference/stateful-mechanics.md`: run-lifetime progress is
  a supported `[SavedProperty]` `int`/`bool` and is never cleared at combat end; combat-
  local fixed/periodic turns read `PlayerCombatState.TurnNumber`; turn/combat fields reset
  only at the SPEC boundary. Any visible setter calls `InvokeDisplayAmountChanged()`.

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

**Enemy encounter** — author two classes as one slice (see `recipes/monster.md`), no
`[Pool]` on either:

- `<ModName>Code/Monsters/<Name>.cs` extends `CustomMonsterModel`: set `MinInitialHp`/
  `MaxInitialHp` (equal for deterministic HP), and `GenerateMoveStateMachine()` returning a
  `MonsterMoveStateMachine` built from a `MoveState("<ID>", <MoveBody>, new SingleAttackIntent(<N>))`
  with `.FollowUpState` set to loop. The `<MoveBody>(IReadOnlyList<Creature> targets)` deals
  damage with `DamageCmd.Attack(<N>m).FromMonster(this).Execute(null)` — **never
  `.Targeting()`** (that is the card pattern and it hangs the enemy turn).
- `<ModName>Code/Encounters/<Name>Encounter.cs` extends `CustomEncounterModel`, calls
  `base(RoomType.Monster)`, and overrides `IsValidForAct`, `AllPossibleMonsters`
  (`ModelDb.Monster<T>()`), and `GenerateMonsters()` (`ModelDb.Monster<T>().ToMutable()` +
  slot, `null` slot ok). Do **not** call `AddEncounter` manually — the base constructor does it.

**Event / World Node** — create `<ModName>Code/Events/` and add `<Name>.cs` from
`recipes/event.md`:

- Extend `CustomEventModel`; no `[Pool]` and no manual `AddEvent` (the base constructor
  registers it). Leave `Acts` empty for the default all-act placement unless SPEC scopes it.
- Override `Localization` with `EventLoc` containing the title, `INITIAL` page, every
  `EventOptionLoc`, and every result page. The key for `Option(Method)` must be the exact
  upper-snake slug of the method name.
- `GenerateInitialOptions()` returns `Option(<Method>)`. The method uses confirmed public
  Cmds against `Owner`, logs the observed state delta, then calls
  `SetEventFinished(PageDescription("<RESULT_KEY>"))` (or deliberately `SetEventState` for
  another choice page).
- Override `CustomInitialPortraitPath` with the recipe's verified vanilla placeholder;
  custom event portrait/background generation is not yet supported.

**Counter Power amount-domain gate (applies to every source element)** — before writing
any custom Counter mutation, read that Power's `amount domain` from SPEC. The default
nonnegative domain means:

- positive gain/application may use `PowerCmd.Apply<T>`;
- consumption must call `GetPower<T>()`, spend zero when absent, clamp the actual spend
  to the existing `Amount`, then call `PowerCmd.ModifyAmount` on that instance with
  `null, null` applier/card source (the vanilla internal-consumption context);
- a negative `PowerCmd.Apply<T>` is forbidden for consumption because it can create a
  missing Power with a negative amount;
- every finite SPEC bound must be enforced by clamping gain/consumption to current
  headroom, and a signed domain is allowed only with explicit negative-stack semantics;
- because amount hooks can rewrite a requested offset, capture the Cmd return and re-read
  the retained Power. The domain and Tier-2 assertion apply to that final post-hook state,
  and logs must distinguish requested offset, actual offset, and remaining amount.

Use the exact copyable sequence in `recipes/power.md`; do not treat `PowerVar<T>` or
`AllowNegative` as min/max validation.

## 2. Inject the load and diagnostic markers

The Alchyr template's `MainFile.cs` does NOT log anything by
default — you must add the **load** marker yourself, or tier-1 verify silently
finds nothing. In `MainFile.Initialize()`, right after `harmony.PatchAll();`:

```csharp
Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");
```

Then log a **diagnostic** marker inside the trigger showing what code ran
(a relic's combat-start hook, a potion's `OnUse`, a card's `OnPlay`, an enemy's move body,
or an event option method):

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ElementName> fired/used: <requested outcome>");
```

The load marker proves Tier 1. The trigger marker stays for diagnosis, but it is **not**
Tier-2 proof: preview/calculation hooks may log without committing state. The harness in
the next step independently asserts post-state and emits the only accepted proof marker.

## 2.5 Emit the tier-2 self-test harness

This is what makes tier-2 automatic — the effect fires and is grepped with **no human at
the keyboard, no dev-console typing**. Query the **sts2-api** skill for
`reference/selftest-harness.md` and follow it. In short:

1. Emit `<ModName>Code/SelfTest.cs` from that page. The arg gate, menu→run navigation,
   timeout, catch, terminal markers, and ship-safety are shared by every type; the hosted
   room entry is scenario-specific. Keep it in the **same namespace as `MainFile.cs`**
   (`<ModName>.<ModName>Code`) so it reaches `MainFile.Logger`.
2. Fill **exactly one** source DRIVER body based on the source element's real type:
   **relic** → `BeforeCombat` (grant it, its `AfterSideTurnStart` fires on its own);
   **card** → `InCombat` (`GainEnergy` → spawn into hand → `CardCmd.AutoPlay`);
   **potion** → `InCombat` (`TryToProcure` → `EnqueueManualUse`);
   **enemy encounter** → the **`CombatEnemy`** variant: enter the custom encounter via
   `ModelDb.Encounter<TEncounter>().ToMutable()` + `EnterRoomDebug`, confirm the monster in
   `Enemies` (`e.Monster is TMonster`), then `PlayerCmd.EndTurn(player, canBackOut: false)`
   (void — do NOT await) and assert the player HP delta after the turn resumes. Do NOT apply
   `PlatingPower` in this scenario (the enemy hit must land).
   **event** → the **`MapNode`** variant: enter the canonical custom event with
   `EnterRoomDebug(RoomType.Event, MapPointType.Unknown, ModelDb.Event<T>())`, wait for its
   real `NEventOptionButton`, read formatted nested loc, click it with `UiHelper.Click`, and
   assert the SPEC's run-state consequence plus result page. For a multi-element SPEC, use
   that same source driver, then walk `interactions` in dependency order and
   observe each dependent marker/state invariant. There is no `combo` element or separate
   registration path; the reference page's card→power example shows the additional waits
   and `EndTurn` needed by that particular interaction. A nonnegative Counter `consumes`
   edge must also run the reference page's zero/fewer-than-N/at-least-N boundary matrix and
   assert that no negative instance appears. Its § CombatEnemy shows the full enemy-encounter
   driver body.
   A stateful source must instead use the page's **stateful cadence** variant: assert the
   `N-1` no-fire state, the exact threshold delta, and the reset/carry-over boundary. A
   run-lifetime `[SavedProperty]` additionally round-trips through
   `SavedProperties.From`/`Fill`; a run cadence must enter a second combat rather than
   mutating the property directly to simulate carry-over.
3. In every driver, snapshot concrete state, drive the real source, assert the SPEC's exact
   post-state, then call the shared `StateProof(...)`. Its structured
   `[T2MOD-SELFTEST] <ModName> state proof:` line must include expected and observed values;
   a broad `played/fired/used` marker never qualifies.
4. Add the **gated arm line** to `MainFile.Initialize()`, right after the load marker:

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

For an **event**, use the recipe's in-code `EventLoc` / `EventPageLoc` /
`EventOptionLoc` inside the event class. Do not also add `events.json` for the same keys;
BaseLib prefixes the relative nested keys with the real `Id.Entry` at `ModelDb.Init`.

For the JSON-backed types, add entries to `<ModName>/localization/eng/<table>.json` — **`relics.json`** for a
relic, **`potions.json`** for a potion, **`cards.json`** for a card, **`powers.json`**
for a custom power, **`monsters.json`** + **`encounters.json`** for an enemy encounter.
**Keys are FLAT and prefixed** (recipe's loc-key rule + errors.md "raw-key title"):

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
`.title/.description` with `{Amount}` for the stack count. An **enemy encounter** takes
two tables: `monsters.json` with just `<PREFIX>-<MONSTER_SLUG>.name`, and `encounters.json`
with `<PREFIX>-<ENCOUNTER_SLUG>.title` + `.loss`. Use the exact `<PREFIX>-<SLUG>`
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
absent. This is the fast path — nothing to build, no backend, no dev box. For an **event**,
the class must instead set `CustomInitialPortraitPath` to the verified vanilla placeholder
from `recipes/event.md`; the default event layout always preloads a portrait. Skip to §5.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

Supported sprite specs (see `sts2-api` → `reference/art-contract.md` for the full
contract):
Events and enemy encounters are **not** supported sprite specs; keep their provisional
placeholders and do not call `gen_sprite.py` for them.
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
1a. **Confirm before spending.** Show the assembled prompt, chosen model/backend, output
   count (**one**), and that this action spends credits; get a one-line yes for this exact
   generation. Never treat an earlier art preference as spending approval. Every
   regeneration needs a new confirmation.
2. **Locate the mod's images dir**: `<work dir>/<ModName>/images` (the resource subdir
   the template made; `<slug>` = lowercased prefix-stripped id, same as the loc keys).
3. **Acquire through the SPEC's `art source`, then import** (`scripts` resolves
   per install — same as `build.py`). Use the `--spec` matching SPEC's element.

   **Vofy managed credits:** the user installs/authenticates Vofy themselves. Never run
   `vofy login`, inspect credential files, or put status/credit output in SPEC/MEMORY/logs.
   First run the read-only checks:
   ```
   python scripts/acquire_sprite.py preflight --model <chosen-model>
   vofy models <chosen-model>
   ```
   Read the live model capabilities before choosing `--image`, `--aspect-ratio`, or
   `--resolution`; do not hardcode a model or current price. Pick at most three files from
   `./reference/art-samples/<spec>/` only when that model supports
   image-to-image references. After step 1a's confirmation, submit exactly one synchronous
   paid task:
   ```
   python scripts/acquire_sprite.py create \
     --spec <card|relic|power|potion> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --model <chosen-model> \
     [--aspect-ratio <confirmed-ratio>] [--resolution <confirmed-resolution>] \
     [--reference <sample.png> ...] --yes
   ```
   `--yes` means the user approved this exact prompt/model/one-image spend. The tool reruns
   preflight, downloads into a unique empty directory, requires exactly one image, then
   calls `gen_sprite.py import` (including chroma for icon specs). It never parses Vofy
   stdout for a filename. On timeout or ambiguous output, inspect `vofy tasks --plain`;
   never auto-resubmit because the first task may already have spent credits.

   **BYO HTTP backend:** run the existing generator:
   ```
   python scripts/gen_sprite.py generate \
     --spec <card|relic|power|potion> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --config <path to art-backend.json> \
     --reference ./reference/art-samples
   ```
   `--reference` passes the shipped STS2 style samples (Layer 2 few-shot) — keep it on, and
   point it at the **root** `art-samples` dir (as shown): the tool auto-picks the `card/`,
   `relic/`, `power/`, or `potion/` subdir matching `--spec`, so a relic never gets card refs. Backends
   that accept reference images (gpt-image-1 edits, Gemini/nano-banana, ComfyUI) imitate the
   game style far better, and plain text-to-image backends just ignore it.
   The tool POSTs to the user's backend, then chroma-keys (per spec — OFF for a full-bleed
   `card`, ON for a cut-out `relic`/`power`/`potion` icon) / fits / resizes to the exact
   contract size and writes every required path: one card/potion file or two relic/power
   files. A relic's optional `_outline.png` is not generated (see above).
   **Local image:** use `gen_sprite.py import --input <file> ...`; for a magenta-backed
   relic/power/potion source add `--chroma`.
4. **Unavailable/failure → bounded fallback, don't block.** Missing Vofy/auth/credits,
   unsupported model flags, task failure/timeout, zero or multiple downloads, missing BYO
   config, or import failure must stop that route. Tell the user what failed and offer BYO
   HTTP, local import, or placeholder. Never silently choose another paid backend or retry
   a possibly charged Vofy task. Record only the route/outcome in `MEMORY.md`, never account
   or credit output.
5. **Regenerate/tweak** means adjusting the subject/prompt, obtaining fresh approval, then
   rerunning the chosen acquisition + import. The `.pck` rebuild in `build.md` picks up
   whatever PNG is at the path — placeholder if none, the custom one if present.

Whether placeholder or generated, the `.pck` build (`build.md`) is what makes the art
reach the game — a code-only `dotnet build` won't (same rule as localization).

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
any Cmd choices, the state lifetime/reset/persistence (when present), which DRIVER body
the harness uses, and the **art outcome**
(placeholder, or generated `<slug>.png`/`big/<slug>.png` — and if generate was chosen
but fell back to placeholder, why). Mark `author` and `art` done in `PLAN.md`. Then go
to `build.md`.
