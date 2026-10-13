from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.claim import Claim, ClaimStatus
from app.models.user import User, UserRole
from app.models.audit_log import AuditAction
from app.services.audit import log_action
from app.tasks.pipeline_runner import process_claim_task
from app.models.pipeline_status import PipelineStatus

router = APIRouter()

# Statuses that are considered "already processed" — pipeline should not
# restart automatically for these. Only an explicit Redo Triage (force=True)
# from an agent can override.
_ALREADY_PROCESSED = {
    ClaimStatus.processing,
    ClaimStatus.triaged,
    ClaimStatus.approved,
    ClaimStatus.rejected,
    ClaimStatus.closed,
}


@router.post("/{id}/pipeline/run", status_code=202)
def run_pipeline(
    id: int,
    background_tasks: BackgroundTasks,
    force: bool = Query(
        False,
        description="Set to true only for manual Redo Triage. "
                    "Without force, the pipeline is blocked if the claim is already processed.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = db.query(Claim).filter(Claim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Guard: block automatic re-runs triggered by page load / navigation.
    # Only explicit Redo Triage (force=True, agents only) may bypass this.
    if claim.status in _ALREADY_PROCESSED and not force:
        return {
            "message": "Pipeline already ran for this claim",
            "claim_id": claim.id,
            "status": claim.status.value,
            "skipped": True,
        }

    # Redo Triage requires agent or admin role
    if force and current_user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Only agents can re-run the triage pipeline")

    # Update status and queue the background task
    claim.status = ClaimStatus.processing
    action_detail = "AI triage pipeline re-started by agent" if force else "AI triage pipeline started"
    log_action(db, claim.id, AuditAction.pipeline_started, current_user.id, action_detail)
    db.commit()

    background_tasks.add_task(process_claim_task, claim.id)

    return {"message": "Pipeline started", "claim_id": claim.id, "status": "processing"}


PIPELINE_STEP_NAMES = {
    0: "Starting Pipeline",
    1: "Fetching Evidence",
    2: "OCR Invoice Analysis",
    3: "Product Label OCR",
    4: "NLP Complaint Analysis",
    5: "Warranty Rule Engine",
    6: "Duplicate Evidence Check",
    7: "Policy RAG Retrieval",
    8: "AI Vision & Triage Decision",
}


@router.get("/{id}/pipeline/status")
def get_pipeline_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status = db.query(PipelineStatus).filter(PipelineStatus.claim_id == id).first()
    if not status:
        return {"status": "pending", "current_step": 0, "total_steps": 8, "step_name": "Pending"}
    return {
        "status": status.status,
        "current_step": status.current_step,
        "total_steps": status.total_steps,
        "step_name": PIPELINE_STEP_NAMES.get(status.current_step, f"Step {status.current_step}/8"),
        "error_message": status.error_message,
    }
