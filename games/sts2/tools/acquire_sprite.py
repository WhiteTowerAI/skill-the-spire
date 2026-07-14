#!/usr/bin/env python3
"""Acquire one image through Vofy, then normalize it with gen_sprite.py import.

This tool deliberately owns only the managed-credit CLI boundary. It never logs in,
reads credentials, parses Vofy's human output for filenames, or implements STS2 image
processing. A successful synchronous job must download exactly one image into an
isolated directory; that file is then passed to the existing gen_sprite.py import
command.

The caller must show the user the prompt, model, output count, and paid action before
passing --yes. Missing setup or any failed/ambiguous job exits nonzero so the modmaker
can offer BYO HTTP, local import, or placeholder art without making a second charge.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ICON_SPECS = {"relic", "power", "potion"}


class AcquisitionError(Exception):
    """A bounded acquisition failure with a user-actionable message."""

    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


def command_prefix(command: str) -> list[str]:
    """Resolve a CLI executable; Python paths are supported for local test doubles."""
    candidate = Path(command)
    if candidate.suffix.lower() == ".py" and candidate.is_file():
        return [sys.executable, str(candidate.resolve())]

    resolved = shutil.which(command)
    if not resolved:
        raise AcquisitionError(
            "Vofy CLI was not found. Install and authenticate it yourself, then run "
            "`vofy status`; open-mod will never install it or launch `vofy login`.",
            2,
        )
    return [resolved]


def run_quiet(command: list[str], timeout: float, failure: str) -> None:
    """Run without echoing account, credit, task, or generated-resource output."""
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AcquisitionError(
            f"{failure} timed out. Do not submit it again automatically; inspect "
            "`vofy tasks --plain` first to avoid a second charge.",
            5,
        ) from exc
    except OSError as exc:
        raise AcquisitionError(f"{failure} could not start: {exc}", 2) from exc
    if result.returncode != 0:
        raise AcquisitionError(f"{failure} (Vofy exit {result.returncode}).", 3)


def preflight(prefix: list[str], model: str, timeout: float) -> None:
    run_quiet(
        [*prefix, "status"],
        timeout,
        "Vofy status/auth/credits check failed; authenticate or resolve the account "
        "issue yourself with `vofy status`",
    )
    run_quiet(
        [*prefix, "models", model],
        timeout,
        f"Vofy model capability lookup failed for {model!r}; choose a model shown by "
        "`vofy models --type image`",
    )


def image_files(directory: Path) -> list[Path]:
    return sorted(
        path for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def single_line_prompt(prompt: str) -> str:
    """Keep the complete prompt while making it safe for Windows CLI shims."""
    return " ".join(prompt.split())


def import_source(args: argparse.Namespace, source: Path) -> Path:
    gen_sprite = Path(__file__).with_name("gen_sprite.py")
    command = [
        sys.executable,
        str(gen_sprite),
        "import",
        "--spec",
        args.spec,
        "--slug",
        args.slug,
        "--input",
        str(source),
        "--out",
        str(Path(args.out)),
    ]
    if args.spec in ICON_SPECS:
        command.append("--chroma")
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise AcquisitionError(
            "Vofy downloaded one image, but deterministic gen_sprite.py import failed. "
            "Keep the mod on placeholder art until the local image/import issue is fixed.",
            7,
        )

    output_lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not output_lines:
        raise AcquisitionError(
            "gen_sprite.py import succeeded but returned no destination path.", 7
        )
    return Path(output_lines[-1])


def cmd_preflight(args: argparse.Namespace) -> int:
    prefix = command_prefix(args.vofy_command)
    preflight(prefix, args.model, args.preflight_timeout)
    print(f"[acquire_sprite] Vofy is ready and model {args.model!r} is available.")
    print("Review `vofy models <model>` before selecting reference, ratio, or resolution flags.")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    prompt = single_line_prompt(args.prompt)
    if not prompt:
        raise AcquisitionError("The image prompt cannot be empty or whitespace-only.", 2)

    if not args.yes:
        raise AcquisitionError(
            "Paid generation was not approved. Show the user the final prompt, model, "
            "output count (1), and credit-spending action; pass --yes only after they agree.",
            2,
        )

    references = [Path(item).resolve() for item in args.reference]
    missing = [str(path) for path in references if not path.is_file()]
    if missing:
        raise AcquisitionError(f"Reference image not found: {missing[0]}", 2)
    if len(references) > 3:
        raise AcquisitionError("Use at most three STS2 style reference images.", 2)

    prefix = command_prefix(args.vofy_command)
    preflight(prefix, args.model, args.preflight_timeout)

    with tempfile.TemporaryDirectory(prefix="open-mod-vofy-") as tmp:
        download_dir = Path(tmp)
        command = [
            *prefix,
            "image",
            "create",
            "--model",
            args.model,
            "--prompt",
            prompt,
            "--yes",
            "--n",
            "1",
            "--download-to",
            str(download_dir),
        ]
        if args.aspect_ratio:
            command.extend(["--aspect-ratio", args.aspect_ratio])
        if args.resolution:
            command.extend(["--resolution", args.resolution])
        for reference in references:
            command.extend(["--image", str(reference)])

        run_quiet(
            command,
            args.generation_timeout,
            "Vofy image generation failed; inspect `vofy tasks --plain` before deciding "
            "whether to recover the task or fall back",
        )

        downloaded = image_files(download_dir)
        if len(downloaded) != 1:
            raise AcquisitionError(
                "Vofy completed but the isolated download directory contained "
                f"{len(downloaded)} images; expected exactly 1. Nothing was imported and "
                "open-mod will not submit another paid task automatically.",
                6,
            )
        destination = import_source(args, downloaded[0])

    print(f"[acquire_sprite] acquired and imported {args.spec} {args.slug!r}")
    print(str(destination))
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", required=True, help="model selected after `vofy models`")
    parser.add_argument("--vofy-command", default="vofy", help=argparse.SUPPRESS)
    parser.add_argument("--preflight-timeout", type=float, default=30.0, help=argparse.SUPPRESS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Acquire one paid Vofy image, then use gen_sprite.py import."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("preflight", help="Check existing Vofy auth/account and model availability.")
    add_common(check)
    check.set_defaults(func=cmd_preflight)

    create = sub.add_parser("create", help="Create one approved image and import it into an STS2 mod.")
    add_common(create)
    create.add_argument("--spec", required=True, choices=("card", "relic", "power", "potion"))
    create.add_argument("--slug", required=True)
    create.add_argument("--prompt", required=True)
    create.add_argument("--out", required=True, help="the mod's <ModName>/images directory")
    create.add_argument("--reference", action="append", default=[], help="supported STS2 style image; repeat up to three times")
    create.add_argument("--aspect-ratio", help="only after confirming support with `vofy models <model>`")
    create.add_argument("--resolution", help="only after confirming support with `vofy models <model>`")
    create.add_argument("--generation-timeout", type=float, default=600.0, help="synchronous task timeout in seconds (default 600)")
    create.add_argument("--yes", action="store_true", help="assert that the user approved this exact paid generation")
    create.set_defaults(func=cmd_create)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except AcquisitionError as exc:
        print(f"[acquire_sprite] {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    sys.exit(main())
