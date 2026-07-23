# Установка и эксплуатация

## Рекомендуемая установка

```bash
git clone git@github.com:ai-babai/hermes-codex-stt.git
cd hermes-codex-stt
uv sync --frozen
```

Для production checkout:

```bash
uv sync --frozen --no-dev
```

Codex login должен принадлежать runtime-пользователю:

```bash
codex login status
```

Не копируйте auth другого Unix-пользователя.

Проверьте file-based storage в `~/.codex/config.toml`:

```toml
cli_auth_credentials_store = "file"
```

И права:

```bash
chmod 600 ~/.codex/auth.json
```

## Standalone smoke

Используйте собственное короткое неперсональное аудио:

```bash
out="$(mktemp)"
.venv/bin/codex-stt --input /path/to/smoke.ogg --output "$out"
wc -m "$out"
rm -f "$out"
```

Не выводите содержимое транскрипта в общий лог.

## Hermes config

Скопируйте структуру из `examples/hermes-stt-provider.yaml` и замените только
путь к checkout.

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
5. проверить новое Telegram voice;
6. убедиться, что обычный текстовый чат продолжает работать.

## Production hardening

- executable path должен быть абсолютным;
- checkout и `.venv` желательно сделать root/admin-owned и read-only для
  пользователя Hermes;
- auth и config остаются `hermes:hermes`, mode `0600`;
- не передавайте OAuth через environment или command arguments;
- не включайте shell debug/`set -x`;
- не добавляйте автоматический retry кроме одного refresh после 401;
- не запускайте bridge как отдельный daemon и не открывайте сетевой порт.

## Обновление

```bash
git fetch origin
git switch main
git pull --ff-only
uv sync --frozen --no-dev
```

Перед обновлением сохраните текущий commit SHA. При несовместимости вернитесь
на него обычным Git checkout и повторите `uv sync --frozen`.

## Наблюдаемость

Допустимые operational metrics:

- число успешных/неуспешных запросов;
- HTTP status;
- latency;
- размер аудио;
- длина транскрипта;
- версия Codex CLI и bridge.

Не логировать:

- audio bytes;
- transcript content;
- OAuth/account values;
- полный request/response;
- Telegram file IDs, если они не нужны для локальной диагностики.

## Rollback

Минимальный rollback:

1. восстановить предыдущий Hermes config без `stt.provider`;
2. перезапустить gateway;
3. сохранить checkout и входные данные для локальной диагностики;
4. убедиться, что text/image turns продолжают работать.

Удаление sessions, foodlog, Codex auth или проекта для rollback не требуется.
