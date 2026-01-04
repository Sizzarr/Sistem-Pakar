import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..model import SesiDiagnosa, JawabanDiagnosa, Penyakit, Solusi
from ..skema import DiagnosaMulaiMasuk, DiagnosaMulaiKeluar, DiagnosaJawabMasuk, DiagnosaHasilKeluar, Pertanyaan, Progres, Biodata, PenyakitKeluar, PenyakitDetailKeluar, SolusiKeluar
from ..mesin import langkah_berikutnya, simpan_riwayat, solusi_penyakit

router = APIRouter(prefix="/api/diagnosa", tags=["diagnosa"])

NO_DIAGNOSA_TEXT = (
    "Berdasarkan jawaban kamu, gejala belum cukup untuk menyimpulkan penyakit yang dipilih. "
    "Sistem ini hanya memeriksa penyakit yang ada di basis pengetahuan. "
    "Kalau keluhan kamu mengganggu aktivitas atau makin berat, sebaiknya konsultasi tenaga kesehatan."
)

@router.post("/mulai", response_model=DiagnosaMulaiKeluar)
def mulai(payload: DiagnosaMulaiMasuk, db: Session = Depends(get_db)):
    p = db.get(Penyakit, payload.kode_penyakit)
    if not p:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")

    sid = str(uuid.uuid4())
    sesi = SesiDiagnosa(
        id=sid,
        nama=payload.nama,
        umur=payload.umur,
        jk=payload.jk,
        alamat=payload.alamat,
        kode_penyakit=payload.kode_penyakit,
        status="aktif",
    )
    db.add(sesi)
    db.commit()

    status, q_or_p, prog = langkah_berikutnya(db, sesi)
    if status != "tanya":
        raise HTTPException(status_code=400, detail="Tidak ada pertanyaan. Cek data aturan.")
    return DiagnosaMulaiKeluar(
        sesi_id=sid,
        penyakit=PenyakitKeluar(kode=p.kode, nama=p.nama, pengertian=p.pengertian, penyebab=p.penyebab),
        pertanyaan=Pertanyaan(**q_or_p),
        progres=Progres(**prog),
    )

@router.post("/jawab", response_model=DiagnosaHasilKeluar)
def jawab(payload: DiagnosaJawabMasuk, db: Session = Depends(get_db)):
    sesi = db.get(SesiDiagnosa, payload.sesi_id)
    if not sesi:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")
    if sesi.status != "aktif":
        raise HTTPException(status_code=400, detail="Sesi sudah selesai")

    # upsert jawaban
    existing = db.scalar(select(JawabanDiagnosa).where(
        JawabanDiagnosa.sesi_id == payload.sesi_id,
        JawabanDiagnosa.kode_gejala == payload.kode_gejala
    ))
    if existing:
        existing.jawaban = payload.jawaban
        db.add(existing)
    else:
        db.add(JawabanDiagnosa(sesi_id=payload.sesi_id, kode_gejala=payload.kode_gejala, jawaban=payload.jawaban))
    db.commit()

    status, q_or_p, prog = langkah_berikutnya(db, sesi)

    p = db.get(Penyakit, sesi.kode_penyakit)
    sol = solusi_penyakit(db, sesi.kode_penyakit)
    penyakit_detail = PenyakitDetailKeluar(
        kode=p.kode,
        nama=p.nama,
        pengertian=p.pengertian,
        penyebab=p.penyebab,
        solusi=[SolusiKeluar(kode=s.kode, deskripsi=s.deskripsi, urutan=s.urutan) for s in sol]
    )
    biodata = Biodata(nama=sesi.nama, umur=sesi.umur, jk=sesi.jk, alamat=sesi.alamat)

    if status == "tanya":
        return DiagnosaHasilKeluar(
            status="tanya",
            pesan="Lanjut pertanyaan berikutnya.",
            sesi_id=sesi.id,
            biodata=biodata,
            penyakit=penyakit_detail,
            solusi=penyakit_detail.solusi,
            pertanyaan=Pertanyaan(**q_or_p),
            progres=Progres(**prog),
        )

    if status == "selesai":
        sesi.status = "selesai"
        db.add(sesi)
        db.commit()
        pesan = f"Gejala yang kamu jawab cocok dengan aturan untuk {p.nama}."
        simpan_riwayat(db, sesi, "selesai", pesan)
        return DiagnosaHasilKeluar(
            status="selesai",
            pesan=pesan,
            sesi_id=sesi.id,
            biodata=biodata,
            penyakit=penyakit_detail,
            solusi=penyakit_detail.solusi,
            progres=Progres(**prog),
        )

    # tidak_terpenuhi
    sesi.status = "tidak_terpenuhi"
    db.add(sesi)
    db.commit()
    simpan_riwayat(db, sesi, "tidak_terpenuhi", NO_DIAGNOSA_TEXT)
    return DiagnosaHasilKeluar(
        status="tidak_terpenuhi",
        pesan=NO_DIAGNOSA_TEXT,
        sesi_id=sesi.id,
        biodata=biodata,
        penyakit=penyakit_detail,
        solusi=penyakit_detail.solusi,
        progres=Progres(**prog),
    )
