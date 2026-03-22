from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import login
from app.database.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    return {"access_token": token}
