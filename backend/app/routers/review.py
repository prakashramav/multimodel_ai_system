from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.db.database import get_db
from backend.app.db.models import Document, ExtractedField, DocumentPage

router = APIRouter(prefix="/review-queue", tags=["review"])

@router.get("")
async def get_review_queue(
    doc_type: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all documents and flagged fields that require human review.
    Grouped by document for fast triage.
    """
    # Find documents with status 'needs_review' or flagged_count > 0
    stmt = (
        select(Document)
        .where(Document.flagged_count > 0)
        .order_by(desc(Document.uploaded_at))
    )
    if doc_type:
        stmt = stmt.where(Document.type == doc_type)

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    docs = res.scalars().all()

    queue_items = []
    for doc in docs:
        # Get flagged fields for this doc
        f_stmt = (
            select(ExtractedField)
            .where(
                ExtractedField.document_id == doc.id,
                ExtractedField.flagged == True
            )
            .order_by(ExtractedField.confidence.asc())
        )
        f_res = await db.execute(f_stmt)
        flagged_fields = f_res.scalars().all()

        # Get first page thumbnail image path
        p_stmt = (
            select(DocumentPage)
            .where(DocumentPage.document_id == doc.id)
            .order_by(DocumentPage.page_number.asc())
            .limit(1)
        )
        p_res = await db.execute(p_stmt)
        first_page = p_res.scalar_one_or_none()

        queue_items.append({
            "document": doc.to_dict(),
            "thumbnail_url": f"/api/pages/{first_page.image_path}" if first_page else None,
            "flagged_count": len(flagged_fields),
            "flagged_fields": [f.to_dict() for f in flagged_fields]
        })

    return queue_items
