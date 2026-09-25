import io
import csv
import json
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.db.database import get_db, AsyncSessionLocal
from backend.app.db.models import Document, DocumentPage, ExtractedField, ExtractedTable, QAHistory
from backend.app.core.storage import storage
from backend.app.core.config import settings
from backend.app.services.pipeline import pipeline

router = APIRouter(prefix="/documents", tags=["documents"])

async def run_pipeline_task(document_id: str):
    async with AsyncSessionLocal() as session:
        await pipeline.run_pipeline(document_id, session)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Uploads a document (PDF, PNG, JPG) and triggers background pipeline."""
    filename = file.filename
    ext = Path(filename).suffix.lower()
    
    allowed = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".webp"]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Supported: {', '.join(allowed)}")

    # Read content
    content = await file.read()
    file_size = len(content)

    # Save to storage
    rel_path = f"uploads/{filename}"
    await storage.save_file(content, rel_path)

    # Create document record
    doc = Document(
        filename=filename,
        file_path=rel_path,
        mime_type=file.content_type or ("application/pdf" if ext == ".pdf" else "image/png"),
        file_size=file_size,
        status="processing",
        current_stage="ingest",
        stage_message="File ingested, queuing processing pipeline..."
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Kick off background task
    background_tasks.add_task(run_pipeline_task, doc.id)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": "Upload successful. Extraction pipeline started."
    }

@router.post("/seed-sample/{sample_type}")
async def seed_sample_document(
    sample_type: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Instantly seeds and processes one of the pre-built sample documents (invoice, resume, receipt)."""
    valid_samples = {
        "invoice": "sample_invoice.pdf",
        "resume": "sample_resume.pdf",
        "receipt": "sample_receipt.pdf"
    }

    if sample_type not in valid_samples:
        raise HTTPException(status_code=400, detail=f"Invalid sample type. Choose: {list(valid_samples.keys())}")

    filename = valid_samples[sample_type]
    sample_path = Path(__file__).resolve().parent.parent.parent / "sample_data" / filename

    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file {filename} not found.")

    with open(sample_path, "rb") as f:
        content = f.read()

    rel_path = f"uploads/{filename}"
    await storage.save_file(content, rel_path)

    doc = Document(
        filename=filename,
        file_path=rel_path,
        mime_type="application/pdf",
        file_size=len(content),
        status="processing",
        current_stage="ingest",
        stage_message=f"Seeding demo {sample_type} document..."
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    background_tasks.add_task(run_pipeline_task, doc.id)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": f"Sample {sample_type} seeded. Pipeline running."
    }

@router.get("")
async def list_documents(
    doc_type: Optional[str] = Query(None, alias="type"),
    status: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Lists all documents with optional filtering by type or status."""
    stmt = select(Document).order_by(desc(Document.uploaded_at))
    if doc_type:
        stmt = stmt.where(Document.type == doc_type)
    if status:
        stmt = stmt.where(Document.status == status)

    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    docs = res.scalars().all()

    return [d.to_dict() for d in docs]

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves real-time stage progress of document pipeline."""
    stmt = select(Document).where(Document.id == doc_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "status": doc.status,
        "current_stage": doc.current_stage,
        "stage_message": doc.stage_message,
        "type": doc.type,
        "type_confidence": doc.type_confidence,
        "flagged_count": doc.flagged_count,
        "page_count": doc.page_count
    }

@router.get("/{doc_id}")
async def get_document_detail(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Returns full document details, pages, extracted fields grouped by section, and tables."""
    stmt = select(Document).where(Document.id == doc_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Fetch pages
    p_stmt = select(DocumentPage).where(DocumentPage.document_id == doc_id).order_by(DocumentPage.page_number)
    p_res = await db.execute(p_stmt)
    pages = p_res.scalars().all()

    # Fetch fields
    f_stmt = select(ExtractedField).where(ExtractedField.document_id == doc_id)
    f_res = await db.execute(f_stmt)
    fields = f_res.scalars().all()

    # Fetch tables
    t_stmt = select(ExtractedTable).where(ExtractedTable.document_id == doc_id)
    t_res = await db.execute(t_stmt)
    tables = t_res.scalars().all()

    # Group fields by section
    sections: dict[str, list] = {}
    for f in fields:
        sec = f.section or "General"
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(f.to_dict())

    return {
        "document": doc.to_dict(),
        "pages": [p.to_dict() for p in pages],
        "fields": [f.to_dict() for f in fields],
        "sections": sections,
        "tables": [t.to_dict() for t in tables]
    }

@router.patch("/{doc_id}/fields/{field_id}")
async def update_field_value(
    doc_id: str,
    field_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Inline correction for an extracted field.
    Updates value, marks reviewed=True, clears flagged status,
    and updates parent document status if all flagged fields are resolved.
    """
    stmt = select(ExtractedField).where(
        ExtractedField.id == field_id,
        ExtractedField.document_id == doc_id
    )
    res = await db.execute(stmt)
    field = res.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    if "value" in payload:
        field.value = str(payload["value"])
    if "notes" in payload:
        field.correction_notes = str(payload["notes"])

    field.reviewed = True
    field.flagged = False
    await db.commit()

    # Re-evaluate remaining flagged fields for document
    remaining_flagged_stmt = select(ExtractedField).where(
        ExtractedField.document_id == doc_id,
        ExtractedField.flagged == True
    )
    remaining_res = await db.execute(remaining_flagged_stmt)
    remaining_flagged = remaining_res.scalars().all()

    doc_stmt = select(Document).where(Document.id == doc_id)
    doc_res = await db.execute(doc_stmt)
    doc = doc_res.scalar_one_or_none()
    if doc:
        doc.flagged_count = len(remaining_flagged)
        if len(remaining_flagged) == 0 and doc.status == "needs_review":
            doc.status = "auto_approved"
            doc.stage_message = "All flagged fields reviewed and verified by user."
        await db.commit()

    return {
        "field": field.to_dict(),
        "remaining_flagged_count": len(remaining_flagged),
        "document_status": doc.status if doc else "auto_approved"
    }

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes document and associated pages and files."""
    stmt = select(Document).where(Document.id == doc_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await storage.delete_file(doc.file_path)
    await db.delete(doc)
    await db.commit()

    return {"message": "Document deleted successfully"}

@router.get("/{doc_id}/export")
async def export_document(
    doc_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: AsyncSession = Depends(get_db)
):
    """Exports structured extracted data as JSON or CSV."""
    stmt = select(Document).where(Document.id == doc_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    f_stmt = select(ExtractedField).where(ExtractedField.document_id == doc_id)
    f_res = await db.execute(f_stmt)
    fields = f_res.scalars().all()

    t_stmt = select(ExtractedTable).where(ExtractedTable.document_id == doc_id)
    t_res = await db.execute(t_stmt)
    tables = t_res.scalars().all()

    if format == "json":
        export_data = {
            "document_id": doc.id,
            "filename": doc.filename,
            "document_type": doc.type,
            "type_confidence": doc.type_confidence,
            "status": doc.status,
            "fields": {f.field_name: f.value for f in fields},
            "detailed_fields": [f.to_dict() for f in fields],
            "tables": [t.to_dict() for t in tables]
        }
        json_str = json.dumps(export_data, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={Path(doc.filename).stem}_extracted.json"}
        )

    else:
        # CSV Export (Fields and Tables)
        output = io.StringIO()
        writer = csv.writer(output)

        # Section 1: Metadata
        writer.writerow(["DOCUMENT METADATA"])
        writer.writerow(["ID", doc.id])
        writer.writerow(["Filename", doc.filename])
        writer.writerow(["Type", doc.type])
        writer.writerow(["Status", doc.status])
        writer.writerow([])

        # Section 2: Fields
        writer.writerow(["EXTRACTED FIELDS"])
        writer.writerow(["Field Name", "Label", "Section", "Value", "Confidence", "Reviewed"])
        for f in fields:
            writer.writerow([f.field_name, f.field_label, f.section, f.value, f.confidence, f.reviewed])
        writer.writerow([])

        # Section 3: Tables
        for t in tables:
            writer.writerow([f"TABLE: {t.table_name.upper()}"])
            writer.writerow(t.columns)
            for row in t.rows:
                row_vals = [row.get(col, row.get(col.lower().replace(" ", "_"), "")) for col in t.columns]
                writer.writerow(row_vals)
            writer.writerow([])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={Path(doc.filename).stem}_extracted.csv"}
        )
