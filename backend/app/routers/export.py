from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import KnowledgePoint, Project
from ..services.exporter import build_html, build_pdf

router = APIRouter(prefix="/api/projects", tags=["export"])


@router.get("/{project_id}/export")
def export_project(
    project_id: int,
    format: str = "html",
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    kps = (
        db.query(KnowledgePoint)
        .filter(KnowledgePoint.project_id == project_id)
        .order_by(KnowledgePoint.order, KnowledgePoint.id)
        .all()
    )
    if format == "pdf":
        try:
            pdf = build_pdf(project, kps)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"PDF export failed: {exc}") from exc
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{project.name}.pdf"'},
        )
    return HTMLResponse(
        content=build_html(project, kps),
        headers={"Content-Disposition": f'attachment; filename="{project.name}.html"'},
    )
