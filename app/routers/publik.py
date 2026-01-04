from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..model import Penyakit, Gejala, Solusi
from ..skema import PenyakitKeluar, PenyakitDetailKeluar, GejalaKeluar, SolusiKeluar

router = APIRouter(prefix="/api", tags=["publik"])

@router.get("/penyakit", response_model=list[PenyakitKeluar])
def list_penyakit(db: Session = Depends(get_db)):
    return list(db.scalars(select(Penyakit).order_by(Penyakit.kode)).all())

@router.get("/penyakit/{kode}", response_model=PenyakitDetailKeluar)
def detail_penyakit(kode: str, db: Session = Depends(get_db)):
    p = db.get(Penyakit, kode)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    solusi = list(db.scalars(select(Solusi).where(Solusi.kode_penyakit==kode).order_by(Solusi.urutan)).all())
    return PenyakitDetailKeluar(
        kode=p.kode,
        nama=p.nama,
        pengertian=p.pengertian,
        penyebab=p.penyebab,
        solusi=[SolusiKeluar(kode=s.kode, deskripsi=s.deskripsi, urutan=s.urutan) for s in solusi]
    )

@router.get("/gejala", response_model=list[GejalaKeluar])
def list_gejala(db: Session = Depends(get_db)):
    return list(db.scalars(select(Gejala).order_by(Gejala.kode)).all())
