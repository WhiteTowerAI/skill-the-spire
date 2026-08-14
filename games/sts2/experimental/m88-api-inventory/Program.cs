using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Text.Json;

if (args.Length != 2)
{
    Console.Error.WriteLine("usage: m88-api-inventory <assembly.dll> <output.json>");
    return 2;
}

var assemblyPath = Path.GetFullPath(args[0]);
var outputPath = Path.GetFullPath(args[1]);

using var stream = File.OpenRead(assemblyPath);
using var peReader = new PEReader(stream);
var reader = peReader.GetMetadataReader();
var types = new List<object>();

foreach (var handle in reader.TypeDefinitions)
{
    var type = reader.GetTypeDefinition(handle);
    var visibility = type.Attributes & TypeAttributes.VisibilityMask;
    if (visibility is not TypeAttributes.Public and not TypeAttributes.NestedPublic)
        continue;

    var methods = new List<string>();
    foreach (var methodHandle in type.GetMethods())
    {
        var method = reader.GetMethodDefinition(methodHandle);
        if ((method.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public)
            methods.Add(reader.GetString(method.Name));
    }

    var fields = new List<string>();
    foreach (var fieldHandle in type.GetFields())
    {
        var field = reader.GetFieldDefinition(fieldHandle);
        if ((field.Attributes & FieldAttributes.FieldAccessMask) == FieldAttributes.Public)
            fields.Add(reader.GetString(field.Name));
    }

    var properties = new List<string>();
    foreach (var propertyHandle in type.GetProperties())
    {
        var property = reader.GetPropertyDefinition(propertyHandle);
        var accessors = property.GetAccessors();
        var publicAccessor = IsPublic(accessors.Getter) || IsPublic(accessors.Setter)
            || accessors.Others.Any(IsPublic);
        if (publicAccessor)
            properties.Add(reader.GetString(property.Name));
    }

    var events = new List<string>();
    foreach (var eventHandle in type.GetEvents())
    {
        var eventDefinition = reader.GetEventDefinition(eventHandle);
        var accessors = eventDefinition.GetAccessors();
        var publicAccessor = IsPublic(accessors.Adder) || IsPublic(accessors.Remover)
            || IsPublic(accessors.Raiser) || accessors.Others.Any(IsPublic);
        if (publicAccessor)
            events.Add(reader.GetString(eventDefinition.Name));
    }

    types.Add(new
    {
        @namespace = reader.GetString(type.Namespace),
        name = reader.GetString(type.Name),
        kind = (type.Attributes & TypeAttributes.Interface) != 0 ? "interface" : "type",
        methods = methods.Distinct().Order().ToArray(),
        properties = properties.Distinct().Order().ToArray(),
        fields = fields.Distinct().Order().ToArray(),
        events = events.Distinct().Order().ToArray(),
    });
}

Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
File.WriteAllText(
    outputPath,
    JsonSerializer.Serialize(
        new
        {
            assembly = assemblyPath,
            publicTypeCount = types.Count,
            types = types.OrderBy(
                item => JsonSerializer.SerializeToElement(item).GetProperty("namespace").GetString()
                    + "."
                    + JsonSerializer.SerializeToElement(item).GetProperty("name").GetString())
        },
        new JsonSerializerOptions { WriteIndented = true }));

return 0;

bool IsPublic(MethodDefinitionHandle handle)
{
    if (handle.IsNil)
        return false;
    var method = reader.GetMethodDefinition(handle);
    return (method.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public;
}
