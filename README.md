# Codex STT Bridge

**English** | [Русский](README.ru.md)

Speech-to-text for AI agents through an existing local Codex login.
`codex-stt` accepts an audio file, sends it to the transcription backend used
by Codex Desktop, and returns plain UTF-8 text.

It is designed for people who sign in to Codex with a ChatGPT plan, including
subscription-based access. No OpenAI Platform API key is required or used.

```text
Voice message or audio file
  → Hermes, OpenClaw, or another agent
  → codex-stt
  → Codex Desktop transcription backend
  → plain-text transcript
  → normal agent turn
```

The CLI is agent-independent. It can be used:

- as a Hermes Agent command-type STT provider;
- as an OpenClaw media CLI;
- from shell scripts and other agents that can call a local command.

## Important compatibility notice

The transcription endpoint is internal and undocumented. This project is an
experimental compatibility bridge, not an official OpenAI SDK or API
integration. OpenAI may change the endpoint, authentication requirements,
availability, or plan eligibility without notice.

This project does not claim that speech-to-text is an official benefit of a
particular ChatGPT subscription. It reuses a valid local Codex/ChatGPT OAuth
session and fails closed if that flow stops working.

## Requirements

- Python 3.11 or newer;
- Codex CLI installed;
- a valid Codex login through ChatGPT for the same Unix user that runs the
  bridge;
- file-based Codex credential storage;
- network access to `https://chatgpt.com`.

No Whisper, Faster Whisper, local STT model, ffmpeg conversion, daemon,
container, MCP server, or dedicated network port is required.

## Create `auth.json` safely

Do not download, hand-write, or copy `auth.json`. Let the official Codex CLI
create and refresh it.

Add this top-level setting to `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

On a computer with a browser:

```bash
codex login
codex login status
chmod 600 ~/.codex/auth.json
```

On a remote or headless server:

```bash
codex login --device-auth
codex login status
chmod 600 ~/.codex/auth.json
```

Open the URL and enter the short device code on a trusted browser when Codex
asks. The resulting `~/.codex/auth.json` is created on the server
automatically.

Run login as the same Unix user that will run `codex-stt`. Never copy another
user's auth file, paste a browser callback URL into chat, or commit
`auth.json`; the file contains access credentials and must be treated like a
password.

## Installation

```bash
git clone https://github.com/ai-babai/codex-stt-bridge.git
cd codex-stt-bridge
uv sync --frozen
```

For a production checkout:

```bash
uv sync --frozen --no-dev
```

## Usage

Write the transcript to a file:

```bash
.venv/bin/codex-stt \
  --input /path/to/message.ogg \
  --output /path/to/transcript.txt
```

Or write it to stdout:

```bash
.venv/bin/codex-stt --input /path/to/message.ogg
```

Optional arguments:

- `--auth-path` — a non-default path to Codex `auth.json`;
- `--timeout` — HTTPS request timeout in seconds;
- `--language` — accepted for agent compatibility; the backend currently
  detects the language automatically, so the value is not sent.

Environment variables:

- `CODEX_AUTH_PATH` — alternative path to the Codex auth file;
- `CODEX_CLI_PATH` — path to Codex CLI for refreshing an expired OAuth
  session.

The command returns a non-zero exit code on failure. A successful output file
is written atomically with mode `0600`.

Exit codes:

- `0` — transcript created successfully;
- `1` — authentication, network, compatibility, or file operation error;
- `2` — invalid CLI arguments.

## Agent integration

- [Hermes command-provider example](examples/hermes-stt-provider.yaml)
- [OpenClaw media CLI example](examples/openclaw-media.json5)

Keep the absolute path to `codex-stt` in production. The agent runtime and the
bridge must run under the Unix account that owns the Codex login.

## Security

This repository must never contain keys, tokens, browser callback URLs, real
audio recordings, or transcripts. OAuth credentials are read directly from
the local Codex auth file and are never copied by the bridge.

For production, make the checkout and virtual environment administrator-owned
and read-only for the agent runtime user. This does not hide OAuth credentials
from that user, but it prevents the agent from silently changing the code that
handles them.

Read the complete [security policy](docs/SECURITY.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Internal API compatibility](docs/API-COMPATIBILITY.md)
- [Security](docs/SECURITY.md)
- [Installation and operations](docs/OPERATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Development](CONTRIBUTING.md)

## Attribution

The Codex Desktop transcription flow was identified with the help of
[`anthnykr/codex-voice`](https://github.com/anthnykr/codex-voice).
See [NOTICE.md](NOTICE.md) for details.
