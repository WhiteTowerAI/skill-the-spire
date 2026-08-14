<#
.SYNOPSIS
  Launch STS2 headless-of-Steam for load verification, wait, then close it.

.DESCRIPTION
  Launch helper for modmaker's verify.md. Ensures steam_appid.txt (=2868840) exists in
  the game dir so SlayTheSpire2.exe runs without Steam, launches the game, waits, then
  stops the process. Does NOT assert anything itself — pair with grep_log.ps1 to check
  for the [T2MOD-SELFTEST] marker.

  Two modes:
   - default (tier-1): launch, wait a fixed -WaitSeconds, close. Proves it loads.
   - -SelfTest (tier-2): pass --t2selftest so the mod's in-process harness drives itself
     from the main menu into the hosted scenario required by the mod and fires the effect
     with zero interaction.
     Instead of a fixed wait, POLL the log until the harness prints its terminal marker
     ([T2MOD-SELFTEST] <ModName> selftest done | selftest FAILED), bounded by -WaitSeconds.
     Requires -ModName so we know whose marker to wait for.

.PARAMETER GameDir
  STS2 install dir. Defaults to the M0-recorded path.

.PARAMETER WaitSeconds
  Tier-1: seconds to let the game load before closing (default 25).
  -SelfTest: max seconds to wait for the harness's terminal marker before giving up
  (default 180 — menu nav + combat entry + effect take longer than a bare load).

.PARAMETER SelfTest
  Append --t2selftest and poll for the harness done/FAILED marker instead of a fixed wait.

.PARAMETER ModName
  Mod name (mods/<ModName> folder / Mod.json id). Required with -SelfTest — the marker to
  poll for is "[T2MOD-SELFTEST] <ModName> selftest done".

.PARAMETER LogPath
  godot.log location. Defaults to the standard Windows path.

.EXAMPLE
  pwsh tools/launch.ps1                                  # tier-1: launch, wait 25s, close
  pwsh tools/launch.ps1 -SelfTest -ModName ExampleMod    # tier-2: self-drive, poll for marker
#>
[CmdletBinding()]
param(
    [string] $GameDir = "D:\Steam\steamapps\common\Slay the Spire 2",
    [int]    $WaitSeconds = 25,
    [switch] $SelfTest,
    [string] $ModName = "",
    [string] $LogPath = "$env:APPDATA\SlayTheSpire2\logs\godot.log"
)

$ErrorActionPreference = 'Stop'

if ($SelfTest) {
    if (-not $ModName) { Write-Error "-SelfTest requires -ModName (whose 'selftest done' marker to wait for)."; exit 2 }
    if ($WaitSeconds -lt 60) { $WaitSeconds = 180 }   # self-test needs real time; don't inherit the 25s tier-1 default
}

$exe = Join-Path $GameDir 'SlayTheSpire2.exe'
if (-not (Test-Path $exe)) {
    Write-Error "SlayTheSpire2.exe not found in $GameDir. Pass -GameDir with the real install path."; exit 2
}

# No-Steam launch: steam_appid.txt must sit next to the exe.
$appid = Join-Path $GameDir 'steam_appid.txt'
if (-not (Test-Path $appid)) {
    Set-Content -Path $appid -Value '2868840' -NoNewline -Encoding ascii
    Write-Host "[launch] created steam_appid.txt (2868840) for no-Steam launch"
}

# STS2 archives the old log and starts a fresh godot.log on launch, so grep_log.ps1
# just reads the whole current file afterward — no offset bookkeeping needed here.
$argList = @()
if ($SelfTest) {
    $argList += '--t2selftest'
    Write-Host "[launch] SELF-TEST mode: passing --t2selftest; harness will self-drive its scenario"
}
Write-Host "[launch] starting SlayTheSpire2.exe ..."
$proc = if ($argList.Count -gt 0) {
    Start-Process -FilePath $exe -WorkingDirectory $GameDir -ArgumentList $argList -PassThru
} else {
    Start-Process -FilePath $exe -WorkingDirectory $GameDir -PassThru
}

if ($SelfTest) {
    # Poll the fresh log for the harness's terminal marker, up to $WaitSeconds.
    $doneRe   = [regex]::Escape("[T2MOD-SELFTEST] $ModName selftest done")
    $failRe   = [regex]::Escape("[T2MOD-SELFTEST] $ModName selftest FAILED")
    Write-Host "[launch] pid $($proc.Id); polling log up to ${WaitSeconds}s for '$ModName selftest done|FAILED'"
    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    $outcome  = 'timeout'
    while ((Get-Date) -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if (-not (Test-Path $LogPath)) { continue }
        # Shared read — the game holds the log open while running.
        try {
            $fs = [System.IO.File]::Open($LogPath, [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
            try { $sr = New-Object System.IO.StreamReader($fs); try { $txt = $sr.ReadToEnd() } finally { $sr.Dispose() } }
            finally { $fs.Dispose() }
        } catch { continue }
        if ($txt -match $doneRe) { $outcome = 'done';   break }
        if ($txt -match $failRe) { $outcome = 'failed'; break }
    }
    switch ($outcome) {
        'done'    { Write-Host "[launch] harness reported: selftest DONE (scenario driven; grep for the type-specific effect marker now)" }
        'failed'  { Write-Host "[launch] harness reported: selftest FAILED (couldn't reach/drive its scenario) -- verify.md: fall back to manual, report tier-1 only" }
        default   { Write-Host "[launch] TIMEOUT after ${WaitSeconds}s with no terminal marker -- treat as harness setup failure (manual fallback)" }
    }
} else {
    Write-Host "[launch] pid $($proc.Id); waiting $WaitSeconds s for load"
    Start-Sleep -Seconds $WaitSeconds
}

if (-not $proc.HasExited) {
    Write-Host "[launch] closing game"
    try { $proc.CloseMainWindow() | Out-Null } catch {}
    Start-Sleep -Seconds 2
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}

Write-Host "[launch] done. Now run grep_log.ps1 -ModName $ModName $(if($SelfTest){'-Tier2Pattern ''<type-specific-effect-pattern>'''}) to check the fresh log."
