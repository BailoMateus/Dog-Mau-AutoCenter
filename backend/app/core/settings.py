"""
Configuração central (Pydantic Settings).

Boas práticas:
- Local: arquivo backend/.env (não versionado; já está no .gitignore).
- GCP: as mesmas chaves em variáveis de ambiente do Cloud Run ou como
  "secrets" referenciados no serviço (Secret Manager). Não commitar segredos.

Nomes aceitos em maiúsculas ou minúsculas (ex.: DB_USER ou db_user), útil
quando as variáveis vêm do console do Google Cloud.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            _BACKEND_DIR / ".env",
            Path(".env"),
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    secret_key: str = Field(
        ...,
        description="Segredo para assinar JWT. Obrigatório. Nunca commitar no código.",
    )

    # Opcional: URL completa do Postgres (ex.: local com proxy ou tunel)
    database_url: Optional[str] = Field(default=None)

    db_user: str = "usuario_vazio"
    db_pass: str = ""
    db_name: str = "banco_vazio"
    instance_connection_name: str = "conexao_vazia"

    debug_log: bool = False

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    firebase_web_api_key: str = ""

    @field_validator("debug_log", mode="before")
    @classmethod
    def _coerce_debug_log(cls, v):
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "on")
        return bool(v)


@lru_cache
def get_settings() -> Settings:
    return Settings()
