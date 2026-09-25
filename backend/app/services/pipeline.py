import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.db.models import Document, DocumentPage, ExtractedField, ExtractedTable
from backend.app.services.ocr_service import ocr_service
from backend.app.services.classification_service import classification_service
from backend.app.services.extraction_service import extraction_service
from backend.app.services.table_service import table_service
from backend.app.schemas.registry import get_schema_for_type

logger = logging.getLogger("docintel.pipeline")

class DocumentPipeline:
    async def run_pipeline(self, document_id: str, db: AsyncSession):
        """
        Executes the full 8-step multimodal extraction pipeline for a document.
        """
        logger.info(f"Starting extraction pipeline for document_id={document_id}")
        
        # 1. Fetch document record
        stmt = select(Document).where(Document.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            logger.error(f"Document {document_id} not found in database")
            return

        try:
            # Stage 1: Ingest
            doc.status = "processing"
            doc.current_stage = "ingest"
            doc.stage_message = "Ingesting and validating document file format"
            await db.commit()

            file_full_path = await storage.get_file_path(doc.file_path)

            # Stage 2: Preprocess (Rasterize & OCR)
            doc.current_stage = "preprocess"
            doc.stage_message = "Rasterizing pages and extracting text layer"
            await db.commit()

            pages_data = await ocr_service.rasterize_and_extract(
                file_path=file_full_path,
                doc_id=doc.id,
                mime_type=doc.mime_type
            )

            # Persist pages
            doc.page_count = len(pages_data)
            for p in pages_data:
                page_record = DocumentPage(
                    document_id=doc.id,
                    page_number=p["page_number"],
                    image_path=p["image_path"],
                    width=p["width"],
                    height=p["height"],
                    ocr_text=p["ocr_text"],
                    ocr_data=p.get("ocr_data", {})
                )
                db.add(page_record)
            await db.commit()

            first_page_img = pages_data[0]["image_path"] if pages_data else ""
            combined_ocr_text = "\n".join([p["ocr_text"] for p in pages_data])

            # Stage 3: Classification
            doc.current_stage = "classify"
            doc.stage_message = "Multimodal classification via vision AI"
            await db.commit()

            classification = await classification_service.classify_document(
                first_page_rel_path=first_page_img,
                extracted_text=combined_ocr_text,
                filename=doc.filename
            )

            doc.type = classification.document_type
            doc.type_confidence = classification.confidence
            doc.type_reasoning = classification.reasoning
            await db.commit()

            # Stage 4: Schema Selection
            schema_info = get_schema_for_type(doc.type)

            # Stage 5: Structured Extraction
            doc.current_stage = "extract_fields"
            doc.stage_message = f"Extracting structured fields for {doc.type.upper()}"
            await db.commit()

            extracted_fields = await extraction_service.extract_fields(
                doc_type=doc.type,
                pages_info=pages_data,
                filename=doc.filename
            )

            # Stage 6: Table Extraction
            doc.current_stage = "extract_tables"
            doc.stage_message = "Detecting tabular regions and row structures"
            await db.commit()

            extracted_tables = await table_service.extract_tables(
                doc_type=doc.type,
                pages_info=pages_data,
                filename=doc.filename
            )

            # Stage 7: Review Routing & Persistence
            doc.current_stage = "review_routing"
            doc.stage_message = "Evaluating confidence scores and review queues"
            await db.commit()

            flagged_count = 0
            threshold = settings.CONFIDENCE_THRESHOLD

            for f in extracted_fields:
                is_flagged = f.confidence < threshold
                if is_flagged:
                    flagged_count += 1

                field_record = ExtractedField(
                    document_id=doc.id,
                    field_name=f.field_name,
                    field_label=f.field_label,
                    value=str(f.value) if f.value is not None else "",
                    confidence=f.confidence,
                    bbox=f.bbox.dict() if f.bbox else None,
                    page_number=f.page_number,
                    section=f.section,
                    reviewed=False,
                    flagged=is_flagged,
                    original_value=str(f.value) if f.value is not None else "",
                    correction_notes=""
                )
                db.add(field_record)

            for t in extracted_tables:
                table_record = ExtractedTable(
                    document_id=doc.id,
                    table_name=t.table_name,
                    columns=t.columns,
                    rows=t.rows,
                    page_number=t.page_number,
                    confidence=t.confidence
                )
                db.add(table_record)

            # Document status
            doc.flagged_count = flagged_count
            if flagged_count > 0:
                doc.status = "needs_review"
                doc.stage_message = f"Processing complete. {flagged_count} low-confidence field(s) routed to Needs Review."
            else:
                doc.status = "auto_approved"
                doc.stage_message = "Processing complete. All fields meet confidence threshold (Auto-Approved)."

            doc.current_stage = "completed"
            await db.commit()
            logger.info(f"Pipeline finished for document {document_id} with status={doc.status}")

        except Exception as e:
            logger.exception(f"Error during pipeline execution for {document_id}: {e}")
            doc.status = "failed"
            doc.current_stage = "failed"
            doc.stage_message = f"Pipeline execution failed: {str(e)}"
            await db.commit()

pipeline = DocumentPipeline()
