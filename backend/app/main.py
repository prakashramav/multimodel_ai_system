import os
from pathlib import Path
from contextlib import asynccontextmanager
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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local frontend development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "ocr_provider": settings.OCR_PROVIDER
    }
