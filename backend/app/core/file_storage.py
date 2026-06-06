import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_SUBDIRS = ("produtos", "pecas", "perfil")


def get_uploads_root() -> Path:
    """Raiz de uploads: backend/uploads ou UPLOADS_DIR (absoluto no container/host)."""
    override = get_settings().uploads_dir
    if override:
        return Path(override).expanduser().resolve()
    return (_BACKEND_DIR / "uploads").resolve()


UPLOADS_ROOT = get_uploads_root()

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024


def ensure_upload_subdirs() -> Path:
    """Cria uploads/ e subpastas produtos, pecas, perfil."""
    root = get_uploads_root()
    root.mkdir(parents=True, exist_ok=True)
    for name in UPLOAD_SUBDIRS:
        (root / name).mkdir(parents=True, exist_ok=True)
    logger.info(
        "uploads prontos backend_dir=%s uploads_root=%s cwd=%s",
        _BACKEND_DIR.resolve(),
        root,
        Path.cwd(),
    )
    return root


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

    # Mede o tamanho do arquivo avançando o ponteiro
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    # Garante o reset do ponteiro para o início do arquivo de qualquer forma
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

    uploads_root = get_uploads_root()
    target_dir = uploads_root / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{entity_id}_{uuid4().hex}.{ext}"
    file_path = target_dir / file_name

    # Assegura que o ponteiro está no zero antes da leitura final
    file.file.seek(0)
    content = file.file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem vazio ou já consumido.",
        )

    logger.info("Saving file at %s", file_path.resolve())
    file_path.write_bytes(content)
    logger.info("File exists after save: %s", file_path.exists())
    
    if not file_path.exists() or file_path.stat().st_size != len(content):
        logger.error(
            "falha ao persistir upload subdir=%s path=%s size_esperado=%s size_disco=%s",
            subdir,
            file_path.resolve(),
            len(content),
            file_path.stat().st_size if file_path.exists() else None,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível salvar a imagem no disco.",
        )

    public_url = f"/uploads/{subdir}/{file_name}"
    logger.info(
        "imagem salva entity_id=%s subdir=%s url=%s bytes=%s",
        entity_id,
        subdir,
        public_url,
        len(content),
    )
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