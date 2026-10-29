# Reference: the user's own sound effects

A Mod keeps every vanilla sound unless the user supplies an audio file for a named slot. There is
no generated audio and no catalog of vanilla sounds to pick from. A supplied file plays through a
RitsuLib virtual event: an FMOD-style path that RitsuLib maps to a raw `res://` file and resolves
wherever the game plays a one-shot through `SfxCmd` or `NAudioManager`.

## Supported slots

| Surface | Slot | Wire the event path |
|---|---|---|
| any effect (Card, Relic, Potion, Power, Orb, Event option, Monster move) | a sound at that point in the effect | `SfxCmd.Play(ModAudio.<Name>);` in the effect sequence |
| attack in an effect | sound on the attacker or on each hit | `DamageCmd.Attack(...).WithAttackerFx(sfx: ModAudio.<Name>)` or `.WithHitFx(sfx: ModAudio.<Name>)` |
| Relic | trigger flash (`Flash()`) | `public override string FlashSfx => ModAudio.<Name>;` |
| Orb | channel | `protected override string ChannelSfx => ModAudio.<Name>;` |
| Orb | passive / evoke | override `PassiveSfx` / `EvokeSfx`, and call `PlayPassiveSfx()` / `PlayEvokeSfx()` in `Passive` / `Evoke` |
| Monster | death | `public override string DeathSfx => ModAudio.<Name>;` and delete `HasDeathSfx => false` |
| Monster | hurt (each damage taken) | `public override string? HurtSfx => ModAudio.<Name>;` |
| Character | select, transition, attack, cast, death | `AssetProfile` field `Audio = new(AttackSfx: ModAudio.<Name>, ...)` |
| Act | treasure chest opening | `public override string ChestOpenSfx => ModAudio.<Name>;` |
| Ancient dialogue line | the sound when a line appears | the line's `.sfx` key (below) |

A slot without a supplied file keeps the recipe's current default: the vanilla event, the
Character's Ironclad placeholder audio, the Frost channel sound, the Act profile's chest sound,
or no Monster death sound. Name a
virtual event only on a slot the user supplied a file for. Character `CharacterAudioAssetSet`
fields left `null` keep the placeholder's sound. Never call `PlayPassiveSfx()` or
`PlayEvokeSfx()` without the matching override: an empty value makes the game probe a missing
debug file.

Ancient line sound: add `<line key>.sfx` with the event path as its value, beside the line key,
in both `eng` and `zhs` with the same value. Omit it to keep the native line sound. This works for
a new Ancient's own dialogue (`recipes/ancient.md`) and for a custom Character's dialogue in a
vanilla Ancient (`reference/ancient-dialogue.md`); never on a transition prompt (`.next`).

## Files

Copy each user file to `<work dir>/<ModName>/audio/<slug>.<ext>`. Build packs it unchanged into
the `.pck` at `res://<ModName>/audio/<slug>.<ext>`; no Godot import step exists or is needed.
Build's audio check fails unless every file:

- sits directly in `audio/` with a lowercase snake_case name;
- is PCM/float `.wav`, Ogg Vorbis `.ogg`, or `.mp3`, and its bytes match the suffix; and
- is at most 256 MiB;

and every `res://.../audio/...` literal in the Mod's sources names an existing file there. When
the user's file is another format (`.flac`, `.m4a`, Ogg Opus, compressed WAV), ask them to
re-export it, for example in Audacity; never transcode it yourself. Keep sound effects short:
each file is decoded whole into memory when it first plays.

## Registration

One Mod-owned class holds every event path and registers each exactly once from
`MainFile.RegisterContent()`, before or after the content pack:

```csharp
// <ModName>Code/ModAudio.cs
using STS2RitsuLib.Audio;

namespace <ModName>;

internal static class ModAudio
{
    public const string HeavyHit = "event:/mods/<ModName>/heavy_hit";
    public const string Roar = "event:/mods/<ModName>/roar";

    public static void Register()
    {
        VirtualFmodEventRegistry.RegisterOneShot(HeavyHit, "res://<ModName>/audio/heavy_hit.ogg");
        VirtualFmodEventRegistry.RegisterOneShotVariants(Roar,
            ["res://<ModName>/audio/roar_1.wav", "res://<ModName>/audio/roar_2.wav"]);
    }
}
```

- Event paths are `event:/mods/<ModName>/<slug>`, case-sensitive, one per slot. Several files on
  one slot use `RegisterOneShotVariants` (random by default).
- `volume:` (0 or more, default 1) and `pitch:` (above 0, default 1) adjust a file that is too
  loud or too quiet. The default bus is the game's SFX bus, so the player's SFX volume applies.
- Use only `RegisterOneShot` and `RegisterOneShotVariants`. Loops, ambience, and music are not
  supported routes (§ Not supported).

## Behavior to expect

- `SfxCmd.Play` does nothing while combat is ending or in non-interactive mode, like every vanilla
  sound.
- Sound is local presentation. In multiplayer every peer runs the same effect and plays it for
  itself; never gate gameplay on a sound or sync one.
- A virtual event reads the bus volume when it starts. A volume change during playback applies to
  the next play. FMOD parameters such as `SfxCmd.Play(path, param, value)` are ignored with a
  RitsuLib warning.

## SPEC

Under the element's `presentation`, list each supplied sound:

```text
- audio: <slot> -> <ModName>/audio/<slug>.<ext> (event:/mods/<ModName>/<slug>) | vanilla
```

## Proof

Add one `RunStart` scenario that asserts every supplied sound, with these exact checks:

```csharp
plan.RunStart("audio_ready", async t =>
{
    foreach (var (eventPath, file) in new[]
    {
        (ModAudio.HeavyHit, "res://<ModName>/audio/heavy_hit.ogg"),
    })
    {
        var played = GameAudioService.Shared.PlayOneShot(AudioSource.ResourceFile(file));
        t.Proof(VirtualFmodEventRegistry.IsRegistered(eventPath)
                && Godot.FileAccess.FileExists(file) && played.Succeeded,
            $"{eventPath} registered={VirtualFmodEventRegistry.IsRegistered(eventPath)} " +
            $"file={Godot.FileAccess.FileExists(file)} play={played.Status}");
    }
    t.Proof(ModelDb.Relic<<Relic>>().FlashSfx == ModAudio.HeavyHit,
        $"relic flash sfx observed={ModelDb.Relic<<Relic>>().FlashSfx}");
    await Task.CompletedTask;
});
```

Also assert each public slot property that names a sound (`FlashSfx`, Monster `DeathSfx` and
`HurtSfx`, the Character's `AttackSfx`, `CastSfx`, `DeathSfx`, `CharacterSelectSfx`, and
`CharacterTransitionSfx`). Protected Orb slots and in-effect `SfxCmd.Play` calls have no
structured observation beyond registration. Whether each sound plays at the right moment and
sounds right is headed review: list every supplied sound and the action that should play it.

## Not supported

- background music: Act `BgMusicOptions`/`MusicBankPaths`, Encounter `CustomBgm`, and adaptive
  music. These go through the game's run-music proxy, which RitsuLib virtual events do not reach;
- ambience and loops: Act and Encounter `AmbientSfx`, Ancient `AmbientBgm`, and
  `SfxCmd.PlayLoop`;
- UI button sounds, and registering a vanilla event path to replace that sound everywhere;
- FMOD Studio banks, GUID maps, snapshots, mixing, and FMOD parameters; and
- generated audio and a catalog of vanilla sounds.
