# Internal Codex Desktop API compatibility

**English** | [Русский](API-COMPATIBILITY.ru.md)

## Status

The transcription endpoint used by this project is not a public OpenAI API.
Its contract was inferred from Codex Desktop behavior and
[`anthnykr/codex-voice`](https://github.com/anthnykr/codex-voice). The refresh
sequence follows the official
[`codex app-server` protocol](https://github.com/openai/codex/blob/ceb2ffb793b7b990b435e70b4d71ee86eba823c4/codex-rs/app-server/README.md#initialization).

Do not expect versioning, a changelog, or backward-compatibility guarantees.

## Verified matrix

Last live smoke check: `2026-08-21`.

| Component | Verified version or form |
| --- | --- |
| Bridge | `0.2.1` |
| Codex CLI | `0.145.0`, ChatGPT OAuth |
| Hermes Agent | `0.19.0`, upstream tag `v2026.7.20` |
| Server | Ubuntu 24.04, Python 3.12 |
| Input | Telegram OGG/Opus |
| Upstream reference | `anthnykr/codex-voice@ee4570c4ea71` |
| App-server protocol | `openai/codex@ceb2ffb793b7` |

Installation of the built package was also verified on Python 3.11. This
matrix does not guarantee that the internal endpoint will remain compatible
with later versions.

## Current contract

| Part | Current value |
| --- | --- |
| Method | `POST` |
| URL | `https://chatgpt.com/backend-api/transcribe` |
| Authorization | `Bearer <tokens.access_token>` |
| Account header | `ChatGPT-Account-Id: <tokens.account_id>` |
| Originator | `Codex Desktop` |
| Body | `multipart/form-data` |
| File field | `file` |
| Success response | JSON object with string field `text` |
| OAuth refresh | Codex app-server stdio handshake: `initialize` → `initialized` → `account/read` with `refreshToken: true` |

The bridge supports only `cli_auth_credentials_store = "file"`. A keyring is a
good general choice for Codex CLI, but this internal endpoint cannot be called
without a bearer token, and the bridge must not extract it from the OS
keychain through an unofficial workaround.

All variable request constants are centralized in
`src/codex_stt_bridge/constants.py`.

## Likely compatibility breaks

### Endpoint

The hostname, path, API version, or transport may change. The bridge refuses
to send credential headers to any hostname other than `chatgpt.com` and does
not follow HTTP redirects. If the endpoint starts redirecting, stop the
integration until the new URL has been reviewed explicitly.

### Authentication

Potential changes include:

- the structure of `~/.codex/auth.json`;
- the names of `access_token` or `account_id`;
- required OAuth scopes;
- the account header format;
- cookie, device-binding, or proof-token requirements;
- refresh behavior through the Codex app server.

Do not bypass new authentication controls by copying browser cookies.

Loss of file-based authentication support is a breaking change. The safe
behavior is an explicit error and disabled STT provider.

### Multipart request

Potential changes include:

- the `file` field name;
- accepted MIME types;
- upload size limits;
- new required fields;
- required audio conversion.

### Response

The `text` field may be renamed or replaced by a stream, segments, or a nested
structure. Responses are limited to 1 MiB; oversized and empty transcripts
are treated as errors.

### Client identity

The backend may begin enforcing `originator`, Codex Desktop version,
`User-Agent`, operating system, or other headers.

## Interpreting HTTP errors

These are diagnostic hypotheses, not a guaranteed public contract:

| Status | Check first |
| ---: | --- |
| 400 | multipart shape, MIME type, new required fields |
| 401 | OAuth expiry and whether `account/read` refresh succeeded |
| 403 | entitlement, account header, new client attestation |
| 404 | changed endpoint or path |
| 413 | server-side size limit |
| 415 | changed MIME type or supported container |
| 429 | rate limit; do not add aggressive retries |
| 5xx | temporary backend failure or incompatibility |

## Safe update procedure

1. Confirm that normal Codex Desktop voice transcription still works.
2. Review recent changes in `anthnykr/codex-voice` and Codex CLI.
3. Use a short, non-sensitive recording that you own.
4. Record only:
   - UTC timestamp;
   - bridge and Codex CLI versions;
   - HTTP status;
   - exit code;
   - transcript length.
5. Do not retain request headers, auth JSON, audio bytes, response bodies, or
   transcript text.
6. Change constants and parsing as narrowly as possible.
7. Check the standalone CLI.
8. Check the configured agent command dispatch.
9. Check a new incoming voice message.
10. Update this document and `CHANGELOG.md`.

## When to stop using the bridge

Disable the provider and keep the agent text-only if the backend requires:

- browser cookies;
- bypassing device attestation;
- sending tokens to a third-party domain;
- manual modification of the Codex auth file;
- an unclear or unsafe credential flow.
