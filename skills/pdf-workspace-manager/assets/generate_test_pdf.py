#!/usr/bin/env python3
"""
generate_test_pdf.py — Generate a multi-page test PDF with text and metadata.

Use this to test all PDF Workspace Manager scripts:
  python assets/generate_test_pdf.py
  python assets/generate_test_pdf.py --output mytest.pdf --pages 10
"""

import argparse
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def generate_test_pdf(output_path: str, num_pages: int = 5) -> str:
    """Generate a test PDF with numbered pages, text blocks, and metadata."""
    doc = fitz.open()

    # Set metadata
    doc.set_metadata({
        "title": "Test PDF for PDF Workspace Manager",
        "author": "PDF Workspace Manager",
        "subject": "Testing",
        "keywords": "test, pdf, workspace, manager",
        "creator": "generate_test_pdf.py",
    })

    # Page dimensions: A4 (595 x 842 points)
    width, height = 595, 842
    margin = 50

    for i in range(num_pages):
        page = doc.new_page(width=width, height=height)

        # Header
        page.insert_text(
            point=(margin, margin + 20),
            text=f"PDF Workspace Manager — Test Document",
            fontsize=16,
            fontname="helv",
            color=(0.2, 0.3, 0.6),
        )

        # Page number
        page.insert_text(
            point=(width - margin, margin + 20),
            text=f"Page {i + 1} of {num_pages}",
            fontsize=11,
            fontname="helv",
            color=(0.5, 0.5, 0.5),
        )

        # Separator line
        page.draw_line(
            fitz.Point(margin, margin + 35),
            fitz.Point(width - margin, margin + 35),
            color=(0.7, 0.7, 0.7),
            width=1,
        )

        # Body text
        y = margin + 70
        lines = [
            f"This is test page {i + 1}.",
            "",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "",
            "Features available in this skill:",
            "  • PDF Info — extract pages, dimensions, metadata, and text",
            "  • Browser Preview — convert PDF to HTML with page navigation",
            "  • Merge — combine multiple PDFs into one file",
            "  • Split — divide a PDF by page ranges or individual pages",
            "  • Reorder — change page order or extract pages",
            "  • Remove Pages — delete specific pages",
            "  • Text Editing — search and replace text while preserving formatting",
            "  • Metadata — read and write document metadata",
        ]

        for line in lines:
            page.insert_text(
                point=(margin, y),
                text=line,
                fontsize=11,
                fontname="helv",
                color=(0.1, 0.1, 0.1),
            )
            y += 18

        # Footer with searchable text for testing --search/--replace
        y = height - margin - 20
        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width - margin, y),
            color=(0.7, 0.7, 0.7),
            width=1,
        )
        page.insert_text(
            point=(margin, y + 18),
            text=f"Test PDF generated on: placeholder_date — SEARCHABLE_TEXT_MARKER",
            fontsize=9,
            fontname="helv",
            color=(0.6, 0.6, 0.6),
        )

    doc.save(output_path, deflate=True)
    doc.close()
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate a multi-page test PDF with text and metadata."
    )
    parser.add_argument("--output", "-o", default="test_document.pdf",
                        help="Output filename (default: test_document.pdf)")
    parser.add_argument("--pages", "-p", type=int, default=5,
                        help="Number of pages (default: 5)")
    args = parser.parse_args()

    if args.pages < 1:
        print("ERROR: Number of pages must be at least 1.", file=sys.stderr)
        sys.exit(1)

    output = generate_test_pdf(args.output, args.pages)
    size = os.path.getsize(output)
    print(f"✅ Generated: {output} ({args.pages} pages, {_format_size(size)})")
    print(f"\nTry these commands to test the skill:")
    print(f"  python scripts/pdf_info.py \"{output}\" --text")
    print(f"  python scripts/pdf_view.py \"{output}\"")
    print(f"  python scripts/pdf_merge.py \"merged.pdf\" \"{output}\" \"{output}\"")
    print(f"  python scripts/pdf_split.py \"{output}\" --pages 1-3")
    print(f"  python scripts/pdf_reorder.py \"{output}\" --order {args.pages},{args.pages-1},1")
    print(f"  python scripts/pdf_remove_pages.py \"{output}\" --pages 2")
    print(f'  python scripts/pdf_edit_text.py \"{output}\" --search "placeholder_date" --replace "2026-07-02"')
    print(f'  python scripts/pdf_metadata.py \"{output}\"')
    print(f'  python scripts/pdf_metadata.py \"{output}\" --set title="My Custom Title"')


def _format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    main()