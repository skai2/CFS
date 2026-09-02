"""
Google Drive operations for CFS.
Server-side file operations via the Drive API.

Design principles:
  - Server-side by default. Every operation that can work without local FS
    access does so.
  - POSIX-inspired CLI (ls, cp, mv, rm, mkdir, find) with safety-first flags.
  - Drive IDs are first-class: any target argument can be a path (resolved
    by walking the Drive tree) or an explicit ID (prefix with "id:").
  - Trailing slash on a target means "folder": `foo/` must be a folder.
  - Destructive actions require explicit flags: -r for folder recursion,
    -f to overwrite existing targets.

Target syntax:
  System/Archive/Entity         — file at this path
  System/Archive/Entity/        — folder at this path (trailing slash)
  id:1abcXYZ...                 — Drive ID (type is discovered via API)

Commands:
  auth              Test authentication
  ls <target>       List folder contents
  mkdir <path>      Create folder(s), idempotent, creates parents
  cp <src> <dest>   Copy file or folder (-r for folder, -f to overwrite)
  mv <src> <dest>   Move file or folder (-f to overwrite)
  rm <target>       Delete file or folder (-r for folder, --stdin for batch)
  find <root>       Recursive search (--name, --type, --mime, --max-depth)
  upload <l> <d>    Upload local file (-f to overwrite)
  download <t>      Download file content (-o for file, else stdout)
  restore-rev <t>   Restore to latest non-empty revision (-f, --stdin)
  export <t>        Export Google-native file content (-o for file, else stdout)
  sync-diff <l> <d> Compare local directory to Drive folder

Setup:
  1. Place OAuth credentials at ~/.cfs/credentials_gdrive.json
  2. First run opens browser for consent; token saved to ~/.cfs/token.json

Requires: google-api-python-client, google-auth, google-auth-oauthlib
"""

import io
import json
import mimetypes
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from datetime import date
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import (
    MediaFileUpload,
    MediaIoBaseDownload,
    MediaIoBaseUpload,
)

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_PATH = Path.home() / ".cfs" / "credentials_gdrive.json"
TOKEN_PATH = Path.home() / ".cfs" / "token.json"

FOLDER_MIME = "application/vnd.google-apps.folder"

GSUITE_MIMES = {
    "application/vnd.google-apps.document": ".gdoc",
    "application/vnd.google-apps.spreadsheet": ".gsheet",
    "application/vnd.google-apps.presentation": ".gslides",
}

EXPORT_MIMES = {
    ".gdoc": {
        "md": "text/markdown",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "txt": "text/plain",
    },
    ".gsheet": {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "pdf": "application/pdf",
    },
    ".gslides": {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
    },
}

DEFAULT_EXPORT_FORMAT = {".gdoc": "md", ".gsheet": "xlsx", ".gslides": "pptx"}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def authenticate():
    """Authenticate with Google Drive API. Returns service object."""
    creds = None
    changed = False

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            changed = True
        except RefreshError as e:
            # Refresh token revoked/expired (invalid_grant): fall through to a fresh
            # consent instead of crashing. Keep the dead token aside for forensics.
            dead = TOKEN_PATH.with_name(f"token.json.dead-{date.today().isoformat()}")
            TOKEN_PATH.replace(dead)
            print(
                f"Warning: token refresh failed ({e}); moved to {dead.name}; re-consenting",
                file=sys.stderr,
            )
            creds = None

    if not creds or not creds.valid:
        if not CREDENTIALS_PATH.exists():
            print(
                f"Error: OAuth credentials not found at {CREDENTIALS_PATH}\n"
                f"Download from Google Cloud Console → APIs & Services → Credentials",
                file=sys.stderr,
            )
            sys.exit(1)
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        changed = True

    if changed:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# Target parsing and resolution
# ---------------------------------------------------------------------------


def parse_target(arg: str) -> dict:
    """Parse a target argument into structured form.

    Returns one of:
      {'id': '<drive_id>'}
      {'path': '<drive_path>', 'expects_folder': bool}
    """
    if arg.startswith("id:"):
        return {"id": arg[3:]}
    expects_folder = arg.endswith("/")
    return {"path": arg.rstrip("/"), "expects_folder": expects_folder}


def resolve_path(service, folder_path: str, root_id: str = "root") -> str | None:
    """Resolve a Drive path to a file/folder ID. Returns None if not found."""
    parts = [p for p in folder_path.split("/") if p]
    current_id = root_id

    for part in parts:
        query = f"name='{_escape_query(part)}' and '{current_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])
        if not files:
            return None
        current_id = files[0]["id"]

    return current_id


def _escape_query(value: str) -> str:
    """Escape a value for inclusion in a Drive query string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_or_create_folder(service, folder_path: str, root_id: str = "root") -> str:
    """Find or create a folder path on Drive. Returns the folder ID."""
    parts = [p for p in folder_path.split("/") if p]
    parent_id = root_id

    for part in parts:
        query = (
            f"name='{_escape_query(part)}' and '{parent_id}' in parents "
            f"and mimeType='{FOLDER_MIME}' and trashed=false"
        )
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])

        if files:
            parent_id = files[0]["id"]
        else:
            metadata = {
                "name": part,
                "mimeType": FOLDER_MIME,
                "parents": [parent_id],
            }
            folder = service.files().create(body=metadata, fields="id").execute()
            parent_id = folder["id"]

    return parent_id


def resolve_target(service, target: dict) -> dict | None:
    """Resolve a parsed target to Drive metadata. Returns None if not found.

    Returns: {'id', 'name', 'mimeType', 'is_folder'} or None.
    """
    if "id" in target:
        try:
            info = (
                service.files()
                .get(fileId=target["id"], fields="id,name,mimeType,trashed")
                .execute()
            )
            if info.get("trashed"):
                return None
            info["is_folder"] = info["mimeType"] == FOLDER_MIME
            return info
        except HttpError as e:
            if e.resp.status in (404, 410):
                return None
            raise

    path = target["path"]
    if not path:
        return {
            "id": "root",
            "name": "My Drive",
            "mimeType": FOLDER_MIME,
            "is_folder": True,
        }

    file_id = resolve_path(service, path)
    if not file_id:
        return None

    info = service.files().get(fileId=file_id, fields="id,name,mimeType").execute()
    info["is_folder"] = info["mimeType"] == FOLDER_MIME
    return info


def require_target(service, target: dict, arg_repr: str) -> dict:
    """Like resolve_target but raises if not found."""
    info = resolve_target(service, target)
    if not info:
        raise FileNotFoundError(f"not found: {arg_repr}")
    return info


def split_path(path: str) -> tuple[str, str]:
    """Split a path into (parent_path, final_name)."""
    path = path.rstrip("/")
    if "/" not in path:
        return "", path
    parent, _, name = path.rpartition("/")
    return parent, name


# ---------------------------------------------------------------------------
# ls
# ---------------------------------------------------------------------------


def list_folder(service, folder_id: str) -> list[dict]:
    """List direct children of a folder by ID."""
    items = []
    page_token = None
    while True:
        results = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        items.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return items


# ---------------------------------------------------------------------------
# Internal operation helpers (by ID)
# ---------------------------------------------------------------------------


def _copy_file_by_id(
    service, source_id: str, dest_parent_id: str, name: str, force: bool = False
) -> dict:
    """Copy a single file (not folder) by ID to a parent folder with given name.
    If a file with the same name already exists in dest_parent, overwrite it
    (delete + recreate) when force=True, else raise FileExistsError.
    """
    existing = _find_child_by_name(service, dest_parent_id, name)
    if existing and not force:
        raise FileExistsError(f"file exists: {name}")
    if existing and force:
        service.files().delete(fileId=existing["id"]).execute()

    body = {"parents": [dest_parent_id], "name": name}
    return (
        service.files()
        .copy(fileId=source_id, body=body, fields="id,name,mimeType,size")
        .execute()
    )


def _find_child_by_name(service, parent_id: str, name: str) -> dict | None:
    """Find a direct child of parent_id with the given name. Returns None if absent."""
    query = (
        f"name='{_escape_query(name)}' and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id,name,mimeType)").execute()
    files = results.get("files", [])
    return files[0] if files else None


def _copy_folder_tree(
    service,
    source_id: str,
    dest_parent_id: str,
    dest_name: str,
    force: bool = False,
    stats: dict | None = None,
) -> dict:
    """Recursively copy a folder tree. If dest_name exists in dest_parent:
    - if it's a file: error
    - if it's a folder: merge source children into it (file collisions require force)
    """
    if stats is None:
        stats = {
            "folders_created": 0,
            "folders_merged": 0,
            "files_copied": 0,
            "files_overwritten": 0,
        }

    existing = _find_child_by_name(service, dest_parent_id, dest_name)
    if existing:
        if existing["mimeType"] != FOLDER_MIME:
            raise ValueError(f"cannot copy folder over existing file: {dest_name}")
        new_folder_id = existing["id"]
        stats["folders_merged"] += 1
    else:
        metadata = {
            "name": dest_name,
            "mimeType": FOLDER_MIME,
            "parents": [dest_parent_id],
        }
        new_folder_id = (
            service.files().create(body=metadata, fields="id").execute()["id"]
        )
        stats["folders_created"] += 1

    children = list_folder(service, source_id)
    for child in children:
        if child["mimeType"] == FOLDER_MIME:
            _copy_folder_tree(
                service, child["id"], new_folder_id, child["name"], force, stats
            )
        else:
            existing_file = _find_child_by_name(service, new_folder_id, child["name"])
            if existing_file and not force:
                raise FileExistsError(
                    f"file exists in destination: {child['name']} (use -f to overwrite)"
                )
            if existing_file and force:
                service.files().delete(fileId=existing_file["id"]).execute()
                stats["files_overwritten"] += 1
            else:
                stats["files_copied"] += 1
            body = {"parents": [new_folder_id], "name": child["name"]}
            service.files().copy(fileId=child["id"], body=body, fields="id").execute()

    return {"id": new_folder_id, "stats": stats}


def _move_by_id(
    service,
    source_id: str,
    dest_parent_id: str,
    new_name: str | None = None,
) -> dict:
    """Move a file or folder by ID. Optionally rename."""
    info = service.files().get(fileId=source_id, fields="parents,name").execute()
    current_parents = info.get("parents", [])
    body = {}
    if new_name and new_name != info["name"]:
        body["name"] = new_name
    return (
        service.files()
        .update(
            fileId=source_id,
            addParents=dest_parent_id,
            removeParents=",".join(current_parents),
            body=body,
            fields="id,name,parents",
        )
        .execute()
    )


def _delete_by_id(service, file_id: str) -> None:
    """Permanent delete (not trash). Folders deleted recursively."""
    service.files().delete(fileId=file_id).execute()


def _restore_by_id(service, file_id: str) -> dict | None:
    """Restore file to its latest non-empty revision. Returns None if no
    non-empty revision exists. Only works for binary/regular files, not gsuite
    (gsuite files manage revisions internally; use Drive web UI for those)."""
    revs = (
        service.revisions()
        .list(fileId=file_id, fields="revisions(id,size,modifiedTime)")
        .execute()
        .get("revisions", [])
    )

    target_rev = None
    for rev in reversed(revs):
        size = rev.get("size")
        if size is not None and int(size) > 0:
            target_rev = rev
            break

    if not target_rev:
        return None

    request = service.revisions().get_media(fileId=file_id, revisionId=target_rev["id"])
    content = io.BytesIO()
    downloader = MediaIoBaseDownload(content, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    content.seek(0)
    media = MediaIoBaseUpload(
        content, mimetype="application/octet-stream", resumable=True
    )
    result = (
        service.files()
        .update(fileId=file_id, media_body=media, fields="id,name,size")
        .execute()
    )
    result["restored_from_revision"] = target_rev["id"]
    result["restored_size"] = target_rev.get("size")
    return result


# ---------------------------------------------------------------------------
# cp command
# ---------------------------------------------------------------------------


def cmd_cp(service, source_arg: str, dest_arg: str, recursive: bool, force: bool):
    source = parse_target(source_arg)
    src_info = require_target(service, source, source_arg)

    if src_info["is_folder"] and not recursive:
        raise ValueError(f"'{source_arg}' is a folder, use -r for recursive copy")

    dest = parse_target(dest_arg)
    dest_info = resolve_target(service, dest)

    if dest_info:
        if dest_info["is_folder"]:
            # Copy INTO this folder using source's name
            target_parent_id = dest_info["id"]
            target_name = src_info["name"]
            existing = _find_child_by_name(service, target_parent_id, target_name)
            if existing and not force and not src_info["is_folder"]:
                raise FileExistsError(
                    f"'{target_name}' exists in destination; use -f to overwrite"
                )
        else:
            if dest.get("expects_folder"):
                raise ValueError(f"'{dest_arg}' has trailing slash but is a file")
            if src_info["is_folder"]:
                raise ValueError(f"cannot copy folder over existing file: '{dest_arg}'")
            if not force:
                raise FileExistsError(f"'{dest_arg}' exists; use -f to overwrite")
            # Replace file
            _delete_by_id(service, dest_info["id"])
            parent_path, target_name = split_path(dest["path"])
            parent_id = resolve_path(service, parent_path)
            target_parent_id = parent_id
    else:
        # Dest doesn't exist — treat final segment as new name
        if "id" in dest:
            raise FileNotFoundError(f"dest ID not found: {dest_arg}")
        if dest.get("expects_folder"):
            raise FileNotFoundError(
                f"dest folder doesn't exist: '{dest_arg}' (use mkdir first)"
            )
        parent_path, target_name = split_path(dest["path"])
        target_parent_id = resolve_path(service, parent_path)
        if not target_parent_id:
            raise FileNotFoundError(
                f"parent folder doesn't exist: '{parent_path}' (use mkdir first)"
            )

    if src_info["is_folder"]:
        result = _copy_folder_tree(
            service, src_info["id"], target_parent_id, target_name, force
        )
        stats = result["stats"]
        print(
            f"Copied folder '{src_info['name']}' → '{target_name}' "
            f"(folders: {stats['folders_created']} created, {stats['folders_merged']} merged; "
            f"files: {stats['files_copied']} copied, {stats['files_overwritten']} overwritten)"
        )
    else:
        result = _copy_file_by_id(
            service, src_info["id"], target_parent_id, target_name, force=force
        )
        print(f"Copied: {result['name']} (id: {result['id']})")


# ---------------------------------------------------------------------------
# mv command
# ---------------------------------------------------------------------------


def cmd_mv(service, source_arg: str, dest_arg: str, force: bool):
    source = parse_target(source_arg)
    src_info = require_target(service, source, source_arg)

    dest = parse_target(dest_arg)
    dest_info = resolve_target(service, dest)

    if dest_info:
        if dest_info["is_folder"]:
            target_parent_id = dest_info["id"]
            target_name = src_info["name"]
            existing = _find_child_by_name(service, target_parent_id, target_name)
            if existing and not force:
                raise FileExistsError(
                    f"'{target_name}' exists in destination; use -f to overwrite"
                )
            if existing and force:
                _delete_by_id(service, existing["id"])
        else:
            if dest.get("expects_folder"):
                raise ValueError(f"'{dest_arg}' has trailing slash but is a file")
            if src_info["is_folder"]:
                raise ValueError(f"cannot move folder over existing file: '{dest_arg}'")
            if not force:
                raise FileExistsError(f"'{dest_arg}' exists; use -f to overwrite")
            _delete_by_id(service, dest_info["id"])
            parent_path, target_name = split_path(dest["path"])
            target_parent_id = resolve_path(service, parent_path)
    else:
        if "id" in dest:
            raise FileNotFoundError(f"dest ID not found: {dest_arg}")
        if dest.get("expects_folder"):
            raise FileNotFoundError(
                f"dest folder doesn't exist: '{dest_arg}' (use mkdir first)"
            )
        parent_path, target_name = split_path(dest["path"])
        target_parent_id = resolve_path(service, parent_path)
        if not target_parent_id:
            raise FileNotFoundError(
                f"parent folder doesn't exist: '{parent_path}' (use mkdir first)"
            )

    result = _move_by_id(
        service, src_info["id"], target_parent_id, new_name=target_name
    )
    print(f"Moved: {result['name']} (id: {result['id']})")


# ---------------------------------------------------------------------------
# rm command
# ---------------------------------------------------------------------------


def cmd_rm(
    service,
    target_arg: str | None,
    recursive: bool,
    from_stdin: bool,
):
    if from_stdin and target_arg is not None:
        raise ValueError("cannot specify both target and --stdin")
    if not from_stdin and target_arg is None:
        raise ValueError("specify a target or use --stdin")

    def delete_one(tid: str) -> tuple[bool, str]:
        try:
            info = (
                service.files()
                .get(fileId=tid, fields="id,name,mimeType,trashed")
                .execute()
            )
            if info.get("trashed"):
                return False, f"already trashed: {info['name']}"
            if info["mimeType"] == FOLDER_MIME and not recursive:
                return False, f"'{info['name']}' is a folder (use -r)"
            _delete_by_id(service, tid)
            return True, info["name"]
        except HttpError as e:
            if e.resp.status in (404, 410):
                return False, "already deleted"
            raise

    if from_stdin:
        ids = [line.strip() for line in sys.stdin if line.strip()]
        deleted = 0
        errors = 0
        for tid in ids:
            ok, msg = delete_one(tid)
            if ok:
                print(f"RM: {msg}", file=sys.stderr)
                deleted += 1
            else:
                # Skipping already-deleted isn't an error; other failures are
                if "already deleted" in msg or "already trashed" in msg:
                    print(f"skip: {msg}", file=sys.stderr)
                else:
                    print(f"ERR: {tid}: {msg}", file=sys.stderr)
                    errors += 1
        print(f"\n{deleted} deleted, {errors} errors", file=sys.stderr)
        return

    target = parse_target(target_arg)
    info = require_target(service, target, target_arg)
    if info["is_folder"] and not recursive:
        raise ValueError(f"'{info['name']}' is a folder, use -r")
    _delete_by_id(service, info["id"])
    print(f"Deleted: {info['name']}")


# ---------------------------------------------------------------------------
# find command
# ---------------------------------------------------------------------------


def _parse_since(s: str) -> str:
    """Parse ISO 8601 or relative (Nd/Nh/Nm) into a UTC Z-suffixed string."""
    import re
    from datetime import datetime, timedelta, timezone

    m = re.fullmatch(r"(\d+)([dhm])", s)
    if m:
        n = int(m.group(1))
        unit_map = {"d": "days", "h": "hours", "m": "minutes"}
        dt = datetime.now(timezone.utc) - timedelta(**{unit_map[m.group(2)]: n})
    else:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"invalid time: {s!r} (use ISO 8601 or Nd/Nh/Nm)") from e
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_find(
    service,
    root_arg: str,
    name: str | None,
    type_filter: str | None,
    mime_filter: str | None,
    max_depth: int | None,
    output_format: str,
    modified_since: str | None,
    created_since: str | None,
    skip: list[str] | None,
):
    root = parse_target(root_arg)
    root_info = require_target(service, root, root_arg)
    if not root_info["is_folder"]:
        raise ValueError(f"'{root_arg}' is not a folder")

    if "path" in root:
        root_path = root["path"]
    else:
        # For id: prefix root, paths in output start from the root's name
        root_path = root_info["name"]

    ms = _parse_since(modified_since) if modified_since else None
    cs = _parse_since(created_since) if created_since else None
    skip_set = set(skip or [])

    matches = _walk(
        service,
        root_info["id"],
        root_path,
        name,
        type_filter,
        mime_filter,
        max_depth,
        current_depth=0,
        skip=skip_set,
    )

    if ms or cs:
        matches = [
            m
            for m in matches
            if (not ms or m["modifiedTime"] > ms) and (not cs or m["createdTime"] > cs)
        ]

    for item in matches:
        if output_format == "ids":
            print(item["id"])
        elif output_format == "paths":
            print(item["path"])
        elif output_format == "json":
            print(json.dumps(item, ensure_ascii=False))


def _walk(
    service,
    folder_id: str,
    folder_path: str,
    name: str | None,
    type_filter: str | None,
    mime_filter: str | None,
    max_depth: int | None,
    current_depth: int,
    skip: set | None = None,
) -> list[dict]:
    if max_depth is not None and current_depth >= max_depth:
        return []

    skip = skip or set()
    results = []
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields=(
                    "nextPageToken, "
                    "files(id,name,mimeType,size,modifiedTime,createdTime)"
                ),
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        for item in response.get("files", []):
            is_folder = item["mimeType"] == FOLDER_MIME
            # Skip pruned subtrees entirely
            if is_folder and item["name"] in skip:
                continue
            item_path = f"{folder_path}/{item['name']}" if folder_path else item["name"]

            matches_name = name is None or item["name"] == name
            matches_type = (
                type_filter is None
                or (type_filter == "folder" and is_folder)
                or (type_filter == "file" and not is_folder)
            )
            matches_mime = mime_filter is None or item["mimeType"] == mime_filter

            if matches_name and matches_type and matches_mime:
                results.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "path": item_path,
                        "mimeType": item["mimeType"],
                        "size": item.get("size"),
                        "modifiedTime": item.get("modifiedTime"),
                        "createdTime": item.get("createdTime"),
                    }
                )

            if is_folder:
                results.extend(
                    _walk(
                        service,
                        item["id"],
                        item_path,
                        name,
                        type_filter,
                        mime_filter,
                        max_depth,
                        current_depth + 1,
                        skip=skip,
                    )
                )

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return results


# ---------------------------------------------------------------------------
# upload command
# ---------------------------------------------------------------------------


def cmd_upload(service, local_arg: str, dest_arg: str, force: bool):
    local = Path(local_arg).resolve()
    if not local.exists():
        raise FileNotFoundError(f"local file not found: {local}")
    if not local.is_file():
        raise ValueError(f"not a file: {local}")

    dest = parse_target(dest_arg)
    dest_info = resolve_target(service, dest)
    mime_type = mimetypes.guess_type(str(local))[0] or "application/octet-stream"

    if dest_info:
        if dest_info["is_folder"]:
            # Upload into folder
            target_parent_id = dest_info["id"]
            target_name = local.name
            existing = _find_child_by_name(service, target_parent_id, target_name)
            if existing and not force:
                raise FileExistsError(
                    f"'{target_name}' exists in destination; use -f to overwrite"
                )
            if existing and force:
                media = MediaFileUpload(str(local), mimetype=mime_type, resumable=True)
                result = (
                    service.files()
                    .update(
                        fileId=existing["id"],
                        media_body=media,
                        fields="id,name,size",
                    )
                    .execute()
                )
                print(f"Updated: {result['name']} ({result.get('size', '?')} bytes)")
                return
        else:
            if dest.get("expects_folder"):
                raise ValueError(f"'{dest_arg}' has trailing slash but is a file")
            if not force:
                raise FileExistsError(f"'{dest_arg}' exists; use -f to overwrite")
            # Overwrite the existing file directly
            media = MediaFileUpload(str(local), mimetype=mime_type, resumable=True)
            result = (
                service.files()
                .update(fileId=dest_info["id"], media_body=media, fields="id,name,size")
                .execute()
            )
            print(f"Updated: {result['name']} ({result.get('size', '?')} bytes)")
            return
    else:
        if "id" in dest:
            raise FileNotFoundError(f"dest ID not found: {dest_arg}")
        if dest.get("expects_folder"):
            raise FileNotFoundError(
                f"dest folder doesn't exist: '{dest_arg}' (use mkdir first)"
            )
        parent_path, target_name = split_path(dest["path"])
        target_parent_id = resolve_path(service, parent_path)
        if not target_parent_id:
            raise FileNotFoundError(
                f"parent folder doesn't exist: '{parent_path}' (use mkdir first)"
            )

    # New upload
    media = MediaFileUpload(str(local), mimetype=mime_type, resumable=True)
    metadata = {"name": target_name, "parents": [target_parent_id]}
    result = (
        service.files()
        .create(body=metadata, media_body=media, fields="id,name,size")
        .execute()
    )
    print(f"Uploaded: {result['name']} ({result.get('size', '?')} bytes)")


# ---------------------------------------------------------------------------
# restore-rev command
# ---------------------------------------------------------------------------


def cmd_restore_rev(service, target_arg: str | None, force: bool, from_stdin: bool):
    if not force:
        raise ValueError(
            "restore-rev overwrites current file content; use -f to confirm"
        )
    if from_stdin and target_arg is not None:
        raise ValueError("cannot specify both target and --stdin")
    if not from_stdin and target_arg is None:
        raise ValueError("specify a target or use --stdin")

    def restore_one(tid: str) -> tuple[str, dict | None]:
        try:
            return "ok", _restore_by_id(service, tid)
        except Exception as e:
            return f"err:{e}", None

    if from_stdin:
        ids = [line.strip() for line in sys.stdin if line.strip()]
        restored = 0
        no_rev = 0
        errors = 0
        for tid in ids:
            status, result = restore_one(tid)
            if status == "ok" and result:
                print(f"RESTORED: {result['name']}", file=sys.stderr)
                restored += 1
            elif status == "ok" and result is None:
                print(f"no non-empty revision: {tid}", file=sys.stderr)
                no_rev += 1
            else:
                print(f"ERR: {tid}: {status}", file=sys.stderr)
                errors += 1
        print(
            f"\n{restored} restored, {no_rev} no non-empty revision, {errors} errors",
            file=sys.stderr,
        )
        return

    target = parse_target(target_arg)
    info = require_target(service, target, target_arg)
    if info["is_folder"]:
        raise ValueError("cannot restore a folder; use a file target")
    result = _restore_by_id(service, info["id"])
    if result:
        print(
            f"Restored: {result['name']} to revision "
            f"{result['restored_from_revision']} "
            f"({result.get('restored_size', '?')} bytes)"
        )
    else:
        raise ValueError(f"no non-empty revision found for {info['name']}")


# ---------------------------------------------------------------------------
# Byte output helpers — shared by download and export
# ---------------------------------------------------------------------------


def _write_bytes(content: bytes, output: str | None, force: bool) -> None:
    """Write bytes to a file (if output is given) or to stdout."""
    if output:
        out_path = Path(output)
        if out_path.exists() and not force:
            raise FileExistsError(f"'{output}' exists; use -f to overwrite")
        out_path.write_bytes(content)
        print(f"Wrote {len(content)} bytes to {output}", file=sys.stderr)
        return
    try:
        sys.stdout.buffer.write(content)
    except AttributeError:
        sys.stdout.write(content.decode("utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# download command
# ---------------------------------------------------------------------------


def cmd_download(service, target_arg: str, output: str | None, force: bool):
    target = parse_target(target_arg)
    info = require_target(service, target, target_arg)

    if info["is_folder"]:
        raise ValueError(f"'{target_arg}' is a folder, download requires a file")

    mime = info["mimeType"]
    if mime in GSUITE_MIMES:
        raise ValueError(
            f"'{info['name']}' is a Google-native file ({mime}); use export instead"
        )

    content = service.files().get_media(fileId=info["id"]).execute()
    _write_bytes(content, output, force)


# ---------------------------------------------------------------------------
# export command
# ---------------------------------------------------------------------------


def cmd_export(
    service, target_arg: str, fmt: str | None, output: str | None, force: bool
):
    target = parse_target(target_arg)
    info = require_target(service, target, target_arg)

    mime = info["mimeType"]
    if mime not in GSUITE_MIMES:
        raise ValueError(f"not a Google-native file: {info['name']} (mime: {mime})")

    ext = GSUITE_MIMES[mime]
    fmt = fmt or DEFAULT_EXPORT_FORMAT[ext]
    export_mime = EXPORT_MIMES[ext].get(fmt)
    if not export_mime:
        raise ValueError(
            f"unsupported format '{fmt}' for {ext}; "
            f"options: {list(EXPORT_MIMES[ext].keys())}"
        )

    content = service.files().export(fileId=info["id"], mimeType=export_mime).execute()
    if isinstance(content, str):
        content = content.encode("utf-8")
    _write_bytes(content, output, force)


# ---------------------------------------------------------------------------
# mkdir command
# ---------------------------------------------------------------------------


def cmd_mkdir(service, path: str):
    folder_id = find_or_create_folder(service, path.rstrip("/"))
    print(f"Folder ready: {path} (id: {folder_id})")


# ---------------------------------------------------------------------------
# ls command
# ---------------------------------------------------------------------------


def cmd_ls(service, target_arg: str):
    target = parse_target(target_arg)
    info = require_target(service, target, target_arg)
    if not info["is_folder"]:
        raise ValueError(f"'{target_arg}' is not a folder")

    items = list_folder(service, info["id"])
    folders = sorted(
        [i for i in items if i["mimeType"] == FOLDER_MIME], key=lambda x: x["name"]
    )
    files = sorted(
        [i for i in items if i["mimeType"] != FOLDER_MIME], key=lambda x: x["name"]
    )
    for item in folders:
        print(f"  {item['name']}/")
    for item in files:
        size = item.get("size", "")
        print(f"  {item['name']}  {size}")


# ---------------------------------------------------------------------------
# sync-diff command (preserved — purpose is local ↔ server comparison)
# ---------------------------------------------------------------------------


def _get_drivefs_item_id(path: str) -> str | None:
    """Read the com.google.drivefs.item-id xattr on a local file/folder."""
    import subprocess

    try:
        result = subprocess.run(
            ["xattr", "-p", "com.google.drivefs.item-id#S", path],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _resolve_id_to_path(service, file_id: str) -> str | None:
    """Walk a Drive file's parent chain to build its full path."""
    parts = []
    current_id = file_id
    try:
        while True:
            info = (
                service.files()
                .get(fileId=current_id, fields="id,name,parents")
                .execute()
            )
            parents = info.get("parents", [])
            if not parents:
                break
            parts.append(info["name"])
            current_id = parents[0]
        return "/".join(reversed(parts))
    except Exception:
        return None


def _nfc(s: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFC", s)


def _ts_from_epoch(ts: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _local_key(name: str, is_dir: bool) -> tuple[str, str | None]:
    n = _nfc(name)
    if not is_dir:
        for ext in (".gdoc", ".gsheet", ".gslides"):
            if n.endswith(ext):
                return n[: -len(ext)], ext
    return n, None


def _server_key(item: dict) -> tuple[str, str | None]:
    n = _nfc(item["name"])
    mime = item.get("mimeType", "")
    if mime in GSUITE_MIMES:
        return n, GSUITE_MIMES[mime]
    return n, None


def _list_local_items(local_path: Path, skip: set[str]) -> dict:
    """List immediate children of local_path with metadata."""
    items = {}
    for entry in local_path.iterdir():
        if _nfc(entry.name) in skip:
            continue
        is_dir = entry.is_dir()
        key_base, ext = _local_key(entry.name, is_dir)
        key = (key_base + ext) if ext else key_base
        try:
            stat = entry.stat()
        except OSError:
            continue
        if is_dir:
            try:
                count = sum(1 for c in entry.iterdir() if _nfc(c.name) not in skip)
            except OSError:
                count = None
        else:
            count = None
        items[key] = {
            "name": key,
            "local_abs_path": str(entry),
            "is_folder": is_dir,
            "is_gsuite_pointer": ext is not None,
            "size": 0 if is_dir else stat.st_size,
            "item_count": count,
            "modified": _ts_from_epoch(stat.st_mtime),
            "created": _ts_from_epoch(getattr(stat, "st_birthtime", stat.st_ctime)),
        }
    return items


def _list_server_items(service, folder_id: str) -> dict:
    """List immediate children of server folder_id with metadata."""
    items = {}
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields=(
                    "nextPageToken, "
                    "files(id,name,mimeType,size,createdTime,modifiedTime)"
                ),
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        for item in resp.get("files", []):
            key_base, ext = _server_key(item)
            key = (key_base + ext) if ext else key_base
            is_folder = item["mimeType"] == FOLDER_MIME
            is_gsuite = ext is not None and not is_folder
            items[key] = {
                "id": item["id"],
                "name": key,
                "mimeType": item["mimeType"],
                "is_folder": is_folder,
                "is_gsuite": is_gsuite,
                "size": int(item.get("size", 0)) if "size" in item else None,
                "item_count": None,
                "modified": item.get("modifiedTime"),
                "created": item.get("createdTime"),
            }
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return items


def _count_server_children(service, folder_id: str) -> int:
    """Count immediate children of a server folder."""
    count = 0
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id)",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        count += len(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return count


class _Resolver:
    """Lazy resolver for set 6 (elsewhere on server) and revision checks.

    API calls are made on demand — the diff's set construction does not
    preemptively walk every local item's xattr or fetch every empty file's
    revision history. Callers that need these checks (dispatch for sets 3/4/5)
    invoke the resolver; results are cached.
    """

    def __init__(self, service, target_folder_id, target_drive_path):
        self.service = service
        self.target_folder_id = target_folder_id
        self.target_drive_path = target_drive_path
        self._set_6: dict[str, dict | None] = {}
        self._revisions: dict[str, bool] = {}

    def set_6_match(self, local_item: dict) -> dict | None:
        """Resolve a local item's xattr Drive ID to a server item.

        Returns None if there's no xattr, the referenced item is trashed,
        the ID doesn't resolve, or the item is already at the target path.
        """
        key = local_item["local_abs_path"]
        if key in self._set_6:
            return self._set_6[key]
        drive_id = _get_drivefs_item_id(key)
        if not drive_id:
            self._set_6[key] = None
            return None
        try:
            info = (
                self.service.files()
                .get(
                    fileId=drive_id,
                    fields=(
                        "id,name,parents,trashed,mimeType,size,createdTime,modifiedTime"
                    ),
                )
                .execute()
            )
        except Exception:
            self._set_6[key] = None
            return None
        if info.get("trashed"):
            self._set_6[key] = None
            return None
        parents = info.get("parents", [])
        if parents and self.target_folder_id and parents[0] == self.target_folder_id:
            self._set_6[key] = None
            return None
        path = _resolve_id_to_path(self.service, drive_id)
        if path is None:
            self._set_6[key] = None
            return None
        result = {
            "id": drive_id,
            "path": path,
            "name": info.get("name"),
            "mimeType": info.get("mimeType"),
            "is_folder": info.get("mimeType") == FOLDER_MIME,
            "size": int(info.get("size", 0)) if "size" in info else None,
            "modified": info.get("modifiedTime"),
            "created": info.get("createdTime"),
        }
        self._set_6[key] = result
        return result

    def has_non_empty_revision(self, file_id: str) -> bool:
        if file_id in self._revisions:
            return self._revisions[file_id]
        try:
            resp = (
                self.service.revisions()
                .list(fileId=file_id, fields="revisions(id,size)")
                .execute()
            )
            has = any(int(r.get("size", 0)) > 0 for r in resp.get("revisions", []))
            self._revisions[file_id] = has
            return has
        except Exception:
            self._revisions[file_id] = False
            return False

    def resolved_elsewhere(self) -> list[dict]:
        return [v for v in self._set_6.values() if v is not None]


def _dispatch_set_3(item: dict, resolver: _Resolver) -> dict:
    """Local-only item → MKDIR+QUEUE (folder) | CP-from-elsewhere | UPLOAD."""
    target_path = f"{resolver.target_drive_path.rstrip('/')}/{item['name']}"
    if item["is_folder"]:
        return {
            "item": item,
            "set": 3,
            "state": "local_only",
            "actions": [
                {
                    "op": "MKDIR+QUEUE",
                    "dest_path": target_path,
                    "local_item_count": item["item_count"],
                    "reason": "local folder not on server; create and descend",
                }
            ],
        }
    elsewhere = resolver.set_6_match(item)
    if elsewhere:
        return {
            "item": item,
            "set": 3,
            "state": "local_only",
            "actions": [
                {
                    "op": "CP",
                    "src": elsewhere,
                    "dest_path": target_path,
                    "reason": (
                        "xattr Drive ID resolves to a server file at a different"
                        " path — CP saves upload bandwidth"
                    ),
                    "followup_on_empty_result": {
                        "if_restorable": "RESTORE_REV",
                        "else": "WARN (source was also empty)",
                    },
                }
            ],
        }
    return {
        "item": item,
        "set": 3,
        "state": "local_only",
        "actions": [
            {
                "op": "UPLOAD",
                "src_local_path": item["local_abs_path"],
                "src_size": item["size"],
                "dest_path": target_path,
                "reason": (
                    "local-only file with no server source (no xattr or xattr"
                    " resolves missing/trashed)"
                ),
                "followup_on_empty_result": {
                    "warn": True,
                    "note": (
                        "uploaded file is empty; local was likely a streaming"
                        " stub without recoverable source"
                    ),
                },
            }
        ],
    }


def _dispatch_set_4(item: dict, resolver: _Resolver) -> dict:
    """Server-only item → WARN (folder) | NONE | RESTORE_REV | WARN."""
    if item["is_folder"]:
        return {
            "item": item,
            "set": 4,
            "state": "server_only",
            "actions": [
                {
                    "op": "WARN",
                    "reason": (
                        "server folder not on local; no automatic action"
                        " (user decides to keep, delete, or pull down)"
                    ),
                    "server_item_count": item["item_count"],
                }
            ],
        }
    size = item["size"]
    if size and size > 0:
        return {
            "item": item,
            "set": 4,
            "state": "server_only",
            "actions": [
                {
                    "op": "NONE",
                    "reason": "server has content; local absent — no action (server may sync down)",
                    "server_size": size,
                }
            ],
        }
    if resolver.has_non_empty_revision(item["id"]):
        return {
            "item": item,
            "set": 4,
            "state": "server_only",
            "actions": [
                {
                    "op": "RESTORE_REV",
                    "target_id": item["id"],
                    "reason": "server file is empty but has a non-empty revision",
                }
            ],
        }
    return {
        "item": item,
        "set": 4,
        "state": "server_only",
        "actions": [
            {
                "op": "WARN",
                "reason": (
                    "server file is empty and has no non-empty revision;"
                    " no recovery path"
                ),
            }
        ],
    }


def _dispatch_set_5(entry: dict, resolver: _Resolver) -> dict:
    """Both-paths item → QUEUE (folder) | NONE | [RESTORE_REV|CP|UPLOAD]+."""
    local = entry["local"]
    server = entry["server"]
    if server["is_folder"]:
        lc = local["item_count"]
        sc = server["item_count"]
        return {
            "item": entry,
            "set": 5,
            "state": "both",
            "actions": [
                {
                    "op": "QUEUE",
                    "local_path": local["local_abs_path"],
                    "server_id": server["id"],
                    "server_path": f"{resolver.target_drive_path.rstrip('/')}/{server['name']}",
                    "local_item_count": lc,
                    "server_item_count": sc,
                    "count_mismatch": (lc is not None and sc is not None and lc != sc),
                    "reason": "folder exists on both sides; descend",
                }
            ],
        }
    server_size = server["size"] or 0
    local_size = local["size"] or 0
    if server_size > 0:
        return {
            "item": entry,
            "set": 5,
            "state": "both",
            "actions": [
                {
                    "op": "NONE",
                    "reason": "server has content; server is truth",
                    "server_size": server_size,
                    "local_size": local_size,
                }
            ],
        }
    # Server empty — gather all valid recovery candidates; the tool does not
    # choose among them.
    candidates = []
    if resolver.has_non_empty_revision(server["id"]):
        candidates.append(
            {
                "op": "RESTORE_REV",
                "target_id": server["id"],
                "reason": (
                    "server file is empty but has a non-empty revision"
                    " (in-place, no bandwidth)"
                ),
            }
        )
    elsewhere = resolver.set_6_match(local)
    if elsewhere:
        candidates.append(
            {
                "op": "CP",
                "src": elsewhere,
                "dest_id": server["id"],
                "dest_path": f"{resolver.target_drive_path.rstrip('/')}/{server['name']}",
                "reason": (
                    "xattr Drive ID resolves to a server file at a different"
                    " path — CP (requires replacing the empty target)"
                ),
                "followup_on_empty_result": {
                    "if_restorable": "RESTORE_REV",
                    "else": "WARN",
                },
            }
        )
    if local_size > 0:
        candidates.append(
            {
                "op": "UPLOAD",
                "src_local_path": local["local_abs_path"],
                "src_size": local_size,
                "dest_id": server["id"],
                "reason": "local has content — upload to replace empty server",
            }
        )
    if not candidates:
        candidates.append(
            {
                "op": "WARN",
                "reason": (
                    "server empty, no non-empty revision, no elsewhere match,"
                    " local also empty — no recovery path"
                ),
                "local_size": local_size,
                "server_size": server_size,
            }
        )
    return {
        "item": entry,
        "set": 5,
        "state": "both",
        "actions": candidates,
    }


def sync_diff(
    local_dir: str,
    drive_path: str,
    skip: list[str] | None = None,
) -> dict:
    """Compare a local directory against a Drive folder, produce set metadata
    and suggested restoration actions.

    Names are normalized to Unicode NFC (macOS stores NFD, Drive uses NFC).
    Google-native pointer extensions (.gdoc, .gsheet, .gslides) are matched
    against server files by MIME type.

    Output shape:
      {
        "source_path": str,
        "target_path": str,
        "sets": {
            "local_only":  [items in set 3],
            "server_only": [items in set 4],
            "both":        [entries in set 5, each {local, server}],
            "elsewhere":   [set 6 resolved items — those local items whose
                            xattr Drive ID points to a server file at a
                            different path, excluding trashed/missing],
        },
        "suggestions": [ {item, set, state, actions:[...]} ],
      }

    Each suggestion's `actions` list is length 1 when the decision tree yields
    a single choice; >1 when rules cannot disambiguate (set 5 + server empty
    may produce up to 3 valid candidates: RESTORE_REV, CP, UPLOAD — tool does
    not choose).
    """
    local_path = Path(local_dir)
    if not local_path.is_dir():
        raise FileNotFoundError(f"Local directory not found: {local_dir}")

    service = authenticate()
    target_folder_id = resolve_path(service, drive_path)

    skip_set = {_nfc(s) for s in (skip or [])}

    local_items = _list_local_items(local_path, skip_set)
    server_items = (
        _list_server_items(service, target_folder_id) if target_folder_id else {}
    )

    # Populate item_count for server folders (one API call per folder).
    for item in server_items.values():
        if item["is_folder"]:
            item["item_count"] = _count_server_children(service, item["id"])

    local_names = set(local_items.keys())
    server_names = set(server_items.keys())

    set_3 = [local_items[n] for n in sorted(local_names - server_names)]
    set_4 = [server_items[n] for n in sorted(server_names - local_names)]
    set_5 = [
        {"local": local_items[n], "server": server_items[n]}
        for n in sorted(local_names & server_names)
    ]

    resolver = _Resolver(service, target_folder_id, drive_path)

    suggestions = []
    for item in set_3:
        suggestions.append(_dispatch_set_3(item, resolver))
    for item in set_4:
        suggestions.append(_dispatch_set_4(item, resolver))
    for entry in set_5:
        suggestions.append(_dispatch_set_5(entry, resolver))

    return {
        "source_path": str(local_path),
        "target_path": drive_path,
        "sets": {
            "local_only": set_3,
            "server_only": set_4,
            "both": set_5,
            "elsewhere": resolver.resolved_elsewhere(),
        },
        "suggestions": suggestions,
    }


def cmd_sync_diff(
    service,
    local_dir: str,
    drive_path: str,
    skip: list[str],
    output_format: str,
    verbose: bool,
):
    diff = sync_diff(local_dir, drive_path, skip=skip)

    if output_format == "json":
        print(json.dumps(diff, indent=2, ensure_ascii=False, default=str))
        return

    _print_human_diff(diff, verbose)


def _fmt_size(item: dict) -> str:
    if item.get("is_folder"):
        ic = item.get("item_count")
        return f"{ic} items" if ic is not None else "folder"
    sz = item.get("size")
    return f"{sz}B" if sz is not None else "file"


def _print_item_header(marker: str, s: dict) -> None:
    if s["set"] == 5:
        local = s["item"]["local"]
        server = s["item"]["server"]
        name = server["name"]
        if server["is_folder"]:
            lc = local["item_count"]
            sc = server["item_count"]
            detail = f"local: {lc} items, server: {sc} items"
            if lc is not None and sc is not None and lc != sc:
                detail += " ⚠ mismatch"
        else:
            detail = (
                f"local: {local.get('size', '?')}B, server: {server.get('size', '?')}B"
            )
        print(f"  {marker} {name}  ({detail})")
    else:
        item = s["item"]
        print(f"  {marker} {item['name']}  ({_fmt_size(item)})")


def _print_action(action: dict) -> None:
    op = action["op"]
    reason = action.get("reason", "")
    extra = []
    if op == "CP":
        src = action.get("src") or {}
        extra.append(f"from: {src.get('path', '?')}")
    elif op in ("UPLOAD",) and "src_size" in action:
        extra.append(f"{action['src_size']}B")
    elif op == "MKDIR+QUEUE" and action.get("local_item_count") is not None:
        extra.append(f"{action['local_item_count']} items")
    elif op == "QUEUE":
        lc, sc = action.get("local_item_count"), action.get("server_item_count")
        extra.append(f"local: {lc}, server: {sc}")
        if action.get("count_mismatch"):
            extra.append("⚠ count mismatch")
    elif op == "WARN" and action.get("server_item_count") is not None:
        extra.append(f"{action['server_item_count']} items on server")
    suffix = f" [{', '.join(extra)}]" if extra else ""
    print(f"      → {op}{suffix}: {reason}")
    followup = action.get("followup_on_empty_result")
    if followup:
        if "if_restorable" in followup:
            print(
                f"        ↳ if result empty: {followup['if_restorable']};"
                f" else {followup.get('else', 'WARN')}"
            )
        elif followup.get("warn"):
            note = followup.get("note", "")
            print(f"        ↳ if result empty: WARN ({note})")


def _print_human_diff(diff: dict, verbose: bool) -> None:
    suggestions = diff["suggestions"]
    by_set = {3: [], 4: [], 5: []}
    for s in suggestions:
        by_set[s["set"]].append(s)

    print(f"=== sync-diff: {diff['source_path']} ↔ {diff['target_path']} ===\n")

    for set_num, marker, title in [
        (3, "+", "Set 3: Local only"),
        (4, "-", "Set 4: Server only"),
        (5, "=", "Set 5: Both"),
    ]:
        bucket = by_set[set_num]
        print(f"--- {title} ({len(bucket)}) ---")
        for s in bucket:
            if not verbose and all(a["op"] == "NONE" for a in s["actions"]):
                continue
            _print_item_header(marker, s)
            for a in s["actions"]:
                _print_action(a)
        print()

    elsewhere = diff["sets"]["elsewhere"]
    print(f"--- Set 6: Elsewhere on server ({len(elsewhere)}) ---")
    for e in sorted(elsewhere, key=lambda x: x.get("path", "")):
        print(f"  → {e['path']}  (id: {e['id']})")
    if not elsewhere:
        print("  (none)")
    print()

    actionable = sum(
        1 for s in suggestions if any(a["op"] not in ("NONE",) for a in s["actions"])
    )
    ambiguous = sum(1 for s in suggestions if len(s["actions"]) > 1)
    print("--- Summary ---")
    print(f"  Set 3 (local only):   {len(by_set[3])}")
    print(f"  Set 4 (server only):  {len(by_set[4])}")
    print(f"  Set 5 (both):         {len(by_set[5])}")
    print(f"  Set 6 (elsewhere):    {len(elsewhere)}")
    print(f"  Items with actions:   {actionable}")
    print(f"  Items with multiple candidates (ambiguous): {ambiguous}")


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Google Drive operations for CFS (server-side)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("auth", help="Test authentication")

    ls = subparsers.add_parser("ls", help="List folder contents")
    ls.add_argument("target", help="Drive path or id:<ID>")

    mkdir = subparsers.add_parser(
        "mkdir", help="Create folder(s), idempotent, creates parents"
    )
    mkdir.add_argument("path", help="Drive folder path")

    cp = subparsers.add_parser("cp", help="Copy file or folder")
    cp.add_argument("source", help="Drive path or id:<ID>")
    cp.add_argument(
        "dest",
        help="Drive path. Trailing '/' = into folder; otherwise rename-on-copy",
    )
    cp.add_argument(
        "-r", "--recursive", action="store_true", help="Required for folders"
    )
    cp.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing files"
    )

    mv = subparsers.add_parser("mv", help="Move file or folder (rename if parent same)")
    mv.add_argument("source", help="Drive path or id:<ID>")
    mv.add_argument(
        "dest", help="Drive path. Trailing '/' = into folder; otherwise rename-on-move"
    )
    mv.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing files"
    )

    rm = subparsers.add_parser("rm", help="Delete file or folder")
    rm.add_argument("target", nargs="?", help="Drive path or id:<ID>")
    rm.add_argument(
        "-r", "--recursive", action="store_true", help="Required for folders"
    )
    rm.add_argument(
        "--stdin", action="store_true", help="Read IDs from stdin, one per line"
    )

    find = subparsers.add_parser("find", help="Recursive search")
    find.add_argument("root", help="Drive path or id:<ID> (must be a folder)")
    find.add_argument("--name", help="Exact name to match")
    find.add_argument("--type", choices=["file", "folder"], help="Filter by type")
    find.add_argument("--mime", help="Filter by MIME type")
    find.add_argument(
        "--max-depth", type=int, help="Maximum recursion depth (0 = direct children)"
    )
    find.add_argument(
        "--modified-since",
        help="Include only items with modifiedTime > T (ISO 8601 or Nd/Nh/Nm)",
    )
    find.add_argument(
        "--created-since",
        help="Include only items with createdTime > T (ISO 8601 or Nd/Nh/Nm)",
    )
    find.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Folder names to prune from descent (e.g. .git .venv __pycache__ node_modules)",
    )
    find.add_argument(
        "--format",
        choices=["ids", "paths", "json"],
        default="ids",
        help="Output format (default: ids for piping)",
    )

    upload = subparsers.add_parser("upload", help="Upload local file to Drive")
    upload.add_argument("local", help="Local file path")
    upload.add_argument(
        "dest",
        help="Drive path. Trailing '/' = into folder; otherwise rename-on-upload",
    )
    upload.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing files"
    )

    download = subparsers.add_parser(
        "download", help="Download file content (stdout by default)"
    )
    download.add_argument("target", help="Drive path or id:<ID>")
    download.add_argument(
        "-o", "--output", help="Write to this local file instead of stdout"
    )
    download.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing output file"
    )

    restore = subparsers.add_parser(
        "restore-rev", help="Restore file to latest non-empty revision"
    )
    restore.add_argument("target", nargs="?", help="Drive path or id:<ID>")
    restore.add_argument(
        "-f", "--force", action="store_true", help="Required (overwrites)"
    )
    restore.add_argument(
        "--stdin", action="store_true", help="Read IDs from stdin, one per line"
    )

    export = subparsers.add_parser(
        "export", help="Export Google-native file content (stdout by default)"
    )
    export.add_argument("target", help="Drive path or id:<ID>")
    export.add_argument(
        "--format",
        help="Export format (md, docx, pdf, txt, xlsx, csv, pptx)",
    )
    export.add_argument(
        "-o", "--output", help="Write to this local file instead of stdout"
    )
    export.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing output file"
    )

    sd = subparsers.add_parser(
        "sync-diff",
        help="Compare local directory to Drive; surface sets + suggested actions",
    )
    sd.add_argument("local_dir", help="Local directory path")
    sd.add_argument("drive_path", help="Drive folder path")
    sd.add_argument(
        "--skip",
        nargs="*",
        default=[".DS_Store"],
        help="Names to skip from the local listing (default: .DS_Store)",
    )
    sd.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)",
    )
    sd.add_argument(
        "--verbose",
        action="store_true",
        help="Show items with no action (set 5 server-has-truth) too",
    )

    args = parser.parse_args()

    try:
        service = authenticate() if args.command != "auth" else None

        if args.command == "auth":
            service = authenticate()
            about = service.about().get(fields="user").execute()
            print(f"Authenticated as: {about['user']['emailAddress']}")

        elif args.command == "ls":
            cmd_ls(service, args.target)

        elif args.command == "mkdir":
            cmd_mkdir(service, args.path)

        elif args.command == "cp":
            cmd_cp(service, args.source, args.dest, args.recursive, args.force)

        elif args.command == "mv":
            cmd_mv(service, args.source, args.dest, args.force)

        elif args.command == "rm":
            cmd_rm(service, args.target, args.recursive, args.stdin)

        elif args.command == "find":
            cmd_find(
                service,
                args.root,
                args.name,
                args.type,
                args.mime,
                args.max_depth,
                args.format,
                args.modified_since,
                args.created_since,
                args.skip,
            )

        elif args.command == "upload":
            cmd_upload(service, args.local, args.dest, args.force)

        elif args.command == "download":
            cmd_download(service, args.target, args.output, args.force)

        elif args.command == "restore-rev":
            cmd_restore_rev(service, args.target, args.force, args.stdin)

        elif args.command == "export":
            cmd_export(service, args.target, args.format, args.output, args.force)

        elif args.command == "sync-diff":
            cmd_sync_diff(
                service,
                args.local_dir,
                args.drive_path,
                args.skip,
                args.format,
                args.verbose,
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
