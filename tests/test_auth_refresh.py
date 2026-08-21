import io
import json
import os
import unittest
from typing import Any
from unittest.mock import patch

from codex_stt_bridge import auth


class _InspectableStdin(io.BytesIO):
    def close(self) -> None:
        pass


class _FakeProcess:
    def __init__(self, stdout: Any | None = None) -> None:
        self.stdin = _InspectableStdin()
        self.stdout = stdout or io.BytesIO(
            b'{"id":1,"result":{}}\n{"id":2,"result":{}}\n'
        )
        self.returncode: int | None = None
        self.terminated = False

    def wait(self, timeout: float | None = None) -> int:
        self.returncode = 0
        return 0

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = 0


class _ProtocolStdin(_InspectableStdin):
    def __init__(self, output_fd: int) -> None:
        super().__init__()
        self.output_fd = output_fd
        self.messages: list[dict[str, Any]] = []

    def flush(self) -> None:
        lines = self.getvalue().splitlines()
        while len(self.messages) < len(lines):
            message = json.loads(lines[len(self.messages)])
            self.messages.append(message)
            if message.get("method") == "initialize":
                os.write(self.output_fd, b'{"id":1,"result":{}}\n')
            elif message.get("method") == "account/read":
                os.write(
                    self.output_fd,
                    b'{"method":"account/updated","params":{}}\n{"id":2,"result":{}}\n',
                )


class AppServerRefreshProtocolTests(unittest.TestCase):
    def test_refresh_uses_required_handshake_order(self) -> None:
        process = _FakeProcess()

        with (
            patch.object(auth.subprocess, "Popen", return_value=process) as popen,
            patch.object(
                auth.select,
                "select",
                side_effect=lambda read, write, error, timeout: (read, [], []),
            ),
        ):
            confirmed = auth._refresh_via_app_server("/fake/codex", timeout=5)

        self.assertTrue(confirmed)
        messages = [json.loads(line) for line in process.stdin.getvalue().splitlines()]
        self.assertEqual(
            [message.get("method") for message in messages],
            ["initialize", "initialized", "account/read"],
        )
        popen.assert_called_once_with(
            ["/fake/codex", "app-server", "--listen", "stdio://"],
            stdin=auth.subprocess.PIPE,
            stdout=auth.subprocess.PIPE,
            stderr=auth.subprocess.DEVNULL,
            text=False,
            bufsize=0,
        )

    def test_refresh_skips_notification_before_account_result(self) -> None:
        read_fd, write_fd = os.pipe()
        stdout = os.fdopen(read_fd, "rb", buffering=0)
        process = _FakeProcess(stdout)
        protocol_stdin = _ProtocolStdin(write_fd)
        process.stdin = protocol_stdin

        try:
            with patch.object(auth.subprocess, "Popen", return_value=process):
                confirmed = auth._refresh_via_app_server("/fake/codex", timeout=5)
        finally:
            stdout.close()
            os.close(write_fd)

        self.assertTrue(confirmed)
        self.assertEqual(
            [message.get("method") for message in protocol_stdin.messages],
            ["initialize", "initialized", "account/read"],
        )
