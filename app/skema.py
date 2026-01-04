from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ORMBase(BaseModel):
    """Base schema untuk response yang membaca atribut dari ORM (SQLAlchemy)."""
    model_config = ConfigDict(from_attributes=True)

# --- Auth ---
class LoginMasuk(BaseModel):
    username: str
    password: str

class TokenKeluar(ORMBase):
    access_token: str
    token_type: str = "bearer"

# --- Public ---
class PenyakitKeluar(ORMBase):
    kode: str
    nama: str
    pengertian: Optional[str] = None
    penyebab: Optional[str] = None

class GejalaKeluar(ORMBase):
    kode: str
    nama: str

class SolusiKeluar(ORMBase):
    kode: str
    deskripsi: str
    urutan: int

class PenyakitDetailKeluar(PenyakitKeluar):
    solusi: List[SolusiKeluar] = []

# --- Diagnosa ---
class Biodata(BaseModel):
    nama: str
    umur: int
    jk: str
    alamat: str

class DiagnosaMulaiMasuk(Biodata):
    kode_penyakit: str = Field(min_length=2, max_length=3)

class Pertanyaan(BaseModel):
    kode_gejala: str
    teks: str

class Progres(BaseModel):
    ditanya: int
    total: int

class DiagnosaMulaiKeluar(ORMBase):
    sesi_id: str
    penyakit: PenyakitKeluar
    pertanyaan: Pertanyaan
    progres: Progres

class DiagnosaJawabMasuk(BaseModel):
    sesi_id: str
    kode_gejala: str
    jawaban: bool

class DiagnosaHasilKeluar(ORMBase):
    status: str  # tanya|selesai|tidak_terpenuhi
    pesan: str
    sesi_id: str
    biodata: Biodata
    penyakit: PenyakitDetailKeluar
    solusi: List[SolusiKeluar] = []
    pertanyaan: Optional[Pertanyaan] = None
    progres: Optional[Progres] = None
