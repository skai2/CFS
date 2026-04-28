"""
Extract text from images using Surya OCR.
Use when the agent's visual reading is unreliable — tall images,
small text, high-resolution scans, or 16-bit color depth.

Usage:
    python ocr.py <image_path>

Outputs extracted text lines to stdout.
Requires: surya-ocr (install via tools/ocr/setup.sh)
"""

import sys
from pathlib import Path

# Suppress torch warnings
import os
import torch

# Use Apple GPU (MPS) if available, fall back to CPU
if not os.environ.get("TORCH_DEVICE"):
    if torch.backends.mps.is_available():
        os.environ["TORCH_DEVICE"] = "mps"
    else:
        os.environ["TORCH_DEVICE"] = "cpu"

from PIL import Image
from surya.detection import DetectionPredictor
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor


def extract(file_path: str) -> str:
    """Extract text from an image file using Surya OCR."""
    foundation = FoundationPredictor()
    det = DetectionPredictor()
    rec = RecognitionPredictor(foundation)

    img = Image.open(file_path)
    predictions = rec([img], det_predictor=det)

    lines = []
    for page in predictions:
        for line in page.text_lines:
            lines.append(line.text)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image_path>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)

    text = extract(path)
    print(text)


if __name__ == "__main__":
    main()
