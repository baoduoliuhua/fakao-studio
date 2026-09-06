#!/usr/bin/env python3
"""Convert a PDF or Markdown file into the canonical Markdown used by fakao-prep."""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path
from typing import Any


def read_markdown(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def read_pdf(path: Path) -> str:
    """Return extracted text and bookmarks from a text PDF.

    Tries pypdf, pdfplumber, then PyMuPDF. Returns empty string if no text is
    found or no suitable library is available.
    """

    text = ""
    bookmarks: list[str] = []

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
        if reader.outline:
            bookmarks = _flatten_outline(reader.outline)
    except Exception:
        text = ""
        bookmarks = []

    if not text.strip():
        try:
            import pdfplumber  # type: ignore

            with pdfplumber.open(path) as pdf:
                pages = [(page.extract_text() or "") for page in pdf.pages]
                text = "\n\n".join(pages)
        except Exception:
            text = ""

    if not text.strip():
        try:
            import fitz  # type: ignore

            doc = fitz.open(path)
            text = "\n\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            text = ""

    prefix = "\n\n".join(f"# {item}" for item in bookmarks if item)
    return f"{prefix}\n\n{text}".strip() if prefix else text


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


def extract_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    raw = match.group(1)
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw) or {}
    except Exception:
        data = _parse_simple_front_matter(raw)
    return data if isinstance(data, dict) else {}, text[match.end() :]


def _parse_simple_front_matter(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("\"'")
    return data


def heading_info(line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def parse_kp_marker(block: str) -> dict[str, str]:
    marker = {}
    for match in re.finditer(r"<!--\s*kp\b([^>]*)-->", block, re.IGNORECASE):
        attrs = match.group(1)
        for key in ("id", "page", "confidence"):
            m = re.search(rf'\b{key}\s*=\s*"([^"]*)"', attrs, re.IGNORECASE)
            if m:
                marker[key] = m.group(1)
    return marker


def canonicalize_markdown(text: str, source_name: str) -> str:
    front_matter, body = extract_front_matter(text)
    if not body.strip():
        body = text

    lines = body.splitlines()
    output: list[str] = []
    current_h2: list[str] = []
    last_marker = ""
    has_h2 = False

    for line in lines:
        info = heading_info(line)
        if info and info[0] == 2:
            if current_h2:
                _flush_kp(output, current_h2, last_marker)
            has_h2 = True
            current_h2 = [line]
            last_marker = ""
        elif current_h2:
            current_h2.append(line)
            if re.match(r"<!--\s*kp\b", line, re.IGNORECASE):
                last_marker = line
        else:
            output.append(line)

    if current_h2:
        _flush_kp(output, current_h2, last_marker)

    canonical_body = "\n".join(output).strip()
    if not has_h2:
        canonical_body = _wrap_body_as_kp(body)

    if not front_matter:
        front_matter = {"title": Path(source_name).stem}
    front_matter.setdefault("source_file", source_name)

    return _render_canonical(front_matter, canonical_body)


def _flush_kp(output: list[str], block: list[str], marker: str) -> None:
    if marker:
        output.append(marker)
    output.extend(line.rstrip() for line in block)
    output.append("")


def _wrap_body_as_kp(body: str) -> str:
    first_line = body.strip().splitlines()[0] if body.strip() else "知识点"
    title = re.sub(r"^#+\s*", "", first_line).strip() or "知识点"
    rest = "\n".join(body.strip().splitlines()[1:]).strip()
    return f"<!-- kp id=\"kp-01\" confidence=\"low\" -->\n## {title}\n{rest}".strip()


def _render_canonical(front_matter: dict[str, Any], body: str) -> str:
    try:
        import yaml  # type: ignore

        fm = yaml.safe_dump(
            {k: front_matter[k] for k in front_matter if front_matter[k] not in ("", None)},
            allow_unicode=True,
            sort_keys=False,
        ).strip()
    except Exception:
        fm = "\n".join(f"{k}: {v}" for k, v in front_matter.items())
    return f"---\n{fm}\n---\n\n{body}\n"


def scanned_pdf_to_text(path: Path, args: argparse.Namespace) -> str:
    """Best-effort OCR for scanned PDFs."""

    page_images = _render_pages(path)
    if args.vision_model and args.api_key and page_images:
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=args.api_key, base_url=args.base_url or None)
            parts: list[str] = []
            for page_no, image_bytes in page_images:
                b64 = base64.b64encode(image_bytes).decode("ascii")
                response = client.chat.completions.create(
                    model=args.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请逐字识别这张法考讲义页面，保留标题和段落。不要总结，只输出识别文字。",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                                },
                            ],
                        }
                    ],
                )
                content = response.choices[0].message.content or ""
                parts.append(f"\n\n<!-- page:{page_no} -->\n{content}")
            return "\n".join(parts)
        except Exception as exc:
            print(f"Vision OCR failed: {exc}", file=sys.stderr)

    if page_images:
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore
            import io

            parts = []
            for page_no, image_bytes in page_images:
                image = Image.open(io.BytesIO(image_bytes))
                content = pytesseract.image_to_string(image, lang="chi_sim+eng")
                parts.append(f"\n\n<!-- page:{page_no} -->\n{content}")
            return "\n".join(parts)
        except Exception as exc:
            print(f"Local OCR failed: {exc}", file=sys.stderr)

    return ""


def _render_pages(path: Path, dpi: int = 150) -> list[tuple[int, bytes]]:
    try:
        import fitz  # type: ignore

        doc = fitz.open(path)
        images: list[tuple[int, bytes]] = []
        for page_no in range(len(doc)):
            pix = doc[page_no].get_pixmap(dpi=dpi)
            images.append((page_no + 1, pix.tobytes("png")))
        doc.close()
        return images
    except Exception:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--vision-model", default=None)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.exists():
        print(f"Input not found: {source}", file=sys.stderr)
        return 2

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if source.suffix.lower() == ".md":
        raw = read_markdown(source)
    elif source.suffix.lower() == ".pdf":
        raw = read_pdf(source)
        if not raw.strip():
            raw = scanned_pdf_to_text(source, args)
        if not raw.strip():
            print(
                "No text could be extracted from the PDF. Use a vision model or install OCR dependencies.",
                file=sys.stderr,
            )
            return 3
    else:
        print("Only .md and .pdf inputs are supported.", file=sys.stderr)
        return 2

    canonical = canonicalize_markdown(raw, source.name)
    target = output_dir / f"{source.stem}.md"
    target.write_text(canonical, encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
