from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    body: str
    is_internal: bool = False

class CommentCreate(CommentBase):
    claim_id: int

class CommentResponse(CommentBase):
    id: int
    claim_id: int
    user_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}