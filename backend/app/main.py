import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure repository root and backend directory are in sys.path
# This guarantees 'from backend.app...' imports work whether running from repo root or backend/ folder
_APP_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _APP_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent
for _path_str in [str(_REPO_ROOT), str(_BACKEND_DIR)]:
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.db.database import init_db
from backend.app.routers import documents, review, qa

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    await init_db()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multimodal AI Document Intelligence Platform — Structured Extraction, Tables, Classification, Grounded Q&A, and Human Review Queue.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - Allow local frontend, production domain, and preview environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/api/health",
        "api_endpoints": {
            "documents": f"{settings.API_V1_STR}/documents",
            "upload": f"{settings.API_V1_STR}/documents/upload",
            "review_queue": f"{settings.API_V1_STR}/review-queue",
            "qa": f"{settings.API_V1_STR}/documents/{{id}}/ask",
            "page_images": "/api/pages/{path}",
        }
    }

# Include API routers
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(review.router, prefix=settings.API_V1_STR)
app.include_router(qa.router, prefix=settings.API_V1_STR)

# Serve rendered page images
@app.get("/api/pages/{subpath:path}")
async def serve_page_image(subpath: str):
    full_path = await storage.get_file_path(subpath)
    file_obj = Path(full_path)
    if not file_obj.exists():
        raise HTTPException(status_code=404, detail=f"Page asset {subpath} not found")
    return FileResponse(file_obj, media_type="image/png")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "ocr_provider": settings.OCR_PROVIDER
    }
