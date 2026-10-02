from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings
from app.security import ALLOWED_UPLOAD_EXT, ALLOWED_UPLOAD_MIME


def validate_upload(file: UploadFile) -> tuple[str, str]:
    settings = get_settings()
    name = file.filename or "file"
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_EXT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_UPLOAD_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MIME type not allowed")
    stored = f"{uuid.uuid4().hex}{suffix}"
    return stored, content_type


def save_upload(file: UploadFile, stored_name: str) -> int:
    settings = get_settings()
    dest_dir = Path(settings.upload_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / stored_name
    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0
    with dest.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")
            out.write(chunk)
    return size


def attachment_path(stored_name: str) -> Path:
    settings = get_settings()
    path = (Path(settings.upload_dir) / stored_name).resolve()
    root = Path(settings.upload_dir).resolve()
    if not str(path).startswith(str(root)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return path
