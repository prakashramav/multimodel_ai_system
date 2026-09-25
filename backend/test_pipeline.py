import asyncio
from pathlib import Path
from backend.app.db.database import init_db, AsyncSessionLocal
from backend.app.db.models import Document, ExtractedField, ExtractedTable
from backend.app.core.storage import storage
from backend.app.services.pipeline import pipeline
from sqlalchemy import select

async def test_run():
    print("Initializing database...")
    await init_db()

    sample_dir = Path("backend/sample_data")
    sample_invoice = sample_dir / "sample_invoice.pdf"

    if not sample_invoice.exists():
        print("Sample invoice missing!")
        return

    # Ingest sample
    with open(sample_invoice, "rb") as f:
        content = f.read()

    rel_path = "uploads/sample_invoice.pdf"
    await storage.save_file(content, rel_path)

    async with AsyncSessionLocal() as session:
        doc = Document(
            filename="sample_invoice.pdf",
            file_path=rel_path,
            mime_type="application/pdf",
            file_size=len(content),
            status="processing",
            current_stage="ingest"
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        doc_id = doc.id
        print(f"Created doc record: {doc_id}")

    # Run pipeline
    print("Running pipeline...")
    async with AsyncSessionLocal() as session:
        await pipeline.run_pipeline(doc_id, session)

    # Inspect results
    async with AsyncSessionLocal() as session:
        stmt = select(Document).where(Document.id == doc_id)
        res = await session.execute(stmt)
        d = res.scalar_one()
        print(f"\nPipeline Output for Document {d.id}:")
        print(f"Type: {d.type} (confidence={d.type_confidence})")
        print(f"Status: {d.status}")
        print(f"Stage: {d.current_stage}")
        print(f"Flagged fields count: {d.flagged_count}")
        print(f"Message: {d.stage_message}")

        f_stmt = select(ExtractedField).where(ExtractedField.document_id == doc_id)
        f_res = await session.execute(f_stmt)
        fields = f_res.scalars().all()
        print(f"\nExtracted Fields ({len(fields)} items):")
        for f in fields[:6]:
            print(f" - [{f.section}] {f.field_label}: {f.value} (conf={f.confidence}, flagged={f.flagged})")

        t_stmt = select(ExtractedTable).where(ExtractedTable.document_id == doc_id)
        t_res = await session.execute(t_stmt)
        tables = t_res.scalars().all()
        print(f"\nExtracted Tables ({len(tables)} tables):")
        for t in tables:
            print(f" Table: {t.table_name}, {len(t.rows)} rows, columns: {t.columns}")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_run())
