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


def _content_type_for_ext(ext: str) -> str:
    return "image/png" if ext == "png" else "image/jpeg"


def _storage_object_name(subdir: str, file_name: str) -> str:
    return f"uploads/{subdir}/{file_name}"


def _try_storage_upload(subdir: str, file_name: str, content: bytes, content_type: str) -> bool:
    """Faz upload da imagem para o Firebase Storage (persistente). Retorna
    True em caso de sucesso, False se o Storage estiver indisponível."""
    try:
        from app.core.firebase import get_bucket

        bucket = get_bucket()
        if not bucket:
            return False
        blob = bucket.blob(_storage_object_name(subdir, file_name))
        blob.upload_from_string(content, content_type=content_type)
        logger.info("imagem enviada ao Firebase Storage object=%s bytes=%s",
                    _storage_object_name(subdir, file_name), len(content))
        return True
    except Exception as e:
        logger.warning(
            "falha no upload ao Firebase Storage subdir=%s file=%s: %s — usando disco local",
            subdir, file_name, e,
        )
        return False


def _save_to_disk(subdir: str, file_name: str, content: bytes) -> None:
    uploads_root = get_uploads_root()
    target_dir = uploads_root / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / file_name
    file_path.write_bytes(content)
    if not file_path.exists() or file_path.stat().st_size != len(content):
        logger.error(
            "falha ao persistir upload subdir=%s path=%s size_esperado=%s size_disco=%s",
            subdir, file_path.resolve(), len(content),
            file_path.stat().st_size if file_path.exists() else None,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível salvar a imagem no disco.",
        )


def save_image_upload(subdir: str, entity_id: int, file: UploadFile) -> str:
    """Salva imagem e retorna URL pública (/uploads/<subdir>/<arquivo>).

    Persiste primeiro no Firebase Storage (durável e compatível com o
    filesystem efêmero do Cloud Run). Se o Storage estiver indisponível
    (ex.: ambiente local sem credenciais), grava no disco como fallback.
    O caminho retornado (/uploads/...) é servido pela rota de uploads do
    backend, que sabe ler do disco ou do Storage.
    """
    validate_image_upload(file)

    ext = _normalize_extension(file.filename, file.content_type)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível determinar o formato da imagem.",
        )

    file_name = f"{entity_id}_{uuid4().hex}.{ext}"

    # Assegura que o ponteiro está no zero antes da leitura final
    file.file.seek(0)
    content = file.file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem vazio ou já consumido.",
        )

    content_type = _content_type_for_ext(ext)

    stored_in_cloud = _try_storage_upload(subdir, file_name, content, content_type)
    if not stored_in_cloud:
        # Fallback: disco local (desenvolvimento ou Storage indisponível)
        _save_to_disk(subdir, file_name, content)

    public_url = f"/uploads/{subdir}/{file_name}"
    logger.info(
        "imagem salva entity_id=%s subdir=%s url=%s bytes=%s destino=%s",
        entity_id, subdir, public_url, len(content),
        "storage" if stored_in_cloud else "disco",
    )
    return public_url


def read_image_bytes(rel_path: str) -> tuple[bytes, str] | None:
    """Lê uma imagem de uploads/<rel_path>. Procura primeiro no disco local
    e, se não houver, no Firebase Storage. Retorna (bytes, content_type) ou None.

    rel_path é algo como "pecas/2_abc.jpg" (sem o prefixo /uploads/).
    """
    rel_path = (rel_path or "").lstrip("/")
    # Proteção contra path traversal
    if not rel_path or ".." in rel_path.replace("\\", "/").split("/"):
        return None

    ext = rel_path.rsplit(".", 1)[-1].lower() if "." in rel_path else ""
    content_type = _content_type_for_ext(ext)

    # 1. Disco local
    try:
        local_path = (get_uploads_root() / rel_path).resolve()
        uploads_root = get_uploads_root().resolve()
        if str(local_path).startswith(str(uploads_root)) and local_path.exists() and local_path.is_file():
            return local_path.read_bytes(), content_type
    except Exception as e:
        logger.warning("falha ao ler imagem do disco rel=%s: %s", rel_path, e)

    # 2. Firebase Storage
    try:
        from app.core.firebase import get_bucket

        bucket = get_bucket()
        if bucket:
            blob = bucket.blob(f"uploads/{rel_path}")
            if blob.exists():
                data = blob.download_as_bytes()
                return data, (blob.content_type or content_type)
    except Exception as e:
        logger.warning("falha ao ler imagem do Firebase Storage rel=%s: %s", rel_path, e)

    return None


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