from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class OrganizationBase(BaseModel):
    name: str
    slug: str
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}