# Installation and operations

**English** | [Русский](OPERATIONS.ru.md)

## Recommended installation

```bash
git clone git@github.com:ai-babai/hermes-codex-stt.git
cd hermes-codex-stt
uv sync --frozen
```

For a production checkout:

```bash
uv sync --frozen --no-dev
```

The Codex login must belong to the runtime user:

```bash
codex login status
```

Do not copy another Unix user's auth file.

Confirm file-based storage in `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

Set restrictive permissions:

```bash
chmod 600 ~/.codex/auth.json
```

## Standalone smoke check

Use a short, non-sensitive recording that you own:

```bash
out="$(mktemp)"
.venv/bin/codex-stt --input /path/to/smoke.ogg --output "$out"
wc -m "$out"
rm -f "$out"
```

Do not print transcript content to a shared log.

## Hermes configuration

Copy the structure from `examples/hermes-stt-provider.yaml` and change only
the checkout path.

Important settings:

- `echo_transcripts: true` lets the user verify the recognized text;
- `timeout: 120` bounds a stalled backend call;
- `format: txt` tells Hermes to read plain UTF-8 output.

The name `codex-desktop` intentionally differs from built-in Hermes provider
names because built-in names take precedence over custom command providers.

After changing the configuration:

1. Save a backup.
2. Check the standalone CLI.
3. Check Hermes STT dispatcher behavior.
4. Restart only the gateway.
5. Check a new Telegram voice message.
6. Confirm that normal text chat still works.

## Production hardening

- Use an absolute executable path.
- Prefer a root/admin-owned checkout and `.venv` that are read-only for the
  Hermes runtime user.
- Keep auth and configuration owned by `hermes:hermes` with mode `0600`.
- Do not pass OAuth credentials through the environment or command arguments.
- Do not enable shell debugging or `set -x`.
- Do not add automatic retries beyond one refresh after HTTP 401.
- Do not run the bridge as a daemon or expose a network port.

## Updating

```bash
git fetch origin
git switch main
git pull --ff-only
uv sync --frozen --no-dev
```

Record the current commit SHA before updating. If compatibility breaks, check
out that SHA and run `uv sync --frozen --no-dev` again.

## Observability

Allowed operational metrics:

- successful and failed request counts;
- HTTP status;
- latency;
- audio size;
- transcript length;
- Codex CLI and bridge versions.

Never log:

- audio bytes;
- transcript content;
- OAuth or account values;
- full requests or responses;
- Telegram file IDs unless required for local diagnosis.

## Rollback

Minimum rollback:

1. Restore the previous Hermes configuration without the STT provider.
2. Restart the gateway.
3. Preserve the checkout and input metadata for local diagnosis.
4. Confirm that text and image turns still work.

Rollback does not require deleting sessions, foodlog data, Codex auth, or the
project checkout.
