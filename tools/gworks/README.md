# gworks

Optional CFS-bundled reference implementation for Gmail and Google Calendar operations. A CLI over the Gmail and Calendar APIs, one identity per call, JSON on stdout.

Use when your environment has no native, MCP, or connector capability for the identity you need — typically a second Google account beside the one a harness connector is bound to.

## When to use

- **Knowledge encoding** — read threads and events for an identity into context.
- **Filing** — pull message bodies and attachments metadata as source material.
- **Writes** — drafts, sends, replies, label changes, event create/update/delete, RSVPs. Writes are separate commands; nothing else mutates.

Drive stays with [`gdrive`](../gdrive/README.md).

## Setup

```bash
bash tools/gworks/setup.sh
```

Creates a venv at `~/.cfs/tools/gworks/.venv` and installs the Google API client libraries.

### Prerequisites

- Python 3.12+
- OAuth Desktop App credentials per identity at `~/.cfs/google/<account>/credentials.json`

### Identities

Each identity is a directory under `~/.cfs/google/`:

```
~/.cfs/google/personal/credentials.json   OAuth client (Desktop App) JSON
~/.cfs/google/personal/token.json         written on first consent
~/.cfs/google/work/credentials.json
~/.cfs/google/work/token.json
```

One OAuth client may serve several identities; each consent yields its own token. Use a client whose consent screen is **Internal** (Workspace org project) or **External + In production** — External + Testing expires refresh tokens after 7 days.

### Google credentials (one-time per client)

1. Google Cloud Console → enable the Gmail API and Google Calendar API
2. Google Auth Platform → Branding, Audience (Internal or In production), Data access
3. Create OAuth 2.0 Desktop App credentials → download JSON → `~/.cfs/google/<account>/credentials.json`
4. Consent: `~/.cfs/tools/gworks/.venv/bin/python tools/gworks/gworks.py -a <account> auth`

Scopes requested: `gmail.modify`, `gmail.send`, `calendar.events`, `calendar.readonly`.

## Commands

```bash
PYTHON=~/.cfs/tools/gworks/.venv/bin/python
SCRIPT=tools/gworks/gworks.py
G="$PYTHON $SCRIPT -a work"        # identity is always explicit

$G auth

# Gmail
$G gmail search 'from:someone newer_than:7d' -n 10
$G gmail search 'label:INBOX is:unread' --page <nextPage>
$G gmail thread <thread-id>
$G gmail message <message-id>
$G gmail labels
$G gmail label <thread-id> --add Clients --remove INBOX
$G gmail draft --to someone@example.com --subject "…" --body "…" [--cc …] [--bcc …]  # pii:allow
$G gmail send  --to someone@example.com --subject "…" --body "…"  # pii:allow
$G gmail reply <thread-id> --body "…" [--all]

# Calendar
$G calendar calendars
$G calendar events [--calendar primary] [--from 2026-09-01] [--to 2026-09-30] [-n 25] [-q text]
$G calendar event <event-id>
$G calendar create --summary "…" --start 2026-09-10T14:00:00 --end 2026-09-10T15:00:00 [--attendees someone@example.com other@example.com] [--notify all]  # pii:allow
$G calendar create --summary "…" --start 2026-09-10 --end 2026-09-11          # all-day
$G calendar update <event-id> --location "…"
$G calendar delete <event-id> [--notify all]
$G calendar respond <event-id> --status accepted|declined|tentative
$G calendar freebusy --from 2026-09-10T00:00:00Z --to 2026-09-11T00:00:00Z [--calendars primary shared@example.com]  # pii:allow
```

Date-times without an offset are interpreted in the target calendar's time zone; a bare date means all-day. `search` returns thread summaries with a `nextPage` token; `thread` returns full messages with `text` (or `html` when no plain part) and `attachments` metadata.

## Output and errors

Every command prints JSON to stdout. Errors go to stderr with exit code 1 (`Error: 404 Not Found`). A revoked or expired token is moved aside as `token.json.dead-<date>` and a fresh consent is opened in the browser.
