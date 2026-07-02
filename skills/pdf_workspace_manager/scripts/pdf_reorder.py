#!/usr/bin/env python3
"""
pdf_reorder.py — Reorder, extract, or remove pages from a PDF.

Uses pypdf (PdfWriter, PdfReader) to create a new PDF with pages in a
specified order, optionally excluding certain pages.

Usage:
    python pdf_reorder.py "input.pdf" --order 3,1,2,5,4
    python pdf_reorder.py "input.pdf" --order 5,4,3,2,1 --output reversed.pdf
    python pdf_reorder.py "input.pdf" --remove 2,4
    python pdf_reorder.py "input.pdf" --order 3,1,2 --remove 5
"""

import argparse
import os
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def parse_page_list(spec: str, total_pages: int) -> list:
    """Parse a comma-separated list of page numbers. Returns 0-based indices."""
    pages = []
    for part in spec.split(","):
        part = part.strip()
        try:
            p = int(part)
            if 1 <= p <= total_pages:
                pages.append(p - 1)  # convert to 0-based
            else:
                print(f"WARNING: Page {p} is out of bounds (1-{total_pages}), skipping.",
                      file=sys.stderr)
        except ValueError:
            print(f"WARNING: Invalid page number '{part}', skipping.", file=sys.stderr)

    if not pages:
        print("ERROR: No valid pages specified.", file=sys.stderr)
        sys.exit(1)

    return pages


def reorder_pdf(pdf_path: str, order: list[int], remove: set[int],
                output_path: str) -> int:
    """
    Create a new PDF with pages in the given order, excluding removed pages.
    order: list of 0-based page indices in desired order.
    remove: set of 0-based page indices to exclude.
    Returns the number of pages in the output.
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    pages_added = 0

    for idx in order:
        if idx in remove:
            continue
        writer.add_page(reader.pages[idx])
        pages_added += 1

    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()

    return pages_added


def main():
    parser = argparse.ArgumentParser(
        description="Reorder, extract, or remove pages from a PDF."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--order", help="New page order, 1-based, comma-separated (e.g. '3,1,2,5,4')")
    parser.add_argument("--remove", help="Pages to remove, 1-based, comma-separated (e.g. '2,4')")
    parser.add_argument("--output", "-o", help="Output filename (default: input_reordered.pdf)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    reader = PdfReader(args.input)
    total_pages = len(reader.pages)
    reader.stream.close()

    # Default order is [1, 2, 3, ..., total_pages]
    if args.order:
        order_1based = parse_page_list(args.order, total_pages)
        order = order_1based
    else:
        order = list(range(total_pages))

    remove_set = set()
    if args.remove:
        remove_1based = parse_page_list(args.remove, total_pages)
        remove_set = set(remove_1based)

    if not args.order and not args.remove:
        print("ERROR: Specify at least one of --order or --remove.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path:
        base = os.path.splitext(args.input)[0]
        output_path = base + "_reordered.pdf"

    result_pages = reorder_pdf(args.input, order, remove_set, output_path)

    # Summary of changes
    if args.order:
        print(f"  Order: {', '.join(str(p + 1) for p in order)}")
    if args.remove:
        print(f"  Removed: {', '.join(str(p + 1) for p in sorted(remove_set))}")

    print(f"\n✅ Created: {output_path} ({result_pages} pages)")


if __name__ == "__main__":
    main()