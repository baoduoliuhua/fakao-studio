from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any


def decode_text_bytes(data: bytes) -> str:
    """Decode uploaded text using common Chinese encodings without mojibake."""

    for encoding in ("utf-8-sig", "utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def read_markdown_file(path: Path) -> str:
    return decode_text_bytes(path.read_bytes())


def extract_pdf_text(data: bytes) -> str:
    """Extract text and bookmarks from a text PDF."""

    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        bookmarks = _flatten_outline(reader.outline or [])
        prefix = "\n\n".join(bookmarks)
        body = "\n\n".join(pages).strip()
        return f"{prefix}\n\n{body}".strip() if prefix else body
    except Exception as exc:
        raise ValueError(f"PDF 文本提取失败：{exc}") from exc


def pdf_text_to_markdown(text: str) -> str:
    """Convert loose PDF text lines into simple Markdown headings."""

    lines = text.splitlines()
    output: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            output.append("")
            continue
        heading = _heading_for_line(stripped)
        output.append(f"{heading} {stripped}" if heading else stripped)
    return "\n".join(output)


def _heading_for_line(line: str) -> str | None:
    if re.match(r"^第[一二三四五六七八九十百千0-9]+章", line):
        return "#"
    if re.match(r"^第[一二三四五六七八九十百千0-9]+节", line):
        return "##"
    if re.match(r"^[一二三四五六七八九十]+、", line):
        return "##"
    if re.match(r"^（[一二三四五六七八九十]+）", line):
        return "###"
    if re.match(r"^\d+(\.\d+)*[、.\s]", line):
        return "##"
    return None


def _flatten_outline(outline: list[Any], depth: int = 0) -> list[str]:
    items: list[str] = []
    for entry in outline:
        if isinstance(entry, list):
            items.extend(_flatten_outline(entry, depth + 1))
            continue
        title = getattr(entry, "title", None)
        if title:
            items.append(f"{'#' * min(depth + 2, 6)} {title}")
        children = getattr(entry, "children", None)
        if children:
            items.extend(_flatten_outline(children, depth + 1))
    return items
