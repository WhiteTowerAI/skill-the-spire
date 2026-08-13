"""Stage corpora used by product authoring tests.

The implementation work order delegates surface-specific technical knowledge to
the co-located surface pages, so tests that protect an authorable capability read
the stage page plus those owners. This helper does not add a process-policy page.
"""
from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
MODMAKER_DIR = SKILLS_DIR / "modmaker"
STS2_API_DIR = SKILLS_DIR / "sts2-api"
SURFACES_DIR = MODMAKER_DIR / "surfaces"

# A stage's corpus = its own page + every surface page it delegates to.
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
    """Full corpus for one pipeline stage: its page and surface owners."""
    return join(stage_paths(name))


def stage_paths(name: str) -> tuple[Path, ...]:
    """The exact files making up a stage corpus (for per-file assertions)."""
    return _STAGE_PAGES[name] + surface_pages()


def with_invariants(*pages: Path) -> str:
    """Backward-compatible helper for tests that only need the named pages."""
    return join(tuple(pages))


def surface(element: str) -> str:
    """One element's surface page by slug, e.g. `card`."""
    return read(SURFACES_DIR / f"{element}.md")


def surface_names() -> tuple[str, ...]:
    return tuple(p.stem for p in surface_pages())
