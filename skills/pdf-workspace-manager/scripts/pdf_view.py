#!/usr/bin/env python3
"""
pdf_view.py — Convert a PDF to an HTML page for browser preview.

Uses PyMuPDF (fitz) to render each page as an SVG embedded in a standalone
HTML file with page navigation. The output file is saved alongside the input.

Usage:
    python pdf_view.py "input.pdf"
    python pdf_view.py "input.pdf" --output preview.html
"""

import argparse
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def pdf_to_html(pdf_path: str, output_path: str = None) -> str:
    """
    Convert a PDF to a standalone HTML file with SVG pages.
    Returns the path to the generated HTML file.
    """
    doc = fitz.open(pdf_path)

    if output_path is None:
        base = os.path.splitext(pdf_path)[0]
        output_path = base + ".pdf.html"

    # Read page_count BEFORE closing document
    total_pages = doc.page_count
    
    pages_html = []
    for i in range(total_pages):
        page = doc[i]
        svg = page.get_svg_image(matrix=fitz.Matrix(1.5, 1.5))
        pages_html.append(
            f'<div class="page" data-page="{i + 1}">\n'
            f'  <div class="page-label">Page {i + 1} of {total_pages}</div>\n'
            f'  {svg}\n'
            f'</div>'
        )

    doc.close()

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Preview: {os.path.basename(pdf_path)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #404040; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  .toolbar {{
    position: sticky; top: 0; z-index: 100;
    background: #2d2d2d; color: #fff;
    display: flex; align-items: center; gap: 12px;
    padding: 8px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  }}
  .toolbar button {{
    background: #555; color: #fff; border: none;
    padding: 6px 14px; border-radius: 4px; cursor: pointer;
    font-size: 14px;
  }}
  .toolbar button:hover {{ background: #666; }}
  .toolbar span {{ font-size: 14px; }}
  .page-counter {{ margin-left: auto; }}
  .pages-container {{
    display: flex; flex-direction: column; align-items: center;
    padding: 20px; gap: 16px;
  }}
  .page {{
    background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    border-radius: 4px; overflow: hidden;
  }}
  .page-label {{
    background: #f0f0f0; padding: 6px 16px; font-size: 13px;
    color: #555; text-align: center; border-bottom: 1px solid #ddd;
  }}
  .page svg {{ display: block; max-width: 100%; height: auto; }}
</style>
</head>
<body>
<div class="toolbar">
  <button onclick="goPage(-1)">◀ Prev</button>
  <button onclick="goPage(1)">Next ▶</button>
  <span class="page-counter" id="pageCounter">Page 1 of {total_pages}</span>
</div>
<div class="pages-container" id="pagesContainer">
{''.join(pages_html)}
</div>
<script>
  var currentPage = 1;
  var totalPages = {total_pages};
  function showPage(n) {{
    if (n < 1 || n > totalPages) return;
    currentPage = n;
    document.getElementById('pageCounter').textContent = 'Page ' + n + ' of ' + totalPages;
    document.querySelectorAll('.page').forEach(function(el, idx) {{
      el.style.display = (idx + 1 === n) ? 'block' : 'none';
    }});
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}
  function goPage(delta) {{ showPage(currentPage + delta); }}
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowLeft') showPage(currentPage - 1);
    if (e.key === 'ArrowRight') showPage(currentPage + 1);
  }});
  showPage(1);
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF to an HTML page for browser preview."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Output HTML file path (default: input.pdf.html)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = pdf_to_html(args.input, args.output)
    print(f"✅ Preview saved to: {output}")
    print(f"   Open this file with the browser tool (open_browser_page or navigate_page).")


if __name__ == "__main__":
    main()