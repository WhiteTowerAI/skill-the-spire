# Surface: Ancient

Use this surface for a new Ancient encounter with its own identity, dialogue, option pool,
outcomes, and map/run-history presentation. Editing an existing vanilla Ancient remains a
different operation owned by `reference/vanilla-ancient-overrides.md`.

## DESIGN and SPEC vocabulary

Settle and write:

- placement: Shared Ancient or scoped to one or more exact Acts, never both for the same identity;
- `IsValidForAct` rule, including the neutral rejected Act;
- every possible option, the exact initial subset/ordering rule, enabled/locked state, typed Hover
  Tips, costs, ordered outcomes, page transitions, and terminal `Done()` behavior;
- deterministic selection from the mutable event's supplied `Rng`; preview, disabled, or rejected
  paths consume no random value and mutate nothing;
- first-visit-ever, exact Character, and `ANY` dialogue groups; visit index, repeat mode, speaker,
  prompt, optional line SFX, dialogue color, and any `ANY` blacklist;
- English and Simplified Chinese title, epithet, page/option text, dialogue, and SmartFormat
  variable parity; stable page/option names are localization and run-history identities;
- layout/portrait/background/VFX, map and run-history icon pairs, optional procedural stage, ambient
  BGM, and explicit fallback. Placeholder mode is the checked Darv fallback profile in
  `recipes/ancient.md` § Required explicit fallback, never empty profiles; and
- a real Ancient `MapNode` SelfTest (`reference/selftest-harness.md` § The Ancient `MapNode`
  scenario) plus headed dialogue/options/icons/controller proof.

Ancient option bodies may use the same bounded public Event outcome routes, but a new Ancient is
not an ordinary Event and must not be lowered through `recipes/event.md`. Settings, Progression,
Telemetry, Multiplayer, post-run Badge, and Update Check integrations remain deferred.

## Text style

Write every player-facing string in the default style of `reference/vanilla-text-style.md`:
the title and epithet stay plain; option descriptions follow the Event option row (`[red]`
costs, `[green]` gains, `[blue]` counts, `[gold]` terms and obtained Relic names); dialogue
follows `reference/ancient-dialogue.md` and keeps its spoken voice.

## Authoring route

- Read `recipes/ancient.md` for `ModAncientEventTemplate`, Shared/Act-scoped registration,
  localization-driven dialogue, option lifecycle, assets, and proof.
- Read the selected Event outcome/presentation references only for the exact option behavior.
  `reference/vanilla-ancient-overrides.md` is not a shortcut for a new model.
- Read `reference/lifecycle-state-rng.md` when state crosses callbacks or an option is randomized.

## Ordinary effect projection

An `EventOption` `Func<Task>` runs on the mutable Ancient and binds its owner Player through
`Owner`. Use `reference/effect-primitives.md` for immediate child effects only after all option
eligibility/cost checks pass. The callback owns blocking completion: await every command, inspect
nullable/result outcomes, then call `SetEventState(...)` or `Done()` and return the completed
Task. It has no generic combat target/context, so combat-pile, Energy/Stars, Orb, draw, or targeted
Creature effects block unless a selected specialized Ancient/Event route actually supplies them.

## Proof matrix

Drive the real Ancient room:

1. assert exactly one registered identity and inclusion in every accepted Act pool but exclusion
   from a rejected Act;
2. assert `AllPossibleOptions`, the generated initial subset/order, enabled/locked states, and no
   duplicate text keys;
3. select every reachable option/branch through its real UI path, wait for queued commands, and
   assert exact cost/outcome/page/history state plus a no-mutation rejection case;
4. assert first-visit-ever, Character-specific, `ANY`, repeat/visit routing, speaker order,
   prompts, optional SFX paths, and blacklist behavior from the real localization consumer;
5. leave/re-enter or save/load as selected and assert no stale options, repeated reward, or
   duplicate dialogue registration; and
6. headed review checks name/epithet, portrait/stage, map and run-history icons, speech direction/
   color, option layout, mouse/controller progression, ambient audio, and cleanup.

Build, direct `GenerateInitialOptions()` calls, and localization parsing are not game observation.
The new Ancient remains game-unobserved until its exact room and headed matrix run.
