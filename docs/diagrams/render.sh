#!/usr/bin/env bash
# Render all .mmd source files in this directory to .png via mermaid-cli.
# Generates two variants per source: <name>.png (light theme) and
# <name>-dark.png (dark theme), both with transparent backgrounds. README
# uses <picture> to swap based on prefers-color-scheme.
# PNG is used (rather than SVG) for broader renderability across GitHub
# web, mobile app, and other markdown viewers; --scale 2 produces a crisp
# 2x render that still scales down cleanly via container max-width.
# Requires Node + npx. If you hit npm cache permission issues, prefix with
# `npm_config_cache=/tmp/npm-cfs-cache` to use an isolated cache.

set -euo pipefail
cd "$(dirname "$0")"

for src in *.mmd; do
    base="${src%.mmd}"
    light="${base}.png"
    dark="${base}-dark.png"

    echo "Rendering $src -> $light (light)"
    npx --yes -p @mermaid-js/mermaid-cli@latest mmdc -i "$src" -o "$light" -b transparent --scale 2

    echo "Rendering $src -> $dark (dark)"
    npx --yes -p @mermaid-js/mermaid-cli@latest mmdc -i "$src" -o "$dark" -t dark -b transparent --scale 2
done

echo "Done. PNGs in $(pwd)"
