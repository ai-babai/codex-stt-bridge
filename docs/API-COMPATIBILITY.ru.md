# Совместимость внутреннего Codex Desktop API

[English](API-COMPATIBILITY.md) | **Русский**

## Статус

Используемый endpoint не является публичным OpenAI API. Контракт был
восстановлен по поведению Codex Desktop и реализации
[`anthnykr/codex-voice`](https://github.com/anthnykr/codex-voice).

Нельзя рассчитывать на версионирование, changelog или обратную совместимость.

## Проверенная матрица

Последний live smoke: `2026-07-24`.

| Компонент | Проверенная версия/форма |
| --- | --- |
| Bridge | `0.2.0` |
| Codex CLI | `0.145.0`, ChatGPT OAuth |
| Hermes Agent | `0.19.0`, upstream tag `v2026.7.20` |
| Server | Ubuntu 24.04, Python 3.12 |
| Input | Telegram OGG/Opus |
| Upstream reference | `anthnykr/codex-voice@ee4570c4ea71` |

Установка собранного пакета дополнительно проверена на Python 3.11. Эта
матрица не означает, что внутренний endpoint гарантированно совместим со всеми
следующими версиями.

## Текущий контракт

| Часть | Текущее значение |
| --- | --- |
| Method | `POST` |
| URL | `https://chatgpt.com/backend-api/transcribe` |
| Authorization | `Bearer <tokens.access_token>` |
| Account header | `ChatGPT-Account-Id: <tokens.account_id>` |
| Originator | `Codex Desktop` |
| Body | `multipart/form-data` |
| File field | `file` |
| Success response | JSON object with string field `text` |
| OAuth refresh | Codex app-server `account/read`, `refreshToken: true` |

Bridge поддерживает только `cli_auth_credentials_store = "file"`. Keyring
является хорошим общим выбором для Codex CLI, но текущий внутренний endpoint
нельзя вызвать без bearer token, а bridge не должен пытаться извлекать его из
OS keychain обходным способом.

Все изменяемые request constants находятся в
`src/codex_stt_bridge/constants.py`.

## Основные точки возможной поломки

### Endpoint

Возможны новый hostname, path, API version или переход на другой transport.
Bridge специально запрещает отправлять credential headers на hostname,
отличный от `chatgpt.com`, и не следует HTTP redirects. Если endpoint начнёт
перенаправлять запросы, интеграция должна явно остановиться до проверки нового
URL.

### Авторизация

Может измениться:

- структура `~/.codex/auth.json`;
- название `access_token` или `account_id`;
- обязательный scope;
- формат account header;
- необходимость cookie, device binding или proof token;
- способ обновления через Codex app-server.

Не следует обходить новый auth-контроль копированием browser cookies.

Если file-based auth исчезнет или перестанет поддерживаться, это breaking
change. Безопасный результат — явная ошибка и отключение STT provider.

### Multipart

Может измениться:

- имя поля `file`;
- список MIME types;
- лимит размера;
- обязательные дополнительные поля;
- необходимость предварительной конвертации.

### Ответ

Поле `text` может быть переименовано или заменено потоковым ответом,
сегментами либо вложенной структурой. Ответ ограничен 1 MiB; превышение и
пустой транскрипт считаются ошибкой.

### Client identity

Backend может начать строго проверять `originator`, версию Codex Desktop,
`User-Agent`, OS или другие заголовки.

## Значение HTTP-ошибок

Это диагностические гипотезы, а не гарантированный публичный контракт:

| Статус | Сначала проверить |
| ---: | --- |
| 400 | multipart, MIME type, новые обязательные поля |
| 401 | срок OAuth; прошёл ли `account/read` refresh |
| 403 | entitlement, account header, новая client attestation |
| 404 | endpoint/path изменился |
| 413 | серверный лимит размера |
| 415 | MIME type или поддерживаемый контейнер изменился |
| 429 | rate limit; не добавлять агрессивные retry |
| 5xx | временная проблема backend или несовместимость |

## Безопасная процедура обновления

1. Убедиться, что обычный Codex Desktop всё ещё распознаёт голос.
2. Проверить свежие изменения в `anthnykr/codex-voice` и Codex CLI.
3. Использовать короткое собственное неперсональное аудио.
4. В диагностике сохранять только:
   - UTC timestamp;
   - версию bridge и Codex CLI;
   - HTTP status;
   - exit code;
   - длину транскрипта.
5. Не сохранять request headers, auth JSON, audio bytes, response body или
   текст транскрипта.
6. Менять constants и parser минимально.
7. Проверить standalone CLI.
8. Проверить command dispatch настроенного агента.
9. Проверить новое входящее голосовое сообщение.
10. Обновить этот документ и `CHANGELOG.md`.

## Когда прекратить использование

Отключить provider и оставить агента в text-only режиме, если backend требует:

- browser cookies;
- обход device attestation;
- передачу токенов третьему домену;
- модификацию Codex auth-файла вручную;
- неясный или небезопасный credential flow.
