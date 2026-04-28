# markitdown

Optional CFS-bundled reference implementation for extracting readable text from complex binary formats (Excel, PowerPoint, Word, etc.).

Use only if your environment lacks an equivalent capability — most agents read PDFs, images, and plain text natively without needing a tool.

## When to use

- Office formats the agent can't read directly: `.xlsx`, `.pptx`, `.docx`
- Other binary formats markitdown supports (HTML, ZIP, EPUB, etc.)

## Setup

```bash
bash tools/markitdown/setup.sh
```

Creates a venv at `~/.cfs/tools/markitdown/.venv` and installs `markitdown[all]`.

Prerequisites: Python 3.12+.

## Usage

```bash
~/.cfs/tools/markitdown/.venv/bin/python tools/markitdown/extract.py <file_path>
```

Outputs the extracted markdown text to stdout.

The script is named `extract.py` rather than `markitdown.py` to avoid shadowing the `markitdown` PyPI package on import.
