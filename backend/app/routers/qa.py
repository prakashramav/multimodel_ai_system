from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.database import get_db
from backend.app.db.models import Document, DocumentPage, ExtractedField, ExtractedTable, QAHistory
from backend.app.services.qa_service import qa_service

router = APIRouter(prefix="/documents", tags=["qa"])

@router.post("/{doc_id}/ask")
async def ask_document_question(
    doc_id: str,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Answers free-form questions grounded strictly in the document content.
    Returns answer, grounded sources, and saves query into QA history.
    """
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Fetch document
    d_stmt = select(Document).where(Document.id == doc_id)
    d_res = await db.execute(d_stmt)
    doc = d_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Fetch fields, tables, pages
    f_stmt = select(ExtractedField).where(ExtractedField.document_id == doc_id)
    f_res = await db.execute(f_stmt)
    fields = [f.to_dict() for f in f_res.scalars().all()]

    t_stmt = select(ExtractedTable).where(ExtractedTable.document_id == doc_id)
    t_res = await db.execute(t_stmt)
    tables = [t.to_dict() for t in t_res.scalars().all()]

    p_stmt = select(DocumentPage).where(DocumentPage.document_id == doc_id).order_by(DocumentPage.page_number)
    p_res = await db.execute(p_stmt)
    pages = [p.to_dict() for p in p_res.scalars().all()]

    answer, sources = await qa_service.answer_question(
        question=question,
        document_dict=doc.to_dict(),
        fields=fields,
        tables=tables,
        pages=pages
    )

    # Persist in QA history
    qa_record = QAHistory(
        document_id=doc.id,
        question=question,
        answer=answer,
        grounded_sources=sources
    )
    db.add(qa_record)
    await db.commit()
    await db.refresh(qa_record)

    return {
        "qa_id": qa_record.id,
        "document_id": doc.id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "created_at": qa_record.created_at.isoformat()
    }

@router.get("/{doc_id}/qa-history")
async def get_qa_history(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Returns conversation Q&A history for a document."""
    stmt = select(QAHistory).where(QAHistory.document_id == doc_id).order_by(QAHistory.created_at.asc())
    res = await db.execute(stmt)
    records = res.scalars().all()
    return [r.to_dict() for r in records]
