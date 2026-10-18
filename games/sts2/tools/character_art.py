#!/usr/bin/env python3
"""Shared contract and review helpers for the static Character art bundle."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


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
class CharacterCueAction:
    """One cue and its runtime frame sequence, as sheet cells in play order.

    `play_cells` names sheet cells (0-based, reading order). A repeated cell is a hold, and
    a cell may serve two cues: Hit recovers through Attack's recovery pose, and Attack and
    Hit both start on the shared anchor cell, so switching cues never redraws the body. A
    breathing cue plays only the anchor, stretched per frame by `CharacterCueContract.breath`:
    redrawn idle cells read as jitter in headed review, and a single frame cannot.
    """

    name: str
    state_name: str
    play_cells: tuple[int, ...]
    frame_count: int
    frame_duration_ms: int
    loop: bool
    terminal: bool
    output_dir: str
    breathing: bool = False


@dataclass(frozen=True)
class CharacterCueContract:
    """Shared acquisition, normalization, geometry, and fallback contract for combat cues.

    All cues come from one paid sheet of `sheet_columns` x `sheet_rows` cells: a single
    image keeps one style, light, and scale across the actions, which four separate action
    sheets did not. The approved static combat body is the anchor reference, and the sheet's
    `anchor_cell` redraws it once for every cue to share. `attack_strike_frame` is the Attack
    frame where the strike pose starts; the Character's AttackAnimDelay is that many Attack
    frame times, so damage lands on the strike.
    """

    actions: tuple[CharacterCueAction, ...]
    source_spec: str
    sheet_columns: int
    sheet_rows: int
    cell_size: int
    anchor_cell: int
    breath: tuple[float, ...]
    attack_strike_frame: int
    frame_size: tuple[int, int]
    content_box: tuple[int, int, int, int]
    baseline_y: int
    reference_family: str
    fallback_slot: str
    consumer: str
    visual_scale: float
    visual_position: tuple[float, float]
    bounds_position: tuple[float, float]
    bounds_size: tuple[float, float]
    intent_position: tuple[float, float]
    center_position: tuple[float, float]
    orb_position: tuple[float, float]
    talk_position: tuple[float, float]

    @property
    def generation_calls(self) -> int:
        return 1

    @property
    def sheet_size(self) -> tuple[int, int]:
        return self.sheet_columns * self.cell_size, self.sheet_rows * self.cell_size


@dataclass(frozen=True)
class CharacterArtSheet:
    """One paid grid image split into several Character slots.

    Cells are in reading order, left-to-right then top-to-bottom; ``None`` is an empty
    cell. One image keeps the cells in one style and, for bodies, one identity.
    """

    name: str
    columns: int
    rows: int
    cells: tuple[str | None, ...]
    cell_size: int = 512

    @property
    def slots(self) -> tuple[str, ...]:
        return tuple(name for name in self.cells if name is not None)

    @property
    def source_size(self) -> tuple[int, int]:
        return self.columns * self.cell_size, self.rows * self.cell_size


@dataclass(frozen=True)
class CharacterArtTier:
    """One user-selectable spend level: the generated slots it acquires, plus cue sheets."""

    name: str
    slots: tuple[str, ...]
    combat_cues: bool = False


@dataclass(frozen=True)
class CharacterArtBundle:
    """The one source of truth for Character asset metadata and reference routing."""

    slots: tuple[CharacterArtSlot, ...]
    identity_slot: str = "selection_portrait"
    combat_cues: CharacterCueContract | None = None
    sheets: tuple[CharacterArtSheet, ...] = ()
    tiers: tuple[CharacterArtTier, ...] = ()

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

        sheet_names: set[str] = set()
        sheet_slots: set[str] = set()
        for sheet in self.sheets:
            if not sheet.name or sheet.name in sheet_names:
                raise CharacterArtValidationError(f"duplicate or empty Character art sheet: {sheet.name!r}")
            sheet_names.add(sheet.name)
            if sheet.columns <= 0 or sheet.rows <= 0 or sheet.cell_size <= 0:
                raise CharacterArtValidationError(f"Character art sheet {sheet.name!r} has an invalid grid")
            if len(sheet.cells) != sheet.columns * sheet.rows or len(sheet.slots) < 2:
                raise CharacterArtValidationError(
                    f"Character art sheet {sheet.name!r} must fill its grid and hold at least two slots"
                )
            roles = set()
            for name in sheet.slots:
                if name not in names:
                    raise CharacterArtValidationError(
                        f"Character art sheet {sheet.name!r} names unknown slot {name!r}"
                    )
                slot = self.slot(name)
                if slot.asset_origin != "generated" or name == self.identity_slot or name in sheet_slots:
                    raise CharacterArtValidationError(
                        f"Character art sheet {sheet.name!r} may hold only generated non-identity "
                        f"slots that no other sheet holds; {name!r} is not one"
                    )
                sheet_slots.add(name)
                roles.add(slot.reference_role)
            if len(roles) != 1:
                raise CharacterArtValidationError(
                    f"Character art sheet {sheet.name!r} mixes reference roles {sorted(roles)}"
                )

        tier_names: set[str] = set()
        for tier in self.tiers:
            if not tier.name or tier.name in tier_names:
                raise CharacterArtValidationError(f"duplicate or empty Character art tier: {tier.name!r}")
            tier_names.add(tier.name)
            if self.identity_slot not in tier.slots:
                raise CharacterArtValidationError(
                    f"Character art tier {tier.name!r} must acquire the identity portrait"
                )
            for name in tier.slots:
                if name not in names:
                    raise CharacterArtValidationError(
                        f"Character art tier {tier.name!r} names unknown slot {name!r}"
                    )
                slot = self.slot(name)
                if not slot.required or slot.asset_origin == "fixed_template":
                    raise CharacterArtValidationError(
                        f"Character art tier {tier.name!r} may list only required generated "
                        f"or derived slots; {name!r} is not one"
                    )
            for sheet in self.sheets:
                listed = set(sheet.slots) & set(tier.slots)
                if listed and listed != set(sheet.slots):
                    raise CharacterArtValidationError(
                        f"Character art tier {tier.name!r} lists part of sheet {sheet.name!r}; "
                        "one sheet call yields all of its slots, so list them all"
                    )
            if tier.combat_cues and self.combat_cues is None:
                raise CharacterArtValidationError(
                    f"Character art tier {tier.name!r} selects cues the bundle does not define"
                )

        cues = self.combat_cues
        if cues is not None:
            expected_actions = ("idle", "attack", "hit", "dead")
            if tuple(action.name for action in cues.actions) != expected_actions:
                raise CharacterArtValidationError(
                    "Character combat cues must be ordered Idle, Attack, Hit, Dead"
                )
            cell_count = cues.sheet_columns * cues.sheet_rows
            if (
                not cues.source_spec
                or cues.source_spec in self.specs
                or cues.sheet_columns <= 0
                or cues.sheet_rows <= 0
                or cues.cell_size <= 0
                or not 0 <= cues.anchor_cell < cell_count
            ):
                raise CharacterArtValidationError("Character cue sheet has invalid metadata")
            cue_paths: set[str] = set()
            for action in cues.actions:
                output = Path(action.output_dir)
                if (
                    not action.state_name
                    or not action.play_cells
                    or any(not 0 <= cell < cell_count for cell in action.play_cells)
                    or action.frame_duration_ms <= 0
                    or output.is_absolute()
                    or ".." in output.parts
                    or output.suffix
                ):
                    raise CharacterArtValidationError(
                        f"Character cue action {action.name!r} has invalid metadata"
                    )
                if action.output_dir in cue_paths:
                    raise CharacterArtValidationError(
                        f"Character cue output directory is duplicated: {action.output_dir!r}"
                    )
                if action.breathing:
                    if (
                        action.play_cells != (cues.anchor_cell,)
                        or len(cues.breath) != action.frame_count
                        or cues.breath[0] != 0
                        or any(not 0 <= amount < 0.05 for amount in cues.breath)
                    ):
                        raise CharacterArtValidationError(
                            f"Character cue {action.name!r} must breathe the anchor cell with "
                            "one small stretch per frame, starting at 0"
                        )
                elif action.frame_count != len(action.play_cells):
                    raise CharacterArtValidationError(
                        f"Character cue {action.name!r} frame count must match its play cells"
                    )
                if action.name in ("attack", "hit") and action.play_cells[0] != cues.anchor_cell:
                    raise CharacterArtValidationError(
                        f"Character cue {action.name!r} must start on the shared anchor cell"
                    )
                cue_paths.add(action.output_dir)
            attack = next(action for action in cues.actions if action.name == "attack")
            if not 0 < cues.attack_strike_frame < attack.frame_count:
                raise CharacterArtValidationError("Attack strike frame is outside the Attack cue")
            if [action.name for action in cues.actions if action.breathing] not in ([], ["idle"]):
                raise CharacterArtValidationError("only the Idle cue may breathe")
            if cues.actions[-1].terminal is not True or any(
                action.terminal for action in cues.actions[:-1]
            ):
                raise CharacterArtValidationError("only the Dead cue may be terminal")
            if cues.actions[0].loop is not True or any(
                action.loop for action in cues.actions[1:]
            ):
                raise CharacterArtValidationError("only the Idle cue may loop")
            width, height = cues.frame_size
            left, top, right, bottom = cues.content_box
            if (
                width <= 0
                or height <= 0
                or left < 0
                or top < 0
                or right > width
                or bottom > height
                or left >= right
                or top >= bottom
                or cues.baseline_y != bottom
                or cues.visual_scale <= 0
                or cues.fallback_slot not in names
                or not cues.reference_family
                or not cues.consumer
            ):
                raise CharacterArtValidationError("Character combat cues have invalid shared geometry")

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

    def tier(self, name: str) -> CharacterArtTier:
        try:
            return next(tier for tier in self.tiers if tier.name == name)
        except StopIteration as exc:
            known = ", ".join(tier.name for tier in self.tiers)
            raise CharacterArtValidationError(
                f"unknown Character art tier {name!r}; choose one of: {known}"
            ) from exc

    def tier_slots(self, name: str) -> tuple[CharacterArtSlot, ...]:
        """The tier's generated slots plus the derived/template slots that follow them."""
        listed = set(self.tier(name).slots)
        specs = {self.slot(slot_name).spec for slot_name in listed}
        return tuple(
            slot
            for slot in self.slots
            if slot.name in listed or (slot.asset_origin != "generated" and slot.spec in specs)
        )

    def present_slots(self, images_root: Path) -> tuple[CharacterArtSlot, ...]:
        """Every slot of each consumer group that has at least one output on disk.

        A group is the slots sharing one spec: the top-panel icon with its derived outline,
        and the five full-Energy layers. One file of a group present means its consumer
        switches away from the fallback, so the rest of that group is required too; groups
        with nothing on disk keep their fallback.
        """
        specs = {slot.spec for slot in self.slots if (images_root / slot.output_path).is_file()}
        return tuple(slot for slot in self.slots if slot.spec in specs)

    def sheet(self, name: str) -> CharacterArtSheet:
        try:
            return next(sheet for sheet in self.sheets if sheet.name == name)
        except StopIteration as exc:
            known = ", ".join(sheet.name for sheet in self.sheets)
            raise CharacterArtValidationError(
                f"unknown Character art sheet {name!r}; choose one of: {known}"
            ) from exc

    def sheet_for_slot(self, name: str) -> CharacterArtSheet | None:
        return next((sheet for sheet in self.sheets if name in sheet.slots), None)

    def tier_generation_calls(self, name: str) -> int:
        """One call per sheet the tier touches, plus one per slot outside any sheet."""
        tier = self.tier(name)
        sheets: set[str] = set()
        calls = 0
        for slot_name in tier.slots:
            sheet = self.sheet_for_slot(slot_name)
            if sheet is not None:
                sheets.add(sheet.name)
            else:
                calls += self.slot(slot_name).generation_calls
        calls += len(sheets)
        if tier.combat_cues and self.combat_cues is not None:
            calls += self.combat_cues.generation_calls
        return calls

    @property
    def cue_specs(self) -> tuple[str, ...]:
        if self.combat_cues is None:
            return ()
        return (self.combat_cues.source_spec,)

    @property
    def acquisition_specs(self) -> tuple[str, ...]:
        return (*self.specs, *self.cue_specs)

    def cue_action(self, name: str) -> CharacterCueAction:
        cues = self.combat_cues
        if cues is not None:
            for action in cues.actions:
                if name in (action.name, action.state_name):
                    return action
        raise CharacterArtValidationError(f"unknown Character combat cue: {name!r}")

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
        families = {spec: self.slot_for_spec(spec).reference_family for spec in self.specs}
        if self.combat_cues is not None:
            families[self.combat_cues.source_spec] = self.combat_cues.reference_family
        return families

    def reference_role(self, spec: str) -> ReferenceRole:
        if spec in self.cue_specs:
            return "identity"
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
        if spec not in self.acquisition_specs:
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
                f"Character spec {spec!r} requires the approved selection portrait "
                "(preferably its full-resolution source) as --identity-reference"
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
            module.parents[1] / "skills" / "sts2api" / "reference" / "energy_template",
            module.parents[2] / "sts2api" / "reference" / "energy_template",
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

    def render_energy_counter(
        self, images_root: Path, frame_hex: str, outline_hex: str
    ) -> tuple[Path, ...]:
        """Write all five full-Energy layers from the Character theme, with no generation.

        Layer 1 is the bottom backing disc; the fixed layers 2-5 carry the shape, and only
        layer 1's tint around the core shows through them. So layer 1 is a radial disc in
        the card-frame color, the core layers 2-3 and ring layer 4 are the templates recolored
        along the frame color, and the edge layer 5 follows the Energy outline color.
        Template geometry and alpha are kept exactly; only color changes.
        """
        from PIL import Image, ImageOps

        frame = _parse_hex_color(frame_hex, "card-frame color")
        outline = _parse_hex_color(outline_hex, "Energy outline color")
        white = (255, 255, 255)
        # Validate every source before writing so a bad template leaves no partial counter.
        self.validate_templates()
        ramps = {
            "full_energy_layer_2": (_scale(frame, 0.40), _mix(frame, white, 0.55)),
            "full_energy_layer_3": (_scale(frame, 0.45), _mix(frame, white, 0.65)),
            "full_energy_layer_4": (_scale(frame, 0.12), _scale(frame, 0.55)),
            "full_energy_layer_5": (_scale(outline, 0.55), _mix(outline, white, 0.25)),
        }
        written: list[Path] = []
        for slot in self.slots:
            if slot.spec != "character_energy":
                continue
            if slot.asset_origin == "fixed_template":
                with Image.open(self.template_source_path(slot)) as source:
                    template = source.convert("RGBA")
                dark, light = ramps[slot.name]
                image = ImageOps.colorize(
                    ImageOps.grayscale(template.convert("RGB")), dark, light
                ).convert("RGBA")
                image.putalpha(template.getchannel("A"))
            else:
                image = _radial_disc(slot.size, _scale(frame, 0.55), _scale(frame, 0.22))
            destination = images_root / slot.output_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination, "PNG")
            written.append(destination)
        return tuple(written)

    def validate_outputs(
        self,
        images_root: Path,
        identity_reference: Path | None = None,
        tier: str | None = None,
        present_only: bool = False,
    ) -> tuple[Path, ...]:
        """Validate the required normalized outputs and the identity bootstrap.

        With ``tier``, only that tier's slots are required; every other slot keeps its
        fallback. With ``present_only``, only the groups already on disk are required (see
        ``present_slots``), for user-supplied images that cover part of the bundle.
        ``identity_reference`` is retained as a compatibility argument, but it must be the
        selection portrait itself. A separate canonical sheet is deliberately invalid.
        """
        if tier is not None and present_only:
            raise CharacterArtValidationError("choose either a tier or present-only, not both")
        if present_only:
            required = {slot.name for slot in self.present_slots(images_root)}
            if not required:
                raise CharacterArtValidationError(
                    f"no Character art output exists under {images_root}"
                )
        elif tier is not None:
            required = {slot.name for slot in self.tier_slots(tier)}
        else:
            required = {slot.name for slot in self.slots if slot.required}
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
                if slot.name in required:
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
        tier: str | None = None,
        present_only: bool = False,
    ) -> tuple[Path, Path | None]:
        """Write a labeled contact sheet and, when Energy is present, its five-layer composite."""
        checked = self.validate_outputs(images_root, identity_reference, tier, present_only)
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
        if not all(images_root / slot.output_path in checked_paths for slot in energy_slots):
            # This tier keeps the base-game Energy counter.
            return contact_path, None
        composite = Image.new("RGBA", energy_slots[0].size, (0, 0, 0, 0))
        for slot in energy_slots:
            with Image.open(images_root / slot.output_path) as layer:
                composite = Image.alpha_composite(composite, layer.convert("RGBA"))
        composite_path = output_dir / "character_energy_composite.png"
        composite.save(composite_path, "PNG")
        return contact_path, composite_path

    def number_contrast(
        self,
        images_root: Path,
        energy_outline: str | None = None,
        label_outline: str | None = None,
    ) -> tuple[list[str], list[str]]:
        """Check (or suggest) the two Mod-owned outlines around Energy numbers.

        Returns (report lines, errors). The card cost sits on `energy_large.png` with the
        pool `EnergyOutlineColor`; the combat "3/3" sits on the five-layer counter with the
        Character `EnergyLabelOutlineColor`. A consumer still on its fallback is checked
        against vanilla Ironclad's measured center, since the Mod's outline is drawn there.
        """
        from PIL import Image

        lines: list[str] = []
        errors: list[str] = []
        large = images_root / self.slot("large_energy_icon").output_path
        layers = [images_root / slot.output_path
                  for slot in self.slots if slot.spec == "character_energy"]
        consumers: list[tuple[str, str, str | None, Image.Image | None]] = []
        if large.is_file():
            with Image.open(large) as icon:
                consumers.append(("card cost", "EnergyOutlineColor", energy_outline,
                                  icon.convert("RGBA")))
        else:
            consumers.append(("card cost", "EnergyOutlineColor", energy_outline, None))
        if all(path.is_file() for path in layers):
            composite = None
            for path in layers:
                with Image.open(path) as layer:
                    rgba = layer.convert("RGBA")
                composite = rgba if composite is None else Image.alpha_composite(composite, rgba)
            consumers.append(("combat counter", "EnergyLabelOutlineColor", label_outline, composite))
        else:
            consumers.append(("combat counter", "EnergyLabelOutlineColor", label_outline, None))

        fallback_centers = {"card cost": FALLBACK_CARD_ICON_CENTER,
                            "combat counter": FALLBACK_COUNTER_CENTER}
        for consumer, member, chosen, image in consumers:
            if image is None:
                center = fallback_centers[consumer]
                consumer = f"{consumer} (fallback Ironclad art)"
            else:
                center = icon_center_color(image)
            suggested = derive_number_outline(center)
            if chosen is None:
                lines.append(f"{consumer}: icon center #{_hex(center)}; use {member} "
                             f"#{_hex(suggested)}")
                continue
            outline = _parse_hex_color(chosen, member)
            problems = number_outline_problems(outline, center)
            if problems:
                errors.append(f"{consumer}: {member} #{_hex(outline)} is hard to read on icon "
                              f"center #{_hex(center)} ({'; '.join(problems)}); use "
                              f"#{_hex(suggested)}")
            else:
                lines.append(
                    f"{consumer}: {member} #{_hex(outline)} OK on icon center #{_hex(center)} "
                    f"(vs number {contrast_ratio(outline, COST_FILL):.2f}, "
                    f"vs icon {contrast_ratio(outline, center):.2f})"
                )
        return lines, errors


def _parse_hex_color(value: str, label: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) != 6 or any(character not in "0123456789abcdefABCDEF" for character in text):
        raise CharacterArtValidationError(f"{label} must be RRGGBB hex, got {value!r}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def _scale(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, round(channel * factor))) for channel in color)


def _mix(color: tuple[int, int, int], other: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(a * (1 - amount) + b * amount) for a, b in zip(color, other))


def _radial_disc(
    size: tuple[int, int], inner: tuple[int, int, int], outer: tuple[int, int, int]
) -> "Image.Image":
    """An opaque disc filling ~92% of the square, inner color at the center."""
    from PIL import Image

    width, height = size
    radius = min(width, height) * 0.46
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            distance = ((x - width / 2 + 0.5) ** 2 + (y - height / 2 + 0.5) ** 2) ** 0.5
            if distance < radius:
                pixels[x, y] = (*_mix(inner, outer, distance / radius), 255)
    return image


def _checkerboard(size: tuple[int, int], tile: int = 16) -> "Image.Image":
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", size, "#d5d8dc")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#aeb4bb")
    return image


# --- cost-number contrast ---------------------------------------------------------------
#
# STS2 draws Energy numbers in a fixed fill (`StsColors.cream` #FFF6E2) with an outline the
# Mod owns: the card-pool `EnergyOutlineColor` around the cost on the large card Energy
# icon, and the Character `EnergyLabelOutlineColor` around "3/3" on the combat counter
# (NCard.UpdateEnergyCostColor, NEnergyCounter). The rich-text icon never carries a number.
# Calibrated on the seven vanilla large card icons in STS2 0.107.1: icon centers are mostly
# light (cream vs center 1.37-2.48), so readability comes from the outline, which reaches
# 6.57-13.62 against cream and at least 2.88 against the icon center. The one dark icon
# (Quest, cream vs center 8.97) relies on the fill instead.
COST_FILL = (0xFF, 0xF6, 0xE2)
OUTLINE_MIN_VS_FILL = 6.5
OUTLINE_MIN_VS_ICON = 2.8
FILL_MIN_VS_DARK_ICON = 4.5
CENTER_BOX = (0.3, 0.3, 0.7, 0.7)
# Without custom art the fallbacks are vanilla Ironclad's, whose centers measured from the
# 0.107.1 PCK are: card icon (ui_atlas energy_ironclad) and five-layer combat counter.
FALLBACK_CARD_ICON_CENTER = (0xF5, 0x7E, 0x19)
FALLBACK_COUNTER_CENTER = (0xFF, 0x66, 0x12)


def _relative_luminance(color: tuple[int, int, int]) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    """WCAG contrast ratio, 1.0 (identical) to 21.0 (black on white)."""
    high, low = sorted((_relative_luminance(a), _relative_luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def icon_center_color(image: "Image.Image") -> tuple[int, int, int]:
    """The median-luminance opaque color in the central box, where the number sits."""
    rgba = image.convert("RGBA")
    w, h = rgba.size
    box = rgba.crop(tuple(round(f * s) for f, s in zip(CENTER_BOX, (w, h, w, h))))
    pixels = [p[:3] for p in box.getdata() if p[3] >= 200]
    if not pixels:
        raise CharacterArtValidationError("the Energy icon center is transparent")
    pixels.sort(key=_relative_luminance)
    return pixels[len(pixels) // 2]


# Derivation aims inside vanilla's range, not at the acceptance edge.
DERIVE_MARGIN = 1.15
NEUTRAL_SATURATION = 0.15


def number_outline_problems(outline: tuple[int, int, int], center: tuple[int, int, int],
                            margin: float = 1.0) -> list[str]:
    """Why a cost-number outline is hard to read on this icon center; empty when readable."""
    problems = []
    vs_fill = contrast_ratio(outline, COST_FILL)
    if vs_fill < OUTLINE_MIN_VS_FILL * margin:
        problems.append(f"outline vs number {vs_fill:.2f} < {OUTLINE_MIN_VS_FILL * margin:.2f}")
    vs_icon = contrast_ratio(outline, center)
    fill_vs_icon = contrast_ratio(COST_FILL, center)
    if vs_icon < OUTLINE_MIN_VS_ICON * margin and fill_vs_icon < FILL_MIN_VS_DARK_ICON:
        problems.append(
            f"outline vs icon {vs_icon:.2f} < {OUTLINE_MIN_VS_ICON * margin:.2f} and number "
            f"vs icon {fill_vs_icon:.2f} < {FILL_MIN_VS_DARK_ICON}"
        )
    return problems


def derive_number_outline(center: tuple[int, int, int]) -> tuple[int, int, int]:
    """The lightest shade of the icon center's own hue that reads clearly, like vanilla.

    A neutral (gray) center keeps a neutral outline instead of borrowing hue 0 (red).
    """
    import colorsys

    hue, _lightness, saturation = colorsys.rgb_to_hls(*(v / 255 for v in center))
    if saturation >= NEUTRAL_SATURATION:
        saturation = min(max(saturation, 0.35), 0.75)
    for step in range(60, -1, -1):
        rgb = tuple(round(v * 255) for v in colorsys.hls_to_rgb(hue, step / 100, saturation))
        if not number_outline_problems(rgb, center, DERIVE_MARGIN):
            return rgb
    return (0, 0, 0)


def _hex(color: tuple[int, int, int]) -> str:
    return "".join(f"{v:02X}" for v in color)


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
_IRONCLAD_ENERGY_COUNTER_FALLBACK = (
    "base-game Ironclad profile: ironclad_energy_counter.tscn"
)
_IRONCLAD_LARGE_ENERGY_FALLBACK = (
    'base-game EnergyIconHelper.GetPath("ironclad"): energy_ironclad.tres'
)
_IRONCLAD_TEXT_ENERGY_FALLBACK = (
    "base-game sprite font: ironclad_energy_icon.png"
)


CHARACTER_ART_BUNDLE = CharacterArtBundle(
    slots=(
        CharacterArtSlot(
            "selection_portrait", "character_select", "charui/select.png", (132, 195),
            "opaque", True, _PROFILE_FALLBACK, "NCharacterSelectButton.%Icon and selected panel",
            # Vanilla select portraits are full-bleed head close-ups that run off every edge,
            # so the source covers the whole 132x195 button instead of a padded safe box.
            "character_select", "cover", True, "bootstrap",
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
            "transparent", True, _IRONCLAD_ENERGY_COUNTER_FALLBACK, "NEnergyCounter.Layer1",
            "character_icon", "contain", True, "palette", "derived", 0,
        ),
        CharacterArtSlot(
            "full_energy_layer_2", "character_energy", "charui/orb_layer_2.png", (256, 256),
            "transparent", True, _IRONCLAD_ENERGY_COUNTER_FALLBACK, "NEnergyCounter.Layer2",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_2.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_3", "character_energy", "charui/orb_layer_3.png", (256, 256),
            "transparent", True, _IRONCLAD_ENERGY_COUNTER_FALLBACK, "NEnergyCounter.Layer3",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_3.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_4", "character_energy", "charui/orb_layer_4.png", (256, 256),
            "transparent", True, _IRONCLAD_ENERGY_COUNTER_FALLBACK, "NEnergyCounter.Layer4",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_4.png",
        ),
        CharacterArtSlot(
            "full_energy_layer_5", "character_energy", "charui/orb_layer_5.png", (256, 256),
            "transparent", True, _IRONCLAD_ENERGY_COUNTER_FALLBACK, "NEnergyCounter.Layer5",
            "character_icon", "contain", True, "palette", "fixed_template", 0, "layer_5.png",
        ),
        CharacterArtSlot(
            "large_energy_icon", "character_energy_large", "charui/energy_large.png", (256, 256),
            "transparent", True, _IRONCLAD_LARGE_ENERGY_FALLBACK,
            "EnergyIconHelper.GetPath -> NCard.%EnergyIcon",
            "character_icon", "contain", True, "palette",
        ),
        CharacterArtSlot(
            "compact_energy_icon", "character_energy_text", "charui/energy_text.png", (24, 24),
            "transparent", True, _IRONCLAD_TEXT_ENERGY_FALLBACK,
            "EnergyIconsFormatter rich-text image",
            "character_icon", "contain", True, "palette",
        ),
    ),
    # One anchor + 6 Attack + 4 Hit + 5 Dead poses on a 4x4 sheet, chosen after headed review
    # of a real Character: a shared anchor removes the redraw jump when a cue starts, distinct
    # poses per cell stop the model from filling cells with anchor copies, and holds come from
    # repeated cells, not extra cells. Cell 10 (a Hit "steadying" pose) is drawn but not
    # played: Hit recovers through Attack's recovery (cell 6), which keeps the held item.
    combat_cues=CharacterCueContract(
        actions=(
            CharacterCueAction("idle", "Idle", (0,), 4, 250, True, False,
                               "charui/cues/idle", breathing=True),
            CharacterCueAction("attack", "Attack", (0, 1, 2, 2, 3, 4, 4, 5, 6), 9, 60,
                               False, False, "charui/cues/attack"),
            CharacterCueAction("hit", "Hit", (0, 7, 8, 9, 9, 6), 6, 70, False, False,
                               "charui/cues/hit"),
            CharacterCueAction("dead", "Dead", (11, 12, 13, 14, 15), 5, 170, False, True,
                               "charui/cues/dead"),
        ),
        source_spec="character_cues",
        sheet_columns=4,
        sheet_rows=4,
        cell_size=512,
        anchor_cell=0,
        breath=(0.0, 0.004, 0.008, 0.004),
        attack_strike_frame=5,
        frame_size=(512, 512),
        content_box=(26, 26, 486, 486),
        baseline_y=486,
        reference_family="character_combat",
        fallback_slot="combat_body",
        consumer="CombatPlayer NCreature visual cue state machine",
        visual_scale=0.80,
        visual_position=(0.0, -184.0),
        bounds_position=(-160.0, -368.0),
        bounds_size=(320.0, 368.0),
        intent_position=(0.0, -410.0),
        center_position=(0.0, -184.0),
        orb_position=(-178.0, -230.0),
        talk_position=(0.0, -420.0),
    ),
    # Grid acquisitions: one paid image per sheet, split into its slots. A real 2x2 trial
    # kept one identity across the three bodies and one style across the icons.
    sheets=(
        CharacterArtSheet(
            "body_sheet", 2, 2, ("combat_body", "rest_body", "merchant_body", None),
        ),
        CharacterArtSheet(
            "icon_sheet", 2, 2,
            ("top_panel_icon", "large_energy_icon", "compact_energy_icon", None),
        ),
    ),
    # Spend levels offered at interview. A slot outside the chosen tier keeps its fallback.
    # The optional locked portrait and map marker are in no tier: generate them only when
    # the user asks for them by name, since their custom consumers are unpromoted.
    tiers=(
        CharacterArtTier(
            "minimal", ("selection_portrait", "combat_body", "rest_body", "merchant_body"),
        ),
        CharacterArtTier(
            "standard",
            (
                "selection_portrait",
                "top_panel_icon",
                "selection_background",
                "combat_body",
                "rest_body",
                "merchant_body",
                "full_energy_layer_1",
                "large_energy_icon",
                "compact_energy_icon",
            ),
        ),
        CharacterArtTier(
            "full",
            (
                "selection_portrait",
                "top_panel_icon",
                "selection_background",
                "combat_body",
                "rest_body",
                "merchant_body",
                "full_energy_layer_1",
                "large_energy_icon",
                "compact_energy_icon",
            ),
            combat_cues=True,
        ),
    ),
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Review a normalized Character art bundle.")
    parser.add_argument("--images-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--energy-colors",
        metavar="FRAME,OUTLINE",
        help="render the five full-Energy layers from the theme's card-frame and Energy "
             "outline colors (RRGGBB,RRGGBB) before review; OUTLINE may be `auto` to derive "
             "the card-pool EnergyOutlineColor from energy_large.png",
    )
    parser.add_argument(
        "--number-outlines",
        metavar="ENERGY_OUTLINE,LABEL_OUTLINE",
        help="check the card-pool EnergyOutlineColor and Character EnergyLabelOutlineColor "
             "(RRGGBB, either may be empty) against the icons the numbers sit on; without "
             "it the review prints the colors to use",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--tier",
        choices=[tier.name for tier in CHARACTER_ART_BUNDLE.tiers],
        help="require only this art tier's outputs; other slots keep their fallback",
    )
    scope.add_argument(
        "--present-only",
        action="store_true",
        help="require only the groups already on disk (user-supplied images that cover part "
             "of the bundle); every other slot keeps its fallback",
    )
    args = parser.parse_args()
    images_root = Path(args.images_root)
    energy_outline, _, label_outline = (args.number_outlines or "").partition(",")
    rendered = False
    try:
        if args.energy_colors:
            frame, _, outline = args.energy_colors.partition(",")
            if outline.strip().lower() == "auto":
                large = images_root / CHARACTER_ART_BUNDLE.slot("large_energy_icon").output_path
                if not large.is_file():
                    raise CharacterArtValidationError(
                        f"--energy-colors {frame},auto needs the large Energy icon at {large}"
                    )
                from PIL import Image

                with Image.open(large) as icon:
                    outline = _hex(derive_number_outline(icon_center_color(icon)))
                print(f"[character_art] derived EnergyOutlineColor #{outline} from {large.name}")
            energy_outline = energy_outline or outline
            written = CHARACTER_ART_BUNDLE.render_energy_counter(images_root, frame, outline)
            rendered = True
            print(f"[character_art] rendered Energy layers: {len(written)}")
        contact, composite = CHARACTER_ART_BUNDLE.render_review(
            images_root, Path(args.out_dir), tier=args.tier,
            present_only=args.present_only,
        )
        lines, errors = CHARACTER_ART_BUNDLE.number_contrast(
            images_root, energy_outline or None, label_outline or None
        )
        if errors:
            raise CharacterArtValidationError("\n".join(errors))
    except CharacterArtValidationError as exc:
        if rendered:
            hint = ("\n(use --present-only when the other slots are meant to keep their "
                    "fallback)" if "missing required" in str(exc) else "")
            exc = CharacterArtValidationError(
                f"the Energy layers were written, but the review failed:\n{exc}{hint}"
            )
        parser.error(str(exc))
    print(f"[character_art] contact sheet: {contact}")
    print(f"[character_art] energy composite: {composite or 'not in this review'}")
    for line in lines:
        print(f"[character_art] number contrast, {line}")


if __name__ == "__main__":
    main()
