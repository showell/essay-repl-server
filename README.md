# essay-repl-server

The ladder droplet's public web surface: rendered markdown essays with
accounts and paragraph-anchored notes. The online Codex REPL will ride
on this same server; that is milestone 2 and not started.

The essay mechanics are ported from `claude-collab/server/` (Go, the
laptop's localhost surface) into Python; the inline-notes widget is
that server's, minus the type-your-own-name author box — here a note is
signed by the logged-in account.

## Run

    ./serve.sh              # foreground, port 9100
    ops/install.sh          # durable: systemd --user service

Dependencies are system packages: `python3-flask python3-markdown
python3-waitress` (apt). No CLI flags anywhere; configuration is
`config.py`.

## Routes

- `/essays` — published essays (served from the claude-collab clone's
  `essays/`; that repo is the canonical home, this box just renders it).
- `/notes` — this repo's `notes/`: droplet-side drafts and session
  essays.
- `/<collection>/<name>.md` — rendered essay, notes widget enabled.
- `/register`, `/login`, `/logout` — accounts.
- `/article-comments` — GET (public) / POST (logged in) for the widget.

## Data layout (gitignored)

- `data/users.db` — usernames + scrypt password hashes (SQLite).
- `data/secret_key` — session-cookie signing key; delete to log
  everyone out.
- `data/comments/<collection>/<name>.md.comments.json` — notes, same
  hand-editable schema as claude-collab sidecars. Kept here rather
  than beside the essays because the essays live in git clones and
  reader data does not belong in them.

## Security posture

Deliberately basic, on purpose and by agreement: passwords are scrypt
hashed and sessions signed, but there is no email verification, no
rate limiting, no CSRF tokens, and no TLS (no domain yet — plain HTTP
on 9100). Nothing on this box is secret; treat accounts as names for
notes, not identities.
