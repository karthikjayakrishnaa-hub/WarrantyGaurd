from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

from app.models.claim import ClaimStatus
from app.schemas.evidence import EvidenceResponse
from app.schemas.triage_result import TriageResultResponse
from app.schemas.audit_log import AuditLogResponse

class ClaimBase(BaseModel):
    customer_name: str
    product_model: str
    serial_number: str
    complaint_text: str

    @field_validator('customer_name', 'product_model', 'serial_number', 'complaint_text')
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        from app.core.validators import sanitize_html
        return sanitize_html(v)

class ClaimCreate(ClaimBase):
    pass

class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus


class ClaimResponse(ClaimBase):
    id: int
    user_id: Optional[int] = None
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime
    
    evidence: List[EvidenceResponse] = []
    triage_result: Optional[TriageResultResponse] = None
    audit_logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True


class ClaimListResponse(BaseModel):
    """Paginated response wrapper with total count for the dashboard."""
    claims: List[ClaimResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True
