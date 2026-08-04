param(
    [Parameter(Mandatory = $true)][string]$AssemblyPath,
    [Parameter(Mandatory = $true)][string]$TargetsPath,
    [Parameter(Mandatory = $true)][string]$Profile,
    [Parameter(Mandatory = $true)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$Schema = 'openmod.sts2.vanilla-assembly-catalog/v1'

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-FileSha256Hex([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Get-FullTypeName($Reader, $Handle) {
    $definition = $Reader.GetTypeDefinition($Handle)
    $name = $Reader.GetString($definition.Name)
    if (-not $definition.GetDeclaringType().IsNil) {
        return (Get-FullTypeName $Reader $definition.GetDeclaringType()) + '+' + $name
    }
    $namespace = $Reader.GetString($definition.Namespace)
    if ([string]::IsNullOrEmpty($namespace)) { return $name }
    return $namespace + '.' + $name
}

function Get-MetadataToken([int]$Prefix, $Handle) {
    return [int]($Prefix + $Handle.GetHashCode())
}

$assemblyFullPath = [IO.Path]::GetFullPath($AssemblyPath)
$targetsFullPath = [IO.Path]::GetFullPath($TargetsPath)
$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
if (-not [IO.File]::Exists($assemblyFullPath) -or -not [IO.File]::Exists($targetsFullPath)) {
    throw 'assembly or adapter-targets file does not exist'
}

$metadataDll = Get-ChildItem -LiteralPath (Join-Path $env:ProgramFiles 'dotnet\sdk') -Recurse `
    -Filter 'System.Reflection.Metadata.dll' -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -like '*Microsoft.NET.Sdk\tools\net472\System.Reflection.Metadata.dll' } |
    Sort-Object FullName -Descending |
    Select-Object -First 1
if ($null -eq $metadataDll) {
    throw 'System.Reflection.Metadata net472 tooling was not found in the installed .NET SDK'
}
$metadataDir = $metadataDll.DirectoryName
$unsafeDll = Get-ChildItem -LiteralPath (Join-Path $env:USERPROFILE '.nuget\packages') -Recurse `
    -Filter 'System.Runtime.CompilerServices.Unsafe.dll' -ErrorAction SilentlyContinue |
    Where-Object {
        try {
            ([Reflection.AssemblyName]::GetAssemblyName($_.FullName)).Version -eq [Version]'4.0.4.1' -and
                $_.FullName -like '*\lib\net461\*'
        }
        catch { $false }
    } |
    Select-Object -First 1
if ($null -eq $unsafeDll) {
    throw 'System.Runtime.CompilerServices.Unsafe 4.0.4.1 net461 was not found in the NuGet cache'
}

[void][Reflection.Assembly]::LoadFrom($unsafeDll.FullName)
foreach ($dependency in @('System.Memory.dll', 'System.Collections.Immutable.dll', 'System.Reflection.Metadata.dll')) {
    [void][Reflection.Assembly]::LoadFrom((Join-Path $metadataDir $dependency))
}

$targetsDocument = [IO.File]::ReadAllText($targetsFullPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
if ($targetsDocument.schema -ne 'openmod.sts2.adapter-targets/v1') {
    throw 'adapter-targets schema is not openmod.sts2.adapter-targets/v1'
}
$duplicateTarget = $targetsDocument.targets | Group-Object id | Where-Object Count -gt 1 | Select-Object -First 1
if ($null -ne $duplicateTarget) {
    throw "duplicate adapter target id $($duplicateTarget.Name)"
}

$stream = [IO.File]::OpenRead($assemblyFullPath)
$peReader = [System.Reflection.PortableExecutable.PEReader]::new($stream)
try {
    $reader = [System.Reflection.Metadata.PEReaderExtensions]::GetMetadataReader($peReader)
    $typesByName = @{}
    $typeRecords = [Collections.Generic.List[object]]::new()
    foreach ($typeHandle in $reader.TypeDefinitions) {
        $fullName = Get-FullTypeName $reader $typeHandle
        $typesByName[$fullName] = $typeHandle
        if ($fullName.StartsWith('MegaCrit.Sts2.Core.Models', [StringComparison]::Ordinal)) {
            $typeRecords.Add([ordered]@{
                full_name = $fullName
                metadata_token = Get-MetadataToken 0x02000000 $typeHandle
            })
        }
    }

    $adapterRecords = [Collections.Generic.List[object]]::new()
    foreach ($target in ($targetsDocument.targets | Sort-Object id)) {
        if (-not $typesByName.ContainsKey([string]$target.type)) {
            throw "adapter $($target.id) target type not found: $($target.type)"
        }

        $currentType = $typesByName[[string]$target.type]
        $selectedHandle = $null
        $selectedDefinition = $null
        $declaringType = $null
        while ($null -ne $currentType -and $null -eq $selectedHandle) {
            $typeDefinition = $reader.GetTypeDefinition($currentType)
            $candidates = @()
            foreach ($methodHandle in $typeDefinition.GetMethods()) {
                $methodDefinition = $reader.GetMethodDefinition($methodHandle)
                if ($reader.GetString($methodDefinition.Name) -eq [string]$target.method) {
                    $candidates += ,@($methodHandle, $methodDefinition)
                }
            }
            if ($candidates.Count -gt 1) {
                throw "adapter $($target.id) has overloaded target $($target.type).$($target.method); use the C# collector"
            }
            if ($candidates.Count -eq 1) {
                $selectedHandle = $candidates[0][0]
                $selectedDefinition = $candidates[0][1]
                $declaringType = Get-FullTypeName $reader $currentType
                break
            }
            if ($typeDefinition.BaseType.Kind.ToString() -eq 'TypeDefinition') {
                $currentType = [System.Reflection.Metadata.TypeDefinitionHandle]$typeDefinition.BaseType
            }
            else {
                $currentType = $null
            }
        }
        if ($null -eq $selectedHandle) {
            throw "adapter $($target.id) target was not found: $($target.type).$($target.method)"
        }

        $signatureBytes = $reader.GetBlobBytes($selectedDefinition.Signature)
        [byte[]]$ilBytes = @()
        $maxStack = 0
        $localSignatureToken = 0
        $exceptionRegionCount = 0
        if ($selectedDefinition.RelativeVirtualAddress -ne 0) {
            $body = [System.Reflection.Metadata.PEReaderExtensions]::GetMethodBody(
                $peReader, $selectedDefinition.RelativeVirtualAddress)
            $ilBytes = $body.GetILBytes()
            $maxStack = $body.MaxStack
            if (-not $body.LocalSignature.IsNil) {
                $localSignatureToken = Get-MetadataToken 0x11000000 $body.LocalSignature
            }
            $exceptionRegionCount = $body.ExceptionRegions.Length
        }

        $signature = [string]$target.signature
        if (-not [string]::IsNullOrWhiteSpace([string]$target.signature_label)) {
            $signature = ([string]$target.signature_label).Replace('{declaring_type}', $declaringType)
        }
        if ([string]::IsNullOrWhiteSpace($signature)) {
            $signature = "metadata $declaringType.$($target.method)"
        }

        $adapterRecords.Add([ordered]@{
            id = [string]$target.id
            type = $declaringType
            method = [string]$target.method
            signature = $signature
            metadata_token = Get-MetadataToken 0x06000000 $selectedHandle
            signature_sha256 = Get-Sha256Hex $signatureBytes
            il_sha256 = Get-Sha256Hex $ilBytes
            body_shape = [ordered]@{
                il_byte_count = $ilBytes.Length
                max_stack = $maxStack
                local_signature_token = $localSignatureToken
                exception_region_count = $exceptionRegionCount
            }
        })
    }

    $assemblyDefinition = $reader.GetAssemblyDefinition()
    $moduleDefinition = $reader.GetModuleDefinition()
    $hostMarker = '-sts2-'
    $hostIndex = $Profile.LastIndexOf($hostMarker, [StringComparison]::Ordinal)
    if ($hostIndex -lt 0) { throw "profile does not contain a host version: $Profile" }
    $snapshot = [ordered]@{
        schema = $Schema
        host_version = $Profile.Substring($hostIndex + $hostMarker.Length)
        profile = $Profile
        assembly = [ordered]@{
            name = $reader.GetString($assemblyDefinition.Name)
            version = $assemblyDefinition.Version.ToString()
            sha256 = Get-FileSha256Hex $assemblyFullPath
            size = (Get-Item -LiteralPath $assemblyFullPath).Length
            mvid = $reader.GetGuid($moduleDefinition.Mvid).ToString('D')
            metadata_version = $reader.MetadataVersion
        }
        types = @($typeRecords | Sort-Object full_name)
        adapters = @($adapterRecords)
    }
    $parent = [IO.Path]::GetDirectoryName($outputFullPath)
    if (-not [string]::IsNullOrEmpty($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $json = $snapshot | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText($outputFullPath, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    Write-Output "[assembly-catalog] types=$($typeRecords.Count) adapters=$($adapterRecords.Count) sha256=$($snapshot.assembly.sha256)"
}
finally {
    $peReader.Dispose()
    $stream.Dispose()
}
