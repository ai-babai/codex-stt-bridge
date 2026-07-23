# Hermes Codex STT

[English](README.md) | **Русский**

Небольшая команда для расшифровки аудио через тот же внутренний backend,
который использует Codex Desktop. Команда использует уже существующую
ChatGPT/Codex OAuth-сессию и подключается к Hermes Agent как штатный
command-type STT provider.

```text
Telegram voice
  → Hermes STT dispatcher
  → codex-stt
  → Codex Desktop transcription backend
  → UTF-8 transcript
  → обычный текстовый turn Hermes
```

## Статус и ограничения

Рабочий прототип проверен на Linux с Telegram OGG/Opus и авторизацией Codex
через ChatGPT OAuth:

- OpenAI Platform API key не требуется и не используется;
- Whisper, Faster Whisper и другие локальные STT-модели не используются;
- ffmpeg и предварительная конвертация не требуются;
- отдельный Hermes plugin, MCP-сервер, daemon или контейнер не нужны.

Транскрипционный endpoint Codex Desktop является внутренним и официально не
документирован. OpenAI может изменить его без предупреждения. Это
экспериментальная интеграция, а не официальный OpenAI SDK.

## Требования

- Python 3.11+;
- установленный Codex CLI;
- выполненный `codex login` от того же Unix-пользователя;
- file-based Codex credential storage (`cli_auth_credentials_store = "file"`);
- права `0600` на `~/.codex/auth.json`;
- доступ к `https://chatgpt.com`;
- Hermes Agent — только если команда используется как его STT provider.

## Установка

```bash
git clone git@github.com:ai-babai/hermes-codex-stt.git
cd hermes-codex-stt
uv sync
```

Для production:

```bash
uv sync --frozen --no-dev
```

## Использование

```bash
.venv/bin/codex-stt \
  --input /path/to/message.ogg \
  --output /path/to/transcript.txt
```

Без `--output` транскрипт выводится в stdout:

```bash
.venv/bin/codex-stt --input /path/to/message.ogg
```

Дополнительные параметры:

- `--auth-path` — нестандартный путь к Codex `auth.json`;
- `--timeout` — таймаут HTTPS-запроса;
- `--language` — совместимый с Hermes аргумент; backend сейчас сам определяет
  язык, поэтому значение не отправляется.

Переменные окружения:

- `CODEX_AUTH_PATH` — альтернативный путь к Codex auth;
- `CODEX_CLI_PATH` — путь к Codex CLI для обновления истёкшей OAuth-сессии.

## Hermes

Пример находится в
[`examples/hermes-stt-provider.yaml`](examples/hermes-stt-provider.yaml).

Команда возвращает ненулевой exit code при ошибке. Успешный транскрипт
записывается атомарно с правами `0600`.

Exit codes:

- `0` — транскрипт создан;
- `1` — ошибка auth, сети, совместимости API или файловой операции;
- `2` — некорректные CLI arguments.

## Безопасность

Проект не содержит и не должен содержать ключи, токены, реальные аудиофайлы
или транскрипты. OAuth читается непосредственно из локального Codex auth-файла
и не копируется.

Это публичный репозиторий. Никогда не добавляйте credentials или приватные
данные пользователей. Полные правила:
[`docs/SECURITY.ru.md`](docs/SECURITY.ru.md).

Production checkout и виртуальное окружение рекомендуется делать
администраторскими/read-only для runtime-пользователя Hermes. Это не скрывает
OAuth от самого пользователя, но не позволяет агенту незаметно закрепить
изменение в credential-handling коде.

## Документация

- [Архитектура](docs/ARCHITECTURE.ru.md)
- [Контракт внутреннего API](docs/API-COMPATIBILITY.ru.md)
- [Безопасность](docs/SECURITY.ru.md)
- [Установка и эксплуатация](docs/OPERATIONS.ru.md)
- [Диагностика](docs/TROUBLESHOOTING.ru.md)
- [Разработка](CONTRIBUTING.ru.md)

## Происхождение

Поток Codex Desktop transcription был найден благодаря
[`anthnykr/codex-voice`](https://github.com/anthnykr/codex-voice).
Подробности: [NOTICE.md](NOTICE.md).
