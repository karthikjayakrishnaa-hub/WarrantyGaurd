from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.security import get_current_user, require_org
from app.models.claim import Claim, ClaimStatus
from app.models.user import User, UserRole
from app.models.audit_log import AuditAction
from app.models.product import Product
from app.schemas.claim import ClaimCreate, ClaimResponse, ClaimStatusUpdate, ClaimListResponse
from app.schemas.audit_log import AuditLogResponse
from pydantic import BaseModel
from app.services.audit import log_action

router = APIRouter()


def _enrich_audit_logs(claim):
    """Populate user_name on audit log entries for display."""
    for log in claim.audit_logs:
        if log.user:
            log.user_name = log.user.full_name
        else:
            log.user_name = "System"
    return claim


@router.post("/", response_model=ClaimResponse, status_code=201)
def create_claim(
    claim_in: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    # Verify product exists in organization's catalog
    product = db.query(Product).filter(
        Product.org_id == current_user.org_id,
        Product.name.ilike(f"%{claim_in.product_model}%")
    ).first()

    if not product:
        raise HTTPException(
            status_code=400, 
            detail=f"Product model '{claim_in.product_model}' not found in your organization's catalog."
        )
        
    db_claim = Claim(
        org_id=current_user.org_id,
        user_id=current_user.id,
        customer_name=claim_in.customer_name,
        product_model=product.name,  # Normalize to catalog name
        serial_number=claim_in.serial_number,
        complaint_text=claim_in.complaint_text,
    )
    db.add(db_claim)
    db.flush()

    log_action(db, db_claim.id, AuditAction.claim_created, current_user.id,
               f"Claim submitted for {claim_in.product_model}")

    db.commit()
    db.refresh(db_claim)
    return _enrich_audit_logs(db_claim)


@router.get("/", response_model=ClaimListResponse)
def list_claims(
    status: Optional[ClaimStatus] = None,
    search: Optional[str] = Query(None, description="Search across customer name, product model, serial number"),
    date_from: Optional[str] = Query(None, description="Filter claims from this date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter claims up to this date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field: created_at, updated_at, status"),
    sort_order: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    # Tenant isolation: strictly filter by org_id first
    query = db.query(Claim).filter(Claim.org_id == current_user.org_id)

    # Role-based filtering: customers see only their own claims
    if current_user.role == UserRole.customer:
        query = query.filter(Claim.user_id == current_user.id)

    # Status filter
    if status:
        query = query.filter(Claim.status == status)

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Claim.customer_name.ilike(search_term),
                Claim.product_model.ilike(search_term),
                Claim.serial_number.ilike(search_term),
                Claim.complaint_text.ilike(search_term),
            )
        )

    # Date range filter
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Claim.created_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            # Include the entire end day
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Claim.created_at <= dt_to)
        except ValueError:
            pass

    # Get total before pagination
    total = query.count()

    # Sorting
    sort_column = getattr(Claim, sort_by, Claim.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    claims = query.offset(skip).limit(limit).all()

    # Enrich audit logs with user names
    for claim in claims:
        _enrich_audit_logs(claim)

    return ClaimListResponse(claims=claims, total=total, skip=skip, limit=limit)


@router.get("/{id}", response_model=ClaimResponse)
def get_claim(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    claim = db.query(Claim).filter(Claim.id == id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Customers can only see their own claims
    if current_user.role == UserRole.customer and claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return _enrich_audit_logs(claim)


@router.patch("/{id}/status", response_model=ClaimResponse)
def update_claim_status(
    id: int,
    status_update: ClaimStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    # Only agents and admins can change claim status
    if current_user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Only agents and admins can update claim status")

    claim = db.query(Claim).filter(Claim.id == id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    old_status = claim.status.value
    claim.status = status_update.status

    # Determine audit action
    if status_update.status == ClaimStatus.approved:
        action = AuditAction.claim_approved
    elif status_update.status == ClaimStatus.rejected:
        action = AuditAction.claim_rejected
    else:
        action = AuditAction.status_changed

    log_action(db, claim.id, action, current_user.id,
               f"Status changed from '{old_status}' to '{status_update.status.value}'")

    db.commit()
    db.refresh(claim)
    return _enrich_audit_logs(claim)


class BulkClaimUpdate(BaseModel):
    claim_ids: List[int]
    status: ClaimStatus

@router.post("/bulk-update")
def bulk_update_claims(
    update_data: BulkClaimUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    if current_user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    claims = db.query(Claim).filter(
        Claim.id.in_(update_data.claim_ids), 
        Claim.org_id == current_user.org_id
    ).all()

    updated_ids = []
    for claim in claims:
        old_status = claim.status.value
        claim.status = update_data.status
        
        if update_data.status == ClaimStatus.approved:
            action = AuditAction.claim_approved
        elif update_data.status == ClaimStatus.rejected:
            action = AuditAction.claim_rejected
        else:
            action = AuditAction.status_changed
            
        log_action(db, claim.id, action, current_user.id,
                   f"Bulk status changed from '{old_status}' to '{update_data.status.value}'")
        updated_ids.append(claim.id)

    db.commit()
    return {"message": f"Successfully updated {len(updated_ids)} claims", "updated_ids": updated_ids}



@router.delete("/{id}", status_code=204)
def delete_claim(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org),
):
    """
    Delete a claim. Only allowed for claims still in 'submitted' or 'processing' status
    (i.e. ghost/partial claims that failed before the pipeline completed).
    Called automatically by the frontend on evidence upload failure to prevent
    orphaned evidence records from triggering false duplicate detections on retry.
    """
    claim = db.query(Claim).filter(
        Claim.id == id,
        Claim.org_id == current_user.org_id
    ).first()

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Only allow deletion of claims that never completed the pipeline
    if claim.status not in [ClaimStatus.submitted, ClaimStatus.processing]:
        raise HTTPException(
            status_code=400,
            detail="Only submitted/processing claims can be deleted. Use status update to reject completed claims."
        )

    # Customers can only delete their own claims
    if current_user.role == UserRole.customer and claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(claim)
    db.commit()