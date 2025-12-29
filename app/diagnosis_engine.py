"""
Backward chaining versi web (session-based):
- mulai dari hipotesis penyakit (urut priority)
- cek gejala yang dibutuhkan dari rules
- tanya hanya yang dibutuhkan (working memory = jawaban di session)
- jika ada 1 gejala False -> hipotesis gagal, lanjut penyakit berikutnya
- kalau semua gejala True -> diagnosis ditemukan (confidence 100)
"""
from __future__ import annotations

import uuid
from sqlalchemy.orm import Session
from . import models

def _hypotheses(db: Session) -> list[models.Disease]:
    return db.query(models.Disease).order_by(models.Disease.priority.asc(), models.Disease.code.asc()).all()

def _required_symptoms(db: Session, disease_code: str) -> list[str]:
    rows = (
        db.query(models.DiseaseSymptom)
        .filter(models.DiseaseSymptom.disease_code == disease_code)
        .order_by(models.DiseaseSymptom.sort_order.asc(), models.DiseaseSymptom.id.asc())
        .all()
    )
    return [r.symptom_code for r in rows]

def _answers_map(session: models.DiagnosisSession) -> dict[str, bool]:
    return {a.symptom_code: a.answer for a in session.answers}

def start(db: Session) -> models.DiagnosisSession:
    s = models.DiagnosisSession(id=str(uuid.uuid4()), status="asking")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def answer(db: Session, session_id: str, symptom_code: str, answer_value: bool) -> models.DiagnosisSession:
    session = db.query(models.DiagnosisSession).filter(models.DiagnosisSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")
    if session.status == "done":
        return session

    existing = (
        db.query(models.DiagnosisAnswer)
        .filter(models.DiagnosisAnswer.session_id == session_id, models.DiagnosisAnswer.symptom_code == symptom_code)
        .first()
    )
    if existing:
        existing.answer = answer_value
    else:
        db.add(models.DiagnosisAnswer(session_id=session_id, symptom_code=symptom_code, answer=answer_value))

    db.commit()
    db.refresh(session)
    return session

def next_question_or_result(db: Session, session: models.DiagnosisSession) -> tuple[str, dict]:
    if session.status == "done":
        return ("result", build_result(db, session))

    ans = _answers_map(session)

    for disease in _hypotheses(db):
        required = _required_symptoms(db, disease.code)
        if not required:
            continue

        # fail fast if any required is false
        if any(ans.get(sc) is False for sc in required):
            continue

        # success if all required are true
        if all(ans.get(sc) is True for sc in required):
            session.status = "done"
            session.current_disease_code = disease.code
            session.result_disease_code = disease.code
            db.commit()
            return ("result", build_result(db, session))

        # ask first unknown
        for sc in required:
            if sc not in ans:
                session.current_disease_code = disease.code
                db.commit()
                symptom = db.query(models.Symptom).filter(models.Symptom.code == sc).first()
                return ("question", {"code": sc, "question": symptom.question if symptom else sc})

    # no hypotheses match
    session.status = "done"
    session.current_disease_code = None
    session.result_disease_code = None
    db.commit()
    return ("result", build_result(db, session))

def build_result(db: Session, session: models.DiagnosisSession) -> dict:
    ans = _answers_map(session)
    if not session.result_disease_code:
        return {
            "disease": None,
            "matched_symptoms": [],
            "confidence": None,
            "note": "Tidak ada hipotesis penyakit yang bisa dibuktikan. Saran: konsultasi dengan dokter.",
        }

    disease = db.query(models.Disease).filter(models.Disease.code == session.result_disease_code).first()
    required_codes = _required_symptoms(db, disease.code)

    matched = (
        db.query(models.Symptom)
        .filter(models.Symptom.code.in_([c for c in required_codes if ans.get(c) is True]))
        .order_by(models.Symptom.code.asc())
        .all()
    )

    return {
        "disease": {
            "code": disease.code,
            "name": disease.name,
            "description": disease.description,
            "priority": disease.priority,
            "symptoms": required_codes,
        },
        "matched_symptoms": [{"code": m.code, "question": m.question} for m in matched],
        "confidence": 100 if required_codes and all(ans.get(c) is True for c in required_codes) else None,
        "note": None,
    }
