# Contributing

**English** | [Русский](CONTRIBUTING.ru.md)

## Principles

- Never add secrets, real audio recordings, or transcripts, even to a private
  repository.
- Keep the CLI independent from Hermes.
- Do not add implicit API-key or local STT fallbacks.
- Change the internal HTTP contract only together with
  `docs/API-COMPATIBILITY.md` and `docs/API-COMPATIBILITY.ru.md`.
- Never log request or response bodies, credential headers, or transcript
  text.

## Development environment

```bash
uv sync --frozen
```

The project has no runtime dependencies. Quality tools run in isolated `uvx`
environments so they do not enter the production environment:

```bash
uvx ruff check src
uvx ruff format --check src
uvx mypy --strict src/hermes_codex_stt
uvx bandit -q -r src
uv build
```

## Behavior checks

Use only short, non-sensitive recordings that you own. Check logs may contain
HTTP status, exit code, latency, and transcript length, but never transcript
content.

Recommended order:

1. Check the CLI with a missing or unsupported input file.
2. Check the standalone CLI with approved test audio.
3. Check Hermes command-provider dispatch.
4. Check a new Telegram voice message.
5. Confirm that normal text turns still work when STT is unavailable.

## Before committing

```bash
git diff --check
git status --short
git diff
```

Check for common secret patterns:

```bash
git grep -n -I -E \
  '(sk-[A-Za-z0-9_-]{20,}|ac_[A-Za-z0-9_.-]{20,}|eyJ[A-Za-z0-9_-]{10,}\.)'
```

Matches for field names such as `access_token` are acceptable; values are not.

Keep each commit small and focused on one logical reason for change. Do not
combine an internal API change, a refactor, and deployment configuration in
one commit.

English files without a language suffix are canonical. Update each matching
`*.ru.md` translation in the same commit so operational and security
instructions do not drift between languages.

## Release checklist

1. Update the version and `CHANGELOG.md`.
2. Repeat static checks and the package build.
3. Scan the staged tree for secrets and sensitive filenames.
4. Run a live smoke check without writing the transcript to logs.
5. Record the compatible Codex CLI version.
6. Push the commit to the private GitHub repository.
7. Update production in a separate controlled step with a known rollback SHA.
