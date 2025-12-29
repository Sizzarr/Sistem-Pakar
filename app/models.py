from sqlalchemy import String, Text, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Disease(Base):
    __tablename__ = "diseases"
    code: Mapped[str] = mapped_column(String(10), primary_key=True)  # P01
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=100)

    symptoms: Mapped[list["DiseaseSymptom"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )

class Symptom(Base):
    __tablename__ = "symptoms"
    code: Mapped[str] = mapped_column(String(10), primary_key=True)  # G01
    question: Mapped[str] = mapped_column(Text)

    diseases: Mapped[list["DiseaseSymptom"]] = relationship(
        back_populates="symptom", cascade="all, delete-orphan"
    )

class DiseaseSymptom(Base):
    __tablename__ = "disease_symptoms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disease_code: Mapped[str] = mapped_column(ForeignKey("diseases.code", ondelete="CASCADE"))
    symptom_code: Mapped[str] = mapped_column(ForeignKey("symptoms.code", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    disease: Mapped["Disease"] = relationship(back_populates="symptoms")
    symptom: Mapped["Symptom"] = relationship(back_populates="diseases")

    __table_args__ = (
        UniqueConstraint("disease_code", "symptom_code", name="uq_disease_symptom"),
    )

class DiagnosisSession(Base):
    __tablename__ = "diagnosis_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    status: Mapped[str] = mapped_column(String(20), default="asking")  # asking|done
    current_disease_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    result_disease_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    answers: Mapped[list["DiagnosisAnswer"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

class DiagnosisAnswer(Base):
    __tablename__ = "diagnosis_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"))
    symptom_code: Mapped[str] = mapped_column(String(10))
    answer: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DiagnosisSession"] = relationship(back_populates="answers")

    __table_args__ = (
        UniqueConstraint("session_id", "symptom_code", name="uq_session_symptom"),
    )
