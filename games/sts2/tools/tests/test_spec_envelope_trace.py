"""A generated SPEC must be shaped like the surface it claims to be.

M8.0 mismatch 8 had two halves. `test_surface_cross_check.py` closed the first -- pairing each
mandatory envelope field with the proof case that observes it -- but only inside the shipped
pack. The second half, checking a *generated* project's `SPEC.md` against its surface envelope,
could not be done while two envelope forms were both legal: six surfaces opened with a flat
`element:` key and ad-hoc top-level fields while card and relic used the nested form, so there
was no single shape to validate against.

v2 normalizes all ten, so this check becomes possible. It is deliberately structural: sections
present, no invented top-level keys, contract line v2 or absent. It cannot tell whether a
declared value is correct -- a SPEC can pass here and still describe the wrong Mod.

The pre-v2 pass-through matters as much as the checks. A project written before this Package
resumes unchanged, the same precedent an absent coherence block (pre-M7.5) or deliverable block
(pre-M8.1) already sets.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import spec_envelope_trace as envelope  # noqa: E402


VALID_V2_CARD = """# SPEC - Ember Step

- **contract**: sts2-content-semantic/v2
- **mod id**: ember_step_mod
- **author**: Tester
- **content**:
  - name: Ember Step
  - surface: card
  - logical id: ember_step
  - kind: Attack
  - rarity: Common
- **registration**:
  - availability: shared
  - ownership: player
  - placement: any character
- **localization**:
  - fields: title=Ember Step; description=Deal {Damage} damage.
  - formatting: dynamic value placeholders
- **effects**:
  - trigger: play
  - target: one enemy
  - cost: 1
  - sequence: deal 9 damage
  - scaling: damage 9
- **state**: none
- **presentation**:
  - assets: card portrait; placeholder
  - native presentation: standard card body/preview
- **fallback**:
  - missing asset: checked template card portrait
- **proof**:
  - scenario: CombatPlayer
  - driver: play the real card against its declared target
  - invariants: target loses 9 HP; card in Discard
"""

PRE_V2_CARD = """# SPEC - Old Card

- contract: sts2-content-semantic/v1
- content: surface=card; logical id=old_card
- effects: trigger=play; target=one enemy; sequence=deal 6 damage
"""

NO_CONTRACT_LINE = """# SPEC - Ancient Project

- **mod id**: ancient
- **element**: card
- **effect**: deal 6 damage
"""


class ValidSpecTests(unittest.TestCase):
    def test_valid_v2_card_spec_passes(self) -> None:
        contract, keys = envelope.validate_spec_text(VALID_V2_CARD)
        self.assertEqual(envelope.CONTRACT_V2, contract)
        self.assertGreaterEqual(keys, len(envelope.REQUIRED_SECTIONS))

    def test_pre_v2_spec_passes_unchanged(self) -> None:
        """A v1 project resumes rather than failing; only new SPECs are written as v2."""
        contract, _ = envelope.validate_spec_text(PRE_V2_CARD)
        self.assertEqual(envelope.CONTRACT_V1, contract)

    def test_spec_with_no_contract_line_passes(self) -> None:
        contract, _ = envelope.validate_spec_text(NO_CONTRACT_LINE)
        self.assertEqual("absent", contract)


class RejectionTests(unittest.TestCase):
    def test_invented_top_level_key_fails(self) -> None:
        """The exact gap: `design_trace.py` accepted invented SPEC fields silently."""
        spoiled = VALID_V2_CARD + "- **secret sauce**: something the envelope never declared\n"
        with self.assertRaises(envelope.SpecEnvelopeError) as caught:
            envelope.validate_spec_text(spoiled)
        message = str(caught.exception)
        self.assertIn("secret sauce", message)
        self.assertIn("no surface envelope allows", message)

    def test_missing_required_section_fails(self) -> None:
        spoiled = VALID_V2_CARD.replace(
            "- **fallback**:\n  - missing asset: checked template card portrait\n", ""
        )
        with self.assertRaises(envelope.SpecEnvelopeError) as caught:
            envelope.validate_spec_text(spoiled)
        self.assertIn("missing required shared sections", str(caught.exception))
        self.assertIn("fallback", str(caught.exception))

    def test_v2_spec_without_a_surface_line_fails(self) -> None:
        spoiled = VALID_V2_CARD.replace("  - surface: card\n", "")
        with self.assertRaises(envelope.SpecEnvelopeError) as caught:
            envelope.validate_spec_text(spoiled)
        self.assertIn("no `surface:` line", str(caught.exception))

    def test_unknown_surface_fails(self) -> None:
        spoiled = VALID_V2_CARD.replace("  - surface: card\n", "  - surface: dragon\n")
        with self.assertRaises(envelope.SpecEnvelopeError) as caught:
            envelope.validate_spec_text(spoiled)
        self.assertIn("no shipped surface page", str(caught.exception))


class SurfacePageAgreementTests(unittest.TestCase):
    """Allowed keys come from the surface pages, so the two cannot disagree."""

    def test_every_surface_with_an_envelope_resolves_its_allowed_keys(self) -> None:
        root = envelope.surface_page_root()
        checked = 0
        for page in sorted(root.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            if "## SPEC envelope" not in text:
                continue  # keyword/enchantment are host-scoped and own no envelope
            surface = "enemy encounter" if page.stem == "monster" else page.stem
            with self.subTest(surface=surface):
                allowed = envelope.allowed_top_level_keys(surface)
                for section in envelope.REQUIRED_SECTIONS:
                    self.assertIn(section, allowed)
            checked += 1
        self.assertGreaterEqual(checked, 8, "expected at least eight enveloped surfaces")


class CliTests(unittest.TestCase):
    def test_cli_reports_ok_for_a_valid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "SPEC.md"
            path.write_text(VALID_V2_CARD, encoding="utf-8")
            self.assertEqual(0, envelope.main(["--spec", str(path)]))

    def test_cli_fails_for_an_invented_key(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "SPEC.md"
            path.write_text(VALID_V2_CARD + "- **invented**: x\n", encoding="utf-8")
            self.assertEqual(2, envelope.main(["--spec", str(path)]))


if __name__ == "__main__":
    unittest.main()
