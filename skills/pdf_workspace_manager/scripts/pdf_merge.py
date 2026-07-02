#!/usr/bin/env python3
"""
pdf_merge.py — Merge multiple PDF files into a single PDF.

Uses pypdf (PdfWriter) to combine pages from multiple input PDFs.

Usage:
    python pdf_merge.py "output.pdf" "file1.pdf" "file2.pdf" ...
    python pdf_merge.py "output.pdf" --input-dir ./pdfs
"""

import argparse
import os
import sys

try:
    from pypdf import PdfWriter
except ImportError:
    print("ERROR: pypdf is required. Install with: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def merge_pdfs(input_paths: list, output_path: str) -> int:
    """
    Merge multiple PDFs into one. Returns the total number of pages.
    """
    writer = PdfWriter()
    total_pages = 0

    for path in input_paths:
        if not os.path.isfile(path):
            print(f"WARNING: File not found, skipping: {path}", file=sys.stderr)
            continue
        try:
            writer.append(path)
        except Exception as e:
            print(f"WARNING: Could not read {path}: {e}", file=sys.stderr)
            continue

    with open(output_path, "wb") as f:
        writer.write(f)

    from pypdf import PdfReader
    reader = PdfReader(output_path)
    total_pages = len(reader.pages)

    writer.close()
    return total_pages


def collect_pdfs_from_dir(directory: str, recursive: bool = False) -> list:
    """Collect all .pdf files from a directory, sorted alphabetically."""
    pdfs = []
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        if os.path.isfile(path) and entry.lower().endswith(".pdf"):
            pdfs.append(path)
        elif recursive and os.path.isdir(path):
            pdfs.extend(collect_pdfs_from_dir(path, recursive=True))
    return pdfs


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into a single PDF."
    )
    parser.add_argument("output", help="Path to the output PDF file")
    parser.add_argument("inputs", nargs="*", help="Input PDF files to merge")
    parser.add_argument("--input-dir", help="Directory containing PDF files to merge (sorted alphabetically)")
    parser.add_argument("--recursive", action="store_true",
                        help="Scan input directory recursively")
    args = parser.parse_args()

    input_files = list(args.inputs)

    if args.input_dir:
        if not os.path.isdir(args.input_dir):
            print(f"ERROR: Directory not found: {args.input_dir}", file=sys.stderr)
            sys.exit(1)
        dir_pdfs = collect_pdfs_from_dir(args.input_dir, recursive=args.recursive)
        if not dir_pdfs:
            print(f"ERROR: No PDF files found in {args.input_dir}", file=sys.stderr)
            sys.exit(1)
        input_files.extend(dir_pdfs)

    if not input_files:
        print("ERROR: No input files specified. Provide files as arguments or use --input-dir.",
              file=sys.stderr)
        sys.exit(1)

    print(f"Merging {len(input_files)} PDFs...")
    for f in input_files:
        print(f"  + {f}")

    total_pages = merge_pdfs(input_files, args.output)
    print(f"\n✅ Merged {len(input_files)} files ({total_pages} pages) into: {args.output}")


if __name__ == "__main__":
    main()