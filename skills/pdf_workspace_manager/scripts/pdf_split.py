#!/usr/bin/env python3
"""
pdf_split.py — Split a PDF into multiple files by page ranges or individual pages.

Uses pypdf (PdfWriter) to extract pages into separate PDF files.

Usage:
    python pdf_split.py "input.pdf" --pages 1-3,5,7-9
    python pdf_split.py "input.pdf" --every
    python pdf_split.py "input.pdf" --pages 1-3 --output "prefix"
"""

import argparse
import os
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def parse_page_spec(spec: str, total_pages: int) -> list:
    """
    Parse a page range specification like "1-3,5,7-9" into a list of 0-based
    page indices. Returns a sorted, deduplicated list.
    """
    pages = set()
    parts = spec.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start = int(start.strip())
                end = int(end.strip())
                if start < 1 or end > total_pages:
                    print(f"WARNING: Range {part} is out of bounds (1-{total_pages}), clamping.",
                          file=sys.stderr)
                    start = max(1, min(start, total_pages))
                    end = max(1, min(end, total_pages))
                pages.update(range(start, end + 1))
            except ValueError:
                print(f"WARNING: Invalid range '{part}', skipping.", file=sys.stderr)
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p)
                else:
                    print(f"WARNING: Page {p} is out of bounds (1-{total_pages}), skipping.",
                          file=sys.stderr)
            except ValueError:
                print(f"WARNING: Invalid page number '{part}', skipping.", file=sys.stderr)

    if not pages:
        print("ERROR: No valid pages specified.", file=sys.stderr)
        sys.exit(1)

    return sorted(pages)


def split_by_ranges(pdf_path: str, output_prefix: str, ranges: list) -> list:
    """
    Split PDF by ranges. Each range produces one output file.
    ranges is a list of page numbers (1-based).
    Returns list of generated filenames.
    """
    reader = PdfReader(pdf_path)
    generated = []

    # Group consecutive pages into chunks
    chunks = []
    current = [ranges[0]]
    for p in ranges[1:]:
        if p == current[-1] + 1:
            current.append(p)
        else:
            chunks.append(current)
            current = [p]
    chunks.append(current)

    for i, chunk in enumerate(chunks, 1):
        writer = PdfWriter()
        for p in chunk:
            writer.add_page(reader.pages[p - 1])

        if len(chunks) == 1:
            out_path = f"{output_prefix}.pdf"
        else:
            out_path = f"{output_prefix}_part{i}_{chunk[0]}-{chunk[-1]}.pdf"

        with open(out_path, "wb") as f:
            writer.write(f)
        writer.close()
        generated.append(out_path)

    return generated


def split_every_page(pdf_path: str, output_prefix: str) -> list:
    """Split PDF into individual pages. Returns list of generated filenames."""
    reader = PdfReader(pdf_path)
    generated = []

    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        out_path = f"{output_prefix}_page_{i + 1}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        writer.close()
        generated.append(out_path)

    return generated


def main():
    parser = argparse.ArgumentParser(
        description="Split a PDF into multiple files by page ranges or individual pages."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--pages", help="Page ranges to extract, e.g. '1-3,5,7-9' (1-based)")
    parser.add_argument("--every", action="store_true",
                        help="Split every page into a separate file")
    parser.add_argument("--output", "-o",
                        help="Output filename prefix (default: input name without extension)")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_prefix = args.output or os.path.splitext(os.path.basename(input_path))[0]

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    reader.stream.close()

    if args.every:
        print(f"Splitting '{input_path}' into {total_pages} individual pages...")
        files = split_every_page(input_path, output_prefix)
    elif args.pages:
        pages = parse_page_spec(args.pages, total_pages)
        print(f"Splitting '{input_path}' by ranges: {args.pages} ({len(pages)} pages)...")
        files = split_by_ranges(input_path, output_prefix, pages)
    else:
        print("ERROR: Specify either --pages or --every.", file=sys.stderr)
        sys.exit(1)

    print(f"\n✅ Generated {len(files)} file(s):")
    for f in files:
        size = os.path.getsize(f)
        print(f"  + {f} ({_format_size(size)})")


def _format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    main()