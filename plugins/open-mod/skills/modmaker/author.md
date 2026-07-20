# Author — write the element, localization, and marker

Goal: fill in ONLY the effect logic on top of the recipe skeleton, add the
localization JSON, and inject the self-test marker. Everything structural
(class skeleton, `[Pool]`, image paths) comes from the recipe — don't reinvent it.

## 0. Read the quirks and the recipe first

- Read `quirks.md` before writing any C#.
- Query the **sts2-api** skill for the recipe matching SPEC's **element**:
  `recipes/relic.md` for a relic, `recipes/potion.md` for a potion, `recipes/card.md`
  for a card. For a **card or power**, also read `reference/mechanics.md` first
  (DynamicVars, SmartFormat descriptions, shared enums). If a Card/relic/potion/power
  display selects bounded vanilla text effects, also read
  `reference/content-text-effects.md` and apply only its per-surface allowlist. If the effect needs a
  buff/debuff no vanilla power covers, read `recipes/power.md` and author the custom
  power as a dependency. If SPEC declares custom keywords, also read
  `recipes/keyword.md`: emit the generated enum field and `card_keywords.json`, attach
  it to each host Card, and implement the named rule separately from its tooltip. If SPEC
  declares a card enchantment, read `recipes/enchantment.md`, author
  `CustomEnchantmentModel`, and attach it through `CardCmd.Enchant<T>`; never substitute
  the unrelated run-level `CustomModifierModel`. If SPEC declares a custom orb, read
  `recipes/orb.md`, author `CustomOrbModel`, and make the real host channel it via
  `OrbCmd.Channel<T>`; preserve separate passive and evoke observations, and keep the
  recipe's checked icon plus explicit Spine-scene/channel-SFX fallbacks. For an **enemy
  encounter** (`element: enemy encounter`), read `recipes/monster.md` and author BOTH the
  `CustomMonsterModel` and the `CustomEncounterModel(RoomType.Monster)` it spawns as one
  slice. Implement SPEC's compact move contract with `MoveState`, explicit `FollowUpState`,
  and `ConditionalBranchState` only where declared. Use the recipe's grounded intent/effect
  patterns for buff/Power, debuff, block/heal, multi-hit, and composite actions. Monster
  attacks use `.FromMonster(this).Execute(null)` (**never** `.Targeting()`), and the
  diagnostic trigger marker goes on the enemy's move; do not model the pair as two
  `elements` + an interaction. Keep the recipe's checked static-body factory plus explicit
  fallback scene; animation is outside this pass. For an **event / World Node** (`element: event`),
  read `recipes/event.md`: author one `CustomEventModel`, nested `EventLoc` pages/options,
  public-Cmd consequences, and explicit page/finish flow; no `[Pool]` or manual `AddEvent`.
  Also read `reference/event-outcomes.md` when SPEC includes selections, rewards,
  conditional pages, or special combat; read `reference/event-vfx.md` when it selects
  `portrait_halo`; read `reference/event-text-effects.md` when descriptions select bounded
  vanilla text effects; read `reference/event-option-presentation.md` when enabled options
  select typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings. For a
  **Character Foundation** (`element: character`), read
  `recipes/character.md`: keep the character template's `PlaceholderCharacterModel` and
  three pool bases, fill exact starters/HP/loc, and never call `AddCharacter` manually.
  If SPEC selects a character resource, read `reference/character-resource.md`; if it
  selects a bounded ordered semantic buffer/dynamic output, read
  `reference/ordered-card-buffer.md`.
  Read `reference/capability-kernel.md` only when the selected resource UI needs its exact
  verified combat-UI adapter. Prefer public/BaseLib, emit only selected self-contained
  modules, and do not generalize the adapter into alternative-energy patches, visible
  zone UI, C/D access, assembly-wide `PatchAll`, or `OpenMod.Runtime`.
  Pull the skeleton, the trigger/usage rules, the effect
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

**Custom orb** - add `<ModName>Code/Orbs/<OrbName>.cs` from `recipes/orb.md`:

- Extend `CustomOrbModel`; no `[Pool]`. Implement channel, passive, and evoke as separate
  behavior contracts through a real Card/relic/power host.
- Keep the existence-checked `CustomIconPath`: generated art is one 100x100 icon shared by
  the smart tooltip and trigger flash. Its missing-file branch returns the Frost icon.
- Keep the explicit Frost `CustomSpritePath` and `CustomChannelSfx`. The icon is not the
  persistent combat body; a custom Spine scene is later animation work, and null fallbacks
  emit missing custom-id scene/audio errors.

**Enemy encounter** — author two classes as one slice (see `recipes/monster.md`), no
`[Pool]` on either:

- `<ModName>Code/Monsters/<Name>.cs` extends `CustomMonsterModel`: set `MinInitialHp`/
  `MaxInitialHp` (equal for deterministic HP), then translate every SPEC move to one
  `MoveState` whose intent list matches every visible effect. Link deterministic order with
  explicit `.FollowUpState`; for a declared condition, add one `ConditionalBranchState`
  with exhaustive ordered predicates and include it in the machine's state list. A
  self-buff/custom Power uses `PowerCmd.Apply<T>` on `Creature`; a player debuff applies to
  `targets`; block/heal use `CreatureCmd.GainBlock/Heal`; multi-hit uses matching
  `MultiAttackIntent(N, R)` + `.WithHitCount(R)`; a composite move lists and awaits every
  effect in order. Every attack ends with `.FromMonster(this).Execute(null)` — **never
  `.Targeting()`** (that is the card pattern and it hangs the enemy turn).
- Declare `ModVisualPath` at `images/monsters/<slug>.png`; existence-check it in
  `CreateCustomVisuals()` and call `NodeFactory<NCreatureVisuals>.CreateFromResource` only
  when present. Keep `CustomVisualPath` on `creature_visuals/fallback` for the missing-file
  branch, and set `HasDeathSfx => false`. Never return the PNG from `CustomVisualPath`.
- If the monster needs a custom buff/debuff, author its power from `recipes/power.md` and
  include all three `powers.json` keys. A buff is not proven by attachment alone: SPEC and
  Tier 2 must observe its downstream effect on a later move.
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
- `GenerateInitialOptions()` returns the authored options. Each method uses the confirmed
  public Cmd/selection/reward vocabulary against `Owner`, awaits blocking overlays, logs
  the observed state delta, then follows SPEC with `SetEventFinished`, `SetEventState`, or
  one special-combat transition.
- If any option enters combat, author its monster + encounter dependency from
  `recipes/monster.md`, set `IsShared => true`, and call
  `EnterCombatWithoutExitingEvent<TEncounter>(extraRewards, shouldResumeAfterCombat)`.
  A resumable branch overrides `Resume(AbstractRoom)` and restores its exact named page;
  a terminal branch proceeds to the map. Never emit a second combat from the same mutable
  Event instance or a direct merchant/rest/treasure room transition.
- Override `CustomInitialPortraitPath` with the recipe's existence check: use the generated
  `images/events/<event-slug>.png` when present, otherwise the verified vanilla
  `this_or_that.png` fallback. For every explicitly requested page portrait, check
  `images/events/<event-slug>_<page-key-lower>.png` and call `NEventRoom.SetPortrait`
  immediately before the page transition; when absent, retain the current portrait. Clean
  owned portrait child nodes before a switch.
- When SPEC selects `portrait_halo`, emit the exact bounded helper from
  `reference/event-vfx.md`, attach page profiles through `OnRoomEnter`/the portrait host,
  honor Instant/Fast mode, and explicitly `QueueFreeSafely` every owned named root before
  page, portrait, combat, or finish transitions. Do not use `CustomVfxPath`. Custom phobia
  art, arbitrary VFX, custom layouts, and Ancient background assets remain unsupported.
- When SPEC selects vanilla Event text effects, apply only the exact bounded tags from
  `reference/event-text-effects.md` around the named phrases in `EventPageLoc` and
  `EventOptionLoc` descriptions. Keep titles plain; emit no helper node or cleanup code.
- When an enabled option selects typed Hover Tips, pass the exact grounded
  `HoverTipFactory` values through `Option`; do not emit a locked-option workaround. For
  relic-backed presentation, use `RelicOption<T>` for native title/description/metadata and
  keep semantic acquisition in a separate awaited `RelicCmd.Obtain<T>`. Preserve the
  normal-layout relic image as a presentation gap rather than generating an Ancient Event.
- When a choice pays HP or Max HP, apply `ThatDoesDamage` or `ThatDecreasesMaxHp` to the
  generated option using the exact decimal cost used by its Cmd. The helper is warning-only,
  and its exact-cost boundary is inclusive; never substitute differently rounded values or
  warning-colored text.

**Character Foundation** — use the classes scaffolded by `alchyrsts2charmod` and
`recipes/character.md`:

- Fill the `PlaceholderCharacterModel` subclass with exact `StartingHp`, Basic-card
  `StartingDeck`, Starter `StartingRelics`, and `ModelDb.*Pool<T>()` references.
- Do not call `AddCharacter`, instantiate the character, or add manual registration;
  the BaseLib 3.3.5 `CustomCharacterModel` constructor owns registration.
- Author concrete card/relic/potion members through the existing recipes while retaining
  the character template's inherited `[Pool(typeof(<ModName>*Pool))]` attributes.
- Add all 14 `CharacterLoc` values and the four Architect keys from the character recipe.
- Keep `PlaceholderCharacterModel` plus template icons; character art/animation is not a
  Foundation gate. A Foundation-only SPEC emits no capability-kernel code. A resource
  SPEC emits its named domain state/payment rules plus only the exact selected UI kernel.
  An ordered-buffer SPEC emits combat-scoped semantic state, native source-card result
  piles, visible state text, and a configured output card. Never emit a retained-card
  `CustomPile` without a separately grounded UI lifecycle. Keep proof-only observers and
  assertions out of generated gameplay.

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
   `Enemies` (`e.Monster is TMonster`), and use the reference page's multi-turn helper. Before
   each `PlayerCmd.EndTurn` assert `NextMove.Id` plus its intent types/repeat count; afterward
   require the player's `TurnNumber` to advance, assert the matching
   `MonsterPerformedMoveEntry`, and inspect `CreatureAttackedEntry.DamageResults` plus the
   exact player/monster HP, Block, and Power states. Force every conditional outcome through
   its real state condition. Do NOT apply `PlatingPower` in this scenario (enemy hits must
   remain observable).
   **event** → the **`MapNode`** variant: enter the canonical custom event with
   `EnterRoomDebug(RoomType.Event, MapPointType.Unknown, ModelDb.Event<T>())`, wait for its
   real `NEventOptionButton`, read formatted nested loc, and drive every independent SPEC
   outcome family through real UI. Await card/reward overlays; identify the special
   encounter; prove the named `Resume` page or direct map branch; assert one combat per
   Event instance. For `portrait_halo`, assert movement/static Fast Mode behavior, visible
   headed pages, and explicit cleanup across page/combat transitions. For bounded rich
   text, assert the real `%EventDescription` host, installed effects, exact tagged
   localization, and a second page replacing the first page's tagged text.
   **character** → the **`RunStart` + `CombatPlayer`** variant: locate the real custom
   character button by normalized icon resource path, click it and Confirm, wait for
   `NRun.GlobalUi`, assert runtime HP/pools/starter multisets, enter combat, then assert
   designed `MaxEnergy` and the starter mechanic's independent state delta. Never select
   the first unlocked vanilla character.
   **capability-kernel maintainer canary** → use the two-combat `CombatPlayer` proof in
   `reference/capability-kernel.md`: Tier 1 asserts exact version/MVID target resolution,
   one owned postfix and idempotence; combat 1 asserts typed dispatch/state/listener plus
   the real hosted UI node; combat 2 asserts a distinct combat-scoped state generation.
   This route verifies infrastructure only and is not a substitute for the selected
   capability's gameplay invariant.
   **character resource** → use `reference/character-resource.md`: in combat 1 drive real
   gain and spender cards, assert affordable/unaffordable cases, successful/rejected
   payoff, floor, and live counter refresh; enter combat 2 and assert distinct zero state
   plus reset counter. Finish with `resource UI complete ... observed=all`.
   **ordered semantic buffer/dynamic output** → use `reference/ordered-card-buffer.md`: drive
   real source cards through their native result piles, assert order/capacity/
   non-destructive overflow and visible state, compile/clear the ordered snapshot, assert
   one `CardGeneratedEntry`, play the configured output, then prove a distinct empty state
   in combat 2. Reuse the owning character or `CombatPlayer` suite; do not create a project
   solely for this capability.
   For a multi-element SPEC, use
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

When display `text effects` is `vanilla`, apply semantic `text spans` only after the plain
description and SmartFormat placeholders are correct. Validate every tag against
`reference/content-text-effects.md`, keep tags balanced, do not wrap `:diff()` values in
another color, and never copy user-supplied raw markup. Titles, flavor, and selection
prompts stay plain.

For a **character**, use `CharacterLoc` for the 14 character values and
`ancients.json` for the four exact `THE_ARCHITECT.talk.<CHAR_ID>` keys in
`recipes/character.md`. For an **event**, use the recipe's in-code `EventLoc` / `EventPageLoc` /
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
generate, apply it to every supported asset in the mod using each element's own SPEC
subject.

### Placeholder (the default — do nothing)

Leaving the art file absent makes the scaffolded base class fall back to the template
default, and the mod loads fine on it: a **relic** falls back to `relic.png` if
`images/relics/<slug>.png` is absent; a **potion** falls back to `potion.png` when
`images/potions/<slug>.png` is absent (the base's `PotionImagePath` `Exists()` check); a
**card** renders on the default portrait when `images/card_portraits/big/<slug>.png` is
absent. This is the fast path — nothing to build, no backend, no dev box. For an **event**,
the class uses the recipe's `ResourceLoader.Exists` branch and returns the verified vanilla
portrait when `images/events/<slug>.png` is absent; the default event layout always preloads
a portrait. For an **enchantment**, its `CustomIconPath` existence check returns `null`
when `images/enchantments/<slug>.png` is absent, preserving the game's missing-icon
fallback.
For an **orb**, placeholder mode keeps the recipe's Frost icon, Spine scene, and channel
SFX fallbacks; it must not rely on the custom-id path convention. Skip to §5.
For an **enemy encounter**, the recipe checks `images/monsters/<slug>.png` and returns
`null` from `CreateCustomVisuals()` when absent, so the explicit built-in fallback scene
loads without a missing-resource error. Skip to §5.
For a **character**, keep the character template's icon PNGs and built-in scene fallbacks;
custom character sprite/animation generation is not supported in Foundation.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

Supported sprite specs (see `sts2-api` → `reference/art-contract.md` for the full
contract). Characters are **not yet** supported sprite specs; keep their template
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
- **`--spec enchantment`** — one **64×64** cut-out icon, `fit: contain`, magenta
  chroma-key ON, written to `enchantments/<slug>.png`. **Live-verified in the real hand-card
  tab and its hover tooltip.** Both consumers reuse the same `EnchantmentModel.Icon`; there
  is no `big/` variant. The subclass must use the recipe's existence-checked
  `CustomIconPath` so placeholder mode retains `MissingIconPath`.
- **`--spec orb`** - one **100x100** cut-out icon, `fit: contain`, magenta chroma-key ON,
  written to `orbs/<slug>.png`. **Live-verified in the real smart tooltip and trigger
  flash.** This does not generate the persistent combat Spine scene; retain the recipe's
  Frost scene and channel-SFX fallbacks.
- **`--spec monster`** - one **360x360** transparent static body, `fit: contain`, magenta
  chroma-key ON, written to `monsters/<slug>.png`. **Live-verified in both the real combat
  `NCreature` and default bestiary layout.** The concrete monster must use the recipe's
  existence-checked `CreateCustomVisuals()` factory and keep `CustomVisualPath` on the
  built-in scene fallback. This does not add Spine, move animation, or a phobia variant.
- **`--spec event`** — one opaque **3440×1613** normal/default-layout portrait slot per
  invocation, `fit: cover`, chroma-key OFF, written to `events/<slot-slug>.png`.
  **Live-verified in the real MapNode host for the initial and a later page.** Generate the
  initial slot plus only the later-page slots explicitly listed in SPEC. The event class
  must retain the checked initial fallback and keep the current portrait when optional
  page art is absent. This does not generate a phobia variant, custom layout, or Ancient
  background scene. The optional code-native `portrait_halo` is authored from
  `reference/event-vfx.md` and has no `gen_sprite.py` invocation.

1. **Build the prompt (three segments — see `art-contract.md`).** For card and the M5.5
   `relic`/`power`/`potion` icon specs,
   use ① the fixed STS2 style
   descriptor (verbatim, incl. the "reference images = STYLE ONLY, don't reuse their
   objects" guard), ② the visual subject you *translate* from the element's **name**
   (flavor secondary) — NOT its damage/keyword numbers; mechanics have no picture, and
   painting them ("two blood drops" for "lose 2 HP") looks literal and awkward. Write ②
   as **two-to-four sentences describing one dramatic, centered, frozen-mid-motion
   subject with a warm rim light** (e.g. "Firebolt" → *a blazing arrow of living fire
   streaking diagonally mid-flight, trailing embers, orange-to-yellow rim light on its
   edge*), not a keyword list. ③ the fixed structural/negative constraints. You write
   it — don't make the user do it. Only ② differs per element; ①③ are shared guardrails.
   **For a `relic`/`power`/`potion` icon** the same name→subject translation applies,
   but since it's a cut-out (chroma ON), ③ must also ask for a **solid flat `#FF00FF`
   magenta background, no gradient** so the tool can key it out cleanly.
   **For `enchantment`**, use the contract's dedicated micro-emblem template: bold slightly
   irregular silhouette, broad matte fills, one dominant hue with only one or two value
   steps, and almost no fine detail so it survives at 64x64. Do not turn it into a relic,
   glossy app icon, badge, or miniature scene.
   **For `orb`**, use the dedicated elemental-core template: a large irregular near-circle,
   chunky layered material forms, three-to-five broad values, dark internal occlusion,
   selective highlights, and contained glow. Do not request a generic vector glyph, glass
   marble, UI frame, detached particles, or persistent combat body.
   **For `monster`**, use the dedicated softly hand-painted render template, not Card's hard
   cel shading/radial burst. Translate the concept into one complete creature with broad
   values, gently modeled volume, controlled brush texture, selective edges, a restrained
   base palette, and focused accents. Keep a neutral front/3/4 pose, both feet on one
   baseline, the full silhouette inside the frame, and no ground/shadow/attack effect; the
   same still is shown for every move and in bestiary.
   **For `event`**, use the separate event template: derive one concrete opening situation,
   place the focal subject in the left third, and reserve darker low-detail center-right and
   lower-right space for the game's title, description, and options. Do not reuse the card
   prompt's centered-subject constraint or paint option reward numbers into the scene.
1a. **Respect the selected route's consent boundary.** For `runtime-imagegen`, the user's
   mod-level `generate` choice authorizes the initial one-image-per-asset native-tool run;
   it needs no separate API key, but follow any approval or usage warning presented by the
   host and never claim that host usage is free. For Vofy or BYO HTTP, show the assembled
   prompt, chosen model/backend, output count (**one**), and credit-spending action, then
   get a one-line yes for this exact paid generation. Never treat an earlier art preference
   as approval to spend through an external route. Every regeneration, on any route, needs
   a new confirmation after the user sees the current result.
2. **Locate the mod's images dir**: `<work dir>/<ModName>/images` (the resource subdir
   the template made; `<slug>` = lowercased prefix-stripped id, same as the loc keys).
3. **Acquire through the SPEC's `art source`, then import** (`${CLAUDE_PLUGIN_ROOT}/tools` resolves
   per install — same as `build.py`). Use the `--spec` matching SPEC's element.

   **Host-native image generation (`runtime-imagegen`):** use this route only when the
   current runtime actually exposes a callable raster image-generation tool. In Codex,
   follow the installed `imagegen` skill and use its built-in `image_gen` mode; do not
   switch to that skill's CLI/API fallback, which requires `OPENAI_API_KEY`, unless the
   user explicitly selected the separate `byo-http` route. A model name or installed skill
   file alone does not prove that the native tool is available.

   Issue one native image call per distinct asset with the assembled prompt. For a full-
   bleed card, request the landscape composition without a keyed background. For relic,
   power, potion, enchantment, orb icons, and monster bodies, keep the prompt's perfectly flat `#FF00FF`
   background; do not
   remove it with a runtime-specific helper because `gen_sprite.py import --chroma` owns
   that deterministic step. When the native tool supports reference images, randomly choose
   up to three type-matched files from
   `${CLAUDE_PLUGIN_ROOT}/skills/sts2-api/reference/art-samples/<spec>/`, make them visible using the
   runtime's normal local-image viewing mechanism, and label them STYLE REFERENCE ONLY. If reference inputs
   are unavailable, use the fixed text style descriptor alone.

   Inspect the generated image, then use the actual local file path reported by the host
   (Codex normally saves built-in results below `$CODEX_HOME/generated_images/`; do not
   assume that path for other runtimes). The route is unavailable if it produces no local
   image file. Pass that file through the existing normalizer:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py import \
     --spec <card|relic|power|potion|enchantment|orb|monster|event> --slug <slug> --input "<native-output.png>" \
     --out "<work dir>/<ModName>/images" [--chroma]
   ```
   Add `--chroma` only for `relic`, `power`, `potion`, `enchantment`, `orb`, and `monster`. The normalized project asset,
   not the host's raw output, is what the mod references and packages.

   **Vofy managed credits:** the user installs/authenticates Vofy themselves. Never run
   `vofy login`, inspect credential files, or put status/credit output in SPEC/MEMORY/logs.
   First run the read-only checks:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/tools/acquire_sprite.py preflight --model <chosen-model>
   vofy models <chosen-model>
   ```
   Read the live model capabilities before choosing `--image`, `--aspect-ratio`, or
   `--resolution`; do not hardcode a model or current price. Use the bundled pool only when
   that model supports image-to-image references. Pass the root directory once;
   `acquire_sprite.py` selects the matching spec and randomly samples three files. After
   step 1a's confirmation, submit exactly one synchronous paid task:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/tools/acquire_sprite.py create \
     --spec <card|relic|power|potion|enchantment|orb|monster|event> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --model <chosen-model> \
     [--aspect-ratio <confirmed-ratio>] [--resolution <confirmed-resolution>] \
     [--reference ${CLAUDE_PLUGIN_ROOT}/skills/sts2-api/reference/art-samples] --yes
   ```
   `--yes` means the user approved this exact prompt/model/one-image spend. The tool reruns
   preflight, downloads into a unique empty directory, requires exactly one image, then
   calls `gen_sprite.py import` (including chroma for cut-out specs). It never parses Vofy
   stdout for a filename. On timeout or ambiguous output, inspect `vofy tasks --plain`;
   never auto-resubmit because the first task may already have spent credits.

   **BYO HTTP backend:** run the existing generator:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py generate \
     --spec <card|relic|power|potion|enchantment|orb|monster|event> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --config <path to art-backend.json> \
     --reference ${CLAUDE_PLUGIN_ROOT}/skills/sts2-api/reference/art-samples
   ```
   `--reference` passes the shipped STS2 style samples (Layer 2 few-shot) — keep it on, and
   point it at the **root** `art-samples` dir (as shown). The tool auto-picks the matching
   `card`/`relic`/`power`/`potion`/`enchantment`/`orb`/`monster`/`event` subdir and randomly
   samples three distinct files; families are never mixed. Backends
   that accept reference images (gpt-image edits or Gemini/nano-banana) imitate the
   game style far better, and plain text-to-image backends just ignore it.
   The tool POSTs to the user's backend, then chroma-keys (per spec — OFF for a full-bleed
   `card`/`event`, ON for a cut-out `relic`/`power`/`potion`/`enchantment`/`orb`/`monster`) / fits /
   resizes to the exact contract size and writes every required path: one
   card/potion/enchantment/orb/monster/event file or two relic/power files. A relic's optional
   `_outline.png` is not generated (see above).
   **Local image:** use `gen_sprite.py import --input <file> ...`; for a magenta-backed
   relic/power/potion/enchantment/orb/monster source add `--chroma`.
4. **Unavailable/failure → bounded fallback, don't block.** A missing native image tool,
   native output with no local file, host-tool failure, missing Vofy/auth/credits,
   unsupported model flags, task failure/timeout, zero or multiple downloads, missing BYO
   config, or import failure must stop that route. Keep the placeholder unless the user
   explicitly selects BYO HTTP, Vofy, or local import instead. Never silently choose a paid
   backend or retry a possibly charged task. Record only the route/outcome in `MEMORY.md`,
   never account or credit output.
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
