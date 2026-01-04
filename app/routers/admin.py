from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete
from pydantic import BaseModel
from typing import List, Optional

import re
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
        "gejala": [{"kode": g.kode, "nama": g.nama} for g in gejala],
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


# -----------------------------
# CRUD Admin: penyakit & gejala
# -----------------------------

class PenyakitMasuk(BaseModel):
    kode: str
    nama: str
    pengertian: Optional[str] = None
    penyebab: Optional[str] = None


class GejalaMasuk(BaseModel):
    kode: str
    nama: str


class AturanSimpanMasuk(BaseModel):
    gejala: List[str] = []
    solusi: List[str] = []  # daftar baris solusi


def _norm_kode_penyakit(kode: str) -> str:
    k = (kode or "").strip().upper()
    if not re.fullmatch(r"P\d{2}", k):
        raise HTTPException(status_code=400, detail="Kode penyakit harus format P01, P02, dst")
    return k


def _norm_kode_gejala(kode: str) -> str:
    k = (kode or "").strip().upper()
    if not re.fullmatch(r"G-\d{2}", k):
        raise HTTPException(status_code=400, detail="Kode gejala harus format G-01, G-02, dst")
    return k



def _next_solusi_number(db: Session) -> int:
    # cari nomor terbesar dari Sxx
    rows = db.scalars(select(Solusi.kode)).all()
    mx = 0
    for code in rows:
        if not code:
            continue
        m = re.fullmatch(r"S(\d+)", code.strip().upper())
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def _fmt_solusi_kode(n: int) -> str:
    return f"S{n:02d}" if n < 100 else f"S{n}"


@router.post("/import", dependencies=[Depends(wajib_admin)])
def import_data(payload: dict = Body(...), db: Session = Depends(get_db)):
    """Import ulang basis pengetahuan (penyakit, gejala, aturan, solusi).

    Catatan: Riwayat diagnosa tidak dihapus.
    Payload yang punya field lama seperti `kelompok` akan diabaikan.
    """

    penyakit_items = payload.get("penyakit", [])
    gejala_items = payload.get("gejala", [])
    aturan_items = payload.get("aturan", [])
    solusi_items = payload.get("solusi", [])

    if not all(isinstance(x, list) for x in [penyakit_items, gejala_items, aturan_items, solusi_items]):
        raise HTTPException(status_code=400, detail="Format JSON tidak valid")

    # wipe knowledge-base tables (keep riwayat)
    db.execute(delete(Aturan))
    db.execute(delete(Solusi))
    db.execute(delete(Gejala))
    db.execute(delete(Penyakit))

    # insert penyakit
    for p in penyakit_items:
        kode = _norm_kode_penyakit((p or {}).get("kode"))
        nama = ((p or {}).get("nama") or "").strip()
        if not nama:
            raise HTTPException(status_code=400, detail=f"Nama penyakit kosong untuk {kode}")
        db.add(Penyakit(
            kode=kode,
            nama=nama,
            pengertian=(p or {}).get("pengertian"),
            penyebab=(p or {}).get("penyebab"),
        ))

    # insert gejala
    for g in gejala_items:
        kode = _norm_kode_gejala((g or {}).get("kode"))
        nama = ((g or {}).get("nama") or "").strip()
        if not nama:
            raise HTTPException(status_code=400, detail=f"Nama gejala kosong untuk {kode}")
        db.add(Gejala(kode=kode, nama=nama))

    db.flush()

    # insert aturan
    for a in aturan_items:
        kp = _norm_kode_penyakit((a or {}).get("kode_penyakit"))
        kg = _norm_kode_gejala((a or {}).get("kode_gejala"))
        ur = int((a or {}).get("urutan") or 1)
        db.add(Aturan(kode_penyakit=kp, kode_gejala=kg, urutan=ur))

    # insert solusi
    for s in solusi_items:
        kode = ((s or {}).get("kode") or "").strip().upper()
        if not kode:
            raise HTTPException(status_code=400, detail="Kode solusi kosong")
        kp = _norm_kode_penyakit((s or {}).get("kode_penyakit"))
        des = ((s or {}).get("deskripsi") or "").strip()
        ur = int((s or {}).get("urutan") or 1)
        db.add(Solusi(kode=kode, kode_penyakit=kp, deskripsi=des, urutan=ur))

    db.commit()
    return {"ok": True}


@router.get("/penyakit", dependencies=[Depends(wajib_admin)])
def list_penyakit(db: Session = Depends(get_db)):
    items = db.scalars(select(Penyakit).order_by(Penyakit.kode)).all()
    return [
        {"kode": p.kode, "nama": p.nama, "pengertian": p.pengertian, "penyebab": p.penyebab}
        for p in items
    ]


@router.get("/penyakit/{kode}", dependencies=[Depends(wajib_admin)])
def detail_penyakit(kode: str, db: Session = Depends(get_db)):
    kode = _norm_kode_penyakit(kode)
    p = db.get(Penyakit, kode)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    return {"kode": p.kode, "nama": p.nama, "pengertian": p.pengertian, "penyebab": p.penyebab}


@router.post("/penyakit", dependencies=[Depends(wajib_admin)])
def tambah_penyakit(payload: PenyakitMasuk, db: Session = Depends(get_db)):
    kode = _norm_kode_penyakit(payload.kode)
    if db.get(Penyakit, kode):
        raise HTTPException(status_code=409, detail="Kode penyakit sudah ada")
    p = Penyakit(kode=kode, nama=payload.nama.strip(), pengertian=payload.pengertian, penyebab=payload.penyebab)
    db.add(p)
    db.commit()
    return {"kode": p.kode, "nama": p.nama, "pengertian": p.pengertian, "penyebab": p.penyebab}


@router.put("/penyakit/{kode}", dependencies=[Depends(wajib_admin)])
def ubah_penyakit(kode: str, payload: PenyakitMasuk, db: Session = Depends(get_db)):
    kode = _norm_kode_penyakit(kode)
    p = db.get(Penyakit, kode)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    p.nama = payload.nama.strip()
    p.pengertian = payload.pengertian
    p.penyebab = payload.penyebab
    db.commit()
    return {"kode": p.kode, "nama": p.nama, "pengertian": p.pengertian, "penyebab": p.penyebab}


@router.delete("/penyakit/{kode}", dependencies=[Depends(wajib_admin)])
def hapus_penyakit(kode: str, db: Session = Depends(get_db)):
    kode = _norm_kode_penyakit(kode)
    p = db.get(Penyakit, kode)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    db.delete(p)
    db.commit()
    return {"ok": True}


@router.get("/gejala", dependencies=[Depends(wajib_admin)])
def list_gejala(db: Session = Depends(get_db)):
    items = db.scalars(select(Gejala).order_by(Gejala.kode)).all()
    return [
        {"kode": g.kode, "nama": g.nama}
        for g in items
    ]


@router.get("/gejala/{kode}", dependencies=[Depends(wajib_admin)])
def detail_gejala(kode: str, db: Session = Depends(get_db)):
    kode = _norm_kode_gejala(kode)
    g = db.get(Gejala, kode)
    if not g:
        raise HTTPException(status_code=404, detail="Gejala tidak ditemukan")
    return {"kode": g.kode, "nama": g.nama}


@router.post("/gejala", dependencies=[Depends(wajib_admin)])
def tambah_gejala(payload: GejalaMasuk, db: Session = Depends(get_db)):
    kode = _norm_kode_gejala(payload.kode)
    if db.get(Gejala, kode):
        raise HTTPException(status_code=409, detail="Kode gejala sudah ada")
    g = Gejala(kode=kode, nama=payload.nama.strip())
    db.add(g)
    db.commit()
    return {"kode": g.kode, "nama": g.nama}


@router.put("/gejala/{kode}", dependencies=[Depends(wajib_admin)])
def ubah_gejala(kode: str, payload: GejalaMasuk, db: Session = Depends(get_db)):
    kode = _norm_kode_gejala(kode)
    g = db.get(Gejala, kode)
    if not g:
        raise HTTPException(status_code=404, detail="Gejala tidak ditemukan")
    g.nama = payload.nama.strip()
    db.commit()
    return {"kode": g.kode, "nama": g.nama}


@router.delete("/gejala/{kode}", dependencies=[Depends(wajib_admin)])
def hapus_gejala(kode: str, db: Session = Depends(get_db)):
    kode = _norm_kode_gejala(kode)
    g = db.get(Gejala, kode)
    if not g:
        raise HTTPException(status_code=404, detail="Gejala tidak ditemukan")
    db.delete(g)
    db.commit()
    return {"ok": True}


# -----------------------------
# Aturan + Solusi per penyakit
# -----------------------------

@router.get("/aturan", dependencies=[Depends(wajib_admin)])
def list_aturan(db: Session = Depends(get_db)):
    penyakit = db.scalars(select(Penyakit).order_by(Penyakit.kode)).all()
    out = []
    for p in penyakit:
        gej = db.scalars(
            select(Aturan).where(Aturan.kode_penyakit == p.kode).order_by(Aturan.urutan)
        ).all()
        sol = db.scalars(
            select(Solusi).where(Solusi.kode_penyakit == p.kode).order_by(Solusi.urutan)
        ).all()
        out.append({
            "kode_penyakit": p.kode,
            "nama_penyakit": p.nama,
            "gejala": [a.kode_gejala for a in gej],
            "solusi": [{"kode": s.kode, "deskripsi": s.deskripsi, "urutan": s.urutan} for s in sol],
        })
    return out


@router.get("/aturan/{kode_penyakit}", dependencies=[Depends(wajib_admin)])
def detail_aturan(kode_penyakit: str, db: Session = Depends(get_db)):
    kode_penyakit = _norm_kode_penyakit(kode_penyakit)
    p = db.get(Penyakit, kode_penyakit)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    gej = db.scalars(select(Aturan).where(Aturan.kode_penyakit == kode_penyakit).order_by(Aturan.urutan)).all()
    sol = db.scalars(select(Solusi).where(Solusi.kode_penyakit == kode_penyakit).order_by(Solusi.urutan)).all()
    return {
        "kode_penyakit": p.kode,
        "nama_penyakit": p.nama,
        "gejala": [a.kode_gejala for a in gej],
        "solusi": [{"kode": s.kode, "deskripsi": s.deskripsi, "urutan": s.urutan} for s in sol],
    }


@router.put("/aturan/{kode_penyakit}", dependencies=[Depends(wajib_admin)])
def simpan_aturan(kode_penyakit: str, payload: AturanSimpanMasuk, db: Session = Depends(get_db)):
    kode_penyakit = _norm_kode_penyakit(kode_penyakit)
    p = db.get(Penyakit, kode_penyakit)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")

    # validasi gejala (harus ada di tabel gejala)
    gejala_kode = [_norm_kode_gejala(k) for k in payload.gejala]
    if gejala_kode:
        ada = set(db.scalars(select(Gejala.kode).where(Gejala.kode.in_(gejala_kode))).all())
        tidak_ada = [k for k in gejala_kode if k not in ada]
        if tidak_ada:
            raise HTTPException(status_code=400, detail=f"Kode gejala tidak ditemukan: {', '.join(tidak_ada)}")

    # replace aturan
    db.execute(delete(Aturan).where(Aturan.kode_penyakit == kode_penyakit))
    for i, kg in enumerate(gejala_kode, start=1):
        db.add(Aturan(kode_penyakit=kode_penyakit, kode_gejala=kg, urutan=i))

    # replace solusi (pakai teks per baris)
    new_lines = [s.strip() for s in payload.solusi if s and s.strip()]
    existing = db.scalars(select(Solusi).where(Solusi.kode_penyakit == kode_penyakit).order_by(Solusi.urutan)).all()

    # update existing
    for idx, line in enumerate(new_lines):
        if idx < len(existing):
            existing[idx].deskripsi = line
            existing[idx].urutan = idx + 1
        else:
            n = _next_solusi_number(db)
            db.add(Solusi(kode=_fmt_solusi_kode(n), kode_penyakit=kode_penyakit, deskripsi=line, urutan=idx + 1))

    # delete extras
    for j in range(len(new_lines), len(existing)):
        db.delete(existing[j])

    db.commit()
    return detail_aturan(kode_penyakit, db)
