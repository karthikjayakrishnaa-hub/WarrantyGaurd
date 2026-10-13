from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    brand: str
    category: str
    warranty_months: int = 12

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    org_id: UUID
    
    model_config = {"from_attributes": True}