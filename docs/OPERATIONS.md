# Installation and operations

**English** | [Русский](OPERATIONS.ru.md)

## 1. Prepare the Codex login

Install the official Codex CLI and run all login commands as the same Unix
user that will run the bridge. A personal desktop user, a dedicated `hermes`
user, and an `openclaw` service user each have separate home directories and
must not share copied auth files.

Add this top-level setting to `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

For a local computer with a browser:

```bash
codex login
```

For a remote or headless machine:

```bash
codex login --device-auth
```

The device flow prints a URL and a short code. Open the URL on a trusted
computer or phone, enter the code, and return to the terminal. Codex creates
`~/.codex/auth.json` on the target machine; do not copy a callback URL or an
auth file from another user.

Verify the result:

```bash
codex login status
chmod 600 ~/.codex/auth.json
test -s ~/.codex/auth.json
```

If the file is still missing after changing from keyring storage, complete a
fresh `codex login`. Use `codex logout` first only when Codex reports that the
old session is already active.

Treat `auth.json` like a password. Never print, upload, commit, or paste it
into chat, an issue, or a support ticket.

## 2. Install the bridge

```bash
git clone https://github.com/ai-babai/codex-stt-bridge.git
cd codex-stt-bridge
uv sync --frozen
```

For a production checkout:

```bash
uv sync --frozen --no-dev
```

## 3. Standalone smoke check

Use a short, non-sensitive recording that you own:

```bash
out="$(mktemp)"
.venv/bin/codex-stt --input /path/to/smoke.ogg --output "$out"
wc -m "$out"
rm -f "$out"
```

Do not print transcript content to a shared log.

## 4. Hermes Agent

Copy the structure from `examples/hermes-stt-provider.yaml` and change the
absolute checkout path.

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
5. Check a new voice message.
6. Confirm that normal text chat still works.

## 5. OpenClaw

Copy the `tools.media` structure from `examples/openclaw-media.json5` and
change the absolute command path. OpenClaw passes the local attachment path as
`{{MediaPath}}`; the bridge writes the transcript to stdout.

The example uses the current `tools.media.models` CLI contract. Do not use the
retired `audio.transcription.command` setting or the old `{input}`
placeholder. Validate the final configuration with the OpenClaw version
installed on the target host before restarting its gateway.

## Production hardening

- Use an absolute executable path.
- Prefer a root/admin-owned checkout and `.venv` that are read-only for the
  agent runtime user.
- Keep auth and agent configuration owned by the runtime user with mode
  `0600`.
- Do not pass OAuth credentials through environment variables or command
  arguments.
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
- messaging-platform file IDs unless required for local diagnosis.

## Rollback

Minimum rollback:

1. Restore the previous agent configuration without this STT command.
2. Restart only the agent gateway.
3. Preserve the checkout and non-sensitive failure metadata for diagnosis.
4. Confirm that normal text and image turns still work.

Rollback does not require deleting sessions, application data, Codex auth, or
the project checkout.
