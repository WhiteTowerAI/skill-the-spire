# Surface: Reward

Use this surface for a custom option shown in the native rewards UI. A Reward owns its displayed
description/icon, selection success or refusal, deterministic side effect, optional save payload,
and reconstruction after a combat-room save/load. It is not a generic immediate grant helper.

## DESIGN and SPEC vocabulary

Settle and write:

- stable Mod-local reward identity and the player/context that creates it;
- native offer route: a blocking custom reward screen or insertion into the current combat's end
  rewards;
- description in English and Simplified Chinese, checked icon or explicit empty-control fallback,
  display order only when the default custom slot is unsuitable, and content-seen behavior;
- availability and cancellation/refusal conditions, ordered selection side effects, and the exact
  success result: `false` keeps the reward untaken;
- every fact needed to reproduce the same pending reward after save/load, with a versioned typed
  payload when reward type alone is insufficient;
- independent rewards versus one linked set, and for a linked set `choose one` versus `take all`;
  child display order and failure behavior; and
- a real reward-screen SelfTest covering claim, refusal/cancel, leave/continue, and combat-room
  save/load reconstruction without treating registration or serialization alone as behavior.

The selection outcome and reconstructed payload must describe the same deterministic reward. New
Multiplayer synchronization or host-authoritative side effects are deferred; do not add them
through this surface.

## Text style

Write every player-facing string in the default style of `reference/vanilla-text-style.md`:
the reward description is one short sentence with `[blue]` counts and `[gold]` glossary terms
and named Card/Relic/Potion names.

## Authoring route

- Read `recipes/reward.md` for `ModRewardRegistry`, `ModCustomReward`, typed payload persistence,
  native offer/insertion, and `LinkedRewardSets`.
- Read `reference/lifecycle-state-rng.md` only when the selected outcome subscribes beyond the
  Reward's own claim or needs deterministic host/Mod RNG.
- Read the owner recipe for each concrete side effect (Card, Relic, Potion, state, or another
  included route). Do not perform the grant during reconstruction.

## Ordinary effect projection

`ModCustomReward.OnSelect()` supplies its exact owner Player and an awaited blocking transaction;
it supplies no general combat `PlayerChoiceContext`, target Creature, Card source, or `CardPlay`.
Use `reference/effect-primitives.md` for known run-content acquisition and other primitives whose
inputs are truly available. Perform final availability checks first, await the ordered sequence,
inspect Card/Potion acquisition results, return `false` on rejection without claiming success,
and return `true` only after the complete deterministic result. Serialization/reconstruction must
never run the effect. Combat-only primitives require a separately selected callback that exposes
their missing context rather than an `OnSelect()` approximation.

## Proof matrix

Use the real native rewards host selected by SPEC:

1. assert one registered qualified reward type and exact description/icon/order;
2. drive an unavailable or cancelled selection and assert `OnSelect()` returns `false`, no side
   effect occurs, and the reward remains untaken;
3. drive a successful selection, await its complete effect, assert exact post-state, one
   `RewardTakenEvent`, and no duplicate application;
4. for combat insertion, finish the real combat and assert the extra reward appears once; for a
   blocking custom offer, assert the caller resumes only after the reward screen closes;
5. save/load with the reward pending and assert its owner, type, payload, description, and future
   outcome are reconstructed without applying the outcome early;
6. for linked sets, test the chosen mode, child order, failed first claim, skip behavior, and reject
   duplicates, cross-player children, nesting, already-linked children, and size-limit overflow;
   and
7. headed review checks icon, description, focus, controller selection, cancellation, and continue
   flow.

Compile and serialized JSON establish neither a displayed reward nor a successful claim. Until
this matrix runs, custom Reward behavior and presentation remain game-unobserved.
