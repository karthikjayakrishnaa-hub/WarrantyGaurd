import os

MODELS = {
    "app/models/pipeline_status.py": """
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PipelineStatus(Base):
    __tablename__ = "pipeline_statuses"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, unique=True)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=8)
    status = Column(String, default="pending") # pending, running, completed, failed
    error_message = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim")
""",
    "app/models/notification_pref.py": """
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class NotificationPref(Base):
    __tablename__ = "notification_prefs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_on_status_change = Column(Boolean, default=True)
    email_on_assignment = Column(Boolean, default=True)

    user = relationship("User")
""",
    "app/models/sla.py": """
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class SLA(Base):
    __tablename__ = "slas"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True)
    response_target_hours = Column(Integer, default=24)
    resolution_target_hours = Column(Integer, default=72)

    org = relationship("Organization")
"""
}

SERVICES = {
    "app/services/notifications.py": """
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.claim import Claim

def send_status_change_email(db: Session, claim: Claim, new_status: str):
    # Mock sending email
    user = db.query(User).filter(User.id == claim.user_id).first()
    if user:
        print(f"[EMAIL MOCK] To: {user.email} | Subject: Claim #{claim.id} Status Updated | Body: Your claim status is now {new_status}")
""",
    "app/services/sla.py": """
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from app.models.claim import Claim
from app.models.sla import SLA

def get_overdue_claims(db: Session, org_id: str) -> List[Claim]:
    sla = db.query(SLA).filter(SLA.org_id == org_id).first()
    if not sla:
        return []
    
    # In a real app, this would use a complex SQL query to calculate hours elapsed
    # For now, we mock returning claims older than the resolution target
    from datetime import timedelta
    target_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=sla.resolution_target_hours)
    
    overdue = db.query(Claim).filter(
        Claim.org_id == org_id,
        Claim.status != "resolved",
        Claim.created_at < target_date
    ).all()
    
    return overdue
""",
    "app/tasks/task_store.py": """
# In-memory dictionary as a fallback for live progress before DB flush
in_memory_task_store = {}
""",
    "app/tasks/pipeline_runner.py": """
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.pipeline_status import PipelineStatus
from app.models.claim import Claim, ClaimStatus
from app.tasks.task_store import in_memory_task_store
from app.services.triage import triage_claim
import traceback

async def process_claim_task(claim_id: int):
    # Execute in background thread or asyncio
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

        # Step 1: Simulated OCR / Image hashing taking time
        status.current_step = 1
        in_memory_task_store[claim_id] = {"step": 1, "status": "running", "name": "Analyzing Evidence"}
        db.commit()
        await asyncio.sleep(2)  # simulate ML load

        # Step 2: Actually run triage ML pipeline
        status.current_step = 2
        in_memory_task_store[claim_id] = {"step": 2, "status": "running", "name": "Running Triage ML"}
        db.commit()
        
        # Real ML execution
        triage_claim(db, claim_id)

        # Complete
        status.current_step = 3
        status.status = "completed"
        in_memory_task_store[claim_id] = {"step": 3, "status": "completed", "name": "Finished"}
        db.commit()
        
    except Exception as e:
        status.status = "failed"
        status.error_message = str(e)
        in_memory_task_store[claim_id] = {"step": status.current_step, "status": "failed", "error": str(e)}
        db.commit()
        print(f"Pipeline failed for claim {claim_id}: {traceback.format_exc()}")
    finally:
        db.close()
"""
}

ENDPOINTS = {
    "app/api/v1/endpoints/sse.py": """
from fastapi import APIRouter, Depends
from fastapi.responses import EventSourceResponse
import asyncio
from app.tasks.task_store import in_memory_task_store

router = APIRouter()

@router.get("/{claim_id}/progress")
async def stream_pipeline_progress(claim_id: int):
    async def event_generator():
        while True:
            # Check in-memory store
            state = in_memory_task_store.get(claim_id)
            if state:
                yield {"data": str(state)}
                if state.get("status") in ["completed", "failed"]:
                    break
            else:
                yield {"data": "{'status': 'pending'}"}
            await asyncio.sleep(1)
            
    return EventSourceResponse(event_generator())
""",
    "app/api/v1/endpoints/sla.py": """
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
"""
}

for d in [MODELS, SERVICES, ENDPOINTS]:
    for path, content in d.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content.strip()) # Removed + "\\n" to prevent syntax errors

print("Files generated.")
