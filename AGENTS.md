# AGENTS.md

This repository contains a small security-sensitive compatibility bridge.

## Purpose

Convert an audio file to text through the internal Codex Desktop
transcription flow, using the existing local Codex OAuth session, and expose
that operation as a small CLI for Hermes Agent, OpenClaw, and other local
agent runtimes.

## Non-negotiable safety rules

- Never commit, copy, print or include `~/.codex/auth.json`.
- Never log bearer tokens, refresh tokens, account IDs, request headers,
  audio bytes or transcript text.
- Never add real recordings or transcripts to fixtures, examples or issues.
- Never use an OpenAI Platform API key as an implicit fallback.
- Never silently fall back to a local STT model.
- Keep authentication files read-only from the bridge's perspective.
- Require mode `0600` for file-based Codex credentials on POSIX.
- Send Codex credentials only to the fixed `https://chatgpt.com` endpoint.

## Compatibility boundary

The endpoint is internal and unsupported. Before changing the request
contract, read `docs/API-COMPATIBILITY.md`.

Keep endpoint, header and response-field constants centralized in
`src/codex_stt_bridge/constants.py`.

When diagnosing a break:

1. record only HTTP status, exit code and transcript length;
2. compare the contract with the current Codex Desktop behavior and upstream
   `anthnykr/codex-voice`;
3. do not paste auth files, headers or network captures containing tokens into
   commits, chats or issues;
4. keep failure isolated to STT and preserve normal agent text handling.

## Changes

- Prefer Python standard library over new runtime dependencies.
- Keep network responses bounded and reject empty transcripts.
- Keep supported input formats explicit; do not turn the CLI into a generic
  file uploader.
- Keep the CLI usable independently from any agent runtime.
- Network-dependent checks must be explicit and must use user-owned,
  non-sensitive audio.
- English documentation files without a language suffix are canonical. Keep
  every matching `*.ru.md` translation synchronized in the same change.
- Update `CHANGELOG.md` and both compatibility documents when the internal
  contract changes.
