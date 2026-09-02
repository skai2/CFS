# gdrive

Optional CFS-bundled reference implementation for Google Drive operations. A POSIX-inspired CLI over the Drive API — every command runs entirely server-side, bypassing local sync.

Use when your environment has no native Drive support, no MCP, and no installed CLI for Google Drive.

Scope is Drive only. Gmail and Calendar live in [`gworks`](../gworks/README.md); this one stays focused on the POSIX-style Drive semantics and `sync-diff` recovery that the `gdrive:` backend relies on.

## When to use

- **Cloud storage operations** — any mutation on Google Drive. Server-side by default; changes stream down rather than syncing up.
- **Google-native files** (`.gdoc`, `.gsheet`, `.gslides`) — `export` to read content, `cp`/`mv` to relocate.
- **Sync recovery** — when local and server states diverge (0-byte files from failed sync, stuck upload queues), use `sync-diff` to identify drift, `restore-rev` to recover from revision history, and `upload -f` to push local content over a corrupted Drive file.

`upload` and `sync-diff` are the only commands that read from the local filesystem; `download` and `export` write to it when given `-o`.

## Setup

```bash
bash tools/gdrive/setup.sh
```

Creates a venv at `~/.cfs/tools/gdrive/.venv` and installs the Google API client libraries.

### Prerequisites

- Python 3.12+
- Google Drive API credentials at `~/.cfs/credentials_gdrive.json`

### Google Drive credentials (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project, enable Google Drive API
3. Create OAuth 2.0 Desktop App credentials
4. Download JSON → save as `~/.cfs/credentials_gdrive.json`
5. Run auth: `~/.cfs/tools/gdrive/.venv/bin/python tools/gdrive/gdrive.py auth`

## Target syntax

Any command that takes a Drive target accepts either a path or an explicit Drive ID:

| Form | Meaning |
|---|---|
| `System/Archive/Entity` | Path — resolves via API walk. Ambiguous as file vs. folder until resolved. |
| `System/Archive/Entity/` | Path with trailing `/` — must resolve to a folder. POSIX-style folder intent. |
| `id:1abcXYZ...` | Explicit Drive ID. Type discovered via API. Stable across renames/moves. |

Drive IDs are preferred when available — they survive renames and moves, unlike paths.

The `gdrive:` scheme prefix used in `config.yaml` addresses is a **config-level** backend selector — it tells the agent to invoke this tool. The CLI itself takes the path portion only; do not pass `gdrive:...` to the CLI.

## Destination semantics (`cp`, `mv`, `upload`)

The destination argument follows POSIX `cp`/`mv`:

- `dest/` (trailing slash) — copy/move *into* the folder, keeping the source name
- `dest` (no trailing slash) — copy/move *as* that name (rename on the fly)

## Safety flags

Destructive operations require explicit flags:

- `-r` / `--recursive` — required for any operation on a folder (`cp`, `rm`)
- `-f` / `--force` — required to overwrite an existing target (`cp`, `mv`, `upload`, `restore-rev`, and on the local side: `download`, `export` when given `-o`)

## Commands

```bash
PYTHON=~/.cfs/tools/gdrive/.venv/bin/python
SCRIPT=tools/gdrive/gdrive.py

# Auth test
$PYTHON $SCRIPT auth

# List folder contents
$PYTHON $SCRIPT ls "System/Archive/Entity"
$PYTHON $SCRIPT ls id:1abcXYZ

# Create folder (idempotent, creates parents)
$PYTHON $SCRIPT mkdir "System/Archive/Entity/Domain"

# Copy — file into folder (keep name)
$PYTHON $SCRIPT cp "Source/file.pdf" "Dest/Folder/"

# Copy — file with rename
$PYTHON $SCRIPT cp "Source/file.pdf" "Dest/Folder/renamed.pdf"

# Copy — folder tree (requires -r)
$PYTHON $SCRIPT cp -r "Source/Folder" "Dest/Parent/"

# Copy — overwrite existing destination
$PYTHON $SCRIPT cp -f "Source/file.pdf" "Dest/existing.pdf"

# Move / rename
$PYTHON $SCRIPT mv "Source/Path" "Dest/Parent/"
$PYTHON $SCRIPT mv "Source/Old Name" "Source/New Name"
$PYTHON $SCRIPT mv id:1abcXYZ "Dest/Parent/"

# Delete file
$PYTHON $SCRIPT rm "Path/To/File"

# Delete folder (requires -r)
$PYTHON $SCRIPT rm -r "Path/To/Folder"

# Find — recursive search (default output: IDs for piping)
$PYTHON $SCRIPT find "System/Projects" --name ".git" --type folder
$PYTHON $SCRIPT find "System" --mime application/vnd.google-apps.spreadsheet
$PYTHON $SCRIPT find "System" --name "venv" --max-depth 3

# Find — human-readable paths
$PYTHON $SCRIPT find "System/Projects" --name ".venv" --format paths

# Find — items modified or created recently
# Accepts ISO 8601 (2026-04-23T10:30:00Z) or relative (Nd / Nh / Nm)
$PYTHON $SCRIPT find "System/Archive" --modified-since 7d --format json
$PYTHON $SCRIPT find "System/Unsorted" --created-since 24h --format paths
$PYTHON $SCRIPT find "System" --modified-since 2026-04-23T10:30:00Z --type file

# Find + rm composition
$PYTHON $SCRIPT find "System/Projects" --name ".git" --type folder \
  | $PYTHON $SCRIPT rm -r --stdin

# Upload local file (new file on Drive)
$PYTHON $SCRIPT upload ./local.pdf "Dest/Folder/"
$PYTHON $SCRIPT upload ./local.pdf "Dest/Folder/renamed.pdf"

# Upload — overwrite existing Drive file's content (fixes 0-byte files)
$PYTHON $SCRIPT upload -f ./local.pdf "Dest/Folder/file.pdf"
$PYTHON $SCRIPT upload -f ./local.pdf id:1abcXYZ

# Download file bytes — stdout by default
$PYTHON $SCRIPT download "System/Archive/Entity/doc.pdf" | less
$PYTHON $SCRIPT download id:1abcXYZ > ./doc.pdf

# Download — write to a local file (-f to overwrite)
$PYTHON $SCRIPT download "System/Archive/Entity/doc.pdf" -o ./doc.pdf
$PYTHON $SCRIPT download "System/Archive/Entity/doc.pdf" -o ./doc.pdf -f

# Restore file to latest non-empty revision
$PYTHON $SCRIPT restore-rev -f id:1abcXYZ

# Restore — batch from stdin
echo "id1
id2
id3" | $PYTHON $SCRIPT restore-rev -f --stdin

# Export Google-native file content (stdout by default, markdown default format)
$PYTHON $SCRIPT export "System/Archive/Entity/Doc"
$PYTHON $SCRIPT export "System/Archive/Entity/Sheet" --format csv

# Export — write to a local file (-f to overwrite)
$PYTHON $SCRIPT export id:1abcXYZ --format pdf -o ./out.pdf
$PYTHON $SCRIPT export "System/Archive/Entity/Sheet" --format csv -o ./sheet.csv -f

# Compare local directory to Drive folder — sets + suggested actions
$PYTHON $SCRIPT sync-diff ./local "Drive/Path"

# Skip specific local names (default: .DS_Store)
$PYTHON $SCRIPT sync-diff ./local "Drive/Path" --skip .DS_Store Thumbs.db

# Structured output for agent consumption
$PYTHON $SCRIPT sync-diff ./local "Drive/Path" --format json

# Verbose — show items with no action (set 5 where server has content)
$PYTHON $SCRIPT sync-diff ./local "Drive/Path" --verbose
```

## `sync-diff` sets and dispatch

Sync-diff builds six sets from the immediate children of the source and target, then dispatches a suggested action per item. It does not execute — suggestions are for the caller (user or agent) to review and apply.

### Sets

| Set | Meaning |
|---|---|
| 1 | Local items at source path |
| 2 | Server items at target path |
| 3 | `local_only` = 1 \\ 2 |
| 4 | `server_only` = 2 \\ 1 |
| 5 | `both` = 1 ∩ 2 |
| 6 | `elsewhere` — items in set 1 whose xattr Drive ID resolves to a server file at a different path (computed lazily, on demand) |

Every item in every set carries metadata: `name`, `id` (where available), `size` (file bytes) or `item_count` (folder children), `created`, `modified`.

### Dispatch (suggested actions per item)

| Set | Kind | Condition | Suggested |
|---|---|---|---|
| 3 | folder | — | `MKDIR+QUEUE` (include local item count) |
| 3 | file | xattr resolves elsewhere (set 6) | `CP` from source; followup: if empty, try `RESTORE_REV` or WARN |
| 3 | file | no elsewhere match | `UPLOAD`; followup: if result empty, WARN |
| 4 | folder | — | `WARN` (server-only folder; no auto action) |
| 4 | file | size > 0 | `NONE` (server has content) |
| 4 | file | size = 0, has non-empty revision | `RESTORE_REV` |
| 4 | file | size = 0, no revision | `WARN` |
| 5 | folder | — | `QUEUE` with local+server item counts (mismatch flagged) |
| 5 | file | server size > 0 | `NONE` (server is truth) |
| 5 | file | server empty | every applicable recovery candidate is surfaced (multiple): `RESTORE_REV` (if revision), `CP` (if set 6), `UPLOAD` (if local has content). Tool does not choose; caller picks. |

**Ambiguity model.** When the rules yield a single action the tool returns one; when multiple recovery paths are valid (set 5 + server empty is the main case), all are surfaced with metadata. The caller decides.
