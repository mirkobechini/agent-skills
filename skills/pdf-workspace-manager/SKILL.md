---
name: pdf-workspace-manager
version: 1.0.1
author: Mirko Bechini
description: "Full PDF management skill: browser preview, merge, split, reorder, remove pages, text editing, metadata editing. Use when the user asks to manipulate or inspect PDF files."
argument-hint: "[operation] [file.pdf] [options]"
user-invocable: true
---

# PDF Workspace Manager

A comprehensive skill for manipulating PDF files directly from the workspace. Combines **PyMuPDF (fitz)** for advanced operations and **pypdf** for structural operations.

## When to Use

- User wants to **view/preview** a PDF in the browser
- User wants to **merge** multiple PDFs into one
- User wants to **split** a PDF into multiple files
- User wants to **reorder** or **remove** pages
- User wants to **edit text** or **metadata** in a PDF
- Any operation involving `.pdf` files in the workspace

## Output

This skill produces:

1. **Modified PDF files** — New PDF file in the same directory with a descriptive suffix (e.g., `document_merged.pdf`, `document_split_1.pdf`)
2. **HTML preview** — `original.pdf.html` in the same directory, viewable in VS Code's integrated browser
3. **JSON report** (optional) — `original.pdf.info.json` with metadata, page count, text content when using `--json` flag

## Prerequisites

### Required

- **Python** 3.8+ — Language runtime
- **pip** — Python package manager
- **PyMuPDF (fitz)** — Advanced PDF operations (preview, text editing, metadata)
- **pypdf** — PDF structural operations (merge, split, reorder)

### Installation

**macOS**:

```bash
brew install python
pip install pymupdf pypdf
```

**Ubuntu/Debian**:

```bash
sudo apt update && sudo apt install python3 python3-pip
pip install pymupdf pypdf
```

**Windows**:

```bash
# Via Chocolatey
choco install python
pip install pymupdf pypdf

# Or download Python from python.org and run:
pip install pymupdf pypdf
```

### Verify

```bash
python --version
python -c "import fitz; import pypdf; print('✓ PyMuPDF and pypdf installed')"
```

Expected output:

```
Python 3.8.x or higher
✓ PyMuPDF and pypdf installed
```

## Scripts Overview

| Script                          | Operation                                          | Library |
| ------------------------------- | -------------------------------------------------- | ------- |
| `./scripts/pdf_info.py`         | Detailed info (pages, dimensions, metadata, text)  | PyMuPDF |
| `./scripts/pdf_view.py`         | Browser preview as HTML                            | PyMuPDF |
| `./scripts/pdf_merge.py`        | Merge multiple PDFs into one                       | pypdf   |
| `./scripts/pdf_split.py`        | Split into separate files by page or range         | pypdf   |
| `./scripts/pdf_reorder.py`      | Reorder, remove, or extract pages                  | pypdf   |
| `./scripts/pdf_edit_text.py`    | Search and replace text on pages                   | PyMuPDF |
| `./scripts/pdf_metadata.py`     | Read/write metadata (author, title, subject, etc.) | PyMuPDF |
| `./scripts/pdf_remove_pages.py` | Remove specific pages                              | pypdf   |

## Procedure

### 1. PDF Info

Extract page count, dimensions, metadata, and full text:

```bash
python ./scripts/pdf_info.py "input.pdf"
```

Options:

- `--text` — Also extract text page by page
- `--json` — Output in JSON format

### 2. Browser Preview

Convert the PDF to HTML and open it in VS Code's built-in browser:

```bash
python ./scripts/pdf_view.py "input.pdf"
```

Generates `input.pdf.html` in the same folder and opens it using the browser tool (`open_browser_page`).

### 3. Merge

Combine multiple PDFs into a single file:

```bash
python ./scripts/pdf_merge.py "output.pdf" "file1.pdf" "file2.pdf" ...
```

### 4. Split

Split a PDF into multiple files. Supports:

- **Page range**: `python ./scripts/pdf_split.py "input.pdf" --pages 1-3,5,7-9`
- **Every page (one per file)**: `python ./scripts/pdf_split.py "input.pdf" --every`
- **Custom output prefix**: `--output "prefix"` (default: `input_page_N.pdf`)

### 5. Reorder Pages

Reorder, extract, or remove pages into a new PDF:

```bash
python ./scripts/pdf_reorder.py "input.pdf" --order 3,1,2,5,4
```

Options:

- `--order` — New page order (1-based, e.g. `3,1,2`)
- `--output` — Output filename (default: `input_reordered.pdf`)
- `--remove` — Pages to remove (e.g. `--remove 2,4`)

### 6. Remove Pages

Remove specific pages from a PDF:

```bash
python ./scripts/pdf_remove_pages.py "input.pdf" --pages 2,5,7-9
```

### 7. Text Editing

Search and replace text across pages of a PDF:

```bash
python ./scripts/pdf_edit_text.py "input.pdf" --search "original text" --replace "new text"
```

Options:

- `--pages` — Limit to specific pages (e.g. `1-3,5`)
- `--output` — Output filename (default: `input_modified.pdf`)
- `--regex` — Use regular expressions for search

### 8. Metadata

Read or write PDF metadata:

```bash
# Read
python ./scripts/pdf_metadata.py "input.pdf"

# Write
python ./scripts/pdf_metadata.py "input.pdf" \
  --set title="New Title" \
  --set author="Author Name" \
  --set subject="Subject" \
  --set keywords="keyword1, keyword2"
```

## Reference

| Script                | Purpose                           | Input                     | Output               |
| --------------------- | --------------------------------- | ------------------------- | -------------------- |
| `pdf_info.py`         | Extract metadata, text, page info | `file.pdf`                | JSON/stdout          |
| `pdf_view.py`         | Preview in browser                | `file.pdf`                | `file.pdf.html`      |
| `pdf_merge.py`        | Combine multiple files            | `file1.pdf file2.pdf ...` | `merged.pdf`         |
| `pdf_split.py`        | Split into separate files         | `file.pdf --pages 1-5`    | `file_page_*.pdf`    |
| `pdf_reorder.py`      | Reorder or extract pages          | `file.pdf --order 3,1,2`  | `file_reordered.pdf` |
| `pdf_remove_pages.py` | Remove specific pages             | `file.pdf --pages 2,4`    | `file_removed.pdf`   |
| `pdf_edit_text.py`    | Find and replace text             | `file.pdf --search text`  | `file_modified.pdf`  |
| `pdf_metadata.py`     | Read/write metadata               | `file.pdf --set title=X`  | JSON/modified PDF    |

## Examples

### Example 1: Preview and Extract Text

**User Request**: "Show me the content of this PDF and extract all text"

```bash
python ./scripts/pdf_info.py "document.pdf" --text
python ./scripts/pdf_view.py "document.pdf"
```

**Result**:

- Console output with page count, dimensions, metadata
- Text extracted page-by-page in JSON
- Browser opens with HTML preview of the PDF

---

### Example 2: Merge Multiple PDFs

**User Request**: "Combine these three reports into one PDF"

```bash
python ./scripts/pdf_merge.py "final_report.pdf" "part1.pdf" "part2.pdf" "part3.pdf"
```

**Result**:

- `final_report.pdf` created with all pages in order
- Metadata from first file is preserved

---

### Example 3: Split and Remove Pages

**User Request**: "Remove pages 3-5 from this PDF and save it"

```bash
python ./scripts/pdf_remove_pages.py "document.pdf" --pages 3-5
```

**Result**:

- `document_removed.pdf` created with pages 3-5 deleted
- Original file unchanged

---

### Example 4: Search and Replace Text

**User Request**: "Replace 'Old Company Name' with 'New Company Name' in the PDF"

```bash
python ./scripts/pdf_edit_text.py "contract.pdf" \
  --search "Old Company Name" \
  --replace "New Company Name"
```

**Result**:

- `contract_modified.pdf` created with all replacements made
- Search is case-sensitive by default

---

### Example 5: Update Metadata

**User Request**: "Set the title and author in this PDF"

```bash
python ./scripts/pdf_metadata.py "report.pdf" \
  --set title="Q3 2024 Report" \
  --set author="John Doe" \
  --set subject="Financial Report"
```

**Result**:

- Metadata updated in the PDF
- Visible in PDF properties when opened

## Notes & Tips

- **Original files are never modified**: every operation creates a new file with a descriptive suffix
- **Performance**: For large files (>100MB), PyMuPDF is significantly faster than pypdf
- **Browser preview limitations**: The HTML viewer does not support complex elements (transparencies, advanced embedded fonts); for accurate previews use an external PDF viewer
- **Common workflow**: Explore → Preview → Transform → Verify

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fitz'"

**Cause**: PyMuPDF is not installed or installed in a different Python environment.

**Solution**:

```bash
# Verify Python version
python --version

# Install/reinstall PyMuPDF
pip install --upgrade pymupdf

# Verify installation
python -c "import fitz; print(fitz.__version__)"
```

### Issue: "PDF file seems to be corrupted or not a valid PDF"

**Cause**: The file is not a valid PDF or is password-protected.

**Solution**:

```bash
# Try with pdf_info.py to get detailed error
python ./scripts/pdf_info.py "suspicious.pdf"

# If encrypted, consider using external tools to unlock
# Check if file is actually a PDF
file suspicious.pdf
```

### Issue: "Memory error with large files"

**Cause**: PyMuPDF loads entire file into memory.

**Solution**:

- Use `--pages` flag to process in chunks
- Split the PDF first, then process parts separately
- Use pypdf-based scripts (merge/split/reorder) instead of PyMuPDF-based ones for large files

### Issue: "Text replacement not working"

**Cause**: Text is encoded as images or the exact string doesn't match.

**Solution**:

```bash
# Try with exact matching
python ./scripts/pdf_edit_text.py "file.pdf" --search "exact text" --replace "new text"

# Try limiting to specific pages
python ./scripts/pdf_edit_text.py "file.pdf" --search "text" --replace "new" --pages 1-3

# Check if text is searchable first
python ./scripts/pdf_info.py "file.pdf" --text | grep "search term"
```

## FAQ

**Q: Can I undo changes made by this skill?**  
A: All original files are preserved. The skill creates new files with suffixes, so you can always revert by deleting the modified file and using the original.

**Q: How do I preview a PDF without modifying it?**  
A: Use `python ./scripts/pdf_view.py "file.pdf"` to preview in the browser, or `python ./scripts/pdf_info.py "file.pdf"` to see metadata and page info.

**Q: Can I batch process multiple PDFs?**  
A: Yes, use shell loops or write a script that calls the Python scripts in sequence:

```bash
for pdf in *.pdf; do
  python ./scripts/pdf_info.py "$pdf"
done
```

**Q: What happens to embedded images and fonts?**  
A: They are preserved in most operations (merge, split, reorder). Text-only operations may affect them depending on PDF structure.

**Q: Is there a file size limit?**  
A: No hard limit, but memory usage increases with file size. Very large files (>500MB) may require system resources.

**Q: Can I compress a PDF?**  
A: This skill doesn't include compression yet. Use external tools like `gs` (Ghostscript) or online services.

---

## File Structure

```
pdf-workspace-manager/
├── SKILL.md                           # This documentation file
├── requirements.txt                   # Python dependencies
├── pytest.ini                         # Pytest configuration
├── .gitignore                         # Git ignore rules
├── scripts/
│   ├── __init__.py                    # Package marker
│   ├── pdf_info.py                    # Extract metadata and text
│   ├── pdf_view.py                    # Browser preview
│   ├── pdf_merge.py                   # Merge multiple PDFs
│   ├── pdf_split.py                   # Split by pages
│   ├── pdf_reorder.py                 # Reorder pages
│   ├── pdf_remove_pages.py            # Remove specific pages
│   ├── pdf_edit_text.py               # Find and replace text
│   └── pdf_metadata.py                # Read/write metadata
├── tests/
│   ├── __init__.py                    # Package marker
│   └── test_pdf_operations.py         # Unit tests
├── assets/                            # Test data (sample PDFs)
│   └── ...
└── references/                        # External API documentation
    ├── pymupdf_api.md                 # PyMuPDF API reference
    └── pypdf_api.md                   # pypdf API reference
```

---

**Last Updated**: 2026-07-05  
**Status**: Active  
**Maintainer**: Mirko
