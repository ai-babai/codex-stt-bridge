# Диагностика

## `Codex auth is missing`

- команда запущена не от того Unix-пользователя;
- `CODEX_AUTH_PATH` указывает не туда;
- `codex login` не выполнялся.

Не копируйте чужой auth-файл. Выполните отдельный login для runtime user.

## `Codex CLI was not found`

Укажите:

```bash
export CODEX_CLI_PATH=/absolute/path/to/codex
```

CLI нужен для refresh после HTTP 401.

## HTTP 401

Bridge автоматически вызывает `account/read` и повторяет запрос один раз.
Если повтор не прошёл:

- проверьте `codex login status`;
- выполните новый login;
- не вставляйте callback URL или токены в issue/log.

## HTTP 403

Возможны изменение entitlement, account header или новая проверка клиента.
См. `API-COMPATIBILITY.md`. Не пытайтесь обходить ограничение browser cookies.

## HTTP 404

С высокой вероятностью изменился внутренний path. Сравните с текущим Codex
Desktop и upstream `anthnykr/codex-voice`.

## HTTP 413 или 415

- уменьшите тестовый файл;
- проверьте контейнер и MIME type;
- не добавляйте ffmpeg как скрытый fallback без отдельного решения.

## `incompatible response`

Backend больше не возвращает строковое поле `text`. Не печатайте полный body:
проверьте форму ответа только в приватной локальной диагностике и обновите
parser минимально.

## CLI работает, Hermes — нет

Проверить:

- абсолютный путь в `stt.providers.<name>.command`;
- placeholders `{input_path}` и `{output_path}`;
- права runtime user;
- доступ к `~/.codex/auth.json`;
- systemd network/mount restrictions;
- timeout Hermes;
- выбран ли именно `stt.provider: codex-desktop`.

## Hermes работает с текстом, но voice падает

Это ожидаемая изоляция отказа. Не перезапускайте и не переустанавливайте весь
Hermes до standalone-проверки bridge.
