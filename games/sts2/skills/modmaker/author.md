# Author — write the element, localization, and marker

Goal: translate the accepted framework-neutral SPEC through the selected adapter,
fill only the effect logic, add localization, and inject the shared diagnostics.
Registration, model templates, localization-key derivation, and asset profiles come
from the adapter rather than the user-facing SPEC.

Read `semantic-contract.md` first, then read the selected framework reference
(`sts2-api/reference/ritsulib-adapter.md` for the current target). RitsuLib-specific
snippets live in that reference and the surface recipe it routes to; do not copy a
second framework branch into this file.

> **Adapter guard:** the pinned RitsuLib scaffold/build path and its recipes are the only
> active implementation. No historical-framework branch is available.

## 0. Read the quirks and the recipe first

- Read `quirks.md` before writing any C#.
- Query the **sts2-api** skill for the recipe matching SPEC's **element**:
  `recipes/relic.md` for a relic, `recipes/potion.md` for a potion, `recipes/card.md`
  for a card. For a **card or power**, also read `reference/mechanics.md` first
  (DynamicVars, SmartFormat descriptions, shared enums). For a Card whose SPEC has
  non-`none` `calculated values` or `variable tooltips`, also read
  `reference/card-computed-values.md`; it owns formula timing, preview/execution parity,
  icon formatters, typed Power semantics, and shared tooltip localization. If a
  Card/relic/potion/power
  display selects bounded vanilla text effects, also read
  `reference/content-text-effects.md` and apply only its per-surface allowlist. If the effect needs a
  buff/debuff no vanilla power covers, read `recipes/power.md` and author the custom
  power as a dependency. If SPEC declares custom keywords, also read
  `recipes/keyword.md`: emit the generated enum field and `card_keywords.json`, attach
  it to each host Card, and implement the named rule separately from its tooltip. If SPEC
  declares a card enchantment, read `recipes/enchantment.md`, author
  `ModEnchantmentTemplate`, register it through `.Enchantment<T>()`, and attach it through
  `CardCmd.Enchant<T>`; never substitute an unrelated run-level Modifier. If SPEC declares
  a custom orb, read `recipes/orb.md`, author `ModOrbTemplate`, register it through
  `.Orb<T>()`, and make the real host channel it via
  `OrbCmd.Channel<T>`; preserve separate passive and evoke observations, and keep the
  recipe's checked icon plus explicit Spine-scene/channel-SFX fallbacks. For an **enemy
  encounter** (`element: enemy encounter`), read `recipes/monster.md` and author BOTH the
  RitsuLib `ModMonsterTemplate` and `ModEncounterTemplate` it spawns as one slice. Register
  both exactly once through the scaffold's content pack, with an explicit encounter
  `RoomType`. Implement SPEC's compact move contract with `MoveState`, explicit `FollowUpState`,
  and `ConditionalBranchState` only where declared. Use the recipe's grounded intent/effect
  patterns for buff/Power, debuff, block/heal, multi-hit, and composite actions. Monster
  attacks use `.FromMonster(this).Execute(null)` (**never** `.Targeting()`), and the
  diagnostic trigger marker goes on the enemy's move; do not model the pair as two
  `elements` + an interaction. Keep the recipe's checked static-body factory plus explicit
  fallback scene; animation is outside this pass. For an **event / World Node** (`element: event`),
  read `recipes/event.md`: author one `ModEventTemplate`, flat nested `events.json`,
  explicit `EventOption` keys, public-Cmd consequences, and explicit page/finish flow;
  register it once with `.SharedEvent<T>()` or `.ActEvent<TAct,T>()` and add no `[Pool]` or
  manual `AddEvent`.
  Also read `reference/event-outcomes.md` when SPEC includes selections, rewards,
  conditional pages, or special combat; read `reference/event-vfx.md` when it selects
  `portrait_halo`; read `reference/event-text-effects.md` when descriptions select bounded
  vanilla text effects; read `reference/event-option-presentation.md` when enabled options
  select typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings; read
  `reference/event-native-presentation.md` when options select native Card/relic
  acquisition presentation, `weak_short` screen shake, or built-in `trial_noble` VFX; read
  `reference/forced-followup-event.md` when SPEC selects its Quest Card -> target Event
  composition. For a
  **Character Foundation** (`element: character`), read
  `recipes/character.md`: use `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` and
  the three `TypeList*PoolModel` bases, fill exact starters/HP/Gold/loc, and register the
  Character plus starters/members once through the content pack.
  If SPEC selects any Character art profile or richer resource/buffer presentation, also
  read `reference/character-presentation.md` and obey its per-consumer promotion/fallback
  boundary. If SPEC selects native Ancient/Architect dialogue, read
  `reference/ancient-dialogue.md` and use only its localization route.
  If SPEC selects a character resource, read `reference/character-resource.md`; if it
  selects a bounded ordered semantic buffer/dynamic output, read
  `reference/ordered-card-buffer.md`.
  A selected resource UI uses RitsuLib's public `RegisterCombatUi` route from
  `reference/character-resource.md`. If another capability has no documented public
  game/framework seam, report a pack gap. Do not invent alternative-energy patches,
  visible zone UI, C/D access, assembly-wide `PatchAll`, or `OpenMod.Runtime`.
  Pull the skeleton, the trigger/usage rules, the effect
  building blocks, and the loc-key derivation rule. Do **not** guess API names — if
  the effect needs a Cmd not in the recipe, follow `grounding.md` — at runtime that
  means the rest of the pack (`reference/mechanics.md`, `build-constraints.md`,
  snapshots, `errors.md`), and if it's genuinely not there, report a pack gap. Never
  invent a Cmd name — that's the #1 way the repair loop burns its attempts.
- If a Card or Potion has a non-`none` **advanced target**, read
  `reference/advanced-targeting.md` before authoring either model. Emit one stable
  Mod-local target registration, use only its supported consumer/mode matrix, and stop
  authoring for `potion + many`; do not generate a lifecycle patch or restore a consumed
  Potion.
- If SPEC has a non-`none` **state** block, also read
  `reference/stateful-mechanics.md` before writing the hook. Implement its event,
  threshold/phase, lifetime, reset, persistence, UI meaning, and proof as one contract;
  never infer lifetime from the C# field that happens to be easiest.

## 1. Write the element class

**Relic** — add `<ModName>Code/Relics/<RelicName>.cs`. Use the recipe skeleton, then:

- Set `Rarity` from SPEC.
- Extend `ModRelicTemplate` and add exactly one `.Relic<TPool,TRelic>()` step to
  `MainFile.Content.cs`. The content-pack pool generic is the availability contract.
- Override the hook matching SPEC's trigger (recipe's "Trigger hooks" table). For
  combat-start: `AfterSideTurnStart` + `participants.Contains(Owner.Creature)` +
  `Owner.PlayerCombatState!.TurnNumber <= 1` guards.
- Fill **only** the effect block with the confirmed Cmds/RNG from the recipe. `await`
  every Cmd. Use `Rng`, never `System.Random`. Call `Flash()` when it visibly triggers.
- For stateful relics, follow `reference/stateful-mechanics.md`: run-lifetime progress is
  a `SavedAttachedState<SpecificRelic, int/bool>` whose name includes the Mod id and is
  never cleared at combat end; combat-local fixed/periodic turns read
  `PlayerCombatState.TurnNumber`. Any visible mutation calls
  `InvokeDisplayAmountChanged()` after updating the attached value.

**Potion** — add `<ModName>Code/Potions/<PotionName>.cs` and extend
`ModPotionTemplate`:

- Override the three abstract props: `Rarity`, `Usage` (`CombatOnly`/`AnyTime`),
  `TargetType` (self-buff = `AnyPlayer`, not `Self`; one enemy = `AnyEnemy`).
- For an advanced `mode: one` target, use the registered value and the single-Potion
  route from `reference/advanced-targeting.md`. `mode: many` is unsupported on the pinned
  profile and must stop authoring.
- Add exactly one `.Potion<SharedPotionPool,TPotion>()` step to `MainFile.Content.cs`.
  Use another pool only when SPEC makes the Potion character-specific; do not add a pool
  attribute or a per-Mod Potion base.
- Fill **only** the `OnUse` effect block with confirmed Cmds (`CreatureCmd.Damage/
  GainBlock/Heal`, `PowerCmd.Apply<T>`, `PlayerCmd.*`), using `ValueProp.Unpowered`
  for damage/block. `await` every Cmd; call `AssertValidForTargetedPotion(target)` first.
- Put an optional loose PNG in `PotionAssetProfile`; omit the override for the checked
  placeholder fallback.

**Card** — add `<ModName>Code/Cards/<CardName>.cs` and extend `ModCardTemplate`:

- Pass `cost, CardType, CardRarity, TargetType` to `base(...)`. A card that targets the
  player uses `TargetType.Self` (NOT `AnyPlayer` — that's potions).
- For an advanced target, pass the registered value from
  `reference/advanced-targeting.md`. A single Card uses `cardPlay.Target`; a multi Card
  gates zero candidates through `IsPlayable`, executes once with `null`, and resolves the
  live creature list with `GetTargets()` inside `OnPlay`.
- Add exactly one `.Card<TPool,TCard>()` step to `MainFile.Content.cs`; use
  `ColorlessCardPool` unless SPEC selects a character pool. Do not add a pool attribute.
- Declare static scaling numbers in `CanonicalVars`
  (`DamageVar`/`BlockVar`/`PowerVar<T>`), never literals; bump them in `OnUpgrade()`.
  For a SPEC calculated value, instead follow `reference/card-computed-values.md`: emit
  one pure bounded helper, select the matching computed variable role, account for upgrade
  preview and play-transition timing, and execute through the matching `Compute*Value`
  extension. `PreviewValue` remains display-only and `BaseValue` is not a computed result.
- Fill **only** the `OnPlay` effect block with the recipe's confirmed Cmds
  (`DamageCmd.Attack(...).FromCard(this).Targeting(...).Execute(...)`, `CreatureCmd.GainBlock`
  with the `cardPlay` overload, `PowerCmd.Apply<T>`). Null-check `cardPlay.Target` on a
  targeted card. `await` every Cmd. If a custom power is needed, author it first
  (`recipes/power.md`) and register it once through `.Power<T>()`.
- If SPEC selects Scry, read `reference/scry-helper.md`, emit its attributed
  `<ModName>Code/Helpers/OpenModScry.cs`, and await `OpenModScry.Execute` from `OnPlay`
  using the real `PlayerChoiceContext`, `Owner`, and a scaling `DynamicVar("Scry", X)`.
  Do not add BaseLib, a global hook/service, or a multiplayer fallback.

**Custom power** — add `<ModName>Code/Powers/<PowerName>.cs` and extend
`ModPowerTemplate`:

- Add exactly one `.Power<TPower>()` step to `MainFile.Content.cs`; do not rely on
  reflection discovery or add a pool attribute.
- Declare `Type`, `StackType`, and the SPEC amount domain. Clamp caller-owned changes and
  use `PowerCmd.ModifyAmount` to consume an existing nonnegative Counter.
- Emit `.title`, `.description`, and `.smartDescription` under the exact normalized public
  entry. Use `PowerAssetProfile` only for checked icon paths.

**Custom keyword** — register it once with
`.CardKeywordOwnedByLocNamespace(...)`, keep `iconPath: null`, and attach the minted native
`CardKeyword` through `CanonicalKeywords` or the runtime add/remove helpers. The keyword
owns vocabulary and tooltip text only; implement its named behavior in the host.

**Card enchantment** — extend `ModEnchantmentTemplate`, register it once through
`.Enchantment<T>()`, and attach it with `CardCmd.Enchant<T>`. Keep amount, host restriction,
and `OnPlay` behavior explicit. A custom icon uses the checked 64x64
`EnchantmentAssetProfile`; placeholder mode omits it.

**Custom orb** - add `<ModName>Code/Orbs/<OrbName>.cs` from `recipes/orb.md` and extend
`ModOrbTemplate`:

- Add exactly one `.Orb<TOrb>()` step to `MainFile.Content.cs`. Implement channel,
  passive, and evoke as separate behavior contracts through a real Card/relic/power host.
- Generated art is one 100x100 icon shared by the smart tooltip and trigger flash. Use the
  checked `OrbAssetProfile` Frost fallback when it is absent.
- Override the protected `ChannelSfx` with the verified Frost event. The icon is not the
  persistent combat body; `ContentAssetProfiles.Orb("frost_orb")` retains the Frost Spine
  scene until custom animation is separately proven.

**Enemy encounter** — author two classes as one slice (see `recipes/monster.md`), no
`[Pool]` on either:

- `<ModName>Code/Monsters/<Name>.cs` extends `ModMonsterTemplate`: set `MinInitialHp`/
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
  `TryCreateCreatureVisuals()` and call
  `RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>` only when present. Keep
  `MonsterAssetProfile` on `creature_visuals/fallback` for the missing-file branch, and set
  `HasDeathSfx => false`. Never put the PNG in the profile's scene path.
- If the monster needs a custom buff/debuff, author its power from `recipes/power.md` and
  include all three `powers.json` keys. A buff is not proven by attachment alone: SPEC and
  Tier 2 must observe its downstream effect on a later move.
- `<ModName>Code/Encounters/<Name>Encounter.cs` extends `ModEncounterTemplate`, overrides
  `RoomType => RoomType.Monster`, `IsValidForAct`, and `AllPossibleMonsters`
  (`ModelDb.Monster<T>()`), and `GenerateMonsters()` (`ModelDb.Monster<T>().ToMutable()` +
  slot, `null` slot ok). Add one `.Monster<T>()` plus one `.ActEncounter<TAct,T>()` or
  `.GlobalEncounter<T>()` to `RegisterContent()`; do not add a second registration path.

**Event / World Node** — create `<ModName>Code/Events/` and add `<Name>.cs` from
`recipes/event.md`:

- Extend `ModEventTemplate`; no `[Pool]`, constructor/manual registration, or second content
  pack. Use `.SharedEvent<T>()` for all-act placement or `.ActEvent<TAct,T>()` when scoped.
- For a forced follow-up, also author the one unplayable Quest Card exactly from
  `reference/forced-followup-event.md`: Quest type/rarity, cost `-1`, no upgrades, and the
  two public hook overrides guarded by the exact act. The target Event returns false from
  `IsAllowed`; do not place it in the ordinary Event pool. The source grant rejects a
  duplicate, and the named target option completes/removes all matching tokens.
- Ship flat `events.json` keys for the normalized Event entry, `INITIAL`, every explicit
  option key, and every result page. Use `InitialOptionKey`/`ModOptionKey`; callback method
  names do not mint localization keys.
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
- Fill `EventAssetProfile.InitialPortraitPath` with the recipe's existence check: use the generated
  `images/events/<event-slug>.png` when present, otherwise the verified vanilla
  `this_or_that.png` fallback, and filter the missing convention-derived path from
  `GetAssetPaths`. For every explicitly requested page portrait, check
  `images/events/<event-slug>_<page-key-lower>.png` and call `NEventRoom.SetPortrait`
  immediately before the page transition; when absent, retain the current portrait. Clean
  owned portrait child nodes before a switch.
- When SPEC selects `portrait_halo`, emit the exact bounded helper from
  `reference/event-vfx.md`, attach page profiles through `OnRoomEnter`/the portrait host,
  honor Instant/Fast mode, and explicitly `QueueFreeSafely` every owned named root before
  page, portrait, combat, or finish transitions. Do not promote RitsuLib's arbitrary custom
  VFX/layout routes. Custom phobia
  art, arbitrary VFX, custom layouts, and Ancient background assets remain unsupported.
- When SPEC selects vanilla Event text effects, apply only the exact bounded tags from
  `reference/event-text-effects.md` around the named phrases in `events.json` page/option
  descriptions. Keep titles plain; emit no helper node or cleanup code.
- When an enabled option selects typed Hover Tips, pass the exact grounded
  `HoverTipFactory` values through `EventOption`; do not emit a locked-option workaround. For
  relic-backed presentation, use `CreateModRelicOption<T>` for native title/description/metadata and
  keep semantic acquisition in a separate awaited `RelicCmd.Obtain<T>`. Preserve the
  normal-layout relic image as a presentation gap rather than generating an Ancient Event.
- When a choice pays HP or Max HP, apply `ThatDoesDamage` or `ThatDecreasesMaxHp` to the
  generated option using the exact decimal cost used by its Cmd. The helper is warning-only,
  and its exact-cost boundary is inclusive; never substitute differently rounded values or
  warning-colored text.
- When a choice acquires a Card, await one `CardPileCmd.Add` and pass that exact successful
  result to `CardCmd.PreviewCardPileAdd`; when it acquires a relic, emit exactly one awaited
  `RelicCmd.Obtain<T>`. Do not create duplicate models or custom preview holders.
- When SPEC selects `weak_short`, call `NGame.Instance?.ScreenShake(ShakeStrength.Weak,
  ShakeDuration.Short)` once after the named successful consequence and before its page
  transition. Never read or replace the player's multiplier.
- When SPEC selects `trial_noble`, emit the exact preloaded scene/portrait-host helper from
  `reference/event-native-presentation.md`, keep its vanilla `(292,68)` placement and
  inherited process mode, and `QueueFreeSafely` the owned named root before transitions.

**Character Foundation** - use the pinned scaffold and `recipes/character.md`:

- Fill `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` with every required public
  abstract member. Extend the three public `TypeList*PoolModel` bases.
- Register the Character, exact Basic starters, Starter relic, every concrete pool member,
  and every supporting Power once through one content pack. Do not instantiate the
  character, add pool attributes, or add a second registration path.
- If Shop/static merchant is selected, author enough unlocked non-Basic cards to provide
  at least two Attacks, two Skills, and one Power after filters; the native merchant fills
  those exact slots and otherwise throws before its UI appears.
- Add all 14 normalized `characters.json` values and a complete repeating Architect
  dialogue. When SPEC selects other Ancient targets or richer Architect groups, lower the
  semantic blocks through `reference/ancient-dialogue.md`; do not author an injection patch.
- Keep `CharacterAssetProfile` partial fallback semantics; selected Character static
  profiles fill only the matching fields after headed proof. When combat cues are selected,
  read `reference/character-combat-cues.md` and emit only its private combat-owned
  Idle/Attack/Hit/Dead state machine; never fill profile-global `VisualCues`. A
  Foundation-only SPEC emits no patch infrastructure. A resource SPEC
  registers one `SecondaryResourceDefinition`, uses `SecondaryResourceCmd` for amount and
  all-or-nothing payment, and mounts the fixed control through public `RegisterCombatUi`.
  An ordered-buffer SPEC uses `AttachedState<PlayerCombatState,TState>`, native source-card
  result piles, visible state text, and one configured output card. Never emit a retained-
  card `CustomPile` without a separately grounded UI lifecycle. Keep proof-only observers
  and assertions out of generated gameplay.

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

The selected scaffold must emit the framework diagnostic and exact **load** marker, or
tier-1 verify silently finds nothing. Use the shared envelope from
`semantic-contract.md`:

```csharp
Logger.Info("[OPENMOD-FRAMEWORK] phase=load mod=<mod-id> framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1 adapter=<surface>/sts2-content-semantic-v1 status=resolved");
Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");
```

The adapter must derive these values from the selected compat profile. Do not hardcode
a beta-facing fallback or emit `status=resolved` before the host/compat check succeeds.

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
   **advanced target** → keep the same real Card/Potion driver, then use
   `reference/advanced-targeting.md` to assert exact affected creature IDs, payment or
   Potion retention on cancellation, normal Card result pile, zero/one/multiple legal
   candidates, and queued target invalidation. Headed mouse/controller/reticle checks stay
   separate from the structured state proof.
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
   For native acquisition, `weak_short`, or `trial_noble`, use the combined headed proof
   from `reference/event-native-presentation.md`: exact Card/relic deltas, real preview and
   relic-inventory consumers, preference-aware shake movement/return, settled Event text,
   exact built-in scene host/position/process mode, and complete preview/VFX cleanup.
   For a bounded forced follow-up, use that reference's variant instead of direct canonical
   entry: prove no-token and wrong-act pass-through, force both hooks in the target act,
   enter one real Unknown MapPoint, click the target option, and prove token consumption
   plus restored hook outputs in the same headed run.
   **character** → the **`RunStart` + `CombatPlayer`** variant: locate the real custom
   character button by normalized icon resource path, click it and Confirm, wait for
   `NRun.GlobalUi`, assert runtime HP/pools/starter multisets, enter combat, then assert
   designed `MaxEnergy` and the starter mechanic's independent state delta. When selected,
   also enter real RestSite/Shop hosts and assert background/rest/merchant/full-energy
   resources through `CharacterAssetProfile`. Never select the first unlocked vanilla
   character or require the historical static-merchant patch.
   **character resource** → use `reference/character-resource.md`: in combat 1 drive real
   assert the public `RegisterCombatUi` attachment and `SecondaryResourceCmd` amount, then
   drive real gain and spender cards, affordable/unaffordable cases, successful/rejected
   payoff, floor, and live counter refresh. Assert the 220x32 control at offset 160 is
   disjoint from native Energy, then enter combat 2 and assert distinct zero state plus
   reset counter. Finish with `resource UI complete ... observed=all`.
   **ordered semantic buffer/dynamic output** → use `reference/ordered-card-buffer.md`: drive
   real source cards through their native result piles, assert attached-state order/capacity/
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
   run-lifetime `SavedAttachedState` additionally round-trips through
   `SavedProperties.From`/`Fill`; a run cadence must enter a second combat rather than
   mutating the attached value directly to simulate carry-over.
   A **Scry card** selects the focused `CombatPlayer` variant in
   `reference/scry-helper.md`: cover zero/empty/short with an automated selector, then
   play the real Card and prove the visible `NSimpleCardSelectScreen`, pending play task,
   selected/unselected order, normal source result pile, discard history, and one known
   `AfterCardDiscarded` effect. Keep the whole matrix in one headed run and retain the
   singleplayer assertion.
   A **calculated-value Card** uses the focused matrix in
   `reference/card-computed-values.md`: cover Damage/Block modifiers, zero and changing
   Energy/Star icon counts, raw versus amount-given typed Power, base/upgrade display, and
   the real hand-Card tooltip. Structured post-state proves behavior; headed observation
   separately proves text, icon reflow, and tooltip presentation.
3. In every driver, snapshot concrete state, drive the real source, assert the SPEC's exact
   post-state, then call the shared `StateProof(...)`. Its structured
   `[T2MOD-SELFTEST] <ModName> state proof:` line must include the selected framework,
   framework version, host, compat target, expected value, and observed value. A broad
   `played/fired/used` marker never qualifies.
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

For a **character**, write the 14 normalized flat keys to `characters.json` and the
complete `THE_ARCHITECT.talk.<CHAR_ID>` dialogue to `ancients.json`, as listed in
`recipes/character.md`. Lower every selected semantic Ancient group through
`reference/ancient-dialogue.md`: explicit zero-based `-visit`, one consistent repeat mode,
one speaker per line, and `.next` only on non-terminal lines. Generated Mods rely on
RitsuLib's registered population patch and emit no Harmony/reflection injection. For an
**event**, write the normalized title/page/option/result keys
to `events.json`; `InitialOptionKey` and `ModOptionKey` must match those explicit segments.

For the JSON-backed types, add entries to `<ModName>/localization/eng/<table>.json` — **`relics.json`** for a
relic, **`potions.json`** for a potion, **`cards.json`** for a card, **`powers.json`**
for a custom power, **`monsters.json`** + **`encounters.json`** for an enemy encounter,
**`events.json`** for an Event, and **`characters.json`** + **`ancients.json`** for a
Character.
**Keys are FLAT and prefixed** (recipe's loc-key rule + errors.md "raw-key title"):

```json
{
  "<MOD>_<CATEGORY>_<TYPE>.title": "<title from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.description": "<hover text from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.flavor": "<relic flavor - relics only>"
}
```

Relics take `.title/.description/.flavor`; potions take `.title/.description` (plus
`.selectionScreenPrompt` only if the effect prompts a choice — no `.flavor`); cards take
`.title/.description` (plus `.selectionScreenPrompt` if it prompts a choice — no
`.flavor`, no separate upgrade key). A **card description uses SmartFormat placeholders**
for scaling numbers — `"Deal {Damage:diff()} damage."` not `"Deal 6 damage."` — so the
upgraded value renders automatically (`reference/mechanics.md` §2). A **power** takes
`.title/.description` with `{Amount}` for the stack count. An **enemy encounter** takes
two tables: `monsters.json` with just `<MOD>_MONSTER_<TYPE>.name`, and `encounters.json`
with `<MOD>_ENCOUNTER_<TYPE>.title` + `.loss`. Use the exact normalized public entries
produced by the RitsuLib adapter. Not nested JSON — a flat `Dictionary<string,string>`.
When a calculated Card value declares a tooltip, also add its resolved `.title` and
`.description` keys to `localization/eng/static_hover_tips.json`; omit the icon argument
for the native null-icon fallback.

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
`null` from `TryCreateCreatureVisuals()` when absent, so the explicit
`MonsterAssetProfile` fallback scene loads without a missing-resource error. Skip to §5.
For a **character**, leave optional `CharacterAssetProfile` rows unset so RitsuLib resolves
the placeholder/native fallback. The combat override returns `null` when its checked PNG
is absent, so RitsuLib resumes that resolved profile fallback without a missing-resource
load. Placeholder mode emits no Character asset or combat cue set. The static combat body
remains the cue fallback; Cast, Spine, and unpromoted consumers are not supported.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

Supported sprite specs (see `sts2-api` → `reference/art-contract.md` and
`reference/character-presentation.md` and `reference/character-combat-cues.md` for the full
contracts). Character generation covers
nine promoted static profiles and one optional bounded cue bundle; locked selection and
map marker remain explicit gaps.
- **`--spec card`** — the one portrait a normal card loads, **1000×760 landscape**, full-
  bleed (chroma OFF), written to `card_portraits/big/<slug>.png`. **Live-verified in-game.**
  The 606×852 "full art" size is **Ancient-rarity only and out of scope — we never make it**.
- **`--spec relic` / `--spec power`** — a **256×256** cut-out icon, `fit: contain`, magenta
  chroma-key ON (so the prompt must ask for a solid flat `#FF00FF` background — see the
  contract). **Live-verified in-game.** A relic writes the main and big icons plus
  `relics/<slug>_outline.png`; a power writes only its main and big icons. The outline is
  an opaque-white silhouette expanded by `round(3% * 256) = 8` pixels from the final main
  icon alpha; main normalization reserves the same 8-pixel inset so the expansion cannot
  be clipped by the fixed canvas. It is deterministic and spends no additional acquisition call. A missing
  outline retains the adapter's checked fallback. **power** has no outline.
  **Prereq:** the relic/power subclass must extend `ModRelicTemplate` / `ModPowerTemplate`
  and expose the checked `RelicAssetProfile` / `PowerAssetProfile`. Direct game-model
  subclasses bypass the adapter's asset fallback (see the surface recipes).
- **`--spec potion`** — a **256×256** cut-out icon, `fit: contain`, magenta chroma-key ON
  (prompt asks for a solid flat `#FF00FF` background), a loose PNG like relic/power — **not**
  a `.tres` atlas. **Live-verified in-game.** Writes **ONE file**, `potions/<slug>.png` (the
  bar icon, hover tooltip, and use VFX all reuse that single texture — no `big/`). Art
  direction: draw the bottle **tilted ~45° leaning right** (STS2's potion display angle; see
  `art-contract.md`). **Prereq:** the potion subclass must extend `ModPotionTemplate` and
  expose the checked `PotionAssetProfile`; omit that override in placeholder mode.
- **`--spec enchantment`** — one **64×64** cut-out icon, `fit: contain`, magenta
  chroma-key ON, written to `enchantments/<slug>.png`. **Live-verified in the real hand-card
  tab and its hover tooltip.** Both consumers reuse the same `EnchantmentModel.Icon`; there
  is no `big/` variant. The subclass must use the recipe's checked
  `EnchantmentAssetProfile`; omit it so placeholder mode retains the fallback.
- **`--spec orb`** - one **100x100** cut-out icon, `fit: contain`, magenta chroma-key ON,
  written to `orbs/<slug>.png`. **Live-verified in the real smart tooltip and trigger
  flash.** This does not generate the persistent combat Spine scene; retain the recipe's
  Frost scene and channel-SFX fallbacks.
- **`--spec monster`** - one **360x360** transparent static body, `fit: contain`, magenta
  chroma-key ON, written to `monsters/<slug>.png`. **Live-verified in both the real combat
  `NCreature` and default bestiary layout.** The concrete monster must use the recipe's
  existence-checked `TryCreateCreatureVisuals()` factory and keep `MonsterAssetProfile`
  on the built-in scene fallback. This does not add Spine, move animation, or a phobia
  variant.
- **`--spec event`** — one opaque **3440×1613** normal/default-layout portrait slot per
  invocation, `fit: cover`, chroma-key OFF, written to `events/<slot-slug>.png`.
  **Live-verified in the real MapNode host for the initial and a later page.** Generate the
  initial slot plus only the later-page slots explicitly listed in SPEC. The event class
  must retain the checked initial fallback and keep the current portrait when optional
  page art is absent. This does not generate a phobia variant, custom layout, or Ancient
  background scene. The optional code-native `portrait_halo` is authored from
  `reference/event-vfx.md` and has no `gen_sprite.py` invocation.
- **`--spec character_select` / `character_background` / `character_icon` /
  `character_combat` / `character_rest` / `character_merchant` / `character_energy` /
  `character_energy_large` / `character_energy_text`** — respectively opaque **132x195** and **1920x1200** assets,
  transparent **88x88** and three **512x512** static bodies, five transparent **256x256**
  full-energy layers, one transparent **256x256** large Energy icon, and one transparent
  **24x24** text Energy icon. Never point both pool getters at the same file. The existing
  static profiles are live-proven in
  real selection, top-panel, CombatPlayer, RestSite, Shop, and energy consumers. Author the
  raw icon/background/rest/merchant/energy wrappers and the existence-checked combat resource
  factory from `character-presentation.md`; `build.py`
  packs them without Godot/MegaDot. Full energy uses five loose PNGs inside one raw scene;
  RitsuLib's Shop profile needs no historical `_Ready()` prefix. Keep checked profile/text
  fallbacks. Do not emit
  locked selection or map-marker art as supported.
- **`--spec character_cue_idle` / `character_cue_attack` / `character_cue_hit` /
  `character_cue_dead`** - four identity-referenced action sheets (2x2, 2x2, 2x2, 2x3)
  normalized to 4/4/4/6 transparent 512x512 frames. Import each with the matching lowercase
  action slug. The first three sheets only stage under `art-sources/character-cues`; after
  all four exist, deterministic QC atomically replaces `images/charui/cues` and writes GIF,
  contact-sheet, and metadata review output. A failed or incomplete bundle leaves existing
  runtime cues unchanged. Runtime support is combat-only and all-or-nothing.

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
**Character art profiles.** When `SPEC.md` selects Character art, emit only the nine
selected static profiles and optional bounded cue bundle above. Selection and background
are opaque (`--chroma` off); icon,
combat/rest/merchant bodies, full-energy layers, and large/text Energy icons use `--chroma`.
Do not set `CharacterAssetProfile.Scenes.VisualsPath` to the combat PNG: the texture-only
factory has no per-Character footprint style. Instead, existence-check the PNG in
`TryCreateCreatureVisuals()` and call RitsuLib's public resource factory with the reviewed
`VisualNodeStyle` scale/position; return `null` when absent so the resolved profile fallback
continues normally. Emit minimal raw scenes for background/rest/merchant and the five-layer
energy counter. The icon wrapper layers `icon_outline.png` behind `icon.png`; set
`Ui.IconTexturePath`, `Ui.IconOutlineTexturePath`, and `Ui.IconPath` to the main PNG,
outline PNG, and wrapper scene respectively. Return `energy_large.png` from
`BigEnergyIconPath` and `energy_text.png` from `TextEnergyIconPath`, checking each resource
independently before returning it.
Locked/map consumers remain explicit gaps with inherited profile fallbacks.

The character prompt must describe one original subject in the STS2 painterly style-only
reference pool. Selection portraits keep the full source composition inside the reviewed
132x195 safe box; backgrounds use the exact 16:10 host composition, place the focal
character on the right, and reserve the calm left-center information-panel area at
1920x1200; top-panel icons are bold at 88x88; static combat/rest/
merchant bodies are centered on one baseline at 512x512; full energy requests five
complementary layers. The 256x256 large pool icon and 24x24 text icon share the SPEC's
palette/motif but are normalized separately for their own consumers. Combat cue sheets use
the same identity route and shared combat footprint. Derive the SPEC's neutral combat
anchor once, then repeat the fixed identity/geometry continuity lock from
`art-contract.md` verbatim in all four cue prompts. Adjacent cells are closely spaced
in-between poses with substantial silhouette overlap, not distant key poses; Attack/Hit
start near and recover toward Idle, while Dead falls through six small steps. Do not
request Cast, Spine, trails, transition shaders, remote hands, phobia art, audio, or a
custom Ancient layout. The Ancient name-banner/Architect line is a separate native headed
proof, not a normal Event rich-text shortcut.

**CharacterArtBundle routing.** Generate/import the required `character_select` asset
first. Its normalized `charui/select.png` is the sole identity bootstrap; do not create a
separate character sheet. For identity-sensitive `character_combat`, `character_rest`,
`character_merchant`, and all four `character_cue_*` assets, pass that selection portrait as
`--identity-reference` alongside up to three type-matched STS2 style references. For the
selection background, top-panel icon, five Energy layers, and large/text Energy icons,
derive a concise palette/motif brief from the user's description and the reviewed
selection portrait, but do not pass the portrait as an image reference. `character_icon`
also writes `charui/icon_outline.png` as an opaque-white silhouette expanded by
`round(3% * 88) = 3` pixels from final main alpha. This derived file and every Relic
outline use the same rule; normalization reserves the matching main-icon inset, and the
derivation never triggers an acquisition call. Keep all generation/import calls at one acquired image;
the existing explicit per-paid-call approval remains mandatory.

**Combat cue runtime.** Generate the helper and Character overrides exactly from
`reference/character-combat-cues.md`. Require all eighteen paths and sizes before building
the private `VisualCueSet`; use `Idle/00` plus the shared geometry for the initial visual;
pass the set directly to `ModAnimStateMachines.StandardCue` from
`SetupCustomCombatAnimationStateMachine`. Do not set `CharacterAssetProfile.VisualCues`,
because RitsuLib can reuse that fallback in merchant/rest hosts. On any missing/invalid
frame, mount no playback node and use `combat.png`, then the resolved profile fallback.

**Character-wide theme contract.** Emit one Character-local theme class and copy every
explicit value from SPEC into it: `NameColor`, `EnergyLabelOutlineColor`,
`DeckEntryCardColor`, `EnergyOutlineColor`, the card-frame target RGB/brightness, both
Energy-icon paths, and the shared icon palette/motif. The Character and card-pool models
must delegate to that class instead of repeating literals. Use RitsuLib's public
`MaterialUtils.CreateReplaceHueShaderMaterial` once and return the cached material from
`TypeListCardPoolModel.PoolFrameMaterial`; do not ship a custom shader or generate a card
frame image. The pool's missing-file fallback is per icon: one absent file must not disable
the other route. The self-test asserts all four colors, shader parameters, distinct paths,
exact 256x256/24x24 textures, and both real consumers before it emits the theme marker.

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
3. **Acquire through the SPEC's `art source`, then import** (`${GAME_TOOLS_DIR}` resolves
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
   `${STS2_API_SKILL_DIR}/reference/art-samples/<spec>/`, make them visible using the
   runtime's normal local-image viewing mechanism, and label them STYLE REFERENCE ONLY. If reference inputs
   are unavailable, use the fixed text style descriptor alone.

   Inspect the generated image, then use the actual local file path reported by the host
   (Codex normally saves built-in results below `$CODEX_HOME/generated_images/`; do not
   assume that path for other runtimes). The route is unavailable if it produces no local
   image file. Pass that file through the existing normalizer:
   ```
   python ${GAME_TOOLS_DIR}/gen_sprite.py import \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --input "<native-output.png>" \
     --out "<work dir>/<ModName>/images" [--chroma]
   ```
   Add `--chroma` for `relic`, `power`, `potion`, `enchantment`, `orb`, `monster`, and
   selected Character icon/combat/rest/merchant/full-energy/large-energy/text-energy specs. Leave it
    off for Character selection/background. For full energy, invoke `character_energy`
    exactly once with slug `orb_layer_1`. Install the lead-supplied
    `reference/energy_template/layer_2.png` through `layer_5.png` with
    `character_art.py --install-energy-templates`; those four normalized project assets
    are fixed byte-for-byte and are what the mod references and packages. Never spend a
    generation call on layers 2-5.
   For the other Character slots use the bundle's stable slugs `select`, `background`,
   `icon`, `combat`, `rest`, `merchant`, `energy_large`, and `energy_text`; do not invent a second identity
   filename or a separate character sheet.

   **Vofy managed credits:** the user installs/authenticates Vofy themselves. Never run
   `vofy login`, inspect credential files, or put status/credit output in SPEC/MEMORY/logs.
   First run the read-only checks:
   ```
   python ${GAME_TOOLS_DIR}/acquire_sprite.py preflight --model <chosen-model>
   vofy models <chosen-model>
   ```
   Read the live model capabilities before choosing `--image`, `--aspect-ratio`, or
   `--resolution`; do not hardcode a model or current price. Use the bundled pool only when
   that model supports image-to-image references. Pass the root directory once;
   `acquire_sprite.py` selects the matching spec and randomly samples three files. After
   step 1a's confirmation, submit exactly one synchronous paid task:
   ```
   python ${GAME_TOOLS_DIR}/acquire_sprite.py create \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --model <chosen-model> \
     [--aspect-ratio <confirmed-ratio>] [--resolution <confirmed-resolution>] \
     [--reference ${STS2_API_SKILL_DIR}/reference/art-samples] \
     [--identity-reference <normalized-charui/select.png>] --yes
   ```
   `--yes` means the user approved this exact prompt/model/one-image spend. The tool reruns
   preflight, downloads into a unique empty directory, requires exactly one image, then
   calls `gen_sprite.py import` (including chroma for cut-out specs). It never parses Vofy
   stdout for a filename. On timeout or ambiguous output, inspect `vofy tasks --plain`;
   never auto-resubmit because the first task may already have spent credits.

   **BYO HTTP backend:** run the existing generator:
   ```
   python ${GAME_TOOLS_DIR}/gen_sprite.py generate \
     --spec <card|relic|power|potion|enchantment|orb|monster|event|character_select|character_background|character_icon|character_combat|character_rest|character_merchant|character_energy|character_energy_large|character_energy_text> --slug <slug> --prompt "<the prompt>" \
     --out <work dir>/<ModName>/images --config <path to art-backend.json> \
     --reference ${STS2_API_SKILL_DIR}/reference/art-samples
   ```
   `--reference` passes the shipped STS2 style samples (Layer 2 few-shot) — keep it on, and
   point it at the **root** `art-samples` dir (as shown). The tool auto-picks the matching
   established family or `character_select`/`character_background`/`character_icon`/
   `character_combat`/`character_rest` reference subdir and randomly samples three distinct files; families
   are never mixed. Backends
   that accept reference images (gpt-image edits or Gemini/nano-banana) imitate the
   game style far better, and plain text-to-image backends just ignore it.
   Add `--identity-reference <normalized-charui/select.png>` only for
   `character_combat`, `character_rest`, and `character_merchant`; omit it for
   `character_background`, `character_icon`, `character_energy`, `character_energy_large`, and
   `character_energy_text`.
   The tool POSTs to the user's backend, then chroma-keys (per spec — OFF for a full-bleed
   `card`/`event`/Character selection-background, ON for the cut-out icon/body/energy specs) / fits /
   resizes to the exact contract size and writes every required path: one
   card/potion/enchantment/orb/monster/event/Character main asset, two power files, or a
   relic's main/big/derived-outline triplet. `character_icon` similarly adds its derived
   outline beside the main PNG. Pass `--identity-reference` only for
   identity-sensitive Character body assets; palette-driven Character background/icon/
   Energy requests must omit it.
   **Local image:** use `gen_sprite.py import --input <file> ...`; for a magenta-backed
   relic/power/potion/enchantment/orb/monster or Character cut-out source add `--chroma`.
   After all required Character slots are normalized, validate and review them outside the
   runtime asset directory:
   ```
   python ${GAME_TOOLS_DIR}/character_art.py \
     --images-root <work dir>/<ModName>/images \
     --install-energy-templates \
     --out-dir <work dir>/art-review
   ```
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
