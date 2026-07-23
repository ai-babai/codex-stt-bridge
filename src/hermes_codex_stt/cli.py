"""Command-line interface for Hermes Codex STT."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from hermes_codex_stt import __version__
from hermes_codex_stt.client import TranscriptionError, transcribe_audio
from hermes_codex_stt.constants import DEFAULT_TIMEOUT_SECONDS


def write_transcript(output_path: Path, transcript: str) -> None:
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(transcript)
            temporary.write("\n")
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, output_path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe audio using the current Codex Desktop OAuth session"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--input", required=True, type=Path, help="input audio file")
    parser.add_argument("--output", type=Path, help="UTF-8 transcript file")
    parser.add_argument(
        "--language",
        help="accepted for Hermes compatibility; Codex currently auto-detects it",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument("--auth-path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0:
        print("codex-stt: --timeout must be positive", file=sys.stderr)
        return 2

    try:
        transcript = transcribe_audio(
            args.input,
            auth_path=args.auth_path,
            timeout=args.timeout,
        )
        if args.output:
            write_transcript(args.output, transcript)
        else:
            print(transcript)
    except TranscriptionError as exc:
        print(f"codex-stt: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
