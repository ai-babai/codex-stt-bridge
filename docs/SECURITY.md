# Security

**English** | [Русский](SECURITY.ru.md)

## Threat model

The primary risk is leaking Codex OAuth credential material through Git,
logs, diagnostics, exception bodies, or accidental fixtures.

A private GitHub repository reduces public visibility but never makes storing
secrets acceptable.

## Sensitive material

- the complete `~/.codex/auth.json`;
- access, refresh, and ID tokens;
- account ID;
- browser cookies and device-auth callback URLs;
- Telegram bot token;
- real `.env` files;
- private audio recordings and transcripts.

## Implementation safeguards

- The endpoint is restricted to the HTTPS hostname `chatgpt.com`.
- HTTP redirects are rejected, so credential headers cannot follow a request
  to another URL or hostname.
- Tokens are not accepted through CLI arguments.
- Tokens are never written to stdout or stderr.
- Error response bodies are not printed.
- Response reads are limited to 1 MiB.
- Codex subprocess stderr is excluded from user-facing errors.
- The bridge never writes to the auth file.
- On POSIX, auth files with permissions broader than `0600` are rejected.
- Only explicitly allowlisted audio extensions are accepted.
- Output is written atomically with mode `0600`.
- Real audio formats and `auth.json` are ignored by Git.

## Before every push

Review:

```bash
git status --short
git diff --cached
git grep -n -I -E \
  '(access_token|refresh_token|id_token|Authorization: Bearer|deviceauth/callback)'
```

Documentation and field-name matches are acceptable only when they contain no
secret values.

Also scan staged blobs with a secret scanner when one is available.

Server-side secret scanning is not guaranteed for a private repository owned
by a personal GitHub account. A local pre-push check remains mandatory even
when Dependabot and other GitHub security features are enabled.

## If a secret enters Git

1. Do not assume that deleting the file in a new commit is sufficient.
2. Stop further pushes immediately.
3. Revoke or refresh the compromised OAuth session.
4. Remove the secret from Git history.
5. Scan all refs and GitHub again.
6. Resume operation only after rotation and verification.

Never paste the secret into an issue while reporting the incident.

## Runtime permissions

Recommended:

```text
~/.codex/auth.json      0600
Hermes config           0600
transcript output       0600
project source          no credential copies
```

Run the bridge as the same isolated Unix user that owns the Codex login and
Hermes runtime.

Keep the production executable in an admin-owned, read-only checkout. A
command provider runs with the full permissions of the Hermes Unix user;
agent-writable credential-handling code increases the persistence risk.
