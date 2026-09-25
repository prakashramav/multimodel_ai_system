# DocIntel — Multimodal AI Document Intelligence Platform

DocIntel is a full-stack, multimodal document processing and intelligence platform. It processes uploaded documents (invoices, resumes, contracts, receipts, forms, scanned PDFs) to deliver structured extraction with spatial bounding boxes, tabular data parsing, automatic document classification, grounded document Q&A, and a dedicated human-in-the-loop review workflow for low-confidence fields.

---

## Architecture & Technology Stack

- **Frontend**: Next.js 14+ (App Router), JavaScript, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI (Python 3.10+ / 3.14 compatible), async endpoints with SQLAlchemy 2.0
- **Multimodal Vision & LLM**: Claude 3.5 / 3.7 Sonnet (Anthropic Vision API) with tool-use JSON schema enforcement. Built-in high-fidelity mock fixture mode for zero-API-key testing out of the box.
- **OCR & Rasterization**: High-resolution rasterization via `pypdfium2` / `Pillow` (hardware accelerated, no external poppler binary required on Windows) + `pypdf` text-layer extraction + Tesseract fallback.
- **Database**: PostgreSQL via asyncpg or instant SQLite (`aiosqlite`) + Alembic migrations.
- **File Storage**: Local disk storage structured with an abstract provider interface so S3 is a drop-in swap.
- **Human-in-the-Loop**: Configurable confidence threshold (default `0.75`). Low-confidence fields are routed to a triage review queue with inline correction and audit history.

---

## Project Structure

```
multimodal_AI_system/
├── backend/
│   ├── alembic/                # Alembic migration scripts
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic BaseSettings & env configs
│   │   │   └── storage.py      # Abstract storage interface & local disk provider
│   │   ├── db/
│   │   │   ├── database.py     # SQLAlchemy async engine & session maker
│   │   │   └── models.py       # Document, DocumentPage, ExtractedField, ExtractedTable, QAHistory
│   │   ├── schemas/
│   │   │   ├── base.py         # Base BoundingBox, ExtractedField, Table schemas
│   │   │   ├── invoice.py      # Invoice schema sections & Claude Vision tool spec
│   │   │   ├── resume.py       # Resume schema sections & tool spec
│   │   │   ├── receipt.py      # Store receipt schema & tool spec
│   │   │   ├── contract.py     # Legal contract schema & tool spec
│   │   │   └── registry.py     # Unified document type registry
│   │   ├── services/
│   │   │   ├── ocr_service.py              # PDF rasterization & OCR text extraction
│   │   │   ├── classification_service.py   # Multimodal document classification
│   │   │   ├── extraction_service.py       # Structured extraction with tool-use
│   │   │   ├── table_service.py            # Line items & tabular parsing
│   │   │   ├── qa_service.py               # Grounded Q&A with document citations
│   │   │   ├── mock_engine.py              # High-fidelity fixture & heuristic engine
│   │   │   └── pipeline.py                 # Master 8-stage document pipeline
│   │   ├── routers/
│   │   │   ├── documents.py    # Upload, status, detail, inline correction, export
│   │   │   ├── review.py       # Human review queue endpoints
│   │   │   └── qa.py           # Grounded document Q&A endpoints
│   │   └── main.py             # FastAPI entrypoint, CORS, static page image server
│   ├── sample_data/            # Sample Invoice, Resume, and Receipt PDFs & PNGs
│   ├── storage/                # Local uploaded documents and rasterized pages
│   ├── requirements.txt
│   ├── test_pipeline.py        # CLI end-to-end pipeline test script
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── globals.css         # Tailwind dark theme tokens & highlight animations
│   │   ├── layout.js           # Root layout with navigation bar
│   │   ├── page.js             # Main dashboard, upload dropzone, metrics, recent docs
│   │   ├── review/page.js      # Human-in-the-loop review queue page
│   │   └── documents/[id]/page.js # Split-view workspace (PageViewer + Fields + Tables + Q&A)
│   ├── components/
│   │   ├── Navbar.jsx          # Brand header with demo seeds & review queue counter
│   │   ├── UploadDropzone.jsx  # Drag-and-drop file upload & sample triggers
│   │   ├── DocumentList.jsx    # Filterable documents library
│   │   ├── PageViewer.jsx      # Zoom/pan viewer with BoundingBoxOverlay
│   │   ├── ExtractedFieldsPanel.jsx # Grouped section accordions & search
│   │   ├── FieldRow.jsx        # Individual field row with calm confidence dot & inline edit
│   │   ├── TableExtractionView.jsx  # Interactive editable table component with CSV export
│   │   ├── DocumentQAPanel.jsx # Slide-out grounded Q&A drawer with citation tags
│   │   ├── ClassificationBadge.jsx  # Compact type & confidence pill
│   │   └── ExportMenu.jsx      # JSON & CSV export dropdown
│   └── package.json
└── README.md
```

---

## Quickstart & Local Setup

### 1. Backend Setup (FastAPI)

```bash
# Navigate to project root
cd multimodal_AI_system

# Install Python dependencies
python -m pip install -r backend/requirements.txt

# Configure environment (works out-of-the-box with SQLite dev default)
copy backend\.env.example backend\.env
```

#### Running the Backend Server:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000` (Swagger docs at `http://127.0.0.1:8000/docs`).

---

### 2. Frontend Setup (Next.js)

```bash
# Navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Run the development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 3. PostgreSQL & Alembic Migrations (Production Setup)

By default, the platform runs on SQLite (`sqlite+aiosqlite:///./docintel.db`) with zero setup required.
To switch to PostgreSQL:

1. Update `backend/.env`:
```ini
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/docintel
```

2. Run Alembic migrations:
```bash
python -m alembic upgrade head
```

To create a new migration after modifying database models:
```bash
python -m alembic revision --autogenerate -m "add_new_columns"
```

---

## Pipeline Specification

When a document is uploaded, it runs through an asynchronous 8-stage pipeline:

1. **Ingest**: File validated and saved to storage. Document record created with `status: processing`.
2. **Preprocess**: Each page is rasterized to high-res PNG image (`144-150 DPI`). Text layer and spatial coordinates extracted.
3. **Classification**: Multimodal vision call analyzes page 1 layout and text to classify into `invoice`, `resume`, `receipt`, `contract`, `form`, or `other` with reasoning.
4. **Schema Selection**: Schema registry binds corresponding Pydantic schema sections and Claude tool specification.
5. **Structured Extraction**: Claude Vision extracts key-value fields with normalized `[ymin, xmin, ymax, xmax]` bounding boxes and per-field confidence scores `(0.0 - 1.0)`.
6. **Table Extraction**: Tabular regions (e.g. Line Items, Work History, Purchased Items) parsed into row objects.
7. **Review Routing**: Fields with confidence below `CONFIDENCE_THRESHOLD` (e.g. `0.75`) are flagged. Document status routes to `needs_review` or `auto_approved`.
8. **Persist**: Document, pages, fields, and tables persisted with full audit history.

---

## API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload PDF/image and launch extraction pipeline |
| `POST` | `/api/documents/seed-sample/{type}` | Instantly seed and run sample fixture (`invoice`, `resume`, `receipt`) |
| `GET` | `/api/documents` | List documents with filtering by type, status, and search |
| `GET` | `/api/documents/{id}/status` | Real-time stage progress (`ingest` → `classify` → `extract` → `done`) |
| `GET` | `/api/documents/{id}` | Full document detail: pages, fields grouped by section, tables |
| `PATCH` | `/api/documents/{id}/fields/{field_id}` | Human review correction: updates value, marks reviewed, clears flag |
| `POST` | `/api/documents/{id}/ask` | Grounded document Q&A with citations |
| `GET` | `/api/documents/{id}/qa-history` | Conversation history for document Q&A |
| `GET` | `/api/documents/{id}/export?format=json\|csv` | Structured data export |
| `GET` | `/api/review-queue` | Documents and flagged fields requiring human verification |
| `GET` | `/api/pages/{subpath}` | Rendered document page images for viewer |
| `GET` | `/api/health` | Service health check |

---

## Testing CLI Pipeline

To run an instant verification test of the extraction pipeline directly from CLI:
```bash
python -m backend.test_pipeline
```
