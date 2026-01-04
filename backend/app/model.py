from sqlalchemy import String, Text, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Penyakit(Base):
    __tablename__ = "penyakit"
    kode: Mapped[str] = mapped_column(String(3), primary_key=True)
    nama: Mapped[str] = mapped_column(String(120), nullable=False)
    pengertian: Mapped[str] = mapped_column(Text, nullable=True)
    penyebab: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    aturan: Mapped[list["Aturan"]] = relationship(back_populates="penyakit", cascade="all, delete-orphan")
    solusi: Mapped[list["Solusi"]] = relationship(back_populates="penyakit", cascade="all, delete-orphan")

class Gejala(Base):
    __tablename__ = "gejala"
    kode: Mapped[str] = mapped_column(String(5), primary_key=True)
    nama: Mapped[str] = mapped_column(String(255), nullable=False)
    kelompok: Mapped[str] = mapped_column(String(1), nullable=False, default="A")
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())

    aturan: Mapped[list["Aturan"]] = relationship(back_populates="gejala", cascade="all, delete-orphan")

class Aturan(Base):
    __tablename__ = "aturan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kode_penyakit: Mapped[str] = mapped_column(String(3), ForeignKey("penyakit.kode", ondelete="CASCADE"), nullable=False)
    kode_gejala: Mapped[str] = mapped_column(String(5), ForeignKey("gejala.kode", ondelete="CASCADE"), nullable=False)
    urutan: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("kode_penyakit", "kode_gejala", name="uq_aturan"),)

    penyakit: Mapped["Penyakit"] = relationship(back_populates="aturan")
    gejala: Mapped["Gejala"] = relationship(back_populates="aturan")

class Solusi(Base):
    __tablename__ = "solusi"
    kode: Mapped[str] = mapped_column(String(3), primary_key=True)  # S01 dst
    kode_penyakit: Mapped[str] = mapped_column(String(3), ForeignKey("penyakit.kode", ondelete="CASCADE"), nullable=False)
    deskripsi: Mapped[str] = mapped_column(Text, nullable=False)
    urutan: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    penyakit: Mapped["Penyakit"] = relationship(back_populates="solusi")

class SesiDiagnosa(Base):
    __tablename__ = "sesi_diagnosa"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nama: Mapped[str] = mapped_column(String(120), nullable=False)
    umur: Mapped[int] = mapped_column(Integer, nullable=False)
    jk: Mapped[str] = mapped_column(String(20), nullable=False)
    alamat: Mapped[str] = mapped_column(Text, nullable=False)
    kode_penyakit: Mapped[str] = mapped_column(String(3), ForeignKey("penyakit.kode", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aktif")  # aktif|selesai|tidak_terpenuhi
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    jawaban: Mapped[list["JawabanDiagnosa"]] = relationship(back_populates="sesi", cascade="all, delete-orphan")

class JawabanDiagnosa(Base):
    __tablename__ = "jawaban_diagnosa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sesi_id: Mapped[str] = mapped_column(String(36), ForeignKey("sesi_diagnosa.id", ondelete="CASCADE"), nullable=False)
    kode_gejala: Mapped[str] = mapped_column(String(5), ForeignKey("gejala.kode", ondelete="CASCADE"), nullable=False)
    jawaban: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ditanya_pada: Mapped[object] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("sesi_id", "kode_gejala", name="uq_sesi_gejala"),)

    sesi: Mapped["SesiDiagnosa"] = relationship(back_populates="jawaban")

class RiwayatDiagnosa(Base):
    __tablename__ = "riwayat_diagnosa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sesi_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nama: Mapped[str] = mapped_column(String(120), nullable=False)
    umur: Mapped[int] = mapped_column(Integer, nullable=False)
    jk: Mapped[str] = mapped_column(String(20), nullable=False)
    alamat: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # selesai|tidak_terpenuhi
    kode_penyakit: Mapped[str] = mapped_column(String(3), nullable=False)
    nama_penyakit: Mapped[str] = mapped_column(String(120), nullable=False)
    pesan: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
