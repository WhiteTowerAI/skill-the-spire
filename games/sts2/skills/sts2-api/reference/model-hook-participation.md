# Reference: model hook participation for custom content

> Checked against the pinned STS2 `0.107.1` assembly and RitsuLib `0.5.4`. Every hook here is
> `public virtual` on `AbstractModel`, so a custom element overrides it directly — no Harmony,
> reflection, Publicizer, or IL. The authoritative per-hook data is
> `reference/catalogs/model-hooks-sts2-0.107.1.json`; this page states the rules, the catalog
> holds the values. Never hand-edit the catalog.

## What this route is for

A trigger makes your element *act*. A hook makes the host *ask your element for a value or a
decision* while resolving something else. "When my turn starts, gain 3 Block" is a trigger.
"While I am attached, damage my owner receives is multiplied by 2" is a hook: nothing fires,
the engine simply consults every listener while computing the number.

That distinction is why this route exists. A behavior of the second kind, written as prose in
an effect sequence, has historically been generated as an empty method — the pipeline recorded
the requirement, an operation passed, and the multiplier was never there. Declare it as hook
participation and the number, the guard, and the neutral case each become checkable.

## The catalog decides what your surface may declare

68 hooks are cataloged: 26 numeric, 28 `Should*` decisions, and 14 `TryModify*`. Which of them
a given element can receive is **not uniform**, and this is the one rule to get right before
writing anything.

`Hook` dispatches through two families of iterator, and each walks a different **listener set**.
The run-scope listener set is deck Cards, Enchantments, Relics, Potions, Modifiers, and Badges.
The combat listener set adds Powers, Orbs, Monsters, Afflictions, and pile Cards. So a hook
dispatched only at run scope **can never reach a Power**: the override compiles, ships, and never
fires. Offering it there would manufacture exactly the silent failure this route exists to
prevent.

Read `authorable_surfaces` for the hook and confirm your surface is in it. Do not infer
reachability from the hook's name or from a vanilla implementor you found elsewhere.

| Surface | Hooks it can receive | Shapes available |
|---|---|---|
| card, relic, potion | 66 | scalar 53, out-replacement 6, collection 7 |
| enchantment | 61 | scalar 48, out-replacement 6, collection 7 |
| power, orb, monster | 45 | scalar 40, out-replacement 4, collection 1 |

Two hooks are excluded from all counts above because a shipped route already owns them; see
§ Two hooks that belong to another route.

## Reaching your owner, which differs by surface

Every guard needs the element's own Creature, and the property that yields it is not the same:

| Surface | Own model property | The Creature to compare against |
|---|---|---|
| power | `Owner` is a `Creature` | `Owner` |
| relic, potion, orb, card | `Owner` is a `Player` | `Owner.Creature`, and `Owner.Osty` where an Osty can act |
| monster | `Creature` | `Creature` |

Vanilla `PenNib` compares against both `Owner.Creature` and `Owner.Osty`, because either may be
the dealer. A relic guard that checks only the main Creature silently stops working when the
player's Osty swings.

## Value shape: a guard, a value, and a neutral return

54 scalar-return hooks use this shape. The body is three parts, in this order:

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (target != Owner) return 1m;              // not my subject
    if (!props.IsPoweredAttack()) return 1m;      // not my damage type
    return DynamicVars["DamageIncrease"].BaseValue;
}
```

That is `VulnerablePower` almost verbatim, and it is the shape to copy. Three rules follow from
it, each of which a generated override gets wrong if it is not stated:

**1. The guard decides direction.** The hook carries both `target` and `dealer`, so the same
method is "damage I receive" or "damage I deal" depending only on which one you compare to your
owner. `VulnerablePower` guards `target != Owner` (incoming); `WeakPower` guards
`dealer != Owner` (outgoing). Getting this backwards produces a Power that reads correctly in
its rules text and does the opposite thing.

**2. The neutral return is not boilerplate.** Return the hook's `neutral_default` from the
catalog for every case outside your guard. It is what makes your element invisible to
unrelated interactions, and the engine also uses it to decide whether your element is listed
as a modifier of that number in the UI. An override that returns its modifier unconditionally
passes a single-value assertion while changing every damage event in the run.

**3. Damage type is a separate decision from direction.** `IsPoweredAttack()` is true only for
attack damage from a Card play or a Monster move. Poison-style HP loss (`Unblockable`) and
damage from relics, potions, and powers (`Unpowered`) are excluded. Both vanilla multipliers
guard on it. So "doubles incoming damage" needs the design to say *which* damage: attack
damage only, following Vulnerable, or literally everything including Poison ticks. SPEC records
that answer in the guard; it is not a detail to leave to the author.

**Composition order is fixed by the engine, not by your element.** For damage:
additive across all listeners, then multiplicative across all listeners, then the minimum cap,
then a floor at zero. So `+3` and `x2` on the same hit yield `(base + 3) * 2`. Never write a
combined adjustment assuming your element runs alone.

**The number in the rules text is the same number.** Declare it as a `DynamicVar` and read the
value back from `DynamicVars[...]` in the body, exactly as `VulnerablePower` reads
`DamageIncrease`. Substitution then puts the same value in the description, so the text cannot
drift from the behavior. A literal in the body plus a literal in the description is two facts
that will disagree after the first balance change.

A `Should*` decision hook is the same shape with a `bool`: guard first, then your decision, with
the catalog's neutral (usually `true`) everywhere else. A decision hook that returns `false`
outside its guard is how a generated Mod stops the player from drawing cards for the rest of the
run.

## Out-replacement shape: the same, plus a taken flag

6 `TryModify*` hooks return `bool` and carry the real value in an `out` parameter. The `bool`
means "I am replacing it" — so it is the guard's answer, and the `out` value is only meaningful
when it is `true`:

```csharp
public override bool TryModifyStarCost(CardModel card, decimal originalCost, out decimal modifiedCost)
{
    modifiedCost = originalCost;                  // assign on every path
    if (card.Owner != Owner) return false;        // not mine: declined
    modifiedCost = 0m;
    return true;
}
```

Assign the `out` parameter on every path, including the declined one. Return `false` rather than
returning `true` with an unchanged value: `true` claims a replacement, and a later listener or a
UI modifier list may treat your element as the source of a number it did not change.

## Collection shape: nothing is replaced

8 `TryModify*` hooks hand you a host-owned collection to mutate. The `bool` does **not** report a
replacement — for several of these the host discards it entirely, and where it is kept it only
records which models touched the list. So this shape declares *entries*, not a value:

```csharp
public override bool TryModifyRewards(Player player, List<Reward> rewards, AbstractRoom? room)
{
    if (player != Owner) return false;
    if (room == null || room.RoomType != RoomType.Elite) return false;
    rewards.Add(new RelicReward(player));
    return true;
}
```

That is `BlackStar`. The vocabulary is bounded: `Reward` has exactly six concrete subclasses
(`CardReward`, `SpecialCardReward`, `RelicReward`, `PotionReward`, `GoldReward`,
`CardRemovalReward`), and the other collections are `CardCreationResult`,
`CardRewardAlternative`, `CardKeyword`, and `RestSiteOption`.

**Preserve what you did not come for.** The one vanilla remover, `Midas`, doubles gold rewards by
building a replacement list, calling `rewards.Clear()`, and re-adding *everything* — the
transformed entries and the untouched ones. A generated editor that clears and adds only its own
entry deletes every other contributor's reward while passing an assertion that its own entry is
present. This is why the proof for this shape asserts unrelated entries survive.

Several editors can run on the same list, and a `Late` variant exists precisely so ordering is
expressible: the host runs every listener's base hook, then every listener's `Late` hook. Declare
which one you need and why.

## An Enchantment uses its own five hooks, never the general ones

`EnchantmentModel` declares five replacements, each documented in the pinned assembly as
"Enchantments MUST use this hook instead of" its `AbstractModel` counterpart, and each running
**before** all other modification hooks for that value:

| Instead of the general hook | An Enchantment overrides | Signature and neutral |
|---|---|---|
| `ModifyBlockAdditive` | `EnchantBlockAdditive` | `decimal(decimal originalBlock)`, returns `0m` |
| `ModifyBlockMultiplicative` | `EnchantBlockMultiplicative` | `decimal(decimal originalBlock)`, returns `1m` |
| `ModifyDamageAdditive` | `EnchantDamageAdditive` | `decimal(decimal originalDamage, ValueProp props)`, returns `0m` |
| `ModifyDamageMultiplicative` | `EnchantDamageMultiplicative` | `decimal(decimal originalDamage, ValueProp props)`, returns `1m` |
| `ModifyCardPlayCount` | `EnchantPlayCount` | `int(int originalPlayCount)`, returns `originalPlayCount` |

A generated Enchantment overriding the general hook is wrong on the pinned host. The catalog
removes `enchantment` from those five hooks' `authorable_surfaces` for that reason.

Two differences from the general shape: there is **no subject guard**, because the hook is scoped
to this enchantment's own card already — a `props` guard for damage type may still apply. And the
additive neutral is `0m` while the multiplicative neutral is `1m`, so a copied guard that returns
the wrong one is a silent `x0` or a `+1`.

Every other hook in the catalog remains available to an Enchantment at its normal `AbstractModel`
signature; only these five are redirected.

## Two hooks that belong to another route

`TryModifyRestSiteOptions` and `ShouldDisableRemainingRestSiteOptions` are exactly how the shipped
Relic-owned Rest Site option is contributed and how its stay/leave behavior works. Use
`reference/rest-site-options.md`. It carries four boundaries the bare hook does not — singleplayer
only, absent versus natively disabled, free or fixed Gold, and a fully preflightable outcome before
the first mutation.

Declaring either as raw hook participation is rejected. It would let a generated Mod bypass all
four while looking like a supported declaration.

## Verification this route owes

Two assertions per value declaration, and the second is the one that catches real bugs:

1. the modified value, driven through the real path (play the Card, take the hit, resolve the
   reward); and
2. **the neutral case outside the guard** — one event your guard is supposed to ignore, asserted
   unchanged. Without it, an unconditional modifier passes.

For a value that appears in rules text, also assert the rendered number equals the applied one.
For a collection edit, assert the resulting entries **and** that an unrelated entry placed in the
list beforehand is still there afterwards.

Reuse the nearest hosted scenario — `CombatPlayer` for damage, block, and card values,
`CombatEnemy` for a Monster's own hooks, `RunStart` for run-scope rewards and map decisions. A
model-only read proves registration, not participation: the hook must be driven by the engine.

## Capability ids this route provides

An `OP-###` that consumes one of these names it in `capability_ids` and cites this page as
its `supported_route`; `design_trace.py` rejects an id no route declares. Each id is the
hook's `semantic_id` in the catalog, and a test asserts this list equals the catalog's
authorable set, so a hook cannot be documented here without being reachable.

**Numeric modifiers** (26). The value the host is computing, adjusted. Neutral return per hook in the catalog.

<!-- openmod-capabilities:
modify_attack_hit_count modify_block_additive modify_block_multiplicative
modify_card_play_count modify_card_reward_upgrade_odds modify_damage_additive
modify_damage_cap modify_damage_multiplicative modify_energy_gain modify_gold_gained
modify_hand_draw modify_hand_draw_late modify_hp_lost_after_osty
modify_hp_lost_after_osty_late modify_hp_lost_before_osty modify_hp_lost_before_osty_late
modify_max_energy modify_merchant_price modify_odds_increase_for_unrolled_room_type
modify_orb_passive_trigger_counts modify_orb_value modify_power_amount_given_additive
modify_power_amount_given_multiplicative modify_rest_site_heal_amount modify_summon_amount
modify_x_value
-->

**Decisions** (27). A `bool` the host consults before allowing something. Neutral is usually `true`.

<!-- openmod-capabilities:
should_add_to_deck should_afflict should_allow_ancient should_allow_free_travel
should_allow_hitting should_allow_merchant_card_removal
should_allow_selecting_more_card_rewards should_allow_targeting should_clear_block
should_creature_be_removed_from_combat_after_death should_die should_die_late should_draw
should_ethereal_trigger should_flush should_force_potion_reward should_gain_stars
should_generate_treasure should_pay_excess_energy_cost_with_stars should_play
should_player_reset_energy should_power_be_removed_on_death should_proceed_to_next_map_point
should_procure_potion should_refill_merchant_entry should_stop_combat_from_ending
should_take_extra_turn
-->

**Out-parameter replacements** (6). `bool` plus an `out` value: the flag claims the replacement, the parameter carries it.

<!-- openmod-capabilities:
try_modify_card_being_added_to_deck try_modify_card_being_added_to_deck_late
try_modify_energy_cost_in_combat try_modify_energy_cost_in_combat_late
try_modify_power_amount_received try_modify_star_cost
-->

**Collection edits** (7). A host-owned list you add to or remove from. Preserve every entry you did not come for.

<!-- openmod-capabilities:
try_modify_card_reward_alternatives try_modify_card_reward_options
try_modify_card_reward_options_late try_modify_keywords_in_combat
try_modify_rest_site_heal_rewards try_modify_rewards try_modify_rewards_late
-->

**Enchantment replacements** (5). Available only on an Enchantment, and mandatory there instead of the general hook.

<!-- openmod-capabilities:
enchant_block_additive enchant_block_multiplicative enchant_damage_additive
enchant_damage_multiplicative enchant_play_count
-->

Total: 71 declared ids. The two Rest Site hooks are deliberately absent; they are
declared by `reference/rest-site-options.md`.
