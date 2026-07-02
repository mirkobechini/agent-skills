---
name: pdf-workspace-manager
version: 1.0.0
author: Mirko
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

## Prerequisites

- Python 3.8+ with pip
- Install dependencies:
  ```bash
  pip install pymupdf pypdf
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

## Typical Workflow

1. Use `pdf_info.py --text` to explore the content
2. Use `pdf_view.py` for a quick visual preview
3. Apply transformations (merge/split/reorder/edit)
4. Verify the result with `pdf_info.py` or `pdf_view.py`

## Notes

- Original files are **never modified**: every operation creates a new file
- For large files (>100MB), PyMuPDF is significantly faster
- The HTML viewer does not support complex elements (transparencies, advanced embedded fonts); for accurate previews use an external viewer
