import os
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Union
from backend.app.core.config import settings

class StorageProvider:
    """Abstract interface for storage (Local Disk or S3)."""
    async def save_file(self, file_obj: Union[BinaryIO, bytes], destination_subpath: str) -> str:
        raise NotImplementedError
    
    async def get_file_path(self, relative_path: str) -> str:
        raise NotImplementedError

    async def delete_file(self, relative_path: str) -> bool:
        raise NotImplementedError

class LocalDiskStorage(StorageProvider):
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.FILE_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "uploads").mkdir(parents=True, exist_ok=True)
        (self.base_path / "pages").mkdir(parents=True, exist_ok=True)

    async def save_file(self, content: Union[BinaryIO, bytes], destination_subpath: str) -> str:
        full_dest = (self.base_path / destination_subpath).resolve()
        full_dest.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            with open(full_dest, "wb") as f:
                f.write(content)
        else:
            with open(full_dest, "wb") as f:
                shutil.copyfileobj(content, f)

        # Return path relative to base_path for database persistence
        return str(Path(destination_subpath).as_posix())

    async def get_file_path(self, relative_path: str) -> str:
        full_path = (self.base_path / relative_path).resolve()
        return str(full_path)

    async def delete_file(self, relative_path: str) -> bool:
        try:
            full_path = (self.base_path / relative_path).resolve()
            if full_path.exists():
                full_path.unlink()
                return True
        except Exception:
            pass
        return False

# Drop-in singleton
storage = LocalDiskStorage()
