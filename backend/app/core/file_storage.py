import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_ROOT = _BACKEND_DIR / "uploads"

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024


def _normalize_extension(filename: str | None, content_type: str | None) -> str:
    ext = ""
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return "jpg" if ext == "jpeg" else ext
    if content_type == "image/jpeg":
        return "jpg"
    if content_type == "image/png":
        return "png"
    return ""


def validate_image_upload(file: UploadFile, max_size: int = MAX_IMAGE_SIZE_BYTES) -> None:
    content_type = (file.content_type or "").lower()
    ext = _normalize_extension(file.filename, content_type)
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES and ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não permitido. Use JPG, JPEG ou PNG.",
        )

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo excede o tamanho máximo permitido (2 MB).",
        )


def save_image_upload(subdir: str, entity_id: int, file: UploadFile) -> str:
    """Salva imagem em uploads/<subdir>/ e retorna URL pública (/uploads/...)."""
    validate_image_upload(file)

    ext = _normalize_extension(file.filename, file.content_type)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível determinar o formato da imagem.",
        )

    target_dir = UPLOADS_ROOT / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{entity_id}_{uuid4().hex}.{ext}"
    disk_path = target_dir / file_name

    content = file.file.read()
    with open(disk_path, "wb") as f:
        f.write(content)

    public_url = f"/uploads/{subdir}/{file_name}"
    logger.info("imagem salva entity_id=%s url=%s", entity_id, public_url)
    return public_url


def normalize_stored_image_url(path: str | None) -> str | None:
    """Garante que caminhos legados retornem URL acessível via /uploads."""
    if not path:
        return None
    if path.startswith("/uploads/") or path.startswith("http://") or path.startswith("https://"):
        return path
    normalized = path.replace("\\", "/")
    if normalized.startswith("uploads/"):
        return f"/{normalized}"
    return path
