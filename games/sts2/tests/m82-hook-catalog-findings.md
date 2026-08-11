# M8.2 step 1: the pinned model-hook catalog, and what extracting it found

Step 1 of the M8.2 contract is a blocking prerequisite: before any surface can declare hook
participation, the pack has to know which hooks a given generated element can actually
*receive*. This file records what the extraction produced and the three findings that came
out of building it.

**Scope limit.** Everything here is read from the pinned `0.107.1` decompile under
`baselines/decomp/`, whose original DLL provenance sidecar was not retained. Every fact is a
research result to recheck against the pinned assembly or installed game before it becomes
authoring instruction. Nothing here has been run in a game, and no generated Mod exists yet.

## What was produced

`games/sts2/tools/collect_model_hooks.py` projects the pinned hook surface into
`sts2-api/reference/catalogs/model-hooks-sts2-0.107.1.json`. It follows the
`collect_vanilla_catalog.py` precedent exactly: maintainer-only, excluded from both payloads
by `publish.sh`, with the committed catalog as the shipped artifact.

Per hook it records the exact signature, return type, **neutral default**, the `Hook`
dispatchers that invoke it, the dispatch iterators those walk, the resulting listener
families, the authorable generated surfaces, and the vanilla implementor counts by family.

**68 hooks: 26 numeric, 28 decision, 14 `TryModify*`. Zero unresolved.**

The neutral default is recorded because it is authoring input, not trivia: it is what a
guard must return outside its intended case. A hook that returns its modifier
unconditionally still passes a single-value assertion while changing every unrelated
interaction in the game.

## Finding 1 — reachability is decided by the iterator, and it splits the hook list

`Hook` dispatches through five distinct iterator forms whose listener sets differ:

| Iterator form | Scope | Listener families |
|---|---|---|
| `runState.IterateHookListeners(null)` | run | card, enchantment, relic, potion, modifier, badge |
| `runState.IterateHookListeners(combatState)` | run+combat | affliction, badge, card, enchantment, modifier, monster, orb, potion, power, relic |
| `IterateCombatHookListeners(combatState)` | combat | same as above |
| `combatState.IterateHookListeners()` | combat | same as above |
| `CombatState.IterateHookListeners()` | combat | same as above |

The run-scope set contains **no Powers, Orbs, or Monsters**. So a hook dispatched only
through `IterateHookListeners(null)` can never reach a custom Power: the override compiles,
ships, and never fires. That is the M7.6 Wrath failure shape exactly — an identity-critical
behavior absent while every local stage passes — which is why offering the full 54-hook list
uniformly on every surface would have *added* instances of the bug M8.2 exists to prevent.

The resulting three authorable-surface groups:

| Hooks | Authorable on |
|---|---|
| 40 | card, enchantment, monster, orb, potion, power, relic |
| 23 | card, enchantment, potion, relic (run-scope only) |
| 5 | card, monster, orb, potion, power, relic (Enchantment redirected — finding 2) |

## Finding 2 — an Enchantment must not use five of the general hooks

`EnchantmentModel` declares its own replacements, each documented "Enchantments MUST use this
hook instead of" its `AbstractModel` counterpart, and each running before all other
modification hooks:

| General hook | Enchantment replacement |
|---|---|
| `ModifyBlockAdditive` | `EnchantBlockAdditive` |
| `ModifyBlockMultiplicative` | `EnchantBlockMultiplicative` |
| `ModifyDamageAdditive` | `EnchantDamageAdditive` |
| `ModifyDamageMultiplicative` | `EnchantDamageMultiplicative` |
| `ModifyCardPlayCount` | `EnchantPlayCount` |

A generated Enchantment overriding the general hook is wrong on the pinned host. The catalog
records the redirect and removes `enchantment` from those five hooks' authorable surfaces.

## Finding 3 — the first reachability derivation was wrong, and the vanilla cross-check caught it

The first attempt classified scope by nearest-enclosing iterator within a context window
around each call site. It self-contradicted: `ModifyDamageAdditive` and
`ShouldStopCombatFromEnding` came out run-only while having combat-only vanilla implementors
(Powers).

Cause: some hooks are dispatched from a shared private helper rather than from the public
dispatcher that names them. `ModifyDamageAdditive`, `ModifyDamageMultiplicative`, and
`ModifyDamageCap` all dispatch from `ModifyDamageInternal`, which iterates with a combat
state. A context window centred on the call site read whichever iterator happened to be
textually nearest.

Replaced with brace-balanced whole-body attribution over all 148 `Hook` static methods:
every hook resolves to at least one dispatcher, zero are unresolved, and the vanilla
cross-check now reports **zero contradictions**. That cross-check — a vanilla `override` on a
family the catalog calls unreachable is a hard error — is the check that exposed the bad
derivation, and it is now a permanent test.

**A second data bug, found the same way and fixed before the catalog shipped.** The
`run+combat` iterator form was initially modelled as the *union* of the run and combat sets,
which wrongly included run-scope Modifiers and Badges. Reading `RunState.IterateHookListeners`
shows those are added only on the `childCombatState == null` branch; with a combat state it
chains `childCombatState.IterateHookListeners()` instead. Corrected 11 hooks' listener families.

**And a third, found in step 3 by reading the combat iterator the correction had not opened.**
The step-1 fix over-corrected: it concluded the combat-state form reached *no* Modifiers or
Badges and dropped both families from the combat set entirely. But
`CombatState.IterateHookListeners()` ends by walking `combatState.Modifiers` and
`combatState.BadgeModels`. What the run-only branch adds is the run-scope *instances*, not the
family. So both sets contain both families, and `listener_families` was under-specified on every
combat-dispatched hook until step 3 re-extracted the catalog.

All three changed no authorable surface, because Modifier and Badge are not surfaces this pack
generates — real errors with no downstream effect, which is precisely the kind that survives
review indefinitely. Note what did and did not catch them: the vanilla cross-check caught the
first, because a Power implementor contradicted an unreachable claim. It could not catch the
third, because every one of the six vanilla Modifier hook overrides
(`DeadlyEvents`, `NightTerrors`, `Flight`, `Hoarder`, `Midas`, `Vintage`) happens to be
run-scope, so no vanilla evidence contradicted the narrowed set. A cross-check only fails where
vanilla exercises the case; silence from it is not confirmation.

## Cross-check against the shipped vanilla reference: exact match

`sts2-api/reference/vanilla-non-card-overrides.md` independently lists 26 scalar and 28
decision hooks for *vanilla* owners. Compared against the assembly extraction:

- numeric: 26 shipped, 26 extracted, **exact match**;
- decision: 28 shipped, 28 extracted, **exact match**.

That reference is sound and needs no correction. `test_model_hook_catalog.py` now holds the
two statements together, so a future host bump that changes the hook surface fails loudly
instead of leaving one of them silently wrong.

**One gap in that reference, recorded not fixed here.** The 14 `TryModify*` callbacks appear
in neither the vanilla reference nor any custom surface, though they are public virtual and
vanilla uses them heavily. The human lead confirmed on 2026-08-10 that M8.2 opens all 14, so
they are now in scope; the vanilla reference's omission of them remains a separate finding
about that page rather than something this step changed.

## Finding 4 — the 14 `TryModify*` need two declaration shapes, not one

Opening them exposed a distinction the family name hides. `bool` return does not mean the
same thing across the 14:

| Shape | Count | The `bool` means | Declares like |
|---|---|---|---|
| `out-replacement` | 6 | "I am replacing it", with the value in an `out` parameter | a scalar hook plus a taken/not-taken flag |
| `collection-edit` | 8 | only "I touched it" — nothing is replaced | needs add/remove plus a composition rule |

The six replacements are `TryModifyEnergyCostInCombat(Late)`, `TryModifyStarCost`,
`TryModifyPowerAmountReceived`, and `TryModifyCardBeingAddedToDeck(Late)`. These are
structurally identical to `ModifyDamageMultiplicative`: one guard, one value, one neutral
return.

The eight collection edits mutate a list the host owns —
`List<Reward>`, `List<CardCreationResult>`, `List<CardRewardAlternative>`,
`ISet<CardKeyword>`, `ICollection<RestSiteOption>`. Reading the dispatchers confirms the
host ignores the return for behavior: `Hook.ModifyKeywordsInCombat` discards it entirely,
and `ModifyRewards`/`ModifyRestSiteOptions` collect it only to report *which* models touched
the list. So a declaration cannot state a replacement value; it must state what is added or
removed, under what condition, and how it composes with other editors.

The vocabulary is bounded, which is what makes the shape tractable: `Reward` has exactly six
concrete subclasses (`CardReward`, `SpecialCardReward`, `RelicReward`, `PotionReward`,
`GoldReward`, `CardRemovalReward`), and vanilla usage is almost entirely add-one-entry under
a room/owner guard — `BlackStar` adds a `RelicReward` in Elite rooms, `AmethystAubergine`
adds a `GoldReward` in combat rooms. `Midas` is the one vanilla remover, filtering
`SmithRestSiteOption` out of the Rest Site list, so remove is a real case rather than a
hypothetical.

The catalog now records `declaration_shape` per hook (54 scalar-return, 6 out-replacement,
8 collection-edit) plus the exact collection or `out` parameter, so step 3 reads the required
shape as data instead of re-deriving it from a signature.

## Finding 5 — two hooks are already owned by a shipped route

`TryModifyRestSiteOptions` is not a free hook: it is exactly how the shipped Relic-owned Rest
Site option is contributed (`reference/rest-site-options.md`, and `surfaces/relic.md`'s
authoring line). `ShouldDisableRemainingRestSiteOptions` is how that route implements its
stay/leave behavior.

That route carries four boundaries the raw hook does not — singleplayer only, absent versus
natively disabled, free or fixed Gold, and a fully preflightable outcome before the first
mutation. Offering the bare hook beside it would let a generated Mod bypass all four while
looking like a supported declaration.

The catalog records `owned_by_route` for both, and a test asserts the named route file
exists. Step 3 must route Rest Site intent through the existing reference and reject a raw
hook declaration for these two, rather than shipping a second way to do the same thing with
weaker rules.

## Verification status

- Focused tests: `312/312`, up from `298`. Fourteen new in `test_model_hook_catalog.py`.
- Mutation-checked, four ways: offering a run-only hook on a Power, an Enchantment on a
  redirected hook, a collection-edit hook mislabelled as a replacement, and a dropped route
  ownership each fail the specific test written to catch them. A test that cannot fail proves
  nothing.
- The freshness re-extraction skips when `baselines/decomp/` is absent, since it is
  gitignored; the other ten tests validate the committed catalog on its own terms.
- **Not established:** that any generated override fires in a running game. No Mod was built,
  no game launched, no Tier 1 or Tier 2 run. Step 3 owns that and needs a real host.
