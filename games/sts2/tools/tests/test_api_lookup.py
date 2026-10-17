from __future__ import annotations

import contextlib
import io
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import api  # noqa: E402


def core_library() -> Path | None:
    """System.Runtime.dll from any installed Microsoft.NETCore.App, as a metadata fixture."""
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        return None
    try:
        listing = subprocess.run([dotnet, "--list-runtimes"], capture_output=True, text=True,
                                 timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    for line in listing.splitlines():
        match = re.match(r"Microsoft\.NETCore\.App (\S+) \[(.+)\]", line.strip())
        if match:
            candidate = Path(match.group(2)) / match.group(1) / "System.Private.CoreLib.dll"
            if candidate.is_file():
                return candidate
    return None


class EncodingTests(unittest.TestCase):
    def test_compressed_integers(self) -> None:
        self.assertEqual((0x03, 1), api.read_compressed(bytes([0x03]), 0))
        self.assertEqual((0x80, 2), api.read_compressed(bytes([0x80, 0x80]), 0))
        self.assertEqual((0x3FFF, 2), api.read_compressed(bytes([0xBF, 0xFF]), 0))
        self.assertEqual((0x4000, 4), api.read_compressed(bytes([0xC0, 0x00, 0x40, 0x00]), 0))

    def test_method_signature_with_generic_byref_and_array(self) -> None:
        # static !!0 M<T>(int, ref string, T[]) with one generic parameter.
        blob = bytes([0x10, 0x01, 0x03, 0x1E, 0x00, 0x08, 0x10, 0x0E, 0x1D, 0x1E, 0x00])
        generic_count, ret, params = api.SigReader(blob).method()
        self.assertEqual(1, generic_count)
        self.assertEqual(api.Sig("mvar", 0), ret)
        self.assertEqual([api.Sig("prim", 0x08), api.Sig("byref", args=(api.Sig("prim", 0x0E),)),
                          api.Sig("szarray", args=(api.Sig("mvar", 0),))], params)

    def test_doc_text_keeps_cref_names(self) -> None:
        element = api.ET.fromstring(
            '<summary>Use <see cref="M:A.B.AfterPlayerTurnStart(X)"/> for a\n   choice.</summary>')
        self.assertEqual("Use AfterPlayerTurnStart for a choice.", api.doc_text(element))


@unittest.skipIf(core_library() is None, "no installed .NET runtime to read as a fixture")
class CoreLibraryLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assemblies = api.load_all([("corelib", core_library())])

    def run_cmd(self, fn, *args) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = fn(self.assemblies, *args)
        return code, output.getvalue()

    def test_generic_type_members_render_like_csharp(self) -> None:
        code, output = self.run_cmd(api.cmd_search, "System.Collections.Generic.List", "ConvertAll")
        self.assertEqual(0, code, output)
        self.assertIn("public class System.Collections.Generic.List<T>", output)
        self.assertIn("List<TOutput> ConvertAll<TOutput>(Converter<T, TOutput> converter)", output)

    def test_properties_constants_and_enums(self) -> None:
        _code, output = self.run_cmd(api.cmd_search, "System.String", "Length")
        self.assertIn("public int Length { get; }", output)
        _code, output = self.run_cmd(api.cmd_search, "System.Int32", "MaxValue")
        self.assertIn("public const int MaxValue = 2147483647", output)
        _code, output = self.run_cmd(api.cmd_search, "System.DayOfWeek")
        self.assertIn("Monday = 1", output)

    def test_defaults_and_out_parameters(self) -> None:
        _code, output = self.run_cmd(api.cmd_search, "System.Int32", "TryParse")
        self.assertIn("out int result", output)
        _code, output = self.run_cmd(api.cmd_search, "System.String", "Split")
        self.assertRegex(output, r"StringSplitOptions options = StringSplitOptions\.None")

    def test_inherited_members_follow_the_base_chain(self) -> None:
        code, output = self.run_cmd(api.cmd_search, "System.ArgumentNullException", "HResult")
        self.assertEqual(0, code, output)
        self.assertIn("(inherited from System.Exception)", output)

    def test_find_and_missing_member(self) -> None:
        code, output = self.run_cmd(api.cmd_find, "IsNullOrWhiteSpace")
        self.assertEqual(0, code)
        self.assertIn("System.String", output)
        code, output = self.run_cmd(api.cmd_search, "System.String", "NoSuchMemberAnywhere")
        self.assertEqual(1, code)
        self.assertIn("api.py find NoSuchMemberAnywhere", output)

    def test_private_members_are_hidden(self) -> None:
        _code, output = self.run_cmd(api.cmd_search, "System.String")
        self.assertNotIn("_stringLength", output)


if __name__ == "__main__":
    unittest.main()
