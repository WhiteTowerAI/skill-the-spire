#!/usr/bin/env python3
"""Shared contract and review helpers for the static Character art bundle."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import shutil


AlphaPolicy = Literal["opaque", "transparent"]
FitMode = Literal["cover", "contain"]
ReferenceRole = Literal["bootstrap", "identity", "palette", "fallback"]
AssetOrigin = Literal["generated", "derived", "fixed_template", "fallback"]


class CharacterArtValidationError(ValueError):
    """Raised when Character art metadata or normalized outputs are invalid."""


@dataclass(frozen=True)
class VisibleFootprint:
    """Host-specific normalized content bounds, baseline, and public visual style."""

    host: str
    content_box: tuple[int, int, int, int]
    alpha_content: bool
    baseline_y: int | None = None
    minimum_fill: tuple[float, float] = (0.0, 0.0)
    visual_scale: float | None = None
    visual_position: tuple[float, float] | None = None


@dataclass(frozen=True)
class CharacterArtSlot:
    """One runtime-facing asset slot in the Character bundle."""

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
    reference_role: ReferenceRole
    asset_origin: AssetOrigin = "generated"
    generation_calls: int = 1
    template_path: str | None = None
    visible_footprint: VisibleFootprint | None = None


@dataclass(frozen=True)
class CharacterArtBundle:
    """The one source of truth for Character asset metadata and reference routing."""

    slots: tuple[CharacterArtSlot, ...]
    identity_slot: str = "selection_portrait"

    def __post_init__(self) -> None:
        names: set[str] = set()
        paths: set[str] = set()
        for slot in self.slots:
            if not slot.name or slot.name in names:
                raise CharacterArtValidationError(
                    f"duplicate or empty Character slot name: {slot.name!r}"
                )
            if not slot.spec or not slot.output_path:
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has incomplete path metadata"
                )
            if not slot.fallback or not slot.consumer:
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has incomplete fallback/consumer metadata"
                )
            output = Path(slot.output_path)
            if output.is_absolute() or ".." in output.parts or output.suffix.lower() != ".png":
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has unsafe output path {slot.output_path!r}"
                )
            if slot.output_path in paths:
                raise CharacterArtValidationError(
                    f"Character slots share output path {slot.output_path!r}"
                )
            if len(slot.size) != 2 or any(value <= 0 for value in slot.size):
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has invalid size {slot.size!r}"
                )
            if slot.generation_calls < 0:
                raise CharacterArtValidationError(
                    f"Character slot {slot.name!r} has a negative generation budget"
                )
            if slot.asset_origin == "fixed_template":
                if not slot.template_path:
                    raise CharacterArtValidationError(
                        f"fixed-template slot {slot.name!r} has no source template"
                    )
                template = Path(slot.template_path)
                if template.is_absolute() or ".." in template.parts or template.suffix.lower() != ".png":
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an unsafe template path"
                    )
                if slot.generation_calls != 0:
                    raise CharacterArtValidationError(
                        f"fixed-template slot {slot.name!r} must not spend a generation call"
                    )
            elif slot.asset_origin == "derived" and slot.generation_calls != 0:
                raise CharacterArtValidationError(
                    f"derived slot {slot.name!r} must not spend a generation call"
                )
            elif slot.template_path is not None:
                raise CharacterArtValidationError(
                    f"non-template slot {slot.name!r} cannot declare a template path"
                )
            footprint = slot.visible_footprint
            if footprint is not None:
                left, top, right, bottom = footprint.content_box
                if (
                    not footprint.host
                    or left < 0
                    or top < 0
                    or right > slot.size[0]
                    or bottom > slot.size[1]
                    or left >= right
                    or top >= bottom
                ):
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an invalid visible content box"
                    )
                if footprint.alpha_content and slot.alpha != "transparent":
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} cannot alpha-check an opaque footprint"
                    )
                if footprint.baseline_y is not None and (
                    not footprint.alpha_content or footprint.baseline_y != bottom
                ):
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an invalid visible baseline"
                    )
                if any(value < 0.0 or value > 1.0 for value in footprint.minimum_fill):
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an invalid minimum fill"
                    )
                if (footprint.visual_scale is None) != (footprint.visual_position is None):
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an incomplete visual style"
                    )
                if footprint.visual_scale is not None and footprint.visual_scale <= 0:
                    raise CharacterArtValidationError(
                        f"Character slot {slot.name!r} has an invalid visual scale"
                    )
            names.add(slot.name)
            paths.add(slot.output_path)

        if self.identity_slot not in names:
            raise CharacterArtValidationError(
                f"identity slot is not in the Character bundle: {self.identity_slot!r}"
            )
        identity = self.slot(self.identity_slot)
        if identity.reference_role != "bootstrap" or identity.spec != "character_select":
            raise CharacterArtValidationError(
                "the identity slot must be the selection portrait bootstrap"
            )

        for spec in self.specs:
            members = [slot for slot in self.slots if slot.spec == spec]
            first = members[0]
            shared = (
                first.size,
                first.alpha,
                first.reference_family,
                first.fit,
                first.verified,
                first.visible_footprint,
            )
            if any(
                (
                    slot.size,
                    slot.alpha,
                    slot.reference_family,
                    slot.fit,
                    slot.verified,
                    slot.visible_footprint,
                ) != shared
                for slot in members[1:]
            ):
                raise CharacterArtValidationError(
                    f"Character spec {spec!r} has inconsistent slot metadata"
                )
            roles = {slot.reference_role for slot in members}
            if len(roles) != 1:
                raise CharacterArtValidationError(
                    f"Character spec {spec!r} has inconsistent reference roles"
                )

    @property
    def specs(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(slot.spec for slot in self.slots))

    def slot(self, name: str) -> CharacterArtSlot:
        try:
            return next(slot for slot in self.slots if slot.name == name)
        except StopIteration as exc:
            raise CharacterArtValidationError(f"unknown Character art slot: {name!r}") from exc

    def slot_for_spec(self, spec: str) -> CharacterArtSlot:
        try:
            return next(slot for slot in self.slots if slot.spec == spec)
        except StopIteration as exc:
            raise CharacterArtValidationError(f"unknown Character art spec: {spec!r}") from exc

    def sprite_specs(self) -> dict[str, dict]:
        """Expose the normalizer shape without duplicating the Character contract."""
        return {
            spec: {
                "sub_path": "charui",
                "extra_sub_paths": [],
                "size": self.slot_for_spec(spec).size,
                "verified": self.slot_for_spec(spec).verified,
                "fit": self.slot_for_spec(spec).fit,
                "chroma": self.slot_for_spec(spec).alpha == "transparent",
                "visible_footprint": self.slot_for_spec(spec).visible_footprint,
            }
            for spec in self.specs
        }

    def visible_footprint(self, spec: str) -> VisibleFootprint | None:
        return self.slot_for_spec(spec).visible_footprint

    def validate_visible_footprint(
        self, spec: str, image: "Image.Image"
    ) -> tuple[int, int, int, int] | None:
        """Validate the alpha-aware part of a normalized host footprint contract."""
        slot = self.slot_for_spec(spec)
        footprint = slot.visible_footprint
        if footprint is None or not footprint.alpha_content:
            return None
        if image.size != slot.size:
            raise CharacterArtValidationError(
                f"{slot.name} footprint has size {image.size}, expected {slot.size}"
            )
        alpha_bounds = image.convert("RGBA").getchannel("A").getbbox()
        if alpha_bounds is None:
            raise CharacterArtValidationError(f"{slot.name} footprint is empty")
        left, top, right, bottom = alpha_bounds
        width, height = slot.size
        if left <= 0 or top <= 0 or right >= width or bottom >= height:
            raise CharacterArtValidationError(
                f"{slot.name} footprint touches the {width}x{height} canvas edge: {alpha_bounds}"
            )
        safe_left, safe_top, safe_right, safe_bottom = footprint.content_box
        if (
            left < safe_left
            or top < safe_top
            or right > safe_right
            or bottom > safe_bottom
        ):
            raise CharacterArtValidationError(
                f"{slot.name} footprint {alpha_bounds} exceeds content box "
                f"{footprint.content_box}"
            )
        if footprint.baseline_y is not None and bottom != footprint.baseline_y:
            raise CharacterArtValidationError(
                f"{slot.name} baseline is {bottom}, expected {footprint.baseline_y}"
            )
        box_width = safe_right - safe_left
        box_height = safe_bottom - safe_top
        min_width, min_height = footprint.minimum_fill
        if (
            right - left < round(box_width * min_width)
            or bottom - top < round(box_height * min_height)
        ):
            raise CharacterArtValidationError(
                f"{slot.name} footprint {alpha_bounds} is undersized for content box "
                f"{footprint.content_box}"
            )
        return alpha_bounds

    def reference_families(self) -> dict[str, str]:
        return {spec: self.slot_for_spec(spec).reference_family for spec in self.specs}

    def reference_role(self, spec: str) -> ReferenceRole:
        return self.slot_for_spec(spec).reference_role

    def requires_identity_reference(self, spec: str) -> bool:
        return self.reference_role(spec) == "identity"

    def validate_identity_reference(
        self, spec: str, identity_reference: Path | None
    ) -> Path | None:
        """Validate role-specific routing for a generated Character asset.

        The selection portrait is the only identity bootstrap. Identity-sensitive
        body/cue assets require its normalized PNG; palette-driven assets explicitly
        reject it so the portrait cannot be accidentally sent as an image reference.
        """
        if spec not in self.specs:
            if identity_reference is not None:
                raise CharacterArtValidationError(
                    "--identity-reference is only valid for Character art specs"
                )
            return None

        role = self.reference_role(spec)
        if role != "identity":
            if identity_reference is not None:
                raise CharacterArtValidationError(
                    f"Character spec {spec!r} uses {role}-only routing; do not pass "
                    "the selection portrait as an image reference"
                )
            return None
        if identity_reference is None:
            raise CharacterArtValidationError(
                f"Character spec {spec!r} requires the normalized selection portrait "
                "as --identity-reference"
            )
        resolved = identity_reference.resolve()
        if not _readable_image(resolved):
            raise CharacterArtValidationError(
                f"Character identity reference is not a readable image: {resolved}"
            )
        return resolved

    def identity_path(self, images_root: Path) -> Path:
        """Return the normalized selection portrait used as the identity bootstrap."""
        return images_root / self.slot(self.identity_slot).output_path

    @property
    def fixed_template_slots(self) -> tuple[CharacterArtSlot, ...]:
        return tuple(slot for slot in self.slots if slot.asset_origin == "fixed_template")

    def template_root_candidates(self) -> tuple[Path, ...]:
        """Locate source assets in both the repository and generated payload layouts."""
        module = Path(__file__).resolve()
        candidates = (
            module.parents[1] / "skills" / "sts2-api" / "reference" / "energy_template",
            module.parents[2] / "sts2-api" / "reference" / "energy_template",
        )
        return tuple(dict.fromkeys(candidates))

    def template_source_path(self, slot: CharacterArtSlot) -> Path:
        if slot.asset_origin != "fixed_template" or not slot.template_path:
            raise CharacterArtValidationError(
                f"Character slot {slot.name!r} is not backed by a fixed template"
            )
        for root in self.template_root_candidates():
            path = root / slot.template_path
            if path.is_file():
                return path
        searched = ", ".join(str(root) for root in self.template_root_candidates())
        raise CharacterArtValidationError(
            f"missing fixed template for {slot.name!r}; searched: {searched}"
        )

    def validate_templates(self) -> tuple[Path, ...]:
        """Validate the lead-supplied fixed layer 2-5 PNGs without resizing them."""
        errors: list[str] = []
        checked: list[Path] = []
        for slot in self.fixed_template_slots:
            try:
                path = self.template_source_path(slot)
                from PIL import Image

                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.size != slot.size:
                        errors.append(
                            f"{slot.name} template has size {image.size}, expected {slot.size}: {path}"
                        )
                    alpha_min, _alpha_max = image.convert("RGBA").getchannel("A").getextrema()
                    if slot.alpha == "transparent" and alpha_min == 255:
                        errors.append(f"{slot.name} template has no transparent pixels: {path}")
                checked.append(path)
            except (CharacterArtValidationError, OSError, ValueError, SyntaxError) as exc:
                errors.append(str(exc))
        if errors:
            raise CharacterArtValidationError("\n".join(errors))
        return tuple(checked)

    def install_fixed_templates(self, images_root: Path) -> tuple[Path, ...]:
        """Copy validated layer 2-5 templates to their exact runtime output paths."""
        # Validate all sources before creating runtime output so a malformed template
        # cannot leave a partially installed Energy bundle.
        self.validate_templates()
        installed: list[Path] = []
        for slot in self.fixed_template_slots:
            source = self.template_source_path(slot)
            destination = images_root / slot.output_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            installed.append(destination)
        return tuple(installed)

    def validate_outputs(self, images_root: Path, identity_reference: Path | None = None) -> tuple[Path, ...]:
        """Validate all required normalized outputs and the identity bootstrap.

        ``identity_reference`` is retained as a compatibility argument, but it must be
        the selection portrait itself. A separate canonical sheet is deliberately invalid.
        """
        errors: list[str] = []
        identity_path = self.identity_path(images_root)
        if identity_reference is not None and identity_reference.resolve() != identity_path.resolve():
            errors.append(
                "selection portrait is the sole Character identity reference; "
                "a separate character sheet is not supported"
            )

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
                        errors.append(f"{slot.name} has size {image.size}, expected {slot.size}: {path}")
                    alpha_min, alpha_max = image.convert("RGBA").getchannel("A").getextrema()
                    if slot.alpha == "opaque" and alpha_min != 255:
                        errors.append(f"{slot.name} must be opaque: {path}")
                    if slot.alpha == "transparent" and alpha_max == 0:
                        errors.append(f"{slot.name} is empty: {path}")
                    elif slot.alpha == "transparent" and alpha_min == 255:
                        errors.append(f"{slot.name} has no transparent pixels: {path}")
                    try:
                        self.validate_visible_footprint(slot.spec, image)
                    except CharacterArtValidationError as exc:
                        errors.append(f"{exc}: {path}")
            except (OSError, ValueError, SyntaxError) as exc:
                errors.append(f"{slot.name} is not a readable PNG: {path} ({exc})")

        if errors:
            raise CharacterArtValidationError("\n".join(errors))
        return tuple(checked)

    def render_review(
        self,
        images_root: Path,
        output_dir: Path,
        identity_reference: Path | None = None,
    ) -> tuple[Path, Path]:
        """Write a labeled contact sheet and deterministic five-layer Energy composite."""
        checked = self.validate_outputs(images_root, identity_reference)
        checked_paths = set(checked)

        from PIL import Image, ImageDraw, ImageFont, ImageOps

        output_dir.mkdir(parents=True, exist_ok=True)
        review_items = [
            (slot.name, images_root / slot.output_path)
            for slot in self.slots
            if images_root / slot.output_path in checked_paths
        ]
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

        energy_slots = [slot for slot in self.slots if slot.spec == "character_energy"]
        if len(energy_slots) != 5:
            raise CharacterArtValidationError("Character bundle must contain exactly five Energy layers")
        composite = Image.new("RGBA", energy_slots[0].size, (0, 0, 0, 0))
        for slot in energy_slots:
            with Image.open(images_root / slot.output_path) as layer:
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
_UNPROMOTED_FALLBACK = "checked native/shared fallback; custom consumer unsupported"


CHARACTER_ART_BUNDLE = CharacterArtBundle(
    slots=(
        CharacterArtSlot(
            "selection_portrait", "character_select", "charui/select.png", (132, 195),
            "opaque", True, _PROFILE_FALLBACK, "NCharacterSelectButton.%Icon and selected panel",
            "character_select", "contain", True, "bootstrap",
            visible_footprint=VisibleFootprint(
                host="character select button and selected panel",
                content_box=(6, 8, 126, 187),
                alpha_content=False,
            ),
        ),
        CharacterArtSlot(
            "locked_selection_portrait", "character_select_locked", "charui/select_locked.png", (132, 195),
            "opaque", False, _UNPROMOTED_FALLBACK, "locked character-select view",
            "character_select", "cover", False, "fallback",
        ),
        CharacterArtSlot(
            "top_panel_icon", "character_icon", "charui/icon.png", (88, 88),
            "transparent", True, _PROFILE_FALLBACK, "NRun.GlobalUi.TopBar.Portrait",
            "character_icon", "contain", True, "palette",
        ),
        CharacterArtSlot(
            "top_panel_icon_outline", "character_icon", "charui/icon_outline.png", (88, 88),
            "transparent", True, _PROFILE_FALLBACK,
            "NRun.GlobalUi.TopBar.Portrait outline and CharacterModel.IconOutlineTexture",
            "character_icon", "contain", True, "palette", "derived", 0,
        ),
        CharacterArtSlot(
            "map_marker", "character_map_marker", "charui/map_marker.png", (49, 64),
            "transparent", False, _UNPROMOTED_FALLBACK, "native/shared run-map marker",
            "character_icon", "contain", False, "fallback",
        ),
        CharacterArtSlot(
            "selection_background", "character_background", "charui/background.png", (1920, 1200),
            "opaque", True, _PROFILE_FALLBACK, "character-select background",
            "character_background", "cover", True, "palette",
        ),
        CharacterArtSlot(
            "combat_body", "character_combat", "charui/combat.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "player NCreature.Visuals",
            "character_combat", "contain", True, "identity",
            visible_footprint=VisibleFootprint(
                host="CombatPlayer NCreature.Visuals",
                content_box=(26, 26, 486, 486),
                alpha_content=True,
                baseline_y=486,
                minimum_fill=(0.45, 0.65),
                visual_scale=0.80,
                visual_position=(0.0, -184.0),
            ),
        ),
        CharacterArtSlot(
            "rest_body", "character_rest", "charui/rest.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "NRestSiteCharacter",
            "character_rest", "contain", True, "identity",
        ),
        CharacterArtSlot(
            "merchant_body", "character_merchant", "charui/merchant.png", (512, 512),
            "transparent", True, _PROFILE_FALLBACK, "NMerchantCharacter",
            "character_combat", "contain", True, "identity",
        ),
        CharacterArtSlot(
            "full_energy_layer_1", "character_energy", "charui/orb_layer_1.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer1",
            "character_icon", "contain", True, "palette",
        ),
        CharacterArtSlot(
            "full_energy_layer_2", "character_energy", "charui/orb_layer_2.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer2",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_2.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_3", "character_energy", "charui/orb_layer_3.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer3",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_3.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_4", "character_energy", "charui/orb_layer_4.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer4",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_4.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_5", "character_energy", "charui/orb_layer_5.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "NEnergyCounter.Layer5",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_5.png",
        ),
        CharacterArtSlot(
            "large_energy_icon", "character_energy_large", "charui/energy_large.png", (256, 256),
            "transparent", True, _PROFILE_FALLBACK, "EnergyIconHelper.GetPath -> NCard.%EnergyIcon",
            "character_icon", "contain", True, "palette",
        ),
        CharacterArtSlot(
            "compact_energy_icon", "character_energy_text", "charui/energy_text.png", (24, 24),
            "transparent", True, _PROFILE_FALLBACK, "EnergyIconsFormatter rich-text image",
            "character_icon", "contain", True, "palette",
        ),
    )
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Review a normalized Character art bundle.")
    parser.add_argument("--images-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--install-energy-templates",
        action="store_true",
        help="validate and copy the fixed layer 2-5 templates before review",
    )
    args = parser.parse_args()
    try:
        if args.install_energy_templates:
            installed = CHARACTER_ART_BUNDLE.install_fixed_templates(Path(args.images_root))
            print(f"[character_art] installed fixed templates: {len(installed)}")
        contact, composite = CHARACTER_ART_BUNDLE.render_review(
            Path(args.images_root), Path(args.out_dir)
        )
    except CharacterArtValidationError as exc:
        parser.error(str(exc))
    print(f"[character_art] contact sheet: {contact}")
    print(f"[character_art] energy composite: {composite}")


if __name__ == "__main__":
    main()
