from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete
from ..db import get_db
from ..dependensi import wajib_admin
from ..model import Penyakit, Gejala, Aturan, Solusi, RiwayatDiagnosa

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats", dependencies=[Depends(wajib_admin)])
def stats(db: Session = Depends(get_db)):
    return {
        "total_penyakit": db.scalar(select(func.count()).select_from(Penyakit)) or 0,
        "total_gejala": db.scalar(select(func.count()).select_from(Gejala)) or 0,
        "total_solusi": db.scalar(select(func.count()).select_from(Solusi)) or 0,
        "total_riwayat": db.scalar(select(func.count()).select_from(RiwayatDiagnosa)) or 0,
    }

@router.get("/riwayat", dependencies=[Depends(wajib_admin)])
def riwayat(db: Session = Depends(get_db), limit: int = 200):
    rows = db.scalars(select(RiwayatDiagnosa).order_by(RiwayatDiagnosa.id.desc()).limit(limit)).all()
    return {
        "items": [
            {
                "id": r.id,
                "created_at": str(r.created_at),
                "nama": r.nama,
                "umur": r.umur,
                "jk": r.jk,
                "alamat": r.alamat,
                "status": r.status,
                "kode_penyakit": r.kode_penyakit,
                "nama_penyakit": r.nama_penyakit,
                "pesan": r.pesan,
            } for r in rows
        ]
    }

@router.delete("/riwayat", dependencies=[Depends(wajib_admin)])
def hapus_riwayat(db: Session = Depends(get_db)):
    db.execute(delete(RiwayatDiagnosa))
    db.commit()
    return {"ok": True}

@router.get("/export", dependencies=[Depends(wajib_admin)])
def export_data(db: Session = Depends(get_db)):
    penyakit = list(db.scalars(select(Penyakit).order_by(Penyakit.kode)).all())
    gejala = list(db.scalars(select(Gejala).order_by(Gejala.kode)).all())
    aturan = list(db.scalars(select(Aturan).order_by(Aturan.kode_penyakit, Aturan.urutan)).all())
    solusi = list(db.scalars(select(Solusi).order_by(Solusi.kode)).all())
    return {
        "penyakit": [{"kode": p.kode, "nama": p.nama, "pengertian": p.pengertian, "penyebab": p.penyebab} for p in penyakit],
        "gejala": [{"kode": g.kode, "nama": g.nama, "kelompok": g.kelompok} for g in gejala],
        "aturan": [{"kode_penyakit": a.kode_penyakit, "kode_gejala": a.kode_gejala, "urutan": a.urutan} for a in aturan],
        "solusi": [{"kode": s.kode, "kode_penyakit": s.kode_penyakit, "deskripsi": s.deskripsi, "urutan": s.urutan} for s in solusi],
    }

@router.post("/reset", dependencies=[Depends(wajib_admin)])
def reset_data(db: Session = Depends(get_db)):
    # Reset = re-import SQL seed is easier; but we provide a quick wipe so user can re-import db_init.sql
    db.execute(delete(Aturan))
    db.execute(delete(Solusi))
    db.execute(delete(Gejala))
    db.execute(delete(Penyakit))
    db.execute(delete(RiwayatDiagnosa))
    db.commit()
    return {"ok": True, "note": "Data sudah dikosongkan. Import ulang db_init.sql untuk seed."}
