from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_org
from app.models.comment import Comment
from app.models.claim import Claim
from app.models.user import UserRole
from app.schemas.comment import CommentResponse, CommentCreate

router = APIRouter()

@router.get("/claim/{claim_id}", response_model=List[CommentResponse])
def get_claim_comments(claim_id: int, db: Session = Depends(get_db), current_user = Depends(require_org)):
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    query = db.query(Comment).filter(Comment.claim_id == claim_id)
    if current_user.role == UserRole.customer:
        query = query.filter(Comment.is_internal == False)
    return query.all()

@router.post("/", response_model=CommentResponse)
def add_comment(comment_in: CommentCreate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    claim = db.query(Claim).filter(Claim.id == comment_in.claim_id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    if current_user.role == UserRole.customer and comment_in.is_internal:
        raise HTTPException(status_code=403, detail="Customers cannot add internal comments")
        
    comment = Comment(**comment_in.model_dump(), user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment