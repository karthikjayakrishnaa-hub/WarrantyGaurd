import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.claim import Claim
from app.models.evidence import Evidence, EvidenceType
from app.models.user import User
from app.models.audit_log import AuditAction
from app.schemas.evidence import EvidenceResponse
from app.services.audit import log_action

router = APIRouter()

@router.post("/{id}/evidence", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(
    id: int, 
    type: EvidenceType, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if claim exists
    claim = db.query(Claim).filter(Claim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read file content and compute hash
    content = await file.read()
    
    # Validate file size (max 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    file_hash = hashlib.sha256(content).hexdigest()
    
    phash = None
    if type in [EvidenceType.product_photo, EvidenceType.label_photo, EvidenceType.invoice]:
        try:
            from PIL import Image
            import imagehash
            import io
            img = Image.open(io.BytesIO(content))
            phash = str(imagehash.phash(img))
        except Exception as e:
            print(f"Error computing phash: {e}")

    # Ensure storage exists and write file
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{id}_{type.value}_{file_hash[:8]}{file_ext}"
    
    from app.core.storage import upload_file
    try:
        file_path = upload_file(content, file_name, file.content_type or "application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file")

    # Save to db
    db_evidence = Evidence(
        claim_id=id,
        type=type,
        file_path=file_path,
        file_hash=file_hash,
        phash=phash
    )
    db.add(db_evidence)

    log_action(db, id, AuditAction.evidence_uploaded, current_user.id,
               f"Uploaded {type.value} file: {file.filename}")

    db.commit()
    db.refresh(db_evidence)

    return db_evidence

@router.get("/{id}/evidence/{evidence_id}/download")
def download_evidence(
    id: int,
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify claim exists and evidence belongs to it
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id, Evidence.claim_id == id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    from app.core.storage import get_signed_url
    url = get_signed_url(evidence.file_path)
    if not url:
        raise HTTPException(status_code=500, detail="Could not generate download link")
        
    return {"url": url}
