# ocr

Optional CFS-bundled reference implementation for extracting text from images using [Surya OCR](https://github.com/datalab-to/surya).

Use when the agent's visual reading is unreliable — tall screenshots, small text, high-resolution scans, or 16-bit color depth. Surya processes the full-resolution image locally without downscaling.

## When to use

- Images where the agent's native reading produces uncertain or incomplete text
- Tall or 16-bit images that the agent silently downsamples
- Scanned documents where text extraction needs to be deterministic

If the agent can read the image reliably, this tool is unnecessary.

## Setup

```bash
bash tools/ocr/setup.sh
```

Creates a venv at `~/.cfs/tools/ocr/.venv` and installs `surya-ocr`, `torch`, and `pillow`.

Prerequisites: Python 3.12+, ~5 GB disk for torch and Surya model weights.

On Apple silicon, Surya auto-detects MPS (Metal) for faster inference; otherwise CPU.

## Usage

```bash
~/.cfs/tools/ocr/.venv/bin/python tools/ocr/ocr.py <image_path>
```

Outputs extracted text lines to stdout.
