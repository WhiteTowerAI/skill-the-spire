<#
.SYNOPSIS
  Build an STS2 content mod (.dll + .pck + .json) into the game's mods/ folder.

.DESCRIPTION
  Wraps `dotnet build -c Release`. The Alchyr template's csproj auto-copies the
  .dll/.pdb/.json (CopyToModsFolderOnBuild) and, when BSchneppe.StS2.PckPacker is
  uncommented, the .pck (CopyQuickPck) into <game>/mods/<ModName>/. Game + mods
  paths auto-resolve via Sts2PathDiscovery.props, so no override is normally
  needed. This is the R1 build step used by modmaker's build.md.

  On success prints the artifacts found in the mods folder. On failure prints the
  dotnet output and exits non-zero (repair is handled by the caller, M3+).

.PARAMETER ProjectDir
  Path to the mod project root (the dir holding <ModName>.csproj).

.PARAMETER ModName
  Mod name = csproj base name = mods/<ModName>/ folder. Defaults to the single
  .csproj found in ProjectDir.

.EXAMPLE
  pwsh tools/build.ps1 -ProjectDir D:\26summer_intern\m1-gamblers-coin
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ProjectDir,
    [string] $ModName
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ProjectDir)) {
    Write-Error "ProjectDir not found: $ProjectDir"; exit 2
}

$csproj = Get-ChildItem -Path $ProjectDir -Filter '*.csproj' -File | Select-Object -First 1
if (-not $csproj) {
    Write-Error "No .csproj found in $ProjectDir"; exit 2
}
if (-not $ModName) { $ModName = $csproj.BaseName }

Write-Host "[build] dotnet build -c Release  ($($csproj.Name))"
$log = & dotnet build $csproj.FullName -c Release 2>&1
$code = $LASTEXITCODE

# Keep the console quiet: full output goes to a file, not the transcript.
$buildLog = Join-Path $ProjectDir '.build.log'
$log | Out-File -FilePath $buildLog -Encoding utf8
Write-Host "[build] full output -> $buildLog"

if ($code -ne 0) {
    Write-Host "[build] FAILED (exit $code). Error/warning lines:"
    # Show only diagnostic lines (localized 'error'/'warning' + the MSBuild codes),
    # capped, so a failure is actionable without dumping the whole build.
    $diag = $log | Where-Object { $_ -match '(?i)error|warning|错误|警告|: error|: warning|CS\d|MSB\d' }
    if ($diag) { $diag | Select-Object -First 25 | ForEach-Object { Write-Host "  $_" } }
    else { $log | Select-Object -Last 15 | ForEach-Object { Write-Host "  $_" } }
    Write-Error "[build] dotnet build FAILED (exit $code). Full log: $buildLog"
    exit $code
}

# Locate the mods/<ModName>/ folder the build copied into. Try, in order:
#  1. any log line containing a path ending in ...\mods\<ModName> (locale-agnostic;
#     the copy-confirmation wording is localized, so match the PATH not the words),
#  2. ask MSBuild for the resolved $(ModsPath) property (authoritative fallback).
$modsDir = $null
$escaped = [regex]::Escape($ModName)
$pathHit = $log | Select-String -Pattern "(?<p>[A-Za-z]:[\\/].*?[\\/]mods[\\/]$escaped)(?=[\\/'`" ]|$)" | Select-Object -First 1
if ($pathHit) { $modsDir = $pathHit.Matches[0].Groups['p'].Value }

if (-not $modsDir) {
    $mp = & dotnet msbuild $csproj.FullName -getProperty:ModsPath -nologo 2>$null
    if ($LASTEXITCODE -eq 0 -and $mp) {
        $candidate = Join-Path ($mp.Trim()) $ModName
        if (Test-Path $candidate) { $modsDir = $candidate }
    }
}

Write-Host ""
Write-Host "[build] OK. Artifacts for '$ModName':"
if ($modsDir -and (Test-Path $modsDir)) {
    Get-ChildItem $modsDir -File | ForEach-Object { Write-Host ("  {0}  ({1:N0} bytes)" -f $_.Name, $_.Length) }
    $hasPck = Test-Path (Join-Path $modsDir "$ModName.pck")
    if (-not $hasPck) {
        Write-Warning "[build] No .pck in mods folder. If localization/images don't show in-game, uncomment BSchneppe.StS2.PckPacker in the csproj (see errors.md)."
    }
    Write-Output $modsDir
} else {
    Write-Warning "[build] Build succeeded but could not locate mods/$ModName/ from the log. Check Sts2PathDiscovery.props resolved the game path."
}
