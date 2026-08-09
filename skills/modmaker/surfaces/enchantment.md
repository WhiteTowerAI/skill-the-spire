# Surface: enchantment

Everything the pipeline needs for one card enchantment, in one place. Read this page at the
`spec.md`, `author.md`, and `verify.md` stages when SPEC declares an enchantment.

## No SPEC envelope of its own

An enchantment is always attached to a host Card, so it has **no element block**. Declare it
inside its host Card's envelope:

```markdown
  - enchantment: <name> — <what it adds to the host card>
    amount: <value and bounds>
    host restriction: <which cards may legally carry it>
    stacking: replaces an existing enchantment | not stackable
```

`host restriction` is a required line, not commentary: it is the enchantment's identity and
the thing its proof must exercise — see § Proof matrix. Reviewed and accepted on 2026-08-07:
enchantment and keyword stay host-scoped, while `orb` received its own envelope.

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

## Author the element class

**Card enchantment** — extend `ModEnchantmentTemplate`, register it once through
`.Enchantment<T>()`, and attach it with `CardCmd.Enchant<T>`. Keep amount, host restriction,
and `OnPlay` behavior explicit. A custom icon uses the checked 64x64
`EnchantmentAssetProfile`; placeholder mode omits it.

- Preserve base restrictions when overriding `CanEnchant`. The engine's own restrictions
  already reject Status/Curse/Quest card types and `Unplayable` deck cards, and reject a
  second enchantment unless `IsStackable`. An override may **add** restrictions; removing one
  is out of contract.
- Ship `localization/eng/enchantments.json` with `.title`, `.description`, and — only when
  `HasExtraCardText` — `.extraCardText`.
- Leave the host card's description free of both strings.

See `sts2-api/recipes/enchantment.md` for the exact registration call and JSON shape.

## Self-test driver body

An enchantment has no scenario of its own. Use its host Card's `InCombat` driver
(`surfaces/card.md`) and add the enchantment assertions below to that run.

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

Custom icon support still requires a headed render in both the Card tab and hover tooltip; a
path getter alone does not promote visual support.
