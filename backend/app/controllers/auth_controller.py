import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import login
from app.database.database import get_db
from app.middlewares.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    logger.info("POST /auth/login email=%s", data.email)
    token = login(db, data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    return {"access_token": token}

@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current
