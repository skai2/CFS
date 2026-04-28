#!/usr/bin/env bash
# CFS — ocr tool setup
# Creates a Python venv at ~/.cfs/tools/ocr/.venv and installs Surya OCR
# for extracting text from images when visual reading is unreliable.
#
# Prerequisites:
#   - Python 3.12+
#   - ~5 GB disk for torch + Surya model weights
#
# Usage:
#   bash tools/ocr/setup.sh

set -euo pipefail

TOOL_NAME="ocr"
VENV_DIR="$HOME/.cfs/tools/$TOOL_NAME/.venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "CFS — $TOOL_NAME setup"
echo "================="

PYTHON=""
for candidate in python3.12 python3.13 python3.14 python3; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(sys.version_info.minor)")
        if [ "$version" -ge 12 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.12+ not found." >&2
    exit 1
fi

if [ -d "$VENV_DIR" ]; then
    echo "Venv exists at $VENV_DIR — reinstalling packages"
else
    echo "Creating venv at $VENV_DIR"
    mkdir -p "$(dirname "$VENV_DIR")"
    "$PYTHON" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$REQ_FILE"

TORCH_DEVICE=cpu "$VENV_DIR/bin/python" -c "from surya.detection import DetectionPredictor; print('  surya-ocr: OK')"

echo ""
echo "Ready: $VENV_DIR/bin/python $SCRIPT_DIR/ocr.py <image>"
