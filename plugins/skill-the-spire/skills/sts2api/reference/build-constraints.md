# Build and load constraints

Use this page before authoring registration/localization output and when a build/profile
diagnostic fails. The active toolchain is the local-runtime skill-the-spire RitsuLib profile.

## Pinned Profile

- host: STS2 stable `0.107.1`;
- authoring baseline: RitsuLib `0.6.7` public API and capability catalog;
- compile runtime: the pinned local RitsuLib version, at least `0.6.7`;
- bundled build SDK: `Godot.NET.Sdk` `4.5.1`;
- `Sts2ApiCompat`: `0.107.1`;
- runtime dependency: `STS2-RitsuLib >= 0.6.7`; a newer local compile runtime does not raise
  this player floor because generated code stays inside the `0.6.7` authoring/API baseline;
- `RitsuLibAutoCopy`: `false`;
- no framework DLL inside the generated Mod directory.

Run `scaffold.py` and `build.py`; do not substitute a generic template or bare publish
flow. The validators reject a missing or drifting local runtime profile, a wrong compat
variant, a wrong host, PackageReference framework dependencies, a malformed manifest, and
a framework DLL copied into the generated Mod.

Keep the authoring/API baseline at `0.6.7`. At compile time use the scaffold-pinned local
RitsuLib version only when its `compat/0.107.1/` variant, marker, `shared/` modules, and
schema-2 manifest hashes validate and the five-module digest matches the scaffold pin. Discover the game-local runtime first, then official Steam Workshop item
`3747602295`; do not copy the framework DLL into the deployed Mod.

The generated consumer has no framework PackageReference. `Godot.NET.Sdk 4.5.1` is supplied
by the skill asset, while `GodotSharp`, `System.IO.Hashing`, STS2, Harmony, and RitsuLib are
resolved from the checked local game/runtime directories. No machine-specific absolute path
is written into the generated project.

## Registration

- Add each selected model exactly once through the scaffold's partial content hook.
- Call one content-pack `.Apply()` after all selected registrations.
- Use the matching `Mod*Template` and pool generic. Do not add pool attributes or
  constructor auto-registration.
- Register Monster and Encounter together. Select the Event's shared/act route explicitly.
- Register a Character with its three typed pools, exact members, starters, and supporting
  models in the same content pack.
- Treat the public registration entry printed by RitsuLib as the localization identity.

## Localization

The default entry is `MOD_CATEGORY_TYPENAME`, normalized to uppercase snake case. Preserve
an already-published entry only through the documented public-entry override.

Common flat keys:

| Surface | Required authored values |
|---|---|
| Card | title, description |
| Potion | title, description |
| Relic | title, description, flavor |
| Power | title, description, smart description |
| Orb | title, description, smart description |
| Keyword | title, description |
| Monster | name |
| Encounter | title, loss |

Events use the explicit nested `events.json` page/option shape documented in
`recipes/event.md`; option keys must exactly match `InitialOptionKey`/`ModOptionKey`.

Characters use the 14 fields documented in `recipes/character.md` plus the four Architect
keys when that presentation is selected. A build can succeed while the visible title is a
raw key, so Tier 1/Tier 2 must resolve the real consumer.

## Resources And Packaging

- Put localization, loose images, and raw scenes under `<project>/<ModName>/`.
- `build.py` packs that resource tree after the C# build.
- Asset profiles must check custom paths and retain the documented fallback.
- Do not claim a custom image from the fallback path; verify the real consumer.
- The deployed Mod directory must contain its DLL, JSON manifest, and PCK when resources
  exist. It must not contain `STS2-RitsuLib.dll`, any other RitsuLib module, or another
  framework payload.

## Runtime Variant

The installed RitsuLib runtime, whether game-local or from official Workshop item
`3747602295`, must be version `>= 0.6.7` and be a complete 0.6 module folder: the root
loader, a schema-2 variant manifest, `compat/0.107.1/` with its marker, `shared/`, and
`assets.zip`. The loader picks the highest variant not newer than the host, so the
`0.107.1` variant is the one that runs. A missing or mismatched variant is a hard actionable
failure. Never skip runtime/host validation for
Tier 1.

## Re-Grounding

When STS2 or RitsuLib changes, maintainers must re-check the package id/version, compat
metadata, public template/registry signatures, manifest schema, localization consumers,
runtime variant manifest, and one stable-host load proof. `$modmaker` sessions read this
pack; they do not live-decompile assemblies or invent a replacement API.
