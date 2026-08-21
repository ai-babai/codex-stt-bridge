"""Read and refresh the existing local Codex OAuth session."""

from __future__ import annotations

import json
import os
import select
import shutil
import stat
import subprocess  # nosec B404
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codex_stt_bridge import __version__


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


def _refresh_via_app_server(binary: str, *, timeout: float) -> bool:
    """Refresh file-backed Codex credentials through the app-server protocol."""
    initialize = {
        "id": 1,
        "method": "initialize",
        "params": {
            "clientInfo": {"name": "codex-stt-bridge", "version": __version__},
            "capabilities": {
                "experimentalApi": True,
                "optOutNotificationMethods": [],
            },
        },
    }
    initialized = {"method": "initialized", "params": {}}
    account_read = {
        "id": 2,
        "method": "account/read",
        "params": {"refreshToken": True},
    }

    try:
        # The executable is resolved from a fixed local allowlist above.
        process = subprocess.Popen(  # nosec B603
            [binary, "app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=False,
            bufsize=0,
        )
    except OSError as exc:
        raise AuthError(f"Codex auth refresh could not start: {exc}") from exc

    stdin = process.stdin
    stdout = process.stdout
    if stdin is None or stdout is None:
        process.terminate()
        process.wait(timeout=3)
        raise AuthError("Codex auth refresh could not open stdio")

    deadline = time.monotonic() + timeout

    def send(message: dict[str, Any]) -> None:
        stdin.write((json.dumps(message) + "\n").encode())
        stdin.flush()

    def wait_for_result(request_id: int) -> bool:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            readable, _, _ = select.select([stdout], [], [], remaining)
            if not readable:
                return False
            line = stdout.readline()
            if not line:
                return False
            try:
                response: Any = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(response, dict) and response.get("id") == request_id:
                return "result" in response and "error" not in response

    try:
        send(initialize)
        if not wait_for_result(1):
            return False
        send(initialized)
        send(account_read)
        return wait_for_result(2)
    finally:
        stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=3)


def refresh_credentials(
    auth_path: Path,
    *,
    timeout: float = 30.0,
) -> CodexCredentials:
    try:
        confirmed = _refresh_via_app_server(resolve_codex_binary(), timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise AuthError("Codex auth refresh timed out") from exc

    if confirmed:
        return read_credentials(auth_path)
    raise AuthError("Codex did not confirm the auth refresh request")
