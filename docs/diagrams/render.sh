#!/usr/bin/env bash
# Render all .mmd source files in this directory to .svg via mermaid-cli.
# Generates two variants per source: <name>.svg (light theme) and
# <name>-dark.svg (dark theme), both with transparent backgrounds. README
# uses <picture> to swap based on prefers-color-scheme.
# Requires Node + npx. If you hit npm cache permission issues, prefix with
# `npm_config_cache=/tmp/npm-cfs-cache` to use an isolated cache.

set -euo pipefail
cd "$(dirname "$0")"

for src in *.mmd; do
    base="${src%.mmd}"
    light="${base}.svg"
    dark="${base}-dark.svg"

    echo "Rendering $src -> $light (light)"
    npx --yes -p @mermaid-js/mermaid-cli@latest mmdc -i "$src" -o "$light" -b transparent

    echo "Rendering $src -> $dark (dark)"
    npx --yes -p @mermaid-js/mermaid-cli@latest mmdc -i "$src" -o "$dark" -t dark -b transparent
done

echo "Done. SVGs in $(pwd)"
