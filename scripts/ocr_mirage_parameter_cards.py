#!/usr/bin/env python3
"""
OCR **Mirage-docs/mirage-parameter-cards.png** (same layout as the PDF card).

Requires ``uv sync --extra dev`` and a **Tesseract** install (PATH or default Windows path).

Writes **Mirage-docs/mirage-parameter-cards.ocr.txt** with raw Tesseract output (useful
for grep / manual cleanup). OCR quality varies with resolution and fonts; verify against
the image.

Usage:
  python scripts/ocr_mirage_parameter_cards.py
  python scripts/ocr_mirage_parameter_cards.py --psm 6
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def _configure_tesseract() -> None:
    import pytesseract

    if shutil.which("tesseract"):
        return
    # Common Windows install path (winget: UB-Mannheim.TesseractOCR)
    win = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe"
    if win.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(win)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    default_png = root / "Mirage-docs" / "mirage-parameter-cards.png"
    default_out = root / "Mirage-docs" / "mirage-parameter-cards.ocr.txt"

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", nargs="?", type=Path, default=default_png, help="PNG path")
    ap.add_argument("-o", "--output", type=Path, default=default_out, help="Output .txt")
    ap.add_argument(
        "--psm",
        type=int,
        default=4,
        help="Tesseract page segmentation mode (4=single column, 6=uniform block, 11=sparse)",
    )
    ap.add_argument("--lang", default="eng", help="Tesseract language(s), e.g. eng")
    args = ap.parse_args()

    if not args.image.is_file():
        raise SystemExit(f"Image not found: {args.image}")

    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise SystemExit(
            "Missing dependency. Run: uv sync --extra dev\n" f"({e})"
        ) from e

    _configure_tesseract()

    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        raise SystemExit(
            "Tesseract is not installed or not on PATH.\n"
            "Windows: winget install UB-Mannheim.TesseractOCR\n"
            "Then reopen the terminal or add Tesseract-OCR to PATH."
        ) from None

    img = Image.open(args.image)
    config = f"--psm {int(args.psm)}"
    text = pytesseract.image_to_string(img, lang=args.lang, config=config)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    header = f"# OCR: {args.image.name}  psm={args.psm}  lang={args.lang}\n\n"
    args.output.write_text(header + text, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
