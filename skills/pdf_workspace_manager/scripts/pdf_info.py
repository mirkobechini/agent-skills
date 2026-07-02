#!/usr/bin/env python3
"""
pdf_info.py — Extract detailed information from a PDF file.

Uses PyMuPDF (fitz) to read: page count, page dimensions, metadata, and
optionally the full text content page by page.

Usage:
    python pdf_info.py "input.pdf"
    python pdf_info.py "input.pdf" --text
    python pdf_info.py "input.pdf" --json
"""

import argparse
import json
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def get_pdf_info(pdf_path: str, extract_text: bool = False) -> dict:
    """Extract info from a PDF and return a dictionary."""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata or {}
    info = {
        "filename": pdf_path,
        "page_count": doc.page_count,
        "pages": [],
        "metadata": {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "format": metadata.get("format", ""),
        },
        "file_size_bytes": _get_file_size(pdf_path),
    }

    for i in range(doc.page_count):
        page = doc[i]
        rect = page.rect
        page_info = {
            "page_number": i + 1,
            "width_pts": round(rect.width, 2),
            "height_pts": round(rect.height, 2),
            "width_inches": round(rect.width / 72, 2),
            "height_inches": round(rect.height / 72, 2),
        }
        if extract_text:
            page_info["text"] = page.get_text("text").strip()
        info["pages"].append(page_info)

    doc.close()
    return info


def _get_file_size(path: str) -> int:
    import os
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def _format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def print_info(info: dict) -> None:
    """Print PDF info in a human-readable format."""
    print(f"\n{'='*60}")
    print(f"  PDF Info: {info['filename']}")
    print(f"{'='*60}")
    print(f"  Pages:      {info['page_count']}")
    print(f"  File size:  {_format_size(info['file_size_bytes'])}")
    print()

    meta = info["metadata"]
    if any(meta.values()):
        print(f"  {'Metadata':-^60}")
        for key, val in meta.items():
            if val:
                print(f"    {key.capitalize():12s}: {val}")
        print()

    print(f"  {'Pages':-^60}")
    for p in info["pages"]:
        print(f"    Page {p['page_number']:>4d}:  {p['width_pts']:>7.2f} x {p['height_pts']:>7.2f} pt"
              f"  ({p['width_inches']} x {p['height_inches']} in)")
        if "text" in p and p["text"]:
            preview = p["text"][:120].replace("\n", " ")
            print(f"             Text: {preview}...")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract detailed information from a PDF file."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--text", action="store_true",
                        help="Extract text content page by page")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    info = get_pdf_info(args.input, extract_text=args.text)

    if args.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print_info(info)


if __name__ == "__main__":
    main()