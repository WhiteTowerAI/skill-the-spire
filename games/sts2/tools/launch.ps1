<#
.SYNOPSIS
  Launch STS2 headless-of-Steam for load verification, wait, then close it.

.DESCRIPTION
  R2 tier-1 launch step (modmaker's verify.md). Ensures steam_appid.txt (=2868840)
  exists in the game dir so SlayTheSpire2.exe runs without Steam, snapshots the
  current log size (so grep_log.ps1 can read only new lines), launches the game,
  waits, then stops the process. Does NOT assert anything itself — pair with
  grep_log.ps1 to check for the [T2MOD-SELFTEST] marker.

.PARAMETER GameDir
  STS2 install dir. Defaults to the M0-recorded path.

.PARAMETER WaitSeconds
  Seconds to let the game load before closing. Default 25 (M0 used ~this).

.EXAMPLE
  pwsh tools/launch.ps1            # launch, wait 25s, close
#>
[CmdletBinding()]
param(
    [string] $GameDir = "D:\Steam\steamapps\common\Slay the Spire 2",
    [int]    $WaitSeconds = 25
)

$ErrorActionPreference = 'Stop'

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

# Snapshot current log length so the grep step reads only this run's lines.
$log = Join-Path $env:APPDATA 'SlayTheSpire2\logs\godot.log'
$offset = 0
if (Test-Path $log) { $offset = (Get-Item $log).Length }
Write-Host "[launch] log offset before launch: $offset bytes ($log)"

Write-Host "[launch] starting SlayTheSpire2.exe ..."
$proc = Start-Process -FilePath $exe -WorkingDirectory $GameDir -PassThru
Write-Host "[launch] pid $($proc.Id); waiting $WaitSeconds s for load"
Start-Sleep -Seconds $WaitSeconds

if (-not $proc.HasExited) {
    Write-Host "[launch] closing game"
    try { $proc.CloseMainWindow() | Out-Null } catch {}
    Start-Sleep -Seconds 2
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}

# Emit the byte offset so the caller can pass it to grep_log.ps1 -SinceOffset.
Write-Output $offset
