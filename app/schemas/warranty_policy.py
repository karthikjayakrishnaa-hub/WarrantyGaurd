from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class WarrantyPolicyBase(BaseModel):
    product_id: int
    file_path: str
    version: str = "1.0"
    is_active: bool = True

class WarrantyPolicyCreate(WarrantyPolicyBase):
    pass

class WarrantyPolicyResponse(WarrantyPolicyBase):
    id: int
    org_id: UUID
    
    model_config = {"from_attributes": True}