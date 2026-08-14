# Surface: Card Pile

Use this surface for an independently registered place that stores, moves, inspects, or visibly
presents exact Card instances outside the vanilla piles. Card Pile owns its combat/run lifetime,
registration, persistence, screen/control/ExtraHand presentation, movement rules, and cleanup.

Do not reduce this surface to the previously exercised ExtraHand case. RitsuLib `0.5.11` exposes
the complete documented Package through `reference/card-piles.md`.

## DESIGN and SPEC vocabulary

Settle and write every selected pile's:

- stable local identity, capacity/duplicate rules, combat-only or run-persistent scope, and exact
  reset/save/restore/run-end behavior;
- `headless`, top-bar deck, bottom-left, bottom-right, or ExtraHand style; matching preset plus
  offset, or explicit custom position/pivot;
- English and Simplified Chinese title, description, and empty text; checked icon or placeholder;
- visibility predicate, hover placement, hotkeys, default or capstone open behavior, and vanilla,
  deck-like, or explicit inspect/upgrade/sort view;
- every trigger that moves an exact Card instance in or out, source, destination, top/bottom order,
  pre-move rejection, and normal result-pile behavior;
- ExtraHand visibility, layout, scale, glow, manual-play policy, and any scoped visual callbacks;
  and
- real-host SelfTest plus headed/controller cases for every selected lifetime and UI consumer.

## Authoring route

- Read `recipes/card-pile.md`, then the complete `reference/card-piles.md` Package.
- Read `recipes/card.md` for Card creation/play semantics and `reference/card-play-lifecycle.md`
  when manual play must compose with owner play hooks or result-pile rules.
- Use only awaited native `CardPileCmd` movement. Do not mutate pile collections, clone a Card to
  imitate movement, or patch the native ExtraHand play coordinator.

## Proof matrix

Follow the selected matrix in `reference/card-piles.md`:

1. assert the qualified ID, dynamic `PileType`, exact scope, one live pile per declared owner, and
   no duplicate registration;
2. test empty/full/capacity/duplicate rejection before mutation, exact instance identity, movement
   order, and every declared exit/result destination;
3. test combat reset or run persistence, save/load restoration, existing-save behavior, and run
   cleanup as selected;
4. test each selected button, hotkey, visibility, hover, open/view/sort/inspect/upgrade consumer;
5. for ExtraHand, test mouse/controller focus, cancel restoration, payment, consecutive plays,
   normal result piles, numbered-shortcut isolation, layout, and callback cleanup; and
6. headed review covers requested aspect ratios, custom anchors, neighboring controls, icon/text,
   animations, and controller behavior.

Static registration and pile lookup are not UI, movement, persistence, or gameplay proof. Newly
selected `0.5.11` variants remain game-unobserved until their exact real hosts run.
