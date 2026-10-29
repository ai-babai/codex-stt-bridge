# BB voice input

**English** | [Русский](README.ru.md)

This optional plugin adds **Codex STT Bridge** to BB's voice-input services.
It calls the existing `codex-stt` CLI instead of BB's built-in Codex HTTP
transcription client. The Python bridge, endpoint and OAuth handling remain
unchanged.

The CLI must be installed on the computer running the **BB server**, under
the same Unix account and Codex login. The plugin does not dispatch to a
remote BB machine. BB must be version 0.48 or newer.

## Install

First install the bridge and sign in with Codex as described in the
[main README](../../README.md). From this directory:

```bash
npm ci --ignore-scripts
npx tsc --noEmit
bb plugin build .
bb plugin install /absolute/path/codex-stt-bridge/integrations/bb --yes
bb plugin config codex-stt-bridge set executablePath /absolute/path/codex-stt-bridge/.venv/bin/codex-stt
bb settings ai-services set voice codex-stt-bridge
```

The same selection is available in **Settings → AI services → Voice input**.
Only voice changes; thread titles, commit messages and agent models retain
their existing selections. The service reports ready when the configured
executable is accessible; authenticate with `codex login` if transcription
reports an authentication error. The path is read on each request, so
changing it does not require a plugin reload.

Check the complete BB dispatch path with non-sensitive audio:

```bash
bb voice transcribe /path/to/test.webm --type audio/webm
```

This command prints the transcript. Do not capture it in diagnostic logs.
Browser `audio/webm;codecs=opus`, WAV, OGG/Opus and the CLI's other explicit
audio formats are supported. Transcription context hints are not forwarded;
the CLI does not expose that option.

## Data handling

The plugin does not read or copy Codex credentials. Audio passes through a
private temporary directory (0700) with an input file created as 0600.
The CLI writes the transcript as 0600. Both files are removed after success,
failure or cancellation. Child stdout/stderr is captured and discarded;
errors returned to BB contain neither child output nor transcript text.
Input is limited to 50 MiB, transcript output to 1 MiB, and the subprocess to
240 seconds, including the CLI's possible OAuth refresh and retry.

No additional HTTP server, listening port, Platform API key, local STT model
or automatic fallback is added. Audio still leaves the computer for the
fixed ChatGPT endpoint through the Python bridge.

## Update and rollback

After pulling changes, repeat `npm ci`, type checking and `bb plugin build .`,
then run `bb plugin reload codex-stt-bridge`. The Python package has an
independent version; update it only when its CLI code changes.

To restore BB's built-in Codex service:

```bash
bb settings ai-services set voice codex
bb plugin disable codex-stt-bridge
```

See the [internal-endpoint compatibility boundary](../../docs/API-COMPATIBILITY.md).
