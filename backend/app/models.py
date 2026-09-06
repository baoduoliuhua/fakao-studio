from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    chapters = relationship("ChapterNode", back_populates="project", cascade="all, delete-orphan")
    knowledge_points = relationship("KnowledgePoint", back_populates="project", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="project", uselist=False, cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    content_md = Column(Text, nullable=False)
    source_file = Column(String, nullable=True)
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="documents")
    knowledge_points = relationship("KnowledgePoint", back_populates="document", cascade="all, delete-orphan")


class ChapterNode(Base):
    __tablename__ = "chapter_nodes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("chapter_nodes.id"), nullable=True)
    title = Column(String, nullable=False)
    level = Column(Integer, default=1)
    order = Column(Integer, default=0)
    source_refs = Column(JSON, default=list)

    project = relationship("Project", back_populates="chapters")
    parent = relationship("ChapterNode", remote_side=[id])
    knowledge_points = relationship("KnowledgePoint", back_populates="chapter")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapter_nodes.id"), nullable=True)
    title = Column(String, nullable=False)
    body_md = Column(Text, default="")
    source_refs = Column(JSON, default=list)
    confidence = Column(String, default="high")
    status = Column(String, default="raw")
    order = Column(Integer, default=0)
    locked = Column(Boolean, default=False)

    project = relationship("Project", back_populates="knowledge_points")
    document = relationship("Document", back_populates="knowledge_points")
    chapter = relationship("ChapterNode", back_populates="knowledge_points")
    artifact = relationship("Artifact", back_populates="knowledge_point", uselist=False, cascade="all, delete-orphan")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    diagram = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)
    key_points = Column(JSON, default=list)
    source_citations = Column(JSON, default=list)
    model = Column(String, default="mock")
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="artifact")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    last_knowledge_point_id = Column(Integer, nullable=True)
    completed_ids = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="progress")
