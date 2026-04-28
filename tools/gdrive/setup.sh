#!/usr/bin/env bash
# CFS — gdrive tool setup
# Creates a Python venv at ~/.cfs/tools/gdrive/.venv (outside cloud-synced
# storage) and installs Google Drive API dependencies.
#
# Prerequisites:
#   - Python 3.12+
#   - Google Drive API OAuth credentials at ~/.cfs/credentials_gdrive.json
#     (from Google Cloud Console → APIs & Services → Credentials)
#
# Usage:
#   bash tools/gdrive/setup.sh
#
# After setup, authenticate once:
#   ~/.cfs/tools/gdrive/.venv/bin/python tools/gdrive/gdrive.py auth

set -euo pipefail

TOOL_NAME="gdrive"
VENV_DIR="$HOME/.cfs/tools/$TOOL_NAME/.venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "CFS — $TOOL_NAME setup"
echo "===================="

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

"$VENV_DIR/bin/python" -c "from googleapiclient.discovery import build; print('  google-api: OK')"

if [ -f "$HOME/.cfs/credentials_gdrive.json" ]; then
    chmod 600 "$HOME/.cfs/credentials_gdrive.json"
    echo "Credentials: found at ~/.cfs/credentials_gdrive.json"
    if [ -f "$HOME/.cfs/token.json" ]; then
        chmod 600 "$HOME/.cfs/token.json" 2>/dev/null || true
        echo "Token: found (authenticated)"
    else
        echo "Token: not yet created — run:"
        echo "  $VENV_DIR/bin/python $SCRIPT_DIR/gdrive.py auth"
    fi
else
    echo "Credentials: NOT FOUND at ~/.cfs/credentials_gdrive.json"
    echo "  Download OAuth Desktop App credentials from Google Cloud Console"
    echo "  and save as ~/.cfs/credentials_gdrive.json"
fi

echo ""
echo "Ready: $VENV_DIR/bin/python $SCRIPT_DIR/gdrive.py <command>"
