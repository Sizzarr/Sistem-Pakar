from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .keamanan import cek_token

bearer = HTTPBearer(auto_error=False)

def wajib_admin(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    if not creds:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        sub = cek_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalid")
    if sub != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return sub
