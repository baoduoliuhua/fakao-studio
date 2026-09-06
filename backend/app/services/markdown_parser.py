from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class ParsedKnowledgePoint:
    title: str
    body_md: str
    source_refs: list[dict[str, Any]]
    confidence: str
    order: int
    chapter_title: str | None = None
    marker_id: str | None = None


@dataclass
class ParsedChapter:
    title: str
    level: int
    order: int
    parent_title: str | None = None


@dataclass
class ParsedMarkdown:
    title: str
    source_file: str
    page_start: int | None
    page_end: int | None
    chapters: list[ParsedChapter] = field(default_factory=list)
    knowledge_points: list[ParsedKnowledgePoint] = field(default_factory=list)


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except Exception:
        data = {}
        for line in raw.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip().strip("\"'")
    return data if isinstance(data, dict) else {}, text[match.end() :]


def _heading(line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def _parse_kp_marker(block: str) -> dict[str, str]:
    marker: dict[str, str] = {}
    for match in re.finditer(r"<!--\s*kp\b([^>]*)-->", block, re.IGNORECASE):
        attrs = match.group(1)
        for key in ("id", "page", "confidence"):
            m = re.search(rf'\b{key}\s*=\s*"([^"]*)"', attrs, re.IGNORECASE)
            if m:
                marker[key] = m.group(1)
    return marker


def _page_range(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None
    parts = re.split(r"[-–]", value.strip())
    try:
        start = int(parts[0])
        end = int(parts[-1])
        return start, end
    except Exception:
        return None, None


def parse_markdown(content: str, filename: str) -> ParsedMarkdown:
    front_matter, body = parse_front_matter(content)
    source_file = str(front_matter.get("source_file") or filename)
    title = str(front_matter.get("title") or _derive_title(body, filename))
    page_start = _as_int(front_matter.get("page_start"))
    page_end = _as_int(front_matter.get("page_end"))
    chapter_path = front_matter.get("chapter_path") or []
    if isinstance(chapter_path, str):
        chapter_path = [chapter_path]

    heading_levels = sorted({_heading(line)[0] for line in body.splitlines() if _heading(line)})
    if len(heading_levels) == 0:
        chapter_level: int | None = None
        kp_level: int | None = None
    elif len(heading_levels) == 1:
        chapter_level = None
        kp_level = heading_levels[0]
    else:
        chapter_level = heading_levels[0]
        kp_level = heading_levels[1]

    chapters: list[ParsedChapter] = []
    knowledge_points: list[ParsedKnowledgePoint] = []
    chapter_by_title: dict[str, ParsedChapter] = {}
    current_chapter: ParsedChapter | None = None
    current_kp: list[str] = []
    kp_marker: dict[str, str] = {}
    pending_marker: dict[str, str] = {}
    order = 0
    chapter_order = 0

    def is_kp_heading(line: str) -> bool:
        if kp_level is None:
            return False
        heading = _heading(line)
        return bool(heading and heading[0] == kp_level)

    def flush_kp() -> None:
        nonlocal order
        if not current_kp:
            return
        title_line = next((line for line in current_kp if is_kp_heading(line)), "")
        kp_title = _heading(title_line)[1].strip() if title_line else "未命名知识点"
        body_lines = [line for line in current_kp if line != title_line]
        page_value = kp_marker.get("page")
        p_start, p_end = _page_range(page_value)
        if p_start is None:
            p_start = page_start
        if p_end is None:
            p_end = page_end
        excerpt = " ".join(
            line.strip()
            for line in body_lines
            if line.strip() and not line.startswith("#")
        )[:300]
        knowledge_points.append(
            ParsedKnowledgePoint(
                title=kp_title,
                body_md="\n".join(body_lines).strip(),
                source_refs=[
                    {
                        "source_file": source_file,
                        "page_start": p_start,
                        "page_end": p_end,
                        "heading": kp_title,
                        "excerpt": excerpt,
                    }
                ],
                confidence=kp_marker.get("confidence", "high"),
                order=order,
                chapter_title=current_chapter.title if current_chapter else None,
                marker_id=kp_marker.get("id"),
            )
        )
        order += 1

    lines = body.splitlines()
    for index, line in enumerate(lines):
        heading = _heading(line)
        if heading and chapter_level is not None and heading[0] == chapter_level:
            flush_kp()
            current_kp = []
            kp_marker = {}
            pending_marker = {}
            current_chapter = _get_or_create_chapter(
                heading[1], heading[0], chapters, chapter_by_title, chapter_order
            )
            chapter_order += 1
            continue

        if heading and is_kp_heading(line):
            flush_kp()
            current_kp = [line]
            kp_marker = pending_marker
            pending_marker = {}
            continue

        if current_kp:
            current_kp.append(line)
            if re.match(r"<!--\s*kp\b", line, re.IGNORECASE):
                kp_marker = _parse_kp_marker(line)
        elif re.match(r"<!--\s*kp\b", line, re.IGNORECASE):
            pending_marker = _parse_kp_marker(line)

    flush_kp()

    if not knowledge_points:
        knowledge_points = [
            ParsedKnowledgePoint(
                title=title,
                body_md=body.strip(),
                source_refs=[
                    {
                        "source_file": source_file,
                        "page_start": page_start,
                        "page_end": page_end,
                        "heading": title,
                        "excerpt": body.strip()[:300],
                    }
                ],
                confidence="low",
                order=0,
                chapter_title=chapters[0].title if chapters else None,
            )
        ]

    if not chapters:
        root_title = str(chapter_path[0]) if chapter_path else title
        chapters.append(ParsedChapter(title=root_title, level=1, order=0))

    return ParsedMarkdown(
        title=title,
        source_file=source_file,
        page_start=page_start,
        page_end=page_end,
        chapters=chapters,
        knowledge_points=knowledge_points,
    )


def _get_or_create_chapter(
    title: str,
    level: int,
    chapters: list[ParsedChapter],
    by_title: dict[str, ParsedChapter],
    order: int,
) -> ParsedChapter:
    key = f"{level}:{title}"
    if key in by_title:
        return by_title[key]
    chapter = ParsedChapter(title=title, level=level, order=order)
    chapters.append(chapter)
    by_title[key] = chapter
    return chapter


def _derive_title(body: str, filename: str) -> str:
    for line in body.splitlines():
        heading = _heading(line)
        if heading:
            return heading[1]
    return filename.rsplit(".", 1)[0]


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None
