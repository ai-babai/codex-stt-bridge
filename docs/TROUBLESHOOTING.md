# Troubleshooting

**English** | [Русский](TROUBLESHOOTING.ru.md)

## `Codex auth is missing`

Possible causes:

- the command runs as the wrong Unix user;
- `CODEX_AUTH_PATH` points to the wrong location;
- `codex login` has not been completed.

Do not copy another user's auth file. Complete a separate login for the runtime
user. On a headless host, run:

```bash
codex login --device-auth
```

Open the displayed URL and enter the short code in a trusted browser. Codex
creates the file on the host automatically; a browser callback URL is not an
auth file and must not be pasted into chat or an issue.

If Codex is configured to use a keyring, the bridge cannot read its
credentials. This experimental provider requires:

```toml
cli_auth_credentials_store = "file"
```

Run `codex login` again after changing the setting.

## `Codex auth permissions are too broad`

On POSIX, the bridge requires:

```bash
chmod 600 ~/.codex/auth.json
```

## `Codex CLI was not found`

Set an explicit path:

```bash
export CODEX_CLI_PATH=/absolute/path/to/codex
```

Codex CLI is required to refresh the session after HTTP 401.

## HTTP 401

The bridge automatically invokes `account/read` and retries once. If the retry
fails:

- check `codex login status`;
- complete a new login;
- never paste a callback URL or token into an issue or log.

## HTTP 403

The entitlement, account header, or client verification may have changed. See
`API-COMPATIBILITY.md`. Do not work around the restriction with browser
cookies.

## HTTP 404

The internal path has probably changed. Compare it with current Codex Desktop
behavior and the upstream `anthnykr/codex-voice` implementation.

## HTTP 413 or 415

- Use a smaller test file.
- Check the container and MIME type.
- Do not add ffmpeg as a hidden fallback without a separate design decision.

## `incompatible response`

The backend no longer returns a string `text` field. Do not print the complete
body. Inspect only its shape in private local diagnostics and update the
parser narrowly.

## `response is unexpectedly large` or `response is empty`

The bridge treats either result as a backend incompatibility, not as a
successful empty message. Review `API-COMPATIBILITY.md`; do not increase the
limit or accept empty output without reviewing the new contract.

## `Unsupported audio extension`

The bridge is intentionally not a generic file uploader. Before allowing a new
container, confirm that it is a real Hermes or Telegram audio format and that
the backend accepts it. Then update both the allowlist and documentation.

## The CLI works but Hermes does not

Check:

- the absolute path in `stt.providers.<name>.command`;
- the `{input_path}` and `{output_path}` placeholders;
- runtime-user permissions;
- access to `~/.codex/auth.json`;
- systemd network or mount restrictions;
- the Hermes timeout;
- that `stt.provider` selects `codex-desktop`.

## Text works in Hermes but voice fails

This is the intended failure isolation. Do not restart or reinstall all of
Hermes before checking the bridge independently.

## The CLI works but OpenClaw does not

Check:

- the absolute `command` in `tools.media.models`;
- `args: ["--input", "{{MediaPath}}"]`;
- `capabilities: ["audio"]`;
- permissions of the OpenClaw runtime user;
- that this same user owns `~/.codex/auth.json`;
- the OpenClaw media timeout and size limits.

Use the current `tools.media.models` contract. The retired
`audio.transcription.command` setting and `{input}` placeholder are not
compatible with the example in this repository.
