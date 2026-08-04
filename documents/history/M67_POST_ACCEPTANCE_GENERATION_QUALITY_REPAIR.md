# M6.7 post-acceptance generation-quality repair

Date: 2026-08-04

## Scope

This is a post-closure authoring-quality repair based on feedback from the retained
independent acceptance session. It does not reopen M6.7, change the accepted representative
game result, promote another operation Package, or turn an unrun check into a pass.

## Repaired defects

1. A request to replace a vanilla Card's effect and original description had been silently
   lowered to complete `OnPlay` replacement plus appended description text. The latter is
   not equivalent: RitsuLib `0.5.4` exposes only before/after Card description fragments.
   Interview, semantic-contract, SPEC, author, routing, and Card-reference instructions now
   require an explicit stop for replace/remove/hide intent. Authoring may continue with
   composition only after the user explicitly accepts keeping the original description.
   The manifest validator also reports this exact capability conflict when `replace` reaches
   `card.description.fragments`.
2. The Ancient patch-registration and Gold-cost examples omitted imports required by the
   files that consume them. The references now include
   `using STS2RitsuLib.Patching.Core;` for `RegisterPatch<T>()` and
   `using MegaCrit.Sts2.Core.Entities.Gold;` for `GoldLossType`. The author stage now checks
   namespace completeness per generated `.cs` file instead of assuming imports carry across
   snippets or files.

## Verification

- four focused regressions passed, including explicit manifest rejection, all authoring
  stages carrying the blocking rule, both reference imports, and a fresh-scaffold C# compile
  that uses `RegisterPatch<T>()` and `GoldLossType.Spent` together;
- the complete STS2 source regression passed `169/169`;
- Python compilation and all six source/plugin/portable skill-root validations passed; and
- plugin and portable payloads were each generated twice. Excluding the portable-only
  `GENERATED.md`, both contain 161 effective files with identical, repeatable tree digest
  `75129DC96A8010FA7FD5A34157B917CF327ACBC6FC8E4E722E9E243A52C67DE6`.

No Tier 1, Tier 2/SelfTest, headed game run, acceptance rerun, or installed-plugin refresh
was performed for this documentation, validator-diagnostic, and compile-fixture repair.
