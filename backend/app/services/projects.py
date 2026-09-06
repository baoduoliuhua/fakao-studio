from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import ChapterNode, Document, KnowledgePoint
from .markdown_parser import parse_markdown


def import_document(db: Session, project_id: int, filename: str, content: str) -> dict:
    parsed = parse_markdown(content, filename)
    document = Document(
        project_id=project_id,
        filename=filename,
        content_md=content,
        source_file=parsed.source_file,
        page_start=parsed.page_start,
        page_end=parsed.page_end,
    )
    db.add(document)
    db.flush()

    chapter_map: dict[tuple[int, str], int] = {}
    for index, chapter in enumerate(parsed.chapters):
        node = ChapterNode(
            project_id=project_id,
            parent_id=None,
            title=chapter.title,
            level=chapter.level,
            order=index,
            source_refs=[
                {
                    "source_file": parsed.source_file,
                    "page_start": parsed.page_start,
                    "page_end": parsed.page_end,
                    "heading": chapter.title,
                }
            ],
        )
        db.add(node)
        db.flush()
        chapter_map[(chapter.level, chapter.title)] = node.id

    for kp in parsed.knowledge_points:
        chapter_id = chapter_map.get((1, kp.chapter_title)) or (
            next(iter(chapter_map.values())) if chapter_map else None
        )
        db.add(
            KnowledgePoint(
                project_id=project_id,
                document_id=document.id,
                chapter_id=chapter_id,
                title=kp.title,
                body_md=kp.body_md,
                source_refs=kp.source_refs,
                confidence=kp.confidence,
                status="raw",
                order=kp.order,
                locked=False,
            )
        )
    db.commit()
    return {
        "document_id": document.id,
        "chapter_count": len(parsed.chapters),
        "knowledge_point_count": len(parsed.knowledge_points),
    }
