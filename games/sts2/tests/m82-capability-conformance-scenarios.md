# M8.2 behavioral scenarios: exact semantic capability conformance and preflight

Three cases, each one a way the pipeline used to produce a Mod whose promised behavior was
absent while every local stage passed. They are semantic rubrics, not prose snapshots: what
matters is the decision the workflow reaches, not the wording it reaches it in.

Scope limit: these describe expected workflow behavior. No forward-model run, generated Mod,
game launch, Tier 1, or Tier 2 is claimed by this file. The two real-host proofs step 3 owes are
listed under § What these scenarios do not prove.

## Scenario 1 — the Wrath case: a stance that doubles incoming damage

**Request.** "A stance Power called Wrath. While you're in it, you deal double damage but you
also take double damage."

This is the M7.6 failure verbatim. The requirement was recorded, an operation was generated, the
harness passed, and the multiplier was never implemented. Three things must now happen instead.

**Expected.**

1. **The design question gets asked, because the grammar now has a field for the answer.** Two
   distinct guards are involved: outgoing damage keys on the dealer, incoming keys on the target.
   And "damage" is ambiguous on this host — attack damage from a Card or Monster move is a
   different thing from Poison-style HP loss and from damage dealt by relics, potions, and powers.
   The workflow proposes the vanilla-consistent reading (attack damage only, as Vulnerable and
   Weak both do) and says what it excludes, rather than silently choosing.
2. **SPEC declares participation, not prose.** Two `hook participation` entries on the Power
   surface, each carrying its capability id, shape, subject, condition, value, the
   `DynamicVar` name that puts the number in the rules text, and the neutral return outside the
   guard. Both cite `reference/model-hook-participation.md`, and both appear in the generation
   trace with `capability_ids`.
3. **Preflight passes for a reachable declaration and the author has a guard shape to copy.**
   `modify_damage_multiplicative` is authorable on `power`, so the check is silent here — its job
   in this scenario is to *not* block, while the recipe supplies the three-part body
   (subject guard, condition guard, value read from `DynamicVars`) that the empty method lacked.

**Rejected.** Recording "doubles damage taken" only inside `effects.sequence`, where nothing
downstream can check it. Choosing a damage-kind reading without stating it. Writing the multiplier
as a literal in the body and again in the description. Returning the multiplier without a guard —
which passes a single-value assertion while doubling every damage event in the run.

## Scenario 2 — a hook requested on a surface that cannot receive it

**Request.** "A Power that makes card rewards show four options instead of three."

**Expected.** The capability exists (`try_modify_card_reward_options`) but it is dispatched at run
scope, and the run-scope listener set contains no Powers. So the declaration is rejected before
generation, with a message naming the capability, the declaring surface, and the surfaces that can
receive it. The workflow then offers what actually works: the same rule on a Relic or a Potion,
which are in the run-scope set. If the user's design requires it to be a Power, that is `INV-3` —
a gap recorded in `DESIGN.md`, not an approximation.

**Rejected.** Generating the override because the method exists on `AbstractModel` and compiles.
This is the case that makes the whole Package worth having: the code would ship, never fire, and
present exactly as the Watcher failure did — a passing build and an absent behavior. Also
rejected: silently relocating the rule to a Relic without telling the user the surface changed.

## Scenario 3 — an Enchantment damage multiplier

**Request.** "An enchantment that makes the card it's on deal 50% more damage."

**Expected.** The declaration routes to `enchant_damage_multiplicative`, not
`modify_damage_multiplicative`. The pinned `EnchantmentModel` documents five such replacements as
mandatory in place of their `AbstractModel` counterparts, and each runs before every other
modification hook for that value. Preflight rejects the general id on an enchantment and the
`enchant_*` id anywhere else. The authored body has no subject guard — the hook is already scoped
to its own card — and returns `1m` outside its condition, because this is the multiplicative
member of the family.

**Rejected.** Overriding `ModifyDamageMultiplicative` on the Enchantment: it compiles, and the
framework's own documentation forbids it. Copying the additive neutral (`0m`) into the
multiplicative hook, which silently zeroes the card's damage. Writing a cross-card rule here,
which the signature cannot express.

## What these scenarios do not prove

Preflight is static. A green run means the declaration is well-formed, reachable, correctly
shaped, and paired with a route that claims the capability — not that the generated override
fires, returns the right number, or leaves unrelated interactions alone.

Two real-host proofs are owed and unrun, and they need Windows + STS2 `0.107.1` + RitsuLib
`0.5.4`:

1. **Value shape.** A custom Power declaring an incoming-damage multiplier, asserted for the
   modified value, the neutral case outside the guard, and the rules-text number matching the
   applied multiplier.
2. **Collection shape.** One collection edit asserting both its own entry and the survival of
   unrelated entries — the `Midas` failure mode, where an editor that clears the list still
   passes "my entry is present".

Until those run, every hook route in the catalog is implemented-and-unproved. Per `AGENTS.md`,
that is missing verification, not missing support, and it is recorded rather than rounded up.
