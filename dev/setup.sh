#!/usr/bin/env bash
# CFS — dev environment setup
# For contributors working on the CFS project itself. Installs the pre-commit
# hooks defined in .pre-commit-config.yaml (secrets detection, PII scan,
# Python lint/format, commit message convention).
#
# Prerequisites:
#   - pre-commit installed and on PATH
#       pip3 install pre-commit   # or:  brew install pre-commit
#
# Usage:
#   bash dev/setup.sh

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

PRE_COMMIT=""
if command -v pre-commit &>/dev/null; then
    PRE_COMMIT="pre-commit"
elif python3 -m pre_commit --version &>/dev/null 2>&1; then
    PRE_COMMIT="python3 -m pre_commit"
else
    echo "ERROR: pre-commit not found. Install with:" >&2
    echo "  pip3 install pre-commit   # or  brew install pre-commit" >&2
    exit 1
fi

$PRE_COMMIT install
$PRE_COMMIT install --hook-type commit-msg

echo ""
echo "pre-commit hooks installed."
