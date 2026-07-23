# Architecture

**English** | [Русский](ARCHITECTURE.ru.md)

## Purpose

`hermes-codex-stt` converts one local audio file into text. It is an isolated
adapter between the standard Hermes Agent command-provider interface and the
internal Codex Desktop transcription flow.

```mermaid
flowchart LR
    TG["Telegram voice/audio"] --> HG["Hermes Gateway"]
    HG --> DP["Hermes STT dispatcher"]
    DP --> CLI["codex-stt CLI"]
    CLI --> AF["~/.codex/auth.json<br/>read only"]
    CLI --> BE["chatgpt.com<br/>Codex Desktop transcription"]
    BE --> CLI
    CLI --> TF["UTF-8 transcript<br/>mode 0600"]
    TF --> HG
    HG --> AG["Normal Hermes text turn"]
```

## Responsibilities

### Hermes

Hermes is responsible for:

- receiving the Telegram file;
- invoking the command with `{input_path}` and `{output_path}`;
- reading the result;
- showing the recognized text;
- continuing with a normal agent turn.

Hermes core is not patched.

### Bridge

The bridge is responsible for:

- validating the input file and size;
- reading the current Codex OAuth session;
- uploading the original audio directly;
- refreshing once and retrying once after HTTP 401;
- validating the response shape;
- writing the result atomically with mode `0600`;
- failing safely without exposing credential material.

The bridge does not retain its own copy of audio, tokens, or the account ID.

### Codex

Codex CLI is responsible only for initial login and refreshing an expired
OAuth session. Its real-time app server is not used for transcription.

The current implementation requires file-based credential storage. The bridge
cannot read the Codex keyring directly, while the internal transcription
endpoint requires a bearer token. If Codex stops supporting a safe file-based
flow, the bridge must stop rather than extract credentials through an
unofficial workaround.

## Why a command provider

A command provider is the smallest stable integration boundary:

- no separate process or port;
- no dependency on the Hermes plugin API;
- no MCP server;
- an STT failure does not stop normal text chat;
- the CLI can be checked independently from the gateway;
- updating the bridge does not require changing Hermes core.

The Hermes documentation recommends a Python plugin when OAuth refresh,
streaming, or provider-specific setup must be part of the provider API. Here,
refresh is encapsulated inside a deterministic one-command CLI, so the command
provider remains the smaller and better-isolated boundary. Reconsider a plugin
if streaming chunks, provider metadata, or interactive setup become necessary.

## Failure flow

```mermaid
flowchart TD
    A["Audio received"] --> B["codex-stt"]
    B --> C{"HTTP status"}
    C -- "2xx" --> D["Validate JSON text"]
    C -- "401" --> E["Codex account/read refresh"]
    E --> F["Retry once"]
    C -- "other error" --> G["Safe non-zero failure"]
    F --> D
    F --> G
    D --> H["Atomic transcript file"]
    G --> I["Hermes reports STT failure<br/>text chat remains available"]
```

## Data flow

| Data | Read | Transmitted | Stored by bridge |
| --- | ---: | ---: | ---: |
| Input audio | yes | `chatgpt.com` | no |
| OAuth access token | yes | `chatgpt.com` | no |
| Codex account ID | yes | `chatgpt.com` | no |
| Refresh token | not directly | through Codex CLI | no |
| Transcript | yes | Hermes | only at the requested output path |

## Production ownership

Recommended boundary:

```text
/opt/hermes-codex-stt/       root/admin owned, runtime read+execute
~/.codex/auth.json           hermes owned, mode 0600
Hermes config                hermes owned, mode 0600
audio cache                  hermes owned
transcript temp output       hermes owned, mode 0600
```

A user-writable checkout is acceptable for development, but it is not the
preferred production executable path for code that handles credentials.
