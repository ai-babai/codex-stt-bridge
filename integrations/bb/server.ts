import { execFile } from "node:child_process";
import { constants } from "node:fs";
import { access, mkdtemp, readFile, rm, stat, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { isAbsolute, join } from "node:path";
import type { BbPluginApi } from "@get-bb/plugin-sdk";

const MAX_AUDIO_BYTES = 50 * 1024 * 1024;
const MAX_TRANSCRIPT_BYTES = 1024 * 1024;
const AUDIO_SUFFIXES: Record<string, string> = {
  "audio/aac": ".aac",
  "audio/flac": ".flac",
  "audio/x-flac": ".flac",
  "audio/mp4": ".m4a",
  "audio/x-m4a": ".m4a",
  "audio/mpeg": ".mp3",
  "audio/ogg": ".ogg",
  "audio/opus": ".opus",
  "audio/wav": ".wav",
  "audio/wave": ".wav",
  "audio/x-wav": ".wav",
  "audio/webm": ".webm",
  "video/mp4": ".mp4",
  "video/webm": ".webm",
};

export default function plugin(bb: BbPluginApi) {
  const settings = bb.settings.define({
    executablePath: {
      type: "string",
      label: "codex-stt executable",
      description: "Absolute CLI path on the computer running the BB server.",
      default: "",
    },
  });

  async function executable(): Promise<string> {
    const { executablePath } = await settings.get();
    if (!isAbsolute(executablePath)) {
      throw new Error("Set the absolute codex-stt executable path in plugin settings.");
    }
    await access(executablePath, constants.X_OK);
    return executablePath;
  }

  bb.experimental_aiServices.register({
    id: "codex-stt-bridge",
    displayName: "Codex STT Bridge",
    async status() {
      try {
        await executable();
        return { ready: true };
      } catch {
        return {
          ready: false,
          message: "Install codex-stt on the BB server and set its absolute executable path.",
        };
      }
    },
    async transcribe(audio, { signal }) {
      const command = await executable();
      const suffix = AUDIO_SUFFIXES[audio.type.split(";", 1)[0].trim().toLowerCase()];
      if (!suffix) throw new Error("Codex STT Bridge does not support this audio MIME type.");
      if (audio.size === 0 || audio.size > MAX_AUDIO_BYTES) {
        throw new Error("Recording must contain audio and be at most 50 MiB.");
      }
      signal.throwIfAborted();
      // mkdtemp creates a private 0700 directory; never use the supplied filename.
      const directory = await mkdtemp(join(tmpdir(), "bb-codex-stt-"));
      try {
        const input = join(directory, `audio${suffix}`);
        const output = join(directory, "transcript.txt");
        await writeFile(input, Buffer.from(await audio.arrayBuffer()), { mode: 0o600 });
        await new Promise<void>((resolve, reject) => {
          execFile(command, ["--input", input, "--output", output], {
            signal,
            timeout: 240_000,
            maxBuffer: 64 * 1024,
            encoding: "utf8",
          }, (error) => {
            if (error) {
              // Child output can contain sensitive text. Never forward it to BB logs.
              reject(new Error(signal.aborted
                ? "Codex STT Bridge transcription was cancelled."
                : "Codex STT Bridge failed. Check the CLI directly for authentication or network errors."));
            } else resolve();
          });
        });
        if ((await stat(output)).size > MAX_TRANSCRIPT_BYTES) {
          throw new Error("Codex STT Bridge returned an oversized transcript.");
        }
        const text = (await readFile(output, "utf8")).trim();
        if (!text) throw new Error("Codex STT Bridge returned an empty transcript.");
        return text;
      } finally {
        // Both audio and transcript are temporary, including on failure/cancellation.
        await rm(directory, { recursive: true, force: true });
      }
    },
  });
}
