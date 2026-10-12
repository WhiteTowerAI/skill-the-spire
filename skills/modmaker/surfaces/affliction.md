# Surface: Affliction

Use this surface when the requested product is a combat-only condition attached to one concrete
Card. An Affliction is not a run-wide curse, a deck-wide rule, or another name for an Enchantment.
It is applied to a mutable Card during combat, participates while attached, and travels only with
the host Card lifecycle the game provides.

## DESIGN and SPEC vocabulary

Settle and write:

- identity and the Card types/keywords/states it may afflict;
- stackable or single-application behavior and the integer amount meaning;
- application source, selected Card or Card set, preview style, and rejection behavior;
- attached triggers/effects, hook participation, and exact owner guard;
- `AfterApplied`, `BeforeRemoved`, and attached-Card `OnPlay` behavior when selected;
- title, description, optional extra Card text, `{Amount}` use, hover tips, and overlay choice;
- removal/reset expectations and every neutral or rejected case; and
- `CombatPlayer` SelfTest plus headed Card-overlay/text review when presentation is selected.

An Affliction is combat-only. Do not promise run persistence, deck acquisition, or a post-combat
owner. `CardCmd.Afflict<T>` returns `null` when combat/host checks or `CanAfflict` reject it. The
existing Affliction must be the same concrete type before stacking; another attached type is not a
replacement route.

## Text style

Write every player-facing string in the default style of `reference/vanilla-text-style.md`:
the title stays plain; `.description` shows `[blue]{Amount}[/blue]`, glossary terms in
`[gold]`, and Energy through `energyIcons()`; `.extraCardText` is one short Card-face
sentence. A Card or Relic that applies the Affliction names it in `[gold]` and declares
`HoverTipFactory.FromAffliction<T>()` in its `AdditionalHoverTips`.

## Authoring route

- Read `recipes/affliction.md` for template, registration, `CardCmd.Afflict<T>`,
  `AfflictAndPreview<T>`, stacking, removal, localization, and overlay rules.
- Read `reference/model-hook-participation.md` for raw scalar/decision/collection hooks on the
  attached Affliction. SPEC uses `surface: affliction`; only combat-reachable hooks are admitted.
- Read `reference/model-capabilities.md` only when behavior is a separable component of the
  Affliction rather than the Affliction's own identity.
- Read `reference/lifecycle-state-rng.md` for subscriptions, disposal, or deterministic target
  selection, and `reference/shared-effect-hooks.md` for the dedicated per-hit/heal/resource/hand
  services.

The Affliction itself is the truthful owner. Do not register a process-wide listener or Global
Effect to imitate a Card-attached condition.

## Ordinary effect projection

Only the attached awaited `OnPlay(PlayerChoiceContext choiceContext, Creature? target)` path can
compose ordinary commands directly. It binds the exact host `Card`, `Card.Owner`,
`Card.Owner.Creature`, `choiceContext`, and nullable resolved `target`; null-check the target when
the selected primitive requires one, follow `reference/effect-primitives.md`, and preserve the
host Card as `cardSource`. This callback does not receive the enclosing `CardPlay`, so pass
`cardPlay: null` where a primitive permits it and block any effect that specifically requires the
current `CardPlay`. `AfterApplied` and `BeforeRemoved` are synchronous and cannot run awaited
primitives; select an actual async lifecycle hook or block with that exact missing async context.
Affliction apply/preview/clear remain this surface's specialized transaction, not ordinary Card
creation or movement.

## Proof matrix

Use a real mutable Card in `CombatPlayer`:

1. reject every disallowed Card and assert no Affliction, history entry, preview, or side effect;
2. apply to one allowed Card and assert concrete type, exact integer amount, owner Card identity,
   `AfterApplied` exactly once, localized text, and selected overlay resource;
3. for stackable behavior, apply again and assert the same attached instance/type and exact summed
   amount; for non-stackable behavior, assert the second application is rejected;
4. play the attached Card and assert `OnPlay` and selected hook effects after the real Card wrapper,
   plus one unrelated Card/event that remains neutral;
5. clear through `CardCmd.ClearAffliction`, assert `BeforeRemoved` exactly once and no further
   participation, then cross the declared combat end/reset edge; and
6. for multi-Card preview, use same-owner Cards, assert only successful Cards are previewed, and
   never claim mouse/controller/text/overlay quality without headed review.

Source/Build establishes neither attachment behavior nor visual proof. This new surface remains
game-unobserved until its exact hosted matrix runs.
