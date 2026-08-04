<# RitsuLib verifier wrapper. The Python tool owns profile and error-block checks. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ModName,
    [string] $LogPath,
    [string] $Tier2Pattern
)

$ErrorActionPreference = 'Stop'
$argsList = @((Join-Path $PSScriptRoot 'grep_log.py'), '--mod-name', $ModName)
if ($LogPath) { $argsList += @('--log-path', $LogPath) }
if ($Tier2Pattern) { $argsList += @('--tier2-pattern', $Tier2Pattern) }
& python @argsList
exit $LASTEXITCODE
