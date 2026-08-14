# Surface: Modifier

Use this surface for a selectable good or bad daily/custom-run rule that lasts for one run. A
Modifier is part of `RunState.Modifiers`, is saved with that run, and receives both run and combat
model hooks. It is not a Settings toggle, a generic Global Effect, or a replacement for an
obtainable model.

## DESIGN and SPEC vocabulary

Settle and write:

- identity and polarity: good or bad;
- custom/daily list placement, using an explicit integer sort order when placement matters;
- mutually exclusive groups and every other Modifier type in each group;
- effect triggers, guards, order, neutral behavior, and state owner;
- new-run initialization versus load restoration, including whether the starting deck is cleared;
- optional Neow choice and its deterministic awaited outcome;
- title, description, Neow text, hover tips, optional Rest Site Heal text, and icon choice; and
- `RunStart`/`CombatPlayer` SelfTest, save/load case when state persists, and headed selection/icon
  review.

Negative list sort orders insert before the built-in list segment; nonnegative orders insert after
it. Members of an exclusivity group must be at least two distinct concrete Modifier types;
overlapping registered groups merge. Do not invent a setup-screen host or register one type as
both good and bad.

## Authoring route

- Read `recipes/modifier.md` for `ModModifierTemplate`, good/bad registration, ordering,
  exclusivity, run lifecycle, serialization, localization, and icon fallback.
- Read `reference/model-hook-participation.md` for raw hook participation with
  `surface: modifier`; the host exposes the full run/combat listener reachability.
- Read `reference/model-capabilities.md`, `reference/lifecycle-state-rng.md`, and
  `reference/shared-effect-hooks.md` only for their selected separable behavior.
- Read `reference/rest-site-options.md` if the Modifier owns an independent Rest Site action.

The mutable Modifier instance in the run is the owner of run-lifetime behavior and saved model
properties. Do not keep current-run state on the canonical `ModelDb` instance or on a process
static. Do not use a Global Effect for a rule whose visible identity is the selected Modifier.

## Ordinary effect projection

Choose an actual async run/combat hook whose signature matches the trigger in SPEC, then combine
only its concrete Player/Creature/Card/choice-context parameters with
`reference/effect-primitives.md`. The mutable Modifier supplies identity and run lifetime, not an
automatic Player, target, Card source, or `PlayerChoiceContext`. `AfterRunCreated` and
`AfterRunLoaded` are synchronous setup/restoration callbacks and cannot run awaited ordinary
effects; a Neow option uses its own awaited function and world-transaction boundary. Block with
the exact missing input rather than moving the effect into setup or a process listener.

## Proof matrix

Use the real custom-run/daily selection host and the resulting run:

1. assert the registered polarity, deterministic placement, exact localization, icon fallback,
   and selection state;
2. select one member of an exclusivity group and assert all other group members are unticked;
3. start a new run and assert the exact mutable Modifier identity, `AfterRunCreated` behavior,
   optional deck clear, and effect/neutral cases;
4. save and reload, assert serialized properties and `AfterRunLoaded` restoration without replaying
   new-run-only mutations;
5. exercise any selected Neow option through the real Event and await its complete outcome; and
6. assert no effect in a run where the Modifier is absent. Headed review owns list layout, color,
   icon framing, controller selection, and Neow presentation.

The registration/lifecycle compile probe is framework evidence only. No custom Modifier is yet
game-observed by M8.8.
