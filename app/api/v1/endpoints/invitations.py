from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.core.security import require_org, require_role
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationResponse, InvitationCreate

router = APIRouter()

@router.post("/", response_model=InvitationResponse, dependencies=[Depends(require_role(["admin", "super_admin"]))])
def create_invitation(inv_in: InvitationCreate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    inv = Invitation(
        **inv_in.model_dump(),
        org_id=current_user.org_id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv