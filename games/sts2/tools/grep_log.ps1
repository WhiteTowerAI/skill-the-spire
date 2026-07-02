<#
.SYNOPSIS
  Grep godot.log for the [T2MOD-SELFTEST] load marker and any mod-related errors.

.DESCRIPTION
  R2 tier-1 verify step (modmaker's verify.md). Reads the CURRENT
  %APPDATA%\SlayTheSpire2\logs\godot.log in full. STS2 archives the previous log
  (renaming it to godot<timestamp>.log) and starts a fresh godot.log on every
  launch, so the current file already contains exactly one run — no byte-offset
  slicing is needed, and offsets from a prior file are meaningless against the new
  one (that was the tier-1 false-FAIL bug). Exits 0 if the mod's load marker is
  found AND no error lines name the mod; exits 1 otherwise, with a readable verdict.

.PARAMETER ModName
  Mod name (the 'id' field in Mod.json, also the mods/<ModName> folder name).

.PARAMETER LogPath
  Full path to godot.log. Defaults to the standard Windows location.

.EXAMPLE
  pwsh tools/launch.ps1                          # launch, wait, close
  pwsh tools/grep_log.ps1 -ModName GamblersCoin  # then check the fresh log
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ModName,
    [string] $LogPath = "$env:APPDATA\SlayTheSpire2\logs\godot.log"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $LogPath)) {
    Write-Error "godot.log not found: $LogPath"; exit 2
}

# Read the whole current log. STS2 rotates on launch, so this file == this run.
$content = [System.IO.File]::ReadAllText($LogPath)

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
Write-Host "Log: $LogPath (current run; STS2 rotates on launch)"
Write-Host ""
Write-Host "RUNNING MODDED flag : $(if($modded){'YES'}else{'NOT SEEN (mod may not have loaded)'})"
Write-Host "Tier-1 load marker  : $(if($loadLine){"FOUND => $loadLine"}else{"NOT FOUND -- mod did not log its init marker"})"
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
