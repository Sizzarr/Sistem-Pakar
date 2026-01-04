from datetime import datetime, timedelta, timezone
from jose import jwt
from .konfigurasi import settings

ALGO = "HS256"

def buat_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": exp}, settings.JWT_SECRET, algorithm=ALGO)

def cek_token(token: str) -> str:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
    return payload.get("sub", "")
