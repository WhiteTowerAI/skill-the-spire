# art-samples — attribution & purpose

These 36 images are **© Mega Crit**, extracted from *Slay the Spire 2*. They are included
**solely as visual style references** for the art pipeline (`reference/art-contract.md` →
`tools/gen_sprite.py --reference`): they are shown to a user-configured image model as
few-shot examples so a generated custom sprite matches the game's art style. They are
**not** redistributed as game content, are **not** used in any produced mod, and carry
**no** open-source license from this project — they remain Mega Crit's property.

Source: extracted/rendered via `ptrlrd/spire-codex` (GDRE unpack), which mirrors our own
grounding method.

The set is split into **one subdirectory per sprite spec** so the few-shot references
match the target sprite's visual language (a card portrait, a relic icon, a power icon, and
a potion icon look nothing alike). `gen_sprite.py --reference <this dir>` auto-picks the
subdir matching `--spec`; the kinds are never mixed.

If Mega Crit requests removal, delete this directory — the pipeline falls back to the
text-only style descriptor in `art-contract.md` (which needs no images).

## `card/` — 18 card portraits (native 1000×760)
5 characters × 3 + 3 colorless neutrals, chosen for style range, not curated for
consistency (the game's own art is not stylistically uniform):
- Ironclad: bludgeon, inflame, offering
- Silent: abrasive, adrenaline, accuracy
- Defect: ball_lightning, all_for_one, barrage
- Necrobinder: afterlife, blight_strike, bodyguard
- Regent: astral_pulse, arsenal, alignment
- Colorless: alchemize, beacon_of_hope, anointed

## `relic/` — 6 relic icons (native 256×256)
Chosen for material/shape range (cut-out object on transparency): akabeko, anchor,
blood_vial, bronze_scales, burning_blood, calling_bell.

## `power/` — 6 power icons (native 256×256)
Chosen for buff/debuff symbol range: accuracy, artifact, barricade, blur, constrict,
corruption. (Filenames strip the game's `_power` suffix.)

## `potion/` — 6 potion icons (native 256×256)
Chosen for bottle-shape / liquid-colour range (a corked flask on transparency):
block_potion, fire_potion, blood_potion, energy_potion, fairy_in_a_bottle,
explosive_ampoule.
