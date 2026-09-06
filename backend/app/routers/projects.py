from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ChapterNode, KnowledgePoint, Progress, Project
from ..schemas import (
    ChapterOut,
    ImportResult,
    KnowledgePointDetail,
    KnowledgePointSummary,
    ProgressUpdate,
    ProjectCreate,
    ProjectOut,
)
from ..services.projects import import_document

router = APIRouter(prefix="/api", tags=["projects"])


@router.post("/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("/projects/{project_id}/import", response_model=ImportResult)
async def import_file(
    project_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not file.filename or not file.filename.lower().endswith((".md", ".markdown")):
        raise HTTPException(status_code=400, detail="Only Markdown files are supported")
    content = (await file.read()).decode("utf-8", errors="replace")
    return import_document(db, project_id, file.filename, content)


@router.get("/projects/{project_id}/outline")
def get_outline(project_id: int, db: Session = Depends(get_db)):
    chapters = (
        db.query(ChapterNode)
        .filter(ChapterNode.project_id == project_id)
        .order_by(ChapterNode.order, ChapterNode.id)
        .all()
    )
    knowledge_points = (
        db.query(KnowledgePoint)
        .filter(KnowledgePoint.project_id == project_id)
        .order_by(KnowledgePoint.order, KnowledgePoint.id)
        .all()
    )
    summaries = []
    for kp in knowledge_points:
        summaries.append(
            KnowledgePointSummary(
                id=kp.id,
                chapter_id=kp.chapter_id,
                title=kp.title,
                confidence=kp.confidence,
                status=kp.status,
                locked=kp.locked,
                order=kp.order,
                generated=kp.artifact is not None,
            ).model_dump()
        )
    return {
        "chapters": [ChapterOut.model_validate(c).model_dump() for c in chapters],
        "knowledge_points": summaries,
    }


@router.patch("/projects/{project_id}/progress")
def update_progress(
    project_id: int,
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
):
    progress = db.query(Progress).filter(Progress.project_id == project_id).first()
    if not progress:
        progress = Progress(project_id=project_id)
        db.add(progress)
    progress.last_knowledge_point_id = payload.last_knowledge_point_id
    progress.completed_ids = payload.completed_ids
    db.commit()
    return {"ok": True}
