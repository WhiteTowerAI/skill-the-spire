# Custom Character dialogue in native Ancient scenes

This capability adds localization-defined dialogue for a registered Mod Character to a
cataloged vanilla Ancient. It preserves the vanilla Event model, scene, background,
options, rewards, progression, and selection rules. It is not custom Ancient creation or
an M6.7 vanilla replacement.

## Pinned STS2 0.107.1 catalog

Resolve the user's natural-language target through this catalog. Use
`ancient_dialogue.py --list-targets` for the machine-owned copy; never guess an entry id.

| entry | display name | availability | headed entry route |
|---|---|---|---|
| `DARV` | Darv | shared across acts | `ancient DARV` |
| `NEOW` | Neow | act 1 | `ancient NEOW` |
| `OROBAS` | Orobas | act 2 | `ancient OROBAS` |
| `PAEL` | Pael | act 2 | `ancient PAEL` |
| `TEZCATARA` | Tezcatara | act 2 | `ancient TEZCATARA` |
| `NONUPEIPE` | Nonupeipe | act 3 | `ancient NONUPEIPE` |
| `TANX` | Tanx | act 3 | `ancient TANX` |
| `VAKUU` | Vakuu | act 3 | `ancient VAKUU` |
| `THE_ARCHITECT` | The Architect | finale Event | production `EnterNextAct()` route |

`THE_ARCHITECT` is an `EventModel`, not an `AncientEventModel`; neither the built-in
`ancient` command nor its completion list can enter it. A proof-only driver may call
`RunManager.Instance.EnterNextAct()` after moving the selected run to its final act. Do
not patch the Event catalog or create a substitute Architect model.

## Semantic SPEC block

Store player meaning, with one-based visit numbers and no localization syntax:

```text
Ancient dialogue:
  target: Darv
  groups:
    - visit rule: first
      lines:
        - speaker: Character
          text: I know what I seek.
          transition prompt: Listen
        - speaker: Ancient
          text: Then choose carefully.
    - visit rule: repeat from visit 2
      lines:
        - speaker: Ancient
          text: Back again?
          transition prompt: Always
        - speaker: Character
          text: The path changed.
```

The three supported visit rules are `first`, `visit N`, and `repeat from visit N`, where
`N >= 1`. `first` means this Character's first visit and lowers to visit index `0`.
`visit N` lowers to `N-1` without repeat. `repeat from visit N` lowers to `N-1` with the
`r` suffix and becomes eligible at that visit and later.

The vanilla global first-visit-ever dialogue has higher priority than Character dialogue.
On a profile that has never completed a run with that Ancient, preserve the native
introduction. The custom `first` group becomes eligible when total visits no longer select
that introduction and this Character's visit index is still zero. Never edit or add a
`firstVisitEver` branch for this capability.

Architect groups additionally store semantic `start attackers` and `end attackers`, each
one of `None`, `Player`, `Architect`, or `Both`. Because Architect uses Character total
wins as the Character visit count, its groups must cover win index zero through the first
repeating group without gaps. It does not allow `ANY` fallback. A complete Architect
dialogue is mandatory for every generated Character even when no other Ancient target was
requested.

## Flat localization lowering

RitsuLib uses the registered Character's normalized public entry:

```text
<ANCIENT>.talk.<CHAR_ID>.<DIALOGUE>-<LINE>[r].ancient
<ANCIENT>.talk.<CHAR_ID>.<DIALOGUE>-<LINE>[r].char
<ANCIENT>.talk.<CHAR_ID>.<DIALOGUE>-<LINE>[r].next
<ANCIENT>.talk.<CHAR_ID>.<DIALOGUE>-visit
THE_ARCHITECT.talk.<CHAR_ID>.<DIALOGUE>-startattack
THE_ARCHITECT.talk.<CHAR_ID>.<DIALOGUE>-endattack
```

Dialogue and line indexes begin at zero and are contiguous. Each line has exactly one
speaker key. Every non-terminal line has exactly one matching `.next`; the terminal line
has none. Every line and prompt in one group either has `r` or omits it. Emit an explicit
`-visit` for every newly authored group instead of depending on RitsuLib's legacy
`0,1,4,+3` defaults.

The existing Character Foundation shape with one repeating Architect dialogue and legacy
`-attack` remains accepted for compatibility. New output uses explicit `-startattack` and
`-endattack`; never emit legacy `-attack` together with `-endattack`.

Line text may use only the balanced vanilla Ancient subset observed in `0.107.1`:
`aqua`, `b`, `font_size=22`, `i`, `jitter`, `orange`, `red`, `sine`, and `thinky_dots`.
Transition prompts are plain text. Do not emit `.sfx`, user-supplied raw markup, custom
colors, tag parameters other than `font_size=22`, or empty strings. Shipped languages use
identical structural keys; line-level Ancient dialogue SFX is unsupported.

## RitsuLib route

RitsuLib `0.5.4` registers `AncientDialoguePopulateLocKeysPatch`. Its prefix appends
localization-defined groups for registered Mod Characters once, before the native
`AncientDialogueSet.PopulateLocKeys` call. Generated Mods only provide `ancients.json`;
they do not emit Harmony, reflection, IL, Publicizer, a second injection patch, or another
runtime dependency.

Normal Ancient selection remains native:

1. global first-visit-ever dialogue;
2. Character dialogue at the exact Character visit index;
3. `ANY` dialogue at that exact index;
4. eligible Character and `ANY` repeating pools.

Tezcatara's vanilla `ANY` blacklist contains Defect only. Do not extend that list to a Mod
Character. Architect instead uses Character wins, forbids `ANY`, and consumes its start/end
attacker metadata. Character speech uses the Character speech-bubble color and Architect
player attacks use `CharacterModel.GetArchitectAttackVfx()`.

RitsuLib's missing-Architect fallback is enabled only by debug compatibility settings and
uses reflection to avoid a crash. It is diagnostic recovery, never production output or
acceptance evidence.

### Native-host prerequisites

The localization resource tree requires `has_pck=true`; a packed but unmounted PCK does
not register any dialogue. `build.py` must reject either manifest/resource mismatch before
MSBuild, and the focused host must assert that the actual RitsuLib lookup returns every
authored group before entering a scene.

Darv can offer `DustyTome`, whose vanilla setup requires a non-transcendence Ancient Card
for the current Character. When `DARV` dialogue is selected, register at least one
Mod-local `CardRarity.Ancient` candidate through
`.DustyTomeCard<<Character>, <AncientCard>>()`. If the semantic Character design has no
such Card, stop during intake instead of removing the native option, patching Darv, or
letting an empty candidate set reach the host.

The focused proof Character must also resolve its normal native Event-option text assets.
This is a proof-fixture prerequisite, not a new Character-art claim: use an existing native
Energy prefix or an existing `TextEnergyIconPath`, and reject any fresh missing-resource or
UI exception before headed review.

## Validation and proof

`build.py` runs the validator before MSBuild. It can also be invoked directly:

```bash
python ../modmaker/scripts/ancient_dialogue.py --project-dir <outer-dir> --mod-name <ModName>
```

The validator rejects unknown catalog ids, wrong Character entries, index gaps, duplicate
speakers, mixed repeat modes, missing/orphan prompts, invalid visit/attacker metadata,
line SFX, unsupported or unbalanced markup, language-key drift, and incomplete Architect
win coverage.

Contract proof parses every authored target and asserts group count, line order/speaker,
visit/repeat routing, prompts, and Architect attackers. A focused real-host proof uses the
actual RitsuLib parser for all nine targets, proves the PCK is mounted, and exercises Darv's
Dusty Tome setup without an exception. Headed review then enters one ordinary Ancient and
the production Architect path.

For an ordinary Ancient, confirm the native banner/background/scene, correct Ancient and
Character icons/bubble directions/colors, readable text and prompts, mouse/controller
progression, and restoration of the untouched native options after the terminal line. For
Architect, also confirm start/end attacks, every selected Character attack VFX, and clean
run completion after Proceed.

This promotes only custom-Character dialogue in native Ancient scenes. Custom Ancient
models, backgrounds/layouts, options/rewards, line audio, arbitrary VFX, global dialogue
replacement, and multiplayer presentation remain unsupported.
