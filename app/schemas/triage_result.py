from datetime import datetime
from pydantic import BaseModel
from app.models.triage_result import TriageCategory

class TriageResultBase(BaseModel):
    category: TriageCategory
    reasoning_summary: str
    recommended_action: str

class TriageResultCreate(TriageResultBase):
    claim_id: int

class TriageResultResponse(TriageResultBase):
    id: int
    claim_id: int
    created_at: datetime

    class Config:
        from_attributes = True
