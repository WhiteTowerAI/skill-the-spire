# Grounding rules

Every symbol a generated Mod uses must be grounded before it is written: an exact public owner,
signature, lifecycle, and await behavior from one of the sources below. Never guess a name,
decompile code, or use a private or internal member.

## Four Sources

| Source | Answers |
|---|---|
| pinned vanilla catalog, read through `${GAME_TOOLS_DIR}/vanilla_overrides.py resolve` | what vanilla content exists, does, and resembles: titles, costs, values and upgrades, pools, eng/zhs rules text |
| pinned official RitsuLib tutorial distillations | player-facing purpose and documented feature-family membership |
| pinned STS2 + RitsuLib signatures (distilled by maintainers into recipes and catalogs; at runtime, public metadata only) | exact C# commands, hooks, enums, templates, registries, and hosts |
| skill-the-spire profile/recipes/tests/live runs | what the generator implements and what was observed |

These are complementary. Official tutorial semantics plus public members in the pinned
profile make a documented feature family and all its public consumers supported. A vanilla
analog or tutorial example does not prove a stable-version C# signature, a decompiled
signature does not prove the pinned build profile, and a compiling model does not prove
behavior or presentation. Missing recipe or host verification does not remove support.
Record a concrete failure as the smallest known limitation.

## Runtime Lookup Order

1. Read the selected element recipe.
2. Read only the referenced mechanics, state, presentation, art, or self-test page, and the
   shipped catalogs under `reference/catalogs/` when they cover the symbol.
3. Check `errors.md` for an exact failure signature.
4. For an exact signature, overload, default value, or base-class hook the pages do not
   spell out, run `api.py` (below) instead of guessing.
5. If no maintained route covers the operation, implement it as a Mod-local route below.

## Mod-local Routes

A missing recipe is an authoring gap, not a stop condition. When no maintained route covers an
accepted operation:

1. Ground the exact public types and members in the pinned local assemblies the scaffold
   references (STS2, GodotSharp, RitsuLib). Use only public metadata: type and member names,
   signatures, and documentation. Read it with the lookup tool, which reads the installed
   assemblies and their XML docs without loading them:

   ```powershell
   python ${GAME_TOOLS_DIR}/api.py search CardSelectCmd FromHand   # a type's matching members
   python ${GAME_TOOLS_DIR}/api.py search RelicModel AfterPlayerTurnStart   # with inherited
   python ${GAME_TOOLS_DIR}/api.py find ShuffleIfNecessary         # which type declares it
   python ${GAME_TOOLS_DIR}/api.py --godot search Node2D Position  # include GodotSharp
   ```

   It prints public and protected members only. Nullable reference annotations and
   attributes are not shown, and the compiler is the final check on every signature.
2. Write the smallest Mod-owned implementation that uses only those public members, ordinary
   C#/BCL, and Mod-owned state. Never use Harmony, reflection, Publicizer, IL, or runtime
   patching.
3. Record it in the SPEC `## Implementation` section as
   `- Mod-local: <operation> - <public Owner.Member list>`; the compiler checks each member.
   List the recipes and references for the parts that do have maintained routes.
4. Record the grounded signatures in `MEMORY.md`.
5. Verify it in full: Build, Tier 1, and a Tier 2 SelfTest scenario that drives it through the
   real host and asserts its exact post-state, plus headed review when it has visible UI, input,
   or presentation. Until every required check passes, report it as unverified, not working.
6. Name every Mod-local route in the final report.

Stop and report the operation as unsupported only when it needs a private API, runtime patching,
or decompilation, or when it has no lifecycle the real host can verify. Offer a supported
alternative only with the user's explicit acceptance, because the player-visible result changes.
