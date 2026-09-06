from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ChapterNode, Document, KnowledgePoint, Progress, Project
from ..schemas import ChapterCreate, ChapterUpdate

router = APIRouter(prefix="/api", tags=["chapters"])


@router.delete("/projects/{project_id}/content")
def clear_project_content(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.query(KnowledgePoint).filter(KnowledgePoint.project_id == project_id).delete()
    db.query(Document).filter(Document.project_id == project_id).delete()
    db.query(ChapterNode).filter(ChapterNode.project_id == project_id).delete()
    db.query(Progress).filter(Progress.project_id == project_id).delete()
    db.commit()
    return {"ok": True}


@router.post("/chapters")
def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)):
    project = db.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    max_order = (
        db.query(ChapterNode.order)
        .filter(ChapterNode.project_id == payload.project_id)
        .order_by(ChapterNode.order.desc())
        .first()
    )
    chapter = ChapterNode(
        project_id=payload.project_id,
        parent_id=payload.parent_id,
        title=payload.title,
        level=payload.level,
        order=(max_order[0] + 1) if max_order else 0,
        source_refs=[],
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return {"id": chapter.id, "title": chapter.title}


@router.patch("/chapters/{chapter_id}")
def update_chapter(
    chapter_id: int,
    payload: ChapterUpdate,
    db: Session = Depends(get_db),
):
    chapter = db.get(ChapterNode, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter.title = payload.title
    db.commit()
    db.refresh(chapter)
    return {"id": chapter.id, "title": chapter.title}


@router.delete("/chapters/{chapter_id}")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.get(ChapterNode, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(chapter)
    db.commit()
    return {"ok": True}
