from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routers.auth import router as auth_router
from .routers.publik import router as publik_router
from .routers.diagnosa import router as diagnosa_router
from .routers.admin import router as admin_router

app = FastAPI(title="Sistem Pakar Diagnosa Tidur", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(publik_router)
app.include_router(diagnosa_router)
app.include_router(admin_router)

# Serve frontend (satu domain biar simpel)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
