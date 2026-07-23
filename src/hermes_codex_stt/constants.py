"""Internal Codex Desktop compatibility constants.

If the upstream request contract changes, update this file together with
docs/API-COMPATIBILITY.md and CHANGELOG.md.
"""

TRANSCRIPTION_ENDPOINT = "https://chatgpt.com/backend-api/transcribe"
TRANSCRIPTION_HOST = "chatgpt.com"
ORIGINATOR = "Codex Desktop"
MULTIPART_FILE_FIELD = "file"
RESPONSE_TEXT_FIELD = "text"

DEFAULT_TIMEOUT_SECONDS = 90.0
DEFAULT_MAX_AUDIO_BYTES = 50 * 1024 * 1024
MAX_RESPONSE_BYTES = 1024 * 1024

SUPPORTED_AUDIO_SUFFIXES = frozenset(
    {
        ".aac",
        ".flac",
        ".m4a",
        ".mp3",
        ".mp4",
        ".oga",
        ".ogg",
        ".opus",
        ".wav",
        ".webm",
    }
)
