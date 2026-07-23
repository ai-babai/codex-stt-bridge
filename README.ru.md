# Codex STT Bridge

[English](README.md) | **Русский**

Преобразование голоса в текст для AI-агентов через существующий локальный
Codex login. Команда `codex-stt` принимает аудиофайл, отправляет его в backend
транскрипции Codex Desktop и возвращает обычный UTF-8 текст.

Проект рассчитан на пользователей, которые входят в Codex через тариф
ChatGPT, в том числе по подписке. OpenAI Platform API key не требуется и не
используется.

```text
Голосовое сообщение или аудиофайл
  → Hermes, OpenClaw или другой агент
  → codex-stt
  → backend транскрипции Codex Desktop
  → текстовый транскрипт
  → обычный turn агента
```

CLI не зависит от конкретного агента. Его можно использовать:

- как command-type STT provider в Hermes Agent;
- как media CLI в OpenClaw;
- из shell-скриптов и других агентов, умеющих запускать локальные команды.

## Важное ограничение совместимости

Endpoint транскрипции является внутренним и официально не документирован. Это
экспериментальный compatibility bridge, а не официальный OpenAI SDK или API.
OpenAI может без предупреждения изменить endpoint, требования к авторизации,
доступность или условия для тарифов.

Проект не утверждает, что STT официально входит в конкретную подписку ChatGPT.
Он использует действующую локальную Codex/ChatGPT OAuth-сессию и безопасно
останавливается, если этот механизм перестаёт работать.

## Требования

- Python 3.11+;
- установленный Codex CLI;
- действующий вход Codex через ChatGPT от того же Unix-пользователя, который
  запускает bridge;
- файловое хранение Codex credentials;
- доступ к `https://chatgpt.com`.

Whisper, Faster Whisper, локальная STT-модель, ffmpeg-конвертация, daemon,
контейнер, MCP-сервер и отдельный сетевой порт не требуются.

## Как безопасно получить `auth.json`

Не скачивайте, не создавайте и не копируйте `auth.json` вручную. Его должен
создать и обновлять официальный Codex CLI.

Добавьте top-level настройку в `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

На компьютере с браузером:

```bash
codex login
codex login status
chmod 600 ~/.codex/auth.json
```

На удалённом сервере без браузера:

```bash
codex login --device-auth
codex login status
chmod 600 ~/.codex/auth.json
```

Когда Codex попросит, откройте URL в доверенном браузере и введите короткий
device code. После подтверждения `~/.codex/auth.json` автоматически появится
на сервере.

Выполняйте login от того же Unix-пользователя, который будет запускать
`codex-stt`. Не копируйте auth другого пользователя, не отправляйте callback
URL из браузера в чат и не добавляйте `auth.json` в Git: файл содержит
credentials и должен храниться как пароль.

## Установка

```bash
git clone https://github.com/ai-babai/codex-stt-bridge.git
cd codex-stt-bridge
uv sync --frozen
```

Для production checkout:

```bash
uv sync --frozen --no-dev
```

## Использование

Запись транскрипта в файл:

```bash
.venv/bin/codex-stt \
  --input /path/to/message.ogg \
  --output /path/to/transcript.txt
```

Или вывод в stdout:

```bash
.venv/bin/codex-stt --input /path/to/message.ogg
```

Дополнительные параметры:

- `--auth-path` — нестандартный путь к Codex `auth.json`;
- `--timeout` — таймаут HTTPS-запроса;
- `--language` — аргумент совместимости с агентами; backend сейчас сам
  определяет язык, поэтому значение не отправляется.

Переменные окружения:

- `CODEX_AUTH_PATH` — альтернативный путь к Codex auth-файлу;
- `CODEX_CLI_PATH` — путь к Codex CLI для обновления истёкшей OAuth-сессии.

При ошибке команда возвращает ненулевой exit code. Успешный output-файл
записывается атомарно с правами `0600`.

Exit codes:

- `0` — транскрипт создан;
- `1` — ошибка авторизации, сети, совместимости или файловой операции;
- `2` — некорректные CLI arguments.

## Интеграция с агентами

- [Пример command provider для Hermes](examples/hermes-stt-provider.yaml)
- [Пример media CLI для OpenClaw](examples/openclaw-media.json5)

В production используйте абсолютный путь к `codex-stt`. Агент и bridge должны
работать от Unix-пользователя, которому принадлежит Codex login.

## Безопасность

В репозитории не должно быть ключей, токенов, browser callback URL, реальных
аудиофайлов и транскриптов. OAuth читается непосредственно из локального
Codex auth-файла и не копируется bridge.

Production checkout и виртуальное окружение рекомендуется сделать
administrator-owned и read-only для runtime-пользователя агента. Это не
скрывает OAuth от самого пользователя, но не позволяет агенту незаметно
изменить код, работающий с credentials.

Полные правила: [docs/SECURITY.ru.md](docs/SECURITY.ru.md).

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
