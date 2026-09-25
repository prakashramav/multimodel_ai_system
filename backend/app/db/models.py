import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), default="application/pdf")
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    
    # Classification result
    type = Column(String(50), default="other") # invoice, resume, receipt, contract, form, other
    type_confidence = Column(Float, default=0.0)
    type_reasoning = Column(Text, nullable=True)
    
    # Processing state & Human Review routing
    status = Column(String(50), default="pending") # pending, processing, auto_approved, needs_review, failed
    current_stage = Column(String(50), default="idle") # idle, ingest, preprocess, classify, extract_fields, extract_tables, review_routing, completed, failed
    stage_message = Column(String(255), default="Document uploaded")
    flagged_count = Column(Integer, default=0)
    
    uploaded_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan", order_by="DocumentPage.page_number")
    fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("ExtractedTable", back_populates="document", cascade="all, delete-orphan")
    qa_history = relationship("QAHistory", back_populates="document", cascade="all, delete-orphan", order_by="QAHistory.created_at.asc()")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "page_count": self.page_count,
            "type": self.type,
            "type_confidence": self.type_confidence,
            "type_reasoning": self.type_reasoning,
            "status": self.status,
            "current_stage": self.current_stage,
            "stage_message": self.stage_message,
            "flagged_count": self.flagged_count,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class DocumentPage(Base):
    __tablename__ = "pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String(512), nullable=False)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    ocr_text = Column(Text, default="")
    ocr_data = Column(JSON, default=dict)

    document = relationship("Document", back_populates="pages")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "image_path": self.image_path,
            "width": self.width,
            "height": self.height,
            "ocr_text": self.ocr_text,
        }

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(100), nullable=False)
    value = Column(Text, default="")
    confidence = Column(Float, default=1.0)
    bbox = Column(JSON, nullable=True) # {"ymin": ..., "xmin": ..., "ymax": ..., "xmax": ..., "page": 1}
    page_number = Column(Integer, default=1)
    section = Column(String(100), default="General")
    reviewed = Column(Boolean, default=False)
    flagged = Column(Boolean, default=False)
    original_value = Column(Text, nullable=True)
    correction_notes = Column(Text, nullable=True)

    document = relationship("Document", back_populates="fields")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "field_name": self.field_name,
            "field_label": self.field_label,
            "value": self.value,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "page_number": self.page_number,
            "section": self.section,
            "reviewed": self.reviewed,
            "flagged": self.flagged,
            "original_value": self.original_value,
            "correction_notes": self.correction_notes,
        }

class ExtractedTable(Base):
    __tablename__ = "extracted_tables"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    table_name = Column(String(100), nullable=False)
    columns = Column(JSON, default=list) # e.g. ["Item Description", "Qty", "Unit Price", "Total"]
    rows = Column(JSON, default=list) # e.g. [{"description": "Cloud hosting", "qty": 1, ...}]
    page_number = Column(Integer, default=1)
    confidence = Column(Float, default=1.0)

    document = relationship("Document", back_populates="tables")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "table_name": self.table_name,
            "columns": self.columns,
            "rows": self.rows,
            "page_number": self.page_number,
            "confidence": self.confidence,
        }

class QAHistory(Base):
    __tablename__ = "qa_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    grounded_sources = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    document = relationship("Document", back_populates="qa_history")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "question": self.question,
            "answer": self.answer,
            "grounded_sources": self.grounded_sources,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
