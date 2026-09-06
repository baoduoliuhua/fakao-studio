from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Artifact, KnowledgePoint
from ..schemas import KnowledgePointDetail, KnowledgePointUpdate, MergeRequest, SplitRequest
from ..services.ai import generate_for_knowledge_point

router = APIRouter(prefix="/api/knowledge-points", tags=["knowledge-points"])


@router.get("/{knowledge_point_id}")
def get_knowledge_point(knowledge_point_id: int, db: Session = Depends(get_db)):
    kp = db.get(KnowledgePoint, knowledge_point_id)
    if not kp:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return _detail(kp)


@router.patch("/{knowledge_point_id}")
def update_knowledge_point(
    knowledge_point_id: int,
    payload: KnowledgePointUpdate,
    db: Session = Depends(get_db),
):
    kp = db.get(KnowledgePoint, knowledge_point_id)
    if not kp:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(kp, key, value)
    db.commit()
    db.refresh(kp)
    return _detail(kp)


@router.post("/{knowledge_point_id}/generate")
def generate(knowledge_point_id: int, db: Session = Depends(get_db)):
    kp = db.get(KnowledgePoint, knowledge_point_id)
    if not kp:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    result = generate_for_knowledge_point(kp)
    if kp.artifact:
        db.delete(kp.artifact)
        db.flush()
    db.add(
        Artifact(
            knowledge_point_id=kp.id,
            diagram=result["diagram"],
            explanation=result["explanation"],
            key_points=result.get("key_points", []),
            source_citations=result.get("source_citations", []),
            model=result.get("model", "mock"),
        )
    )
    kp.status = "generated"
    db.commit()
    db.refresh(kp)
    return _detail(kp)


@router.post("/{knowledge_point_id}/regenerate")
def regenerate(knowledge_point_id: int, db: Session = Depends(get_db)):
    return generate(knowledge_point_id, db)


@router.post("/split")
def split_knowledge_point(payload: SplitRequest, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Split is not implemented in this MVP")


@router.post("/merge")
def merge_knowledge_points(payload: MergeRequest, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Merge is not implemented in this MVP")


def _artifact_dict(artifact: Artifact | None) -> dict | None:
    if not artifact:
        return None
    return {
        "id": artifact.id,
        "diagram": artifact.diagram,
        "explanation": artifact.explanation,
        "key_points": artifact.key_points,
        "source_citations": artifact.source_citations,
        "model": artifact.model,
        "created_at": artifact.created_at.isoformat(),
    }


def _detail(kp: KnowledgePoint) -> dict:
    return {
        "id": kp.id,
        "project_id": kp.project_id,
        "document_id": kp.document_id,
        "chapter_id": kp.chapter_id,
        "title": kp.title,
        "body_md": kp.body_md,
        "source_refs": kp.source_refs or [],
        "confidence": kp.confidence,
        "status": kp.status,
        "locked": kp.locked,
        "order": kp.order,
        "artifact": _artifact_dict(kp.artifact),
    }
