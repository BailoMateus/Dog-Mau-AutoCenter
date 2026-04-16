from app.core.settings import get_settings

_s = get_settings()

SECRET_KEY = _s.secret_key
ALGORITHM = _s.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = _s.access_token_expire_minutes
