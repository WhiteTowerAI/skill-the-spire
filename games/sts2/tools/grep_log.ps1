<#
.SYNOPSIS
  Grep godot.log for the [T2MOD-SELFTEST] load marker and any mod-related errors.

.DESCRIPTION
  R2 tier-1 verify step (modmaker's verify.md). Reads %APPDATA%\SlayTheSpire2\logs\godot.log
  from a given byte offset (output of launch.ps1) to isolate the current run.
  Exits 0 if the mod's load marker is found AND no error lines name the mod.
  Exits 1 otherwise — builds a human-readable verdict the caller can relay.

.PARAMETER ModName
  Mod name (the 'id' field in Mod.json, also the mods/<ModName> folder name).

.PARAMETER SinceOffset
  Byte offset from launch.ps1. Defaults to 0 (read entire log).

.PARAMETER LogPath
  Full path to godot.log. Defaults to the standard Windows location.

.EXAMPLE
  $offset = pwsh tools/launch.ps1
  pwsh tools/grep_log.ps1 -ModName GamblersCoin -SinceOffset $offset
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ModName,
    [long]   $SinceOffset = 0,
    [string] $LogPath = "$env:APPDATA\SlayTheSpire2\logs\godot.log"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $LogPath)) {
    Write-Error "godot.log not found: $LogPath"; exit 2
}

# Read only the lines from this run.
$stream = [System.IO.File]::OpenRead($LogPath)
if ($SinceOffset -gt 0 -and $SinceOffset -lt $stream.Length) {
    $stream.Seek($SinceOffset, 'Begin') | Out-Null
}
$reader  = [System.IO.StreamReader]::new($stream)
$content = $reader.ReadToEnd()
$reader.Close(); $stream.Close()

$lines = $content -split "`n"

# --- Tier-1: load marker ---
$marker   = "[T2MOD-SELFTEST]"
$loadLine = $lines | Where-Object { $_ -match [regex]::Escape($marker) -and $_ -match [regex]::Escape($ModName) } | Select-Object -First 1

# --- Error lines naming the mod ---
$errorLines = $lines | Where-Object {
    ($_ -match '(?i)\bERROR\b' -or $_ -match '(?i)Exception') -and $_ -match [regex]::Escape($ModName)
}

# --- Running modded? ---
$modded = ($lines | Where-Object { $_ -match 'RUNNING MODDED' } | Measure-Object).Count -gt 0

Write-Host ""
Write-Host "=== [T2MOD] Verify: $ModName ==="
Write-Host "Log range: offset $SinceOffset -> end of file"
Write-Host ""
Write-Host "RUNNING MODDED flag : $(if($modded){'YES'}else{'NOT SEEN (mod may not have loaded)'})"
Write-Host "Tier-1 load marker  : $(if($loadLine){"FOUND => $loadLine"}else{"NOT FOUND — mod did not log its init marker"})"
Write-Host ""

if ($errorLines) {
    Write-Host "Errors/exceptions naming '$ModName':"
    $errorLines | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "Errors naming '$ModName'   : none"
}
Write-Host ""

if ($loadLine -and -not $errorLines) {
    Write-Host "[PASS] Tier-1 verified: $ModName loaded ok."
    exit 0
} else {
    if (-not $loadLine) {
        Write-Host "[FAIL] Load marker missing. Check: was PckPacker uncommented? did build copy to mods/? see errors.md."
    }
    if ($errorLines) {
        Write-Host "[FAIL] Error lines found. See errors.md for known fixes."
    }
    exit 1
}
