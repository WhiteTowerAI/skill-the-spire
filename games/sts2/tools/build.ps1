<# RitsuLib build wrapper. The Python tool owns the cross-platform profile checks. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ProjectDir,
    [string] $ModName,
    [string] $RuntimeDir,
    [switch] $SkipRuntimeCheck
)

$ErrorActionPreference = 'Stop'
$argsList = @((Join-Path $PSScriptRoot 'build.py'), '--project-dir', $ProjectDir)
if ($ModName) { $argsList += @('--mod-name', $ModName) }
if ($RuntimeDir) { $argsList += @('--runtime-dir', $RuntimeDir) }
if ($SkipRuntimeCheck) { $argsList += '--skip-runtime-check' }
& python @argsList
exit $LASTEXITCODE
