"""
Gmail and Google Calendar operations for CFS.
Server-side operations via the Gmail and Calendar APIs, one identity per call.

Design principles:
  - Identity is explicit: every call names an account (-a/--account) whose
    OAuth credentials and token live under ~/.cfs/google/<account>/.
  - JSON on stdout for everything; diagnostics on stderr; non-zero exit on error.
  - Reads are free; writes are narrow, named commands (send, reply, draft,
    label, create, update, delete, respond).

Commands:
  auth                          Test authentication for the account
  gmail search <query>          Threads matching a Gmail query (-n, --page)
  gmail thread <id>             Full thread: headers, text bodies, attachments
  gmail message <id>            One message
  gmail labels                  List labels
  gmail label <thread-id>       Modify thread labels (--add, --remove)
  gmail draft                   Create a draft (--to, --subject, --body, ...)
  gmail send                    Send a message (same options as draft)
  gmail reply <thread-id>       Reply on a thread (--body, --all)
  calendar calendars            List calendars
  calendar events               List events (--calendar, --from, --to, -n, -q)
  calendar event <id>           One event
  calendar create               Create an event (--summary, --start, --end, ...)
  calendar update <id>          Patch an event (any create option)
  calendar delete <id>          Delete an event
  calendar respond <id>         RSVP as the account (--status)
  calendar freebusy             Busy intervals (--from, --to, --calendars)

Setup:
  1. Place OAuth Desktop App credentials at ~/.cfs/google/<account>/credentials.json
  2. First run per account opens a browser for consent; token saved alongside

Requires: google-api-python-client, google-auth, google-auth-oauthlib
"""

import argparse
import base64
import json
import sys
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]
ACCOUNTS_DIR = Path.home() / ".cfs" / "google"
HEADERS = (
    "From",
    "To",
    "Cc",
    "Subject",
    "Date",
    "Message-ID",
    "In-Reply-To",
    "References",
)


# ---------------------------------------------------------------------------
# Auth and output
# ---------------------------------------------------------------------------


def authenticate(account: str) -> Credentials:
    account_dir = ACCOUNTS_DIR / account
    credentials_path = account_dir / "credentials.json"
    token_path = account_dir / "token.json"
    creds = None
    changed = False

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            changed = True
        except RefreshError as e:
            dead = token_path.with_name(f"token.json.dead-{date.today().isoformat()}")
            token_path.replace(dead)
            print(
                f"Warning: token refresh failed ({e}); moved to {dead.name}; re-consenting",
                file=sys.stderr,
            )
            creds = None

    if not creds or not creds.valid:
        if not credentials_path.exists():
            fail(f"OAuth credentials not found at {credentials_path}")
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)
        changed = True

    if changed:
        token_path.write_text(creds.to_json())
        token_path.chmod(0o600)

    return creds


def fail(message: str, code: int = 1):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def emit(data) -> None:
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()


# ---------------------------------------------------------------------------
# Gmail
# ---------------------------------------------------------------------------


def _headers(payload: dict) -> dict:
    wanted = {h.lower(): h for h in HEADERS}
    out = {}
    for h in payload.get("headers", []):
        key = wanted.get(h["name"].lower())
        if key:
            out[key] = h["value"]
    return out


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode()).decode("utf-8", errors="replace")


def _walk_parts(
    part: dict, text: list[str], html: list[str], attachments: list[dict]
) -> None:
    mime = part.get("mimeType", "")
    body = part.get("body", {})
    filename = part.get("filename")
    if filename:
        attachments.append(
            {
                "filename": filename,
                "mimeType": mime,
                "size": body.get("size"),
                "attachmentId": body.get("attachmentId"),
            }
        )
    elif mime == "text/plain" and body.get("data"):
        text.append(_decode(body["data"]))
    elif mime == "text/html" and body.get("data"):
        html.append(_decode(body["data"]))
    for child in part.get("parts", []):
        _walk_parts(child, text, html, attachments)


def _message_view(msg: dict) -> dict:
    text, html, attachments = [], [], []
    _walk_parts(msg["payload"], text, html, attachments)
    view = {
        "id": msg["id"],
        "threadId": msg["threadId"],
        "labelIds": msg.get("labelIds", []),
        "internalDate": msg.get("internalDate"),
        **_headers(msg["payload"]),
        "text": "\n".join(text) if text else None,
    }
    if not text and html:
        view["html"] = "\n".join(html)
    if attachments:
        view["attachments"] = attachments
    return view


def _thread_summary(gmail, thread_id: str) -> dict:
    t = (
        gmail.users()
        .threads()
        .get(
            userId="me", id=thread_id, format="metadata", metadataHeaders=list(HEADERS)
        )
        .execute()
    )
    messages = t["messages"]
    first, last = messages[0]["payload"], messages[-1]["payload"]
    return {
        "id": t["id"],
        "messages": len(messages),
        "snippet": t.get("snippet"),
        "subject": _headers(first).get("Subject"),
        "from": _headers(first).get("From"),
        "lastFrom": _headers(last).get("From"),
        "lastDate": _headers(last).get("Date"),
        "labelIds": sorted(
            {label for m in messages for label in m.get("labelIds", [])}
        ),
    }


def cmd_gmail_search(gmail, query: str, limit: int, page: str | None):
    resp = (
        gmail.users()
        .threads()
        .list(userId="me", q=query, maxResults=limit, pageToken=page)
        .execute()
    )
    result = {
        "threads": [_thread_summary(gmail, t["id"]) for t in resp.get("threads", [])]
    }
    if resp.get("nextPageToken"):
        result["nextPage"] = resp["nextPageToken"]
    emit(result)


def cmd_gmail_thread(gmail, thread_id: str):
    t = gmail.users().threads().get(userId="me", id=thread_id, format="full").execute()
    emit({"id": t["id"], "messages": [_message_view(m) for m in t["messages"]]})


def cmd_gmail_message(gmail, message_id: str):
    emit(
        _message_view(
            gmail.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
    )


def cmd_gmail_labels(gmail):
    labels = gmail.users().labels().list(userId="me").execute().get("labels", [])
    emit(
        [
            {"id": label["id"], "name": label["name"], "type": label["type"]}
            for label in labels
        ]
    )


def _label_ids(gmail, names: list[str]) -> list[str]:
    by_name = {
        label["name"]: label["id"]
        for label in gmail.users()
        .labels()
        .list(userId="me")
        .execute()
        .get("labels", [])
    }
    ids = []
    for name in names:
        if name in by_name.values():
            ids.append(name)
        elif name in by_name:
            ids.append(by_name[name])
        else:
            fail(f"unknown label: {name}")
    return ids


def cmd_gmail_label(gmail, thread_id: str, add: list[str], remove: list[str]):
    body = {
        "addLabelIds": _label_ids(gmail, add),
        "removeLabelIds": _label_ids(gmail, remove),
    }
    t = gmail.users().threads().modify(userId="me", id=thread_id, body=body).execute()
    emit(
        {
            "id": t["id"],
            "labelIds": sorted(
                {label for m in t["messages"] for label in m.get("labelIds", [])}
            ),
        }
    )


def _build_message(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str],
    bcc: list[str],
    headers: dict | None = None,
) -> dict:
    msg = EmailMessage()
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = subject
    for k, v in (headers or {}).items():
        msg[k] = v
    msg.set_content(body)
    return {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def _outgoing(args) -> dict:
    return _build_message(args.to, args.subject, args.body, args.cc, args.bcc)


def cmd_gmail_draft(gmail, args):
    d = (
        gmail.users()
        .drafts()
        .create(userId="me", body={"message": _outgoing(args)})
        .execute()
    )
    emit(
        {
            "draftId": d["id"],
            "messageId": d["message"]["id"],
            "threadId": d["message"]["threadId"],
        }
    )


def cmd_gmail_send(gmail, args):
    m = gmail.users().messages().send(userId="me", body=_outgoing(args)).execute()
    emit({"messageId": m["id"], "threadId": m["threadId"]})


def cmd_gmail_reply(gmail, thread_id: str, body: str, reply_all: bool):
    t = (
        gmail.users()
        .threads()
        .get(
            userId="me", id=thread_id, format="metadata", metadataHeaders=list(HEADERS)
        )
        .execute()
    )
    last = _headers(t["messages"][-1]["payload"])
    me = gmail.users().getProfile(userId="me").execute()["emailAddress"]
    to = [last["From"]]
    cc = []
    if reply_all:
        others = [
            a.strip()
            for field in ("To", "Cc")
            for a in last.get(field, "").split(",")
            if a.strip()
        ]
        cc = [
            a
            for a in others
            if parseaddr(a)[1].lower() != me.lower() and a != last["From"]
        ]
    subject = last.get("Subject", "")
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    references = " ".join(
        filter(None, [last.get("References"), last.get("Message-ID")])
    )
    message = _build_message(
        to,
        subject,
        body,
        cc,
        [],
        {"In-Reply-To": last.get("Message-ID", ""), "References": references},
    )
    message["threadId"] = thread_id
    m = gmail.users().messages().send(userId="me", body=message).execute()
    emit({"messageId": m["id"], "threadId": m["threadId"], "to": to, "cc": cc})


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------


def _when(value: str, tz: str) -> dict:
    if "T" in value:
        return {"dateTime": value, "timeZone": tz}
    return {"date": value}


def _event_view(e: dict) -> dict:
    return {
        "id": e["id"],
        "status": e.get("status"),
        "summary": e.get("summary"),
        "start": e.get("start"),
        "end": e.get("end"),
        "location": e.get("location"),
        "description": e.get("description"),
        "organizer": e.get("organizer", {}).get("email"),
        "attendees": [
            {"email": a.get("email"), "responseStatus": a.get("responseStatus")}
            for a in e.get("attendees", [])
        ],
        "htmlLink": e.get("htmlLink"),
    }


def _calendar_tz(calendar, calendar_id: str) -> str:
    return (
        calendar.calendars()
        .get(calendarId=calendar_id)
        .execute()
        .get("timeZone", "UTC")
    )


def cmd_calendar_calendars(calendar):
    items = calendar.calendarList().list().execute().get("items", [])
    emit(
        [
            {
                "id": c["id"],
                "summary": c.get("summary"),
                "primary": c.get("primary", False),
                "accessRole": c.get("accessRole"),
                "timeZone": c.get("timeZone"),
            }
            for c in items
        ]
    )


def _iso(value: str | None, default: datetime | None = None) -> str:
    if value is None:
        return default.isoformat(timespec="seconds")
    return value if "T" in value else f"{value}T00:00:00Z"


def cmd_calendar_events(
    calendar,
    calendar_id: str,
    start: str | None,
    end: str | None,
    limit: int,
    query: str | None,
):
    now = datetime.now(timezone.utc)
    resp = (
        calendar.events()
        .list(
            calendarId=calendar_id,
            timeMin=_iso(start, now),
            timeMax=_iso(end, now + timedelta(days=30)),
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
            q=query,
        )
        .execute()
    )
    emit([_event_view(e) for e in resp.get("items", [])])


def cmd_calendar_event(calendar, calendar_id: str, event_id: str):
    emit(
        _event_view(
            calendar.events().get(calendarId=calendar_id, eventId=event_id).execute()
        )
    )


def _event_body(calendar, calendar_id: str, args) -> dict:
    tz = _calendar_tz(calendar, calendar_id)
    body = {}
    if args.summary is not None:
        body["summary"] = args.summary
    if args.description is not None:
        body["description"] = args.description
    if args.location is not None:
        body["location"] = args.location
    if args.start is not None:
        body["start"] = _when(args.start, tz)
    if args.end is not None:
        body["end"] = _when(args.end, tz)
    if args.attendees is not None:
        body["attendees"] = [{"email": a} for a in args.attendees]
    return body


def cmd_calendar_create(calendar, calendar_id: str, args):
    body = _event_body(calendar, calendar_id, args)
    if not {"summary", "start", "end"} <= body.keys():
        fail("--summary, --start and --end are required")
    emit(
        _event_view(
            calendar.events()
            .insert(calendarId=calendar_id, body=body, sendUpdates=args.notify)
            .execute()
        )
    )


def cmd_calendar_update(calendar, calendar_id: str, event_id: str, args):
    body = _event_body(calendar, calendar_id, args)
    if not body:
        fail("nothing to update")
    emit(
        _event_view(
            calendar.events()
            .patch(
                calendarId=calendar_id,
                eventId=event_id,
                body=body,
                sendUpdates=args.notify,
            )
            .execute()
        )
    )


def cmd_calendar_delete(calendar, calendar_id: str, event_id: str, notify: str):
    calendar.events().delete(
        calendarId=calendar_id, eventId=event_id, sendUpdates=notify
    ).execute()
    emit({"deleted": event_id})


def cmd_calendar_respond(calendar, calendar_id: str, event_id: str, status: str, gmail):
    me = gmail.users().getProfile(userId="me").execute()["emailAddress"].lower()
    e = calendar.events().get(calendarId=calendar_id, eventId=event_id).execute()
    attendees = e.get("attendees", [])
    mine = [a for a in attendees if a.get("email", "").lower() == me]
    if not mine:
        fail(f"{me} is not an attendee of {event_id}")
    mine[0]["responseStatus"] = status
    e = (
        calendar.events()
        .patch(
            calendarId=calendar_id,
            eventId=event_id,
            body={"attendees": attendees},
            sendUpdates="all",
        )
        .execute()
    )
    emit(_event_view(e))


def cmd_calendar_freebusy(calendar, start: str, end: str, calendars: list[str]):
    body = {
        "timeMin": _iso(start),
        "timeMax": _iso(end),
        "items": [{"id": c} for c in calendars],
    }
    resp = calendar.freebusy().query(body=body).execute()
    emit({cid: v.get("busy", []) for cid, v in resp.get("calendars", {}).items()})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_outgoing_options(p):
    p.add_argument("--to", nargs="+", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--cc", nargs="*", default=[])
    p.add_argument("--bcc", nargs="*", default=[])


def _add_event_options(p):
    p.add_argument("--summary")
    p.add_argument("--description")
    p.add_argument("--location")
    p.add_argument("--start", help="ISO 8601 date-time, or date for all-day")
    p.add_argument("--end", help="ISO 8601 date-time, or date for all-day")
    p.add_argument("--attendees", nargs="*")
    p.add_argument(
        "--notify",
        choices=["all", "externalOnly", "none"],
        default="none",
        help="Send invitations/updates",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Gmail and Google Calendar operations for CFS"
    )
    parser.add_argument(
        "-a", "--account", required=True, help="Identity under ~/.cfs/google/<account>/"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("auth", help="Test authentication")

    gm = sub.add_parser("gmail", help="Gmail operations").add_subparsers(
        dest="gmail_command", required=True
    )
    p = gm.add_parser("search", help="Threads matching a Gmail query")
    p.add_argument("query")
    p.add_argument("-n", "--limit", type=int, default=10)
    p.add_argument("--page", help="nextPage token from a previous search")
    gm.add_parser("thread", help="Full thread").add_argument("id")
    gm.add_parser("message", help="One message").add_argument("id")
    gm.add_parser("labels", help="List labels")
    p = gm.add_parser("label", help="Modify thread labels")
    p.add_argument("id")
    p.add_argument("--add", nargs="*", default=[], help="Label names or ids")
    p.add_argument("--remove", nargs="*", default=[], help="Label names or ids")
    _add_outgoing_options(gm.add_parser("draft", help="Create a draft"))
    _add_outgoing_options(gm.add_parser("send", help="Send a message"))
    p = gm.add_parser("reply", help="Reply on a thread")
    p.add_argument("id")
    p.add_argument("--body", required=True)
    p.add_argument("--all", action="store_true", help="Reply to all recipients")

    cal = sub.add_parser("calendar", help="Calendar operations").add_subparsers(
        dest="calendar_command", required=True
    )
    cal.add_parser("calendars", help="List calendars")
    p = cal.add_parser("events", help="List events")
    p.add_argument("--calendar", default="primary")
    p.add_argument("--from", dest="start", help="ISO 8601; default now")
    p.add_argument("--to", dest="end", help="ISO 8601; default now + 30 days")
    p.add_argument("-n", "--limit", type=int, default=25)
    p.add_argument("-q", "--query")
    p = cal.add_parser("event", help="One event")
    p.add_argument("id")
    p.add_argument("--calendar", default="primary")
    p = cal.add_parser("create", help="Create an event")
    p.add_argument("--calendar", default="primary")
    _add_event_options(p)
    p = cal.add_parser("update", help="Patch an event")
    p.add_argument("id")
    p.add_argument("--calendar", default="primary")
    _add_event_options(p)
    p = cal.add_parser("delete", help="Delete an event")
    p.add_argument("id")
    p.add_argument("--calendar", default="primary")
    p.add_argument("--notify", choices=["all", "externalOnly", "none"], default="none")
    p = cal.add_parser("respond", help="RSVP as the account")
    p.add_argument("id")
    p.add_argument("--calendar", default="primary")
    p.add_argument(
        "--status", choices=["accepted", "declined", "tentative"], required=True
    )
    p = cal.add_parser("freebusy", help="Busy intervals")
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--to", dest="end", required=True)
    p.add_argument("--calendars", nargs="+", default=["primary"])

    args = parser.parse_args()
    creds = authenticate(args.account)

    try:
        if args.command == "auth":
            gmail = build("gmail", "v1", credentials=creds)
            emit(
                {
                    "account": args.account,
                    "email": gmail.users()
                    .getProfile(userId="me")
                    .execute()["emailAddress"],
                }
            )
        elif args.command == "gmail":
            gmail = build("gmail", "v1", credentials=creds)
            c = args.gmail_command
            if c == "search":
                cmd_gmail_search(gmail, args.query, args.limit, args.page)
            elif c == "thread":
                cmd_gmail_thread(gmail, args.id)
            elif c == "message":
                cmd_gmail_message(gmail, args.id)
            elif c == "labels":
                cmd_gmail_labels(gmail)
            elif c == "label":
                cmd_gmail_label(gmail, args.id, args.add, args.remove)
            elif c == "draft":
                cmd_gmail_draft(gmail, args)
            elif c == "send":
                cmd_gmail_send(gmail, args)
            elif c == "reply":
                cmd_gmail_reply(gmail, args.id, args.body, args.all)
        else:
            calendar = build("calendar", "v3", credentials=creds)
            c = args.calendar_command
            if c == "calendars":
                cmd_calendar_calendars(calendar)
            elif c == "events":
                cmd_calendar_events(
                    calendar,
                    args.calendar,
                    args.start,
                    args.end,
                    args.limit,
                    args.query,
                )
            elif c == "event":
                cmd_calendar_event(calendar, args.calendar, args.id)
            elif c == "create":
                cmd_calendar_create(calendar, args.calendar, args)
            elif c == "update":
                cmd_calendar_update(calendar, args.calendar, args.id, args)
            elif c == "delete":
                cmd_calendar_delete(calendar, args.calendar, args.id, args.notify)
            elif c == "respond":
                cmd_calendar_respond(
                    calendar,
                    args.calendar,
                    args.id,
                    args.status,
                    build("gmail", "v1", credentials=creds),
                )
            elif c == "freebusy":
                cmd_calendar_freebusy(calendar, args.start, args.end, args.calendars)
    except HttpError as e:
        fail(f"{e.resp.status} {e.reason}")


if __name__ == "__main__":
    main()
