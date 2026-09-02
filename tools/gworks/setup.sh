#!/usr/bin/env bash
# CFS — gworks tool setup
# Creates a Python venv at ~/.cfs/tools/gworks/.venv (outside cloud-synced
# storage) and installs the Gmail and Calendar API dependencies.
#
# Prerequisites:
#   - Python 3.12+
#   - OAuth Desktop App credentials per identity at
#     ~/.cfs/google/<account>/credentials.json
#     (from Google Cloud Console → APIs & Services → Credentials)
#
# Usage:
#   bash tools/gworks/setup.sh
#
# After setup, authenticate each identity once:
#   ~/.cfs/tools/gworks/.venv/bin/python tools/gworks/gworks.py -a <account> auth

set -euo pipefail

TOOL_NAME="gworks"
VENV_DIR="$HOME/.cfs/tools/$TOOL_NAME/.venv"
ACCOUNTS_DIR="$HOME/.cfs/google"
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

mkdir -p "$ACCOUNTS_DIR"
chmod 700 "$ACCOUNTS_DIR"
found=0
for dir in "$ACCOUNTS_DIR"/*/; do
    [ -d "$dir" ] || continue
    account="$(basename "$dir")"
    if [ -f "$dir/credentials.json" ]; then
        found=1
        chmod 600 "$dir/credentials.json"
        if [ -f "$dir/token.json" ]; then
            chmod 600 "$dir/token.json"
            echo "Account $account: credentials + token"
        else
            echo "Account $account: credentials only — run:"
            echo "  $VENV_DIR/bin/python $SCRIPT_DIR/gworks.py -a $account auth"
        fi
    fi
done
if [ "$found" -eq 0 ]; then
    echo "No identities: place OAuth Desktop App credentials at"
    echo "  $ACCOUNTS_DIR/<account>/credentials.json"
fi

echo ""
echo "Ready: $VENV_DIR/bin/python $SCRIPT_DIR/gworks.py -a <account> <command>"
