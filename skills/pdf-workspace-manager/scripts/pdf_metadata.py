#!/usr/bin/env python3
"""
pdf_metadata.py — Read and write PDF metadata.

Uses PyMuPDF (fitz) to get/set document metadata fields:
title, author, subject, keywords, creator, producer.

Usage:
    python pdf_metadata.py "input.pdf"
    python pdf_metadata.py "input.pdf" --set title="New Title" --set author="Author Name"
"""

import argparse
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def read_metadata(pdf_path: str) -> dict:
    """Read metadata from a PDF file."""
    doc = fitz.open(pdf_path)
    meta = dict(doc.metadata) if doc.metadata else {}
    # Add file info
    meta["_filename"] = os.path.basename(pdf_path)
    meta["_page_count"] = doc.page_count
    meta["_file_size_bytes"] = os.path.getsize(pdf_path)
    doc.close()
    return meta


def write_metadata(pdf_path: str, updates: dict, output_path: str = None) -> str:
    """Update metadata and save to output_path. Returns the output path."""
    if output_path is None:
        base = os.path.splitext(pdf_path)[0]
        output_path = base + "_updated.pdf"

    doc = fitz.open(pdf_path)
    current = dict(doc.metadata) if doc.metadata else {}

    for key, value in updates.items():
        if value is not None:
            current[key] = str(value)

    doc.set_metadata(current)
    doc.save(output_path, incremental=False, deflate=True)
    doc.close()

    return output_path


def print_metadata(meta: dict) -> None:
    """Pretty-print metadata."""
    print(f"\n{'='*60}")
    print(f"  PDF Metadata: {meta.get('_filename', 'unknown')}")
    print(f"{'='*60}")
    print(f"  Pages:      {meta.get('_page_count', '?')}")
    print(f"  File size:  {_format_size(meta.get('_file_size_bytes', 0))}")
    print()

    fields = ["title", "author", "subject", "keywords", "creator", "producer", "format"]
    print(f"  {'Document Info':-^60}")
    for field in fields:
        val = meta.get(field, "")
        if val:
            label = field.capitalize()
            print(f"    {label:12s}: {val}")

    # Show any custom/extra fields
    extra = {k: v for k, v in meta.items()
             if k not in fields and not k.startswith("_")}
    if extra:
        print()
        print(f"  {'Custom Fields':-^60}")
        for k, v in extra.items():
            print(f"    {k.capitalize():12s}: {v}")

    print(f"{'='*60}\n")


def _format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Read and write PDF metadata."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--set", "-s", action="append", nargs=1, metavar="KEY=VALUE",
                        dest="set_pairs",
                        help="Set a metadata field (e.g. --set title='New Title'). "
                             "Can be repeated.")
    parser.add_argument("--output", "-o", help="Output filename (default: input_metadata.pdf)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.set_pairs:
        # Write mode
        updates = {}
        for pair_list in args.set_pairs:
            pair = pair_list[0]
            if "=" not in pair:
                print(f"WARNING: Invalid key=value pair '{pair}', skipping.", file=sys.stderr)
                continue
            key, value = pair.split("=", 1)
            updates[key.strip()] = value.strip()

        if not updates:
            print("ERROR: No valid metadata fields to set.", file=sys.stderr)
            sys.exit(1)

        output = write_metadata(args.input, updates, args.output)
        print(f"  Updated fields: {', '.join(updates.keys())}")
        print(f"\n✅ Metadata written to: {output}")

        # Show updated metadata
        updated_meta = read_metadata(output)
        print_metadata(updated_meta)
    else:
        # Read mode
        meta = read_metadata(args.input)
        print_metadata(meta)


if __name__ == "__main__":
    main()