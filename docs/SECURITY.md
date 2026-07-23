# Безопасность

## Модель угроз

Главный риск проекта — утечка Codex OAuth credential material через Git,
логи, диагностику, exception body или случайные fixtures.

Private GitHub repository уменьшает публичную видимость, но не делает
размещение секретов допустимым.

## Что считается секретом

- весь `~/.codex/auth.json`;
- access, refresh и ID tokens;
- account ID;
- browser cookies и callback URLs device auth;
- Telegram bot token;
- реальные `.env`;
- приватные аудиозаписи и транскрипты.

## Защита в реализации

- endpoint жёстко ограничен HTTPS-hostname `chatgpt.com`;
- HTTP redirects запрещены, поэтому credential headers не следуют на другой
  URL или hostname;
- токены не принимаются через CLI arguments;
- токены не выводятся в stdout/stderr;
- response body ошибок не выводится;
- response body читается с лимитом 1 MiB;
- subprocess stderr Codex не включается в пользовательскую ошибку;
- bridge не пишет auth-файл;
- на POSIX auth-файл с правами шире `0600` отклоняется;
- принимаются только явно перечисленные audio extensions;
- output создаётся атомарно с mode `0600`;
- реальные аудиоформаты и `auth.json` игнорируются Git.

## Перед каждым push

Проверить:

```bash
git status --short
git diff --cached
git grep -n -I -E \
  '(access_token|refresh_token|id_token|Authorization: Bearer|deviceauth/callback)'
```

Совпадения в документации и названиях полей допустимы только без значений.

Дополнительно проверить staged blobs secret scanner'ом, если он доступен.

Для private repository личного GitHub-аккаунта нельзя считать server-side
secret scanning гарантированно доступным. Локальная pre-push проверка остаётся
обязательной даже при включённых Dependabot и GitHub security features.

## Если секрет попал в Git

1. Не считать удаление файла новым commit достаточным.
2. Немедленно прекратить дальнейшие push.
3. Отозвать или обновить скомпрометированную OAuth-сессию.
4. Очистить Git history.
5. Повторно проверить все refs и GitHub.
6. Только после ротации продолжить эксплуатацию.

Не публиковать секрет в issue при описании инцидента.

## Runtime permissions

Рекомендуется:

```text
~/.codex/auth.json      0600
Hermes config           0600
transcript output       0600
project source          без credential copies
```

Запускать bridge следует от того же изолированного Unix-пользователя, которому
принадлежит Codex login и Hermes runtime.

Production executable рекомендуется хранить в admin-owned/read-only checkout.
Command provider запускается с полными правами Unix-пользователя Hermes;
изменяемый агентом credential-handling код увеличивает persistence risk.
