# Голосовой ввод BB

[English](README.md) | **Русский**

Этот необязательный плагин добавляет **Codex STT Bridge** в голосовые сервисы
BB. Он вызывает существующий `codex-stt` CLI вместо встроенного HTTP-клиента
транскрибации Codex в BB. Python bridge, endpoint и работа с OAuth не меняются.

CLI должен быть установлен на компьютере, где работает **сервер BB**, под
тем же Unix-пользователем с его Codex login. Плагин не отправляет команду на
удалённую машину BB. Требуется BB версии 0.48 или новее.

## Установка

Сначала установите bridge и войдите через Codex по
[основному README](../../README.ru.md). Из этой папки:

```bash
npm ci --ignore-scripts
npx tsc --noEmit
bb plugin build .
bb plugin install /absolute/path/codex-stt-bridge/integrations/bb --yes
bb plugin config codex-stt-bridge set executablePath /absolute/path/codex-stt-bridge/.venv/bin/codex-stt
bb settings ai-services set voice codex-stt-bridge
```

Тот же выбор доступен в **Settings → AI services → Voice input**. Меняется
только голос; сервисы заголовков, commit messages и модели агентов сохраняют
свой выбор. Сервис показывает готовность, когда заданный исполняемый файл
доступен; при ошибке авторизации войдите через `codex login`. Путь CLI
читается при каждом запросе, поэтому его изменение не требует reload.

Проверка полного пути BB на несекретном аудио:

```bash
bb voice transcribe /path/to/test.webm --type audio/webm
```

Команда печатает транскрипт. Не сохраняйте его в диагностические логи.
Поддерживаются браузерный `audio/webm;codecs=opus`, WAV, OGG/Opus и другие явно
поддерживаемые CLI аудиоформаты. Подсказки контекста транскрибации не
передаются: в CLI нет такого параметра.

## Работа с данными

Плагин не читает и не копирует Codex credentials. Аудио передаётся через
приватную временную папку (0700), входной файл создаётся с правами 0600.
CLI записывает транскрипт с правами 0600. Оба файла удаляются после успеха,
ошибки или отмены. Stdout/stderr дочернего процесса перехватываются и
отбрасываются; возвращаемые BB ошибки не содержат их вывода или транскрипта.
Лимит входа — 50 MiB, транскрипта — 1 MiB, процесса — 240 секунд с учётом
возможного OAuth refresh и повторного запроса CLI.

Дополнительный HTTP-сервер, слушающий порт, Platform API key, локальная STT
модель и автоматический fallback не добавляются. Аудио по-прежнему уходит
на фиксированный ChatGPT endpoint через Python bridge.

## Обновление и откат

После получения изменений повторите `npm ci`, проверку типов и
`bb plugin build .`, затем `bb plugin reload codex-stt-bridge`. Версия Python
пакета независима; обновляйте её только при изменении кода CLI.

Возврат встроенного сервиса Codex в BB:

```bash
bb settings ai-services set voice codex
bb plugin disable codex-stt-bridge
```

Ограничения endpoint: [документ совместимости](../../docs/API-COMPATIBILITY.ru.md).
