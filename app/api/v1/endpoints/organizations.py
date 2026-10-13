from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user, require_org, require_role
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationCreate

router = APIRouter()

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[dict] = None

@router.get("/me", response_model=OrganizationResponse)
def get_my_organization(db: Session = Depends(get_db), current_user = Depends(require_org)):
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.patch("/me", response_model=OrganizationResponse, dependencies=[Depends(require_role(["admin", "super_admin"]))])
def update_my_organization(org_in: OrganizationUpdate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if org_in.name is not None:
        org.name = org_in.name
    if org_in.settings is not None:
        org.settings = org_in.settings
        
    db.commit()
    db.refresh(org)
    return org