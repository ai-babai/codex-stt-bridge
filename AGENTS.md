# AGENTS.md

This repository contains a small security-sensitive compatibility bridge.

## Purpose

Convert an audio file to text through the internal Codex Desktop
transcription flow, using the existing local Codex OAuth session, and expose
that operation as a command provider for Hermes Agent.

## Non-negotiable safety rules

- Never commit, copy, print or include `~/.codex/auth.json`.
- Never log bearer tokens, refresh tokens, account IDs, request headers,
  audio bytes or transcript text.
- Never add real recordings or transcripts to fixtures, examples or issues.
- Never use an OpenAI Platform API key as an implicit fallback.
- Never silently fall back to a local STT model.
- Keep authentication files read-only from the bridge's perspective.
- Send Codex credentials only to the fixed `https://chatgpt.com` endpoint.

## Compatibility boundary

The endpoint is internal and unsupported. Before changing the request
contract, read `docs/API-COMPATIBILITY.md`.

Keep endpoint, header and response-field constants centralized in
`src/hermes_codex_stt/constants.py`.

When diagnosing a break:

1. record only HTTP status, exit code and transcript length;
2. compare the contract with the current Codex Desktop behavior and upstream
   `anthnykr/codex-voice`;
3. do not paste auth files, headers or network captures containing tokens into
   commits, chats or issues;
4. keep failure isolated to STT and preserve normal Hermes text handling.

## Changes

- Prefer Python standard library over new runtime dependencies.
- Keep the CLI usable independently from Hermes.
- Network-dependent checks must be explicit and must use user-owned,
  non-sensitive audio.
- Update `CHANGELOG.md` and the compatibility document when the internal
  contract changes.
