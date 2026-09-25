import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocIntel - Multimodal Document Intelligence Platform"
    API_V1_STR: str = "/api"
    
    # Environment & Keys: Google Gemini Multimodal API
    GEMINI_API_KEY: str = Field(default="", env=["GEMINI_API_KEY", "GOOGLE_API_KEY"])
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")
    
    # OCR Settings
    OCR_PROVIDER: str = Field(default="tesseract", env="OCR_PROVIDER") # tesseract, cloud, or native
    OCR_API_KEY: str = Field(default="", env="OCR_API_KEY")
    TESSERACT_CMD: str = Field(default="", env="TESSERACT_CMD")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./docintel.db",
        env="DATABASE_URL"
    )
    
    # Storage
    FILE_STORAGE_PATH: str = Field(
        default=str(BASE_DIR / "storage"),
        env="FILE_STORAGE_PATH"
    )
    
    # Confidence routing threshold
    CONFIDENCE_THRESHOLD: float = Field(default=0.75, env="CONFIDENCE_THRESHOLD")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
storage_path = Path(settings.FILE_STORAGE_PATH)
(storage_path / "uploads").mkdir(parents=True, exist_ok=True)
(storage_path / "pages").mkdir(parents=True, exist_ok=True)
