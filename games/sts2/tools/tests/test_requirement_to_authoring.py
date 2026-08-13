from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = TOOLS_DIR.parent / "skills"
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


class RequirementToAuthoringTests(unittest.TestCase):
    def test_simple_card_request_reaches_an_implementable_authoring_route(self) -> None:
        self.assertEqual((1, 0, False), preflight.validate_spec_text(EMBER_STEP_SPEC))

        recipe = (SKILLS_DIR / "sts2-api" / "recipes" / "card.md").read_text(
            encoding="utf-8"
        )
        author = (SKILLS_DIR / "modmaker" / "author.md").read_text(encoding="utf-8")
        verify = (SKILLS_DIR / "modmaker" / "verify.md").read_text(encoding="utf-8")

        for implementation_ingredient in (
            "ModCardTemplate",
            ".Card<",
            "DamageVar",
            "DamageCmd.Attack",
            "UpgradeValueBy",
            "cards.json",
        ):
            self.assertIn(implementation_ingredient, recipe)

        self.assertIn("<ModName>Code/SelfTest.cs", author)
        self.assertIn("independently asserted state proof", verify)
        self.assertIn("concrete structured state assertion", verify)


if __name__ == "__main__":
    unittest.main()
