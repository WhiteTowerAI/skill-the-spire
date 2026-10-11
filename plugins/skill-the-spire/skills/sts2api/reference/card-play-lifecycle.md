# Card play lifecycle - before/after play, free play, transforms, and type text

Status: **authorable with RitsuLib 0.6.7 on STS2 0.107.1**. The public Card play, free-play,
transform, carry-over, and type-text routes compile against the pinned Compat assembly. New
generated combinations remain game-unobserved until their exact real-host scenario runs.

Use this route when a Card or another truthful owner changes a Card's play lifecycle rather than
only implementing the Card's ordinary `OnPlay` body.

## SPEC contract

```markdown
- **Card play lifecycle**:
  - owner: <Card/capability/other model or Global Effect>
  - operation: before owner OnPlay | after owner OnPlay | free play | transform reaction |
    transform carry-over | type-text composition
  - affected Card: <identity and runtime guard>
  - timing/duration: <exact point; next play | until played/end of turn | rest of turn |
    current combat | current CardPlay>
  - behavior/text: <ordered action and localized visible meaning>
  - cleanup: <played, turn end, combat-instance end, transform, or explicit unregister>
  - neutral case: <unmatched Card/play leaves behavior and costs/text unchanged>
```

## Immediately around `OnPlay`

Implement `ICardOnPlayHookListener`, normally through `CardPlayCapability` for a Card-owned
effect. `BeforeCardOnPlay` runs immediately before the Card's protected `OnPlay`; return `true` to
suppress that body while preserving the rest of `OnPlayWrapper`. `AfterCardOnPlay` runs after the
body point and before enchantments, afflictions, and the normal `Hook.AfterCardPlayed`. Its
`OriginalOnPlayRan` distinguishes normal execution from suppression.

For a Card-owned capability, the base filters by Card instance and pushes the capability model into
the choice context. A process-wide `RegisterCardOnPlayHookListener` is allowed only for a selected
Global Effect; every other owner implements the interface on its model/capability. Suppression is a
complete semantic replacement decision, not a shortcut for adding an effect. An after listener
must decide explicitly whether it runs when `OriginalOnPlayRan` is false.

Use `OneShotCardPlayCapability` for an attached effect that runs once after its owning Card and
then removes itself even if the effect throws. Ordinary one-use Cards still use their native
result-pile lifecycle, not this capability.

## Free-play durations

RitsuLib's free-play binding covers fixed base Energy, Star, and registered secondary-resource
costs. X costs keep their normal game behavior unless that resource's own route says otherwise.

- `MarkCardFreeNextPlay(card)`: one charge consumed by the next successful play; no turn expiry.
- `MarkCardFreeThisTurn(card)`: free until the earlier of successful play or end-of-turn cleanup.
- `card.SetToFreeForRestOfTurn()`: every subsequent play this turn; expires at turn cleanup.
- `MarkCardFreeThisCombat(card)`: the Card's current combat instance remains free for that combat.
- `MarkCurrentPlayFree(cardPlay)`: marks only the already-created play instance.

`Resolve(cardPlay)` reports auto-play-no-spend, Card binding, and registered detector sources;
`IsCardFreeForUpcomingPlay(card)` checks display/payment state without consuming a next-play
charge. A custom detector registered through `RegisterFreePlayBinding` only describes an existing
truthful free-play source; it must not grant an unrelated Card free play by broad predicate.

Keep cost display and payment semantics aligned. Do not stack a manual refund on top of free play.
Assert cleanup through the native play/turn/combat lifecycle rather than calling the public clear
helpers as the product implementation.

## Card transformations

`GetCardTransformRegistry(ModId)` registers stable listener IDs for completed base-game
transformations. Choose one of:

- all transformations with an explicit predicate;
- a typed original/replacement pair;
- `RegisterFrom<TOriginal>`; or
- `RegisterTo<TReplacement>`.

The callback receives the original Card, final replacement after base-game modifiers, original
pile, and original pre-transform pile index. Registration order is stable; registering the same
Mod/listener ID replaces the callback without changing its order. `Unregister` removes it.

Use a registry callback for a reaction whose owner is the transformation operation or a truthful
Global Effect. Use `ICardTransformCarryOverCapability` when state/behavior on the original Card
itself should copy to the replacement; see `model-capabilities.md`. Do not rebuild carry-over by
matching IDs after the transform.

## Type-text composition

An individual Card implements `ICustomTypeTextCard`; a model/capability affecting Cards implements
`ICardTypeTextModifier`. Return localized `LocString` modifiers in application order. A modifier
containing `{Type}` wraps the previously selected type text. A modifier without `{Type}` replaces
the base selection; later replacements win, then wrappers apply in order around that result.

Use bilingual localization with matching SmartFormat tokens. Type text is presentation, not a
behavioral Card tag: register any actual tag/keyword separately. Process-wide
`RegisterCardTypeTextModifier` belongs only to a Global Effect with a truthful guard.

## Composition order

A single Card play can combine free resolution, before/after listeners, owner `OnPlay`,
enchantment/affliction handling, normal after-play hooks, result-pile movement, and transform
callbacks. Preserve each API's phase; do not collapse all effects into `OnPlay`. Await every
behavior callback/command before asserting post-state. A transform callback observes a completed
transform and cannot cancel it.

## SelfTest contract

- before/after: drive a real Card play and assert exact order, target/owner identity,
  `OriginalOnPlayRan`, normal wrapper/result-pile behavior, suppression result, and unmatched Card;
- free play: assert visible fixed costs, successful no-spend, effect exactly once, next-play versus
  rest-of-turn distinctions, end-turn/combat cleanup, X-cost behavior, and rejected/other Card;
- transform: drive the native transform command, assert original/replacement/pile/index, typed
  filter, listener order/replacement/unregister, carry-over copy/drop, and no duplicate capability;
  and
- type text: resolve the real Card consumer in `eng` and `zhs`, assert replacement/wrapper order,
  no raw `{Type}`, normal keyword/tag behavior, and the neutral Card unchanged.

Headed review owns real Card readability and layout. Build, direct registry invocation, and text
string inspection are not hosted play/transform/UI proof.
