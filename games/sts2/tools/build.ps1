<# RitsuLib build wrapper. The Python tool owns the cross-platform profile checks. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ProjectDir,
    [string] $ModName,
    [string] $RuntimeDir
)

$ErrorActionPreference = 'Stop'
$argsList = @((Join-Path $PSScriptRoot 'build.py'), '--project-dir', $ProjectDir)
if ($ModName) { $argsList += @('--mod-name', $ModName) }
if ($RuntimeDir) { $argsList += @('--runtime-dir', $RuntimeDir) }
& python @argsList
exit $LASTEXITCODE
