# Установка и эксплуатация

[English](OPERATIONS.md) | **Русский**

## 1. Подготовить Codex login

Установите официальный Codex CLI и выполняйте все команды входа от того же
Unix-пользователя, который будет запускать bridge. Обычный desktop user,
выделенный пользователь `hermes` и service user `openclaw` имеют разные home
directories и не должны использовать скопированный друг у друга auth-файл.

Добавьте top-level настройку в `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

На локальном компьютере с браузером:

```bash
codex login
```

На удалённой машине без браузера:

```bash
codex login --device-auth
```

Device flow покажет URL и короткий код. Откройте URL на доверенном компьютере
или телефоне, введите код и вернитесь в терминал. Codex сам создаст
`~/.codex/auth.json` на целевой машине; не копируйте callback URL или
auth-файл другого пользователя.

Проверьте результат:

```bash
codex login status
chmod 600 ~/.codex/auth.json
test -s ~/.codex/auth.json
```

Если после перехода с keyring файл не появился, выполните свежий
`codex login`. Сначала используйте `codex logout` только если Codex сообщает,
что старая сессия всё ещё активна.

Обращайтесь с `auth.json` как с паролем. Не печатайте, не загружайте, не
добавляйте его в Git и не вставляйте в чат, issue или support ticket.

## 2. Установить bridge

```bash
git clone https://github.com/ai-babai/codex-stt-bridge.git
cd codex-stt-bridge
uv sync --frozen
```

Для production checkout:

```bash
uv sync --frozen --no-dev
```

## 3. Standalone smoke

Используйте собственное короткое неперсональное аудио:

```bash
out="$(mktemp)"
.venv/bin/codex-stt --input /path/to/smoke.ogg --output "$out"
wc -m "$out"
rm -f "$out"
```

Не выводите содержимое транскрипта в общий лог.

## 4. Hermes Agent

Скопируйте структуру из `examples/hermes-stt-provider.yaml` и замените
абсолютный путь к checkout.

Ключевые настройки:

- `echo_transcripts: true` — пользователь видит, что распознано;
- `timeout: 120` — ограничивает зависший backend;
- `format: txt` — Hermes читает простой UTF-8 output.

Имя `codex-desktop` намеренно не совпадает со встроенными provider names
Hermes: встроенные имена имеют приоритет над custom command providers.

После изменения конфигурации:

1. сохранить backup;
2. проверить standalone CLI;
3. проверить Hermes STT dispatcher;
4. перезапустить только gateway;
5. проверить новое голосовое сообщение;
6. убедиться, что обычный текстовый чат продолжает работать.

## 5. OpenClaw

Скопируйте структуру `tools.media` из `examples/openclaw-media.json5` и
замените абсолютный путь к команде. OpenClaw передаёт локальный путь вложения
как `{{MediaPath}}`, а bridge возвращает транскрипт через stdout.

Пример использует актуальный CLI-контракт `tools.media.models`. Не используйте
устаревшую настройку `audio.transcription.command` или старый placeholder
`{input}`. Перед restart gateway проверьте итоговый config той версией
OpenClaw, которая установлена на сервере.

## Production hardening

- executable path должен быть абсолютным;
- checkout и `.venv` желательно сделать root/admin-owned и read-only для
  runtime-пользователя агента;
- auth и agent config остаются во владении runtime user с mode `0600`;
- не передавайте OAuth через environment или command arguments;
- не включайте shell debug/`set -x`;
- не добавляйте автоматический retry кроме одного refresh после 401;
- не запускайте bridge как daemon и не открывайте сетевой порт.

## Обновление

```bash
git fetch origin
git switch main
git pull --ff-only
uv sync --frozen --no-dev
```

Перед обновлением сохраните текущий commit SHA. При несовместимости вернитесь
на него обычным Git checkout и повторите `uv sync --frozen --no-dev`.

## Наблюдаемость

Допустимые operational metrics:

- число успешных и неуспешных запросов;
- HTTP status;
- latency;
- размер аудио;
- длина транскрипта;
- версии Codex CLI и bridge.

Не логировать:

- audio bytes;
- transcript content;
- OAuth/account values;
- полный request/response;
- file IDs платформы сообщений, если они не нужны для локальной диагностики.

## Rollback

Минимальный rollback:

1. восстановить предыдущий agent config без этой STT-команды;
2. перезапустить только agent gateway;
3. сохранить checkout и нечувствительные failure metadata для диагностики;
4. убедиться, что обычные text/image turns продолжают работать.

Удаление sessions, application data, Codex auth или проекта для rollback не
требуется.
