"""Stage prose corpora for shipped-skill contract tests.

These tests pin exact shipped wording so documentation cannot silently drift.
That is the point and it stays. What they must NOT pin is which *file* a
sentence lives in — otherwise the layout is frozen and per-surface content
cannot be co-located with its own proof matrix and driver body.

So a stage owns a corpus, not a file: its main stage page plus the per-surface
pages it dispatches to. `assertIn(...)` against the corpus still fails on real
drift (the words changed or vanished) but passes when content is relocated
within the stage's own file set.

Exact strings are preserved verbatim; pages are joined with a blank line so no
assertion can accidentally match across a page boundary.
"""
from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
MODMAKER_DIR = SKILLS_DIR / "modmaker"
STS2_API_DIR = SKILLS_DIR / "sts2-api"
SURFACES_DIR = MODMAKER_DIR / "surfaces"

# A stage's corpus = its own page + every page it delegates to. `surfaces/`
# holds one page per element type, each carrying that element's SPEC envelope,
# author driver body, and proof matrix together.
_STAGE_PAGES: dict[str, tuple[Path, ...]] = {
    "spec": (MODMAKER_DIR / "spec.md",),
    "author": (MODMAKER_DIR / "author.md",),
    "verify": (MODMAKER_DIR / "verify.md",),
}


def surface_pages() -> tuple[Path, ...]:
    """Every per-element surface page, in stable order."""
    if not SURFACES_DIR.is_dir():
        return ()
    return tuple(sorted(SURFACES_DIR.glob("*.md")))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def join(paths: tuple[Path, ...]) -> str:
    return "\n\n".join(read(p) for p in paths)


def stage(name: str) -> str:
    """Full corpus for one pipeline stage: its page plus the surface pages."""
    pages = _STAGE_PAGES[name] + surface_pages()
    return join(pages)


def stage_paths(name: str) -> tuple[Path, ...]:
    """The exact files making up a stage corpus (for per-file assertions)."""
    return _STAGE_PAGES[name] + surface_pages()


def surface(element: str) -> str:
    """One element's surface page by slug, e.g. `card`."""
    return read(SURFACES_DIR / f"{element}.md")


def surface_names() -> tuple[str, ...]:
    return tuple(p.stem for p in surface_pages())
