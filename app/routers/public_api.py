from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from .. import diagnosis_engine
from ..schemas import DiagnosisStartResponse, DiagnosisAnswerRequest, DiagnosisStepResponse, SymptomOut

router = APIRouter(prefix="/api", tags=["public"])

@router.post("/diagnosis/start", response_model=DiagnosisStartResponse)
def diagnosis_start(db: Session = Depends(get_db)):
    session = diagnosis_engine.start(db)
    session = db.query(models.DiagnosisSession).filter(models.DiagnosisSession.id == session.id).first()
    kind, payload = diagnosis_engine.next_question_or_result(db, session)
    if kind == "question":
        return DiagnosisStartResponse(session_id=session.id, status="asking", question=SymptomOut(**payload))
    return DiagnosisStartResponse(session_id=session.id, status="done", question=None)

@router.post("/diagnosis/{session_id}/answer", response_model=DiagnosisStepResponse)
def diagnosis_answer(session_id: str, req: DiagnosisAnswerRequest, db: Session = Depends(get_db)):
    try:
        diagnosis_engine.answer(db, session_id, req.symptom_code, req.answer)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    session = db.query(models.DiagnosisSession).filter(models.DiagnosisSession.id == session_id).first()
    kind, payload = diagnosis_engine.next_question_or_result(db, session)
    if kind == "question":
        return DiagnosisStepResponse(session_id=session_id, status="asking", question=SymptomOut(**payload), result=None)
    return DiagnosisStepResponse(session_id=session_id, status="done", question=None, result=payload)
