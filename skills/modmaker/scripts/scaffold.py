#!/usr/bin/env python3
"""Generate the minimal open-mod-owned STS2/RitsuLib consumer scaffold."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ritsu_profile import PROFILE
from vanilla_overrides import write_empty_project_manifest


NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def generate(
    project_dir: Path,
    mod_name: str,
    author: str,
    *,
    emit_override_manifest: bool = True,
) -> None:
    if not NAME_RE.fullmatch(mod_name):
        raise ValueError("mod name must be a C# identifier without spaces")
    if "baselib" in mod_name.lower() or "alchyr" in mod_name.lower():
        raise ValueError("mod name may not select a historical BaseLib path")
    if project_dir.name.casefold() == mod_name.casefold():
        raise ValueError("outer project directory name must differ from the Mod name")
    if project_dir.exists() and any(project_dir.iterdir()):
        raise ValueError(
            f"project directory must be empty; use a dedicated outer directory, not {project_dir}"
        )
    project_dir.mkdir(parents=True, exist_ok=True)

    csproj = f'''<Project Sdk="Godot.NET.Sdk/4.5.1">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>true</ImplicitUsings>
    <Nullable>enable</Nullable>
    <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
    <Sts2ApiCompat>{PROFILE.host_version}</Sts2ApiCompat>
    <RitsuLibProfile>{PROFILE.profile_id}</RitsuLibProfile>
    <RitsuLibAutoCopy>false</RitsuLibAutoCopy>
    <RitsuLibDeployDir></RitsuLibDeployDir>
    <CopyLocalLockFileAssemblies>false</CopyLocalLockFileAssemblies>
    <GodotDisabledSourceGenerators>GodotPluginsInitializer</GodotDisabledSourceGenerators>
    <AppOutputBase>$(MSBuildProjectDirectory)\\</AppOutputBase>
    <PathMap>$(AppOutputBase)=.\\</PathMap>
  </PropertyGroup>
  <ItemGroup Condition="Exists('$(Sts2DataDir)')">
    <Reference Include="sts2" HintPath="$(Sts2DataDir)\\sts2.dll" Private="false" />
    <Reference Include="0Harmony" HintPath="$(Sts2DataDir)\\0Harmony.dll" Private="false" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="{PROFILE.package_id}" Version="{PROFILE.framework_version}" PrivateAssets="all" />
    <None Include="{mod_name}.json" />
    <None Include="openmod\\vanilla-overrides.json" Condition="Exists('openmod\\vanilla-overrides.json')" />
    <None Include="Directory.Build.props" />
    <None Include="Sts2PathDiscovery.props" />
  </ItemGroup>
  <Target Name="CheckRitsuLibProfile" BeforeTargets="Build">
    <Error Condition="'$(Sts2ApiCompat)' != '{PROFILE.host_version}'" Text="RitsuLib profile requires Sts2ApiCompat={PROFILE.host_version}." />
    <Error Condition="'$(RitsuLibAutoCopy)' != 'false'" Text="RitsuLib consumer projects must not deploy the framework DLL." />
    <Error Condition="'$(Sts2DataDir)' == '' or !Exists('$(Sts2DataDir)\\sts2.dll')" Text="STS2 stable {PROFILE.host_version} data not found. Set Sts2Dir in local.props." />
  </Target>
  <Target Name="CopyOpenModArtifacts" AfterTargets="Build">
    <MakeDir Directories="$(ModsPath)$(MSBuildProjectName)" />
    <Copy SourceFiles="$(TargetPath)" DestinationFolder="$(ModsPath)$(MSBuildProjectName)" />
    <Copy SourceFiles="$(MSBuildProjectDirectory)\\$(MSBuildProjectName).json" DestinationFolder="$(ModsPath)$(MSBuildProjectName)" />
    <MakeDir Directories="$(ModsPath)$(MSBuildProjectName)\\openmod" Condition="Exists('$(MSBuildProjectDirectory)\\openmod\\vanilla-overrides.json')" />
    <Copy SourceFiles="$(MSBuildProjectDirectory)\\openmod\\vanilla-overrides.json" DestinationFolder="$(ModsPath)$(MSBuildProjectName)\\openmod" Condition="Exists('$(MSBuildProjectDirectory)\\openmod\\vanilla-overrides.json')" />
    <Copy SourceFiles="$(TargetDir)$(TargetName).pdb" DestinationFolder="$(ModsPath)$(MSBuildProjectName)" Condition="Exists('$(TargetDir)$(TargetName).pdb')" />
  </Target>
</Project>
'''
    directory_props = '''<Project>
  <Import Project="local.props" Condition="Exists('local.props')" />
  <Import Project="Sts2PathDiscovery.props" Condition="Exists('Sts2PathDiscovery.props')" />
</Project>
'''
    path_props = '''<Project>
  <PropertyGroup>
    <IsWindows Condition="$([MSBuild]::IsOSPlatform('Windows'))">true</IsWindows>
    <IsLinux Condition="$([MSBuild]::IsOSPlatform('Linux'))">true</IsLinux>
    <IsOSX Condition="$([MSBuild]::IsOSPlatform('OSX'))">true</IsOSX>
  </PropertyGroup>
  <PropertyGroup Condition="'$(IsWindows)' == 'true'">
    <RegistrySts2Path>$([MSBuild]::GetRegistryValueFromView('HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App 2868840', 'InstallLocation', '', RegistryView.Registry64, RegistryView.Registry32))</RegistrySts2Path>
    <AutoSteamPath>$(registry:HKEY_CURRENT_USER\\Software\\Valve\\Steam@SteamPath)\\steamapps</AutoSteamPath>
    <SteamLibraryPath Condition="'$(SteamLibraryPath)' == '' and Exists('$(AutoSteamPath)/common/Slay the Spire 2')">$(AutoSteamPath)</SteamLibraryPath>
    <SteamLibraryPath Condition="'$(SteamLibraryPath)' == ''">C:/Program Files (x86)/Steam/steamapps</SteamLibraryPath>
    <Sts2Dir Condition="'$(Sts2Dir)' == '' and Exists('$(SteamLibraryPath)/common/Slay the Spire 2')">$(SteamLibraryPath)/common/Slay the Spire 2</Sts2Dir>
    <Sts2Dir Condition="'$(Sts2Dir)' == '' and Exists('$(RegistrySts2Path)/data_sts2_windows_x86_64')">$(RegistrySts2Path)</Sts2Dir>
    <Sts2Dir Condition="'$(Sts2Dir)' == ''">$(SteamLibraryPath)/common/Slay the Spire 2</Sts2Dir>
    <Sts2DataDir Condition="'$(Sts2DataDir)' == ''">$(Sts2Dir)/data_sts2_windows_x86_64</Sts2DataDir>
  </PropertyGroup>
  <PropertyGroup Condition="'$(IsLinux)' == 'true'">
    <Sts2Dir Condition="'$(Sts2Dir)' == ''">$(HOME)/.local/share/Steam/steamapps/common/Slay the Spire 2</Sts2Dir>
    <Sts2DataDir Condition="'$(Sts2DataDir)' == ''">$(Sts2Dir)/data_sts2_linuxbsd_x86_64</Sts2DataDir>
  </PropertyGroup>
  <PropertyGroup Condition="'$(IsOSX)' == 'true'">
    <Sts2Dir Condition="'$(Sts2Dir)' == ''">$(HOME)/Library/Application Support/Steam/steamapps/common/Slay the Spire 2</Sts2Dir>
    <Sts2DataDir Condition="'$(Sts2DataDir)' == '' and Exists('$(Sts2Dir)/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64')">$(Sts2Dir)/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64</Sts2DataDir>
    <Sts2DataDir Condition="'$(Sts2DataDir)' == ''">$(Sts2Dir)/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_x86_64</Sts2DataDir>
  </PropertyGroup>
  <PropertyGroup>
    <ModsPath>$(Sts2Dir)/mods/</ModsPath>
  </PropertyGroup>
</Project>
'''
    source = f'''using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Modding;
using STS2RitsuLib;

namespace {mod_name};

[ModInitializer(nameof(Initialize))]
public static partial class MainFile
{{
    public const string ModId = "{mod_name}";
    public static MegaCrit.Sts2.Core.Logging.Logger Logger {{ get; }} =
        RitsuLibFramework.CreateLogger(ModId);

    public static void Initialize()
    {{
        RegisterContent();
        var frameworkAssembly = typeof(Const).Assembly;
        var compat = frameworkAssembly.GetCustomAttributes<AssemblyMetadataAttribute>()
            .FirstOrDefault(attribute => attribute.Key == "Sts2ApiCompat")?.Value ?? "<missing>";
        Logger.Info($"[T2MOD-SELFTEST] {{ModId}} loaded ok framework=RitsuLib frameworkVersion={{Const.Version}} host={PROFILE.host_version} compat={{compat}}");
    }}

    static partial void RegisterContent();
}}
'''
    manifest = {
        "id": mod_name,
        "name": mod_name,
        "author": author,
        "description": "Empty open-mod RitsuLib consumer scaffold",
        "version": "0.0.0",
        "min_game_version": PROFILE.host_version,
        "has_pck": False,
        "has_dll": True,
        "dependencies": [{"id": PROFILE.runtime_mod_id, "min_version": PROFILE.framework_version}],
        "affects_gameplay": False,
    }
    _write(project_dir / f"{mod_name}.csproj", csproj)
    _write(project_dir / "Directory.Build.props", directory_props)
    _write(project_dir / "Sts2PathDiscovery.props", path_props)
    _write(project_dir / f"{mod_name}.json", json.dumps(manifest, indent=2) + "\n")
    _write(project_dir / f"{mod_name}Code" / "MainFile.cs", source)
    if emit_override_manifest:
        write_empty_project_manifest(project_dir, mod_name)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a minimal STS2/RitsuLib consumer project")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--mod-name", required=True)
    parser.add_argument("--author", default="OpenMod")
    args = parser.parse_args(argv)
    try:
        generate(Path(args.project_dir), args.mod_name, args.author)
    except (OSError, ValueError) as exc:
        print(f"[scaffold] FAILED: {exc}", file=sys.stderr)
        return 2
    print(f"[scaffold] generated {PROFILE.profile_id} -> {Path(args.project_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
