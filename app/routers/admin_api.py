from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..security import require_admin
from .. import crud
from ..schemas import DiseaseBase, DiseaseOut, SymptomBase, SymptomOut, SetDiseaseSymptomsRequest

router = APIRouter(prefix="/api", tags=["admin"])

@router.get("/diseases", response_model=list[DiseaseOut])
def list_diseases(db: Session = Depends(get_db), _=Depends(require_admin)):
    items = crud.list_diseases(db)
    return [
        DiseaseOut(
            code=d.code,
            name=d.name,
            description=d.description,
            priority=d.priority,
            symptoms=crud.get_disease_symptom_codes(db, d.code),
        )
        for d in items
    ]

@router.post("/diseases", response_model=DiseaseOut)
def create_disease(payload: DiseaseBase, db: Session = Depends(get_db), _=Depends(require_admin)):
    if crud.get_disease(db, payload.code):
        raise HTTPException(status_code=409, detail="Kode penyakit sudah ada")
    d = crud.create_disease(db, payload.code, payload.name, payload.description, payload.priority)
    return DiseaseOut(code=d.code, name=d.name, description=d.description, priority=d.priority, symptoms=[])

@router.put("/diseases/{code}", response_model=DiseaseOut)
def update_disease(code: str, payload: DiseaseBase, db: Session = Depends(get_db), _=Depends(require_admin)):
    d = crud.update_disease(db, code, payload.name, payload.description, payload.priority)
    if not d:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    return DiseaseOut(code=d.code, name=d.name, description=d.description, priority=d.priority, symptoms=crud.get_disease_symptom_codes(db, d.code))

@router.delete("/diseases/{code}")
def delete_disease(code: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    ok = crud.delete_disease(db, code)
    if not ok:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")
    return {"ok": True}

@router.get("/symptoms", response_model=list[SymptomOut])
def list_symptoms(db: Session = Depends(get_db), _=Depends(require_admin)):
    items = crud.list_symptoms(db)
    return [SymptomOut(code=s.code, question=s.question) for s in items]

@router.post("/symptoms", response_model=SymptomOut)
def create_symptom(payload: SymptomBase, db: Session = Depends(get_db), _=Depends(require_admin)):
    if crud.get_symptom(db, payload.code):
        raise HTTPException(status_code=409, detail="Kode gejala sudah ada")
    s = crud.create_symptom(db, payload.code, payload.question)
    return SymptomOut(code=s.code, question=s.question)

@router.put("/symptoms/{code}", response_model=SymptomOut)
def update_symptom(code: str, payload: SymptomBase, db: Session = Depends(get_db), _=Depends(require_admin)):
    s = crud.update_symptom(db, code, payload.question)
    if not s:
        raise HTTPException(status_code=404, detail="Gejala tidak ditemukan")
    return SymptomOut(code=s.code, question=s.question)

@router.delete("/symptoms/{code}")
def delete_symptom(code: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    ok = crud.delete_symptom(db, code)
    if not ok:
        raise HTTPException(status_code=404, detail="Gejala tidak ditemukan")
    return {"ok": True}

@router.get("/rules")
def list_rules(db: Session = Depends(get_db), _=Depends(require_admin)):
    diseases = crud.list_diseases(db)
    return {d.code: crud.get_disease_symptom_codes(db, d.code) for d in diseases}

@router.put("/diseases/{code}/symptoms")
def set_rule(code: str, payload: SetDiseaseSymptomsRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    if not crud.get_disease(db, code):
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")

    existing = {s.code for s in crud.list_symptoms(db)}
    for sc in payload.symptom_codes:
        if sc not in existing:
            raise HTTPException(status_code=400, detail=f"Gejala tidak dikenal: {sc}")

    crud.set_disease_symptoms(db, code, payload.symptom_codes)
    return {"ok": True, "disease_code": code, "symptoms": payload.symptom_codes}
