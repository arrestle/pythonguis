#!/usr/bin/env python3
"""
Extract human-readable text from Mirage-docs/mirage-parameter-cards.pdf.

The card PDF uses custom-encoded fonts: pypdf returns many ``/gidNNNNN`` tokens
and almost no parameter names or hex command bytes. This script keeps lines that
look like English labels/paragraphs so you can cross-check section titles while
transcribing ``mirage_parm/parameters.py`` from the visual card or ASG.

Requires: ``uv sync --extra dev`` (pypdf).

Usage:
  python scripts/extract_mirage_parameter_pdf.py
  python scripts/extract_mirage_parameter_pdf.py -o out.txt
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from pypdf import PdfReader

# Line has enough Latin letters to be a label or sentence
_READABLE = re.compile(r"[A-Za-z]{3,}")


def clean_page_text(raw: str) -> str:
    lines_out: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        # Custom font encodings come through as /gidNNNNN tokens; drop those lines entirely.
        if "/gid" in s:
            continue
        if not _READABLE.search(s):
            continue
        lines_out.append(s)
    # Collapse duplicate consecutive lines (PDF often repeats blocks)
    deduped: list[str] = []
    for ln in lines_out:
        if deduped and deduped[-1] == ln:
            continue
        deduped.append(ln)
    return "\n".join(deduped) + ("\n" if deduped else "")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    default_pdf = root / "Mirage-docs" / "mirage-parameter-cards.pdf"
    default_out = root / "Mirage-docs" / "mirage-parameter-cards.extracted.txt"

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        default=default_pdf,
        help=f"Input PDF (default: {default_pdf})",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=default_out,
        help=f"Output text file (default: {default_out})",
    )
    args = ap.parse_args()
    pdf_path: Path = args.pdf
    out_path: Path = args.output

    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    parts.append(f"# Extracted from: {pdf_path.name}\n")
    parts.append(f"# Pages: {len(reader.pages)}\n\n")

    for i, page in enumerate(reader.pages):
        raw = page.extract_text() or ""
        parts.append(f"## Page {i + 1}\n\n")
        parts.append(clean_page_text(raw))
        parts.append("\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
