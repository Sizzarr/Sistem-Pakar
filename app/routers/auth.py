from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib

from ..db import get_db
from ..skema import LoginMasuk, TokenKeluar
from ..keamanan import buat_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenKeluar)
def login(payload: LoginMasuk, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT password_sha FROM admin WHERE username=:u LIMIT 1"),
        {"u": payload.username}
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    sha = hashlib.sha256(payload.password.encode("utf-8")).hexdigest()
    if sha != row["password_sha"]:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    return TokenKeluar(access_token=buat_token("admin"))
