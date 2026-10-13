from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import require_org
from app.services.sla import get_overdue_claims

router = APIRouter()

@router.get("/overdue")
def list_overdue_claims(db: Session = Depends(get_db), current_user = Depends(require_org)):
    return get_overdue_claims(db, current_user.org_id)