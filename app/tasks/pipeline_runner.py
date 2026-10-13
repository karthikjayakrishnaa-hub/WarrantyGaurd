import asyncio
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.pipeline_status import PipelineStatus
from app.models.claim import Claim, ClaimStatus
from app.tasks.task_store import in_memory_task_store
from app.services.triage import triage_claim
import traceback

def process_claim_task(claim_id: int):
    # Execute in background thread pool provided by FastAPI
    db = SessionLocal()
    try:
        # Initialize status
        status = db.query(PipelineStatus).filter(PipelineStatus.claim_id == claim_id).first()
        if not status:
            status = PipelineStatus(claim_id=claim_id, current_step=0, status="running")
            db.add(status)
        else:
            status.status = "running"
            status.current_step = 0
            status.error_message = None
        db.commit()

        def progress_callback(step: int, name: str):
            status.current_step = step
            in_memory_task_store[claim_id] = {"step": step, "status": "running", "name": name}
            db.commit()

        in_memory_task_store[claim_id] = {"step": 0, "status": "running", "name": "Starting Pipeline"}

        # Real ML execution
        triage_claim(db, claim_id, progress_callback)

        # Complete
        status.current_step = 8
        status.status = "completed"
        in_memory_task_store[claim_id] = {"step": 8, "status": "completed", "name": "Finished"}
        db.commit()
        
    except Exception as e:
        status.status = "failed"
        status.error_message = str(e)
        in_memory_task_store[claim_id] = {"step": status.current_step, "status": "failed", "error": str(e)}
        
        # FIX: Update claim status to prevent it being stuck in 'processing' indefinitely
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            claim.status = ClaimStatus.submitted
            
        db.commit()
        print(f"Pipeline failed for claim {claim_id}: {traceback.format_exc()}")
    finally:
        db.close()