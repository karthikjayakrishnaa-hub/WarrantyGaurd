from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import require_org, require_role
from app.models.warranty_policy import WarrantyPolicy
from app.schemas.warranty_policy import WarrantyPolicyResponse, WarrantyPolicyCreate

router = APIRouter()

@router.get("/", response_model=List[WarrantyPolicyResponse])
def list_policies(db: Session = Depends(get_db), current_user = Depends(require_org)):
    return db.query(WarrantyPolicy).filter(WarrantyPolicy.org_id == current_user.org_id).all()