from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import init_db, SessionLocal
from .config import settings
from . import models, crud
from .security import hash_password

from .routers import pages as pages_router
from .routers import public_api as public_router
from .routers import auth as auth_router
from .routers import admin_api as admin_router

app = FastAPI(title="Sistem Pakar Gangguan Tidur", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_router.router)
app.include_router(public_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)

@app.on_event("startup")
def on_startup():
    init_db()
    db: Session = SessionLocal()
    try:
        crud.seed_if_empty(db)
        _bootstrap_admin_if_needed(db)
    finally:
        db.close()

def _bootstrap_admin_if_needed(db: Session):
    if db.query(models.User).count() > 0:
        return
    if not settings.FIRST_ADMIN_EMAIL or not settings.FIRST_ADMIN_PASSWORD:
        return
    user = models.User(
        email=settings.FIRST_ADMIN_EMAIL,
        password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
        is_admin=True,
    )
    db.add(user)
    db.commit()

@app.get("/health")
def health():
    return {"ok": True}
