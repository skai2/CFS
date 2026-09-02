# Tools

Optional CFS-bundled reference implementations for capabilities CFS may need (backend operations, content extraction). Each tool is independent — install only what your environment requires.

CFS itself is markdown-only. Flows describe *what* needs to happen; the agent picks *how*. Use these tools only when your environment lacks an equivalent capability — agent-native support, an MCP server, or an installed CLI. See `refs/admin/safety.md` § Backend dispatch for the framing.

## Catalog

| Tool | Purpose | When to use |
|---|---|---|
| [`gdrive/`](gdrive/README.md) | Google Drive operations via the Drive API (POSIX-style CLI) | Configured `gdrive` backend with no native, MCP, or CLI alternative |
| [`gworks/`](gworks/README.md) | Gmail and Google Calendar operations, one identity per call (JSON CLI) | A Google identity with no native, MCP, or connector capability |
| [`markitdown/`](markitdown/README.md) | Extract text from complex binary formats (Excel, PowerPoint, Word, etc.) | Agent can't read a format directly |
| [`ocr/`](ocr/README.md) | OCR for images using Surya | Agent's visual reading is unreliable (tall images, small text, 16-bit color) |

Each tool has its own `README.md`, `requirements.txt`, and `setup.sh`. Install only the ones you need:

```bash
bash tools/<tool>/setup.sh
```

Setup creates an isolated venv at `~/.cfs/tools/<tool>/.venv` (outside cloud-synced storage, to avoid sync issues with compiled binaries).

## Prerequisites

- Python 3.12+ (verified by each tool's setup script)
- For `gdrive`: Google Drive API OAuth credentials at `~/.cfs/credentials_gdrive.json` (see `gdrive/README.md`)
- For `gworks`: OAuth Desktop App credentials per identity at `~/.cfs/google/<account>/credentials.json` (see `gworks/README.md`)
