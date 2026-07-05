#!/usr/bin/env python3
"""
pdf_remove_pages.py — Remove specific pages from a PDF.

Uses pypdf (PdfReader, PdfWriter) to create a new PDF excluding the specified pages.

Usage:
    python pdf_remove_pages.py "input.pdf" --pages 2,5,7-9
    python pdf_remove_pages.py "input.pdf" --pages 1,3-5 --output cleaned.pdf
"""

import argparse
import os
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def parse_page_list(spec: str, total_pages: int) -> set:
    """Parse a page range specification and return a set of 0-based indices to remove."""
    pages_to_remove = set()
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
                    print(f"WARNING: Range {part} out of bounds (1-{total_pages}), clamping.",
                          file=sys.stderr)
                    start = max(1, min(start, total_pages))
                    end = max(1, min(end, total_pages))
                for p in range(start, end + 1):
                    pages_to_remove.add(p - 1)  # convert to 0-based
            except ValueError:
                print(f"WARNING: Invalid range '{part}', skipping.", file=sys.stderr)
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages_to_remove.add(p - 1)
                else:
                    print(f"WARNING: Page {p} out of bounds (1-{total_pages}), skipping.",
                          file=sys.stderr)
            except ValueError:
                print(f"WARNING: Invalid page number '{part}', skipping.", file=sys.stderr)

    return pages_to_remove


def remove_pages(pdf_path: str, pages_to_remove: set, output_path: str) -> int:
    """Remove specified pages and write the output PDF. Returns remaining page count."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        if i not in pages_to_remove:
            writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()

    return len(reader.pages) - len(pages_to_remove)


def main():
    parser = argparse.ArgumentParser(
        description="Remove specific pages from a PDF."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--pages", "-p", required=True,
                        help="Pages to remove, e.g. '2,5,7-9' (1-based)")
    parser.add_argument("--output", "-o", help="Output filename (default: input_cleaned.pdf)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Peek at total pages first
    reader = PdfReader(args.input)
    total_pages = len(reader.pages)
    reader.stream.close()

    remove_set = parse_page_list(args.pages, total_pages)

    if not remove_set:
        print("ERROR: No valid pages specified to remove.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path:
        base = os.path.splitext(args.input)[0]
        output_path = base + "_removed.pdf"

    remaining = remove_pages(args.input, remove_set, output_path)

    removed_sorted = sorted(p + 1 for p in remove_set)
    print(f"  Removed pages: {', '.join(str(p) for p in removed_sorted)}")
    print(f"  Retained: {remaining} pages")
    print(f"\n✅ Created: {output_path}")


if __name__ == "__main__":
    main()