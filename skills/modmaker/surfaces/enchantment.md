# Surface: enchantment

Everything the pipeline needs for one card enchantment, in one place. Read this page at the
`spec.md`, `author.md`, and `verify.md` stages when SPEC declares an enchantment.

## No SPEC fields of its own

An enchantment is always attached to a host Card, so it has **no element block**. Declare it
inside its host Card's SPEC fields:

```markdown
  - enchantment: <name> — <what it adds to the host card>
    amount: <value and bounds>
    host restriction: <which cards may legally carry it>
    stacking: replaces an existing enchantment | not stackable
```

The host Card's `localization` section records exact English and Simplified Chinese
title/description/optional `extraCardText`. The stable entry and the SmartFormat variables are
identical between languages.

`host restriction` is a required line, not commentary: it is the enchantment's identity and
the thing its proof must exercise — see § Proof matrix. Enchantment and keyword stay host-scoped;
`orb` has its own envelope.

Hook participation is declared the same way — nested under the host Card's `enchantment:` block,
using the form in `reference/model-hook-participation.md`:

```markdown
    hook participation: none | one or more
```

## Five hooks an Enchantment must not use

An Enchantment reaches 61 of the 68 cataloged hooks at their ordinary signature. The other five
are **replaced**, and using the general hook there is wrong on the pinned host:

| Instead of | An Enchantment declares | Neutral |
|---|---|---|
| block, additive | `enchant_block_additive` | `0m` |
| block, multiplicative | `enchant_block_multiplicative` | `1m` |
| damage, additive | `enchant_damage_additive` | `0m` |
| damage, multiplicative | `enchant_damage_multiplicative` | `1m` |
| card play count | `enchant_play_count` | the original count |

The pinned assembly documents each as "Enchantments MUST use this hook instead of" its
counterpart, and each runs **before** every other modification hook for that value — so an
enchantment's contribution is the first thing applied, not one contributor among many.

Two differences from the general form follow. There is **no subject guard**: the hook is already
scoped to this enchantment's own card, so the only condition left is which kinds of damage or
block count. And the additive neutral is `0m` while the multiplicative neutral is `1m` — a guard
copied from the wrong one is a silent `x0` or a stray `+1`.

Reachability has one more consequence worth stating: an Enchantment receives combat-scope hooks
only while its host Card is in a combat pile, because it inherits that from the Card. A rule
declared for all of combat does not hold on an enchanted Card sitting outside the piles.

## Shared capability routes

Read `reference/model-capabilities.md` when the Enchantment carries a separable behavior/state
bundle, `reference/lifecycle-state-rng.md` when that state crosses a callback/save boundary or uses
gameplay RNG, and `reference/shared-effect-hooks.md` for a reachable per-hit attack, healing,
Energy/Stars-gain, or maximum-hand-size effect. The Enchantment or its typed capability remains
the owner and inherits the host Card's combat-pile reachability.

Append only the selected reference's nested game-term SPEC block. Preserve the five replacement
hooks above, each service's own phase/order, an unchanged neutral case, and removal/cleanup proof.
Do not register a process-wide listener for an Enchantment-owned rule.

## Ordinary effect projection

The awaited attached callback is `OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)`.
It supplies `choiceContext`, exact host Card `Card`, owner Player `Card.Owner`, owner Creature
`Card.Owner.Creature`, and the nullable host `cardPlay`; use `cardPlay?.Target` only when the
attached effect truthfully follows that selected target. Read `reference/effect-primitives.md`
for the sequence. Preserve the host Card as `cardSource`, pass the real `cardPlay` for Card-caused
Block, and reject target-dependent effects when `cardPlay`/target is absent. Synchronous
attachment/restriction hooks cannot await commands.

## The engine writes `extraCardText` onto the host card

When `HasExtraCardText` is true, the engine stamps the enchantment's localized
`extraCardText` into the host card's rendered description, and folds the enchantment's Hover
Tip into that card's `HoverTips`.

So the enchantment owns two distinct strings and the host card owns neither of them:

- `.description` — the enchantment's own hover text.
- `.extraCardText` — what the engine appends to the host card. Emit it only when
  `HasExtraCardText` is true.

**Do not write either string into the host card's own description.** The recipe's example
values are deliberately near-duplicates of each other; that is a localization shape, not a
license to write the same sentence a third time on the card.

## Text style

Write every player-facing string in the default style of `reference/vanilla-text-style.md`:
the title stays plain; `.description` and `.extraCardText` show `[blue]` numbers and
`[gold]` glossary terms. Any other string that names the Enchantment wraps the name in
`[purple]`, as vanilla does (`[gold]Enchant[/gold] it with [purple]Instinct[/purple].`), and
declares `HoverTipFactory.FromEnchantment<T>()` in its `AdditionalHoverTips`.

## Author the element class

**Card enchantment** — extend `ModEnchantmentTemplate`, register it once through
`.Enchantment<T>()`, and attach it with `CardCmd.Enchant<T>`. Keep amount, host restriction,
and `OnPlay` behavior explicit. A custom icon uses the checked 64x64
`EnchantmentAssetProfile`; placeholder mode omits it.

- Preserve base restrictions when overriding `CanEnchant`. The engine's own restrictions
  already reject Status/Curse/Quest card types and `Unplayable` deck cards, and reject a
  second enchantment unless `IsStackable`. An override may **add** restrictions; removing one
  is out of contract.
- Ship matching `localization/eng/enchantments.json` and
  `localization/zhs/enchantments.json` with `.title`, `.description`, and — only when
  `HasExtraCardText` — `.extraCardText`.
- Leave the host card's description free of both strings.

See `../sts2api/recipes/enchantment.md` for the exact registration call and JSON shape.

## Self-test driver body

An enchantment has no scenario of its own. Use its host Card's scenario (`surfaces/card.md`)
and add the enchantment assertions below to it.

## Proof matrix

- Assert registration and localization resolve, then assert attachment:
  `card.Enchantment is <EnchantmentName>` with the SPEC amount read from that mutable
  instance.
- Drive the host Card and assert the changed outcome the enchantment causes.
- Assert the composed host-card text contains the `extraCardText` exactly **once**, so a
  hand-written duplicate is caught rather than shipped.
- **Assert the host restriction by attempting an illegal host.** Attachment plus a changed
  outcome is a happy path only: it passes for an enchantment that will attach to anything,
  including Curses and `Unplayable` cards. Attempt one host the SPEC restriction forbids and
  assert the attachment is refused and the card is unchanged.
- When `stacking` is `not stackable`, attempt a second enchantment on an already-enchanted
  card and assert the declared outcome — refusal or replacement — rather than assuming it.
- **For hook participation — assert the neutral case outside the guard.** Attachment plus a
  changed host outcome does not observe it: an `enchant_damage_multiplicative` that ignores its
  damage-kind condition passes both while also scaling damage the design excluded. Assert the
  modified value through the host Card, then drive one excluded case and assert it is unchanged.
  For one of the five replacements, additionally assert the value on an **unenchanted** card of
  the same kind is untouched, which is what proves the contribution is scoped to its own host.

Custom icon support still requires a headed render in both the Card tab and hover tooltip; a
path getter alone does not promote visual support.
