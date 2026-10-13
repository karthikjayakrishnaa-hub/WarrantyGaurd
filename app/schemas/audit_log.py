from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    id: int
    claim_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: AuditAction
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
