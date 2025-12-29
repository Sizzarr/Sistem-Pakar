from pydantic import BaseModel, Field
from typing import Optional, List

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SymptomBase(BaseModel):
    code: str = Field(..., pattern=r"^G\d{2}$")
    question: str

class SymptomOut(SymptomBase):
    pass

class DiseaseBase(BaseModel):
    code: str = Field(..., pattern=r"^P\d{2}$")
    name: str
    description: str
    priority: int = 100

class DiseaseOut(DiseaseBase):
    symptoms: List[str] = []

class SetDiseaseSymptomsRequest(BaseModel):
    symptom_codes: List[str]

class DiagnosisStartResponse(BaseModel):
    session_id: str
    status: str
    question: Optional[SymptomOut] = None

class DiagnosisAnswerRequest(BaseModel):
    symptom_code: str
    answer: bool

class DiagnosisResult(BaseModel):
    disease: Optional[DiseaseOut] = None
    matched_symptoms: List[SymptomOut] = []
    confidence: Optional[int] = None
    note: Optional[str] = None

class DiagnosisStepResponse(BaseModel):
    session_id: str
    status: str
    question: Optional[SymptomOut] = None
    result: Optional[DiagnosisResult] = None
