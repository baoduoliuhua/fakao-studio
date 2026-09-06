from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = "法考讲义项目"


class ProjectOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    document_id: int
    chapter_count: int
    knowledge_point_count: int


class ChapterOut(BaseModel):
    id: int
    parent_id: int | None
    title: str
    level: int
    order: int
    source_refs: list[dict[str, Any]] = []

    model_config = {"from_attributes": True}


class KnowledgePointSummary(BaseModel):
    id: int
    chapter_id: int | None
    title: str
    confidence: str
    status: str
    locked: bool
    order: int
    generated: bool

    model_config = {"from_attributes": True}


class KnowledgePointDetail(BaseModel):
    id: int
    project_id: int
    document_id: int
    chapter_id: int | None
    title: str
    body_md: str
    source_refs: list[dict[str, Any]] = []
    confidence: str
    status: str
    locked: bool
    order: int
    artifact: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class KnowledgePointUpdate(BaseModel):
    title: str | None = None
    body_md: str | None = None
    confidence: str | None = None
    locked: bool | None = None


class SplitRequest(BaseModel):
    boundary: str


class MergeRequest(BaseModel):
    knowledge_point_ids: list[int] = Field(min_length=2)


class ProgressUpdate(BaseModel):
    last_knowledge_point_id: int | None = None
    completed_ids: list[int] = []


class SettingsOut(BaseModel):
    mock: bool
    base_url: str
    api_key_set: bool
    model: str


class SettingsUpdate(BaseModel):
    mock: bool = True
    base_url: str = "https://api.deepseek.com/v1"
    api_key: str | None = None
    model: str = "deepseek-chat"
