# Changelog

## Unreleased

## 0.2.0 — 2026-07-24

- Renamed the project and Python package to `codex-stt-bridge` while keeping
  the stable `codex-stt` command.
- Repositioned the bridge as an agent-independent voice-to-text CLI with
  examples for Hermes Agent and OpenClaw.
- Clarified ChatGPT plan and subscription-based Codex login support without
  implying that the internal transcription endpoint is an official plan
  entitlement.
- Added safe desktop and headless instructions for creating `auth.json`
  through the official Codex CLI.
- Made English the primary documentation language and added complete Russian
  versions of the user, operations, security, architecture, compatibility,
  troubleshooting, and contribution guides.
- Updated repository guidance for public distribution.

## 0.1.0 — 2026-07-24

- Added a standalone `codex-stt` command.
- Added Codex OAuth loading and one-time refresh through Codex app-server.
- Added direct OGG/Opus upload to the Codex Desktop transcription backend.
- Added atomic mode-`0600` transcript output.
- Rejected HTTP redirects so OAuth headers cannot follow the request to
  another URL.
- Added strict auth-file permission checks, an audio-extension allowlist,
  bounded response reads and explicit rejection of empty transcripts.
- Modernized package metadata and documented the contribution workflow.
- Added Dependabot monitoring for the committed uv lock.
- Added a Hermes command-provider configuration example.
- Documented architecture, security, operations, troubleshooting and the
  unsupported internal API compatibility boundary.
