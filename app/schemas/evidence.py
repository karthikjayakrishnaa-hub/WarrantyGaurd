from datetime import datetime
from pydantic import BaseModel
from app.models.evidence import EvidenceType

class EvidenceBase(BaseModel):
    type: EvidenceType

class EvidenceCreate(EvidenceBase):
    file_path: str
    file_hash: str

class EvidenceResponse(EvidenceBase):
    id: int
    claim_id: int
    file_path: str
    file_hash: str
    phash: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
