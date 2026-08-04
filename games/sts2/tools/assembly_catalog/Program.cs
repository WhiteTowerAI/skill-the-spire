using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text.Json;

const string Schema = "openmod.sts2.vanilla-assembly-catalog/v1";

if (args.Length != 4)
{
    Console.Error.WriteLine(
        "usage: OpenMod.Sts2.AssemblyCatalog <sts2.dll> <adapter-targets.json> <profile> <output.json>");
    return 2;
}

var assemblyPath = Path.GetFullPath(args[0]);
var targetsPath = Path.GetFullPath(args[1]);
var profile = args[2];
var outputPath = Path.GetFullPath(args[3]);
if (!File.Exists(assemblyPath) || !File.Exists(targetsPath))
{
    Console.Error.WriteLine("assembly or adapter-targets file does not exist");
    return 2;
}

try
{
    using var stream = File.OpenRead(assemblyPath);
    using var peReader = new PEReader(stream, PEStreamOptions.LeaveOpen);
    if (!peReader.HasMetadata)
        throw new InvalidDataException($"{assemblyPath} has no .NET metadata");

    var reader = peReader.GetMetadataReader();
    var names = new MetadataNames(reader);
    var assembly = reader.GetAssemblyDefinition();
    var module = reader.GetModuleDefinition();
    var targets = ReadTargets(targetsPath);
    var typesByName = reader.TypeDefinitions.ToDictionary(names.FullName, handle => handle,
        StringComparer.Ordinal);

    var modelTypes = reader.TypeDefinitions
        .Select(handle => new TypeRecord(names.FullName(handle), MetadataTokens.GetToken(handle)))
        .Where(type => type.FullName.StartsWith("MegaCrit.Sts2.Core.Models", StringComparison.Ordinal))
        .OrderBy(type => type.FullName, StringComparer.Ordinal)
        .ToArray();

    var adapters = targets.Targets
        .OrderBy(target => target.Id, StringComparer.Ordinal)
        .Select(target => ResolveAdapter(target, reader, peReader, names, typesByName))
        .ToArray();

    var snapshot = new AssemblySnapshot(
        Schema,
        HostVersionFromProfile(profile),
        profile,
        new AssemblyRecord(
            reader.GetString(assembly.Name),
            assembly.Version.ToString(),
            Sha256File(assemblyPath),
            new FileInfo(assemblyPath).Length,
            reader.GetGuid(module.Mvid).ToString("D"),
            reader.MetadataVersion),
        modelTypes,
        adapters);

    Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
    File.WriteAllText(outputPath, JsonSerializer.Serialize(snapshot, JsonOptions()) + Environment.NewLine);
    Console.WriteLine(
        $"[assembly-catalog] types={modelTypes.Length} adapters={adapters.Length} sha256={snapshot.Assembly.Sha256}");
    return 0;
}
catch (Exception exception)
{
    Console.Error.WriteLine($"[assembly-catalog] FAILED: {exception.Message}");
    return 2;
}

static AdapterTargets ReadTargets(string path)
{
    var document = JsonSerializer.Deserialize<AdapterTargets>(File.ReadAllText(path), JsonOptions())
        ?? throw new InvalidDataException("adapter-targets root is empty");
    if (document.Schema != "openmod.sts2.adapter-targets/v1")
        throw new InvalidDataException("adapter-targets schema is not openmod.sts2.adapter-targets/v1");
    var duplicate = document.Targets.GroupBy(target => target.Id, StringComparer.Ordinal)
        .FirstOrDefault(group => group.Count() > 1);
    if (duplicate != null)
        throw new InvalidDataException($"duplicate adapter target id {duplicate.Key}");
    return document;
}

static AdapterRecord ResolveAdapter(
    AdapterTarget target,
    MetadataReader reader,
    PEReader peReader,
    MetadataNames names,
    IReadOnlyDictionary<string, TypeDefinitionHandle> typesByName)
{
    if (!typesByName.TryGetValue(target.Type, out var typeHandle))
        throw new InvalidDataException($"adapter {target.Id} target type not found: {target.Type}");

    var provider = new SignatureNames(names);
    (MethodDefinitionHandle Handle, MethodDefinition Definition, string DeclaringType, string Signature)[]
        candidates = [];
    var currentType = typeHandle;
    while (!currentType.IsNil && candidates.Length == 0)
    {
        var currentDefinition = reader.GetTypeDefinition(currentType);
        var declaringType = names.FullName(currentType);
        candidates = currentDefinition.GetMethods()
            .Select(handle => (Handle: handle, Definition: reader.GetMethodDefinition(handle)))
            .Where(candidate => reader.GetString(candidate.Definition.Name) == target.Method)
            .Select(candidate =>
            {
                var decoded = candidate.Definition.DecodeSignature(provider, null);
                var signature = $"{decoded.ReturnType} {declaringType}.{target.Method}" +
                                $"({string.Join(", ", decoded.ParameterTypes)})";
                return (candidate.Handle, candidate.Definition, DeclaringType: declaringType, Signature: signature);
            })
            .Where(candidate => target.Signature == null || candidate.Signature == target.Signature)
            .ToArray();

        currentType = currentDefinition.BaseType.Kind == HandleKind.TypeDefinition
            ? (TypeDefinitionHandle)currentDefinition.BaseType
            : default;
    }
    if (candidates.Length != 1)
    {
        var found = candidates.Length == 0 ? "none" : string.Join(" | ", candidates.Select(item => item.Signature));
        throw new InvalidDataException(
            $"adapter {target.Id} expected one target for {target.Type}.{target.Method}; found {found}");
    }

    var selected = candidates[0];
    var recordedSignature = target.SignatureLabel == null
        ? selected.Signature
        : target.SignatureLabel.Replace("{declaring_type}", selected.DeclaringType, StringComparison.Ordinal);
    var signatureBytes = reader.GetBlobBytes(selected.Definition.Signature);
    byte[] ilBytes = [];
    var maxStack = 0;
    var localSignatureToken = 0;
    var exceptionRegionCount = 0;
    if (selected.Definition.RelativeVirtualAddress != 0)
    {
        var body = peReader.GetMethodBody(selected.Definition.RelativeVirtualAddress);
        ilBytes = body.GetILBytes() ?? [];
        maxStack = body.MaxStack;
        localSignatureToken = body.LocalSignature.IsNil ? 0 : MetadataTokens.GetToken(body.LocalSignature);
        exceptionRegionCount = body.ExceptionRegions.Length;
    }

    return new AdapterRecord(
        target.Id,
        selected.DeclaringType,
        target.Method,
        recordedSignature,
        MetadataTokens.GetToken(selected.Handle),
        Sha256Bytes(signatureBytes),
        Sha256Bytes(ilBytes),
        new MethodBodyShape(ilBytes.Length, maxStack, localSignatureToken, exceptionRegionCount));
}

static string HostVersionFromProfile(string profile)
{
    const string marker = "-sts2-";
    var index = profile.LastIndexOf(marker, StringComparison.Ordinal);
    if (index < 0 || index + marker.Length == profile.Length)
        throw new InvalidDataException($"profile does not contain a host version: {profile}");
    return profile[(index + marker.Length)..];
}

static string Sha256File(string path)
{
    using var source = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(source)).ToLowerInvariant();
}

static string Sha256Bytes(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

static JsonSerializerOptions JsonOptions() => new()
{
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    WriteIndented = true
};

sealed record AdapterTargets(string Schema, AdapterTarget[] Targets);
sealed record AdapterTarget(string Id, string Type, string Method, string? Signature, string? SignatureLabel);
sealed record TypeRecord(string FullName, int MetadataToken);
sealed record MethodBodyShape(int IlByteCount, int MaxStack, int LocalSignatureToken, int ExceptionRegionCount);
sealed record AdapterRecord(
    string Id,
    string Type,
    string Method,
    string Signature,
    int MetadataToken,
    string SignatureSha256,
    string IlSha256,
    MethodBodyShape BodyShape);
sealed record AssemblyRecord(
    string Name,
    string Version,
    string Sha256,
    long Size,
    string Mvid,
    string MetadataVersion);
sealed record AssemblySnapshot(
    string Schema,
    string HostVersion,
    string Profile,
    AssemblyRecord Assembly,
    TypeRecord[] Types,
    AdapterRecord[] Adapters);

sealed class MetadataNames(MetadataReader reader)
{
    public string FullName(TypeDefinitionHandle handle)
    {
        var definition = reader.GetTypeDefinition(handle);
        var name = reader.GetString(definition.Name);
        if (!definition.GetDeclaringType().IsNil)
            return FullName(definition.GetDeclaringType()) + "+" + name;
        var ns = reader.GetString(definition.Namespace);
        return string.IsNullOrEmpty(ns) ? name : ns + "." + name;
    }

    public string FullName(TypeReferenceHandle handle)
    {
        var reference = reader.GetTypeReference(handle);
        var name = reader.GetString(reference.Name);
        var ns = reader.GetString(reference.Namespace);
        return string.IsNullOrEmpty(ns) ? name : ns + "." + name;
    }
}

sealed class SignatureNames(MetadataNames names)
    : ISignatureTypeProvider<string, object?>
{
    public string GetArrayType(string elementType, ArrayShape shape) =>
        elementType + "[" + new string(',', Math.Max(0, shape.Rank - 1)) + "]";
    public string GetByReferenceType(string elementType) => elementType + "&";
    public string GetFunctionPointerType(MethodSignature<string> signature) => "fnptr";
    public string GetGenericInstantiation(string genericType, System.Collections.Immutable.ImmutableArray<string> typeArguments) =>
        genericType + "<" + string.Join(", ", typeArguments) + ">";
    public string GetGenericMethodParameter(object? genericContext, int index) => "!!" + index;
    public string GetGenericTypeParameter(object? genericContext, int index) => "!" + index;
    public string GetModifiedType(string modifier, string unmodifiedType, bool isRequired) =>
        unmodifiedType + (isRequired ? " modreq(" : " modopt(") + modifier + ")";
    public string GetPinnedType(string elementType) => elementType + " pinned";
    public string GetPointerType(string elementType) => elementType + "*";
    public string GetPrimitiveType(PrimitiveTypeCode typeCode) => typeCode.ToString();
    public string GetSZArrayType(string elementType) => elementType + "[]";
    public string GetTypeFromDefinition(MetadataReader metadataReader, TypeDefinitionHandle handle, byte rawTypeKind) =>
        names.FullName(handle);
    public string GetTypeFromReference(MetadataReader metadataReader, TypeReferenceHandle handle, byte rawTypeKind) =>
        names.FullName(handle);
    public string GetTypeFromSpecification(MetadataReader metadataReader, object? genericContext,
        TypeSpecificationHandle handle, byte rawTypeKind) =>
        metadataReader.GetTypeSpecification(handle).DecodeSignature(this, genericContext);
}
