"""Structural cross-check for the co-located per-element surface pages.

M8.0 change 1 puts each element's SPEC envelope, author driver body, and proof
matrix in one `surfaces/<element>.md` page. The Card pilot showed why: when a
proof demands a value the envelope has no field to declare, nothing in the
workflow surfaces the contradiction.

Co-location makes that cross-check possible in a single read. It does not perform
it. These tests perform the part that is mechanically decidable:

1. every surface page is structurally complete (or explicitly states it owns no
   envelope), so a new page cannot silently ship without a proof matrix;
2. every `surfaces/<x>.md` cross-reference resolves to a real page and a real
   heading on it, so a dedup pointer cannot rot into a dangling one; and
3. each mandatory envelope field established by the ten-surface cross-check is
   paired with the proof case that observes it.

Case 3 is the class the pilot found. A Relic that declares `cadence` but whose
proof never advances past the boundary passes its own state assertion while the
guard that *is* its identity is deleted. Pairing them here means the field and
its case cannot drift apart again.

The findings behind these pairs, including the mismatches left unfixed, are in
`games/sts2/tests/m80-surface-cross-check.md`.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import skill_prose


REQUIRED_SECTIONS = ("## Author the element class", "## Proof matrix")

# Surfaces that own a full `## SPEC envelope`. Keyword and enchantment are
# declared inside their host Card's `content:` block instead, so they carry an
# explicit no-envelope statement rather than a block of their own.
HOST_SCOPED = {"keyword", "enchantment"}

EXPECTED_SURFACES = {
    "card",
    "character",
    "enchantment",
    "event",
    "keyword",
    "monster",
    "orb",
    "potion",
    "power",
    "relic",
}

# field the envelope must declare -> the proof case that observes it.
# Each pair is a mismatch this cross-check either found or confirmed closed.
FIELD_PROOF_PAIRS: dict[str, tuple[tuple[str, str], ...]] = {
    "relic": (
        ("cadence:", "Assert the cadence."),
        ("keyword tips:", "Assert each declared keyword tip resolves."),
        ("displayed values:", "Assert each declared displayed value renders live."),
    ),
    "power": (
        ("lifetime:", "Assert the declared lifetime."),
        ("amount domain:", "Assert the declared amount domain at its bounds."),
    ),
    "potion": (
        ("usage:", "Assert the declared `usage`"),
        ("target:", "Assert the declared target, not the implemented one."),
        ("keyword tips:", "Assert each declared keyword tip resolves."),
        ("displayed values:", "Assert each declared displayed value renders live."),
    ),
    "orb": (
        ("passive:", "Prove all three behaviors, not one."),
        ("evoke:", "Fire the passive through the real per-turn path."),
        ("smartDescription:", "smartDescription"),
        ("eviction:", "evokes"),
    ),
    "enchantment": (
        ("host restriction:", "Assert the host restriction by attempting an illegal host."),
        ("stacking:", "already-enchanted"),
    ),
    "keyword": (
        ("behavior owner:", "Assert the named behavior in the host."),
    ),
    "monster": (
        ("moves:", "every advertised move id executes in the declared order"),
        ("branches:", "Drive every branch through both outcomes"),
        ("loop:", "prove it loops rather than terminating"),
        ("group:", "Assert the spawned roster and HP."),
    ),
    "event": (
        ("availability:", "Drive each gated option both ways."),
        ("options:", "Assert the option set before choosing."),
    ),
    "character": (
        ("pool cards:", "Play every behavioral pool card."),
    ),
    "card": (
        ("engine-composed text:", "result pile"),
    ),
}


class SurfaceStructureTests(unittest.TestCase):
    def test_expected_surfaces_are_present(self) -> None:
        self.assertEqual(set(skill_prose.surface_names()), EXPECTED_SURFACES)

    def test_every_surface_is_structurally_complete(self) -> None:
        for slug in skill_prose.surface_names():
            page = skill_prose.surface(slug)
            with self.subTest(surface=slug):
                for section in REQUIRED_SECTIONS:
                    self.assertIn(
                        section,
                        page,
                        f"surfaces/{slug}.md is missing '{section}'",
                    )
                if slug in HOST_SCOPED:
                    self.assertIn(
                        "## No SPEC envelope of its own",
                        page,
                        f"surfaces/{slug}.md must state that it owns no envelope",
                    )
                    self.assertNotIn("## SPEC envelope", page)
                else:
                    self.assertIn(
                        "## SPEC envelope",
                        page,
                        f"surfaces/{slug}.md is missing '## SPEC envelope'",
                    )

    def test_every_surface_names_the_stages_that_read_it(self) -> None:
        for slug in skill_prose.surface_names():
            page = skill_prose.surface(slug)
            with self.subTest(surface=slug):
                for stage in ("spec.md", "author.md", "verify.md"):
                    self.assertIn(stage, page)


class SurfaceReferenceTests(unittest.TestCase):
    """A dedup pointer must resolve, or the stage file lost its content."""

    @classmethod
    def setUpClass(cls) -> None:
        modmaker = skill_prose.MODMAKER_DIR
        cls.pages = {
            path.relative_to(modmaker).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(modmaker.rglob("*.md"))
        }

    def test_surface_references_resolve_to_real_pages(self) -> None:
        known = set(skill_prose.surface_names())
        for name, text in self.pages.items():
            for slug in set(re.findall(r"surfaces/([a-z-]+)\.md", text)):
                with self.subTest(page=name, target=slug):
                    self.assertIn(slug, known, f"{name} points at missing surfaces/{slug}.md")

    def test_section_pointers_resolve_to_real_headings(self) -> None:
        pattern = re.compile(r"`surfaces/([a-z-]+)\.md`\s*§\s*([^.\n,;]+)")
        checked = 0
        for name, text in self.pages.items():
            for slug, section in pattern.findall(text):
                target = skill_prose.surface(slug)
                heading = section.strip()
                with self.subTest(page=name, target=f"{slug}#{heading}"):
                    self.assertIsNotNone(
                        re.search(
                            rf"^#+\s*{re.escape(heading)}\s*$",
                            target,
                            re.MULTILINE,
                        ),
                        f"{name} points at '{heading}' which surfaces/{slug}.md lacks",
                    )
                checked += 1
        self.assertGreater(checked, 0, "no section pointers found to verify")

    def test_errors_catalog_pointers_resolve_to_real_sections(self) -> None:
        """M8.0 change 3: a stage that delegates its diagnostics must land somewhere real.

        Change 3 moves diagnostic scars into `errors.md` and leaves the main path pointing at
        it. That trades inline detail for a pointer, which is only an improvement while the
        pointer resolves. It did not always: `verify.md` pointed at an `errors.md`
        "Verification harness" section that has never existed, and no check caught it.
        """
        errors = (skill_prose.STS2_API_DIR / "errors.md").read_text(encoding="utf-8")
        sections = set(re.findall(r"^##\s+(.+?)\s*$", errors, re.MULTILINE))
        self.assertIn("Verification", sections, "errors.md lost its section structure")

        pattern = re.compile(r"errors\.md`?\s*§\s*([A-Z][A-Za-z]+(?: [A-Z][a-z]+)*)")
        checked = 0
        for name, text in self.pages.items():
            for section in pattern.findall(text):
                with self.subTest(page=name, target=section):
                    self.assertIn(
                        section,
                        sections,
                        f"{name} points at errors.md § {section}, which does not exist",
                    )
                checked += 1
        self.assertGreater(checked, 0, "no errors.md section pointers found to verify")

    def test_delegating_stages_do_not_keep_their_own_cause_and_fix_lists(self) -> None:
        """The two homes split by when you need them; a diagnostic in both drifts.

        `quirks.md` holds rules followed before anything breaks; `errors.md` holds signatures
        matched after. Before change 3, `build.md` restated four profile diagnostics that
        `errors.md` already owned, and `quirks.md` restated MSB1008 and CS8602 by error code.
        """
        build = self.pages["build.md"]
        self.assertNotIn("## Failure classes", build)
        self.assertIn("errors.md", build)

        quirks = self.pages["quirks.md"]
        for code in ("MSB1008", "CS8602"):
            with self.subTest(code=code):
                self.assertNotIn(
                    code,
                    quirks,
                    f"{code} is a signature errors.md owns; quirks.md states the rule instead",
                )

    def test_shipped_pack_states_support_not_which_milestone_promoted_it(self) -> None:
        """M8.0 change 4: runtime instruction says what is supported, not who shipped it.

        Two patterns are forbidden rather than every milestone id, because some ids stay
        load-bearing: `m6.7.1-public-card-overrides` is a manifest key checked against the
        catalog, `R6 scry helper complete` is a Tier 2 marker, `pre-M7.4` is a resume-
        compatibility boundary, and an evidence attribution names the run that grounded a fact.

        What must not return is a milestone standing in for a route, and — worse — an
        instruction to follow a milestone-scoped process. The pack used to tell readers to run
        reduced checks "during the M6.7 batch window" and defer the rest to its close. That
        window closed on 2026-08-04, so a reader following it would have been executing an
        expired verification policy.
        """
        pack = Path(skill_prose.SKILLS_DIR)
        offenders: list[str] = []
        for page in sorted(pack.rglob("*.md")):
            rel = page.relative_to(pack).as_posix()
            text = page.read_text(encoding="utf-8")
            for phrase in ("batch window", "consolidated M6.7", "At closure,"):
                if phrase in text:
                    offenders.append(f"{rel}: expired-process instruction {phrase!r}")
            for heading in re.findall(r"^#+\s+(.*)$", text, re.MULTILINE):
                if re.search(r"\b[MR]\d+(?:\.\d+)*\b", heading) and "20" not in heading:
                    offenders.append(f"{rel}: milestone id in heading {heading!r}")
        self.assertEqual([], offenders, "\n".join(offenders))

    def test_stage_pages_delegate_rather_than_duplicate(self) -> None:
        """Author/verify must not re-inline a body the surface page owns."""
        author = self.pages["author.md"]
        verify = self.pages["verify.md"]
        for surface in ("relic", "potion", "power", "orb", "keyword", "enchantment"):
            with self.subTest(surface=surface):
                self.assertIn(f"`surfaces/{surface}.md`", author)
        for pointer in ("surfaces/card.md", "surfaces/character.md", "surfaces/event.md"):
            self.assertIn(pointer, verify)


class EnvelopeProofPairingTests(unittest.TestCase):
    """The core check: a mandatory field and the case that observes it."""

    def envelope_and_proof(self, slug: str) -> tuple[str, str]:
        page = skill_prose.surface(slug)
        proof = re.search(r"## Proof matrix\n(.*?)(?=\n## |\Z)", page, re.DOTALL)
        self.assertIsNotNone(proof, f"surfaces/{slug}.md has no proof matrix body")
        # Nested envelopes write `field:`; flat ones write `- **field**:`. Strip
        # emphasis so a pairing is stated once, not once per envelope form.
        return page.replace("**", ""), proof.group(1)

    def test_mandatory_fields_are_paired_with_their_proof_case(self) -> None:
        for slug, pairs in FIELD_PROOF_PAIRS.items():
            page, proof = self.envelope_and_proof(slug)
            for field, case in pairs:
                with self.subTest(surface=slug, field=field):
                    self.assertIn(
                        field,
                        page,
                        f"surfaces/{slug}.md declares no '{field}' for its proof to observe",
                    )
                    self.assertIn(
                        case,
                        proof,
                        f"surfaces/{slug}.md declares '{field}' but its proof matrix "
                        f"never observes it (expected {case!r})",
                    )

    def test_engine_composed_text_rule_is_stated_once_and_referenced(self) -> None:
        spec = (skill_prose.MODMAKER_DIR / "spec.md").read_text(encoding="utf-8")
        self.assertIn("Engine-composed text is not author-written text", spec)
        self.assertIn("engine-composed text:", skill_prose.surface("card"))
        for slug in ("keyword", "enchantment"):
            page = skill_prose.surface(slug)
            with self.subTest(surface=slug):
                self.assertIn("exactly **once**", page)

    def test_host_scoped_surfaces_declare_their_fields_on_the_card(self) -> None:
        """keyword/enchantment instruct host-Card fields, so Card must have them."""
        card = skill_prose.surface("card")
        for field in ("keywords:", "behavior owner:", "enchantment:", "host restriction:"):
            with self.subTest(field=field):
                self.assertIn(field, card)


if __name__ == "__main__":
    unittest.main()
