# pypdf API Reference

Key APIs used by the PDF Workspace Manager scripts.

## Reading

```python
from pypdf import PdfReader

reader = PdfReader("file.pdf")
len(reader.pages)           # int: total page count
reader.pages[i]             # Page object (0-based)
reader.metadata             # Optional metadata dict
reader.stream.close()       # Close the file handle
```

## Writing

```python
from pypdf import PdfWriter

writer = PdfWriter()

# Add a page from another PDF
writer.add_page(reader.pages[i])

# Append an entire PDF
writer.append("file.pdf")

# Write output
with open("output.pdf", "wb") as f:
    writer.write(f)

writer.close()
```

## Page Operations

```python
page = reader.pages[0]
page.mediabox.width     # float: width in points
page.mediabox.height    # float: height in points
page.rotation           # int: 0, 90, 180, 270
```

## Common Workflow: Selected pages

```python
writer = PdfWriter()
for page_num in [0, 2, 4]:  # 0-based indices
    writer.add_page(reader.pages[page_num])
with open("selected.pdf", "wb") as f:
    writer.write(f)
writer.close()
```

## Metadata (read)

```python
meta = reader.metadata
if meta:
    meta.title       # str or None
    meta.author      # str or None
    meta.subject     # str or None
    meta.creator     # str or None
    meta.producer    # str or None
```
