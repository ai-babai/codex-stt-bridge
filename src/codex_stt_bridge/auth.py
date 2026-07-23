"""Read and refresh the existing local Codex OAuth session."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess  # nosec B404
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AuthError(RuntimeError):
    """A safe, user-facing authentication failure."""


@dataclass(frozen=True)
class CodexCredentials:
    access_token: str
    account_id: str


def default_auth_path() -> Path:
    configured = os.environ.get("CODEX_AUTH_PATH", "~/.codex/auth.json")
    return Path(configured).expanduser()


def read_credentials(auth_path: Path) -> CodexCredentials:
    try:
        auth_stat = auth_path.stat()
    except FileNotFoundError as exc:
        raise AuthError(
            f"Codex auth is missing at {auth_path}; run `codex login` first"
        ) from exc

    if os.name == "posix":
        permissions = stat.S_IMODE(auth_stat.st_mode)
        if permissions & 0o077:
            raise AuthError(
                f"Codex auth permissions are too broad ({permissions:o}); "
                f"run `chmod 600 {auth_path}`"
            )

    try:
        payload = json.loads(auth_path.read_text(encoding="utf-8"))
        tokens = payload["tokens"]
        access_token = tokens["access_token"]
        account_id = tokens["account_id"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise AuthError(
            f"Codex auth at {auth_path} is incomplete; run `codex login` again"
        ) from exc

    if not isinstance(access_token, str) or not access_token:
        raise AuthError("Codex access token is missing")
    if not isinstance(account_id, str) or not account_id:
        raise AuthError("Codex account id is missing")

    return CodexCredentials(
        access_token=access_token,
        account_id=account_id,
    )


def resolve_codex_binary() -> str:
    candidates = [
        os.environ.get("CODEX_CLI_PATH"),
        shutil.which("codex"),
        str(Path("~/.local/bin/codex").expanduser()),
        str(Path("~/.local/node_modules/.bin/codex").expanduser()),
        "/Applications/Codex.app/Contents/Resources/codex",
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise AuthError(
        "Codex CLI was not found; set CODEX_CLI_PATH or install Codex for this user"
    )


def refresh_credentials(
    auth_path: Path,
    *,
    timeout: float = 30.0,
) -> CodexCredentials:
    messages = (
        {
            "id": 1,
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "codex-stt-bridge",
                    "version": "0.2.0",
                },
                "capabilities": {
                    "experimentalApi": True,
                    "optOutNotificationMethods": [],
                },
            },
        },
        {
            "id": 2,
            "method": "account/read",
            "params": {"refreshToken": True},
        },
    )
    input_text = "".join(json.dumps(message) + "\n" for message in messages)

    try:
        # The executable is resolved from a fixed local allowlist above.
        result = subprocess.run(  # nosec B603
            [resolve_codex_binary(), "app-server", "--listen", "stdio://"],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AuthError("Codex auth refresh timed out") from exc
    except OSError as exc:
        raise AuthError(f"Codex auth refresh could not start: {exc}") from exc

    if result.returncode != 0:
        raise AuthError(f"Codex auth refresh failed with exit code {result.returncode}")

    for line in result.stdout.splitlines():
        try:
            message: Any = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("id") == 2 and "result" in message:
            return read_credentials(auth_path)

    raise AuthError("Codex did not confirm the auth refresh request")
