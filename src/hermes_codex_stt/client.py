"""Codex Desktop transcription client."""

from __future__ import annotations

import json
import mimetypes
import platform
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from hermes_codex_stt.auth import (
    AuthError,
    CodexCredentials,
    default_auth_path,
    read_credentials,
    refresh_credentials,
)
from hermes_codex_stt.constants import (
    DEFAULT_MAX_AUDIO_BYTES,
    DEFAULT_TIMEOUT_SECONDS,
    MULTIPART_FILE_FIELD,
    ORIGINATOR,
    RESPONSE_TEXT_FIELD,
    TRANSCRIPTION_ENDPOINT,
    TRANSCRIPTION_HOST,
)


class TranscriptionError(RuntimeError):
    """A safe, user-facing transcription failure."""


class UnauthorizedError(TranscriptionError):
    """The cached Codex access token is no longer accepted."""


def _content_type(audio_path: Path) -> str:
    overrides = {
        ".oga": "audio/ogg",
        ".ogg": "audio/ogg",
        ".opus": "audio/ogg",
        ".m4a": "audio/mp4",
    }
    return overrides.get(
        audio_path.suffix.lower(),
        mimetypes.guess_type(audio_path.name)[0] or "application/octet-stream",
    )


def _safe_filename(audio_path: Path) -> str:
    filename = audio_path.name
    for unsafe in ("\\", '"', "\r", "\n"):
        filename = filename.replace(unsafe, "_")
    return filename or "audio"


def _multipart_body(audio_path: Path) -> tuple[bytes, str]:
    boundary = f"----hermes-codex-stt-{uuid.uuid4().hex}"
    prefix = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{MULTIPART_FILE_FIELD}"; '
        f'filename="{_safe_filename(audio_path)}"\r\n'
        f"Content-Type: {_content_type(audio_path)}\r\n\r\n"
    ).encode("utf-8")
    suffix = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return prefix + audio_path.read_bytes() + suffix, boundary


def _validate_endpoint() -> None:
    parsed = urlparse(TRANSCRIPTION_ENDPOINT)
    if parsed.scheme != "https" or parsed.hostname != TRANSCRIPTION_HOST:
        raise TranscriptionError(
            "Refusing to send Codex credentials to an unexpected endpoint"
        )


def _request_transcript(
    audio_path: Path,
    credentials: CodexCredentials,
    *,
    timeout: float,
) -> str:
    _validate_endpoint()
    body, boundary = _multipart_body(audio_path)
    system = platform.system() or "unknown"
    machine = platform.machine() or "unknown"

    request = Request(
        TRANSCRIPTION_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {credentials.access_token}",
            "ChatGPT-Account-Id": credentials.account_id,
            "originator": ORIGINATOR,
            "User-Agent": f"Codex Desktop/unknown ({system}; {machine})",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_data = response.read()
    except HTTPError as exc:
        if exc.code == 401:
            raise UnauthorizedError("Codex auth expired") from exc
        raise TranscriptionError(
            f"Codex transcription backend returned HTTP {exc.code}"
        ) from exc
    except URLError as exc:
        raise TranscriptionError(
            f"Codex transcription backend is unavailable: {exc.reason}"
        ) from exc

    try:
        payload = json.loads(response_data)
        text = payload[RESPONSE_TEXT_FIELD]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise TranscriptionError(
            "Codex transcription backend returned an incompatible response"
        ) from exc

    if not isinstance(text, str):
        raise TranscriptionError("Codex transcription response has no text")
    return text.strip()


def transcribe_audio(
    audio_path: Path,
    *,
    auth_path: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_audio_bytes: int = DEFAULT_MAX_AUDIO_BYTES,
) -> str:
    audio_path = audio_path.expanduser().resolve()
    if not audio_path.is_file():
        raise TranscriptionError(f"Audio file does not exist: {audio_path}")

    size = audio_path.stat().st_size
    if size == 0:
        raise TranscriptionError("Audio file is empty")
    if size > max_audio_bytes:
        limit_mib = max_audio_bytes // (1024 * 1024)
        raise TranscriptionError(f"Audio file exceeds the {limit_mib} MiB limit")

    resolved_auth_path = (auth_path or default_auth_path()).expanduser()
    try:
        credentials = read_credentials(resolved_auth_path)
        try:
            return _request_transcript(
                audio_path,
                credentials,
                timeout=timeout,
            )
        except UnauthorizedError:
            refreshed = refresh_credentials(resolved_auth_path)
            return _request_transcript(
                audio_path,
                refreshed,
                timeout=timeout,
            )
    except AuthError as exc:
        raise TranscriptionError(str(exc)) from exc
