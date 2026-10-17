#!/usr/bin/env python3
"""Look up public STS2 and RitsuLib API signatures in the locally installed assemblies.

`grounding.md` requires every Mod-local route to name exact public members from the pinned
assemblies the scaffold references. This tool reads only their public metadata (ECMA-335
tables and signature blobs) plus the XML documentation files shipped beside them. It never
decompiles method bodies and never loads or runs the assemblies.

Sources, all from the user's own install:
  sts2.dll (+ sts2.xml) in the game's data directory;
  the five RitsuLib compile modules (+ their XML) from the runtime the scaffold uses;
  GodotSharp.dll with --godot.

Usage:
  python api.py search CardSelectCmd FromHand   # members of matching types, by name
  python api.py search CardPile                  # every public member of a type
  python api.py search RelicModel AfterPlayerTurnStart   # includes inherited members
  python api.py find ShuffleIfNecessary          # which types declare a member

The compiler stays the final check: nullable reference annotations and attributes are not
shown, and overload resolution is the compiler's job.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

MAX_TYPES = 15
MAX_MEMBERS_PER_TYPE = 150
MAX_FIND_RESULTS = 40

# ECMA-335 II.22 table schemas. Column kinds: fixed widths, heap indexes, simple table
# indexes ("t", table), and coded indexes ("c", name).
TYPEDEF, TYPEREF, TYPESPEC = 0x02, 0x01, 0x1B
FIELD, METHODDEF, PARAM, CONSTANT = 0x04, 0x06, 0x08, 0x0B
PROPERTYMAP, PROPERTY, METHODSEMANTICS = 0x15, 0x17, 0x18
NESTEDCLASS, GENERICPARAM = 0x29, 0x2A

SCHEMAS: dict[int, list] = {
    0x00: [2, "s", "g", "g", "g"],
    0x01: [("c", "ResolutionScope"), "s", "s"],
    0x02: [4, "s", "s", ("c", "TypeDefOrRef"), ("t", 0x04), ("t", 0x06)],
    0x03: [("t", 0x04)],
    0x04: [2, "s", "b"],
    0x05: [("t", 0x06)],
    0x06: [4, 2, 2, "s", "b", ("t", 0x08)],
    0x07: [("t", 0x08)],
    0x08: [2, 2, "s"],
    0x09: [("t", 0x02), ("c", "TypeDefOrRef")],
    0x0A: [("c", "MemberRefParent"), "s", "b"],
    0x0B: [2, ("c", "HasConstant"), "b"],
    0x0C: [("c", "HasCustomAttribute"), ("c", "CustomAttributeType"), "b"],
    0x0D: [("c", "HasFieldMarshal"), "b"],
    0x0E: [2, ("c", "HasDeclSecurity"), "b"],
    0x0F: [2, 4, ("t", 0x02)],
    0x10: [4, ("t", 0x04)],
    0x11: ["b"],
    0x12: [("t", 0x02), ("t", 0x14)],
    0x13: [("t", 0x14)],
    0x14: [2, "s", ("c", "TypeDefOrRef")],
    0x15: [("t", 0x02), ("t", 0x17)],
    0x16: [("t", 0x17)],
    0x17: [2, "s", "b"],
    0x18: [2, ("t", 0x06), ("c", "HasSemantics")],
    0x19: [("t", 0x02), ("c", "MethodDefOrRef"), ("c", "MethodDefOrRef")],
    0x1A: ["s"],
    0x1B: ["b"],
    0x1C: [2, ("c", "MemberForwarded"), "s", ("t", 0x1A)],
    0x1D: [4, ("t", 0x04)],
    0x1E: [4, 4],
    0x1F: [4],
    0x20: [4, 2, 2, 2, 2, 4, "b", "s", "s"],
    0x21: [4],
    0x22: [4, 4, 4],
    0x23: [2, 2, 2, 2, 4, "b", "s", "s", "b"],
    0x24: [4, ("t", 0x23)],
    0x25: [4, 4, 4, ("t", 0x23)],
    0x26: [4, "s", "b"],
    0x27: [4, 4, "s", "s", ("c", "Implementation")],
    0x28: [4, 4, "s", ("c", "Implementation")],
    0x29: [("t", 0x02), ("t", 0x02)],
    0x2A: [2, 2, ("c", "TypeOrMethodDef"), "s"],
    0x2B: [("c", "MethodDefOrRef"), "b"],
    0x2C: [("t", 0x2A), ("c", "TypeDefOrRef")],
}
CODED: dict[str, tuple[int, tuple[int | None, ...]]] = {
    "TypeDefOrRef": (2, (0x02, 0x01, 0x1B)),
    "HasConstant": (2, (0x04, 0x08, 0x17)),
    "HasCustomAttribute": (5, (0x06, 0x04, 0x01, 0x02, 0x08, 0x09, 0x0A, 0x00, 0x0E, 0x17,
                               0x14, 0x11, 0x1A, 0x1B, 0x20, 0x23, 0x26, 0x27, 0x28, 0x2A,
                               0x2C, 0x2B)),
    "HasFieldMarshal": (1, (0x04, 0x08)),
    "HasDeclSecurity": (2, (0x02, 0x06, 0x20)),
    "MemberRefParent": (3, (0x02, 0x01, 0x1A, 0x06, 0x1B)),
    "HasSemantics": (1, (0x14, 0x17)),
    "MethodDefOrRef": (1, (0x06, 0x0A)),
    "MemberForwarded": (1, (0x04, 0x06)),
    "Implementation": (2, (0x26, 0x23, 0x27)),
    "CustomAttributeType": (3, (None, None, 0x06, 0x0A, None)),
    "ResolutionScope": (2, (0x00, 0x1A, 0x23, 0x01)),
    "TypeOrMethodDef": (1, (0x02, 0x06)),
}
PRIMITIVES = {
    0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "sbyte", 0x05: "byte", 0x06: "short",
    0x07: "ushort", 0x08: "int", 0x09: "uint", 0x0A: "long", 0x0B: "ulong", 0x0C: "float",
    0x0D: "double", 0x0E: "string", 0x16: "TypedReference", 0x18: "nint", 0x19: "nuint",
    0x1C: "object",
}
PRIMITIVE_FULL = {
    0x01: "System.Void", 0x02: "System.Boolean", 0x03: "System.Char", 0x04: "System.SByte",
    0x05: "System.Byte", 0x06: "System.Int16", 0x07: "System.UInt16", 0x08: "System.Int32",
    0x09: "System.UInt32", 0x0A: "System.Int64", 0x0B: "System.UInt64", 0x0C: "System.Single",
    0x0D: "System.Double", 0x0E: "System.String", 0x16: "System.TypedReference",
    0x18: "System.IntPtr", 0x19: "System.UIntPtr", 0x1C: "System.Object",
}
ALIASES = {full: PRIMITIVES[code] for code, full in PRIMITIVE_FULL.items()}
ALIASES["System.Decimal"] = "decimal"

# Flag masks (ECMA-335 II.23.1).
TYPE_VISIBILITY, TYPE_INTERFACE, TYPE_ABSTRACT, TYPE_SEALED = 0x7, 0x20, 0x80, 0x100
ACCESS_MASK, ACCESS_FAMILY, ACCESS_FAM_OR_ASSEM, ACCESS_PUBLIC = 0x7, 4, 5, 6
M_STATIC, M_VIRTUAL, M_NEWSLOT, M_ABSTRACT, M_SPECIAL = 0x10, 0x40, 0x100, 0x400, 0x800
F_STATIC, F_INITONLY, F_LITERAL, F_SPECIAL = 0x10, 0x20, 0x40, 0x200
P_OUT, P_HAS_DEFAULT = 0x2, 0x1000
SEM_SETTER, SEM_GETTER = 0x1, 0x2


class ApiError(RuntimeError):
    pass


def read_compressed(data: bytes, pos: int) -> tuple[int, int]:
    """ECMA-335 II.23.2 compressed unsigned integer -> (value, next position)."""
    first = data[pos]
    if first & 0x80 == 0:
        return first, pos + 1
    if first & 0xC0 == 0x80:
        return ((first & 0x3F) << 8) | data[pos + 1], pos + 2
    return (((first & 0x1F) << 24) | (data[pos + 1] << 16) | (data[pos + 2] << 8)
            | data[pos + 3]), pos + 4


def strip_arity(name: str) -> str:
    return name.split("`", 1)[0]


# ---------------------------------------------------------------------------------------
# Metadata reader


class Metadata:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        self.rows: dict[int, list[tuple]] = {}
        self._strings: dict[int, str] = {}
        self._read_pe()

    def _read_pe(self) -> None:
        d = self.data
        if d[:2] != b"MZ":
            raise ApiError(f"{self.path} is not a PE file")
        pe = struct.unpack_from("<I", d, 0x3C)[0]
        if d[pe:pe + 4] != b"PE\0\0":
            raise ApiError(f"{self.path} has no PE signature")
        sections, opt_size = struct.unpack_from("<H", d, pe + 6)[0], struct.unpack_from("<H", d, pe + 20)[0]
        opt = pe + 24
        magic = struct.unpack_from("<H", d, opt)[0]
        dirs = opt + (96 if magic == 0x10B else 112)
        cli_rva = struct.unpack_from("<I", d, dirs + 14 * 8)[0]
        if cli_rva == 0:
            raise ApiError(f"{self.path} is not a .NET assembly")
        self.sections = []
        table = opt + opt_size
        for i in range(sections):
            vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", d, table + i * 40 + 8)
            self.sections.append((va, max(vsize, rawsize), rawptr))
        cli = self._offset(cli_rva)
        meta = self._offset(struct.unpack_from("<I", d, cli + 8)[0])
        if struct.unpack_from("<I", d, meta)[0] != 0x424A5342:
            raise ApiError(f"{self.path} has no metadata root")
        version_len = struct.unpack_from("<I", d, meta + 12)[0]
        pos = meta + 16 + version_len + 2
        stream_count = struct.unpack_from("<H", d, pos)[0]
        pos += 2
        streams: dict[str, tuple[int, int]] = {}
        for _ in range(stream_count):
            offset, size = struct.unpack_from("<II", d, pos)
            end = d.index(b"\0", pos + 8)
            name = d[pos + 8:end].decode("ascii")
            pos = (end + 4) & ~3
            streams[name] = (meta + offset, size)
        self.strings_at = streams["#Strings"][0]
        self.blob_at = streams.get("#Blob", (0, 0))[0]
        tables_at = (streams.get("#~") or streams["#-"])[0]
        self._read_tables(tables_at)

    def _offset(self, rva: int) -> int:
        for va, size, raw in self.sections:
            if va <= rva < va + size:
                return rva - va + raw
        raise ApiError(f"RVA {rva:#x} is outside every section of {self.path}")

    def _read_tables(self, at: int) -> None:
        d = self.data
        heap_sizes = d[at + 6]
        valid = struct.unpack_from("<Q", d, at + 8)[0]
        pos = at + 24
        counts: dict[int, int] = {}
        for table in range(64):
            if valid >> table & 1:
                counts[table] = struct.unpack_from("<I", d, pos)[0]
                pos += 4
        self.counts = counts
        string_w = 4 if heap_sizes & 1 else 2
        guid_w = 4 if heap_sizes & 2 else 2
        blob_w = 4 if heap_sizes & 4 else 2

        def width(kind) -> int:
            if isinstance(kind, int):
                return kind
            if kind == "s":
                return string_w
            if kind == "g":
                return guid_w
            if kind == "b":
                return blob_w
            if kind[0] == "t":
                return 2 if counts.get(kind[1], 0) < 1 << 16 else 4
            bits, tables = CODED[kind[1]]
            largest = max((counts.get(t, 0) for t in tables if t is not None), default=0)
            return 2 if largest < 1 << (16 - bits) else 4

        letter = {1: "B", 2: "H", 4: "I"}
        for table in sorted(counts):
            if table not in SCHEMAS:
                raise ApiError(f"{self.path} has unsupported metadata table {table:#x}")
            columns = SCHEMAS[table]
            fmt = "<" + "".join(letter[width(c)] for c in columns)
            size = struct.calcsize(fmt)
            count = counts[table]
            chunk = d[pos:pos + size * count]
            self.rows[table] = list(struct.iter_unpack(fmt, chunk)) if count else []
            pos += size * count

    def string(self, offset: int) -> str:
        cached = self._strings.get(offset)
        if cached is None:
            start = self.strings_at + offset
            end = self.data.index(b"\0", start)
            cached = self.data[start:end].decode("utf-8", "replace")
            self._strings[offset] = cached
        return cached

    def blob(self, offset: int) -> bytes:
        length, pos = read_compressed(self.data, self.blob_at + offset)
        return self.data[pos:pos + length]

    def table(self, table: int) -> list[tuple]:
        return self.rows.get(table, [])


def decode_coded(name: str, value: int) -> tuple[int | None, int]:
    bits, tables = CODED[name]
    tag = value & ((1 << bits) - 1)
    return (tables[tag] if tag < len(tables) else None), value >> bits


# ---------------------------------------------------------------------------------------
# Signatures


@dataclass(frozen=True)
class Sig:
    kind: str                      # prim, def, ref, generic, var, mvar, szarray, array, ptr, byref, fnptr
    code: int = 0                  # primitive code, table row, or generic index
    args: tuple["Sig", ...] = ()
    rank: int = 0


class SigReader:
    def __init__(self, blob: bytes) -> None:
        self.blob, self.pos = blob, 0

    def u(self) -> int:
        value, self.pos = read_compressed(self.blob, self.pos)
        return value

    def byte(self) -> int:
        value = self.blob[self.pos]
        self.pos += 1
        return value

    def type_def_or_ref(self) -> Sig:
        coded = self.u()
        tag, row = coded & 3, coded >> 2
        return Sig({0: "def", 1: "ref", 2: "spec"}[tag], row)

    def type(self) -> Sig:
        b = self.byte()
        while b in (0x1F, 0x20):           # custom modifiers
            self.type_def_or_ref()
            b = self.byte()
        if b == 0x45:                      # pinned
            return self.type()
        if b in PRIMITIVES:
            return Sig("prim", b)
        if b in (0x11, 0x12):
            return self.type_def_or_ref()
        if b == 0x0F:
            return Sig("ptr", args=(self.type(),))
        if b == 0x10:
            return Sig("byref", args=(self.type(),))
        if b == 0x13:
            return Sig("var", self.u())
        if b == 0x1E:
            return Sig("mvar", self.u())
        if b == 0x1D:
            return Sig("szarray", args=(self.type(),))
        if b == 0x14:
            element = self.type()
            rank = self.u()
            for _ in range(self.u()):
                self.u()
            for _ in range(self.u()):
                self.u()
            return Sig("array", args=(element,), rank=rank)
        if b == 0x15:
            self.byte()
            base = self.type_def_or_ref()
            count = self.u()
            return Sig("generic", args=(base,) + tuple(self.type() for _ in range(count)))
        if b == 0x1B:
            self.method()
            return Sig("fnptr")
        raise ApiError(f"unsupported signature element {b:#x}")

    def method(self) -> tuple[int, Sig, list[Sig]]:
        conv = self.byte()
        generic_count = self.u() if conv & 0x10 else 0
        count = self.u()
        ret = self.type()
        params = []
        for _ in range(count):
            if self.pos < len(self.blob) and self.blob[self.pos] == 0x41:   # vararg sentinel
                self.pos += 1
            params.append(self.type())
        return generic_count, ret, params

    def field(self) -> Sig:
        self.byte()
        return self.type()

    def property(self) -> tuple[Sig, list[Sig]]:
        self.byte()
        count = self.u()
        ret = self.type()
        return ret, [self.type() for _ in range(count)]


# ---------------------------------------------------------------------------------------
# Model


@dataclass
class Member:
    kind: str            # method, ctor, field, property, const
    name: str
    access: str          # public / protected
    text: str            # rendered C#-like signature
    doc_id: str
    summary: str = ""


@dataclass
class TypeInfo:
    assembly: "Assembly"
    row: int             # 1-based TypeDef row
    namespace: str
    name: str            # display name with outer types, arity stripped
    full: str            # namespace + doc-id style name with arity
    kind: str
    access: str
    base: Sig | None
    members: list[Member] = field(default_factory=list)
    summary: str = ""

    @property
    def display_full(self) -> str:
        return f"{self.namespace}.{self.name}" if self.namespace else self.name


class Assembly:
    # Simple names that more than one loaded public type uses; rendered with their namespace.
    ambiguous: set[str] = set()

    def __init__(self, tag: str, path: Path) -> None:
        self.tag, self.path = tag, path
        self.md = Metadata(path)
        md = self.md
        self.typedefs = md.table(TYPEDEF)
        self.typerefs = md.table(TYPEREF)
        self.enclosing = {nested: outer for nested, outer in md.table(NESTEDCLASS)}
        self.generic_params: dict[tuple[int, int], list[str]] = {}
        for _number, _flags, owner, name in md.table(GENERICPARAM):
            table, row = decode_coded("TypeOrMethodDef", owner)
            self.generic_params.setdefault((table, row), []).append(md.string(name))
        self.constants = {}
        for type_code_pad, parent, value in md.table(CONSTANT):
            self.constants[decode_coded("HasConstant", parent)] = (type_code_pad & 0xFF, value)
        self.docs = load_docs(path.with_suffix(".xml"))
        self.types: list[TypeInfo] = []

    def public_type_names(self) -> list[tuple[str, str]]:
        """(simple display name, full display name) of every visible type."""
        names = []
        for row in range(1, len(self.typedefs) + 1):
            raw = self.md.string(self.typedefs[row - 1][1])
            if "<" in raw or self.type_access(row) is None:
                continue
            namespace, display, _doc = self.typedef_names(row)
            names.append((display, f"{namespace}.{display}"))
        return names

    # --- names -------------------------------------------------------------------------
    def typedef_names(self, row: int) -> tuple[str, str, str]:
        """(namespace, display name with outer types, doc-id name with arity)."""
        _flags, name, namespace, *_ = self.typedefs[row - 1]
        display, doc = strip_arity(self.md.string(name)), self.md.string(name)
        outer = self.enclosing.get(row)
        if outer:
            ns, outer_display, outer_doc = self.typedef_names(outer)
            return ns, f"{outer_display}.{display}", f"{outer_doc}.{doc}"
        return self.md.string(namespace), display, doc

    def typeref_names(self, row: int) -> tuple[str, str, str]:
        scope, name, namespace = self.typerefs[row - 1]
        display, doc = strip_arity(self.md.string(name)), self.md.string(name)
        table, scope_row = decode_coded("ResolutionScope", scope)
        if table == TYPEREF and scope_row:
            ns, outer_display, outer_doc = self.typeref_names(scope_row)
            return ns, f"{outer_display}.{display}", f"{outer_doc}.{doc}"
        return self.md.string(namespace), display, doc

    def named(self, sig: Sig) -> tuple[str, str, str]:
        if sig.kind == "def":
            return self.typedef_names(sig.code)
        return self.typeref_names(sig.code)

    def spec(self, row: int) -> Sig:
        return SigReader(self.md.blob(self.md.table(TYPESPEC)[row - 1][0])).type()

    def render(self, sig: Sig, type_params: list[str], method_params: list[str]) -> str:
        if sig.kind == "prim":
            return PRIMITIVES[sig.code]
        if sig.kind == "spec":
            return self.render(self.spec(sig.code), type_params, method_params)
        if sig.kind in ("def", "ref"):
            ns, display, _doc = self.named(sig)
            return ALIASES.get(f"{ns}.{display}", self._qualify(ns, display))
        if sig.kind == "generic":
            base, *args = sig.args
            ns, display, _doc = self.named(base)
            rendered = [self.render(a, type_params, method_params) for a in args]
            if ns == "System" and display == "Nullable" and len(rendered) == 1:
                return rendered[0] + "?"
            return f"{self._qualify(ns, display)}<{', '.join(rendered)}>"
        if sig.kind == "var":
            return type_params[sig.code] if sig.code < len(type_params) else f"T{sig.code}"
        if sig.kind == "mvar":
            return method_params[sig.code] if sig.code < len(method_params) else f"TM{sig.code}"
        if sig.kind == "szarray":
            return self.render(sig.args[0], type_params, method_params) + "[]"
        if sig.kind == "array":
            return self.render(sig.args[0], type_params, method_params) + "[" + "," * (sig.rank - 1) + "]"
        if sig.kind == "ptr":
            return self.render(sig.args[0], type_params, method_params) + "*"
        if sig.kind == "byref":
            return self.render(sig.args[0], type_params, method_params)
        return "delegate*"

    @classmethod
    def _qualify(cls, namespace: str, display: str) -> str:
        return f"{namespace}.{display}" if namespace and display in cls.ambiguous else display

    def enum_member(self, sig: Sig, value: str) -> str | None:
        """`Enum.Member` for a numeric default of an enum declared in this assembly."""
        if sig.kind != "def":
            return None
        row = sig.code
        fields = self.md.table(FIELD)
        start = self.typedefs[row - 1][4]
        end = self.typedefs[row][4] if row < len(self.typedefs) else len(fields) + 1
        for f_row in range(start, end):
            if self.fields_flags(f_row) & F_LITERAL and self._constant(FIELD, f_row) == value:
                _ns, display, _doc = self.typedef_names(row)
                return f"{display}.{self.md.string(fields[f_row - 1][1])}"
        return None

    def fields_flags(self, row: int) -> int:
        return self.md.table(FIELD)[row - 1][0]

    def doc_type(self, sig: Sig) -> str:
        """XML documentation ID spelling of a parameter type."""
        if sig.kind == "prim":
            return PRIMITIVE_FULL[sig.code]
        if sig.kind == "spec":
            return self.doc_type(self.spec(sig.code))
        if sig.kind in ("def", "ref"):
            ns, _display, doc = self.named(sig)
            return f"{ns}.{doc}" if ns else doc
        if sig.kind == "generic":
            base, *args = sig.args
            ns, _display, doc = self.named(base)
            name = re.sub(r"`\d+", "", f"{ns}.{doc}" if ns else doc)
            return f"{name}{{{','.join(self.doc_type(a) for a in args)}}}"
        if sig.kind == "var":
            return f"`{sig.code}"
        if sig.kind == "mvar":
            return f"``{sig.code}"
        if sig.kind == "szarray":
            return self.doc_type(sig.args[0]) + "[]"
        if sig.kind == "array":
            return self.doc_type(sig.args[0]) + "[" + ",".join(["0:"] * sig.rank) + "]"
        if sig.kind == "ptr":
            return self.doc_type(sig.args[0]) + "*"
        if sig.kind == "byref":
            return self.doc_type(sig.args[0]) + "@"
        return "System.IntPtr"

    # --- build -------------------------------------------------------------------------
    def type_access(self, row: int) -> str | None:
        visibility = self.typedefs[row - 1][0] & TYPE_VISIBILITY
        if visibility == 1:
            return "public"
        if visibility in (2, 4, 7):
            outer = self.enclosing.get(row)
            outer_access = self.type_access(outer) if outer else None
            if outer_access is None:
                return None
            return "public" if visibility == 2 and outer_access == "public" else "protected"
        return None

    def build(self) -> None:
        md = self.md
        typedefs = self.typedefs
        fields, methods, params = md.table(FIELD), md.table(METHODDEF), md.table(PARAM)
        property_ranges = self._ranges(md.table(PROPERTYMAP), len(md.table(PROPERTY)))
        accessors: dict[int, dict[int, int]] = {}
        for semantics, method, association in md.table(METHODSEMANTICS):
            table, row = decode_coded("HasSemantics", association)
            if table == PROPERTY:
                accessors.setdefault(row, {})[semantics] = method
        for index, (flags, name, _ns, extends, field_list, method_list) in enumerate(typedefs):
            row = index + 1
            raw_name = md.string(name)
            if raw_name == "<Module>" or "<" in raw_name:
                continue
            access = self.type_access(row)
            if access is None:
                continue
            namespace, display, doc = self.typedef_names(row)
            table, base_row = decode_coded("TypeDefOrRef", extends)
            base = None
            if base_row:
                base = Sig({TYPEDEF: "def", TYPEREF: "ref", TYPESPEC: "spec"}[table], base_row)
            info = TypeInfo(self, row, namespace, display, f"{namespace}.{doc}" if namespace else doc,
                            self._type_kind(flags, base), access, base)
            info.summary = self.docs.get(f"T:{info.full}", "")
            type_params = self._type_params(row)
            field_end = typedefs[row][4] if row < len(typedefs) else len(fields) + 1
            method_end = typedefs[row][5] if row < len(typedefs) else len(methods) + 1
            for f_row in range(field_list, field_end):
                member = self._field(info, f_row, fields[f_row - 1], type_params)
                if member:
                    info.members.append(member)
            for m_row in range(method_list, method_end):
                member = self._method(info, m_row, methods, params, type_params)
                if member:
                    info.members.append(member)
            for p_row in property_ranges.get(row, ()):
                member = self._property(info, p_row, accessors.get(p_row, {}), methods, type_params)
                if member:
                    info.members.append(member)
            self.types.append(info)

    @staticmethod
    def _ranges(map_rows: list[tuple], total: int) -> dict[int, range]:
        result = {}
        for i, (parent, start) in enumerate(map_rows):
            end = map_rows[i + 1][1] if i + 1 < len(map_rows) else total + 1
            result[parent] = range(start, end)
        return result

    def _type_kind(self, flags: int, base: Sig | None) -> str:
        if flags & TYPE_INTERFACE:
            return "interface"
        base_name = ""
        if base is not None and base.kind in ("def", "ref"):
            ns, display, _ = self.named(base)
            base_name = f"{ns}.{display}"
        if base_name == "System.Enum":
            return "enum"
        if base_name == "System.ValueType":
            return "struct"
        if base_name == "System.MulticastDelegate":
            return "delegate"
        if flags & TYPE_ABSTRACT and flags & TYPE_SEALED:
            return "static class"
        if flags & TYPE_ABSTRACT:
            return "abstract class"
        if flags & TYPE_SEALED:
            return "sealed class"
        return "class"

    def _type_params(self, row: int) -> list[str]:
        names: list[str] = []
        outer = self.enclosing.get(row)
        own = self.generic_params.get((TYPEDEF, row), [])
        if outer and not own:
            names = self._type_params(outer)
        return own or names

    @staticmethod
    def _access(flags: int) -> str | None:
        access = flags & ACCESS_MASK
        if access == ACCESS_PUBLIC:
            return "public"
        if access in (ACCESS_FAMILY, ACCESS_FAM_OR_ASSEM):
            return "protected"
        return None

    def _constant(self, table: int, row: int) -> str | None:
        found = self.constants.get((table, row))
        if found is None:
            return None
        code, value = found
        data = self.md.blob(value)
        if code == 0x02:
            return "true" if data and data[0] else "false"
        if code == 0x0E:
            return '"' + data.decode("utf-16-le") + '"'
        if code == 0x12:
            return "null"
        formats = {0x03: "<H", 0x04: "<b", 0x05: "<B", 0x06: "<h", 0x07: "<H", 0x08: "<i",
                   0x09: "<I", 0x0A: "<q", 0x0B: "<Q", 0x0C: "<f", 0x0D: "<d"}
        if code in formats and len(data) >= struct.calcsize(formats[code]):
            number = struct.unpack_from(formats[code], data)[0]
            return repr(chr(number)) if code == 0x03 else str(number)
        return None

    def _field(self, info: TypeInfo, row: int, entry: tuple, type_params: list[str]) -> Member | None:
        flags, name, signature = entry
        access = self._access(flags)
        name = self.md.string(name)
        if access is None or flags & F_SPECIAL or "<" in name:
            return None
        sig = SigReader(self.md.blob(signature)).field()
        type_text = self.render(sig, type_params, [])
        doc_id = f"F:{info.full}.{name}"
        if info.kind == "enum":
            value = self._constant(FIELD, row)
            return Member("const", name, access, f"{name} = {value}", doc_id, self.docs.get(doc_id, ""))
        if flags & F_LITERAL:
            value = self._constant(FIELD, row)
            text = f"{access} const {type_text} {name} = {value}"
            return Member("const", name, access, text, doc_id, self.docs.get(doc_id, ""))
        mods = " static" if flags & F_STATIC else ""
        mods += " readonly" if flags & F_INITONLY else ""
        return Member("field", name, access, f"{access}{mods} {type_text} {name}", doc_id,
                      self.docs.get(doc_id, ""))

    def _method(self, info: TypeInfo, row: int, methods: list[tuple], params: list[tuple],
                type_params: list[str]) -> Member | None:
        _rva, _impl, flags, name, signature, param_list = methods[row - 1]
        name = self.md.string(name)
        access = self._access(flags)
        if access is None or name == ".cctor" or "<" in name:
            return None
        if flags & M_SPECIAL and name != ".ctor":
            return None
        method_params = self.generic_params.get((METHODDEF, row), [])
        generic_count, ret, arg_sigs = SigReader(self.md.blob(signature)).method()
        param_end = methods[row][5] if row < len(methods) else len(params) + 1
        names: dict[int, tuple[str, int, int]] = {}
        for p_row in range(param_list, param_end):
            p_flags, sequence, p_name = params[p_row - 1]
            names[sequence] = (self.md.string(p_name), p_flags, p_row)
        rendered = []
        for i, arg in enumerate(arg_sigs, start=1):
            p_name, p_flags, p_row = names.get(i, (f"arg{i}", 0, 0))
            text = self.render(arg, type_params, method_params)
            if arg.kind == "byref":
                text = ("out " if p_flags & P_OUT else "ref ") + text
            text += f" {p_name}"
            if p_flags & P_HAS_DEFAULT:
                default = self._constant(PARAM, p_row)
                if default is not None:
                    default = self.enum_member(arg, default) or default
                text += f" = {default if default is not None else 'default'}"
            rendered.append(text)
        doc_args = ",".join(self.doc_type(a) for a in arg_sigs)
        doc_name = "#ctor" if name == ".ctor" else name.replace(".", "#")
        doc_id = f"M:{info.full}.{doc_name}" + (f"``{generic_count}" if generic_count else "")
        doc_id += f"({doc_args})" if arg_sigs else ""
        generic = f"<{', '.join(method_params)}>" if method_params else ""
        if name == ".ctor":
            text = f"{access} {info.name.rsplit('.', 1)[-1]}({', '.join(rendered)})"
            return Member("ctor", info.name.rsplit('.', 1)[-1], access, text, doc_id,
                          self.docs.get(doc_id, ""))
        mods = ""
        if flags & M_STATIC:
            mods = " static"
        elif flags & M_ABSTRACT and info.kind != "interface":
            mods = " abstract"
        elif flags & M_VIRTUAL and info.kind != "interface":
            mods = " virtual" if flags & M_NEWSLOT else " override"
        ret_text = self.render(ret, type_params, method_params)
        text = f"{access}{mods} {ret_text} {name}{generic}({', '.join(rendered)})"
        return Member("method", name, access, text, doc_id, self.docs.get(doc_id, ""))

    def _property(self, info: TypeInfo, row: int, accessor: dict[int, int], methods: list[tuple],
                  type_params: list[str]) -> Member | None:
        _flags, name, signature = self.md.table(PROPERTY)[row - 1]
        name = self.md.string(name)
        visible = {}
        for semantics in (SEM_GETTER, SEM_SETTER):
            method = accessor.get(semantics)
            if method:
                access = self._access(methods[method - 1][2])
                if access:
                    visible[semantics] = (access, methods[method - 1][2])
        if not visible or "<" in name:
            return None
        access = "public" if any(a == "public" for a, _ in visible.values()) else "protected"
        flags = next(iter(visible.values()))[1]
        ret, index_sigs = SigReader(self.md.blob(signature)).property()
        mods = ""
        if flags & M_STATIC:
            mods = " static"
        elif flags & M_ABSTRACT and info.kind != "interface":
            mods = " abstract"
        elif flags & M_VIRTUAL and info.kind != "interface":
            mods = " virtual" if flags & M_NEWSLOT else " override"
        parts = []
        for semantics, word in ((SEM_GETTER, "get"), (SEM_SETTER, "set")):
            if semantics in visible:
                own = visible[semantics][0]
                parts.append(word if own == access else f"{own} {word}")
        type_text = self.render(ret, type_params, [])
        shown = name
        doc_id = f"P:{info.full}.{name}"
        if index_sigs:
            shown = "this[" + ", ".join(self.render(s, type_params, []) for s in index_sigs) + "]"
            doc_id += "(" + ",".join(self.doc_type(s) for s in index_sigs) + ")"
        text = f"{access}{mods} {type_text} {shown} {{ {'; '.join(parts)}; }}"
        return Member("property", name, access, text, doc_id, self.docs.get(doc_id, ""))


# ---------------------------------------------------------------------------------------
# XML documentation


def doc_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    parts: list[str] = []

    def walk(node: ET.Element) -> None:
        if node.text:
            parts.append(node.text)
        for child in node:
            ref = child.attrib.get("cref") or child.attrib.get("name") or child.attrib.get("langword")
            if child.tag in ("see", "seealso", "paramref", "typeparamref") and ref:
                parts.append(re.sub(r"\(.*", "", ref.split(":", 1)[-1]).rsplit(".", 1)[-1])
            else:
                walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(element)
    return " ".join("".join(parts).split())


def load_docs(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    docs = {}
    for member in root.iter("member"):
        name = member.attrib.get("name")
        summary = doc_text(member.find("summary"))
        if name and summary:
            docs[name] = summary
    return docs


# ---------------------------------------------------------------------------------------
# Discovery and CLI


DATA_DIRS = (
    "data_sts2_windows_x86_64",
    "data_sts2_linuxbsd_x86_64",
    "SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64",
    "SlayTheSpire2.app/Contents/Resources/data_sts2_macos_x86_64",
)


def game_data_dir(game_dir: Path) -> Path:
    for relative in DATA_DIRS:
        candidate = game_dir / relative
        if (candidate / "sts2.dll").is_file():
            return candidate
    raise ApiError(f"sts2.dll not found under {game_dir}; pass --game-dir")


def locate_assemblies(game_dir: Path | None, runtime_dir: Path | None,
                      godot: bool) -> tuple[list[tuple[str, Path]], list[str]]:
    from launch import default_game_dir
    from ritsu_profile import PROFILE, RitsuProfileError, local_mods_dir, resolve_runtime_asset

    game = game_dir or default_game_dir()
    data = game_data_dir(game)
    found = [("sts2", data / "sts2.dll")]
    if godot:
        found.append(("godot", data / "GodotSharp.dll"))
    notes = []
    try:
        runtime = resolve_runtime_asset(game, local_mods_dir(game), runtime_dir).path
        for name, relative in PROFILE.assembly_relative_paths():
            path = runtime / relative
            if path.is_file():
                found.append((name.replace("STS2-RitsuLib", "ritsulib").lower(), path))
            else:
                notes.append(f"RitsuLib module missing: {path}")
    except RitsuProfileError as exc:
        notes.append(f"RitsuLib not searched: {exc}")
    return found, notes


def load_all(paths: list[tuple[str, Path]]) -> list[Assembly]:
    assemblies = [Assembly(tag, path) for tag, path in paths]
    full_names: dict[str, set[str]] = {}
    for assembly in assemblies:
        for simple, full in assembly.public_type_names():
            full_names.setdefault(simple, set()).add(full)
    Assembly.ambiguous = {simple for simple, fulls in full_names.items() if len(fulls) > 1}
    for assembly in assemblies:
        assembly.build()
    return assemblies


def match_types(assemblies: list[Assembly], query: str) -> list[TypeInfo]:
    needle = query.casefold()
    all_types = [t for a in assemblies for t in a.types]
    if "." in query:
        exact = [t for t in all_types if t.display_full.casefold() == needle
                 or t.display_full.casefold().endswith("." + needle)]
    else:
        exact = [t for t in all_types if t.name.rsplit(".", 1)[-1].casefold() == needle]
    if exact:
        return exact
    return [t for t in all_types if needle in t.display_full.casefold()]


def base_chain(info: TypeInfo, by_full: dict[str, TypeInfo]) -> list[TypeInfo]:
    chain = []
    current = info
    while current.base is not None and len(chain) < 20:
        base = current.base
        asm = current.assembly
        if base.kind == "spec":
            spec = asm.spec(base.code)
            base = spec.args[0] if spec.kind == "generic" else spec
        if base.kind not in ("def", "ref"):
            break
        ns, display, _ = asm.named(base)
        parent = by_full.get(f"{ns}.{display}" if ns else display)
        if parent is None:
            break
        chain.append(parent)
        current = parent
    return chain


def member_matches(member: Member, needle: str | None) -> bool:
    return needle is None or needle.casefold() in member.name.casefold()


def describe_base(info: TypeInfo) -> str:
    if info.base is None or info.kind in ("enum", "struct", "delegate"):
        return ""
    base = info.base
    text = info.assembly.render(base, info.assembly._type_params(info.row), [])
    return "" if text == "object" else f" : {text}"


def print_member(member: Member, prefix: str = "  ") -> None:
    print(f"{prefix}{member.text}")
    if member.summary:
        summary = member.summary if len(member.summary) <= 200 else member.summary[:197] + "..."
        print(f"{prefix}    // {summary}")


def cmd_search(assemblies: list[Assembly], type_query: str, member_query: str | None = None) -> int:
    types = match_types(assemblies, type_query)
    if not types:
        print(f"[api] no public type matches '{type_query}'")
        return 1
    by_full = {t.display_full: t for a in assemblies for t in a.types}
    shown_types = types[:MAX_TYPES]
    any_member = False
    for info in shown_types:
        own_params = info.assembly.generic_params.get((TYPEDEF, info.row), [])
        generic = f"<{', '.join(own_params)}>" if own_params else ""
        print(f"[{info.assembly.tag}] {info.access} {info.kind} "
              f"{info.display_full}{generic}{describe_base(info)}")
        if info.summary:
            print(f"    // {info.summary[:300]}")
        own = [m for m in info.members if member_matches(m, member_query)]
        for member in own[:MAX_MEMBERS_PER_TYPE]:
            print_member(member)
        if len(own) > MAX_MEMBERS_PER_TYPE:
            print(f"  ... {len(own) - MAX_MEMBERS_PER_TYPE} more; add a member filter")
        any_member = any_member or bool(own)
        if member_query is not None:
            for parent in base_chain(info, by_full):
                inherited = [m for m in parent.members if member_matches(m, member_query)
                             and m.kind != "ctor"]
                if inherited:
                    any_member = True
                    print(f"  (inherited from {parent.display_full})")
                    for member in inherited[:MAX_MEMBERS_PER_TYPE]:
                        print_member(member, "    ")
    if len(types) > MAX_TYPES:
        print(f"[api] {len(types) - MAX_TYPES} more matching types; use a longer or dotted name")
    if member_query is not None and not any_member:
        print(f"[api] no public member of the matched types contains '{member_query}'; "
              f"try: api.py find {member_query}")
        return 1
    return 0


def cmd_find(assemblies: list[Assembly], member_query: str) -> int:
    needle = member_query.casefold()
    hits = [(t, m) for a in assemblies for t in a.types for m in t.members
            if m.name.casefold() == needle]
    if not hits:
        hits = [(t, m) for a in assemblies for t in a.types for m in t.members
                if needle in m.name.casefold()]
    if not hits:
        print(f"[api] no public member named like '{member_query}'")
        return 1
    for info, member in hits[:MAX_FIND_RESULTS]:
        print(f"[{info.assembly.tag}] {info.display_full}")
        print_member(member)
    if len(hits) > MAX_FIND_RESULTS:
        print(f"[api] {len(hits) - MAX_FIND_RESULTS} more; add a type: api.py search <Type> {member_query}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Look up public STS2/RitsuLib API signatures.")
    parser.add_argument("--game-dir", type=Path, default=None, help="STS2 install directory")
    parser.add_argument("--runtime-dir", type=Path, default=None,
                        help="installed RitsuLib runtime directory (default: as scaffold resolves it)")
    parser.add_argument("--godot", action="store_true", help="also search GodotSharp.dll")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="members of the types matching TYPE")
    search.add_argument("type")
    search.add_argument("member", nargs="?")
    find = sub.add_parser("find", help="public types that declare MEMBER")
    find.add_argument("member")
    args = parser.parse_args(argv)
    try:
        paths, notes = locate_assemblies(args.game_dir, args.runtime_dir, args.godot)
        assemblies = load_all(paths)
    except (ApiError, OSError) as exc:
        print(f"[api] {exc}", file=sys.stderr)
        return 2
    for note in notes:
        print(f"[api] {note}", file=sys.stderr)
    if args.command == "search":
        return cmd_search(assemblies, args.type, args.member)
    return cmd_find(assemblies, args.member)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
