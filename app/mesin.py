from sqlalchemy.orm import Session
from sqlalchemy import select
from .model import Penyakit, Gejala, Aturan, Solusi, SesiDiagnosa, JawabanDiagnosa, RiwayatDiagnosa

def daftar_gejala_untuk_penyakit(db: Session, kode_penyakit: str) -> list[str]:
    rows = db.scalars(
        select(Aturan).where(Aturan.kode_penyakit == kode_penyakit).order_by(Aturan.urutan)
    ).all()
    return [r.kode_gejala for r in rows]

def teks_gejala(db: Session, kode_gejala: str) -> str:
    g = db.get(Gejala, kode_gejala)
    return g.nama if g else kode_gejala

def peta_jawaban(db: Session, sesi_id: str) -> dict[str, bool]:
    rows = db.scalars(select(JawabanDiagnosa).where(JawabanDiagnosa.sesi_id == sesi_id)).all()
    return {r.kode_gejala: bool(r.jawaban) for r in rows}

def progres(db: Session, sesi: SesiDiagnosa) -> dict:
    req = daftar_gejala_untuk_penyakit(db, sesi.kode_penyakit)
    ans = peta_jawaban(db, sesi.id)
    ditanya = sum(1 for k in req if k in ans)
    total = max(len(req), 1)
    return {"ditanya": ditanya, "total": total}

def solusi_penyakit(db: Session, kode_penyakit: str) -> list[Solusi]:
    return list(db.scalars(
        select(Solusi).where(Solusi.kode_penyakit == kode_penyakit).order_by(Solusi.urutan)
    ).all())

def langkah_berikutnya(db: Session, sesi: SesiDiagnosa):
    req = daftar_gejala_untuk_penyakit(db, sesi.kode_penyakit)
    ans = peta_jawaban(db, sesi.id)
    pr = progres(db, sesi)

    # kalau ada jawaban "Tidak" di salah satu gejala premis, rule gagal
    for k in req:
        if k in ans and ans[k] is False:
            return ("tidak_terpenuhi", None, pr)

    # tanya gejala yg belum ditanya
    for k in req:
        if k not in ans:
            return ("tanya", {"kode_gejala": k, "teks": teks_gejala(db, k)}, pr)

    # semua Ya -> terbukti
    penyakit = db.get(Penyakit, sesi.kode_penyakit)
    return ("selesai", penyakit, pr)

def simpan_riwayat(db: Session, sesi: SesiDiagnosa, status: str, pesan: str):
    p = db.get(Penyakit, sesi.kode_penyakit)
    h = RiwayatDiagnosa(
        sesi_id=sesi.id,
        nama=sesi.nama,
        umur=sesi.umur,
        jk=sesi.jk,
        alamat=sesi.alamat,
        status=status,
        kode_penyakit=p.kode if p else sesi.kode_penyakit,
        nama_penyakit=p.nama if p else sesi.kode_penyakit,
        pesan=pesan
    )
    db.add(h)
    db.commit()
    return h
