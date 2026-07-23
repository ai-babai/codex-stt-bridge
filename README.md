# Hermes Codex STT

**English** | [Русский](README.ru.md)

A small command-line bridge that transcribes audio through the same internal
backend used by Codex Desktop. It reuses an existing ChatGPT/Codex OAuth
session and integrates with Hermes Agent as a standard command-type STT
provider.

```text
Telegram voice message
  → Hermes STT dispatcher
  → codex-stt
  → Codex Desktop transcription backend
  → UTF-8 transcript
  → normal Hermes text turn
```

## Status and limitations

The working prototype has been verified on Linux with Telegram OGG/Opus input
and Codex authenticated through ChatGPT OAuth:

- no OpenAI Platform API key is required or used;
- Whisper, Faster Whisper, and other local STT models are not used;
- ffmpeg and audio pre-conversion are not required;
- no custom Hermes plugin, MCP server, daemon, or container is required.

The Codex Desktop transcription endpoint is internal and undocumented. OpenAI
may change it without notice. This is an experimental compatibility bridge,
not an official OpenAI SDK or API integration.

## Requirements

- Python 3.11 or newer;
- Codex CLI installed;
- `codex login` completed by the same Unix user that runs the bridge;
- file-based Codex credential storage
  (`cli_auth_credentials_store = "file"`);
- mode `0600` on `~/.codex/auth.json`;
- network access to `https://chatgpt.com`;
- Hermes Agent only when the command is used as an STT provider.

## Installation

```bash
git clone git@github.com:ai-babai/hermes-codex-stt.git
cd hermes-codex-stt
uv sync
```

For production:

```bash
uv sync --frozen --no-dev
```

## Usage

```bash
.venv/bin/codex-stt \
  --input /path/to/message.ogg \
  --output /path/to/transcript.txt
```

Without `--output`, the transcript is written to stdout:

```bash
.venv/bin/codex-stt --input /path/to/message.ogg
```

Optional arguments:

- `--auth-path` — a non-default path to Codex `auth.json`;
- `--timeout` — HTTPS request timeout in seconds;
- `--language` — accepted for Hermes compatibility; the backend currently
  detects the language automatically, so the value is not sent.

Environment variables:

- `CODEX_AUTH_PATH` — alternative path to the Codex auth file;
- `CODEX_CLI_PATH` — path to Codex CLI for refreshing an expired OAuth
  session.

## Hermes configuration

Start with
[`examples/hermes-stt-provider.yaml`](examples/hermes-stt-provider.yaml).

The command returns a non-zero exit code on failure. A successful transcript
is written atomically with mode `0600`.

Exit codes:

- `0` — transcript created successfully;
- `1` — authentication, network, API compatibility, or file operation error;
- `2` — invalid CLI arguments.

## Security

This repository must never contain keys, tokens, real audio recordings, or
transcripts. OAuth credentials are read directly from the local Codex auth
file and are never copied by the bridge.

Private repository visibility is not a substitute for secret handling.
Read the complete [security policy](docs/SECURITY.md).

For production, make the checkout and virtual environment
administrator-owned and read-only for the Hermes runtime user. This does not
hide OAuth credentials from that user, but it prevents the agent from
silently persisting changes to the credential-handling code.

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
