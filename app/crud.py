from sqlalchemy.orm import Session
from . import models
from .seed_data import DISEASES, SYMPTOMS, RULES

def seed_if_empty(db: Session):
    if db.query(models.Disease).count() == 0:
        for code, d in DISEASES.items():
            db.add(models.Disease(code=code, name=d["name"], description=d["description"], priority=d["priority"]))
        db.commit()

    if db.query(models.Symptom).count() == 0:
        for code, q in SYMPTOMS.items():
            db.add(models.Symptom(code=code, question=q))
        db.commit()

    if db.query(models.DiseaseSymptom).count() == 0:
        for dcode, scodes in RULES.items():
            for idx, scode in enumerate(scodes):
                db.add(models.DiseaseSymptom(disease_code=dcode, symptom_code=scode, sort_order=idx))
        db.commit()

# Disease
def list_diseases(db: Session):
    return db.query(models.Disease).order_by(models.Disease.priority.asc(), models.Disease.code.asc()).all()

def get_disease(db: Session, code: str):
    return db.query(models.Disease).filter(models.Disease.code == code).first()

def create_disease(db: Session, code: str, name: str, description: str, priority: int):
    obj = models.Disease(code=code, name=name, description=description, priority=priority)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_disease(db: Session, code: str, name: str, description: str, priority: int):
    obj = get_disease(db, code)
    if not obj:
        return None
    obj.name = name
    obj.description = description
    obj.priority = priority
    db.commit()
    db.refresh(obj)
    return obj

def delete_disease(db: Session, code: str) -> bool:
    obj = get_disease(db, code)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# Symptom
def list_symptoms(db: Session):
    return db.query(models.Symptom).order_by(models.Symptom.code.asc()).all()

def get_symptom(db: Session, code: str):
    return db.query(models.Symptom).filter(models.Symptom.code == code).first()

def create_symptom(db: Session, code: str, question: str):
    obj = models.Symptom(code=code, question=question)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_symptom(db: Session, code: str, question: str):
    obj = get_symptom(db, code)
    if not obj:
        return None
    obj.question = question
    db.commit()
    db.refresh(obj)
    return obj

def delete_symptom(db: Session, code: str) -> bool:
    obj = get_symptom(db, code)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# Rules
def set_disease_symptoms(db: Session, disease_code: str, symptom_codes: list[str]):
    db.query(models.DiseaseSymptom).filter(models.DiseaseSymptom.disease_code == disease_code).delete()
    for idx, sc in enumerate(symptom_codes):
        db.add(models.DiseaseSymptom(disease_code=disease_code, symptom_code=sc, sort_order=idx))
    db.commit()

def get_disease_symptom_codes(db: Session, disease_code: str) -> list[str]:
    rows = (
        db.query(models.DiseaseSymptom)
        .filter(models.DiseaseSymptom.disease_code == disease_code)
        .order_by(models.DiseaseSymptom.sort_order.asc(), models.DiseaseSymptom.id.asc())
        .all()
    )
    return [r.symptom_code for r in rows]
