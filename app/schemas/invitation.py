from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole

class InvitationBase(BaseModel):
    email: EmailStr
    role: UserRole

class InvitationCreate(InvitationBase):
    pass

class InvitationResponse(InvitationBase):
    id: int
    org_id: UUID
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}