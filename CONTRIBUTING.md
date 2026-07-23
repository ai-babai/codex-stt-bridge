# Разработка

## Принципы

- Не добавлять секреты, реальные аудиофайлы и транскрипты даже в private repo.
- Сохранять CLI независимым от Hermes.
- Не добавлять неявный API-key или локальный STT fallback.
- Менять внутренний HTTP-контракт только вместе с
  `docs/API-COMPATIBILITY.md`.
- Не логировать request/response body и credential headers.

## Подготовка окружения

```bash
uv sync --frozen
```

Проект не имеет runtime dependencies. Инструменты качества запускаются
изолированно через `uvx`, чтобы не попадать в production environment:

```bash
uvx ruff check src
uvx ruff format --check src
uvx mypy --strict src/hermes_codex_stt
uvx bandit -q -r src
uv build
```

## Проверка поведения

Разрешены только собственные короткие неперсональные записи. В логи проверки
можно выводить HTTP status, exit code, latency и длину результата, но не сам
транскрипт.

Порядок:

1. проверить CLI на отсутствующем/неподдерживаемом файле;
2. проверить standalone CLI на разрешённом тестовом аудио;
3. проверить Hermes command-provider dispatch;
4. проверить новое Telegram voice;
5. убедиться, что обычные text turns работают при недоступном STT.

## Перед commit

```bash
git diff --check
git status --short
git diff
```

Проверка характерных секретов:

```bash
git grep -n -I -E \
  '(sk-[A-Za-z0-9_-]{20,}|ac_[A-Za-z0-9_.-]{20,}|eyJ[A-Za-z0-9_-]{10,}\.)'
```

Совпадения с названиями полей вроде `access_token` допустимы; значения — нет.

Commit должен быть небольшим и описывать одну логическую причину изменения.
Не смешивайте смену внутреннего API, рефакторинг и deployment config.

## Release checklist

1. Обновить версию и `CHANGELOG.md`.
2. Повторить статические проверки и package build.
3. Проверить staged tree на секреты и чувствительные имена файлов.
4. Выполнить живой smoke без записи транскрипта в лог.
5. Зафиксировать совместимую версию Codex CLI.
6. Отправить commit в private GitHub.
7. Обновить production только отдельным контролируемым шагом с rollback SHA.
