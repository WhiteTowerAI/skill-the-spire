from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import capability_preflight as preflight  # noqa: E402


EMBER_STEP_SPEC = """# SPEC - Ember Step

## Card

- Create a shared Common Attack named Ember Step with logical id `ember_step`.
- Cost 1 Energy. On play, target one enemy, deal 9 Damage, then move normally to Discard.
- Upgrade changes Damage from 9 to 13.
- English: `Deal {Damage} damage.`
- Simplified Chinese: `造成 {Damage} 点伤害。`

## Implementation

- Support: `recipes/card.md`

## Autotest

- `CombatPlayer`: add the real Card, play it against a live enemy, wait for queued commands,
  assert exact HP loss after native modifiers and assert the Card is in Discard.
"""


COMPOSED_CARD_SPEC = """# SPEC - Echoing Edge

## Card

- Create a Card whose attached Echo capability has a saved bounded charge count.
- On the owning Card's next successful play, run before its normal OnPlay, make that play free,
  add 1 Damage to each hit from that Card, then remove the capability even if its effect throws.
- Other Cards, rejected plays, later plays, and the next combat remain unchanged.
- Carry the capability to a transformed replacement only when the replacement is an Attack.

## Implementation

- Support: `recipes/card.md`
- Support: `reference/model-capabilities.md`
- Support: `reference/lifecycle-state-rng.md`
- Support: `reference/shared-effect-hooks.md`
- Support: `reference/card-play-lifecycle.md`

## Autotest

- `CombatPlayer`: attach the real capability, drive a rejected play and an unrelated Card first,
  then play the owner; assert callback order, no resource spend, exact per-hit damage, result pile,
  removal despite completion, neutral second play, transform copy/drop identity, and combat reset.
"""


MULTI_SURFACE_SPEC = """# SPEC - Multi-Surface Composition

## Affliction

- Create a stackable combat Affliction on Skills; apply amount 2, run its attached play effect,
  and clear it before combat ends.

## Modifier

- Create a good custom-run Modifier after the built-in segment and make it mutually exclusive
  with a bad Modifier. Keep new-run initialization separate from load restoration.

## Global Effect

- Create one Combat Global Effect that can deny a guarded draw and remains neutral otherwise.

## Rest Site

- Create a standalone once-per-run free option that keeps the other native options.

## Implementation

- Support: `recipes/affliction.md`
- Support: `recipes/modifier.md`
- Support: `recipes/global-effect.md`
- Support: `recipes/rest-site.md`
- Support: `reference/rest-site-options.md`
- Hook: should_draw | surface: global-effect-combat | shape: value | route: reference/model-hook-participation.md

## Autotest

- Drive real combat Card attachment/play/clear, real modifier selection and reload, real combat
  hook delivery/reset, and the complete native Rest Site state matrix.
"""


WORLD_CONTENT_SPEC = """# SPEC - World Content

## Act

- Create a complete first-slot singleplayer Act entered from a weighted pool. Give the existing
  chapter weight 1 and the new Act weight 2. Include nonempty weak, regular, elite, and Boss
  Encounter groups, ordinary Events, and the scoped Ancient below.

## Ancient

- Create one Act-scoped Ancient with a deterministic initial option set, first-visit and ANY
  dialogue, and one option that finishes through native choice history.

## Implementation

- Support: `recipes/act.md`
- Support: `recipes/ancient.md`

## Autotest

- Enter the Act through its real singleplayer resolver, reach every required room family, then
  drive the real Ancient room and assert options, dialogue, outcome, and choice history.
"""


REWARD_CARD_PILE_SPEC = """# SPEC - Reward and Card Pile

## Reward

- Register a custom pending reward with a typed amount payload. Refuse the claim without mutation
  when the amount is zero; otherwise grant the exact outcome. Offer two children as choose-one and
  also insert one reward into the current combat's end rewards.

## Card Pile

- Register a run-persistent top-bar pile with deck-like inspection. Move the exact Card instance
  with native awaited movement and preserve contents across save/load.

## Implementation

- Support: `recipes/reward.md`
- Support: `recipes/card-pile.md`
- Support: `reference/card-piles.md`

## Autotest

- Drive the real rewards screen claim/refusal/reload and the real run pile movement/UI/reload,
  asserting exact post-state and instance identity.
"""


RUNTIME_UI_SPEC = """# SPEC - Runtime Codex

## Runtime UI

- Register one top-bar button and Ctrl+Shift+M runtime hotkey that toggle a local-only Capstone
  screen. The per-frame button state is pure and safe before a Player exists.
- Show a tracked loading Toast, then update and close it.
- Present stable entries through a grid Catalog with a drawer, one fixed pre-tree filter, and
  deterministic local search expansions.
- Attach the owning coordinator to the public top bar, dispose every registration with that
  owner, and use only Mod-scoped shell tokens in this UI.

## Implementation

- Support: `recipes/runtime-ui.md`
- Support: `reference/lifecycle-state-rng.md`

## Autotest

- Drive the real top bar, input router, Capstone, Toast, Catalog, and attachment; assert exact
  open/close, selection, search, action, suppression, disposal, and cleanup state, then perform
  separate headed mouse/controller/layout review.
"""


INTEGRATED_OWNER_SPEC = """# SPEC - Archive Delivery

## Event and Reward

- A real Event offers one pending custom Reward. Refusal changes nothing. A successful claim
  creates one exact Card and continues only after its awaited outcome completes.

## Card Pile

- Move that same Card instance into a run-persistent archive pile through the native awaited pile
  command. Preserve identity and contents across the selected run save/load boundary.

## Runtime UI

- A local top-bar entry shows the archive count and opens a searchable Catalog of the pile's live
  Cards. Providers are null-player safe; the coordinator owns and disposes every handle.

## Implementation

- Support: `recipes/event.md`
- Support: `recipes/reward.md`
- Support: `recipes/card-pile.md`
- Support: `reference/card-piles.md`
- Support: `recipes/runtime-ui.md`
- Support: `reference/lifecycle-state-rng.md`

## Autotest

- Drive the real Event and reward screen, assert refusal is neutral, claim once, await the exact
  Card result, move that instance into the real run pile, round-trip it through run save/load, then
  drive the real top-bar/Catalog host and assert count, identity, search, close, and cleanup.
"""


ACTIVE_OWNER_EFFECT_SPEC = """# SPEC - Charged Strike

## Card

- Create a targeted Attack. On play, deal 8 Damage, apply 2 Weak, draw 1 Card, then gain 1 Energy
  in that exact order. If the selected target is absent, authoring stops before emitting effects.

## Implementation

- Support: `recipes/card.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `CombatPlayer`: play the real Card, assert ordered target damage/Weak/draw/Energy post-state and
  its normal result pile after queued commands complete.
"""


ATTACHED_OWNER_EFFECT_SPEC = """# SPEC - Guarded Script

## Enchantment

- Attach an Enchantment to one playable Card. After that host Card's own OnPlay body, gain 5 Block
  using the same play context. An unenchanted Card and a rejected attachment remain unchanged.

## Implementation

- Support: `recipes/enchantment.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `CombatPlayer`: attach to the exact Card, play it, assert host-body then attached-Block order,
  and assert the unenchanted and rejected-host neutral cases.
"""


BLOCKING_WORLD_EFFECT_SPEC = """# SPEC - Curator's Gift

## Event

- One enabled option gains 25 Gold, creates one known Card in the owner's run, adds that exact
  Card to Deck, then obtains one known Relic. Finish the Event only after all awaited results
  complete. A failed preflight leaves the Event and run unchanged.

## Implementation

- Support: `recipes/event.md`
- Support: `reference/event-outcomes.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `MapNode`: click the real option, assert ordered Gold/Card/Relic state and exact Card identity,
  then assert the result page appears only after acquisition completion.
"""


SCENARIOS = {
    "simple card": (EMBER_STEP_SPEC, (1, 0, False)),
    "composed card": (COMPOSED_CARD_SPEC, (5, 0, False)),
    "multi surface": (MULTI_SURFACE_SPEC, (5, 1, False)),
    "world content": (WORLD_CONTENT_SPEC, (2, 0, False)),
    "reward and card pile": (REWARD_CARD_PILE_SPEC, (3, 0, False)),
    "runtime ui": (RUNTIME_UI_SPEC, (2, 0, False)),
    "integrated owners": (INTEGRATED_OWNER_SPEC, (6, 0, False)),
    "active owner effects": (ACTIVE_OWNER_EFFECT_SPEC, (2, 0, False)),
    "attached owner effects": (ATTACHED_OWNER_EFFECT_SPEC, (2, 0, False)),
    "blocking world effects": (BLOCKING_WORLD_EFFECT_SPEC, (3, 0, False)),
}


class RequirementToAuthoringTests(unittest.TestCase):
    def test_realistic_specs_pass_capability_preflight(self) -> None:
        for name, (spec, expected) in SCENARIOS.items():
            with self.subTest(scenario=name):
                self.assertEqual(expected, preflight.validate_spec_text(spec))


if __name__ == "__main__":
    unittest.main()
