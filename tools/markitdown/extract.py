"""
Extract readable text content from any file using markitdown.
Supports: PDF, DOCX, PPTX, XLSX, images, HTML, and more.

Usage:
    python extract.py <file_path>

Outputs the extracted markdown text to stdout.
Requires: markitdown (install via tools/markitdown/setup.sh)

Note: this script is named extract.py rather than markitdown.py because
a script named markitdown.py inside the markitdown/ directory would
shadow the markitdown PyPI package on import.
"""

import sys
from pathlib import Path
from markitdown import MarkItDown


def extract(file_path: str) -> str:
    """Extract text content from a file, return as markdown string."""
    md = MarkItDown()
    result = md.convert(file_path)
    return result.text_content


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract.py <file_path>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)

    text = extract(path)
    print(text)


if __name__ == "__main__":
    main()
