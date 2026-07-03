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
    [string] $LogPath = "$env:APPDATA\SlayTheSpire2\logs\godot.log",
    # Tier-2: also report [T2MOD-SELFTEST] lines whose text matches this regex
    # (e.g. 'played|fired|used'). The game is typically still running for tier-2 —
    # the shared-read open below handles that. Empty = tier-1 only (load marker).
    [string] $Tier2Pattern = ""
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $LogPath)) {
    Write-Error "godot.log not found: $LogPath"; exit 2
}

# Read the whole current log. STS2 rotates on launch, so this file == this run.
# Open with FileShare.ReadWrite so this works even while the game is STILL RUNNING
# (the tier-2 case) — the game holds the log open, and File.ReadAllText's exclusive
# open would throw "file in use". A shared read-only handle avoids that.
$content = $null
try {
    $fs = [System.IO.File]::Open($LogPath, [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $sr = New-Object System.IO.StreamReader($fs)
        try { $content = $sr.ReadToEnd() } finally { $sr.Dispose() }
    } finally { $fs.Dispose() }
} catch {
    Write-Error "Could not read ${LogPath}: $($_.Exception.Message)"; exit 2
}

$lines = $content -split "`n"

# --- Tier-1: load marker ---
$marker   = "[T2MOD-SELFTEST]"
$loadLine = $lines | Where-Object { $_ -match [regex]::Escape($marker) -and $_ -match [regex]::Escape($ModName) } | Select-Object -First 1

# --- Tier-2: effect marker (only when a pattern is requested) ---
$tier2Lines = @()
if ($Tier2Pattern -ne "") {
    $tier2Lines = $lines | Where-Object {
        $_ -match [regex]::Escape($marker) -and $_ -match [regex]::Escape($ModName) -and $_ -match $Tier2Pattern
    }
}

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
if ($Tier2Pattern -ne "") {
    if ($tier2Lines) {
        Write-Host "Tier-2 effect marker: FOUND ($($tier2Lines.Count)) => $($tier2Lines | Select-Object -First 1)"
    } else {
        Write-Host "Tier-2 effect marker: NOT FOUND (pattern '$Tier2Pattern') -- effect not observed in this log yet"
    }
}
Write-Host ""

if ($errorLines) {
    Write-Host "Errors/exceptions naming '$ModName':"
    $errorLines | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "Errors naming '$ModName'   : none"
}
Write-Host ""

$tier2Requested = ($Tier2Pattern -ne "")
$tier2Ok        = (-not $tier2Requested) -or ($tier2Lines.Count -gt 0)

if ($loadLine -and -not $errorLines -and $tier2Ok) {
    if ($tier2Requested) {
        Write-Host "[PASS] Tier-2 verified: $ModName loaded AND effect marker fired."
    } else {
        Write-Host "[PASS] Tier-1 verified: $ModName loaded ok."
    }
    exit 0
} else {
    if (-not $loadLine) {
        Write-Host "[FAIL] Load marker missing. Check: was PckPacker uncommented? did build copy to mods/? see errors.md."
    }
    if ($errorLines) {
        Write-Host "[FAIL] Error lines found. See errors.md for known fixes."
    }
    if ($tier2Requested -and -not $tier2Lines) {
        Write-Host "[FAIL] Tier-2 effect marker not found (pattern '$Tier2Pattern'). Was the effect triggered before this grep? Don't close the game first."
    }
    exit 1
}
