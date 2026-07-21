# art-samples — attribution & purpose

These 82 images are **© Mega Crit**, derived from *Slay the Spire 2* art. They are included
**solely as visual style references** for the art pipeline (`reference/art-contract.md` →
`tools/gen_sprite.py --reference`): they are shown to a user-configured image model as
few-shot examples so a generated custom sprite matches the game's art style. They are
**not** redistributed as game content, are **not** used in any produced mod, and carry
**no** open-source license from this project — they remain Mega Crit's property.

Source: card/icon/monster files were extracted or rendered via `ptrlrd/spire-codex` (GDRE
unpack), which mirrors our own grounding method. Event previews came from the attributed
wiki.gg file pages listed below.

The set is split into **one subdirectory per sprite spec** so the few-shot references
match the target visual language. Both acquisition tools auto-pick the subdir matching
`--spec` and randomly sample three distinct files when the pool is larger; kinds are never
mixed.

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

## `enchantment/` — 20 normal enchantment icons (native 64×64)
All normal-size non-placeholder icons from the pinned game. The `missing_enchantment`
placeholder and the three special 160×152 assets (`favored`, `slumbering_essence`,
`souls_power`) are excluded because they do not match the supported normal profile.

## `orb/` — 5 orb icons (native 100×100)
Dark, Frost, Glass, Lightning, and Plasma. `empty_orb` is excluded because it is a slot
placeholder rather than an authored orb icon.

## `monster/` — 3 full-body monster renders (native 512×512)
The fixed type-matched set requested for static monster generation: Axebot, Ceremonial
Beast, and Crossbow Ruby Raider. These are rendered creature stills, not individual Spine
source textures or animation frames.

## `event/` — 6 event illustrations (wiki.gg 1616×1616 previews)
Chosen from the 55-image local review set for environment, character, object, lighting,
and palette range: Doors of Light and Dark, Drowning Beacon, Tea Master, This or That?,
War Historian Repy, and Wellspring. All six local files match the SHA-1 reported by the
wiki.gg API. They are square reference previews, not the runtime 3440×1613 texture
contract; generated event portraits still use the wide composition template and are
normalized by `gen_sprite.py`.

Source pages:

- https://slaythespire.wiki.gg/wiki/File:StS2_Doors_of_Light_and_Dark.png
- https://slaythespire.wiki.gg/wiki/File:StS2_Drowning_Beacon.png
- https://slaythespire.wiki.gg/wiki/File:StS2_Tea_Master.png
- https://slaythespire.wiki.gg/wiki/File:StS2_This_or_That%3F.png
- https://slaythespire.wiki.gg/wiki/File:StS2_War_Historian,_Repy.png
- https://slaythespire.wiki.gg/wiki/File:StS2_Wellspring.png

## Character static reference pools

The Character pools are maintainer-only style references for the newly grounded static
profiles. They are split by consumer because selection portraits, top-panel icons,
combat bodies, and rest-site bodies have different composition contracts. The files were
copied from the local `spire-codex` research checkout; they are not generated-mod assets
and are never packed into a mod.

- `character_select/`: Ironclad, Silent, and Regent 132x195 selection portraits.
- `character_icon/`: Ironclad, Defect, and Necrobinder 88x88 top-panel icons.
- `character_combat/`: Ironclad, Silent, and Regent 512x512 static combat renders.
- `character_rest/`: Ironclad, Silent, and Regent 512x512 rest-site renders.

These files remain Mega Crit property and inherit the removal/fallback policy above.
Merchant static references and character backgrounds intentionally use text-only prompts
until a separate source-matched pool is reviewed.
