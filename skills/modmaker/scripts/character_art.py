#!/usr/bin/env python3
"""Shared contract for the current static Character art slots."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


AlphaPolicy = Literal["opaque", "transparent"]
FitMode = Literal["cover", "contain"]


class CharacterArtValidationError(ValueError):
    """Raised when Character art metadata or normalized outputs are invalid."""


@dataclass(frozen=True)
class CharacterArtSlot:
    """One runtime-facing asset slot in a Character art bundle."""

    name: str
    spec: str
    output_path: str
    size: tuple[int, int]
    alpha: AlphaPolicy
    required: bool
    fallback: str
    consumer: str
    reference_family: str
    fit: FitMode
    verified: bool


@dataclass(frozen=True)
class CharacterArtBundle:
    """The current Character art inventory and its generation metadata.

    ``required`` means required only when a Mod selects custom Character art. The
    Character Foundation itself still has a valid template fallback for every slot.
    """

    slots: tuple[CharacterArtSlot, ...]
    identity_reference_required: bool = True

    def __post_init__(self) -> None:
        names: set[str] = set()
        paths: set[str] = set()
        for slot in self.slots:
            if not slot.name or slot.name in names:
                raise CharacterArtValidationError(f"duplicate or empty Character slot name: {slot.name!r}")
            if not slot.spec or not slot.output_path or not slot.fallback or not slot.consumer:
                raise CharacterArtValidationError(f"Character slot {slot.name!r} has incomplete metadata")
            if slot.output_path in paths:
                raise CharacterArtValidationError(
                    f"Character slots share output path {slot.output_path!r}"
                )
            output = Path(slot.output_path)
            if output.is_absolute() or ".." in output.parts or output.suffix.lower() != ".png":
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has unsafe output path {slot.output_path!r}"
                )
            if len(slot.size) != 2 or any(value <= 0 for value in slot.size):
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has invalid size {slot.size!r}"
                )
            names.add(slot.name)
            paths.add(slot.output_path)

        specs = self.specs
        for spec in specs:
            members = [slot for slot in self.slots if slot.spec == spec]
            first = members[0]
            if any(
                (slot.size, slot.alpha, slot.reference_family, slot.fit, slot.verified)
                != (first.size, first.alpha, first.reference_family, first.fit, first.verified)
                for slot in members[1:]
            ):
                raise CharacterArtValidationError(
                    f"Character spec {spec!r} has inconsistent slot metadata"
                )

    @property
    def specs(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(slot.spec for slot in self.slots))

    def sprite_specs(self) -> dict[str, dict]:
        """Return the legacy normalizer shape without duplicating Character metadata."""
        result: dict[str, dict] = {}
        for spec in self.specs:
            slot = next(item for item in self.slots if item.spec == spec)
            result[spec] = {
                "sub_path": "charui",
                "extra_sub_paths": [],
                "size": slot.size,
                "verified": slot.verified,
                "fit": slot.fit,
                "chroma": slot.alpha == "transparent",
            }
        return result

    def reference_families(self) -> dict[str, str]:
        return {spec: next(slot for slot in self.slots if slot.spec == spec).reference_family
                for spec in self.specs}

    def requires_identity_reference(self, spec: str) -> bool:
        """Require identity continuity for Character assets after selection bootstrap."""
        return spec in self.specs and spec != "character_select"

    def validate_identity_reference(
        self,
        spec: str,
        identity_reference: Path | None,
    ) -> Path | None:
        if identity_reference is None:
            if self.requires_identity_reference(spec):
                raise CharacterArtValidationError(
                    f"Character spec {spec!r} requires --identity-reference after selection bootstrap"
                )
            return None
        if spec not in self.specs:
            raise CharacterArtValidationError(
                "--identity-reference is only valid for Character art specs"
            )
        resolved = identity_reference.resolve()
        if not _readable_image(resolved):
            raise CharacterArtValidationError(
                f"Character identity reference is not a readable image: {resolved}"
            )
        return resolved

    def validate_outputs(
        self,
        images_root: Path,
        identity_reference: Path | None = None,
    ) -> tuple[Path, ...]:
        """Validate the canonical identity image and every present required output."""
        errors: list[str] = []
        if self.identity_reference_required:
            if identity_reference is None:
                errors.append("canonical identity reference is required")
            elif not _readable_image(identity_reference):
                errors.append(f"canonical identity reference is not a readable image: {identity_reference}")

        checked: list[Path] = []
        for slot in self.slots:
            path = images_root / slot.output_path
            if not path.is_file():
                if slot.required:
                    errors.append(f"missing required {slot.name}: {path}")
                continue
            checked.append(path)
            try:
                from PIL import Image

                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.size != slot.size:
                        errors.append(
                            f"{slot.name} has size {image.size}, expected {slot.size}: {path}"
                        )
                    alpha_min, _alpha_max = image.convert("RGBA").getchannel("A").getextrema()
                    if slot.alpha == "opaque" and alpha_min != 255:
                        errors.append(f"{slot.name} must be opaque: {path}")
                    if slot.alpha == "transparent" and alpha_min == 255:
                        errors.append(f"{slot.name} has no transparent pixels: {path}")
            except (OSError, ValueError, SyntaxError) as exc:
                errors.append(f"{slot.name} is not a readable PNG: {path} ({exc})")

        if errors:
            raise CharacterArtValidationError("\n".join(errors))
        return tuple(checked)

    def render_review(
        self,
        images_root: Path,
        identity_reference: Path,
        output_dir: Path,
    ) -> tuple[Path, Path]:
        """Write a labeled contact sheet and a deterministic five-layer preview."""
        checked = self.validate_outputs(images_root, identity_reference)
        checked_paths = set(checked)
        review_items: list[tuple[str, Path]] = [("canonical identity", identity_reference)]
        for slot in self.slots:
            path = images_root / slot.output_path
            if path in checked_paths:
                review_items.append((slot.name, path))

        from PIL import Image, ImageDraw, ImageFont, ImageOps

        output_dir.mkdir(parents=True, exist_ok=True)
        cell_size = (300, 280)
        columns = 4
        rows = (len(review_items) + columns - 1) // columns
        sheet = Image.new("RGB", (cell_size[0] * columns, cell_size[1] * rows), "#20252b")
        font = ImageFont.load_default()
        for index, (label, path) in enumerate(review_items):
            with Image.open(path) as source:
                image = source.convert("RGBA")
            x = (index % columns) * cell_size[0]
            y = (index // columns) * cell_size[1]
            tile = _checkerboard((cell_size[0] - 20, cell_size[1] - 48))
            preview = ImageOps.contain(image, tile.size, Image.Resampling.LANCZOS)
            tile.alpha_composite(preview, ((tile.width - preview.width) // 2, 4))
            sheet.paste(tile.convert("RGB"), (x + 10, y + 34))
            ImageDraw.Draw(sheet).text((x + 10, y + 10), label, fill="white", font=font)

        contact_path = output_dir / "character_art_contact_sheet.png"
        sheet.save(contact_path, "PNG")

        energy_slots = [
            slot
            for slot in self.slots
            if slot.spec == "character_energy"
        ]
        composite = Image.new("RGBA", energy_slots[0].size, (0, 0, 0, 0))
        for slot in energy_slots:
            path = images_root / slot.output_path
            with Image.open(path) as layer:
                composite = Image.alpha_composite(composite, layer.convert("RGBA"))
        composite_path = output_dir / "character_energy_composite.png"
        composite.save(composite_path, "PNG")
        return contact_path, composite_path


def _checkerboard(size: tuple[int, int], tile: int = 16) -> "Image.Image":
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", size, "#d5d8dc")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#aeb4bb")
    return image


def _readable_image(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.verify()
    except (OSError, ValueError, SyntaxError):
        return False
    return True


_PROFILE_FALLBACK = "RitsuLib resolved CharacterAssetProfile fallback"
_UNPROMOTED_FALLBACK = "template locked/map fallback"


CHARACTER_ART_BUNDLE = CharacterArtBundle(
    slots=(
        CharacterArtSlot(
            "selection_portrait", "character_select", "charui/select.png", (132, 195),
            "opaque", True, _PROFILE_FALLBACK, "NCharacterSelectButton.%Icon and selected panel",
            "character_select", "cover", True,
        ),
        CharacterArtSlot(
            "locked_selection_portrait", "character_select_locked", "charui/select_locked.png", (132, 195),
            "opaque", False, _UNPROMOTED_FALLBACK, "locked character-select view",
            "character_select", "cover", False,
        ),
        CharacterArtSlot(
            "top_panel_icon", "character_icon", "charui/icon.png", (88, 88),
            "transparent", True, _PROFILE_FALLBACK, "NRun.GlobalUi.TopBar.Portrait",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "map_marker", "character_map_marker", "charui/map_marker.png", (49, 64),
            "transparent", False, _UNPROMOTED_FALLBACK, "run-map Character marker",
            "character_icon", "contain", False,
        ),
        CharacterArtSlot(
            "selection_background", "character_background", "charui/background.png", (1920, 1200),
            "opaque", True, _PROFILE_FALLBACK, "character-select background",
            "character_select", "cover", True,
        ),
        CharacterArtSlot(
            "combat_body", "character_combat", "charui/combat.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "player NCreature.Visuals",
            "character_combat", "contain", True,
        ),
        CharacterArtSlot(
            "rest_body", "character_rest", "charui/rest.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "NRestSiteCharacter",
            "character_rest", "contain", True,
        ),
        CharacterArtSlot(
            "merchant_body", "character_merchant", "charui/merchant.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "NMerchantCharacter",
            "character_combat", "contain", True,
        ),
        CharacterArtSlot(
            "full_energy_layer_1", "character_energy", "charui/orb_layer_1.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer1",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "full_energy_layer_2", "character_energy", "charui/orb_layer_2.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer2",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "full_energy_layer_3", "character_energy", "charui/orb_layer_3.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer3",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "full_energy_layer_4", "character_energy", "charui/orb_layer_4.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer4",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "full_energy_layer_5", "character_energy", "charui/orb_layer_5.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer5",
            "character_icon", "contain", True,
        ),
        CharacterArtSlot(
            "compact_energy_icon", "character_energy_text", "charui/energy_text.png", (24, 24),
            "transparent", True, _PROFILE_FALLBACK, "NCard.EnergyIcon",
            "character_icon", "contain", True,
        ),
    )
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Review a normalized Character art bundle.")
    parser.add_argument("--images-root", required=True)
    parser.add_argument("--identity-reference", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    try:
        contact, composite = CHARACTER_ART_BUNDLE.render_review(
            Path(args.images_root), Path(args.identity_reference), Path(args.out_dir)
        )
    except CharacterArtValidationError as exc:
        parser.error(str(exc))
    print(f"[character_art] contact sheet: {contact}")
    print(f"[character_art] energy composite: {composite}")


if __name__ == "__main__":
    main()
