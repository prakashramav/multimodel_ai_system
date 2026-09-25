# DocIntel — Multimodal AI Document Intelligence Platform

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_Vision-4285F4?style=flat&logo=google)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38bdf8?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat)](https://www.sqlalchemy.org/)

DocIntel is a full-stack, multimodal document processing and intelligence platform. It processes complex uploaded documents (invoices, resumes, contracts, receipts, forms, scanned PDFs) to deliver structured extraction with spatial bounding boxes, tabular data parsing, automatic document classification, grounded document Q&A, and a dedicated human-in-the-loop review workflow for low-confidence fields.

---

## The Problem Statement

Traditional Optical Character Recognition (OCR) and document extraction pipelines suffer from critical flaws that prevent them from operating reliably in enterprise environments:

1. **Loss of 2D Spatial Layout & Visual Context**: Traditional pipelines flatten documents into unstructured text strings before passing them to an LLM. In this process, essential spatial cues—such as column alignments, table borders, key-value proximity, stamps, signatures, and visual hierarchy—are completely lost.
2. **Brittle Extraction & Hallucinations**: Prompting an LLM with raw text and hoping for well-formed JSON often leads to schema drift, missing fields, or hallucinated values that corrupt downstream databases (ERPs, CRMs, ATS).
3. **No Visual Auditability**: Users are presented with extracted data without any verifiable connection to where that data originated on the source page. Manually verifying extracted figures against a 10-page document requires tedious searching.
4. **Lack of Confidence Routing & Human-in-the-Loop Oversight**: In typical systems, errors go unnoticed until downstream operations fail. Without per-field confidence scoring and automated review routing, enterprises are forced to either manually verify 100% of fields or risk catastrophic data inaccuracies.
5. **Flattened Tabular Data**: Complex multi-row line items (e.g. invoice billing breakdowns, candidate work histories) are frequently mangled into loose text rather than preserved as queryable, editable relational tables.

---

## What We Are Solving

DocIntel re-engineers document processing from the ground up by combining **multimodal vision AI**, **strict schema enforcement**, **spatial bounding box mapping**, and **human-in-the-loop verification**:

- **Multimodal Visual Reasoning**: High-resolution page images are rasterized and passed directly to vision-capable LLMs (Google Gemini 2.5 / 1.5 Flash) alongside OCR text. The model "sees" the document layout as a human would, understanding visual headers, tables, logos, and spatial groupings.
- **Strict Pydantic Schema & Tool-Use Enforcement**: Extractions are strictly constrained using defined Pydantic models per document type (`invoice`, `resume`, `receipt`, `contract`, etc.). The model must return typed fields conforming to the schema specification.
- **Bidirectional Visual Grounding**: Every extracted field includes normalized bounding box coordinates (`[ymin, xmin, ymax, xmax]`). In the workspace split-view, hovering over any field lights up its exact location on the document page image, and clicking a bounding box focuses the corresponding field.
- **Automated Human Review Queue**: Every extracted field carries a confidence score (`0.0` to `1.0`). Any field falling below the configurable threshold (e.g. `0.75`) is flagged, and the document is routed to a triage **Review Queue**. Reviewers can verify or correct fields inline with full audit trail history. Once resolved, the document status updates to `auto_approved`.
- **Interactive Tabular Extraction**: Tabular regions are rendered as editable grid components, allowing users to modify cells, add/delete rows, and export tables directly to CSV.
- **Strictly Grounded Document Q&A**: A slide-out conversational drawer answers ad-hoc questions grounded strictly in the document text and structured fields, citing specific line items or sections to prevent hallucinations.

---

## System Architecture

```mermaid
graph TD
    A[User Document Upload / PDF / Scanned Image] --> B[Ingestion & Storage Service]
    B --> C[PyMuPDF / pdfium Page Rasterization]
    C --> D[OCR & Text-Layer Extraction]
    D --> E[Multimodal Vision Classification]
    E --> F{Schema Registry}
    F -->|Invoice| G1[Invoice Schema & Tool Spec]
    F -->|Resume| G2[Resume Schema & Tool Spec]
    F -->|Receipt| G3[Receipt Schema & Tool Spec]
    F -->|Contract| G4[Contract Schema & Tool Spec]
    G1 & G2 & G3 & G4 --> H[Multimodal Structured Extraction]
    H --> I[Tabular Region Parsing]
    I --> J[Confidence Evaluation & Review Routing]
    J -->|Confidence >= 0.75| K[Status: Auto-Approved]
    J -->|Confidence < 0.75| L[Status: Needs Review -> Human Triage Queue]
    K & L --> M[(PostgreSQL / SQLite Database)]
    M --> N[Next.js Split-View Workspace]
    N --> O[Interactive Bounding Box Overlays]
    N --> P[Editable Tabular View]
    N --> Q[Grounded Q&A Engine]
    N --> R[JSON & CSV Export Engine]
```

---

## 8-Stage Extraction Pipeline

1. **Ingest**: File format validation (PDF, PNG, JPG, TIFF, WebP), stored to disk / S3-ready storage layer. Document record initialized.
2. **Preprocess**: Each page is rasterized to a high-DPI image (`144-150 DPI`) for crisp vision LLM reasoning. The native text layer is extracted via `pypdf`, with Tesseract OCR fallback for scanned pages.
3. **Classification**: Multimodal vision analyzes page 1 visual structure and text to classify the document into fixed taxonomy (`invoice`, `resume`, `receipt`, `contract`, `form`, `other`) with reasoning.
4. **Schema Selection**: The classification type dynamically selects the Pydantic schema and tool definition from the registry.
5. **Structured Extraction**: Google Gemini Vision receives the page images and text context, returning typed structured fields, normalized spatial bounding boxes, and per-field confidence scores.
6. **Table Extraction**: A dedicated pass parses tabular regions (e.g. line items, work experience) into row objects.
7. **Review Routing**: Fields with confidence below `CONFIDENCE_THRESHOLD` (e.g. `0.75`) are flagged. Document status is set to `needs_review` or `auto_approved`.
8. **Persist & Audit**: Fields, tables, bounding boxes, original values, and metadata are saved to the database.

---

## Interactive Workspace & Feature Highlights

### 1. Split-View Document Workspace (`/documents/[id]`)
- **Left Pane (PageViewer)**: High-performance canvas viewer with zoom controls (`60%` to `250%`), pan navigation, multi-page thumbnail rail, and clickable bounding box overlays.
- **Right Pane (Extracted Fields & Tables)**:
  - Fields grouped by schema sections (e.g. `Vendor Details`, `Invoice Details`, `Totals & Financials`).
  - Calm confidence indicators (green dot `≥ 85%`, sky dot `75–84%`, amber dot `< 75%`).
  - Monospace formatting for scanned numeric/ID values.
  - Inline edit-in-place control with audit history tracking.
- **Interactive Tables**: Interactive data grid for line items, work history, and receipt items with cell editing, row additions, and CSV export.

### 2. Human-in-the-Loop Review Queue (`/review`)
- Dedicated triage dashboard displaying all documents with low-confidence fields.
- Fast inline correction and one-click *"Verify Correct"* approval.
- Direct jump link to view any flagged field in context with its source bounding box highlighted.

### 3. Grounded Document Q&A Drawer
- Free-form natural language querying against the document.
- One-click suggested prompts based on document type (e.g. *"What is the payment due date?"*, *"What are the primary technical skills?"*).
- Grounded strictly in extracted content with exact citations.

### 4. Zero-API-Key Demo & Fixture Mode
- Pre-built high-fidelity sample fixtures for **Invoices**, **Resumes**, and **Receipts**.
- Instant test buttons to seed and evaluate the full extraction, table parsing, and human review workflow without consuming API credits.

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
│   │   │   ├── invoice.py      # Invoice schema sections & Gemini Vision spec
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

---

## License

MIT License. Designed and built as a modern multimodal AI document intelligence platform.
