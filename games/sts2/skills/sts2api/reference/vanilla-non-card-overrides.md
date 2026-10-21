# Existing vanilla non-Card data and behavior overrides

Use this reference after `vanilla-overrides.md` resolves an exact vanilla target. It covers existing Relic, Potion, Power,
Orb, Enchantment, Affliction, Monster, Encounter, and ordinary Event data or behavior
while preserving the original model type, `ModelId`, save identity, ownership, assets, and
availability.

The checked catalog lists route family `non-card-data-behavior` as authorable. Its assembly identity
is the one in `vanilla-overrides.md`; the catalog contains 1624 models and 4165 reviewed
Adapter fingerprints. Of those Adapters, 4141 ground target-specific non-Card methods and
four ground shared stream/flow boundaries. Every hook, data, and body operation is
`multiplayer: singleplayer`.
A prompt selects a
semantic route and exact model only. It never supplies a method name, patch body, private
field, reflection expression, Publicizer request, or IL.

## Promoted matrix

| Family | Route | Class/mode | Supported targets |
|---|---|---|---|
| rules text | `relic.description.localization`, `potion.description.localization` | public `replace` | Relic, Potion |
| vanilla variable values | `relic.vars.base` | public `adjust` | Relic |
| owner hooks | `behavior.<category>.owner-hooks` | public `compose`; fixed Adapter `replace` | Relic, Potion, Power, Orb, Enchantment, Affliction, Monster |
| intrinsic data | sixteen `data.*` routes below | fixed Adapter `adjust` | Relic, Potion, Power, Enchantment, Affliction, Monster, Encounter |
| Relic body | `behavior.relic.lifecycle` | fixed Adapter `replace` | complete obtain/remove lifecycle |
| Potion body | `behavior.potion.use` | fixed Adapter `replace` | complete use body |
| Power body | `behavior.power.lifecycle` | fixed Adapter `replace` | complete before/apply/remove lifecycle |
| Orb body | `behavior.orb.lifecycle` | fixed Adapter `replace` | complete passive/evoke/turn-trigger lifecycle |
| Enchantment body | `behavior.enchantment.on-play` | fixed Adapter `replace` | complete `OnPlay` body |
| Affliction body | `behavior.affliction.lifecycle` | fixed Adapter `replace` | complete apply/remove suppression plus async `OnPlay` body |
| Monster body | `behavior.monster.moves` | fixed Adapter `replace` | complete move state machine |
| Encounter body | `behavior.encounter.monsters` | fixed Adapter `replace` | actual and all-possible monster rosters |
| ordinary Event body | `behavior.event.options` | fixed Adapter `replace` | complete initial options and Mod-owned pages |

Visuals, availability, and existing-Ancient options each remain their own separate
operations, owned by their own references. Ordinary Event replacement here rejects every `content_kind:
ancient` target.

## Keep the text true, and nothing else changed

The rule from `vanilla-card-overrides.md` § Pick routes applies to every model here: a
number or behavior change leaves the name, rarity, art, and every unnamed surface vanilla,
and never adds a name marker. When the vanilla description would no longer describe the
model, the same plan carries its text operation:

- a changed number the description already shows: `relic.vars.base` alone;
- changed Relic or Potion behavior: the behavior route plus
  `relic.description.localization` or `potion.description.localization`;
- changed Power, Orb, Enchantment, Affliction, or Monster behavior: no text route is
  promoted. Their in-combat text comes from variant keys (`smartDescription`,
  `remoteDescription`, intents) that the catalog does not record. Tell the user the vanilla
  text stays, and pause before SPEC until they accept that or drop the change.

## Rules text and variable values

`relic.description.localization` and `potion.description.localization` replace the vanilla
`<ENTRY>.description` exactly like `card.description.localization`: `mode: replace`, surface
`relic.description_text` or `potion.description_text`, baseline `category`, `type`, and
`description_localization` with its key and vanilla `eng`/`zhs` text, and semantics
`{"localization": {"table": "relics" | "potions", "key": "<ENTRY>.description"}}`. The Mod
ships that key in `<ModName>/localization/<lang>/relics.json` or `potions.json` for `eng`,
`zhs`, and every other shipped language. The text may reference the model's own
`DynamicVars` and the variables the vanilla text already uses; Build rejects any other.
The replacement is global, unshipped languages keep the vanilla text, and a later-loaded Mod
replacing the same key wins.

`relic.vars.base` sets one vanilla Relic variable: `mode: adjust`, surface
`relic.dynamic_vars`, baseline `properties.dynamic_vars`, and semantics
`{"variable": "<Name>", "base_value": <number>}`. Assign it on the canonical Relic in a
`ModelRegistryInitializedEvent` handler, as for Cards; every obtained Relic clones it:

```csharp
RitsuLibFramework.SubscribeLifecycle<ModelRegistryInitializedEvent>(_ =>
    ModelDb.Relic<Akabeko>().DynamicVars["VigorPower"].BaseValue = 10m);
```

Observed on the pinned host: Akabeko `VigorPower` 10 reached the obtained Relic, the combat
start Vigor amount, and its `eng`/`zhs` description, and a replaced Block Potion
description resolved in both languages. Potion variables are not promoted: a
mutable Potion does not clone its canonical `DynamicVars`, and the catalog records none.

## Public owner-hook composition

RitsuLib exposes these typed bases, all derived from
`OwnerHookCapability<TModel>`:

| Target | Capability base |
|---|---|
| Relic | `RelicCapability` |
| Potion | `PotionCapability` |
| Power | `PowerCapability` |
| Orb | `OrbCapability` |
| Enchantment | `EnchantmentCapability` |
| Affliction | `AfflictionCapability` |
| Monster | `MonsterCapability` |

The seven route ids are exact:

```text
behavior.relic.owner-hooks
behavior.potion.owner-hooks
behavior.power.owner-hooks
behavior.orb.owner-hooks
behavior.enchantment.owner-hooks
behavior.affliction.owner-hooks
behavior.monster.owner-hooks
```

Register each generated capability and attach it to the exact vanilla type through default
capabilities. Use one capability per semantic rule, or one per group with the same order,
because `OwnerHookOrder` is the ordering unit. Negative orders run before the vanilla
owner; zero and positive orders run after it. Registration is the same public lifecycle the Card routes use:

```csharp
var content = RitsuLibFramework.GetContentRegistry(MainFile.ModId);
content.RegisterModelCapability<AkabekoTurnRule>();
content.ConfigureDefaultModelCapabilities<Akabeko>(
    "override-relic-akabeko-turn-rule",
    (_, capabilities) => capabilities.Add<AkabekoTurnRule>());
```

Do not register or replace the vanilla model. The capability owns only the selected rule.
It overrides the exact pinned `AbstractModel` method signature, guards the event in game
terms, runs the selected effect or returns the selected scalar/decision, and leaves every
other method inherited. For Orb only, the four typed RitsuLib callbacks may also be used:

```text
owner_orb_passive_triggered
owner_orb_evoked
owner_orb_before_turn_end_triggered
owner_orb_after_turn_start_triggered
```

They run after the owning Orb method and carry the typed passive/evoke/turn context. They
are not substitutes for the ordinary global Orb hook methods in the list below.

### Hook rule manifest

Every compose operation uses surface `<category>.owner_hooks`, a public route with no
fingerprint, and one rule:

```json
{
  "mode": "compose",
  "surface": "relic.owner_hooks",
  "route": {
    "class": "public",
    "id": "behavior.relic.owner-hooks",
    "fingerprint": null
  },
  "semantics": {
    "multiplayer": "singleplayer",
    "rule": {
      "kind": "effect",
      "hook": "after_side_turn_start",
      "order": -10,
      "scope": "owner_side",
      "when": {"kind": "always", "parameters": {}},
      "effects": [
        {
          "kind": "block",
          "amount": {"source": "literal", "value": 3},
          "target": "owner"
        }
      ]
    }
  }
}
```

`kind` is `effect`, `numeric`, or `decision`. Numeric rules replace `effects` with
`adjustment: delta | multiply | min | max | set` and a fixed numeric `value`. Decision
rules replace it with boolean `decision`. `scope` is `any`, `owner`, or `owner_side`; map it
to the selected hook's real subjects and the concrete owning Player/Creature/Card. A hook
without the requested subject is not silently mapped to another hook.

`when` supports nested `all`/`any`/`not`, `always`, `playable`, `upgraded`, `in_pile`,
`player_state`, `has_power`, `has_tag`, `has_keyword`, and the checked
`caused_by_ethereal`/`from_hand_draw` event flags. Use a condition only when the selected
hook signature carries or can deterministically resolve its subject. Missing context is an
authoring error, not `false` by accident.

Effects are the fixed command vocabulary: attack, block, heal, lose HP, apply a known
Power, draw, gain Energy/Gold/Stars, or generate a known Card into Draw/Hand/Discard/
Exhaust. Targets are `owner`, `all_enemies`, `random_enemy`, or a real creature carried by
the hook as `event_target`, as permitted by that command. Amounts are nonnegative literals
or a cataloged owner DynamicVar. Undeclared capability variables are not promoted.
Await every Cmd in an asynchronous callback and preserve the selected rule order.

### Complete owner-hook replacement

`mode: replace` means the vanilla owner is removed from its run/combat hook streams and the
generated capabilities become the complete selected rule set. It requires `complete: true`
and a `rules` list. Relic and Potion require both shared dependencies:

```text
non-card.owner-hook-stream.run
non-card.owner-hook-stream.combat
```

Power, Orb, Enchantment, Affliction, and Monster require the combat dependency. Install
one fixed postfix on each required `IterateHookListeners` target after RitsuLib's
`framework-core` capability expansion. Filter only a selected original owner model by
exact `ModelId`; retain every `IModelCapability`, including the generated rules, and pass
all unrelated owners unchanged. Never patch individual `Hook.*` dispatchers or derive a
stream target from the prompt.

A same-target replacement conflicts with every compose/replacement on that owner-hook
surface in the generated Mod. Multiple compose rules may coexist in manifest order.

### Complete public hook lists

The effect allowlist is all 100 asynchronous public `AbstractModel` callbacks in pinned
`0.107.1`:

```text
after_act_entered, after_add_to_deck_prevented, after_attack,
after_auto_post_play_phase_entered, after_auto_pre_play_phase_entered,
after_auto_pre_play_phase_entered_early, after_auto_pre_play_phase_entered_late,
after_block_broken, after_block_cleared, after_block_gained,
after_card_changed_piles, after_card_changed_piles_late, after_card_discarded,
after_card_drawn, after_card_drawn_early, after_card_entered_combat,
after_card_exhausted, after_card_generated_for_combat, after_card_played,
after_card_played_late, after_combat_end, after_combat_victory,
after_combat_victory_early, after_creature_added_to_combat,
after_current_hp_changed, after_damage_given, after_damage_received,
after_damage_received_late, after_death, after_died_to_doom, after_energy_reset,
after_energy_reset_late, after_energy_spent, after_flush, after_forge,
after_gold_gained, after_hand_emptied, after_item_purchased, after_map_generated,
after_modifying_block_amount, after_modifying_card_play_count,
after_modifying_card_play_result_pile_or_position,
after_modifying_card_reward_options, after_modifying_damage_amount,
after_modifying_energy_gain, after_modifying_gold_gained,
after_modifying_hand_draw, after_modifying_hp_lost_after_osty,
after_modifying_hp_lost_before_osty, after_modifying_orb_passive_trigger_count,
after_modifying_power_amount_given, after_modifying_power_amount_received,
after_modifying_rewards, after_orb_channeled, after_orb_evoked,
after_osty_revived, after_player_turn_start, after_player_turn_start_early,
after_player_turn_start_late, after_potion_discarded, after_potion_procured,
after_potion_used, after_power_amount_changed, after_preventing_block_clear,
after_preventing_death, after_preventing_draw, after_rest_site_heal,
after_rest_site_smith, after_reward_taken, after_room_entered, after_shuffle,
after_side_turn_end, after_side_turn_end_late, after_side_turn_start,
after_side_turn_start_late, after_stars_gained, after_stars_spent, after_summon,
after_taking_extra_turn, after_targeting_blocked_vfx, before_attack,
before_block_gained, before_card_auto_played, before_card_played,
before_card_removed, before_combat_start, before_combat_start_late,
before_damage_received, before_death, before_flush, before_flush_late,
before_hand_draw, before_hand_draw_late, before_potion_used,
before_power_amount_changed, before_room_entered, before_side_turn_end,
before_side_turn_end_early, before_side_turn_end_very_early,
before_side_turn_start
```

The scalar list is every public `int`/`decimal`/`float` modifier callback except model
identity comparison:

```text
modify_attack_hit_count, modify_block_additive, modify_block_multiplicative,
modify_card_play_count, modify_card_reward_upgrade_odds, modify_damage_additive,
modify_damage_cap, modify_damage_multiplicative, modify_energy_gain,
modify_gold_gained, modify_hand_draw, modify_hand_draw_late,
modify_hp_lost_after_osty, modify_hp_lost_after_osty_late,
modify_hp_lost_before_osty, modify_hp_lost_before_osty_late,
modify_max_energy, modify_merchant_price,
modify_odds_increase_for_unrolled_room_type,
modify_orb_passive_trigger_counts, modify_orb_value,
modify_power_amount_given_additive, modify_power_amount_given_multiplicative,
modify_rest_site_heal_amount, modify_summon_amount, modify_x_value
```

The decision list is every public `Should*` callback:

```text
should_add_to_deck, should_afflict, should_allow_ancient,
should_allow_free_travel, should_allow_hitting,
should_allow_merchant_card_removal, should_allow_selecting_more_card_rewards,
should_allow_targeting, should_clear_block,
should_creature_be_removed_from_combat_after_death, should_die,
should_die_late, should_disable_remaining_rest_site_options, should_draw,
should_ethereal_trigger, should_flush, should_force_potion_reward,
should_gain_stars, should_generate_treasure,
should_pay_excess_energy_cost_with_stars, should_play,
should_player_reset_energy, should_power_be_removed_on_death,
should_proceed_to_next_map_point, should_procure_potion,
should_refill_merchant_entry, should_stop_combat_from_ending,
should_take_extra_turn
```

Use the exact method signature from the scaffold-pinned local Compat assembly for the selected
semantic id. Do not infer overloads from another STS2 version.

## Intrinsic data routes

Every data operation uses `mode: adjust`, `surface` equal to its route id, a target-specific
Adapter fingerprint, the cataloged current property in `expected_baseline.properties`, and
`multiplayer: singleplayer`.

| Route | Values |
|---|---|
| `data.relic.rarity` | set `Ancient/Common/Event/None/Rare/Shop/Starter/Uncommon` |
| `data.potion.rarity` | set `Common/Event/None/Rare/Token/Uncommon` |
| `data.potion.target-type` | set `AllEnemies/AnyEnemy/AnyPlayer/Self/TargetedNoCreature` |
| `data.potion.usage` | set `AnyTime/Automatic/CombatOnly` |
| `data.power.allow-negative` | set boolean |
| `data.power.type` | set `Buff/Debuff` |
| `data.power.scales-in-multiplayer` | set boolean; still singleplayer |
| `data.power.stack-type` | set `Counter/None/Single` |
| `data.enchantment.stackable` | set boolean |
| `data.affliction.can-afflict-unplayable` | set boolean |
| `data.affliction.stackable` | set boolean |
| `data.monster.min-initial-hp` | set positive integer or integer delta |
| `data.monster.max-initial-hp` | set positive integer or integer delta |
| `data.monster.show-in-compendium` | set boolean |
| `data.encounter.room-type` | set `Boss/Elite/Monster` |
| `data.encounter.is-weak` | set boolean |

Patch only the cataloged getter. Consolidate selected rules by actual declaring method,
because many concrete types inherit one base implementation, then dispatch by exact
`__instance.Id`. A set assigns the selected value; an integer delta modifies the original
getter result. Pass every unselected model unchanged. Do not patch backing fields, mutate
canonical instances, or assume one Adapter id means one unique CLR method.

The validator checks the exact target-specific Adapter id:
`non-card.<lowercase-model-id-with-dashes>.<route-suffix>`. Its fingerprint is copied from
the catalog, never written from memory.

## Complete lifecycle and body replacement

Every route below uses `mode: replace`, `complete: true`, exact target type/category
baseline, and all target-specific dependencies named by the catalog.

| Route | Semantic body | Required target suffixes |
|---|---|---|
| `behavior.relic.lifecycle` | `after_obtained`, `after_removed` effect lists | `lifecycle.after-obtained`, `lifecycle.after-removed` |
| `behavior.potion.use` | `effects` | `lifecycle.use` |
| `behavior.power.lifecycle` | `before_applied`, `after_applied`, `after_removed` | matching three `lifecycle.*` suffixes |
| `behavior.orb.lifecycle` | `before_turn_end`, `after_turn_start`, `passive`, `evoke` | matching four `lifecycle.*` suffixes |
| `behavior.enchantment.on-play` | `effects` | `lifecycle.on-play` |
| `behavior.affliction.lifecycle` | empty `after_applied`, empty `before_removed`, async `on_play` | matching three `lifecycle.*` suffixes |
| `behavior.monster.moves` | complete state graph | `behavior.move-state-machine` |
| `behavior.encounter.monsters` | complete `(Monster, slot)` list | `behavior.monster-roster`, `behavior.all-possible-monsters` |
| `behavior.event.options` | condition, complete initial options, complete page graph | `behavior.initial-options` plus selected flow dependencies |

Install fixed patches once through `RitsuLibFramework.CreatePatcher` and fail Mod load when
`PatchAll()` fails. For Task-returning bodies, the prefix sets `__result` to one generated
async helper and suppresses the original exactly once. For value-returning bodies, set the
complete result. Dispatch by exact target `ModelId`; inherited methods are consolidated.
Do not run a Task fire-and-forget from a synchronous target.

Pinned Affliction `AfterApplied()` and `BeforeRemoved()` return `void`. A complete lifecycle replacement can suppress
their original bodies as part of a complete lifecycle replacement, but their generated
effect lists must remain empty. `OnPlay` is asynchronous and supports the full effect list.
This is a confirmed smallest lifecycle limitation, not a reason to narrow Affliction owner
hooks or its `OnPlay` replacement.

For Orb `Evoke`, return the deterministic affected creature list from the generated async
body. Preserve exact effect order and do not reuse the original Orb body after replacement.

### Monster and Encounter bodies

Monster replacement builds one `MonsterMoveStateMachine` from manifest states. A `move`
has one or more attack/defend/heal/multi-attack/buff/debuff/escape/sleep/stun/unknown
intents, ordered effects, and one next state. A `branch` has ordered predicate cases. IDs
are unique `UPPER_SNAKE`; every edge must resolve, the initial state must exist, and at
least one move is required. Use the checked move/intent/Cmd patterns in `recipes/monster.md`
and deterministic game RNG only.

Encounter replacement creates mutable instances of every declared known Monster and
retains each optional slot. Patch both `GenerateMonsters` and `AllPossibleMonsters`: the
former returns the actual mutable `(MonsterModel, string?)` roster, while the latter reports
the corresponding canonical possibilities for preload/info consumers. Keeping only one is
an invalid split roster. Duplicate model/slot pairs are rejected.

### Ordinary Event body

Ordinary Event replacement is complete initial options plus Mod-owned reachable pages. It
reuses the checked existing-Ancient fixed condition, cost, typed hover/relic presentation, effect,
selector, reward, and page vocabulary, but uses `<MOD_ID>_EVENT_*` keys and never an
Ancient target. The operation-level condition decides whether replacement is active; false
preserves the complete vanilla initial body.

Each option has visible/enabled conditions, one fixed Gold/HP/Max HP/no cost,
`disable_on_chosen: true`, `is_proceed: false`, ordered outcomes, and `stay`, `page`, or
`finish`. `page` requires the shared fingerprinted `SetEventState` dependency. `finish`
requires `SetEventFinished`; use the selected option description as the final description
and let the native method own cleanup. The complete graph must have no unreachable page
and at least one finish path.

Every option prefix requires `.title` and `.description`; every page description key is a
complete entry. Put all of them in every shipped
`<ModName>/localization/<lang>/events.json`, including required `eng` and `zhs`. Build preflight
rejects missing files, keys, or empty values. Event assets remain separate resource
operations and contain no behavior scripts. Option and page text follows the Event rows of
`reference/vanilla-text-style.md`, matching the vanilla Event it changes.

## Conflicts and boundaries

- One complete replacement conflicts with every same-target operation on that replacement
  surface. Data getter sets/deltas also use the normal same-surface conflict rules.
- Public owner-hook composition never grants an Encounter or Event owner-hook route; those
  model families do not enter the owner streams in pinned `0.107.1`.
- Replacement preserves normal wrappers outside the exact body: Potion payment/use wrapper,
  Power application command, Orb queue/trigger host, Card enchantment/affliction wrapper,
  combat creation, Event room lifecycle, save identity, and history remain native.
- Do not claim random/RNG rewrites, arbitrary Event transitions/layouts, audio, Monster body
  visuals, private state edits, multiplayer, or any route absent from the promoted tables.
- A missing focused compile or real-host proof is missing verification, not an unsupported
  public hook and not a pass.

A focused manifest/catalog/localization test and a representative compile establish the
manifest and the build, nothing more. Real-host lifecycle, intent/option presentation,
save/load, multiplayer, and cleanup are proved only by observing them in a real host.
