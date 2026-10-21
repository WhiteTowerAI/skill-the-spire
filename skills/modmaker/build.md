# Build - compile and deploy the local-runtime RitsuLib Mod

Validate the pinned profile, compile, pack, and deploy only the Mod's own artifacts:

```bash
python ../modmaker/scripts/build.py --project-dir <project path from MEMORY.md> --mod-name <ModName>
```

Build checks, in order: the pinned project and manifest profile; `has_pck` against the resource
tree; bilingual localization parity (tables, keys, nonempty values, SmartFormat variables, live
tokens); rich-text markup and vanilla text style; Ancient dialogue structure; the vanilla override
manifest; the unchanged self-test kit; forbidden source routes (`[Pool(...)]`, raw Harmony, member
reflection, Publicizer, unreviewed patch targets); the installed host and RitsuLib runtime; then
MSBuild, packing, deployment, and hook reachability in the compiled Mod. Each failure prints its
own reason; you do not need to know the checks in advance. Build never downloads a framework
package or substitutes another RitsuLib version for the one scaffold recorded.
`--runtime-dir <path>` selects an installed runtime folder; a release zip must be installed
before it can compile.

## Resources and packaging

- Localization, loose images, and raw scenes live under `<project>/<ModName>/`; Build packs that
  tree into `<ModName>.pck`. A code-only `dotnet build` updates neither text nor art.
- Asset profiles check custom paths and keep the documented fallback; a fallback is never claimed
  as a custom image.
- The deployed `mods/<ModName>/` holds `<ModName>.dll`, `mod_manifest.json`, an optional PDB, and
  the `.pck` when resources exist, and nothing else: no RitsuLib or BaseLib file, and no loose
  `.json` besides the manifest (the game parses every `.json` there as a Mod manifest). Authored
  JSON belongs inside the `.pck`; `skillthespire/vanilla-overrides.json` stays in the project.

## Expect

- build summary `0 warnings, 0 errors`;
- `[build] text style OK`. On `text style WARNING`, read `.text-style.log`, fix each listed string
  in both languages, and rebuild; record in `MEMORY.md` any line where the vanilla shape
  deliberately does not apply;
- `[build] source routes OK` and `[build] hook reachability OK`;
- profile lines with the scaffold-pinned compile version and `host=0.107.1`, `compat=0.107.1`;
- the deployed files above, with RitsuLib still separate in `mods/` or its Workshop item.

## On failure

Match the exact signature in `../sts2api/errors.md` § Build And Profile before changing
anything, then follow `repair.md`. Two rules decide where the fix goes:

- A `RitsuLib profile FAILED` / `RitsuLib restore FAILED` contract error is fixed in the local
  runtime, bundled SDK, manifest, host, or the scaffold profile, never in a C# repair loop.
- Ordinary `CS*`/`MSB*` diagnostics go to `repair.md`, keyed by exact code and symbol. A fix that
  changes the accepted operation returns to DESIGN and SPEC for user acceptance.

On success, mark `build` done in `PLAN.md`, record the deployed path in `MEMORY.md` § Project, and
continue to `verify.md`.
