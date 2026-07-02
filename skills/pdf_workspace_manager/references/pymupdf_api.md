# PyMuPDF (fitz) API Reference

Key APIs used by the PDF Workspace Manager scripts.

## Opening & Saving

```python
import fitz

# Open existing PDF
doc = fitz.open("file.pdf")

# Save with compression
doc.save("output.pdf", incremental=False, deflate=True)

# Close
doc.close()
```

## Document Properties

```python
doc.page_count          # int: total number of pages
doc.metadata            # dict: title, author, subject, keywords, creator, producer
doc.set_metadata(dict)  # Update metadata fields
```

## Page Operations

```python
page = doc[i]           # Get page by 0-based index
page.rect               # fitz.Rect: width, height in points
page.get_text("text")   # str: plain text content
page.get_text("dict")   # dict: blocks, lines, spans with formatting
```

## SVG Rendering

```python
page.get_svg_image(matrix=fitz.Matrix(1.5, 1.5))  # str: SVG markup for browser preview
```

## Text Editing

```python
# Draw a white rectangle to cover old text
page.draw_rect(rect, color=(1,1,1), fill=(1,1,1), overlay=True, width=0)

# Insert new text at position
page.insert_text(point=(x, y), text="Hello", fontsize=12,
                 fontname="helv", color=(0,0,0), overlay=True)
```

## Common Font Names

| Name | Description |
|------|-------------|
| `helv` | Helvetica (sans-serif) |
| `tiro` | Times Roman (serif) |
| `cour` | Courier (monospace) |
| `zadb` | Zapf Dingbats |

## Matrix & Rect

```python
# 1 point = 1/72 inch
rect.width   # width in points
rect.height  # height in points
rect.x0, rect.y0, rect.x1, rect.y1  # coordinates
```