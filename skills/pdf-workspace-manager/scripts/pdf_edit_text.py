#!/usr/bin/env python3
"""
pdf_edit_text.py — Search and replace text on PDF pages.

Uses PyMuPDF (fitz) to find text spans and replace their content while
preserving formatting. Works best with simple, selectable text.

Usage:
    python pdf_edit_text.py "input.pdf" --search "old text" --replace "new text"
    python pdf_edit_text.py "input.pdf" --search "foo" --replace "bar" --pages 1-3
    python pdf_edit_text.py "input.pdf" --search "\\d{4}" --replace "****" --regex
"""

import argparse
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def parse_page_range(spec: str, total_pages: int) -> set[int]:
    """Parse a page range like '1-3,5' into a set of 0-based page indices."""
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
                    print(f"WARNING: Range {part} out of bounds (1-{total_pages}), clamping.",
                          file=sys.stderr)
                    start = max(1, min(start, total_pages))
                    end = max(1, min(end, total_pages))
                pages.update(range(start - 1, end))  # 0-based
            except ValueError:
                print(f"WARNING: Invalid range '{part}', skipping.", file=sys.stderr)
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p - 1)
                else:
                    print(f"WARNING: Page {p} out of bounds (1-{total_pages}), skipping.",
                          file=sys.stderr)
            except ValueError:
                print(f"WARNING: Invalid page number '{part}', skipping.", file=sys.stderr)
    return pages


def edit_text(pdf_path: str, search: str, replace: str,
              use_regex: bool = False, page_set: set[int] = None,
              output_path: str = None) -> dict:
    """
    Search and replace text in a PDF. Returns a dict with:
      - output_path: path to the modified PDF
      - replacements: total number of replacements made
      - affected_pages: list of page numbers (1-based) with changes
    """
    doc = fitz.open(pdf_path)
    total_replacements = 0
    affected_pages = []

    if use_regex:
        pattern = re.compile(search)
    else:
        pattern = re.compile(re.escape(search))

    for i in range(doc.page_count):
        if page_set is not None and i not in page_set:
            continue

        page = doc[i]
        blocks = page.get_text("dict")["blocks"]
        page_replacements = 0

        for block in blocks:
            if block["type"] != 0:  # 0 = text block
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    original = span["text"]
                    new_text = pattern.sub(replace, original)
                    if new_text != original:
                        # Replace the text in the span
                        span["text"] = new_text
                        page_replacements += 1

                        # Update the visual text by redrawing the span
                        # We use insert_text with the new text
                        rect = fitz.Rect(span["bbox"])
                        font_size = span["size"]
                        fontname = span["font"]
                        color = span["color"]

                        # Cover old text with a white rectangle
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1),
                                       overlay=True, width=0)

                        # Insert new text preserving position and style
                        page.insert_text(
                            point=(rect.x0, rect.y0 + font_size * 0.85),
                            text=new_text,
                            fontsize=font_size,
                            fontname=fontname,
                            color=color,
                            overlay=True,
                        )

        if page_replacements > 0:
            total_replacements += page_replacements
            affected_pages.append(i + 1)

    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + "_modified.pdf"

    doc.save(output_path, incremental=False, deflate=True)
    doc.close()

    return {
        "output_path": output_path,
        "replacements": total_replacements,
        "affected_pages": affected_pages,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Search and replace text on PDF pages while preserving formatting."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--search", "-s", required=True, help="Text to search for")
    parser.add_argument("--replace", "-r", required=True, help="Replacement text")
    parser.add_argument("--pages", "-p",
                        help="Page range to process (e.g. '1-3,5'). Default: all pages.")
    parser.add_argument("--output", "-o", help="Output filename (default: input_modified.pdf)")
    parser.add_argument("--regex", action="store_true",
                        help="Treat search string as a regular expression")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Peek at total page count
    doc = fitz.open(args.input)
    total_pages = doc.page_count
    doc.close()

    # Parse page restriction
    page_set = None
    if args.pages:
        page_set = parse_page_range(args.pages, total_pages)
        if not page_set:
            print("ERROR: No valid pages specified.", file=sys.stderr)
            sys.exit(1)

    print(f"Searching for: '{args.search}'{' (regex)' if args.regex else ''}")
    print(f"Replacing with: '{args.replace}'")
    if page_set:
        shown = sorted(p + 1 for p in page_set)
        print(f"Pages: {', '.join(str(p) for p in shown)}")
    else:
        print(f"Pages: all ({total_pages})")
    print()

    result = edit_text(args.input, args.search, args.replace,
                       use_regex=args.regex, page_set=page_set,
                       output_path=args.output)

    print(f"✅ Replacements made: {result['replacements']}")
    print(f"   Affected pages: {', '.join(str(p) for p in result['affected_pages'])}")
    print(f"   Output: {result['output_path']}")


if __name__ == "__main__":
    main()