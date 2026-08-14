# M8.9 ordinary effect primitive audit

This repository-only audit answers which player-visible ordinary results a truthful behavior
owner can execute through the pinned public/fixed profile. Decisions are semantic-family units,
not a permanent symbol ledger.

## Evidence checked

- RitsuLib guide navigation and the effect-relevant framework, content-authoring, custom-Event,
  secondary-resource, and lifecycle pages.
- RitsuLib tag `v0.5.11` at `8a2eb7c756d926287078f953f2fac1d47ec014b4`, including
  model capabilities and the attack-hit, heal, resource-gain, and hand-size services.
- Workshop RitsuLib `0.5.11` stable variant
  `STS2-RitsuLib.dll` SHA-256
  `6c2f65d2245207226aba80d3ea83b928871bd6e9fb7584d28b2669e10d335413`.
- STS2 `0.107.1` public `Commands`, attack builder, mutable models, and the installed
  `sts2.dll` SHA-256
  `a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`.
- Every current open-mod surface, recipe/reference command mention, M8.8 inventory family, and
  representative vanilla Card, Relic, Potion, Power, Monster, and Event call sites used only to
  clarify parameters, source/target binding, queue order, and partial results.

The guide is a semantic index. Exact M8.9 lowerings use the pinned public Compat/game signatures.
No relevant guide/source/API or current-recipe rescan after the decisions below produced another
ordinary player-result family.

## Included shared families

| Player semantic family | Public/fixed evidence | Decision and current gap |
|---|---|---|
| Attack or effect damage | `DamageCmd.Attack(...).FromCard/FromMonster(...).Execute(...)`; `CreatureCmd.Damage(...)` | **Include.** Recipes duplicated source/target/`ValueProp` rules and lacked one cross-surface lowering contract. |
| Block, healing, and bounded HP changes | `CreatureCmd.GainBlock`, `LoseBlock`, `Heal`, `GainMaxHp`, `LoseMaxHp` | **Include.** Centralize returned applied Block, heal caps/hooks, Max HP floor/context, and card-vs-non-card provenance. |
| Apply, change, or remove a Power | `PowerCmd.Apply<T>`, `ModifyAmount`, `Remove<T>/Remove` | **Include.** Centralize rejection/null/partial multi-target results and safe Counter consumption; the Power recipe still owns custom Power identity. |
| Energy, Stars, Gold, and potion capacity | `PlayerCmd.Gain/LoseEnergy`, `Gain/LoseStars`, `Gain/LoseGold`, `Gain/LoseMaxPotionCount` | **Include.** Centralize gain hooks, positive/zero rules, Gold loss classification/floor, and combat/run lifetimes. Secondary resources remain specialized. |
| Draw Cards | `CardPileCmd.Draw(choiceContext, count, player, fromHandDraw: false)` | **Include.** Existing recipes often required fresh lookup; centralize choice context, decimal ceiling/zero behavior, native shuffle/hooks, and partial returned Cards. |
| Discard or Exhaust known combat Cards | `CardCmd.Discard`, `DiscardAndDraw`, `Exhaust` | **Include.** Centralize exact-instance ownership, batch discard timing, context, and terminal-combat no-op behavior. Selecting Cards remains separate. |
| Create a known Card in combat | owner/run `CreateCard<T>` plus `CardPileCmd.AddGeneratedCardToCombat` | **Include.** Centralize creator, exact returned pile result, position, and native pile/history lifecycle. Arbitrary pile movement remains the Card Pile route. |
| Acquire a known Card, Relic, or Potion in a run | `RunState.CreateCard<T>` + `CardPileCmd.Add(..., PileType.Deck)`; `RelicCmd.Obtain<T>`; `PotionCmd.TryToProcure<T>` | **Include.** Centralize exact acquisition results and honest Potion rejection; Reward and selection screens stay separate owners. |
| Channel/evoke Orbs and change Orb slots | `OrbCmd.Channel<T>`, `EvokeNext/EvokeLast`, `AddSlots`, `RemoveSlots` | **Include.** Centralize queue owner/context and slot bounds. Orb passive behavior remains owned by the Orb recipe. |

`Cmd.Wait` is not a semantic family. It may sequence presentation only when an owning specialized
route explicitly requires it; ordinary effect correctness must not depend on an arbitrary delay.

## Excluded or specialized families

| Discovered family | Decision |
|---|---|
| Card play, free play, play-from-draw-pile, and turn completion | **Exclude:** lifecycle control; use `reference/card-play-lifecycle.md`, Card Pile ExtraHand, or the owner hook. |
| Card selection, deck remove/upgrade/transform/enchant, Affliction, and Card keywords | **Exclude:** identity/selection/attachment transactions; use `reference/event-outcomes.md`, `recipes/enchantment.md`, or `recipes/affliction.md`. |
| Arbitrary Card pile movement, shuffle, and custom piles | **Exclude:** pile lifecycle and exact-instance ownership; use `recipes/card-pile.md` and `reference/card-piles.md`. Normal draw/discard/exhaust remain included above. |
| Rewards and linked rewards | **Exclude:** blocking claim/refusal/persistence transaction; use `recipes/reward.md`. |
| Rest Site payment/options, Event pages/combat transitions, forced Events, and map/Act changes | **Exclude:** blocking world transactions and lifecycle; use their dedicated references/recipes. Their immediate child effects may use the shared primitives. |
| Spawn/kill/escape/stun creatures, pets, Osty summon, and Forge | **Exclude:** encounter/state-machine or specialized character mechanics whose lifecycle is not an ordinary effect primitive. |
| Set Energy/Stars/Gold/HP/Max HP directly | **Exclude:** absolute setup/debug/lifecycle control. Express normal player effects as gain/loss/damage/heal; specialized setup routes may use setters when they explicitly own that contract. |
| Secondary resources and payment | **Exclude:** full M8.7 registry/payment/UI contract; use `reference/character-resource.md`. |
| Queries, selectors, RNG, capabilities, hooks, state, and diagnostics | **Exclude:** inputs/infrastructure rather than player results; use the existing shared references. |
| Audio, VFX, Talk/Think, preview, UI, assets, and animation | **Exclude:** presentation with separate host/headed ownership; preserve existing routes. |
| Registration, content composition, availability, and vanilla replacement | **Exclude:** identity/composition, not an effect call; use the owning recipe/override package. |
| Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, WP6, and WP7 | **Exclude:** explicitly deferred product groups. |

## Version findings

- The current online guide and pinned checkout expose the same 25-page navigation used by M8.8;
  it does not document a general effect engine or complete STS2 command catalog.
- The stable Compat assembly is named `STS2-RitsuLib.dll`; generated code still targets the
  `STS2.RitsuLib.Compat.0.107.1` API/profile identity recorded by scaffold.
- `CardPileCmd.Draw` takes `decimal count`, rounds a positive request up, uses
  `fromHandDraw: false` for ordinary effects, and returns only Cards actually drawn.
- `CreatureCmd.GainBlock` returns the post-modifier requested Block amount, while the current
  creature state is still the authoritative observed delta. `PowerCmd.Apply<T>` can return null
  per target. `PotionCmd.TryToProcure` returns a result instead of guaranteeing acquisition.
- RitsuLib `0.5.11` adds dedicated owner-bound effect hooks around ordinary commands; those hooks
  stay in `reference/shared-effect-hooks.md`, while this audit/reference owns invoking the effects.
