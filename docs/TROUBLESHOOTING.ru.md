# Диагностика

[English](TROUBLESHOOTING.md) | **Русский**

## `Codex auth is missing`

- команда запущена не от того Unix-пользователя;
- `CODEX_AUTH_PATH` указывает не туда;
- `codex login` не выполнялся.

Не копируйте чужой auth-файл. Выполните отдельный login для runtime user.
На headless-сервере запустите:

```bash
codex login --device-auth
```

Откройте показанный URL и введите короткий код в доверенном браузере. Codex
сам создаст файл на сервере; browser callback URL не является auth-файлом, его
нельзя вставлять в чат или issue.

Если Codex настроен на keyring, bridge не будет читать credentials. Для этого
экспериментального provider требуется:

```toml
cli_auth_credentials_store = "file"
```

После изменения выполните новый `codex login`.

## `Codex auth permissions are too broad`

На POSIX bridge требует:

```bash
chmod 600 ~/.codex/auth.json
```

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
См. `API-COMPATIBILITY.ru.md`. Не пытайтесь обходить ограничение browser
cookies.

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

## `response is unexpectedly large` или `response is empty`

Это считается несовместимостью backend, а не успешным пустым сообщением.
Проверьте `API-COMPATIBILITY.ru.md`; не увеличивайте лимит и не принимайте
пустой результат без анализа нового контракта.

## `Unsupported audio extension`

Bridge намеренно не является универсальным file uploader. При добавлении нового
контейнера сначала подтвердите, что это реальный audio format Hermes/Telegram и
что backend его принимает, затем обновите allowlist и документацию.

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

## CLI работает, OpenClaw — нет

Проверить:

- абсолютный `command` в `tools.media.models`;
- `args: ["--input", "{{MediaPath}}"]`;
- `capabilities: ["audio"]`;
- права runtime-пользователя OpenClaw;
- принадлежит ли `~/.codex/auth.json` тому же пользователю;
- timeout и size limits OpenClaw media.

Используйте актуальный контракт `tools.media.models`. Устаревшая настройка
`audio.transcription.command` и placeholder `{input}` несовместимы с примером
из этого репозитория.
