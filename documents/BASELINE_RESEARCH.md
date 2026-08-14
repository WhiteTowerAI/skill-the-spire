# Current baseline research

## Runtime Identity

Skill the Spire targets:

- Slay the Spire 2 stable `0.107.1`;
- RitsuLib `0.5.11` and `STS2.RitsuLib.Compat.0.107.1`;
- .NET SDK 9;
- Codex plugin and portable Agent Skills distributions; and
- cross-platform Python tools.

Upstream RitsuLib tag `v0.5.11` resolves to commit
`8a2eb7c756d926287078f953f2fac1d47ec014b4`. The official Workshop item is `3747602295`.
Its `0.107.1` Compat DLL has SHA-256
`6c2f65d2245207226aba80d3ea83b928871bd6e9fb7584d28b2669e10d335413`.

Generated Mods require `STS2-RitsuLib >= 0.5.11`, compile against a validated local Compat DLL,
and use bundled `Godot.NET.Sdk 4.5.1` imports. They have no framework `PackageReference` and no
BaseLib dependency.

## Research Sources

The official RitsuLib tutorials establish intended feature semantics. The pinned public RitsuLib
source/API and Compat metadata establish exact signatures and lifecycle behavior. The exact STS2
assembly and committed catalogs establish host identities, model IDs, and public game types.

Maintainer-only checkouts and decompiled files may locate candidate facts, but they are never
generated-project inputs. A fact found in private implementation becomes authoring guidance only
after it is verified against the pinned public/fixed substrate. Decompiled code and third-party
assets are never copied, compiled, packaged, or shipped.

## Stable Technical Facts

- The pinned STS2 assembly SHA-256 is
  `a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`.
- The vanilla catalog contains 1624 concrete models and 1580 stable title sources.
- Display titles are aliases, not primary identities; duplicate localized titles remain explicit
  ambiguities.
- Public model hooks are authorable only on surfaces reached by the dispatcher's real listener
  iterator.
- Enchantments use their dedicated replacement hooks where the pinned API requires them.
- Existing vanilla edits use the cataloged public/fixed operation routes and fail closed on
  target, fingerprint, profile, or conflict drift.
- Runtime manifests use the canonical `mod_manifest.json`; generated projects keep their own
  resource and override sidecars outside loose game JSON deployment.

## Product Semantics

Official RitsuLib documentation is used at the feature-family level. A documented public family is
not narrowed merely because only one representative consumer has been observed. At the same time,
source support never becomes a gameplay claim without an exact real-host run.

The supported pack includes content registration, behavior composition, deterministic lifecycle
and state, Card movement and costs, targeting, rewards, world content, bounded Runtime UI,
presentation, art, localization, and selected vanilla override routes. The capability graph owns
the exact current boundary and limitations.

## Character Design Grounding

The five native Characters use Character-specific Strike and Defend models. Their displayed names
are `Strike` / `打击` and `Defend` / `防御`; their baseline values are `6 -> 9` damage and
`5 -> 8` Block at 1 Energy.

Observed starting decks are:

- Ironclad: `5 Strike + 4 Defend + Bash`;
- Silent: `5 Strike + 5 Defend + Neutralize + Survivor`;
- Defect, Necrobinder, and Regent: `4 Strike + 4 Defend + 2` identity-teaching Cards.

These are native conventions, not a universal deck rule. Character work proposes one complete
native-shaped starting point and preserves an accepted implementable departure with its onboarding,
compatibility, and balance consequences.

## Design Method

Use a compact progressive flow:

```text
route -> relevant native grammar/planning -> adaptive interview -> concise DESIGN.md
      -> implementable SPEC.md -> thin preflight -> author/build
      -> real-host verification -> human playtest delta
```

Planning distinguishes pinned facts, observed conventions, creative decisions, and open
hypotheses. Balance recommendations may be deliberately Mod-forward, but no fixed percentage or
simulated persona proves that content is fun or balanced. A broader future vision does not widen
the current implementation boundary.

## Decision Rules

1. Semantic intent is framework-neutral; RitsuLib owns the active adapter.
2. A successful Build is not load, behavior, presentation, or gameplay evidence.
3. Prefer public STS2/RitsuLib APIs and maintained fixed Adapters.
4. Do not add a helper without a real supported consumer and a proportional verification route.
5. Do not make paid network calls or select image backends without explicit user choice.
6. Keep maintainer research out of generated runtime sessions.
7. Use checked references for pinned facts and label conventions, creative decisions, and
   playtest hypotheses distinctly.
8. Only supported current operations enter `SPEC.md`.
