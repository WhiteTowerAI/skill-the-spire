"""Rendered skill paths in the committed payload must resolve from the citing skill's directory.

An agent reads a skill path relative to the directory of the skill that cites it, so a token
rendered to "." inside sts2api points at sts2api, not modmaker.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = REPO_ROOT / "skills"
SOURCE = REPO_ROOT / "games" / "sts2" / "skills"
SKILLS = ("modmaker", "sts2api")
TOKENS = ("MODMAKER_SKILL_DIR", "STS2API_SKILL_DIR", "GAME_TOOLS_DIR")

TOKEN_REFERENCE = re.compile(r"\$\{(" + "|".join(TOKENS) + r")\}([^\s`'\"()\[\],;]*)")
UNRENDERED_TOKEN = re.compile(r"\$\{(?:" + "|".join(TOKENS) + r")\}")
# A skill-name prefix without ../ resolves inside the citing skill, where no such directory exists.
BARE_SKILL_PATH = re.compile(r"`(?:modmaker|sts2api)/[^`]*`")


def docs(base: Path):
    for skill in SKILLS:
        root = base / skill
        for path in sorted(root.rglob("*.md")):
            if "scripts" in path.relative_to(root).parts:
                continue
            yield skill, path


def publisher_values() -> dict[str, str]:
    text = (REPO_ROOT / "publish.sh").read_text(encoding="utf-8")
    values = {}
    for token in TOKENS:
        match = re.search(rf'^{token}="([^"]*)"', text, re.MULTILINE)
        assert match, f"publish.sh does not set {token}"
        values[token] = match.group(1)
    return values


def resolvable_part(reference: str) -> str:
    """Drop trailing punctuation and any placeholder segment such as <surface>.md."""
    reference = reference.rstrip(".:")
    parts = reference.split("/")
    for index, part in enumerate(parts):
        if any(mark in part for mark in "<>*{}"):
            return "/".join(parts[:index])
    return reference


class PayloadPathTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (PAYLOAD / "modmaker" / "SKILL.md").is_file():
            self.skipTest("committed skills/ payload is not present")

    def test_token_paths_resolve_from_citing_skill(self) -> None:
        values = publisher_values()
        checked = 0
        missing = []
        for skill, path in docs(SOURCE):
            text = path.read_text(encoding="utf-8")
            for match in TOKEN_REFERENCE.finditer(text):
                rendered = values[match.group(1)] + match.group(2)
                checked += 1
                if not (PAYLOAD / skill / resolvable_part(rendered)).exists():
                    line = text.count("\n", 0, match.start()) + 1
                    source = path.relative_to(REPO_ROOT).as_posix()
                    missing.append(f"{source}:{line}: {match.group(0)} -> {rendered}")
        self.assertGreater(checked, 0)
        self.assertEqual([], missing)

    def test_no_unrendered_or_bare_skill_paths(self) -> None:
        problems = []
        for _skill, path in docs(PAYLOAD):
            text = path.read_text(encoding="utf-8")
            for pattern in (UNRENDERED_TOKEN, BARE_SKILL_PATH):
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    problems.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{line}: {match.group(0)}")
        self.assertEqual([], problems)


if __name__ == "__main__":
    unittest.main()
